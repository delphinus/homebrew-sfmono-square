#!/bin/bash -eux
font_dir=$(brew --prefix sfmono-square)/share/fonts

for i in Bold BoldItalic Regular RegularItalic; do
  font=$font_dir/SFMonoSquare-$i.otf
  if [[ -f $font ]]; then
    echo "found $font"
  else
    echo "cannot find $font" 2>&1
    exit 1
  fi
done
