# -*- coding:utf-8 -*-
from pathlib import Path
from os.path import splitext
from json import load

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
BLACK_CIRCLE = 0x25CF  # ●
BRAILLE_JSON = Path(__file__).parent / "braille.json"
BRAILLE_DIAMETER = 256 / 1024
SHADES_FILE = "src/glyphs/shades.sfd"
WHITE_TRIANGLE_FILE = "src/glyphs/white_triangle.sfd"
WHITE_TRIANGLE = 0x25BD


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
    _add_white_triangle(font)
    _add_bar_to_shade_bottom(font)
    _set_proportion(font)
    _add_braille(font)
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
    shades = fontforge.open(SHADES_FILE)
    shades.selection.select(code)
    shades.copy()
    font.selection.select(code)
    font.paste()


def _add_white_triangle(font):
    wt = fontforge.open(WHITE_TRIANGLE_FILE)
    wt.selection.select(WHITE_TRIANGLE)
    wt.copy()
    font.selection.select(WHITE_TRIANGLE)
    font.paste()


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


DESCENT = 410
BRAILLE_POINTS = [
    (256, 1792 - DESCENT),
    (256, 1280 - DESCENT),
    (256, 768 - DESCENT),
    (256, 256 - DESCENT),
    (768, 1792 - DESCENT),
    (768, 1280 - DESCENT),
    (768, 768 - DESCENT),
    (768, 256 - DESCENT),
]


def _add_braille(font):
    font.selection.select(BLACK_CIRCLE)
    font.copy()
    font.selection.select(PRIVATE)
    font.paste()

    font.selection.select(PRIVATE)
    move_to_origin = translate(-512, -582.4)
    make_small = scale(BRAILLE_DIAMETER)
    for glyph in list(font.selection.byGlyphs):
        glyph.transform(compose(move_to_origin, make_small))

    with BRAILLE_JSON.open() as f:
        braille = load(f)

    for b in braille:
        for p in b["points"]:
            point = BRAILLE_POINTS[p]
            font.selection.select(PRIVATE)
            for glyph in list(font.selection.byGlyphs):
                glyph.transform(translate(point[0], point[1]))
            font.copy()
            font.selection.select(int(b["code"], 16))
            font.pasteInto()
            for glyph in list(font.selection.byGlyphs):
                glyph.width = WIDTH
            font.selection.select(PRIVATE)
            for glyph in list(font.selection.byGlyphs):
                glyph.transform(translate(-point[0], -point[1]))
    font.selection.select(PRIVATE)
    font.cut()


def _set_proportion(font):
    mat = scale(SCALE_DOWN)
    font.selection.all()
    scaled = set()
    for glyph in list(font.selection.byGlyphs):
        # some glyphs will be selected multiple times.
        codepoint = glyph.unicode
        if codepoint != -1 and codepoint in scaled:
            print(f"this is already scaled: {codepoint:#x}")
        else:
            glyph.transform(mat)
            scaled.add(codepoint)
        glyph.width = WIDTH
