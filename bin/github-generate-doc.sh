#!/bin/bash -eu
dir=script/convert_codepoints
script=$dir/convert_codepoints
readme=$dir/README.md
if ! podchecker $script; then
  exit 1
fi
curl -L https://cpanmin.us/ -o bin/cpanm
chmod +x bin/cpanm
bin/cpanm -n Pod::Markdown
/usr/local/opt/perl/bin/pod2markdown < $script > $readme
if git status -sb | grep -q $readme; then
  # https://qiita.com/thaim/items/3d1a4d09ec4a7d8844ce
  git config user.name "github-actions[bot]"
  git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
  git add $readme
  git commit -m "[ci skip] docs: update doc for ${script##*/}"
  git remote set-url origin git@github.com:"$GITHUB_REPOSITORY"
  branch=${GITHUB_REF#refs/heads/}
  git push origin master:"$branch"
fi
