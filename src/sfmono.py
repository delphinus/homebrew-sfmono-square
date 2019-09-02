# -*- coding:utf-8 -*-
from os.path import splitext

import fontforge
from psMat import compose, scale, translate


OLD_WIDTH = 1266
WIDTH = 1024
ITALIC = "Italic"
SCALE_DOWN = float(WIDTH) / OLD_WIDTH
FAMILY = "SF Mono"
FILE_PREFIX = "SF-Mono-"
PS_FAMILY = "SFMono"
FAMILY_SUFFIX = "1x2"
LIGHT_SHADE = 0x2591  # ░
MEDIUM_SHADE = 0x2592  # ▒
DARK_SHADE = 0x2593  # ▓
LOWER_BLOCK = 0x2581  # ▁
PRIVATE = 0xE000  # 


def modify(in_file):
    name, ext = splitext(in_file)
    style = name.replace(FILE_PREFIX, "")
    regular_font = ""
    if ITALIC in style:
        index = style.find(ITALIC)
        regular_font = f"{FILE_PREFIX}{style[:index]}{ext}"
    font = fontforge.open(in_file)
    if regular_font:
        font.mergeFonts(regular_font)
    for code in [LIGHT_SHADE, MEDIUM_SHADE, DARK_SHADE]:
        _expand_shades(font, code)
    _add_bar_to_shade_bottom(font)
    _set_proportion(font)
    font.removeOverlap()
    font.familyname = f"{PS_FAMILY} {FAMILY_SUFFIX}"
    font.fullname = f"{PS_FAMILY} {FAMILY_SUFFIX} {style}"
    font.fontname = f"{PS_FAMILY}-{FAMILY_SUFFIX}-{style}"
    sfnt_names = list(font.sfnt_names)
    for i in range(len(sfnt_names)):
        name = list(sfnt_names[i])
        key = name[1]
        if key == "Family":
            name[2] = f"{FAMILY} {FAMILY_SUFFIX}"
        elif key == "SubFamily":
            name[2] = style
        elif key == "UniqueID" or key == "Fullname":
            name[2] = f"{FAMILY} {FAMILY_SUFFIX} {style}"
        sfnt_names[i] = tuple(name)
    font.sfnt_names = tuple(sfnt_names)
    out_file = f"{PS_FAMILY}-{FAMILY_SUFFIX}-{style}{ext}"
    print(f"Generate {out_file}")
    font.generate(out_file, flags=("opentype",))
    return 0


def _expand_shades(font, code):
    # `421` means the size of a set of pattern in shades.
    mat = translate(0, 421)

    font.selection.select(code)
    font.copy()
    for glyph in list(font.selection.byGlyphs):
        glyph.transform(mat)
    font.pasteInto()


def _add_bar_to_shade_bottom(font):
    font.selection.select(LOWER_BLOCK)
    font.copy()
    font.selection.select(PRIVATE)
    font.paste()

    font.selection.select(LOWER_BLOCK)
    move_to_origin = translate(0, 208)
    shrink_to_fit = scale(1.0, 106.0 / 256)
    move_to_bottom = translate(0, -439)
    mat = compose(compose(move_to_origin, shrink_to_fit), move_to_bottom)
    for glyph in list(font.selection.byGlyphs):
        glyph.transform(mat)
    font.copy()
    font.selection.select(DARK_SHADE)
    font.pasteInto()

    font.selection.select(PRIVATE)
    font.cut()
    font.selection.select(LOWER_BLOCK)
    font.paste()


def _set_proportion(font):
    mat = scale(SCALE_DOWN)
    font.selection.all()
    for glyph in list(font.selection.byGlyphs):
        glyph.transform(mat)
        glyph.width = WIDTH
