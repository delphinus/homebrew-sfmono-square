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
    print("---- changing the weight of migu-1m ----")
    if concurrent_execute(migu1m.weight, MIGU1M_WEIGHTS):
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
    executor = ProcessPoolExecutor()
    futures = [executor.submit(func, *a) for a in args]
    return 1 if any(r.result() for r in as_completed(futures)) else 0
