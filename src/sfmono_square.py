# -*- coding:utf-8 -*-
from datetime import datetime
from os.path import splitext

import fontforge
from psMat import compose, scale, translate


FAMILY = "SF Mono"
FAMILY_SUFFIX = "Square"
FULLNAME = f"{FAMILY} {FAMILY_SUFFIX}"
FILENAME = FULLNAME.replace(" ", "")
ITALIC = "Italic"
ITALIC_ANGLE = -10
ASCENT = 1638
DESCENT = 410
ENCODING = "UnicodeFull"
SCALE_DOWN = 0.65
UNDERLINE_POS = -250
UNDERLINE_HEIGHT = 100
WIDTH = ASCENT + DESCENT
ME = "JINNOUCHI Yasushi"
MAIL = "me@delphinus.dev"
YEAR = 2021
SFMONO = "SF-Mono-Regular.otf"
MIGU1M = "migu-1m-regular.ttf"
ZENKAKU_PARENTHESIS = {
    0xFF08: "left",
    0xFF09: "right",
    0xFF3B: "left",
    0xFF3D: "right",
    0xFF5B: "left",
    0xFF5D: "right",
    # ff5f & ff60 are used with original glyphs in migu-1m
    0xFF5F: "none",
    0xFF60: "none",
}
HANKAKU_GLYPHS = [
    0x22EE,  # ⋮  VERTICAL ELLIPSIS
    0x25CC,  # ◌  DOTTED CIRCLE
    0x25EF,  # ◯  LARGE CIRCLE
]
STYLE_PROPERTY = {
    "Regular": {
        "weight": "Book",
        "os2_weight": 400,
        "panose_weight": 5,
        "panose_letterform": 2,
    },
    "Bold": {
        "weight": "Bold",
        "os2_weight": 700,
        "panose_weight": 8,
        "panose_letterform": 2,
    },
    "RegularItalic": {
        "weight": "Book",
        "os2_weight": 400,
        "panose_weight": 5,
        "panose_letterform": 9,
    },
    "BoldItalic": {
        "weight": "Bold",
        "os2_weight": 700,
        "panose_weight": 8,
        "panose_letterform": 9,
    },
}


def generate(hankaku, zenkaku, version):
    opts = read_opts(hankaku, zenkaku, version)
    font = new_font(opts)
    _merge(font, opts)
    _zenkaku_glyphs(font)
    _hankaku_glyphs(font)
    font.selection.all()
    # TODO: remove this to avoid sementation fault
    # font.removeOverlap()
    font.autoHint()
    font.autoInstr()
    print(f"Generate {opts['out_file']}")
    font.generate(opts["out_file"], flags=("opentype",))
    return 0


def read_opts(hankaku, zenkaku, version):
    (name, _) = splitext(hankaku)
    filename_style = name.split("-")[-1]
    style = filename_style.replace(ITALIC, " " + ITALIC)
    fontname = FILENAME + "-" + filename_style
    return {
        "hankaku": hankaku,
        "zenkaku": zenkaku,
        "version": version,
        "filename_style": filename_style,
        "style": style,
        "fullname": f"{FULLNAME} {style}",
        "fontname": fontname,
        "out_file": f"{fontname}.otf",
    }


