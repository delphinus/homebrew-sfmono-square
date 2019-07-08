# -*- coding:utf-8 -*-
from os.path import splitext

import fontforge
import psMat


OLD_WIDTH = 1266
WIDTH = 1024
ITALIC = "Italic"
SCALE_DOWN = float(WIDTH) / OLD_WIDTH
FAMILY = "SF Mono"
PS_FAMILY = "SFMono"
FAMILY_SUFFIX = "1x2"


def modify(in_file):
    name, ext = splitext(in_file)
    style = name.split("-")[1]
    regular_font = ""
    if ITALIC in style:
        index = style.find(ITALIC)
        regular_font = f"{PS_FAMILY}-{style[:index]}{ext}"
    font = fontforge.open(in_file)
    if regular_font:
        font.mergeFonts(regular_font)
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


def _set_proportion(font):
    mat = psMat.scale(SCALE_DOWN)
    font.selection.all()
    for glyph in list(font.selection.byGlyphs):
        glyph.transform(mat)
        glyph.width = WIDTH
