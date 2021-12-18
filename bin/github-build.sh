#!/bin/bash -eux
sw_vers  # show macOS version
brew update
if [[ $GITHUB_REF = master ]]; then
  : build on the latest tag
  brew tap delphinus/sfmono-square
  brew install sfmono-square
else
  : build on "$GITHUB_REF"
  brew tap delphinus/sfmono-square
  # TODO: avoid errors for this
  brew install --only-dependencies sfmono-square || true
  FORMULA=sfmono-square.rb
  export URL=https://github.com/delphinus/homebrew-sfmono-square/archive/$GITHUB_SHA.tar.gz
  SHA=$(curl -L "$URL" | shasum -a256 | cut -f1 -d ' ')
  export SHA
  perl -i -pe 's,(?<=^  url ").*(?="$),$ENV{URL},' $FORMULA
  perl -i -pe 's,(?<=^  sha256 ").*(?="$),$ENV{SHA},' $FORMULA
  perl -i -pe 's,(?<=^  version ").*(?="$),$ENV{GITHUB_SHA},' $FORMULA
  brew install -vd --build-from-source $FORMULA
fi
