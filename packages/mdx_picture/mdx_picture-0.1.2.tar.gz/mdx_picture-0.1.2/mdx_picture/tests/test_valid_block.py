from unittest import TestCase

import markdown
from mdx_picture import PictureExtension


class MdxPictureBlockVadiationTest(TestCase):
    def testMinimalBlockConfiguration(self):
        """Test minimal block configuration with image"""
        no_sources_mdx = """
Hello World my Babald

[picture]
    ![This picture loads on non-supporting browsers.]\
(image.jpg "The image title")
[/picture]

One more time
"""
        no_sources_html = """<p>Hello World my Babald</p>\n\
<picture>\
<img alt="This picture loads on non-supporting browsers." \
src="image.jpg" title="The image title" />\
</picture>\
<p>One more time</p>"""

        self.assertEqual(no_sources_html,
                         markdown.markdown(no_sources_mdx,
                         extensions=[PictureExtension()]))

    def testCompleteBlockConfiguration(self):
        """Test Complete block configuration with image and multimpe sources"""
        sources_mdx = """
Hello World my Babald

[picture]
    [64em]: high-res.jpg
    [37.5em]: med-res.jpg
    [0em]: low-res.jpg
    ![This picture loads on non-supporting browsers.]\
(image.jpg "The image title")
[/picture]

One more time
"""
        sources_html = """<p>Hello World my Babald</p>\n\
<picture><source media="(min-width: 64em)" srcset="high-res.jpg" />\
<source media="(min-width: 37.5em)" srcset="med-res.jpg" />\
<source media="(min-width: 0em)" srcset="low-res.jpg" />\
<img alt="This picture loads on non-supporting browsers." src="image.jpg" \
title="The image title" /></picture>\
<p>One more time</p>"""

        self.assertEqual(sources_html,
                         markdown.markdown(sources_mdx,
                         extensions=[PictureExtension()]))

    def testInvalidNoImageBlockConfiguration(self):
        """Test invalid block configuration with source but without image"""
        no_img_mdx = """
Hello World my Babald

[picture]
    [37.5em]: med-res.jpg
[/pitture]

One more time
"""
        no_img_html = """<p>Hello World my Babald</p>\n\
<p>[picture]\n    [37.5em]: med-res.jpg\n[/pitture]</p>\n<p>One more time</p>"""

        self.assertEqual(no_img_html,
                         markdown.markdown(no_img_mdx,
                         extensions=[PictureExtension()]))
