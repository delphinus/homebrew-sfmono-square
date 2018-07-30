# -*- coding:utf-8 -*-
from os.path import splitext

import fontforge
import psMat


OLD_WIDTH = 1266
WIDTH = 1024
ITALIC = 'Italic'
SQUARE = 'Square'
SCALE_DOWN = float(WIDTH) / OLD_WIDTH


def modify(in_file):
    name, ext = splitext(in_file)
    family, style = name.split('-')
    regular_font = ''
    if ITALIC in style:
        index = style.find(ITALIC)
        regular_font = '{0}-{1}{2}'.format(family, style[:index], ext)
    font = fontforge.open(in_file)
    if regular_font:
        font.mergeFonts(regular_font)
    _set_proportion(font)
    font.removeOverlap()
    out_file = 'modified-' + in_file
    print('Generate ' + out_file)
    font.generate(out_file, flags=('opentype',))
    return 0


def _set_proportion(font):
    mat = psMat.scale(SCALE_DOWN)
    font.selection.all()
    for glyph in list(font.selection.byGlyphs):
        glyph.transform(mat)
        glyph.width = WIDTH
