# -*- coding:utf-8 -*-
from __future__ import annotations

import math
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
# _plug_wedges() fills the white wedges sharper than this (in degrees). Of
# the kanji that had a gap in Light, this takes in all but 1 in a sample of
# 2,370, and leaves out the corners of counters, which do not open.
WEDGE_ANGLE = 45
# How far apart _flatten() takes the points along a curve (in units of the
# 1000-unit em), and how many of them _plug() follows at most.
WEDGE_STEP = 2
WEDGE_STEPS = 400
# How far into the ink a plug reaches (in units of the 1000-unit em).
PLUG_INSET = 2


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
    if delta < 0:
        # NOTE: The wedges are found where the outlines of strokes cross, so
        # the strokes are merged first.
        font.removeOverlap()
        _plug_wedges(font, -delta)
    font.changeWeight(delta, "CJK", 0, 0, "auto")
    font.removeOverlap()
    _remove_specks(font)
    return font


def _plug_wedges(font: fontforge.font, width: float) -> None:
    """
    Fills the sharp white wedges of the glyphs up to where they are as wide as
    width, so that thinning them by width does not open them.

    Where two strokes of Migu 1M meet at a small angle, there is a white wedge
    between them, too narrow to be seen near its tip. Thinning cuts back both
    sides of it, and the whole of it shows: a gap up to 12 units wide opened
    between the strokes in Light (U+5D4B, U+4E7E and thousands of kanji). A
    wedge filled up to where it is width wide is as wide as 2 * width there
    after thinning, and as wide as it was in Regular plus width beyond.
    """
    for glyph in font.glyphs():
        plugs = _plugs(glyph.foreground, width)
        # Most glyphs take all their plugs at once. Those that do not take them
        # one by one, and leave out the plugs they do not take.
        if plugs and not _add_plugs(glyph, plugs):
            for points in plugs:
                _add_plugs(glyph, [points])


def _add_plugs(glyph: fontforge.glyph, plugs: list[list[tuple[float, float]]]) -> bool:
    """
    Merges the plugs into the glyph. removeOverlap() now and then breaks the
    glyph doing it: it turned the counter of U+601C the wrong way round, which
    changeWeight() then filled. The plugs are left out, and False is returned,
    when the glyph does not keep its contours or gains more ink than the plugs
    have.
    """
    before = glyph.foreground
    layer = glyph.foreground
    for points in plugs:
        contour = fontforge.contour()
        contour.is_quadratic = layer.is_quadratic
        for x, y in points:
            contour += fontforge.point(x, y)
        contour.closed = True
        # The outermost contours of Migu 1M run clockwise.
        if not contour.isClockwise():
            contour.reverseDirection()
        layer += contour
    glyph.foreground = layer
    glyph.removeOverlap()
    after = glyph.foreground
    gained = _ink(after) - _ink(before)
    most = sum(abs(_signed_area(points)) for points in plugs)
    if sorted(c.isClockwise() for c in after) == sorted(c.isClockwise() for c in before) and 0 <= gained <= most:
        return True
    glyph.foreground = before
    return False


def _ink(layer: fontforge.layer) -> float:
    """The area of the ink. The counters run the other way round."""
    return abs(sum(_signed_area(_flatten(c)[0]) for c in layer))


def _plugs(layer: fontforge.layer, width: float) -> list[list[tuple[float, float]]]:
    """The polygons that fill the sharp white wedges of layer."""
    polygons = [_flatten(c)[0] for c in layer]
    plugs = []
    for contour, polygon in zip(layer, polygons):
        if len(polygon) < 3:
            continue
        points, corners = _flatten(contour)
        n = len(points)
        # Whether the ink is on the left of the contour. A contour inside an
        # odd number of others is a counter.
        p = points[0]
        depth = sum(1 for other in polygons if other is not polygon and _in_ink(p, [other]))
        ink_left = (_signed_area(points) > 0) == (depth % 2 == 0)
        for k in corners:
            v, a, b = points[k], points[k - 1], points[(k + 1) % n]
            turn = _turn(a, v, b)
            # A tip of a white wedge turns away from the ink, by nearly 180
            # degrees.
            if turn is None or (turn > 0) == ink_left or abs(turn) <= 180 - WEDGE_ANGLE:
                continue
            plug = _plug(points, k, width)
            if plug:
                plugs.append(plug)
    return plugs


