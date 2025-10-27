#!/bin/bash -eux
# Disable features because these takes much time.
export HOMEBREW_NO_INSTALL_CLEANUP=1
export HOMEBREW_NO_INSTALLED_DEPENDENTS_CHECK=1
export HOMEBREW_NO_INSTALL_FROM_API=1
sw_vers # show macOS version
FORMULA=sfmono-square.rb
if [[ $GITHUB_REF = refs/heads/master ]]; then
  : build on the latest tag
else
  : build on "$GITHUB_REF"
  HASH=$(git describe --tags HEAD | tr -d '\n')
  export HASH
  export URL=https://github.com/delphinus/homebrew-sfmono-square/tarball/$HASH
  SHA=$(curl -L "$URL" | shasum -a256 | cut -wf1)
  export SHA
  perl -i -pe 's,(?<=^  url ").*(?="$),$ENV{URL},' $FORMULA
  perl -i -pe 's,(?<=^  sha256 ").*(?="$),$ENV{SHA},' $FORMULA
  perl -i -pe 's,(?<=^  version ").*(?="$),$ENV{HASH},' $FORMULA
fi
TAP=local/sfmono-square
# NOTE: tap-new needs Git to be done setup.
# https://qiita.com/thaim/items/3d1a4d09ec4a7d8844ce
git config --global user.name "github-actions[bot]"
git config --global user.email "41898282+github-actions[bot]@users.noreply.github.com"
brew update
# Reinstall python@3.14 to ensure it's properly installed and linked
# This works around issues with pre-installed python@3.14 in GitHub Actions runners
brew reinstall python@3.14
brew tap-new $TAP
cp $FORMULA "$(brew --repo $TAP)/Formula/"
brew install -v $TAP/sfmono-square
