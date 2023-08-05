from os import path

from rinoh.font import Typeface
from rinoh.font.style import REGULAR, BOLD, ITALIC
from rinoh.font.opentype import OpenTypeFont


__all__ = ['typeface']


def otf(style):
    filename = 'texgyrebonum-{}.otf'.format(style)
    return path.join(path.dirname(__file__), filename)


typeface = Typeface('TeX Gyre Bonum',
                    OpenTypeFont(otf('regular'), weight=REGULAR),
                    OpenTypeFont(otf('italic'), weight=REGULAR, slant=ITALIC),
                    OpenTypeFont(otf('bold'), weight=BOLD),
                    OpenTypeFont(otf('bolditalic'), weight=BOLD, slant=ITALIC))
