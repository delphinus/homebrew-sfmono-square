# -*- coding=utf8 -*-

from argparse import ArgumentParser, RawTextHelpFormatter
import errno
import os
import re
import sys

import fontforge
import psMat

PROJECT_NAME = 'SFMono Square'

# Most glyphs we want to maximize during the scale.  However, there are some
# that need to be small or stay relative in size to each other.
# The following list are those glyphs.  A tuple represents a range.
DEVI_SCALE_LIST  = { 'ScaleGlyph': 0xE60E, 'GlyphsToScale': [ (0xe6bd, 0xe6c3), ] }
FONTA_SCALE_LIST = { 'ScaleGlyph': 0xF17A, 'GlyphsToScale': [ 0xf005, 0xf006, (0xf026, 0xf028), 0xf02b, 0xf02c, (0xf031, 0xf035), (0xf044, 0xf054), (0xf060, 0xf063), 0xf077, 0xf078, 0xf07d, 0xf07e, 0xf089, (0xf0d7, 0xf0da), (0xf0dc, 0xf0de), (0xf100, 0xf107), 0xf141, 0xf142, (0xf153, 0xf15a), (0xf175, 0xf178), 0xf182, 0xf183, (0xf221, 0xf22d), (0xf255, 0xf25b), ] }
OCTI_SCALE_LIST  = { 'ScaleGlyph': 0xF02E, 'GlyphsToScale': [ (0xf03d, 0xf040), 0xf044, (0xf051, 0xf053), 0xf05a, 0xf05b, 0xf071, 0xf078, (0xf09f, 0xf0aa), 0xf0ca, ] }

# Define the character ranges
# Symbol font ranges

