#!/bin/bash -eu
# Called from .github/workflows/release.yml when a tag is pushed. It creates
# the release from the notes in .github/release-notes, then commits the
# formula that points at the new tag into master.
FORMULA=sfmono-square.rb
NOTES_DIR=.github/release-notes
# The build takes 15-25 minutes, so wait for a while when it is still running.
BUILD_TRIES=70
BUILD_INTERVAL=30
# When a tag is pushed just after a merge, the check runs of the commit are not
# registered yet. Wait for them to appear, but not as long as the build itself.
BUILD_NONE_TRIES=10

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
  wait_for_build "$tag"
  # NOTE: The notes must be read before switching to master, as they are the
  # ones the tag has.
  create_release "$tag"
  update_formula "$tag" "${tag#v}"
}

# Nothing is released unless the fonts are built from the very commit the tag
# points at. Note that this cannot be skipped by tagging without bin/release.
wait_for_build() {
  sha=$(git rev-parse "$1^{commit}")
  none=0
  for _ in $(seq $BUILD_TRIES); do
    state=$(build_state "$sha")
    case $state in
    success)
      echo "the build check for $sha is successful"
      return
      ;;
    running)
      echo "the build check for $sha is still running"
      sleep $BUILD_INTERVAL
      ;;
    none)
      none=$((none + 1))
      [[ $none -lt $BUILD_NONE_TRIES ]] ||
        abort "no build check is found for $sha. Tag a commit built on master."
      echo "the build check for $sha has not started yet"
      sleep $BUILD_INTERVAL
      ;;
    *)
      abort "the build check for $sha is not successful"
      ;;
    esac
  done
  abort "the build check for $sha did not finish in time"
}

build_state() {
  gh api "repos/$GITHUB_REPOSITORY/commits/$1/check-runs?per_page=100" --jq '
    [.check_runs[] | select(.name | startswith("build "))]
    | if length == 0 then "none"
      elif any(.status != "completed") then "running"
      elif all(.conclusion == "success") then "success"
      else "failure" end
  '
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
