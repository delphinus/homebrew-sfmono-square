#!/usr/local/opt/python@2/bin/python
from datetime import datetime
import fontforge
import psMat
import sys


FAMILY = 'Migu 1M'


def filename_str(name):
    return name.lower().replace(' ', '-')


def read_opts():
    return {
        'filename': sys.argv[1],
        'style': 'Oblique' if sys.argv[2] == 'Regular' else 'Bold Oblique',
    } if len(sys.argv) == 3 else False


def main():
    opts = read_opts()
    if not opts:
        return 1
    font = fontforge.open(opts['filename'])
    fullname = '{0} {1}'.format(FAMILY, opts['style'])
    font.encoding = 'UnicodeFull'
    font.fontname = filename_str(fullname)
    font.familyname = FAMILY
    font.fullname = fullname
    font.appendSFNTName(0x409, 2, opts['style'])
    font.appendSFNTName(0x409, 3, 'FontForge 2.0 : {0} : {1}'.format(
        fullname, datetime.today().strftime('%d-%m-%Y')))
    mat = psMat.skew(0.2)
    for glyph in list(font.selection.byGlyphs):
        glyph.transform(mat)
    filename = font.fontname + '.ttf'
    print('Generate ' + filename)
    font.generate(filename, flags=('opentype',))
    return 0


if __name__ == '__main__':
    sys.exit(main())
