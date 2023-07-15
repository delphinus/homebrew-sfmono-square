#!/bin/bash -eux
# Disable features because these takes much time.
export HOMEBREW_NO_INSTALL_CLEANUP=1
export HOMEBREW_NO_INSTALLED_DEPENDENTS_CHECK=1
export HOMEBREW_NO_INSTALL_FROM_API=1
sw_vers                          # show macOS version
brew install python@3.11 || true # This will fail because of linking.
if [[ $GITHUB_REF = refs/heads/master ]]; then
  : build on the latest tag
  brew tap delphinus/sfmono-square
  brew install sfmono-square
else
  : build on "$GITHUB_REF"
  HASH=$(git describe --tags HEAD | tr -d '\n')
  export HASH
  export URL=https://github.com/delphinus/homebrew-sfmono-square/tarball/$HASH
  SHA=$(curl -L "$URL" | shasum -a256 | cut -f1 -d ' ')
  export SHA
  FORMULA=sfmono-square.rb
  perl -i -pe 's,(?<=^  url ").*(?="$),$ENV{URL},' $FORMULA
  perl -i -pe 's,(?<=^  sha256 ").*(?="$),$ENV{SHA},' $FORMULA
  perl -i -pe 's,(?<=^  version ").*(?="$),$ENV{HASH},' $FORMULA
  brew install -v $FORMULA
fi

font_dir=/usr/local/opt/sfmono-square/share/fonts

for i in Bold BoldItalic Regular RegularItalic; do
  font=$font_dir/SFMonoSquare-$i.otf
  if [[ -f $font ]]; then
    echo "found $font"
  else
    echo "cannot find $font" 2>&1
    exit 1
  fi
done
