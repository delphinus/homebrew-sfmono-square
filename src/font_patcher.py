# -*- coding=utf8 -*-

import errno
import os

import fontforge
import psMat

# Define the character ranges
# Symbol font ranges

PATCH_SET = [
    {
        "name": "Seti-UI + Custom",
        "filename": "original-source.otf",
        "sym_start": 0xE4FA,
        "sym_end": 0xE52E,
        "src_start": 0xE5FA,
        "exact": False,
    },
    {
        "name": "Devicons",
        "filename": "devicons.ttf",
        "sym_start": 0xE600,
        "sym_end": 0xE6C5,
        "src_start": 0xE700,
        "exact": False,
    },
    {
        "name": "Powerline Symbols",
        "filename": "PowerlineSymbols.otf",
        "sym_start": 0xE0A0,
        "sym_end": 0xE0A2,
        "src_start": None,
        "exact": True,
    },
    {
        "name": "Powerline Symbols",
        "filename": "PowerlineSymbols.otf",
        "sym_start": 0xE0B0,
        "sym_end": 0xE0B3,
        "src_start": None,
        "exact": True,
    },
    {
        "name": "Powerline Extra Symbols",
        "filename": "PowerlineExtraSymbols.otf",
        "sym_start": 0xE0A3,
        "sym_end": 0xE0A3,
        "src_start": None,
        "exact": True,
    },
    {
        "name": "Powerline Extra Symbols",
        "filename": "PowerlineExtraSymbols.otf",
        "sym_start": 0xE0B4,
        "sym_end": 0xE0C8,
        "src_start": None,
        "exact": True,
    },
    {
        "name": "Powerline Extra Symobls",
        "filename": "PowerlineExtraSymbols.otf",
        "sym_start": 0xE0CA,
        "sym_end": 0xE0CA,
        "src_start": None,
        "exact": True,
    },
    {
        "name": "Powerline Extra Symobls",
        "filename": "PowerlineExtraSymbols.otf",
        "sym_start": 0xE0CC,
        "sym_end": 0xE0D4,
        "src_start": None,
        "exact": True,
    },
    {
        "name": "Pomicons",
        "filename": "Pomicons.otf",
        "sym_start": 0xE000,
        "sym_end": 0xE00A,
        "src_start": None,
        "exact": True,
    },
    {
        "name": "Font Awesome",
        "filename": "FontAwesome.otf",
        "sym_start": 0xF000,
        "sym_end": 0xF2E0,
        "src_start": None,
        "exact": True,
    },  # Maximize
    {
        "name": "Font Awesome Extension",
        "filename": "font-awesome-extension.ttf",
        "sym_start": 0xE000,
        "sym_end": 0xE0A9,
        "src_start": 0xE200,
        "exact": False,
    },
    {
        "name": "Font Linux",
        "filename": "font-logos.ttf",
        # Power, Power On/Off, Power On, Sleep
        "sym_start": 0xF100,
        "sym_end": 0xF11C,
        "src_start": 0xF300,
        "exact": True,
    },
    {
        "name": "Power Symbols",
        "filename": "Unicode_IEC_symbol_font.otf",
        # Heavy Circle (aka Power Off)
        "sym_start": 0x23FB,
        "sym_end": 0x23FE,
        "src_start": None,
        "exact": True,
    },
    {
        "name": "Power Symbols",
        "filename": "Unicode_IEC_symbol_font.otf",
        "sym_start": 0x2B58,
        "sym_end": 0x2B58,
        "src_start": None,
        "exact": True,
    },
    {
        "name": "Octicons",
        "filename": "octicons.ttf",
        "sym_start": 0xF000,
        "sym_end": 0xF105,
        "src_start": 0xF400,
        "exact": False,
    },
    {
        "name": "Octicons",
        "filename": "octicons.ttf",
        "sym_start": 0x2665,
        "sym_end": 0x2665,
        "src_start": None,
        "exact": False,
    },  # Heart
    {
        "name": "Octicons",
        "filename": "octicons.ttf",
        "sym_start": 0x26A1,
        "sym_end": 0x26A1,
        "src_start": None,
        "exact": False,
    },  # Zap
    {
        "name": "Octicons",
        "filename": "octicons.ttf",
        "sym_start": 0xF27C,
        "sym_end": 0xF27C,
        "src_start": 0xF4A9,
        "exact": False,
    },  # Desktop
    {
        "name": "Material",
        "filename": "materialdesignicons-webfont.ttf",
        "sym_start": 0xF001,
        "sym_end": 0xF1D5,
        "src_start": 0xF500,
        "exact": False,
    },
    {
        "name": "Material",
        "filename": "materialdesignicons-webfont.ttf",
        "sym_start": 0xF1DA,
        "sym_end": 0xF3FF,
        "src_start": 0xF6D9,
        "exact": False,
    },
    {
        "name": "Material",
        "filename": "materialdesignicons-webfont.ttf",
        "sym_start": 0xF1D6,
        "sym_end": 0xF1D9,
        "src_start": 0xE7FB,
        "exact": False,
    },
    {
        "name": "Material",
        "filename": "materialdesignicons-webfont.ttf",
        "sym_start": 0xF400,
        "sym_end": 0xF847,
        "src_start": 0xE7FF,
        "exact": False,
    },
    {
        "name": "Weather Icons",
        "filename": "weathericons-regular-webfont.ttf",
        "sym_start": 0xF000,
        "sym_end": 0xF0EB,
        "src_start": 0xE300,
        "exact": False,
    },
    {
        "name": "Codicons",
        "filename": "codicon.ttf",
        "sym_start": 0xEA60,
        "sym_end": 0xEBEB,
        "src_start": 0xFEA60,
        "exact": True,
    },
]


