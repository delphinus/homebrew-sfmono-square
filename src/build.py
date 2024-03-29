# -*- coding:utf-8 -*-
import sys

from concurrent.futures import ProcessPoolExecutor, as_completed
import font_patcher
import migu1m
import sfmono
import sfmono_square
import fonttools


MIGU1M = [["migu-1m-regular.ttf"], ["migu-1m-bold.ttf"]]
MIGU1M_MODIFIED = [["modified-migu-1m-regular.ttf"], ["modified-migu-1m-bold.ttf"]]
SFMONO = [
    ["SF-Mono-Regular.otf"],
    ["SF-Mono-Bold.otf"],
    ["SF-Mono-RegularItalic.otf"],
    ["SF-Mono-BoldItalic.otf"],
]
SFMONO_MIGU1M = [
    ["SFMono-1x2-Regular.otf", "modified-migu-1m-regular.ttf"],
    ["SFMono-1x2-Bold.otf", "modified-migu-1m-bold.ttf"],
    ["SFMono-1x2-RegularItalic.otf", "modified-migu-1m-oblique.ttf"],
    ["SFMono-1x2-BoldItalic.otf", "modified-migu-1m-bold-oblique.ttf"],
]
SFMONO_SQUARE = [
    ["SFMonoSquare-Regular.otf", "Regular"],
    ["SFMonoSquare-Bold.otf", "Bold"],
    ["SFMonoSquare-RegularItalic.otf", "RegularItalic"],
    ["SFMonoSquare-BoldItalic.otf", "BoldItalic"],
]
OUT_DIR = "build"


def build(version):
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


def concurrent_execute(func, args):
    executor = ProcessPoolExecutor()
    futures = [executor.submit(func, *a) for a in args]
    return 1 if any([r.result() for r in as_completed(futures)]) else 0
