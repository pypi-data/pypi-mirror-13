
import pytest

from django_neon.processing.markup import (
    process_markdown,
    process_restructuredtext,
)


INP_TITLE = 'title\n=====\nline 1\nline2\n\nline3'


@pytest.mark.parametrize(
    'inp, out', [
        (INP_TITLE, '<h1>title</h1>\n<p>line 1\nline2</p>\n<p>line3</p>'),
    ])
def test_mk_convert(inp, out):
    assert out == process_markdown(INP_TITLE, False)


@pytest.mark.parametrize(
    'inp, out', [
        (INP_TITLE,
         '<h1 class="title">title</h1>\n<p>line 1\nline2</p>\n<p>line3</p>'),
    ])
def test_rst_convert(inp, out):
    assert out == process_restructuredtext(INP_TITLE, False)
