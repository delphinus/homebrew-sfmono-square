# frozen_string_literal: true

# Formula to install the font: SF Mono Square
class SfmonoSquare < Formula
  desc "Square-sized SF Mono + Japanese fonts + nerd-fonts"
  homepage "https://github.com/delphinus/homebrew-sfmono-square"
  url "https://github.com/delphinus/homebrew-sfmono-square/archive/v3.3.0.tar.gz"
  sha256 "d299446f39272bfa941f4bebdd9688dff903623db02a73b53faf1a676d3734ad"
  version "3.3.0"
  head "https://github.com/delphinus/homebrew-sfmono-square.git"

  depends_on "fontforge" => :build
  depends_on "fonttools" => :build
  depends_on "python@3.14" => :build
  depends_on "pod2man" => :build

  resource "migu1mfonts" do
    output = `#{Utils::Curl.curl_executable} --version`
    curl_name_and_version = output.sub(/^.*?lib(?=curl)/, "").sub(/\s+.*/m, "")
    url "https://github.com/itouhiro/mixfont-mplus-ipa/releases/download/v2020.0307/migu-1m-20200307.zip",
        user_agent: curl_name_and_version
    sha256 "e4806d297e59a7f9c235b0079b2819f44b8620d4365a8955cb612c9ff5809321"
  end

  resource "sfmono" do
    url "https://developer.apple.com/design/downloads/SF-Mono.dmg"
    sha256 "6d4a0b78e3aacd06f913f642cead1c7db4af34ed48856d7171a2e0b55d9a7945"
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

    fontforge_lib = Formula["fontforge"].libexec / "lib/python3.14/site-packages"
    fonttools_lib = Formula["fonttools"].libexec / "lib/python3.14/site-packages"
    python = Formula["python@3.14"].bin / "python3.14"

    system python, "-c", <<~PYTHON
      import sys
      sys.path.append('#{buildpath / 'src'}')
      sys.path.append('#{fontforge_lib}')
      sys.path.append('#{fonttools_lib}')
      import build
      sys.exit(build.build('#{version}'))
    PYTHON
  end
end
