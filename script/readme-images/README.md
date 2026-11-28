# The images of README

The scripts that make the images of README in `.github/images/`.  They need SF Mono Square
installed with the formula (`brew install sfmono-square`), and Python with Pillow and fontTools.
The commands below get them with [uv](https://github.com/astral-sh/uv).

## Drawn

These draw the images from the fonts in `$(brew --prefix sfmono-square)/share/fonts`.

```sh
cd script/readme-images
uv run --with pillow --with fonttools python3 hero.py ../../.github/images/readme-hero.png
uv run --with pillow --with fonttools python3 hero.py ../../.github/images/readme-hero-narrow.png --narrow
uv run --with pillow python3 weights.py ../../.github/images/readme-weights.png
uv run --with pillow python3 weights.py ../../.github/images/readme-weights-narrow.png --narrow
uv run --with pillow --with fonttools python3 kanji.py ../../.github/images/readme-kanji.png
uv run --with pillow --with fonttools python3 kanji.py ../../.github/images/readme-kanji-narrow.png --narrow
```

README shows each image in two sizes with `<picture>`: the one with `-narrow` in its name on a
screen up to 600px wide, such as a phone, and the other on a wider one.  The narrow images are
drawn with `--narrow`, with text as large as that of README on a phone.

`kanji.py` tells where a glyph comes from by the fonts SF Mono Square is built from, which the
formula installs into `share/fonts/src`.

The PNGs in the repository are reduced to 128 colours after they are drawn, except
`readme-hero.png` and `readme-hero-narrow.png`:

```sh
magick readme-weights.png -strip -colors 128 PNG8:readme-weights.png
```

## The gallery

The gallery is not drawn.  `gallery/gallery.sh` runs each program in a kitty of its own
(`gallery/kitty.conf`, SF Mono Square in the colours of tokyonight storm), captures the window,
cuts the blank rows at its bottom and gives it rounded corners and a shadow
(`gallery/compose.py`).  The narrow images of the gallery are taken in windows of 42 columns, with
the content cut down to fit, and shown without the shadow and its margins (`compose.py --flat`).

```sh
script/readme-images/gallery/gallery.sh
```

It needs macOS (`screencapture` and the window list of CoreGraphics), kitty, eza, sqlite3, tig,
btop and Neovim.  The two screenshots of Neovim depend on the setup of the author
([snacks.nvim](https://github.com/folke/snacks.nvim) for the file explorer,
[lualine.nvim](https://github.com/nvim-lualine/lualine.nvim) for the status line, and
[vimdoc-ja](https://github.com/vim-jp/vimdoc-ja) for the help), and look different with
another one.  The files and the history of commits on the screenshots are made by
`gallery/demo.py`; the authors in the history are made up.
