# -*- coding:utf-8 -*-
from __future__ import annotations

from os import getenv
from os.path import splitext
from shutil import copy
from tempfile import TemporaryDirectory

import fontforge
import psMat


ASCENT = 1638
DESCENT = 410
OLD_EM = 1000
EM = ASCENT + DESCENT
HANKAKU_KANA = (0xFF61, 0xFFA0)
OBLIQUE_SKEW = 0.2

try:
    SCALE = float(getenv("MIGU1M_SCALE", "82")) / 100
except ValueError:
    SCALE = 0.82
X_TO_CENTER = EM * (1 - SCALE) / 2
# Migu 1M has only Regular and Bold. The other weights are made by thinning or
# thickening the strokes of Regular, in units of its own 1000-unit em. Heavy
# uses Bold as it is, as thickening Bold fills the counters of dense kanji.
# See https://github.com/delphinus/homebrew-sfmono-square/issues/123
WEIGHT_DELTA = {
    "light": -12,
    "medium": 8,
    "semibold": 18,
}
# Contours with a smaller bounding box than this (in units^2 of the 1000-unit
# em, about 17x17) are debris that changeWeight() and removeOverlap() leave
# at the joints of strokes.
SPECK_AREA = 300
# changeWeight() now and then breaks a glyph: a stroke shoots out of it as a
# hairline spike, far beyond the em (semibold U+9370 reached y = 2350). Which
# glyphs it breaks depends on the delta, and a broken glyph is very slow to
# process later (removeOverlap() on that one glyph took 6 minutes) and makes
# the font's bounding box twice as tall. A glyph whose bounding box grows by
# more than this (in units of the 1000-unit em) is taken as broken.
BROKEN_GROWTH = 60


def weight(in_file: str, style: str) -> int:
    """Makes migu-1m-<style>.ttf by changing the weight of in_file."""
    delta = WEIGHT_DELTA[style]
    source = fontforge.open(in_file)
    boxes = _bounding_boxes(source)
    source.close()
    font = _change_weight(in_file, delta)
    broken = _broken_glyphs(boxes, font)
    # A delta 1 off breaks other glyphs, so a broken glyph is taken from the
    # font made with one of them. 1 unit of 1000 is too thin to be seen.
    for alt_delta in (delta - 1, delta + 1):
        if not broken:
            break
        # NOTE: fontforge.open() returns the font already open for the same
        # path, so the font to change again is opened from a copy.
        with TemporaryDirectory() as tmp:
            alt = _change_weight(copy(in_file, tmp), alt_delta)
            alt_broken = _broken_glyphs(boxes, alt)
            for name in [n for n in broken if n not in alt_broken]:
                print(f"{style}: take {name} from the delta {alt_delta}")
                font[name].foreground = alt[name].foreground
                font[name].width = alt[name].width
                broken.remove(name)
            alt.close()
    if broken:
        print(f"{style}: broken glyphs are left: {broken}")
        return 1
    out_file = f"migu-1m-{style}.ttf"
    print(f"Generate {out_file}")
    font.generate(out_file, flags=("opentype",))
    return 0


def _change_weight(in_file: str, delta: int) -> fontforge.font:
    font = fontforge.open(in_file)
    font.is_quadratic = False
    font.selection.all()
    font.unlinkReferences()
    # NOTE: Do not call correctDirection() before this. Migu 1M has its
    # contours the other way round, and correctDirection() reverses them, which
    # makes changeWeight() thin the glyphs it should thicken.
    _align_direction(font)
    font.changeWeight(delta, "CJK", 0, 0, "auto")
    font.removeOverlap()
    _remove_specks(font)
    return font


