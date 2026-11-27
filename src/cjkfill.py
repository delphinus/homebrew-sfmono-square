# -*- coding:utf-8 -*-
"""Fill the ideographs Migu 1M lacks.

Migu 1M has the kanji of JIS X 0213 only, about 9,600 of the 21,000 of the
CJK Unified Ideographs, and few of Extension A. Any other kanji falls back to a
font the system picks for it, a different one for each, none of them scaled
down as Migu 1M is here, so a line of them looks uneven. The kanji Migu 1M
lacks in the BMP are taken from Source Han Sans, scaled to the size of Migu
1M, and merged into SF Mono Square.

The extensions B and later are too many (more than 70,000) to put into a font
with Migu 1M and SF Mono, as a font holds 65,535 glyphs at most. They are made
from Plangothic into fonts of their own with the same metrics as SF Mono
Square, to be mapped to them by the terminal (symbol_map in kitty).
"""
from __future__ import annotations

from datetime import datetime

import fontforge
import psMat

import migu1m


# The weights of Source Han Sans the weights of Migu 1M are filled with. Each
# is the one with the closest ink density (the ratio of the ink to the em
# square) over 600 kanji. The kanji of SF Mono Square 3.6.0 have 0.274
# (Light), 0.338 (Regular), 0.381 (Medium), 0.434 (Semibold) and 0.516 (Bold),
# and Source Han Sans has 0.233 (Light), 0.304 (Normal), 0.334 (Regular), 0.404
# (Medium), 0.488 (Bold) and 0.566 (Heavy).
SOURCE_HAN_SANS = {
    "light": "SourceHanSans-Normal.otf",
    "regular": "SourceHanSans-Regular.otf",
    "medium": "SourceHanSans-Medium.otf",
    "semibold": "SourceHanSans-Medium.otf",
    "bold": "SourceHanSans-Bold.otf",
}
# The blocks to fill in the BMP.
RANGES = [
    (0x2E80, 0x2FDF),  # CJK Radicals Supplement, Kangxi Radicals
    (0x2FF0, 0x2FFF),  # Ideographic Description Characters
    (0x31C0, 0x31EF),  # CJK Strokes
    (0x3400, 0x4DBF),  # CJK Unified Ideographs Extension A
    (0x4E00, 0x9FFF),  # CJK Unified Ideographs
    (0xF900, 0xFAFF),  # CJK Compatibility Ideographs
]
MIGU1M_FILES = ["migu-1m-regular.ttf", "migu-1m-bold.ttf"]
# Source Han Sans draws its kanji a little larger and higher than Migu 1M. The
# mean bounding box of 1,500 kanji both have is 917 x 912 centred at (499,
# 377) in Source Han Sans, and 911 x 894 centred at (499, 370) in Migu 1M, in
# units of their 1000-unit em. Plangothic is made from Source Han Sans and has
# the same.
ADJUST_SCALE = 0.985
ADJUST_FROM = (499.1, 377.1)
ADJUST_TO = (498.6, 369.6)

PLANGOTHIC = {
    "P1": "PlangothicP1-Regular.ttf",
    "P2": "PlangothicP2-Regular.ttf",
}
EXT_RANGES = [
    (0x20000, 0x3347F),  # CJK Unified Ideographs Extension B to J
    (0x2F800, 0x2FA1F),  # CJK Compatibility Ideographs Supplement
]
EXT_FAMILYNAME = "SF Mono Square Ext"


def fill(style: str) -> int:
    """Makes cjkfill-<style>.ttf and cjkfill-<style>-oblique.ttf."""
    present = _codepoints_of(MIGU1M_FILES)
    font = _subset(_open(SOURCE_HAN_SANS[style]), lambda c: _in(c, RANGES) and c not in present)
    _transform(font)
    out_file = f"cjkfill-{style}.ttf"
    print(f"Generate {out_file} ({_count(font)} glyphs)")
    font.generate(out_file, flags=("opentype",))
    font.selection.all()
    font.transform(psMat.skew(migu1m.OBLIQUE_SKEW))
    out_file = f"cjkfill-{style}-oblique.ttf"
    print(f"Generate {out_file}")
    font.generate(out_file, flags=("opentype",))
    return 0


