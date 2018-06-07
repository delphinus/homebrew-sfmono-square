class SfmonoSquare < Formula
  desc "Square-sized SF Mono + Japanese fonts + nerd-fonts"
  homepage "https://github.com/delphinus/homebrew-sfmono-square"
  url "https://github.com/delphinus/homebrew-sfmono-square/archive/v0.1.2018060713.tar.gz"
  sha256 "5a5d8695c194e3bd72265018c3c36d49773a588f12df3579318929bd36a2d934  -
"
  version "0.1.2018060713"
  depends_on "fontforge" => :build
  depends_on "python@2" => :build

  resource "sfmono" do
    url "https://github.com/ZulwiyozaPutra/SF-Mono-Font/archive/c18d1be46975d55039c3f058cf148742ddeb2723.zip"
    sha256 "d42e21f0696df0be75ea99ab669135ec5cf757b5f3fcf002abf49d284da7b0b8"
  end

  resource "migu1mfonts" do
    url "https://osdn.jp/frs/redir.php?m=gigenet&f=%2Fmix-mplus-ipa%2F63545%2Fmigu-1m-20150712.zip"
    sha256 "d4c38664dd57bc5927abe8f4fbea8f06a8ece3fea49ea02354d4e03ac6d15006"
  end

  resource "changelog-md" do
    url "https://github.com/delphinus/nerd-fonts-simple/raw/master/changelog.md"
    sha256 "37d8824943c35f21e3f0653d9c57601372741fff3ac81cd047ab3d446c5710ac"
  end

  def install
    resource("sfmono").stage { buildpath.install Dir["*"] }
    resource("migu1mfonts").stage { buildpath.install Dir["*"] }
    resource("changelog-md").stage { buildpath.install Dir["*"] }

    system "fontforge", "-script", buildpath/"src/generate-oblique.pe"
    system "fontforge", "-script", buildpath/"src/modify-migu1m.pe"
    system "fontforge", "-script", buildpath/"src/modify-sfmono.pe"
    system "fontforge", "-script", buildpath/"src/generate-sfmono-mod.pe"
    Dir[
      "SFMonoSquare-Regular.otf",
      "SFMonoSquare-Bold.otf",
      "SFMonoSquare-RegularItalic.otf",
      "SFMonoSquare-BoldItalic.otf",
    ].each do |ttf|
      system "fontforge", "-lang=py", "-script", buildpath/"src/font-patcher", "-c", "-q", "-out", "build", "--square", buildpath/ttf
    end
    (share/"fonts").install Dir["build/*.otf"]
  end
end