def patch(in_file, out_dir):
    font = fontforge.open(in_file)
    _patch(font)
    try:
        os.makedirs(out_dir)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    out_file = os.path.join(out_dir, in_file)
    print(f"Generated {out_file}")
    font.generate(out_file)
    return 0


def _patch(font):
    # Prevent opening and closing the fontforge font. Makes things faster when
    # patching multiple ranges using the same symbol font.
    previous_symbol_filename = ""
    symfont = None

    for info in PATCH_SET:
        if previous_symbol_filename != info["filename"]:
            # We have a new symbol font, so close the previous one if it exists
            if symfont:
                symfont.close()
                symfont = None
            symfont = fontforge.open(f"src/glyphs/{info['filename']}")
            # Match the symbol font size to the source font size
            symfont.em = font.em
            previous_symbol_filename = info["filename"]

        _copy_glyphs(font, symfont, info)
    if symfont:
        symfont.close()


def _transform_sym(symfont, info):

    x_ratio = 1.0
    y_ratio = 1.0
    x_diff = 0
    y_diff = 0

    if info["name"] == "Seti-UI + Custom":
        x_ratio = 1.1
        y_ratio = 1.1
        x_diff = -100
        y_diff = -450

    elif info["name"] == "Devicons":
        x_ratio = 1.05
        y_ratio = 1.05
        x_diff = -100
        y_diff = -250

    elif info["name"] in ["Powerline Symbols", "Powerline Extra Symbols"]:
        x_ratio = 0.95
        y_ratio = 0.88
        x_diff = 0
        y_diff = -30

    elif info["name"] == "Font Linux":
        y_diff = -120

    elif info["name"] == "Font Awesome Extension":
        y_diff = -400

    elif info["name"] == "Pomicons":
        x_ratio = 1.2
        y_ratio = 1.2
        x_diff = -200
        y_diff = -300

    elif info["name"] == "Octicons":
        x_ratio = 0.95
        y_ratio = 0.95
        x_diff = 30
        y_diff = -100

    elif info["name"] == "Material":
        x_ratio = 1.1
        y_ratio = 1.1
        x_diff = -50
        y_diff = -250

    elif info["name"] == "Codicons":
        x_ratio = 0.85
        y_ratio = 0.85
        x_diff = 35
        y_diff = -300

    scale = psMat.scale(x_ratio, y_ratio)
    translate = psMat.translate(x_diff, y_diff)
    transform = psMat.compose(scale, translate)
    symfont.transform(transform)


def _copy_glyphs(font, symfont, info):

    selected = symfont.selection.select(
        ("ranges", "unicode"), info["sym_start"], info["sym_end"]
    )
    for i, glyph in enumerate(list(selected.byGlyphs)):
        if info["exact"]:
            src_encoding = glyph.unicode + (
                s - info["sym_start"] if (s := info["src_start"]) else 0
            )
        else:
            src_encoding = (info["src_start"] or info["sym_start"]) + i
        symfont.selection.select(glyph.unicode)
        _transform_sym(symfont, info)
        symfont.copy()
        font.selection.select(src_encoding)
        font.paste()
        font[src_encoding].glyphname = glyph.glyphname
    return
