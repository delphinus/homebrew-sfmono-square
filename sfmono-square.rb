# frozen_string_literal: true

class SfmonoSquare < Formula
  desc "Square-sized SF Mono + Japanese fonts + nerd-fonts"
  homepage "https://github.com/delphinus/homebrew-sfmono-square"
  url "https://github.com/delphinus/homebrew-sfmono-square/archive/v1.2.17.tar.gz"
  sha256 "c711a80ef7717f4f4b21108d320b7a84b4af52ec948f6c493306e2f28dbdd8ba"
  version "1.2.17"
  head "https://github.com/delphinus/homebrew-sfmono-square.git"

  depends_on "fontforge" => :build
  depends_on "python@3.9" => :build

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
    sha256 "fc0beba1460fbe0f1f6d7c0f1eff6e09dd9cd996a24595f47dcb332614ecd541"
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
    fontforge_lib = Formulary.factory("fontforge").lib / "python3.9/site-packages"

    python39 = Formulary.factory("python@3.9").bin / "python3"

    system python39, "-c", <<~PYTHON
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
