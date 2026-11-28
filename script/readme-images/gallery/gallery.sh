#!/bin/bash
# Take the screenshots of the gallery of README into .github/images/gallery-*.png.
#
#   script/readme-images/gallery/gallery.sh [WORK]
#
# WORK (~/.cache/sfm-gallery by default) keeps the files the screenshots show and the
# screenshots before they are finished.  Its path is on some of the screenshots, so keep it
# short: a temporary directory of macOS shows up as /private/var/folders/...  See
# ../README.md for what this needs.
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/../../.." && pwd)
work=${1:-$HOME/.cache/sfm-gallery}
py=(uv run --quiet --with pillow python3)

mkdir -p "$work/raw"
"${py[@]}" "$here/demo.py" "$work" >/dev/null

# btop with the boxes of CPU and memory only: the box of the network shows the address of the
# machine, and that of the processes shows what runs on it.
btop --default-config >"$work/btop.conf"
sed -i '' -E \
  -e 's/^shown_boxes = .*/shown_boxes = "cpu mem"/' \
  -e 's/^color_theme = .*/color_theme = "TTY"/' \
  -e 's/^theme_background = .*/theme_background = False/' \
  -e 's/^show_battery = .*/show_battery = False/' \
  -e 's/^update_ms = .*/update_ms = 500/' \
  "$work/btop.conf"

shot() { "${py[@]}" "$here/shot.py" "$@" >/dev/null; }
prompt() { printf '\033[?25l\033[32m❯\033[0m %s\n' "$1"; }
export -f prompt

shot "$work/raw/eza.png" "$work/demo" 92 17 3 -- bash -c \
  'prompt "eza --icons --long --git --no-user --tree"; eza --icons --long --git --no-user --tree --color=always; sleep 60'
shot "$work/raw/sqlite.png" "$work/demo" 80 12 3 -- bash -c \
  "prompt 'sqlite3 -box fonts.db \"select * from fonts\"'; sqlite3 -box :memory: '.read $here/table.sql' 'select * from fonts'; sleep 60"
shot "$work/raw/tig.png" "$work/history" 96 21 4 -- tig
# The Japanese help needs vimdoc-ja.  The highlight of treesitter does not conceal the bars of
# the links in it, so the syntax of Vim draws it.  The component of the diagnostics of LSP does
# not fit in the status line, so it is left out.
shot "$work/raw/help.png" "$work/demo" 90 26 7 \
  ':lua local c = require("lualine").get_config(); c.sections.lualine_x = {}; require("lualine").setup(c)\r@4' \
  ':setlocal colorcolumn=\r@5' ':\x1b@5.5' \
  -- nvim -c 'help eval()' -c only -c 'lua vim.treesitter.stop()' -c 'setlocal conceallevel=2'
shot "$work/raw/nvim.png" "$work/demo" 110 30 11 \
  ':lua Snacks.explorer({ diagnostics = false })\r@5' '\x17l@7' \
  ':set nolist | lua vim.lsp.inlay_hint.enable(false)\r@8' ':call cursor(15, 5)\r@9' \
  -- nvim -c 'lua vim.diagnostic.enable(false)' lua/demo/init.lua
# btop draws its graphs from what it has measured, so give it time.
shot "$work/raw/btop.png" "$work/demo" 110 24 40 -- btop -c "$work/btop.conf"

# The narrow versions, for a phone: windows of 42 columns, so that their text is about as large
# as the text of README.  The content is cut down to fit.
mkdir -p "$work/raw-narrow"
sed -e 's/^shown_boxes = .*/shown_boxes = "mem"/' "$work/btop.conf" >"$work/btop-narrow.conf"
# A short file name and nothing but the mode in the status line of lualine.
lualine=':lua local c = require("lualine").get_config(); c.sections.lualine_b = { "filename" }; c.sections.lualine_c = {}; c.sections.lualine_x = {}; c.sections.lualine_y = {}; require("lualine").setup(c)\r'

shot "$work/raw-narrow/eza.png" "$work/demo" 42 16 3 -- bash -c \
  'prompt "eza --icons --tree"; eza --icons --tree --color=always; sleep 60'
shot "$work/raw-narrow/sqlite.png" "$work/demo" 42 12 3 -- bash -c \
  "prompt 'sqlite3 -box fonts.db'; printf '  \"select ウェイト, 見本 from fonts\"\n'; sqlite3 -box :memory: '.read $here/table.sql' 'select ウェイト, 見本 from fonts'; sleep 60"
# tig without the columns of the ID and the date; ^L clears the message of the last command.
shot "$work/raw-narrow/tig.png" "$work/history" 42 21 6 \
  ':toggle date\r@2' ':toggle id\r@3' '\x0c@4' -- tig
# The help is laid out in 78 columns, so a section of the user manual, with few tags in it, is
# formatted again into 40 for the screenshot (the file is not written).
shot "$work/raw-narrow/help.png" "$work/demo" 42 24 9 "$lualine@4" \
  ':setlocal modifiable noreadonly colorcolumn= textwidth=40 formatoptions+=mM | silent normal! gggqG\r@5' \
  ':setlocal nomodified scrolloff=0 | call search("\\*01\\.1\\*") | normal! zt\r@6.5' ':\x1b@7' \
  -- nvim -c 'help usr_01.txt' -c only -c 'lua vim.treesitter.stop()' -c 'setlocal conceallevel=2'
shot "$work/raw-narrow/nvim.png" "$work/narrow" 42 24 9 "$lualine@5" \
  ':set nolist | lua vim.lsp.inlay_hint.enable(false)\r@6' ':call cursor(4, 5)\r@7' \
  -- nvim -c 'lua vim.diagnostic.enable(false)' width.lua
shot "$work/raw-narrow/btop.png" "$work/demo" 42 18 40 -- btop -c "$work/btop-narrow.conf"

for name in eza sqlite tig help nvim btop; do
  "${py[@]}" "$here/compose.py" "$work/raw/$name.png" "$repo/.github/images/gallery-$name.png"
  "${py[@]}" "$here/compose.py" "$work/raw-narrow/$name.png" "$repo/.github/images/gallery-$name-narrow.png" --flat
done
echo "$work"
