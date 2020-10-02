# frozen_string_literal: true

class SfmonoSquare < Formula
  desc "Square-sized SF Mono + Japanese fonts + nerd-fonts"
  homepage "https://github.com/delphinus/homebrew-sfmono-square"
  url "https://github.com/delphinus/homebrew-sfmono-square/archive/v1.2.11.tar.gz"
  sha256 "fd6765a9000d887ba38b467bbc80c6fe811dbc7ae32912d2701313dccf0458a3"
  version "1.2.11"
  head "https://github.com/delphinus/homebrew-sfmono-square.git"

  depends_on "fontforge" => :build
  depends_on "python" => :build

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
    sha256 "d91ed5d03a249b515dd1ba9aba7127dcd85bd1c7d2a3a7687531524b6d9a6a6d"
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

    system "python3", "-c", <<~PYTHON
      import sys
      sys.path.append('#{buildpath / 'src'}')
      sys.path.append('#{fontforge_lib}')
      import build
      sys.exit(build.build('#{version}'))
    PYTHON

    (share / "fonts").install Dir["build/*.otf"]
    (share / "fonts/src").install Dir["*.otf"]
    (share / "fonts/src").install Dir["*.ttf"]
  end
end
