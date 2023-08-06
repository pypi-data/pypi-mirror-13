"""
mardown extensions.

https://pythonhosted.org/Markdown/extensions/api.html
"""


try:
    from markdown.blockprocessors import BlockProcessor
    from markdown.extensions import Extension
    from markdown.extensions.tables import TableProcessor
    from markdown import util
    has_markdown = True
except ImportError:
    has_markdown = False


if has_markdown:

    class DivBlockProcessor(BlockProcessor):
        """
        Generic div-processor:

        [class: names]
            indented textblocks

        will be translated to:
        <div class="names">parsed content of indented textblocks</div>
        """

        def test(self, parent, block):
            return block.startswith('[class:')

        def run(self, parent, blocks):
            definition, content = blocks.pop(0).split(']', 1)
            _, classes = definition.split(':', 1)
            attributes = {'class': classes}
            p = util.etree.SubElement(parent, 'div', attrib=attributes)
            innerblocks = self._get_innerblocks(content, blocks)
            self.parser.parseBlocks(p, innerblocks)

        def _get_innerblocks(self, content, blocks):
            innerblocks = [content.strip()]
            indent = ' ' * self.tab_length
            while blocks:
                if blocks[0].startswith(indent):
                    innerblocks.append(blocks.pop(0)[len(indent):])
                else:
                    break
            return innerblocks


    class DivBlockExtension(Extension):
        def extendMarkdown(self, md, md_globals):
            md.parser.blockprocessors.add(
                'DivBlockProcessor',
                DivBlockProcessor(md.parser),
                '_begin')


    class NeonTableProcessor(TableProcessor):
        """
        Enhance Extension TableProcessor.

        If a table-definition is prepended by '|class:name'
        the 'name' will get the class-attribute of the table-tag:

        |class: table
        |header1 |header2 |
        |--------|--------|
        |content |content |

        will compile to:

        <table class="table">
        ...

        """

        def test(self, parent, block):
            rows = block.split('\n')
            self.table_css = None
            if len(rows) and rows[0].startswith('|class:'):
                _, css = rows[0].split(':', 1)
                self.table_css = css.strip(' ')
                rows.pop(0)
            return super().test(parent, '\n'.join(rows))

        def run(self, parent, blocks):
            if self.table_css:
                # discard first row with class-attributes
                _, block = blocks.pop(0).split('\n', 1)
                blocks.insert(0, block)
            result = super().run(parent, blocks)
            if self.table_css:
                table = parent.find('table')
                if table:
                    table.set('class', self.table_css)
            return result


    class NeonTableExtension(Extension):
        """Enhance TableExtension. """

        def extendMarkdown(self, md, md_globals):
            md.parser.blockprocessors.add('table',
                                          NeonTableProcessor(md.parser),
                                          '<hashheader')
