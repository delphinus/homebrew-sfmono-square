#!/bin/bash -eu
# Called from .github/workflows/release.yml when a tag is pushed. It creates
# the release from the notes in .github/release-notes, then commits the
# formula that points at the new tag into master.
FORMULA=sfmono-square.rb
NOTES_DIR=.github/release-notes

abort() {
  echo "::error::$1"
  exit 1
}

main() {
  tag=${GITHUB_REF#refs/tags/}
  [[ $tag != "$GITHUB_REF" ]] || abort "not a tag: $GITHUB_REF"
  [[ $tag =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]] || abort "not a semver tag: $tag"
  git fetch origin master
  git merge-base --is-ancestor "$tag" origin/master ||
    abort "$tag is not on master"
  # NOTE: The notes must be read before switching to master, as they are the
  # ones the tag has.
  create_release "$tag"
  update_formula "$tag" "${tag#v}"
}

create_release() {
  tag=$1
  notes=$NOTES_DIR/$tag.md
  if gh release view "$tag" >/dev/null 2>&1; then
    echo "the release for $tag already exists"
  elif [[ -f $notes ]]; then
    gh release create "$tag" \
      --title "$(head -1 "$notes" | sed 's/^# *//')" \
      --notes "$(tail -n +2 "$notes")"
  else
    echo "::warning::$notes is not found. Use the generated notes instead."
    gh release create "$tag" --generate-notes
  fi
}

update_formula() {
  tag=$1
  ver=$2
  url=https://github.com/$GITHUB_REPOSITORY/archive/refs/tags/$tag.tar.gz
  sha=$(curl -fsSL "$url" | sha256sum | cut -d' ' -f1)
  git switch -C master origin/master
  # NOTE: Resources in the formula have their own url & sha256, but they are
  # indented deeper and are not matched here.
  URL=$url perl -i -ple '$_ = qq{  url "$ENV{URL}"} if /^  url /' $FORMULA
  SHA=$sha perl -i -ple '$_ = qq{  sha256 "$ENV{SHA}"} if /^  sha256 /' $FORMULA
  VER=$ver perl -i -ple '$_ = qq{  version "$ENV{VER}"} if /^  version /' $FORMULA
  if git diff --quiet -- $FORMULA; then
    echo "the formula already points at $tag"
    return
  fi
  # https://qiita.com/thaim/items/3d1a4d09ec4a7d8844ce
  git config user.name "github-actions[bot]"
  git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
  git commit -m "Update formula to use new version" -- $FORMULA
  git remote set-url origin git@github.com:"$GITHUB_REPOSITORY"
  git push origin master
}

[[ ${BASH_SOURCE[0]} = "$0" ]] && main "$@"
