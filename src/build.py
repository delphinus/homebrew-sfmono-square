# -*- coding:utf-8 -*-
import sys

from concurrent.futures import ProcessPoolExecutor, as_completed
import font_patcher
import migu1m
import sfmono
import sfmono_square


MIGU1M = [['migu-1m-regular.ttf'], ['migu-1m-bold.ttf']]
MIGU1M_MODIFIED = [
    ['modified-migu-1m-regular.ttf'],
    ['modified-migu-1m-bold.ttf'],
]
SFMONO = [
    ['SFMono-Regular.otf'], ['SFMono-Bold.otf'],
    ['SFMono-RegularItalic.otf'], ['SFMono-BoldItalic.otf'],
]
SFMONO_MIGU1M = [
    ['modified-SFMono-Regular.otf', 'modified-migu-1m-regular.ttf'],
    ['modified-SFMono-Bold.otf', 'modified-migu-1m-bold.ttf'],
    ['modified-SFMono-RegularItalic.otf', 'modified-migu-1m-oblique.ttf'],
    ['modified-SFMono-BoldItalic.otf', 'modified-migu-1m-bold-oblique.ttf'],
]
SFMONO_SQUARE = [
    ['SFMonoSquare-Regular.otf', 'build'],
    ['SFMonoSquare-Bold.otf', 'build'],
    ['SFMonoSquare-RegularItalic.otf', 'build'],
    ['SFMonoSquare-BoldItalic.otf', 'build'],
]


def build(version):
    print('---- modifying migu-1m ----')
    if concurrent_execute(migu1m.modify, MIGU1M):
        return 1
    print('---- making oblique version of migu-1m ----')
    if concurrent_execute(migu1m.oblique, MIGU1M_MODIFIED):
        return 1
    print('---- modifying SF Mono ----')
    if concurrent_execute(sfmono.modify, SFMONO):
        return 1
    print('---- generate SF Mono Square ----')
    args = [a + [version] for a in SFMONO_MIGU1M]
    if concurrent_execute(sfmono_square.generate, args):
        return 1
    print('---- adding nerd-fonts glyphs ----')
    if concurrent_execute(font_patcher.patch, SFMONO_SQUARE):
        return 1
    return 0


def concurrent_execute(func, args):
    executor = ProcessPoolExecutor()
    futures = [executor.submit(func, *a) for a in args]
    return 1 if any([r.result() for r in as_completed(futures)]) else 0
