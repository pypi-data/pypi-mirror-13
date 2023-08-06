"""
handlers for markup processing.
"""

import re

try:
    from docutils import core
    has_docutils = True
except ImportError:
    has_docutils = False
try:
    import markdown
    from markdown.extensions.attr_list import AttrListExtension
    from markdown.extensions.def_list import DefListExtension
    from .markdown_extensions import (
        DivBlockExtension,
        NeonTableExtension,
    )
    has_markdown = True
except ImportError:
    has_markdown = False

try:
    from .pygmentssupport import CodeBlockExtension
    has_pygments = True
except ImportError:
    has_pygments = False

from django.core.exceptions import ObjectDoesNotExist

from ..models.media import (
    Document,
    Image,
)
from ..models.page import Page


RST_IMAGE_PATTERN = re.compile(r'\.\. (image|figure):: \[(.*?)\]')
RST_DOCUMENT_PATTERN = re.compile(r'`(.*?)<doc:(.*?)>`_')
RST_PAGE_PATTERN = re.compile(r'`(.*?)<page:(.*?)>`_')
MKD_IMAGE_PATTERN = re.compile(r'!\[(.*?)\]\[(.*?)\]')
MKD_IMAGE_PATTERN_2 = re.compile(r'!\[(.*?)\]\(img:(.*?)\)')
MKD_DOCUMENT_PATTERN = re.compile(r'\[(.*?)\]\(doc:(.*?)\)')
MKD_PAGE_PATTERN = re.compile(r'\[(.*?)]\(page:(.*?)\)')

RST_IMAGE_SUBSTR = '.. %s:: %s'
RST_DOCUMENT_SUBSTR = '`%s <%s>`_'
MKD_IMAGE_SUBSTR = '![%s](%s)'
MKD_DOCUMENT_SUBSTR = '[%s](%s)'

MKD_DIV_PATTERN = re.compile(r'<p>\[(.*?)\]</p>(.*?)<p>\[close\]</p>', re.S)
MKD_DIV_SUBSTR = '<div class="\\1">\\2</div>'


def process_markdown(source, use_mediadb):
    """
    Interprets the source as markdown.
    Input and output are unicode strings.
    """
    if not has_markdown:
        return source
    if use_mediadb:
        source = substitute_mkd_images(source)
        source = substitute_mkd_pages(source)
        source = substitute_mkd_documents(source)
    extensions = [
        DivBlockExtension(),
        AttrListExtension(),
        DefListExtension(),
        NeonTableExtension(),
    ]
    if has_pygments:
        extensions.append(CodeBlockExtension())
    html = markdown.markdown(source, extensions=extensions)
    html = MKD_DIV_PATTERN.sub(MKD_DIV_SUBSTR, html)
    return html


def substitute_mkd_images(source):
    """
    Substitutes media-db tag with markdown-markup:
    Reference Style links with imagename as id
    ![alt text][imagename] are converted to Inlines:
    ![alt text](path/to/image)
    Additional more intuitve pattern:
    ![alt text](img:imagename)
    """
    source = _substitute(source, Image, MKD_IMAGE_PATTERN, MKD_IMAGE_SUBSTR)
    return _substitute(source, Image, MKD_IMAGE_PATTERN_2, MKD_IMAGE_SUBSTR)


def substitute_mkd_pages(source):
    """
    Substitutes media-db tag with markdown-markup:
    Reference Style links with documentname as id
    [alt text][documentname] are converted to Inlines:
    [alt text](path/to/document)

    Substitutes internal links to other pages with markdown
    markup:
    [link text](page:pagename) are converted to Inlines:
    [link text](path/to/page)
    """
    return _substitute(
        source, Page, MKD_PAGE_PATTERN, MKD_DOCUMENT_SUBSTR)


def substitute_mkd_documents(source):
    """
    Substitutes media-db documents with markdown-markup:
    [alt text](doc:documentname) are converted to Inlines:
    [alt text](path/to/document)
    """
    return _substitute(
        source, Document, MKD_DOCUMENT_PATTERN, MKD_DOCUMENT_SUBSTR)


def process_restructuredtext(source, use_mediadb):
    """
    Interprets the source as reStructuredText.
    Converts the source to html and extracts the body part. docutils
    wrapps the output into a <div> which is stripped from the returned
    result. Input and output are unicode strings.
    """
    if not has_docutils:
        return source
    if use_mediadb:
        source = substitute_rst_images(source)
        source = substitute_rst_pages(source)
        source = substitute_rst_documents(source)
    overrides = {
        'input_encoding': 'unicode',
        'initial_header_level': 2,
    }
    parts = core.publish_parts(
        source,
        writer_name='html',
        settings_overrides=overrides,
    )
    body = parts['html_body'].strip()
    lines = body.split('\n')
    result = '\n'.join(lines[1:-1])
    return result


def substitute_rst_images(source):
    """
    Substitutes media-db tags with reStructuredText markup:
    .. image:: [name] -> .. image:: path/to/image
    .. figure:: [name] -> .. figure:: path/to/image
    """
    return _substitute(source, Image, RST_IMAGE_PATTERN, RST_IMAGE_SUBSTR)


def substitute_rst_documents(source):
    """
    Substitutes media-db tags with reStructuredText markup:
    In case of embedded URIs documents from the media-db can be
    referenced by name:
    `link text <doc:documentname>`_ -> `link text <url/to/document>`_
    """
    return _substitute(
        source, Document, RST_DOCUMENT_PATTERN, RST_DOCUMENT_SUBSTR)


def substitute_rst_pages(source):
    """
    Substitutes internal links to other pages with reStructuredText
    markup: In case of embedded URIs documents from the media-db can be
    referenced by name:
    `link text <page:page-name>`_ -> `link text <url>`_
    The tailing underscore after the page-name is optional.
    """
    return _substitute(source, Page, RST_PAGE_PATTERN, RST_DOCUMENT_SUBSTR)


def _substitute(source, model, pattern, substr):
    def repl(mo):
        text = mo.group(1)
        name = mo.group(2)
        try:
            obj = model.objects.get(name=name)
        except ObjectDoesNotExist:
            return mo.group(0)
        return substr % (text, obj.url)
    return pattern.sub(repl, source)
