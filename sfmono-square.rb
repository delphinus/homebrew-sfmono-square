# frozen_string_literal: true

# Formula to install the font: SF Mono Square
class SfmonoSquare < Formula
  desc "Square-sized SF Mono + Japanese fonts + nerd-fonts"
  homepage "https://github.com/delphinus/homebrew-sfmono-square"
  url "https://github.com/delphinus/homebrew-sfmono-square/archive/v2.1.1-pre-05.tar.gz"
  sha256 "587528ecc31685e4572a11ad2512bccdca3a238c49d22ef7ce81466827eb5c3b"
  version "2.1.1-pre-05"
  head "https://github.com/delphinus/homebrew-sfmono-square.git"

  depends_on "fontforge" => :build
  depends_on "python@3.11" => :build

  resource "migu1mfonts" do
    output, = system_command curl_executable,
                             args: ["--version"],
                             print_stderr: true
    curl_name_and_version = output.sub(/^.*?lib(?=curl)/, "").sub(/\s+.*/m, "")
    url "https://osdn.net/projects/mix-mplus-ipa/downloads/72511/migu-1m-20200307.zip",
        user_agent: curl_name_and_version
    sha256 "a4770fca22410668d2747d7898ed4d7ef5d92330162ee428a6efd5cf247d9504"
  end

  resource "sfmono" do
    url "https://developer.apple.com/design/downloads/SF-Mono.dmg"
    sha256 "abaf6d62cd5b17ae1837ab40a35386733a3f603cf641a84cf59b1d7fb4caac39"
  end

  def install
    _stage
    _compile

    (share / "fonts").install Dir["build/*.otf"]
    (share / "fonts/src").install Dir["*.otf"]
    (share / "fonts/src").install Dir["*.ttf"]
  end

  def _stage
    resource("migu1mfonts").stage { buildpath.install Dir["*"] }

    resource("sfmono").stage do
      system "/usr/bin/xar", "-xf", "SF Mono Fonts.pkg"
      system "/bin/bash", "-c", "cat SFMonoFonts.pkg/Payload | gunzip -dc | cpio -i"
      ["SF-Mono-Regular.otf", "SF-Mono-RegularItalic.otf", "SF-Mono-Bold.otf", "SF-Mono-BoldItalic.otf"].each do |otf|
        buildpath.install "Library/Fonts/#{otf}"
      end
    end
  end

  def _compile
    # Uncomment and change this value to enlarge glyphs from Migu1M.
    # See https://github.com/delphinus/homebrew-sfmono-square/issues/9
    # ENV["MIGU1M_SCALE"] = "82"

    # Set path for fontforge library to use it in Python
    fontforge_lib = Formulary.factory("fontforge").lib / "python3.11/site-packages"

    python311 = Formulary.factory("python@3.11").bin / "python3.11"

    system python311, "-c", <<~PYTHON
      import sys
      sys.path.append('#{buildpath / 'src'}')
      sys.path.append('#{fontforge_lib}')
      import build
      sys.exit(build.build('#{version}'))
    PYTHON
  end
end
