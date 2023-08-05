from unittest import TestCase

import markdown
from mdx_picture import PictureExtension


class MdxPictureBlockParsingTest(TestCase):
    def testImgOrder(self):
        """Test mixed order of the img block and source blocks inside \
        the picture"""
        mixed_img_order_mdx = """
Hello World my Babald

[picture]
    [64em]: high-res.jpg
    ![This picture loads on non-supporting browsers.]\
(image.jpg "The image title")
    [37.5em]: med-res.jpg
    [0em]: low-res.jpg
[/picture]

One more time
"""
        mixed_size_order_mdx = """
Hello World my Babald

[picture]
    ![This picture loads on non-supporting browsers.]\
(image.jpg "The image title")
    [37.5em]: med-res.jpg
    [64em]: high-res.jpg
    [0em]: low-res.jpg
[/picture]

One more time
"""

        mixed_img_order_html = """<p>Hello World my Babald</p>\n\
<picture><source media="(min-width: 64em)" srcset="high-res.jpg" />\
<source media="(min-width: 37.5em)" srcset="med-res.jpg" />\
<source media="(min-width: 0em)" srcset="low-res.jpg" />\
<img alt="This picture loads on non-supporting browsers." src="image.jpg" \
title="The image title" /></picture><p>One more time</p>"""

        self.assertEqual(mixed_img_order_html,
                         markdown.markdown(mixed_img_order_mdx,
                         extensions=[PictureExtension()]))
        self.assertEqual(mixed_img_order_html,
                         markdown.markdown(mixed_size_order_mdx,
                         extensions=[PictureExtension()]))
