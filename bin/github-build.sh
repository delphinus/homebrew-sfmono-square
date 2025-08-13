#!/bin/bash -eux
# Disable features because these takes much time.
export HOMEBREW_NO_INSTALL_CLEANUP=1
export HOMEBREW_NO_INSTALLED_DEPENDENTS_CHECK=1
export HOMEBREW_NO_INSTALL_FROM_API=1
sw_vers # show macOS version
brew update
if [[ $GITHUB_REF = refs/heads/master ]]; then
  : build on the latest tag
  brew tap delphinus/sfmono-square
  brew install delphinus/sfmono-square/sfmono-square
else
  : build on "$GITHUB_REF"
  HASH=$(git describe --tags HEAD | tr -d '\n')
  export HASH
  export URL=https://github.com/delphinus/homebrew-sfmono-square/tarball/$HASH
  SHA=$(curl -L "$URL" | shasum -a256 | cut -f1 -d ' ')
  export SHA
  FORMULA=sfmono-square.rb
  TAP=local/sfmono-square
  perl -i -pe 's,(?<=^  url ").*(?="$),$ENV{URL},' $FORMULA
  perl -i -pe 's,(?<=^  sha256 ").*(?="$),$ENV{SHA},' $FORMULA
  perl -i -pe 's,(?<=^  version ").*(?="$),$ENV{HASH},' $FORMULA
  brew tap-new $TAP
  cp $FORMULA "$(brew --repo $TAP)/Formula/"
  brew install -v $TAP/sfmono-square
fi
