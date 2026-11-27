# -*- coding:utf-8 -*-
"""Taper the slits that thinning opened between strokes.

Light is made by thinning Migu 1M Regular, which cuts back every edge by half
the delta. Two strokes that meet at a small angle (U+5D4B, U+9D73, and the
root of the left-falling stroke of 木) have a white wedge between them, as thin
as nothing near its tip. Thinning cuts back both of its sides, so it shows as a
slit as wide as the delta, which ends bluntly. taper() fills the slit so that
it narrows to the tip of the wedge in Regular, as it does there. The strokes
get thicker towards the tip, little by little.

Strokes that thinning parted are left parted. Joining them, by extending a
stroke end to the stroke it abutted in Regular, was tried: it made the strokes
joined thicker than the others, and the parts of a glyph out of balance
(U+9A19, U+9A30, U+7672).

This works on the glyph thinned already, and only adds ink to it, so a glyph
without such a slit is left as it was. FontForge's removeOverlap() does not
always merge a polygon well, so a polygon is left out when the glyph does not
keep its contours, or gains more ink than the polygon has.

All lengths are in units of the 1000-unit em of Migu 1M.
"""
from __future__ import annotations

import math
from collections.abc import Sequence

import fontforge


Point = tuple[float, float]
Polygon = list[Point]

# How far apart _flatten() takes the points along a curve.
STEP = 2
# The wedges sharper than this (in degrees) are tapered: those between two
# strokes that run nearly side by side. A wider one is an ordinary corner
# between strokes, which thinning leaves looking right, and filling it puts a
# bump in the corner (U+79C0, U+6589).
WEDGE_ANGLE = 15
# How many points along the sides of a wedge are followed at most.
WEDGE_STEPS = 400
# A slit is tapered from where the wedge in Regular is this wide to its tip.
# The strokes get thicker by half the delta over that stretch.
TAPER_WIDTH = 24
# How far a polygon reaches into the ink, not to put its edges on the outline:
# removeOverlap() does not cope with edges on top of each other.
INSET = 2
# How far the points of a polygon may be from the outline they are put on.
SNAP = 4
# How far beyond the stretch tapered the outline of a slit is followed.
REACH = 80


def mend(regular: fontforge.glyph, thinned: fontforge.glyph, delta: float) -> int:
    """
    Mends the joints of thinned, which is regular thinned by delta. regular has
    its strokes merged. Returns how many polygons are merged.
    """
    rlayer = regular.foreground
    llayer = thinned.foreground
    if not len(rlayer) or not len(llayer):
        return 0
    # NOTE: The polygons are all put on the glyph as it is thinned. Merging one
    # changes the contours the others would be put on.
    polygons = taper(rlayer, llayer, delta)
    return sum(1 for p in polygons if _merge(thinned, p))


# ---- tapering the slits ----


def taper(rlayer: fontforge.layer, llayer: fontforge.layer, delta: float) -> list[Polygon]:
    """The polygons that taper the slits thinning opened from sharp wedges."""
    outline = _Outline(llayer)
    polygons = []
    for tip, sides in _wedges(rlayer, TAPER_WIDTH):
        a, b = sides[-1]
        normal = _unit(_sub(a, b))
        # The edges of Light are delta / 2 off those of Regular.
        qa = _add(a, _mul(normal, delta / 2))
        qb = _sub(b, _mul(normal, delta / 2))
        sa, sb = outline.nearest(qa), outline.nearest(qb)
        if sa is None or sb is None:
            continue
        (ca, ia), (cb, ib) = sa, sb
        reach = _distance(tip, a) + REACH
        # Where thinning parted the two sides of the wedge, they are left parted.
        if ca != cb:
            continue
        path = outline.path(ca, ia, ib, tip, reach)
        if path:
            polygons.append([outline.point(ca, ia), *path, outline.point(cb, ib), tip])
    return polygons