PATCH_SET = [
    {'Name': "Seti-UI + Custom",        'Filename': "original-source.otf",              'Exact': False, 'SymStart': 0xE4FA, 'SymEnd': 0xE52E, 'SrcStart': 0xE5FA, 'SrcEnd': 0xE62E, 'ScaleGlyph': None},
    {'Name': "Devicons",                'Filename': "devicons.ttf",                     'Exact': False, 'SymStart': 0xE600, 'SymEnd': 0xE6C5, 'SrcStart': 0xE700, 'SrcEnd': 0xE7C5, 'ScaleGlyph': DEVI_SCALE_LIST},
    {'Name': "Powerline Symbols",       'Filename': "PowerlineSymbols.otf",             'Exact': True,  'SymStart': 0xE0A0, 'SymEnd': 0xE0A2, 'SrcStart': None,   'SrcEnd': None,   'ScaleGlyph': None},
    {'Name': "Powerline Symbols",       'Filename': "PowerlineSymbols.otf",             'Exact': True,  'SymStart': 0xE0B0, 'SymEnd': 0xE0B3, 'SrcStart': None,   'SrcEnd': None,   'ScaleGlyph': None},
    {'Name': "Powerline Extra Symbols", 'Filename': "PowerlineExtraSymbols.otf",        'Exact': True,  'SymStart': 0xE0A3, 'SymEnd': 0xE0A3, 'SrcStart': None,   'SrcEnd': None,   'ScaleGlyph': None},
    {'Name': "Powerline Extra Symbols", 'Filename': "PowerlineExtraSymbols.otf",        'Exact': True,  'SymStart': 0xE0B4, 'SymEnd': 0xE0C8, 'SrcStart': None,   'SrcEnd': None,   'ScaleGlyph': None},
    {'Name': "Powerline Extra Symobls", 'Filename': "PowerlineExtraSymbols.otf",        'Exact': True,  'SymStart': 0xE0CA, 'SymEnd': 0xE0CA, 'SrcStart': None,   'SrcEnd': None,   'ScaleGlyph': None},
    {'Name': "Powerline Extra Symobls", 'Filename': "PowerlineExtraSymbols.otf",        'Exact': True,  'SymStart': 0xE0CC, 'SymEnd': 0xE0D4, 'SrcStart': None,   'SrcEnd': None,   'ScaleGlyph': None},
    {'Name': "Pomicons",                'Filename': "Pomicons.otf",                     'Exact': True,  'SymStart': 0xE000, 'SymEnd': 0xE00A, 'SrcStart': None,   'SrcEnd': None,   'ScaleGlyph': None},
    {'Name': "Font Awesome",            'Filename': "FontAwesome.otf",                  'Exact': True,  'SymStart': 0xF000, 'SymEnd': 0xF2E0, 'SrcStart': None,   'SrcEnd': None,   'ScaleGlyph': FONTA_SCALE_LIST}, # Maximize
    {'Name': "Font Awesome Extension",  'Filename': "font-awesome-extension.ttf",       'Exact': False, 'SymStart': 0xE000, 'SymEnd': 0xE0A9, 'SrcStart': 0xE200, 'SrcEnd': 0xE2A9, 'ScaleGlyph': None},
    {'Name': "Font Linux",              'Filename': "font-logos.ttf",                   'Exact': False, 'SymStart': 0xF100, 'SymEnd': 0xF11C, 'SrcStart': 0xF300, 'SrcEnd': 0xF31C, 'ScaleGlyph': None},             # Power, Power On/Off, Power On, Sleep
    {'Name': "Power Symbols",           'Filename': "Unicode_IEC_symbol_font.otf",      'Exact': True,  'SymStart': 0x23FB, 'SymEnd': 0x23FE, 'SrcStart': None,   'SrcEnd': None,   'ScaleGlyph': None},             # Heavy Circle (aka Power Off)
    {'Name': "Power Symbols",           'Filename': "Unicode_IEC_symbol_font.otf",      'Exact': True,  'SymStart': 0x2B58, 'SymEnd': 0x2B58, 'SrcStart': None,   'SrcEnd': None,   'ScaleGlyph': None},
    {'Name': "Octicons",                'Filename': "octicons.ttf",                     'Exact': False, 'SymStart': 0xF000, 'SymEnd': 0xF105, 'SrcStart': 0xF400, 'SrcEnd': 0xF505, 'ScaleGlyph': OCTI_SCALE_LIST},  # Magnifying glass
    {'Name': "Octicons",                'Filename': "octicons.ttf",                     'Exact': False, 'SymStart': 0x2665, 'SymEnd': 0x2665, 'SrcStart': None,   'SrcEnd': None,   'ScaleGlyph': OCTI_SCALE_LIST},  # Heart
    {'Name': "Octicons",                'Filename': "octicons.ttf",                     'Exact': False, 'SymStart': 0X26A1, 'SymEnd': 0X26A1, 'SrcStart': None,   'SrcEnd': None,   'ScaleGlyph': OCTI_SCALE_LIST},  # Zap
    {'Name': "Octicons",                'Filename': "octicons.ttf",                     'Exact': False, 'SymStart': 0xF27C, 'SymEnd': 0xF27C, 'SrcStart': 0xF4A9, 'SrcEnd': 0xF4A9, 'ScaleGlyph': OCTI_SCALE_LIST},  # Desktop
    {'Name': "Material",                'Filename': "materialdesignicons-webfont.ttf",  'Exact': False, 'SymStart': 0xF001, 'SymEnd': 0xF847, 'SrcStart': 0xF500, 'SrcEnd': 0xFD46, 'ScaleGlyph': None},
    {'Name': "Weather Icons",           'Filename': "weathericons-regular-webfont.ttf", 'Exact': False, 'SymStart': 0xF000, 'SymEnd': 0xF0EB, 'SrcStart': 0xE300, 'SrcEnd': 0xE3EB, 'ScaleGlyph': None},
]


def patch(in_file, out_dir):
    font = fontforge.open(in_file)
    _patch(font)
    try:
        os.makedirs(out_dir)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    out_file = os.path.join(out_dir, in_file)
    print('Generated ' + out_file)
    font.generate(out_file)
    return 0


def _patch(font):
    # Prevent opening and closing the fontforge font. Makes things faster when
    # patching multiple ranges using the same symbol font.
    previous_symbol_filename = ""
    symfont = None

    for pat in PATCH_SET:
        if previous_symbol_filename != pat['Filename']:
            # We have a new symbol font, so close the previous one if it exists
            if symfont:
                symfont.close()
                symfont = None
            symfont = fontforge.open("src/glyphs/"+pat['Filename'])
            # Match the symbol font size to the source font size
            symfont.em = font.em
            previous_symbol_filename = pat['Filename']
        # If patch table doesn't include a source start and end, re-use the
        # symbol font values
        src_start = pat['SrcStart']
        src_end = pat['SrcEnd']
        if not src_start:
            src_start = pat['SymStart']
        if not src_end:
            src_end = pat['SymEnd']

        _copy_glyphs(font, pat['Name'], src_start, src_end, symfont,
                     pat['SymStart'], pat['SymEnd'], pat['Exact'],
                     pat['ScaleGlyph'])
    if symfont:
        symfont.close()