def _align_direction(font: fontforge.font) -> None:
    """
    Reverses the contours drawn the other way round from the rest. Migu 1M has
    all its outermost contours clockwise but those of 6 glyphs: U+30D8-30DA
    (katakana he, be and pe) and the vertical forms of U+301C, U+30FC and
    U+FF5E. changeWeight() thinned them where it thickened the others. The
    dakuten and the handakuten of be and pe are drawn as the others, so only
    the contour of the stroke is reversed, with the contours inside it.
    """
    for glyph in font.glyphs():
        layer = glyph.foreground
        contours = list(layer)
        boxes = [c.boundingBox() for c in contours]
        reversed_any = False
        for i, contour in enumerate(contours):
            if contour.isClockwise() or any(_inside(boxes[i], b) for j, b in enumerate(boxes) if j != i):
                continue
            for j, inner in enumerate(contours):
                if j == i or _inside(boxes[j], boxes[i]):
                    inner.reverseDirection()
            reversed_any = True
        if reversed_any:
            new_layer = fontforge.layer()
            new_layer.is_quadratic = layer.is_quadratic
            for contour in contours:
                new_layer += contour
            glyph.foreground = new_layer


def _inside(a: tuple[float, ...], b: tuple[float, ...]) -> bool:
    return a != b and a[0] >= b[0] and a[1] >= b[1] and a[2] <= b[2] and a[3] <= b[3]


def _bounding_boxes(font: fontforge.font) -> dict[str, tuple[float, ...]]:
    # This includes references, which are not unlinked yet.
    boxes = {g.glyphname: g.boundingBox() for g in font.glyphs()}
    return {n: b for n, b in boxes.items() if b != (0, 0, 0, 0)}


def _broken_glyphs(boxes: dict[str, tuple[float, ...]], font: fontforge.font) -> list[str]:
    broken = []
    for name, o in boxes.items():
        n = font[name].boundingBox()
        if max(o[0] - n[0], o[1] - n[1], n[2] - o[2], n[3] - o[3]) > BROKEN_GROWTH:
            broken.append(name)
    return broken


def _remove_specks(font: fontforge.font) -> None:
    for glyph in font.glyphs():
        layer = glyph.foreground
        kept = fontforge.layer()
        kept.is_quadratic = layer.is_quadratic
        removed = False
        for contour in layer:
            xmin, ymin, xmax, ymax = contour.boundingBox()
            # A contour with less than 3 points on the curve has no area. It
            # goes away when the font is generated, but its control points
            # widen the bounding box _broken_glyphs() looks at.
            on_curve = sum(1 for p in contour if p.on_curve)
            if on_curve < 3 or (xmax - xmin) * (ymax - ymin) < SPECK_AREA:
                removed = True
            else:
                kept += contour
        if removed:
            glyph.foreground = kept


def modify(in_file: str) -> int:
    font = fontforge.open(in_file)
    _set_new_em(font)
    _set_proportion(font)
    _zenkaku_space(font)
    out_file = f"modified-{in_file}"
    print(f"Generate {out_file}")
    font.generate(out_file, flags=("opentype",))
    return 0


def oblique(in_file: str) -> int:
    font = fontforge.open(in_file)
    _make_oblique(font)
    name, ext = splitext(in_file)
    in_style = name.split("-")[-1]
    style = "oblique" if in_style == "regular" else f"{in_style}-oblique"
    out_file = f"modified-migu-1m-{style}{ext}"
    print(f"Generate {out_file}")
    font.generate(out_file, flags=("opentype",))
    return 0


def _set_new_em(font: fontforge.font) -> None:
    """
    This sets new ascent & descent and scale glyphs.  This sets new ascent &
    descent before it sets em.  When in inverse, it does not change ascent &
    descent.
    """
    font.selection.all()
    font.unlinkReferences()
    font.ascent = round(float(ASCENT) / EM * OLD_EM)
    font.descent = round(float(DESCENT) / EM * OLD_EM)
    font.em = EM


def _set_proportion(font: fontforge.font) -> None:
    scale = psMat.scale(SCALE)
    font.selection.all()
    for glyph in list(font.selection.byGlyphs):
        is_hankaku_kana = glyph.encoding in range(*HANKAKU_KANA)
        x_to_center = X_TO_CENTER / 2 if is_hankaku_kana else X_TO_CENTER
        trans = psMat.translate(x_to_center, 0)
        mat = psMat.compose(scale, trans)
        glyph.transform(mat)
        glyph.width = round(EM / 2) if is_hankaku_kana else EM


def _zenkaku_space(font: fontforge.font) -> None:
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


def _make_oblique(font: fontforge.font) -> None:
    mat = psMat.skew(OBLIQUE_SKEW)
    font.selection.all()
    font.transform(mat)
    font.removeOverlap()