def _wedges(layer: fontforge.layer, width: float) -> list[tuple[Point, list[tuple[Point, Point]]]]:
    """
    The sharp white wedges of layer: the tip of each, and the pairs of points
    along its sides from the tip to where it is width wide.
    """
    polygons = [_flatten(c)[0] for c in layer]
    boxed = _boxed(polygons)
    wedges = []
    for contour, polygon in zip(layer, polygons):
        if len(polygon) < 3:
            continue
        points, corners = _flatten(contour)
        n = len(points)
        ink_left = _ink_left(points, polygon, boxed)
        for k in corners:
            v, a, b = points[k], points[k - 1], points[(k + 1) % n]
            turn = _turn(a, v, b)
            # A tip of a white wedge turns away from the ink, by nearly 180
            # degrees.
            if turn is None or (turn > 0) == ink_left or abs(turn) <= 180 - WEDGE_ANGLE:
                continue
            sides = []
            for i in range(1, min(WEDGE_STEPS, n // 2)):
                pa, pb = points[(k - i) % n], points[(k + i) % n]
                sides.append((pa, pb))
                if _distance(pa, pb) >= width:
                    wedges.append((v, sides))
                    break
    return wedges


# ---- merging ----


def _merge(glyph: fontforge.glyph, polygon: Polygon) -> bool:
    """
    Merges the polygon into the glyph, unless removeOverlap() breaks it: the
    glyph must keep its contours as they run, and may not lose ink or gain more
    than the polygon has.
    """
    before = glyph.foreground
    largest = max(before, key=lambda c: abs(_signed_area(_flatten(c)[0])))
    clockwise = largest.isClockwise()
    layer = glyph.foreground
    contour = fontforge.contour()
    contour.is_quadratic = layer.is_quadratic
    for x, y in polygon:
        contour += fontforge.point(x, y)
    contour.closed = True
    if contour.isClockwise() != clockwise:
        contour.reverseDirection()
    layer += contour
    glyph.foreground = layer
    glyph.removeOverlap()
    after = [c.isClockwise() for c in glyph.foreground]
    was = [c.isClockwise() for c in before]
    gained = _ink(glyph.foreground) - _ink(before)
    if sorted(after) == sorted(was) and 0 <= gained <= abs(_signed_area(polygon)):
        return True
    glyph.foreground = before
    return False


def _ink(layer: fontforge.layer) -> float:
    # The contours of a glyph run all the same way round, so the counters are
    # subtracted from the area.
    return abs(sum(_signed_area(_flatten(c)[0]) for c in layer))


# ---- outlines ----


class _Outline:
    """The contours of a layer as polylines, and where their ink is."""

    def __init__(self, layer: fontforge.layer) -> None:
        self.polygons = [_flatten(c)[0] for c in layer]
        self.boxed = _boxed(self.polygons)
        self.ink_left = [len(p) >= 3 and _ink_left(p, p, self.boxed) for p in self.polygons]

    def point(self, c: int, i: int) -> Point:
        return self.polygons[c][i]

    def inset(self, c: int, i: int) -> Point:
        """The point i of contour c, moved INSET into the ink."""
        pl = self.polygons[c]
        t = _tangent(pl, i, 1)
        normal = (-t[1], t[0]) if self.ink_left[c] else (t[1], -t[0])
        return _add(pl[i], _mul(normal, INSET))

    def nearest(self, q: Point) -> tuple[int, int] | None:
        best = None
        for c, pl in enumerate(self.polygons):
            for i, p in enumerate(pl):
                if abs(p[0] - q[0]) > SNAP or abs(p[1] - q[1]) > SNAP:
                    continue
                d = _distance(p, q)
                if d <= SNAP and (best is None or d < best[0]):
                    best = (d, c, i)
        return None if best is None else (best[1], best[2])


    def path(self, c: int, i0: int, i1: int, center: Point, reach: float) -> list[Point] | None:
        """The points of contour c from i0 to i1, moved into the ink, the way that stays within reach of center."""
        pl = self.polygons[c]
        n = len(pl)
        found = []
        for step in (1, -1):
            indices = [(i0 + step * q) % n for q in range(((i1 - i0) * step) % n + 1)]
            if all(_distance(pl[j], center) <= reach for j in indices):
                found.append(indices)
        if not found:
            return None
        return [self.inset(c, j) for j in min(found, key=len)]


def _flatten(contour: fontforge.contour) -> tuple[list[Point], list[int]]:
    """
    The points along a cubic contour, about STEP apart, and the indices of
    those on its on-curve points.
    """
    key = tuple((p.x, p.y, p.on_curve) for p in contour)
    cached = _FLATTENED.get(key)
    if cached is not None:
        return cached
    src = list(contour)
    n = len(src)
    points: list[Point] = []
    corners: list[int] = []
    if n >= 2:
        start = next(i for i, p in enumerate(src) if p.on_curve)
        src = src[start:] + src[:start]
        i = 0
        while i < n:
            p0 = src[i]
            corners.append(len(points))
            if src[(i + 1) % n].on_curve:
                p1 = src[(i + 1) % n]
                steps = max(1, int(_distance((p0.x, p0.y), (p1.x, p1.y)) / STEP))
                points.extend((p0.x + (p1.x - p0.x) * j / steps, p0.y + (p1.y - p0.y) * j / steps) for j in range(steps))
                i += 1
                continue
            p1, p2, p3 = src[(i + 1) % n], src[(i + 2) % n], src[(i + 3) % n]
            length = sum(_distance((s.x, s.y), (e.x, e.y)) for s, e in ((p0, p1), (p1, p2), (p2, p3)))
            steps = max(1, int(length / STEP))
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
    if len(_FLATTENED) > 20000:
        _FLATTENED.clear()
    _FLATTENED[key] = (points, corners)
    return points, corners


_FLATTENED: dict = {}


def _boxed(polygons: Sequence[list[Point]]) -> list[tuple[float, float, float, float, list[Point]]]:
    out = []
    for pl in polygons:
        if len(pl) < 3:
            continue
        xs = [p[0] for p in pl]
        ys = [p[1] for p in pl]
        out.append((min(xs), min(ys), max(xs), max(ys), pl))
    return out


def _in_ink(point: Point, boxed: list) -> bool:
    """Whether point is in the ink of the polygons, by the even-odd rule."""
    x, y = point
    inside = False
    for _, y0, x1, y1, pl in ((b[0], b[1], b[2], b[3], b[4]) for b in boxed):
        if y < y0 or y > y1 or x > x1:
            continue
        for i in range(len(pl)):
            ax, ay = pl[i]
            bx, by = pl[i - 1]
            if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
                inside = not inside
    return inside


def _ink_left(points: list[Point], polygon: list[Point], boxed: list) -> bool:
    """Whether the ink is on the left of the contour. A contour inside an odd number of others is a counter."""
    depth = sum(1 for b in boxed if b[4] is not polygon and _in_ink(points[0], [b]))
    return (_signed_area(points) > 0) == (depth % 2 == 0)



def _turn(a: Point, v: Point, b: Point) -> float | None:
    """How far the path a -> v -> b turns at v, in degrees. Left is positive."""
    x1, y1 = v[0] - a[0], v[1] - a[1]
    x2, y2 = b[0] - v[0], b[1] - v[1]
    if (x1 == 0 and y1 == 0) or (x2 == 0 and y2 == 0):
        return None
    return math.degrees(math.atan2(x1 * y2 - y1 * x2, x1 * x2 + y1 * y2))



def _tangent(pl: list[Point], i: int, w: int = 3) -> Point:
    n = len(pl)
    return _unit(_sub(pl[(i + w) % n], pl[(i - w) % n]))


def _signed_area(points: Sequence[Point]) -> float:
    return sum(points[i - 1][0] * points[i][1] - points[i][0] * points[i - 1][1] for i in range(len(points))) / 2


def _distance(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _unit(v: Point) -> Point:
    length = math.hypot(*v)
    return (v[0] / length, v[1] / length) if length else (0.0, 0.0)


def _add(a: Point, b: Point) -> Point:
    return (a[0] + b[0], a[1] + b[1])


def _sub(a: Point, b: Point) -> Point:
    return (a[0] - b[0], a[1] - b[1])


def _mul(a: Point, k: float) -> Point:
    return (a[0] * k, a[1] * k)

