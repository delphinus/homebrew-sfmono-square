# SFMono Square - patched font: SFMono + Migu 1M + Nerd Fonts

<img width="598" alt="スクリーンショット 0001-05-23 21 40 50" src="https://user-images.githubusercontent.com/1239245/58253912-802c3480-7da4-11e9-9936-1f68326b9c38.png">

## What's this?

**SF Mono** is a font from Apple, that is clear, easy to read, and suitable for programming.  **SFMono Square** is based on **SF Mono**, and added glyphs for Japanese & patched for [Nerd Fonts][].

[Nerd Fonts]: https://github.com/ryanoasis/nerd-fonts

### font source

* SF Mono: Apple
* Migu 1M: [Miguフォント : M+とIPAの合成フォント](http://mix-mplus-ipa.osdn.jp/migu/)
* Nerd Fonts: [ryanoasis/nerd-fonts: Iconic font aggregator, collection, and patcher. 40+ patched fonts, over 3,600 glyph/icons, includes popular collections such as Font Awesome & fonts such as Hack](https://github.com/ryanoasis/nerd-fonts)

And, idea and some code is from [プログラミング用フォント Ricty](http://www.rs.tus.ac.jp/yyusa/ricty.html).

## How to use

Install with [Homebrew][].

[Homebrew]: https://brew.sh

```sh
brew tap delphinus/sfmono-square
brew install sfmono-square

open "$(brew --prefix sfmono-square)/share/fonts"
# open fonts with Finder
```

## Customize

### Change the ratio the size for zenkaku / hankaku

In default, this formula reduces the size of glyphs in Migu 1M (zenkaku font) and matches with SF Mono (hankaku font). The ratio is **82%**.

When you want to change this value, you can do this by `brew edit` and follow [comments][] in the formula.

[comments]: https://github.com/delphinus/homebrew-sfmono-square/blob/b99df9b00fa3c3c0637eba049f4619b363f69ed3/sfmono-square.rb#L43-L45

```sh
brew edit sfmono-square
```

See screenshots for examples [here][].

[here]: https://github.com/delphinus/homebrew-sfmono-square/issues/9#issuecomment-515827269

## Troubleshooting

### Install failure due to fontforge

```
==> Installing delphinus/sfmono-square/sfmono-square
Error: An exception occurred within a child process:
  RuntimeError: /usr/local/opt/fontforge not present or broken
Please reinstall fontforge. Sorry :(
```

The fontforge formula does not link their binaries in default. If you see this, try again after linking it.

```sh
brew link fontforge
# again
brew install sfmono-square
```

### VSCode shows “space” glyphs (U+0020) as double width.

See [#7][]

[#7]: https://github.com/delphinus/homebrew-sfmono-square/issues/7

## Screen Shots

<img width="746" alt="スクリーンショット 0001-05-23 21 47 37" src="https://user-images.githubusercontent.com/1239245/58253927-8e7a5080-7da4-11e9-9d6b-0520cea1438c.png">

<img width="746" alt="スクリーンショット 0001-05-23 21 42 22" src="https://user-images.githubusercontent.com/1239245/58253934-92a66e00-7da4-11e9-983d-1f90f9d8a846.png">

<img width="746" alt="スクリーンショット 0001-05-23 21 43 33" src="https://user-images.githubusercontent.com/1239245/58253939-95a15e80-7da4-11e9-92d9-5e9693cfbccb.png">
