"""
django-neon: pane and sections model-definition
"""


from django.dispatch import Signal
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.timezone import now as _now
from django.utils.translation import ugettext_lazy as _

from ..processing.markup import (
    process_markdown,
    process_restructuredtext
)
from .page import Page

PLAIN = 0
RESTRUCTURED_TEXT = 1
MARKDOWN = 2
DYNAMIC = 3
MARKUP_CHOICES = [(PLAIN, 'Plain')]

try:
    import docutils  # noqa
    MARKUP_CHOICES.append((RESTRUCTURED_TEXT, 'reStructuredText'))
except ImportError:
    pass
try:
    import markdown  # noqa
    MARKUP_CHOICES.append((MARKDOWN, 'Markdown'))
except ImportError:
    pass

MARKUP_CHOICES.append((DYNAMIC, 'dynamic'))


get_dynamic_pane_content = Signal(providing_args=['pane', 'request'])


# ------------------------------------------------------------------------
# Section Definition
# ------------------------------------------------------------------------

class Section(models.Model):
    """
    A section is just a name. The Page-object collects all related Panes
    to their according sections, so that they can be rendered at
    different parts of a template. See page.get_context(): the sections
    are part of the context.
    """

    name = models.CharField(
        _('Name'),
        max_length=80)

    def __str__(self):
        return self.name


# ------------------------------------------------------------------------
# Pane Definition
# ------------------------------------------------------------------------

class Pane(models.Model):
    """
    Panes are the content-containers.
    """

    name = models.CharField(
        _('Name'),
        max_length=80)

    page = models.ForeignKey(
        Page,
        related_name='panes',
        verbose_name=_('Page'))

    section = models.ForeignKey(
        Section,
        verbose_name=_('Section'))

    content = models.TextField(
        _('Content'),
        blank=True)

    markup = models.IntegerField(
        _('Markup'),
        choices=MARKUP_CHOICES,
        default=PLAIN)

    use_mediadb = models.BooleanField(
        _('Use MediaDB'),
        default=True)

    order_id = models.IntegerField(
        _('Sort order'),
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

    rendered_content = models.TextField(
        _('Rendered Content'),
        blank=True)

    class Meta:
        ordering = ['-order_id']

    def __str__(self):
        return self.name

    @property
    def is_published(self):
        """
        Returns a boolean whether the pane should be rendered on a page.
        """
        if not self.is_active:
            return False
        now = _now()
        if self.publish_from and self.publish_from > now:
            return False
        if self.publish_until and self.publish_until < now:
            return False
        return True

    def get_content(self, request=None):
        """
        Return the content depending on the markup-settings.

        If no markup is set the raw content is returned as text.
        Otherwise the rendered content gets returned as trusted html. If
        the markup is set to DYNAMIC the signal-handler will return the
        content also set as trusted html. It's up to you to be careful
        in this case.
        """
        if not self.markup:
            return self.content
        if self.markup == DYNAMIC:
            content = self._get_dynamic_content(request)
        else:
            content = self.rendered_content
        return mark_safe(content)

    def _get_dynamic_content(self, request):
        """
        This method signals all receivers which are registered to create
        dynamic pane content.

        Every function decorated by

            '@receiver(get_dynamic_pane_content, sender=Pane)'

        will get called when a pane with the markup-attribute 'dynamic'
        should return content.
        It is up to the receivers to check whether they are responsible
        for the given pane to return some content.
        """
        responses = get_dynamic_pane_content.send(
            sender=Pane,
            pane=self,
            request=request)
        result = [response for receiver, response in responses]
        return '\n'.join(result)

    def save(self, **kwargs):
        """handle pre_save processing."""
        self._process_pane_content()
        super().save(**kwargs)

    def _process_pane_content(self):
        """
        Do markup-processing of the pane-content.
        Store processed data in pane.rendered_content.
        """
        if self.markup == RESTRUCTURED_TEXT:
            self.rendered_content = process_restructuredtext(
                self.content, self.use_mediadb)
        elif self.markup == MARKDOWN:
            self.rendered_content = process_markdown(
                self.content, self.use_mediadb)
        # else: do nothing
