import pytest
from django_neon.models.page import Page
from django_neon.models.pane import (
    Section,
    Pane,
    RESTRUCTURED_TEXT,
    MARKDOWN,
)

pytestmark = pytest.mark.django_db

INP_TITLE = 'title\n=====\nline 1\nline2\n\nline3'
OUT_TITLE_M = '<h1>title</h1>\n<p>line 1\nline2</p>\n<p>line3</p>'
OUT_TITLE_R = '<h1 class="title">title</h1>\n<p>line 1\nline2</p>\n<p>line3</p>'

INP_DIV_WRAPPER = """
[alert alert-info]

#Info

some text here

[close]
""".strip()

OUT_DIV_WRAPPER_M = """
<div class="alert alert-info">
<h1>Info</h1>
<p>some text here</p>
</div>
""".strip()

INP_DIV_BLOCK = """
[class:name]
    some text
    more text

    another paragraph

next line
""".strip()

OUT_DIV_BLOCK_M = """
<div class="name">
<p>some text
    more text</p>
<p>another paragraph</p>
</div>
<p>next line</p>
""".strip()

INP_DIV_BLOCK1 = """
[class:name]
    some text
    more text

        another
        paragraph

next line
""".strip()

OUT_DIV_BLOCK_M1 = """
<div class="name">
<p>some text
    more text</p>
<pre><code>another
    paragraph
</code></pre>
</div>
<p>next line</p>
""".strip()

INP_DIV_BLOCK2 = """
[class:name]
    some text
""".strip()

OUT_DIV_BLOCK_M2 = """
<div class="name">
<p>some text</p>
</div>
""".strip()

INP_DIV_BLOCK3 = """
[class:alert alert-warning]
    some text
""".strip()

OUT_DIV_BLOCK_M3 = """
<div class="alert alert-warning">
<p>some text</p>
</div>
""".strip()

INP_DIV_BLOCK4 = """
[class:alert alert-warning]
    #Warning

    some text
""".strip()

OUT_DIV_BLOCK_M4 = """
<div class="alert alert-warning">
<h1>Warning</h1>
<p>some text</p>
</div>
""".strip()


PANE_NAME = 'test'


class TestPane(object):
    @pytest.fixture(autouse=True)
    def set_up(self):
        """a pane requires a page and a section."""
        page = Page()
        page.save()
        section = Section()
        section.save()
        pane = Pane(name=PANE_NAME, page=page, section=section)
        pane.save()

    def get_pane(self):
        return Pane.objects.get(name=PANE_NAME)

    def set_pane(self, inp, markup):
        pane = self.get_pane()
        pane.content = inp
        pane.markup = markup
        pane.save()

    def prepared_pane(self, inp, markup):
        self.set_pane(inp, markup)
        return self.get_pane()

    def test_get_pane(self):
        pane = self.get_pane()
        assert pane.name == PANE_NAME

    @pytest.mark.parametrize('inp, markup, out', [
        (INP_TITLE, MARKDOWN, OUT_TITLE_M),
        (INP_TITLE, RESTRUCTURED_TEXT, OUT_TITLE_R),
        (INP_DIV_WRAPPER, MARKDOWN, OUT_DIV_WRAPPER_M),
        (INP_DIV_BLOCK, MARKDOWN, OUT_DIV_BLOCK_M),
        (INP_DIV_BLOCK1, MARKDOWN, OUT_DIV_BLOCK_M1),
        (INP_DIV_BLOCK2, MARKDOWN, OUT_DIV_BLOCK_M2),
        (INP_DIV_BLOCK3, MARKDOWN, OUT_DIV_BLOCK_M3),
        (INP_DIV_BLOCK4, MARKDOWN, OUT_DIV_BLOCK_M4),
        ])
    def test_title(self, inp, markup, out):
        pane = self.prepared_pane(inp, markup)
        assert out == pane.get_content()
