# frozen_string_literal: true

class SfmonoSquare < Formula
  desc "Square-sized SF Mono + Japanese fonts + nerd-fonts"
  homepage "https://github.com/delphinus/homebrew-sfmono-square"
  url "https://github.com/delphinus/homebrew-sfmono-square/archive/v1.2.4.tar.gz"
  sha256 "6bdabf2751a7fdcd39ee366f8d933b22efdd808e360b1e57e7c14f4ec1f17b11"
  version "1.2.4"
  head "https://github.com/delphinus/homebrew-sfmono-square.git"

  depends_on "fontforge" => :build
  depends_on "python@3.8" => :build

  resource "migu1mfonts" do
    url "https://osdn.jp/frs/redir.php?m=gigenet&f=%2Fmix-mplus-ipa%2F63545%2Fmigu-1m-20150712.zip"
    sha256 "d4c38664dd57bc5927abe8f4fbea8f06a8ece3fea49ea02354d4e03ac6d15006"
  end

  resource "sfmono" do
    url "https://developer.apple.com/design/downloads/SF-Mono.dmg"
    sha256 "e44347f272290875f2ae03866799d3d0958b4e26bc871cb6f4d1c241d5ba507d"
  end

  def install
    resource("migu1mfonts").stage { buildpath.install Dir["*"] }

    resource("sfmono").stage do
      system "/usr/bin/xar", "-xf", "SF Mono Fonts.pkg"
      system "/bin/bash", "-c", "cat SFMonoFonts.pkg/Payload | gunzip -dc | cpio -i"
      [
        "SF-Mono-Regular.otf",
        "SF-Mono-RegularItalic.otf",
        "SF-Mono-Bold.otf",
        "SF-Mono-BoldItalic.otf"
      ].each do |otf|
        buildpath.install "Library/Fonts/" + otf
      end
    end

    # Uncomment and change this value to enlarge glyphs from Migu1M.
    # See https://github.com/delphinus/homebrew-sfmono-square/issues/9
    # ENV["MIGU1M_SCALE"] = "82"

    # Set path for fontforge library to use it in Python
    fontforge_lib = Formulary.factory("fontforge").lib / "python3.8/site-packages"
    # Supply the full path for Python3.8 executable to use with fontforge
    python38 = Formulary.factory("python@3.8").bin / "python3"

    system python38, "-c", <<~PYTHON
      import sys
      sys.path.append('#{buildpath / "src"}')
      sys.path.append('#{fontforge_lib}')
      import build
      sys.exit(build.build('#{version}'))
    PYTHON

    (share / "fonts").install Dir["build/*.otf"]
    (share / "fonts/src").install Dir["*.otf"]
    (share / "fonts/src").install Dir["*.ttf"]
  end
end
