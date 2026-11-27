#!/bin/bash -eux
font_dir=$(brew --prefix sfmono-square)/share/fonts

fonts=()
for w in Light Regular Medium Semibold Bold Heavy; do
  for i in "$w" "${w}Italic"; do
    fonts+=("SFMonoSquare-$i.otf")
  done
done
fonts+=(SFMonoSquareExt-P1.ttf SFMonoSquareExt-P2.ttf)

for f in "${fonts[@]}"; do
  font=$font_dir/$f
  if [[ -f $font ]]; then
    echo "found $font"
  else
    echo "cannot find $font" 2>&1
    exit 1
  fi
done
