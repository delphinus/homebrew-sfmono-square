# frozen_string_literal: true

# Formula to install the font: SF Mono Square
class SfmonoSquare < Formula
  desc "Square-sized SF Mono + Japanese fonts + nerd-fonts"
  homepage "https://github.com/delphinus/homebrew-sfmono-square"
  url "https://github.com/delphinus/homebrew-sfmono-square/archive/v3.1.0.tar.gz"
  sha256 "7633d2c35de856843c28dab79e14e7cbe0d011867faee7b75caf1f9cbbef4771"
  version "3.1.0"
  head "https://github.com/delphinus/homebrew-sfmono-square.git"

  depends_on "fontforge" => :build
  depends_on "python@3.11" => :build
  depends_on "pod2man" => :build

  resource "migu1mfonts" do
    output, = system_command Utils::Curl.curl_executable,
                             args: ["--version"],
                             print_stderr: true
    curl_name_and_version = output.sub(/^.*?lib(?=curl)/, "").sub(/\s+.*/m, "")
    # url "https://osdn.net/projects/mix-mplus-ipa/downloads/72511/migu-1m-20200307.zip",
    url "https://github.com/delphinus/homebrew-sfmono-square/files/12063197/migu-1m-20200307.zip",
        user_agent: curl_name_and_version
    sha256 "a4770fca22410668d2747d7898ed4d7ef5d92330162ee428a6efd5cf247d9504"
  end

  resource "sfmono" do
    url "https://developer.apple.com/design/downloads/SF-Mono.dmg"
    sha256 "a6a91880966db4a287a936286c1523b9dd1f5bbf5d4b9b5dcd8276df07bd4d6e"
  end

  def install
    _stage
    _compile

    (share / "fonts").install Dir["build/*.otf"]
    (share / "fonts/src").install Dir["*.otf"]
    (share / "fonts/src").install Dir["*.ttf"]

    dir = "script/convert_codepoints"
    system "#{Formula['pod2man'].opt_bin}/pod2man", "#{dir}/convert_codepoints", "#{dir}/convert_codepoints.1"
    bin.install "#{dir}/convert_codepoints"
    man1.install "#{dir}/convert_codepoints.1"
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
