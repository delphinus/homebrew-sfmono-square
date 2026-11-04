#!/bin/bash -eux
font_dir=$(brew --prefix sfmono-square)/share/fonts

for w in Light Regular Medium Semibold Bold Heavy; do
  for i in "$w" "${w}Italic"; do
    font=$font_dir/SFMonoSquare-$i.otf
    if [[ -f $font ]]; then
      echo "found $font"
    else
      echo "cannot find $font" 2>&1
      exit 1
    fi
  done
done
