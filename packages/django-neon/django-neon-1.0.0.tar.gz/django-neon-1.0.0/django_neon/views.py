"""
Views based on class based generic views.

"""


from collections import defaultdict

from django.conf import settings
from django.http import Http404
from django.utils.translation import ugettext as _
from django.views.generic import DetailView

from .models.page import Page


MESSAGE_404 = _('Page not found')
TEMPLATE_404 = '404.html'


class PageView(DetailView):
    """
    The PageView renders a page-object identified by its id.
    The content is given by the related panes.
    """

    model = Page
    context_object_name = 'page'

    def get_template_names(self):
        """
        Every page can have an individual template.
        This template is returned here.
        In case the page is not active or does not exist,
        a common 404 template gets returned.
        """
        if not self.object or not self.object.is_published:
            try:
                template_name = settings.NEON_404_TEMPLATE_NAME
            except AttributeError:
                template_name = TEMPLATE_404
            return [template_name]
        return [self.object.template_name]

    def get_object(self, queryset=None):
        """
        Returns the page object to render or None.
        """
        try:
            obj = super().get_object(queryset=queryset)
        except Http404:
            obj = None
        return obj

    def get_context_data(self, **kwargs):
        """
        Returns the context-data if a page is published.
        Otherwise raise 404.
        The content is structured into sections (holding panes).
        Basic navigation info is given by 'root_pages'.
        """
        context = super().get_context_data(**kwargs)
        if self.object and self.object.is_published:
            # calculate only if there is a page and it's published
            context['sections'] = self.get_sections()
        root_pages = self.get_root_pages()
        context['breadcrumbs'] = self.get_breadcrumbs(root_pages)
        context['root_pages'] = root_pages
        return context

    def get_breadcrumbs(self, root_pages):
        """
        Returns the breadcrumbs of this page. If this page is not the
        homepage, the crumb of the homepage is prepended to the
        breadcrumbs.
        """
        try:
            crumbs = self.object.breadcrumbs
        except AttributeError:
            # on 404 self.object is None
            return []
        if root_pages and root_pages[0] != self.object:
            crumbs = root_pages[0].breadcrumbs + crumbs
        return crumbs

    def get_sections(self):
        """
        Returns a dictionary of sections.
        The keys are the section names.
        The values are a list of ordered panes related to the section.
        Panes with higher order_ids come first.
        """
        sections = defaultdict(list)
        for pane in self.object.panes.all():
            if pane.is_published:
                sections[pane.section.name].append(
                    pane.get_content(self.request)
                )
        # don't return a defaultdict for rendering
        return dict(sections)

    def get_root_pages(self):
        """
        Returns a list of pages for the topmost navigation-level:
        pages without a parent.
        A list of subpages can be accessed by 'page.children'
        """
        qs = Page.objects.filter(parent=None)
        qs = qs.order_by('sibling_id')
        pages = [p for p in qs if p.is_published]
        return pages


class HomePageView(PageView):
    """
    Renders the homepage.

    This is the one with no parents and the lowest sibling_id.
    """

    def get_object(self, qs=None):
        """
        Fetch from the pages with no parents the one with the lowest
        sibling_id.
        """
        qs = self.get_queryset()
        qs = qs.filter(parent=None, is_active=True)
        qs = qs.order_by('sibling_id')
        try:
            obj = qs[0]
        except IndexError:
            raise Http404(MESSAGE_404)
        return obj