def new_font(opts):
    prop = STYLE_PROPERTY[opts["filename_style"]]
    sfmono = fontforge.open(SFMONO)
    migu1m = fontforge.open(MIGU1M)
    sfmono_info = {key: value for (lang, key, value) in sfmono.sfnt_names}
    migu1m_info = {key: value for (lang, key, value) in migu1m.sfnt_names}

    font = fontforge.font()
    font.ascent = ASCENT
    font.descent = DESCENT
    font.italicangle = ITALIC_ANGLE
    font.upos = UNDERLINE_POS
    font.uwidth = UNDERLINE_HEIGHT
    font.familyname = FULLNAME
    font.copyright = f"""Copyright (c) {YEAR} {ME} <{MAIL}>
{sfmono_info['Copyright']}
{sfmono_info['UniqueID']}
{migu1m_info['Copyright']}
{migu1m_info['UniqueID']}"""  # noqa
    font.encoding = ENCODING
    font.fontname = opts["fontname"]
    font.fullname = opts["fullname"]
    font.version = opts["version"]
    font.appendSFNTName("English (US)", "SubFamily", opts["style"])
    font.appendSFNTName(
        "English (US)",
        "UniqueID",
        "; ".join(
            [
                f"FontForge {fontforge.version()}",
                opts["fullname"],
                opts["version"],
                datetime.today().strftime("%F"),
            ]
        ),
    )
    font.weight = prop["weight"]
    font.os2_weight = prop["os2_weight"]
    font.os2_width = 5  # Medium (w/h = 1.000)
    font.os2_fstype = 4  # Printable Document (suitable for SF Mono)
    font.os2_vendor = "delp"  # me
    font.os2_family_class = 2057  # SS Typewriter Gothic
    font.os2_panose = (
        2,  # Latin: Text and Display
        11,  # Nomal Sans
        prop["panose_weight"],
        9,  # Monospaced
        2,  # None
        2,  # No Variation
        3,  # Straight Arms/Wedge
        prop["panose_letterform"],
        2,  # Standard/Trimmed
        7,  # Ducking/Large
    )
    # winascent & windescent is for setting the line height for Windows.
    font.os2_winascent = ASCENT
    font.os2_windescent = DESCENT
    # the `_add` version is for setting offsets.
    font.os2_winascent_add = 0
    font.os2_windescent_add = 0
    # hhea_ascent, hhea_descent is the macOS version for winascent &
    # windescent.
    font.hhea_ascent = ASCENT
    font.hhea_descent = -DESCENT
    font.hhea_ascent_add = 0
    font.hhea_descent_add = 0
    # typoascent, typodescent is generic version for above.
    font.os2_typoascent = ASCENT
    font.os2_typodescent = -DESCENT
    font.os2_typoascent_add = 0
    font.os2_typodescent_add = 0
    # linegap is for gap between lines.  The `hhea_` version is for macOS.
    font.os2_typolinegap = 0
    font.hhea_linegap = 0
    return font


def _merge(font, opts):
    font.mergeFonts(opts["hankaku"])
    font.mergeFonts(opts["zenkaku"])
    h = fontforge.open(opts["hankaku"])
    h.selection.select(0x25B8)
    h.copy()
    font.selection.select(0x25B8)
    h.paste()


def _zenkaku_glyphs(font):
    hankaku_start = 0x21
    zenkaku_start = 0xFF01
    glyphs_num = 95
    trans = translate(WIDTH / 4, 0)
    font.selection.none()
    for i in range(0, glyphs_num):
        font.selection.select(i + hankaku_start)
        font.copy()
        font.selection.select(i + zenkaku_start)
        font.paste()
    font.selection.none()
    # select copied glyphs + 2 (0xff5f & 0xff60)
    font.selection.select(
        ("ranges", "unicode"), zenkaku_start, zenkaku_start + glyphs_num + 1
    )
    for glyph in list(font.selection.byGlyphs):
        paren = ZENKAKU_PARENTHESIS.get(glyph.encoding)
        if not paren:
            glyph.transform(trans)
        elif paren == "left":
            glyph.transform(compose(trans, trans))
        glyph.width = WIDTH


def _hankaku_glyphs(font):
    origin = translate(-DESCENT, 0)
    # scale will scale glyphs with the origin (0, DESCENT)
    scl = scale(SCALE_DOWN)
    # original glyphs have width to fit this size.
    orig_glyph_width = WIDTH - DESCENT * 2
    glyph_width = float(orig_glyph_width) * SCALE_DOWN
    trans_x = (WIDTH / 2 - glyph_width) / 2
    trans_y = (WIDTH - glyph_width) / 2 - DESCENT
    trans = translate(trans_x, trans_y)
    mat = compose(compose(origin, scl), trans)
    font.selection.none()
    for i in HANKAKU_GLYPHS:
        font.selection.select(("more", "unicode"), i)
    for glyph in font.selection.byGlyphs:
        glyph.transform(mat)
        glyph.width = round(WIDTH / 2)