def _copy_glyphs(sourceFont, name, sourceFontStart, sourceFontEnd, symbolFont, symbolFontStart, symbolFontEnd, exactEncoding, scaleGlyph):

    if exactEncoding is False:
        sourceFontList = []
        sourceFontCounter = 0

        for i in range(sourceFontStart, sourceFontEnd + 1):
            sourceFontList.append(format(i, 'X'))

    # Create glyphs from symbol font

    # If we are going to copy all Glyphs, then assume we want to be careful
    # and only copy those that are not already contained in the source font
    if symbolFontStart == 0:
        symbolFont.selection.all()
        sourceFont.selection.all()
    else:
        symbolFont.selection.select(("ranges", "unicode"),
                                    symbolFontStart, symbolFontEnd)
        sourceFont.selection.select(("ranges", "unicode"),
                                    sourceFontStart, sourceFontEnd)

    x_ratio = 1.0
    y_ratio = 1.0
    x_diff = 0
    y_diff = 0

    if name == 'Seti-UI + Custom':
        x_ratio = 1.1
        y_ratio = 1.1
        x_diff = -100
        y_diff = -450

    elif name == 'Devicons':
        x_ratio = 1.05
        y_ratio = 1.05
        x_diff = -100
        y_diff = -250

    elif name in ['Powerline Symbols', 'Powerline Extra Symbols']:
        # for Iosevka
        # x_ratio = 0.96
        # y_ratio = 1.10
        # x_diff = 0
        # y_diff = 20
        # for SF Mono 13pt
        x_ratio = 0.95
        y_ratio = 0.88
        x_diff = 0
        y_diff = -30

    elif name == 'Font Linux':
        y_diff = -120

    elif name == 'Font Awesome Extension':
        y_diff = -400

    elif name == 'Pomicons':
        x_ratio = 1.2
        y_ratio = 1.2
        x_diff = -200
        y_diff = -300

    elif name == 'Octicons':
        x_ratio = 0.95
        y_ratio = 0.95
        x_diff = 30
        y_diff = -100

    elif name == 'Material':
        x_ratio = 1.1
        y_ratio = 1.1
        x_diff = -50
        y_diff = -250

    scale = psMat.scale(x_ratio, y_ratio)
    translate = psMat.translate(x_diff, y_diff)
    transform = psMat.compose(scale, translate)
    symbolFont.transform(transform)

    for index, sym_glyph in enumerate(symbolFont.selection.byGlyphs):

        index = max(1, index)

        if exactEncoding:
            # use the exact same hex values for the source font as for the
            # symbol font
            currentSourceFontGlyph = sym_glyph.encoding
            # Save as a hex string without the '0x' prefix
            copiedToSlot = format(sym_glyph.unicode, 'X')
        else:
            # use source font defined hex values based on passed in start and
            # end convince that this string really is a hex:
            currentSourceFontGlyph = int('0x' +
                                         sourceFontList[sourceFontCounter], 16)
            copiedToSlot = sourceFontList[sourceFontCounter]
            sourceFontCounter += 1

        if int(copiedToSlot, 16) < 0:
            print('Found invalid glyph slot number. Skipping.')
            continue

        # Select and copy symbol from its encoding point
        # We need to do this select after the careful check, this way we don't
        # reset our selection before starting the next loop
        symbolFont.selection.select(sym_glyph.encoding)
        symbolFont.copy()

        # Paste it
        sourceFont.selection.select(currentSourceFontGlyph)
        sourceFont.paste()

        sourceFont[currentSourceFontGlyph].glyphname = sym_glyph.glyphname

        # reset selection so iteration works propertly @todo fix? rookie
        # misunderstanding?  This is likely needed because the selection was
        # changed when the glyph was copy/pasted
        if symbolFontStart == 0:
            symbolFont.selection.all()
        else:
            symbolFont.selection.select(("ranges", "unicode"),
                                        symbolFontStart, symbolFontEnd)
    # end for

    return