def _plug(points: list[tuple[float, float]], k: int, width: float) -> list[tuple[float, float]]:
    """
    The polygon that fills the wedge whose tip is points[k], up to where the
    wedge is width wide. Its sides are moved PLUG_INSET into the ink, so that
    they do not lie on the outline: removeOverlap() does not cope with that.
    """
    n = len(points)
    v = points[k]
    sides = []
    for i in range(1, min(WEDGE_STEPS, n // 2)):
        pa, pb = points[(k - i) % n], points[(k + i) % n]
        sides.append((pa, pb))
        if _distance(pa, pb) >= width:
            break
    else:
        return []
    ua = _unit((sides[0][0][0] - v[0], sides[0][0][1] - v[1]))
    ub = _unit((sides[0][1][0] - v[0], sides[0][1][1] - v[1]))
    bisector = _unit((ua[0] + ub[0], ua[1] + ub[1]))
    plug = [(v[0] - bisector[0] * PLUG_INSET, v[1] - bisector[1] * PLUG_INSET)]
    for pa, pb in sides:
        d = _unit((pa[0] - pb[0], pa[1] - pb[1]))
        plug.append((pa[0] + d[0] * PLUG_INSET, pa[1] + d[1] * PLUG_INSET))
    for pa, pb in reversed(sides):
        d = _unit((pb[0] - pa[0], pb[1] - pa[1]))
        plug.append((pb[0] + d[0] * PLUG_INSET, pb[1] + d[1] * PLUG_INSET))
    return plug


def _flatten(contour: fontforge.contour) -> tuple[list[tuple[float, float]], list[int]]:
    """
    The points along a cubic contour, about WEDGE_STEP apart, and the indices
    of those on its on-curve points.
    """
    src = list(contour)
    n = len(src)
    if n < 2:
        return [], []
    start = next(i for i, p in enumerate(src) if p.on_curve)
    src = src[start:] + src[:start]
    points: list[tuple[float, float]] = []
    corners = []
    i = 0
    while i < n:
        p0 = src[i]
        corners.append(len(points))
        if src[(i + 1) % n].on_curve:
            p1 = src[(i + 1) % n]
            steps = max(1, int(_distance((p0.x, p0.y), (p1.x, p1.y)) / WEDGE_STEP))
            for j in range(steps):
                t = j / steps
                points.append((p0.x + (p1.x - p0.x) * t, p0.y + (p1.y - p0.y) * t))
            i += 1
            continue
        p1, p2, p3 = src[(i + 1) % n], src[(i + 2) % n], src[(i + 3) % n]
        length = sum(_distance((s.x, s.y), (e.x, e.y)) for s, e in ((p0, p1), (p1, p2), (p2, p3)))
        steps = max(1, int(length / WEDGE_STEP))
        for j in range(steps):
            t = j / steps
            u = 1 - t
            points.append(
                (
                    u * u * u * p0.x + 3 * u * u * t * p1.x + 3 * u * t * t * p2.x + t * t * t * p3.x,
                    u * u * u * p0.y + 3 * u * u * t * p1.y + 3 * u * t * t * p2.y + t * t * t * p3.y,
                )
            )
        i += 3
    return points, corners


def _turn(a: tuple[float, float], v: tuple[float, float], b: tuple[float, float]) -> float | None:
    """How far the path a -> v -> b turns at v, in degrees. Left is positive."""
    x1, y1 = v[0] - a[0], v[1] - a[1]
    x2, y2 = b[0] - v[0], b[1] - v[1]
    if (x1 == 0 and y1 == 0) or (x2 == 0 and y2 == 0):
        return None
    return math.degrees(math.atan2(x1 * y2 - y1 * x2, x1 * x2 + y1 * y2))


def _signed_area(points: list[tuple[float, float]]) -> float:
    return sum(points[i - 1][0] * points[i][1] - points[i][0] * points[i - 1][1] for i in range(len(points))) / 2


def _distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _unit(v: tuple[float, float]) -> tuple[float, float]:
    length = math.hypot(*v)
    return (v[0] / length, v[1] / length) if length else (0.0, 0.0)


def _in_ink(point: tuple[float, float], polygons: list[list[tuple[float, float]]]) -> bool:
    """Whether point is in the ink of polygons, by the even-odd rule."""
    x, y = point
    inside = False
    for polygon in polygons:
        for i in range(len(polygon)):
            x1, y1 = polygon[i]
            x2, y2 = polygon[i - 1]
            if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
                inside = not inside
    return inside


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
