class SfmonoSquare < Formula
  desc "Square-sized SF Mono + Japanese fonts + nerd-fonts"
  homepage "https://github.com/delphinus/homebrew-sfmono-square"
  url "https://github.com/delphinus/homebrew-sfmono-square/archive/v0.1.2018121601.tar.gz"
  sha256 "3de9cf71a169ef2fec6d773ab25e1de6f4623f790c3f10b8ff719810140d6528"
  version "0.1.2018121601"
  head "https://github.com/delphinus/homebrew-sfmono-square.git"

  depends_on "fontforge" => :build
  depends_on "python@2" => :build

  resource "migu1mfonts" do
    url "https://osdn.jp/frs/redir.php?m=gigenet&f=%2Fmix-mplus-ipa%2F63545%2Fmigu-1m-20150712.zip"
    sha256 "d4c38664dd57bc5927abe8f4fbea8f06a8ece3fea49ea02354d4e03ac6d15006"
  end

  # made by homebrew-pypi-poet
  resource "futures" do
    url "https://files.pythonhosted.org/packages/1f/9e/7b2ff7e965fc654592269f2906ade1c7d705f1bf25b7d469fa153f7d19eb/futures-3.2.0.tar.gz"
    sha256 "9ec02aa7d674acb8618afb127e27fde7fc68994c0437ad759fa094a574adb265"
  end

  def install
    resource("migu1mfonts").stage { buildpath.install Dir["*"] }
    resource("futures").stage { buildpath.install Dir["*"] }

    sfmono_dir = Pathname.new '/Applications/Utilities/Terminal.app/Contents/Resources/Fonts'
    [
      'SFMono-Regular.otf',
      'SFMono-RegularItalic.otf',
      'SFMono-Bold.otf',
      'SFMono-BoldItalic.otf',
    ].each do |otf|
      cp sfmono_dir/otf, buildpath
    end

    system buildpath/"bin/sfmono-square", version
    (share/"fonts").install Dir["build/*.otf"]
  end
end
