# frozen_string_literal: true

class SfmonoSquare < Formula
  desc "Square-sized SF Mono + Japanese fonts + nerd-fonts"
  homepage "https://github.com/delphinus/homebrew-sfmono-square"
  url "https://github.com/delphinus/homebrew-sfmono-square/archive/v1.1.1.tar.gz"
  sha256 "2b7caf6b834465675394b0d26a10c71146636281bcd14b29c52888d76c5c97e9"
  version "1.1.1"
  head "https://github.com/delphinus/homebrew-sfmono-square.git"

  depends_on "fontforge" => :build
  depends_on "python" => :build

  resource "migu1mfonts" do
    url "https://osdn.jp/frs/redir.php?m=gigenet&f=%2Fmix-mplus-ipa%2F63545%2Fmigu-1m-20150712.zip"
    sha256 "d4c38664dd57bc5927abe8f4fbea8f06a8ece3fea49ea02354d4e03ac6d15006"
  end

  def install
    resource("migu1mfonts").stage { buildpath.install Dir["*"] }

    sfmono_dir = Pathname.new "/Applications/Utilities/Terminal.app/Contents/Resources/Fonts"
      [
      "SFMono-Regular.otf",
      "SFMono-RegularItalic.otf",
      "SFMono-Bold.otf",
      "SFMono-BoldItalic.otf"
      ].each do |otf|
      cp sfmono_dir / otf, buildpath
    end

    # Set path for fontforge library to use it in Python
    ENV["PYTHONPATH"] = Formulary.factory("fontforge").opt_lib / "python3.7/site-packages"

    system buildpath / "bin/sfmono-square", version
    (share / "fonts").install Dir["build/*.otf"]
    (share / "fonts/src").install Dir["*.otf"]
    (share / "fonts/src").install Dir["*.ttf"]
  end
end
