# -*- coding:utf-8 -*-
from __future__ import annotations

import json
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from os import cpu_count, getenv
from os.path import splitext
from shutil import copy
from tempfile import TemporaryDirectory

import fontforge
import psMat

import joints


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
JOINT_PROCESSES = cpu_count() or 1


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
    if delta < 0:
        _mend_joints(in_file, font, -delta, style)
    out_file = f"migu-1m-{style}.ttf"
    print(f"Generate {out_file}")
    font.generate(out_file, flags=("opentype",))
    return 0


def _mend_joints(in_file: str, font: fontforge.font, delta: int, style: str) -> None:
    """
    Tapers the slits that thinning by delta opened between strokes. See joints.
    It takes about 0.1 second a glyph, so the glyphs are split among processes.
    """
    with TemporaryDirectory() as tmp:
        regular = fontforge.open(copy(in_file, tmp))
        regular.is_quadratic = False
        regular.selection.all()
        regular.unlinkReferences()
        _align_direction(regular)
        # NOTE: The wedges are found on the outline of the ink, so the strokes
        # of Regular are merged.
        regular.removeOverlap()
        regular_sfd = f"{tmp}/regular.sfd"
        regular.save(regular_sfd)
        regular.close()
        thinned_sfd = f"{tmp}/thinned.sfd"
        font.save(thinned_sfd)
        names = [g.glyphname for g in font.glyphs() if len(g.foreground)]
        mended, merged, crashed = _mend_all(regular_sfd, thinned_sfd, names, delta, tmp)
    for name, contours in mended.items():
        font[name].foreground = _layer(contours, font[name].foreground.is_quadratic)
    if crashed:
        print(f"{style}: FontForge crashed mending, so left as thinned: {crashed}")
    print(f"{style}: tapered {merged} slits of {len(mended)} glyphs")


def _mend_all(regular_sfd: str, thinned_sfd: str, names: list[str], delta: int, tmp: str) -> tuple[dict[str, list], int, list[str]]:
    """
    Mends the glyphs in processes. removeOverlap() now and then crashes
    FontForge on a glyph (it did on 2 glyphs of Light), which breaks the whole
    pool. So each process logs the glyphs it starts and those it finishes with
    their contours. After a crash, the glyphs finished are kept, those that
    were started are tried again one by one, and the rest go on in new
    processes. A glyph that crashes on its own is left as it is.
    """
    mended: dict[str, list] = {}
    merged = 0
    crashed: list[str] = []
    remaining = names
    round_ = 0
    while remaining:
        round_ += 1
        chunks = [c for c in (remaining[i::JOINT_PROCESSES] for i in range(JOINT_PROCESSES)) if c]
        logs = [f"{tmp}/mend-{round_}-{i}.log" for i in range(len(chunks))]
        executor = ProcessPoolExecutor(max_tasks_per_child=1)
        futures = [executor.submit(_mend_chunk, regular_sfd, thinned_sfd, c, delta, log) for c, log in zip(chunks, logs)]
        for f in futures:
            try:
                f.result()
            except BrokenProcessPool:
                pass
        executor.shutdown()
        started: set[str] = set()
        finished: set[str] = set()
        for log in logs:
            for name, contours, count in _read_log(log, started):
                finished.add(name)
                merged += count
                if contours:
                    mended[name] = contours
        suspects = sorted(started - finished)
        for name in suspects:
            log = f"{tmp}/mend-{name}.log"
            with ProcessPoolExecutor(max_workers=1) as single:
                try:
                    single.submit(_mend_chunk, regular_sfd, thinned_sfd, [name], delta, log).result()
                except BrokenProcessPool:
                    crashed.append(name)
                    continue
            for _, contours, count in _read_log(log, set()):
                merged += count
                if contours:
                    mended[name] = contours
        done = finished | set(suspects)
        remaining = [n for n in remaining if n not in done]
    return mended, merged, crashed


def _mend_chunk(regular_sfd: str, thinned_sfd: str, names: list[str], delta: int, log: str) -> None:
    regular = fontforge.open(regular_sfd)
    thinned = fontforge.open(thinned_sfd)
    with open(log, "w") as f:
        for name in names:
            print(json.dumps({"start": name}), file=f, flush=True)
            count = joints.mend(regular[name], thinned[name], delta) if name in regular else 0
            contours = [[(p.x, p.y, p.on_curve) for p in c] for c in thinned[name].foreground] if count else None
            print(json.dumps({"done": name, "contours": contours, "count": count}), file=f, flush=True)


def _read_log(log: str, started: set[str]) -> list[tuple[str, list | None, int]]:
    """The glyphs finished in log. Those started are added to started."""
    out = []
    try:
        with open(log) as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        return out
    for line in lines:
        try:
            entry = json.loads(line)
        except ValueError:
            continue  # the last line of a process that crashed writing it
        if "start" in entry:
            started.add(entry["start"])
        else:
            out.append((entry["done"], entry["contours"], entry["count"]))
    return out


def _layer(contours: list, is_quadratic: bool) -> fontforge.layer:
    layer = fontforge.layer()
    layer.is_quadratic = is_quadratic
    for points in contours:
        contour = fontforge.contour()
        contour.is_quadratic = is_quadratic
        for x, y, on_curve in points:
            contour += fontforge.point(x, y, on_curve)
        contour.closed = True
        layer += contour
    return layer


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
