# -*- coding:utf-8 -*-
import sys

from concurrent.futures import ProcessPoolExecutor, as_completed
import font_patcher
import migu1m
import sfmono
import sfmono_square


MIGU1M = [["migu-1m-regular.ttf"], ["migu-1m-bold.ttf"]]
MIGU1M_MODIFIED = [["modified-migu-1m-regular.ttf"], ["modified-migu-1m-bold.ttf"]]
SFMONO = [
    ["SF-Mono-Regular.otf"],
]
SFMONO_MIGU1M = [
    ["SFMono-1x2-Regular.otf", "modified-migu-1m-regular.ttf"],
    ["SFMono-1x2-Bold.otf", "modified-migu-1m-bold.ttf"],
    ["SFMono-1x2-RegularItalic.otf", "modified-migu-1m-oblique.ttf"],
    ["SFMono-1x2-BoldItalic.otf", "modified-migu-1m-bold-oblique.ttf"],
]
SFMONO_SQUARE = [
    ["SFMonoSquare-Regular.otf", "build"],
    ["SFMonoSquare-Bold.otf", "build"],
    ["SFMonoSquare-RegularItalic.otf", "build"],
    ["SFMonoSquare-BoldItalic.otf", "build"],
]


def build(version):
    print("---- modifying SF Mono ----")
    if concurrent_execute(sfmono.modify, SFMONO):
        return 1
    return 0


def concurrent_execute(func, args):
    executor = ProcessPoolExecutor()
    futures = [executor.submit(func, *a) for a in args]
    return 1 if any([r.result() for r in as_completed(futures)]) else 0
