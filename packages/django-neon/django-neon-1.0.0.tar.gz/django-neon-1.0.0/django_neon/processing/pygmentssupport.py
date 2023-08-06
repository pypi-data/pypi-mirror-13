"""
django-neon pygments support

Adaption of the 'rst-directive.py' and 'markdown-processor' moduls:
https://bitbucket.org/birkenfeld/pygments-main/src/

"""

import re

try:
    from docutils import nodes
    from docutils.parsers.rst import directives, Directive
    has_docutils = True
except ImportError:
    has_docutils = False

try:
    from markdown.preprocessors import Preprocessor
    from markdown.extensions import Extension
    has_markdown = True
except ImportError:
    has_markdown = False

try:
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import get_lexer_by_name, TextLexer
    has_pygments = True
except ImportError:
    has_pygments = False


INLINESTYLES = False


if has_docutils and has_pygments:
    # The default formatter
    DEFAULT = HtmlFormatter(noclasses=INLINESTYLES)
    # Add name -> formatter pairs for every variant you want to use
    VARIANTS = {
        # 'linenos': HtmlFormatter(noclasses=INLINESTYLES, linenos=True),
    }

    class Pygments(Directive):
        """ Source code syntax hightlighting.
        """
        required_arguments = 1
        optional_arguments = 0
        final_argument_whitespace = True
        option_spec = dict([(key, directives.flag) for key in VARIANTS])
        has_content = True

        def run(self):
            self.assert_has_content()
            try:
                lexer = get_lexer_by_name(self.arguments[0])
            except ValueError:
                # no lexer found - use the text one instead of an exception
                lexer = TextLexer()
            # take an arbitrary option if more than one is given
            formatter = self.options and VARIANTS[list(self.options)[0]] or DEFAULT
            parsed = highlight(u'\n'.join(self.content), lexer, formatter)
            return [nodes.raw('', parsed, format='html')]

    directives.register_directive('sourcecode', Pygments)


if has_markdown and has_pygments:

    class CodeBlockPreprocessor(Preprocessor):

        pattern = re.compile(r'\[sourcecode:(.+?)\](.+?)\[/sourcecode\]', re.S)
        formatter = HtmlFormatter(noclasses=INLINESTYLES)

        def run(self, lines):
            def repl(m):
                try:
                    lexer = get_lexer_by_name(m.group(1))
                except ValueError:
                    lexer = TextLexer()
                code = highlight(m.group(2), lexer, self.formatter)
                code = code.replace('\n\n', '\n&nbsp;\n').replace('\n', '<br />')
                return '\n\n<div class="code">%s</div>\n\n' % code
            joined_lines = "\n".join(lines)
            joined_lines = self.pattern.sub(repl, joined_lines)
            return joined_lines.split("\n")

    class CodeBlockExtension(Extension):
        def extendMarkdown(self, md, md_globals):
            md.preprocessors.add('CodeBlockPreprocessor', CodeBlockPreprocessor(), '_begin')