def ext(part: str, version: str) -> int:
    """
    Makes SFMonoSquareExt-<part>.ttf from Plangothic. This is a TrueType font,
    as it is a quarter of the size of an OpenType one with the same glyphs
    (2.9MB to 10.4MB for P2, 61,517 glyphs of P1 made it 72MB), and is made 10
    times faster.
    """
    font = _subset(_open(PLANGOTHIC[part]), lambda c: _in(c, EXT_RANGES))
    _transform(font)
    familyname = f"{EXT_FAMILYNAME} {part}"
    compact = familyname.replace(" ", "")
    font.fontname = f"{compact}-Regular"
    font.familyname = familyname
    font.fullname = f"{familyname} Regular"
    font.version = version
    font.copyright = f"{font.copyright}\n(modified for SF Mono Square)"
    # NOTE: The names of Plangothic must not be left. They are its Reserved
    # Font Names under the OFL, and this is a modified version.
    font.sfnt_names = ()
    font.appendSFNTName("English (US)", "Copyright", font.copyright)
    font.appendSFNTName("English (US)", "Family", familyname)
    font.appendSFNTName("English (US)", "SubFamily", "Regular")
    font.appendSFNTName("English (US)", "Fullname", font.fullname)
    font.appendSFNTName("English (US)", "Version", f"Version {version}")
    font.appendSFNTName(
        "English (US)",
        "UniqueID",
        f"FontForge {fontforge.version()}; {font.fullname}; {version}; {datetime.today():%F}",
    )
    font.appendSFNTName(
        "English (US)", "License", "SIL Open Font License, Version 1.1"
    )
    font.appendSFNTName(
        "English (US)", "License URL", "https://openfontlicense.org"
    )
    _set_metrics(font)
    out_file = f"SFMonoSquareExt-{part}.ttf"
    print(f"Generate {out_file} ({_count(font)} glyphs)")
    font.generate(out_file, flags=("opentype",))
    return 0


def _codepoints_of(files: list[str]) -> set[int]:
    codepoints = set()
    for path in files:
        font = fontforge.open(path)
        for glyph in font.glyphs():
            if glyph.unicode >= 0:
                codepoints.add(glyph.unicode)
            codepoints.update(a[0] for a in glyph.altuni or ())
        font.close()
    return codepoints


def _open(path: str) -> fontforge.font:
    font = fontforge.open(path)
    if font.cidfontname:
        font.cidFlatten()
    font.encoding = "UnicodeFull"
    return font


def _in(codepoint: int, ranges: list[tuple[int, int]]) -> bool:
    return any(a <= codepoint <= b for a, b in ranges)


def _subset(source: fontforge.font, wanted) -> fontforge.font:
    """
    Makes a font of the glyphs of source for the wanted codepoints. Each
    codepoint gets a glyph of its own: mergeFonts() drops the codepoints of a
    glyph but the first, and Source Han Sans has some glyphs two codepoints
    share (U+5F50 and the radical U+2F39, say). This also leaves the lookups
    behind, which SF Mono Square has no use for.
    """
    font = fontforge.font()
    font.encoding = "UnicodeFull"
    font.em = source.em
    font.ascent = source.ascent
    font.descent = source.descent
    font.copyright = source.copyright
    done = set()
    for glyph in source.glyphs():
        codepoints = [glyph.unicode] if glyph.unicode >= 0 else []
        codepoints += [a[0] for a in glyph.altuni or ()]
        for codepoint in codepoints:
            if not wanted(codepoint) or codepoint in done:
                continue
            done.add(codepoint)
            new = font.createChar(codepoint, f"uni{codepoint:04X}" if codepoint < 0x10000 else f"u{codepoint:X}")
            new.foreground = glyph.foreground
            new.width = glyph.width
    return font


def _transform(font: fontforge.font) -> None:
    """Scales the glyphs as migu1m.modify() does Migu 1M."""
    s = ADJUST_SCALE
    adjust = psMat.compose(
        psMat.scale(s),
        psMat.translate(ADJUST_TO[0] - s * ADJUST_FROM[0], ADJUST_TO[1] - s * ADJUST_FROM[1]),
    )
    font.selection.all()
    font.unlinkReferences()
    font.transform(adjust)
    font.ascent = round(float(migu1m.ASCENT) / migu1m.EM * font.em)
    font.descent = round(float(migu1m.DESCENT) / migu1m.EM * font.em)
    font.em = migu1m.EM
    font.selection.all()
    font.transform(psMat.compose(psMat.scale(migu1m.SCALE), psMat.translate(migu1m.X_TO_CENTER, 0)))
    for glyph in font.glyphs():
        glyph.width = migu1m.EM


def _set_metrics(font: fontforge.font) -> None:
    """Gives the font the same line metrics as SF Mono Square."""
    ascent = round(float(migu1m.ASCENT) / migu1m.EM * font.em)
    descent = font.em - ascent
    for attr in ("os2_winascent", "os2_typoascent", "hhea_ascent"):
        setattr(font, attr, ascent)
    font.os2_windescent = descent
    font.os2_typodescent = -descent
    font.hhea_descent = -descent
    for attr in (
        "os2_winascent_add",
        "os2_windescent_add",
        "os2_typoascent_add",
        "os2_typodescent_add",
        "hhea_ascent_add",
        "hhea_descent_add",
    ):
        setattr(font, attr, 0)
    font.os2_typolinegap = 0
    font.hhea_linegap = 0


def _count(font: fontforge.font) -> int:
    return sum(1 for _ in font.glyphs())
