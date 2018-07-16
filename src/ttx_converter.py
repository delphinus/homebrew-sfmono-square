from os import rename
from os.path import splitext
import re
from subprocess import check_call, check_output


VALID_WIDTH = '1024'
X_AVG_CHAR_WIDTH_RE = re.compile(r'(?<=<xAvgCharWidth value=")\d+(?="/>)')
TTX = check_output(['brew', '--prefix']).rstrip() + '/bin/ttx'


def convert(in_filename, in_dir):
    '''
    This function fixes the `xAvgCharWidth` parameter.  FontForge has a bug
    that it changes the param and glyphs in Windows show invalid widths.

    ref. http://itouhiro.hatenablog.com/entry/20140910/font

    commands example:
        mv SFMonoSquare-Regular.ttf SFMonoSquare-Regular-old.ttf
        ttx -t OS/2 SFMonoSquare-Regular-old.ttf
        # replace xAvgCharWidth to 1024 in SFMonoSquare-Regular-old.ttx
        # and rename to SFMonoSquare-Regular.ttx
        ttx -m SFMonoSquare-Regular-old.ttf SFMonoSquare-Regular.ttx
    '''
    (base, ext) = splitext(in_filename)
    in_file = in_dir + '/' + in_filename
    renamed = in_dir + '/' + base + '-old' + ext
    in_ttx = in_dir + '/' + base + '-old.ttx'
    out_ttx = in_dir + '/' + base + '.ttx'
    rename(in_file, renamed)
    check_call([TTX, '-t', 'OS/2', renamed])
    with open(in_ttx, 'r') as fin:
        with open(out_ttx, 'w') as fout:
            for line in fin:
                fout.write(X_AVG_CHAR_WIDTH_RE.sub(VALID_WIDTH, line))
    check_call([TTX, '-m', renamed, out_ttx])
