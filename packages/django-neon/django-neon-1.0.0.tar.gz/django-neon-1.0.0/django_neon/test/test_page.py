

import datetime
import pytest

from django.utils.timezone import now as _now
from django_neon.models.page import Page


pytestmark = pytest.mark.django_db


STRUCTURE = (
    # slug, parent
    ('home', None),
    ('news', 'home'),
    ('events', 'news'),
    ('images', 'news'),
    ('blog', 'home'),
    ('notice', 'blog'),
    ('archive', 'blog'),
    ('video', 'archive'),
    ('doc', 'archive'),
    ('pdf', 'doc'),
    ('articles', 'doc'),
)

ONE_DAY = datetime.timedelta(1)
NOW = _now()
TOMORROW = NOW + ONE_DAY
YESTERDAY = NOW - ONE_DAY


class TestPageCache(object):
    @pytest.fixture(autouse=True)
    def set_up(self):
        for name, parent_name in STRUCTURE:
            # slug and name are synonyme in this tests
            page = Page()
            page.name = name
            page.slug = name
            page.is_active = True
            if parent_name:
                page.parent = Page.objects.get(slug=parent_name)
            page.save()

    def set_caches(self):
        items = Page.objects.all()
        for item in items:
            item.breadcrumbs
            item.children

    def test_initial_empty_caches(self):
        """new pages should have empty chaches."""
        blog = Page.objects.get(slug='blog')
        assert blog.breadcrumbs_cache == ''
        assert blog.children_cache == ''

    def test_call_caches(self):
        """A breadcrumb or children-call should fill the cache."""
        blog = Page.objects.get(slug='blog')
        blog.breadcrumbs
        blog.children
        assert blog.breadcrumbs_cache != ''
        assert blog.children_cache != ''

    def test_set_caches(self):
        """Redundant helper-method test."""
        self.set_caches()
        blog = Page.objects.get(slug='blog')
        assert blog.breadcrumbs_cache != ''
        assert blog.children_cache != ''

    def test_new_page(self):
        """A new node (page) should clear the parent children cache."""
        self.set_caches()
        blog = Page.objects.get(slug='blog')
        vacation = Page()
        vacation.slug = 'vacation'
        vacation.parent = blog
        vacation.save()
        blog = Page.objects.get(slug='blog')
        assert blog.breadcrumbs_cache != ''
        assert blog.children_cache == ''

    def test_delete_page(self):
        """children cache of former parent should cleared."""
        self.set_caches()
        blog = Page.objects.get(slug='blog')
        assert blog.children_cache != ''
        archive = Page.objects.get(slug='archive')
        archive.delete()
        with pytest.raises(Page.DoesNotExist):
            archive = Page.objects.get(slug='archive')
        blog = Page.objects.get(slug='blog')
        assert blog.children_cache == ''

    @pytest.mark.parametrize('item', ['name', 'slug'])
    def test_name_or_slug_change(self, item):
        """
        Change page-name: should clear the breadcrumbs cache of all
        children and should clear the parent-children-cache.
        """
        self.set_caches()
        slugs = ('notice', 'archive', 'video', 'doc', 'pdf', 'articles')
        blog = Page.objects.get(slug='blog')
        # check initial cache
        assert blog.parent.children_cache != ''
        for slug in slugs:
            page = Page.objects.get(slug=slug)
            assert page.breadcrumbs_cache != ''
        # change node name/slug
        if item == 'name':
            blog.name = 'new_name'
        else:
            blog.slug = 'new_slug'
        blog.save()
        # check cache change
        assert blog.parent.children_cache == ''
        for slug in slugs:
            page = Page.objects.get(slug=slug)
            assert page.breadcrumbs_cache == ''

    def test_change_sibling_id(self):
        """On change the parent-children_cache should be cleared."""
        self.set_caches()
        notice = Page.objects.get(slug='notice')
        notice.sibling_id += 1
        notice.save()
        blog = Page.objects.get(slug='blog')
        assert blog.children_cache == ''

    def test_parent_node_change(self):
        """
        A change of the parent node of a page should should clear the
        breadcrumbs_cache of all children of the given page and should
        clear the children_caches of the old and the new parent-node.
        """
        self.set_caches()
        slugs = ('video', 'doc', 'pdf', 'articles')
        news = Page.objects.get(slug='news')
        archive = Page.objects.get(slug='archive')
        archive.parent = news
        archive.save()
        # breadcrumbs of subpages should have cleared:
        for slug in slugs:
            page = Page.objects.get(slug=slug)
            assert page.breadcrumbs_cache == ''
        # children_caches of old and new parent should have cleared:
        for slug in ('blog', 'news'):
            page = Page.objects.get(slug=slug)
            assert page.children_cache == ''

    def test_is_active_change(self):
        """
        A change of the is_active attribute should clear the
        breadcrumbs_caches of all children, because the is_active state
        of the parent are stored there.
        """
        self.set_caches()
        slugs = ('video', 'doc', 'pdf', 'articles')
        archive = Page.objects.get(slug='archive')
        archive.is_active = not archive.is_active
        archive.save()
        for slug in slugs:
            page = Page.objects.get(slug=slug)
            assert page.breadcrumbs_cache == ''

    @pytest.mark.parametrize(
        'is_active, publish_from, publish_until, result', [
            (False, None, None, False),
            (True, None, None, True),
            (True, YESTERDAY, None, True),
            (True, None, YESTERDAY, False),
            (True, TOMORROW, None, False),
            (True, None, TOMORROW, True),
            (True, YESTERDAY, TOMORROW, True),
            (True, TOMORROW, YESTERDAY, False),
        ])
    def test_page_is_published(
        self, is_active, publish_from, publish_until, result):
        """
        Test the visibility status of a page depending on the is_active
        flag and the publication dates publish_from and publish_until.
        """
        page = Page()
        page.is_active = is_active
        page.publish_from = publish_from
        page.publish_until = publish_until
        assert page.page_is_published is result

    def test_is_published(self):
        self.set_caches()
        home = Page.objects.get(slug='home')
        assert home.is_published is True
        home.publish_from = TOMORROW
        assert home.is_published is True
        home.save()
        assert home.is_published is False

    @pytest.mark.parametrize(
        'parent_slug, is_active, page_slug, result', [
            ('doc', True, 'pdf', True),
            ('doc', False, 'pdf', False),
            ('video', True, 'pdf', True),
            ('video', False, 'pdf', True),
            ('archive', True, 'pdf', True),
            ('archive', False, 'pdf', False),
            ('blog', False, 'pdf', False),
            ('home', False, 'pdf', False),
        ])
    def test_is_published_hierarchy(
        self, parent_slug, is_active, page_slug, result):
        """
        Test is_active status of subpages if parent status changes.
        """
        self.set_caches()
        parent = Page.objects.get(slug=parent_slug)
        parent.is_active = is_active
        parent.save()
        page = Page.objects.get(slug=page_slug)
        assert page.is_published is result
