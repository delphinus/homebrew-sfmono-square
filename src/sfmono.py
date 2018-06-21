# -*- coding:utf-8 -*-
from os.path import splitext

import fontforge
import psMat


OLD_WIDTH = 1266
WIDTH = 1024
ITALIC = 'Italic'
SQUARE = 'Square'
SCALE_DOWN = float(WIDTH) / OLD_WIDTH
COPY_GLYPHS = [
    (0xf6d5, 0xe800),
    (0xf6d6, 0xe801),
    (0xf6d7, 0xe802),
    (0xf6d8, 0xe803),
    (0xf8ff, 0xe804),
    (0xfb01, 0xe805),
    (0xfb02, 0xe806),
]


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
    _copy_glyphs(font)
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


def _copy_glyphs(font):
    '''
    This copies glyphs to new codepoints.  The old codepoints will be
    overwritten by glyphs in Material.
    '''
    for (old, new) in COPY_GLYPHS:
        font.selection.select(old)
        font.copy()
        font.selection.select(new)
        font.paste()
