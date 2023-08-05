import re
import markdown
from markdown.util import etree


class PictureExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.parser.blockprocessors.add('picture',
                                      PictureProcessor(md.parser, self.config),
                                      '_begin')


class PictureProcessor(markdown.blockprocessors.BlockProcessor):
    RE = re.compile(r"""\[picture\]\n
        (?:\s*\[\d+\.{0,1}\d*(?:em|px|pt)\]: .*?\.(?:jpg|jpeg|png)\n)*
        \s*!\[[^\]]+\]\([^)]+\.(?:jpg|jpeg|png)\s"[^)]+"\)\n
        (?:\s*\[\d+\.{0,1}\d*(?:em|px|pt)\]: .*?\.(?:jpg|jpeg|png)\n)*
        \[\/picture\]""", re.MULTILINE | re.X)
    RE_SOURCE = re.compile(
        r"\s*\[(\d+\.{0,1}\d*(?:em|px|pt))\]: (.*?\.(?:jpg|jpeg|png))\n")
    RE_IMG = re.compile(
        r'!\[([^\]]+)\]\(([^)]+\.(?:jpg|jpeg|png))\s"([^)]+)"\)')

    def __init__(self, parser, config):
        markdown.blockprocessors.BlockProcessor.__init__(self, parser)
        self.config = config

    def test(self, parent, block):
        return self.RE.search(block)

    def run(self, parent, blocks):
        # Allow source as empty element
        from markdown import serializers
        serializers.HTML_EMPTY.add("source")

        block = blocks.pop(0)

        picture = etree.SubElement(parent, 'picture')

        sources = re.findall(self.RE_SOURCE, block)
        sources.sort(key=lambda x: 0 if x[0] == '' else float(x[0][:-2]),
                     reverse=True)

        for width, src in sources:
            source_node = etree.SubElement(picture, 'source')
            source_node.set('media', '(min-width: ' + width + ')')
            source_node.set('srcset', src)

        img = self.RE_IMG.search(block)

        img_node = etree.SubElement(picture, 'img')
        img_node.set('alt', img.group(1))
        img_node.set('src', img.group(2))
        img_node.set('title', img.group(3))

        block, theRest = self.detab(block)

        self.parser.state.set('picture')
        self.parser.parseChunk(picture, block)
        self.parser.state.reset()


def makeExtension(configs=None):
    return PictureProcessor(configs=configs)
