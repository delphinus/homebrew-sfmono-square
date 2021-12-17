# -*- coding:utf-8 -*-
from concurrent.futures import ProcessPoolExecutor, as_completed
import font_patcher
import mplus
import sfmono
import sfmono_square


MPLUS_IPEX = [
    ["Mplus1-Regular.otf", "ipaexg.ttf"],
    ["Mplus1-Bold.otf", "ipaexg.ttf"],
]
MPLUS_MODIFIED = [
    ["modified-Mplus1-Regular.otf"],
    ["modified-Mplus1-Bold.otf"],
]
SFMONO = [
    ["SF-Mono-Regular.otf"],
    ["SF-Mono-Bold.otf"],
    ["SF-Mono-RegularItalic.otf"],
    ["SF-Mono-BoldItalic.otf"],
]
SFMONO_MIGU1M = [
    ["SFMono-1x2-Regular.otf", "modified-Mplus1-Regular.otf"],
    ["SFMono-1x2-Bold.otf", "modified-Mplus1-Bold.otf"],
    ["SFMono-1x2-RegularItalic.otf", "modified-Mplus1-Oblique.otf"],
    ["SFMono-1x2-BoldItalic.otf", "modified-Mplus1-Bold-Oblique.otf"],
]
SFMONO_SQUARE = [
    ["SFMonoSquare-Regular.otf", "build"],
    ["SFMonoSquare-Bold.otf", "build"],
    ["SFMonoSquare-RegularItalic.otf", "build"],
    ["SFMonoSquare-BoldItalic.otf", "build"],
]


def build(version):
    print("---- modifying Mplus ----")
    if concurrent_execute(mplus.modify, MPLUS_IPEX):
        return 1
    print("---- making oblique version of Mplus ----")
    if concurrent_execute(mplus.oblique, MPLUS_MODIFIED):
        return 1
    print("---- modifying SF Mono ----")
    if concurrent_execute(sfmono.modify, SFMONO):
        return 1
    print("---- generate SF Mono Square ----")
    args = [a + [version] for a in SFMONO_MIGU1M]
    if concurrent_execute(sfmono_square.generate, args):
        return 1
    print("---- adding nerd-fonts glyphs ----")
    if concurrent_execute(font_patcher.patch, SFMONO_SQUARE):
        return 1
    return 0


def concurrent_execute(func, args):
    executor = ProcessPoolExecutor()
    futures = [executor.submit(func, *a) for a in args]
    return 1 if any([r.result() for r in as_completed(futures)]) else 0
