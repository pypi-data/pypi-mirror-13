"""
django-neon: page-model-definition
"""

import json
import os

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.timezone import now as _now
from django.utils.translation import ugettext_lazy as _


try:
    TEMPLATE_NAMES = [(n, n) for n in settings.NEON_TEMPLATE_NAMES]
except AttributeError:
    # NEON_TEMPLATE_NAMES have to be defined in settings
    TEMPLATE_NAMES = [
        (os.path.join('django_neon', 'neon_base.html'), 'neon_base.html')
    ]


# ------------------------------------------------------------------------
# Page Definition
# ------------------------------------------------------------------------

class Page(models.Model):
    """
    Hierarchic pages for holding panes.

    publish_from and publish_until can be blank, meaning no limit.
    is_active overrides any publish_from/until setting.
    """

    name = models.CharField(
        _('Name'),
        max_length=80)

    slug = models.SlugField(
        _('slug'),
        max_length=80)

    description = models.TextField(
        _('Meta description for search engines'),
        default="",
        blank=True)

    parent = models.ForeignKey(
        'self', blank=True, null=True,
        related_name='sub_pages',
        verbose_name=_('Parent Page'))

    sibling_id = models.IntegerField(
        _('Sibling sort order'),
        default=10)

    is_active = models.BooleanField(
        _('active'),
        default=False)

    publish_from = models.DateTimeField(
        _(u'Start publishing'),
        null=True,
        blank=True)

    publish_until = models.DateTimeField(
        _('Stop publishing'),
        null=True,
        blank=True)

    breadcrumbs_cache = models.TextField(
        _('breadcrumbs cache'),
        default="",
        blank=True)

    children_cache = models.TextField(
        _('children cache'),
        default="",
        blank=True)

    template_name = models.CharField(
        _('template'),
        choices=TEMPLATE_NAMES,
        max_length=80)

    class Meta:
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('neonpage', kwargs={'pk': self.pk, 'slug': self.slug})

    @property
    def url(self):
        """
        Ducktyping for pane signal-handler to substitute an internal
        page-link to reStructuredText-syntax.
        """
        return self.get_absolute_url()

    @property
    def is_published(self):
        """
        Returns a boolean whether the page should be rendered (or should
        raise a 404 Error). This depends on the status of the is_active
        flag, the publication time slot (from / until) of the page and
        the parent pages.
        """
        for crumb in self.breadcrumbs:
            if not crumb.get('page_is_published', False):
                return False
        return True

    @property
    def page_is_published(self):
        """
        Returns a boolean whether the page should be rendered (or should
        raise a 404 Error). This depends on the status of the is_active
        flag, the publication time slot (from / until) of the page.
        """
        if not self.is_active:
            return False
        now = _now()
        if self.publish_from and self.publish_from > now:
            return False
        if self.publish_until and self.publish_until < now:
            return False
        return True

    @property
    def breadcrumbs(self):
        """
        Returns a list of dictionaries with the keys 'name', 'url',
        'is_active', 'publish_from' and 'publish_until'.
        name and url are used to construct the breadcrumbs-path, the
        other informations are used to get the visibility status of the
        page: a page is visible if it is set to is_active and if the
        publish-dates enclose the current date. All this must also be
        true for all parent-pages. So if a parent-page is set to
        is_active=False all subpages are inactive too, without changing
        their own settings.
        """
        if self.breadcrumbs_cache:
            return json.loads(self.breadcrumbs_cache)
        breadcrumbs = self._get_breadcrumbs()
        self.breadcrumbs_cache = json.dumps(breadcrumbs)
        self.save()
        return breadcrumbs

    def _get_breadcrumbs(self):
        crumb = {
            'name': self.name,
            'url': self.get_absolute_url(),
            'page_is_published': self.page_is_published,
        }
        if self.parent is not None:
            path = self.parent.breadcrumbs
            path.append(crumb)
        else:
            path = [crumb]
        return path

    def clear_breadcrumbs_cache(self):
        self.breadcrumbs_cache = ''
        for item in self.sub_pages.all():
            item.clear_breadcrumbs_cache()
            item.save()

    @property
    def children(self):
        """
        Returns an ordered list of dictionaries with the keys 'name',
        'url' and 'pk' of the subpages to build up the sub-navigation.
        """
        if self.children_cache:
            return json.loads(self.children_cache)
        children = self._get_children()
        self.children_cache = json.dumps(children)
        self.save()
        return children

    def _get_children(self):
        qs = self.sub_pages.filter(is_active=True).order_by('sibling_id')
        return [
            {'name': c.name, 'url': c.get_absolute_url(), 'pk': c.pk}
            for c in qs
        ]

    def save(self, **kwargs):
        """Handle pre_save tasks."""
        self._update_caches()
        super().save(**kwargs)

    def _update_caches(self):
        """
        Discards the breadcrumbs- and parent children-caches on
        data-changes.
        """
        if not self.pk:
            # new page, clear parent children cache
            clear_parent_children_cache(self)
            return
        original = Page.objects.get(pk=self.pk)

        if (self.name != original.name
            or self.slug != original.slug
            or self.sibling_id != original.sibling_id
            or self.parent != original.parent):
            clear_parent_children_cache(self)

        if self.breadcrumbs_cache and (
                self.name != original.name
                or self.slug != original.slug
                or self.parent != original.parent
                or self.publish_from != original.publish_from
                or self.publish_until != original.publish_until
                or self.is_active != original.is_active):
            self.clear_breadcrumbs_cache()

        if (self.parent != original.parent):
            clear_parent_children_cache(original)


@receiver(pre_delete, sender=Page)
def delete_page_handler(sender, **kwargs):
    """
    Clear the parent children cache.
    This must be done as long as the instance is in the db.
    """
    instance = kwargs.get('instance')
    clear_parent_children_cache(instance)


def clear_parent_children_cache(instance):
    """
    Clears the children_cache of the instance-parent if the instance has
    a parent and the parent is not the instance itself (i.e. pointing to
    itself). The latter will cause an unlimited recursion.
    """
    parent = instance.parent
    if parent and parent != instance:
        if parent.children_cache:
            parent.children_cache = ''
            parent.save()
