# -*- coding:utf-8 -*-
from os import getenv
from os.path import splitext

import fontforge
import psMat


ASCENT = 1638
DESCENT = 410
OLD_EM = 1000
EM = ASCENT + DESCENT
HANKAKU_KANA = (0xFF60, 0xFF9F)
OBLIQUE_SKEW = 0.2

try:
    SCALE = float(getenv("MIGU1M_SCALE", 0.82))
except ValueError:
    SCALE = 0.82
X_TO_CENTER = EM * (1 - SCALE) / 2


def modify(in_file):
    font = fontforge.open(in_file)
    _set_new_em(font)
    _set_proportion(font)
    _zenkaku_space(font)
    out_file = f"modified-{in_file}"
    print(f"Generate {out_file}")
    font.generate(out_file, flags=("opentype",))
    return 0


def oblique(in_file):
    font = fontforge.open(in_file)
    _make_oblique(font)
    name, ext = splitext(in_file)
    in_style = name.split("-")[-1]
    style = "oblique" if in_style == "regular" else "bold-oblique"
    out_file = f"modified-migu-1m-{style}{ext}"
    print(f"Generate {out_file}")
    font.generate(out_file, flags=("opentype",))
    return 0


def _set_new_em(font):
    """
    This sets new ascent & descent and scale glyphs.  This sets new ascent &
    descent before it sets em.  When in inverse, it does not change ascent &
    descent.
    """
    font.selection.all()
    font.unlinkReferences()
    font.ascent = float(ASCENT) / EM * OLD_EM
    font.descent = float(DESCENT) / EM * OLD_EM
    font.em = EM


def _set_proportion(font):
    scale = psMat.scale(SCALE)
    font.selection.all()
    for glyph in list(font.selection.byGlyphs):
        is_hankaku_kana = glyph.encoding in range(*HANKAKU_KANA)
        x_to_center = X_TO_CENTER / 2 if is_hankaku_kana else X_TO_CENTER
        trans = psMat.translate(x_to_center, 0)
        mat = psMat.compose(scale, trans)
        glyph.transform(mat)
        glyph.width = EM / 2 if is_hankaku_kana else EM


def _zenkaku_space(font):
    font.selection.none()
    font.selection.select(0x2610)  # ☐  BALLOT BOX
    font.copy()
    font.selection.select(0x3000)  # 　 IDEOGRAPHIC SPACE
    font.paste()
    font.selection.select(0x271A)  # ✚  HEAVY GREEK CROSS
    font.copy()
    font.selection.select(0x3000)
    font.pasteInto()
    font.intersect()


def _make_oblique(font):
    mat = psMat.skew(OBLIQUE_SKEW)
    font.selection.all()
    font.transform(mat)
    font.removeOverlap()
