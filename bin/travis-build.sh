#!/bin/bash -eux
# show macOS version
sw_vers
brew update
if ls -d /usr/local/Frameworks/Python.framework/Headers > /dev/null 2>&1; then
  brew unlink python@2
fi
if [[ $TRAVIS_EVENT_TYPE = cron ]]; then
  : build on the latest tag
  brew tap delphinus/sfmono-square
  brew install sfmono-square
else
  : build on "$TRAVIS_BRANCH"
  brew tap delphinus/sfmono-square
  brew install --only-dependencies sfmono-square
  FORMULA=sfmono-square.rb
  HASH=$(git describe --tags HEAD | tr -d '\n')
  export HASH
  export URL=https://github.com/delphinus/homebrew-sfmono-square/archive/$HASH.tar.gz
  SHA=$(curl -L "$URL" | shasum -a256 | cut -f1 -d' ')
  export SHA
  perl -i -pe 's,(?<=^  url ").*(?="$),$ENV{URL},' $FORMULA
  perl -i -pe 's,(?<=^  sha256 ").*(?="$),$ENV{SHA},' $FORMULA
  perl -i -pe 's,(?<=^  version ").*(?="$),$ENV{HASH},' $FORMULA
  brew install --build-from-source $FORMULA
fi
