# SFMono Square - patched font: SFMono + Migu 1M + Nerd Fonts

<img width="598" alt="スクリーンショット 0001-05-23 21 40 50" src="https://user-images.githubusercontent.com/1239245/58253912-802c3480-7da4-11e9-9936-1f68326b9c38.png">

## What's this?

**SF Mono** is a font from Apple, that is clear, easy to read, and suitable for programming.  **SFMono Square** is based on **SF Mono**, and added glyphs for Japanese & patched for [Nerd Fonts][].

[Nerd Fonts]: https://github.com/ryanoasis/nerd-fonts

Thoughts and detail description here:

* [SF Mono を使って最高のプログラミング用フォントを作った話 - Qiita][qiita] (in Japanese)

[qiita]: https://qiita.com/delphinus/items/f472eb04ff91daf44274

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

### Some glyphs seem strange to see

SF Mono Square has almost the same codepoints as nerd-fonts' ones. But some are different because the original SF Mono has glyphs placed on the duplicated codepoints that nerd-fonts use.

| codepoint |                                                               SF Mono Square                                                               |                                                                  nerd-fonts                                                                  |                  |
|:---------:|:------------------------------------------------------------------------------------------------------------------------------------------:|:--------------------------------------------------------------------------------------------------------------------------------------------:|:----------------:|
|   0xF6D5  | <img alt=" 0xF6D5" width="32" src="https://user-images.githubusercontent.com/1239245/189081110-055b21d0-6868-43e3-bf9a-20f26f1c8a1b.png"> | <img alt="󿛕 0xFF6D5" width="32" src="https://user-images.githubusercontent.com/1239245/189081906-6034a767-e995-4863-a7cd-608e30e9b690.png"> | moved to 0xFF6D5 |
|   0xF6D6  | <img alt=" 0xF6D6" width="32" src="https://user-images.githubusercontent.com/1239245/189081128-96aa06ac-7a38-4cae-964b-87e9ae4f25af.png"> | <img alt="󿛖 0xFF6D6" width="32" src="https://user-images.githubusercontent.com/1239245/189081935-ffef5ed5-5d90-4cac-90ab-caf3c5adaa5f.png"> | moved to 0xFF6D6 |
|   0xF6D7  | <img alt=" 0xF6D7" width="32" src="https://user-images.githubusercontent.com/1239245/189081145-74953367-fe04-40be-81cd-c937431642b8.png"> | <img alt="󿛗 0xFF6D7" width="32" src="https://user-images.githubusercontent.com/1239245/189081958-8861eca6-7743-433c-a4cd-8dd06fa6ef74.png"> | moved to 0xFF6D7 |
|   0xF6D8  | <img alt=" 0xF6D8" width="32" src="https://user-images.githubusercontent.com/1239245/189081173-56466aed-056c-4c03-9184-17df58e1799a.png"> | <img alt="󿛘 0xFF6D8" width="32" src="https://user-images.githubusercontent.com/1239245/189081975-2c3e0a34-3307-49a1-a5f4-0d619bfa0070.png"> | moved to 0xFF6D8 |
|   0xF8FF  | <img alt=" 0xF8FF" width="32" src="https://user-images.githubusercontent.com/1239245/189081193-2f0f43e3-2910-4559-99a7-e5c52413645b.png"> | <img alt="󿣿 0xFF8FF" width="32" src="https://user-images.githubusercontent.com/1239245/189081984-85e2d466-bdc8-4d44-9eb5-ea2aa2855876.png"> | moved to 0xFF8FF |

See the detail on [this comment](https://github.com/delphinus/homebrew-sfmono-square/issues/67#issuecomment-1238868778).

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

<img width="746" alt="スクリーンショット 0003-04-21 9 20 16" src="https://user-images.githubusercontent.com/1239245/115479188-d8b32780-a282-11eb-9571-4fdc811ddd7c.png">

<img width="746" alt="スクリーンショット 0003-04-21 9 50 04" src="https://user-images.githubusercontent.com/1239245/115481194-0601d480-a287-11eb-8b03-c45f76d2371a.png">

<img width="746" alt="スクリーンショット 0001-05-23 21 47 37" src="https://user-images.githubusercontent.com/1239245/58253927-8e7a5080-7da4-11e9-9d6b-0520cea1438c.png">

<img width="746" alt="スクリーンショット 0001-05-23 21 42 22" src="https://user-images.githubusercontent.com/1239245/58253934-92a66e00-7da4-11e9-983d-1f90f9d8a846.png">

<img width="746" alt="スクリーンショット 0001-05-23 21 43 33" src="https://user-images.githubusercontent.com/1239245/58253939-95a15e80-7da4-11e9-92d9-5e9693cfbccb.png">
