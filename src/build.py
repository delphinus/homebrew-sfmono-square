# -*- coding:utf-8 -*-
from __future__ import annotations

import sys
from collections.abc import Callable, Sequence
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Any

import font_patcher
import fonttools
import migu1m
import sfmono
import sfmono_square


# The weights of SF Mono, and the weight of Migu 1M each of them is combined
# with. Migu 1M has only regular and bold, and the others are made from regular
# by migu1m.weight(). Heavy uses bold as it is.
WEIGHTS = {
    "Regular": "regular",
    "Bold": "bold",
    "Light": "light",
    "Medium": "medium",
    "Semibold": "semibold",
    "Heavy": "bold",
}
MIGU1M_WEIGHTS = [["migu-1m-regular.ttf", s] for s in migu1m.WEIGHT_DELTA]
MIGU1M_STYLES = list(dict.fromkeys(WEIGHTS.values()))
MIGU1M = [[f"migu-1m-{s}.ttf"] for s in MIGU1M_STYLES]
MIGU1M_MODIFIED = [[f"modified-migu-1m-{s}.ttf"] for s in MIGU1M_STYLES]
STYLES = [f"{w}{i}" for i in ["", "Italic"] for w in WEIGHTS]
SFMONO = [[f"SF-Mono-{s}.otf"] for s in STYLES]


def _migu1m_for(style: str) -> str:
    if not style.endswith("Italic"):
        return f"modified-migu-1m-{WEIGHTS[style]}.ttf"
    m = WEIGHTS[style.removesuffix("Italic")]
    return f"modified-migu-1m-{'' if m == 'regular' else m + '-'}oblique.ttf"


SFMONO_MIGU1M = [[f"SFMono-1x2-{s}.otf", _migu1m_for(s)] for s in STYLES]
SFMONO_SQUARE = [[f"SFMonoSquare-{s}.otf", s] for s in STYLES]
OUT_DIR = "build"


def build(version: str) -> int:
    # NOTE: The glyphs of Nerd Fonts are fitted to the cell here, as it needs
    # nothing built before. Changing the weight runs 3 tasks of different
    # lengths, and this takes a CPU that one of them has left.
    print("---- changing the weight of migu-1m & fitting nerd-fonts glyphs ----")
    tasks = [(migu1m.weight, a) for a in MIGU1M_WEIGHTS]
    tasks.append((font_patcher.prepare, [sfmono_square.ASCENT, sfmono_square.DESCENT]))
    if concurrent_run(tasks):
        return 1
    print("---- modifying migu-1m ----")
    if concurrent_execute(migu1m.modify, MIGU1M):
        return 1
    print("---- making oblique version of migu-1m ----")
    if concurrent_execute(migu1m.oblique, MIGU1M_MODIFIED):
        return 1
    print("---- modifying SF Mono ----")
    if concurrent_execute(sfmono.modify, SFMONO):
        return 1
    print("---- generate SF Mono Square ----")
    args = [a + [version] for a in SFMONO_MIGU1M]
    if concurrent_execute(sfmono_square.generate, args):
        return 1
    print("---- adding nerd-fonts glyphs ----")
    args = [[a[0], OUT_DIR] for a in SFMONO_SQUARE]
    if concurrent_execute(font_patcher.patch, args):
        return 1
    print("---- overwriting table with fonttools")
    args = [[f"{OUT_DIR}/{a[0]}", a[1]] for a in SFMONO_SQUARE]
    if concurrent_execute(fonttools.update, args):
        return 1
    return 0


def concurrent_execute(func: Callable[..., Any], args: Sequence[Sequence[Any]]) -> int:
    return concurrent_run([(func, a) for a in args])


def concurrent_run(tasks: Sequence[tuple[Callable[..., Any], Sequence[Any]]]) -> int:
    # NOTE: A fresh process for each task. fontforge.open() and mergeFonts()
    # take the font already open in the process for the same path, so a
    # worker that ran another task hands over the fonts it changed: the shades
    # of an italic were left unscaled when the worker had built its upright.
    executor = ProcessPoolExecutor(max_tasks_per_child=1)
    futures = [executor.submit(func, *a) for func, a in tasks]
    return 1 if any(r.result() for r in as_completed(futures)) else 0
