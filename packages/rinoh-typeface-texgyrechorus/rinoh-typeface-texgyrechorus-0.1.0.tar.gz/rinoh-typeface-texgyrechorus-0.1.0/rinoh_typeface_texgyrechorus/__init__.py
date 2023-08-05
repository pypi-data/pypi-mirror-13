from os import path

from rinoh.font import Typeface
from rinoh.font.style import MEDIUM, ITALIC
from rinoh.font.opentype import OpenTypeFont


__all__ = ['typeface']


def otf(style):
    filename = 'texgyrechorus-{}.otf'.format(style)
    return path.join(path.dirname(__file__), filename)


typeface = Typeface('TeX Gyre Chorus',
                    OpenTypeFont(otf('mediumitalic'),
                                 weight=MEDIUM, slant=ITALIC))
