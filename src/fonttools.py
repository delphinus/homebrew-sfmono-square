# -*- coding:utf-8 -*-
from fontTools.ttLib import TTFont
from os import rename
from tempfile import mkstemp

X_AVG_CHAR_WIDTH = 1024
FS_SELECTION = {
    "Regular": 0b00000001_01000000,
    "RegularItalic": 0b00000001_00000001,
    "Bold": 0b00000001_00100000,
    "BoldItalic": 0b00000001_00100001,
}
MAC_STYLE = {
    "Regular": 0b00,
    "RegularItalic": 0b10,
    "Bold": 0b01,
    "BoldItalic": 0b11,
}


def update(fontname, style):
    font = TTFont(fontname)
    font["post"].isFixedPitch = 1
    font["CFF "].cff[0].isFixedPitch = 1
    font["OS/2"].xAvgCharWidth = X_AVG_CHAR_WIDTH
    font["OS/2"].fsSelection = FS_SELECTION[style]
    font["head"].macStyle = MAC_STYLE[style]
    new_fontname = mkstemp(suffix=".otf")[1]
    font.save(new_fontname)
    font.close()
    rename(new_fontname, fontname)
