#!/bin/bash
tmpfile=$(mktemp)
dir=$(pwd)
fontforge_lib=/usr/local/opt/fontforge/lib/python3.9/site-packages

cat << EOS > "$tmpfile"
import sys
sys.path.append('$dir/src')
sys.path.append('$fontforge_lib')
import build
sys.exit(build.build('2.0.0'))
EOS

/usr/local/bin/python3 "$tmpfile"
