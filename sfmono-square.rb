class SfmonoSquare < Formula
  desc "Square-sized SF Mono + Japanese fonts + nerd-fonts"
  homepage "https://github.com/delphinus/homebrew-sfmono-square"
  url "https://github.com/ZulwiyozaPutra/SF-Mono-Font/archive/c18d1be46975d55039c3f058cf148742ddeb2723.zip"
  sha256 "d42e21f0696df0be75ea99ab669135ec5cf757b5f3fcf002abf49d284da7b0b8"
  version "0.1.20180605"
  depends_on "fontforge" => :build
  depends_on "python@2" => :build

  resource "migu1mfonts" do
    url "https://osdn.jp/frs/redir.php?m=gigenet&f=%2Fmix-mplus-ipa%2F63545%2Fmigu-1m-20150712.zip"
    sha256 "d4c38664dd57bc5927abe8f4fbea8f06a8ece3fea49ea02354d4e03ac6d15006"
  end

  resource "generate-oblique" do
    url "https://github.com/delphinus/homebrew-sfmono-square/raw/master/src/generate-oblique.pe"
    sha256 "be3874426b512955bbfb0f822f3cfc1f37e7ba610680776838ba3791512fd28c"
  end

  resource "generate-sfmono-mod" do
    url "https://github.com/delphinus/homebrew-sfmono-square/raw/master/src/generate-sfmono-mod.pe"
    sha256 "1f0e4fdb34bc072401b34b777145216d27ca3aa82b7c30ea9f15894229b2d17a"
  end

  resource "modify-migu1m" do
    url "https://github.com/delphinus/homebrew-sfmono-square/raw/master/src/modify-migu1m.pe"
    sha256 "0bd1a6eb88b4a3e9a9ef1125ce025c773e4fff2cfb4baddff310ac58e562a475"
  end

  resource "modify-sfmono" do
    url "https://github.com/delphinus/homebrew-sfmono-square/raw/master/src/modify-sfmono.pe"
    sha256 "227609a9e2383dbfba6c4b2649aac8c00a18f59f5d72fa7b5bb7ac2999b9a82c"
  end

  resource "font-patcher" do
    url "https://github.com/delphinus/homebrew-sfmono-square/raw/master/src/font-patcher"
    sha256 "861ac982e00d07c7043505b5b1e45612927724ee90fdc29e9aee833257ec0cd4"
  end

  resource "font-zip" do
    url "https://github.com/delphinus/homebrew-sfmono-square/raw/master/src/font.zip"
    sha256 "17e346c35c8d39d984870c9db18ca1fc2f12fe32dabf11b7389791bbb4de2e47"
  end

  resource "changelog-md" do
    url "https://github.com/delphinus/nerd-fonts-simple/raw/master/changelog.md"
    sha256 "37d8824943c35f21e3f0653d9c57601372741fff3ac81cd047ab3d446c5710ac"
  end

  def install
    resource("migu1mfonts").stage { buildpath.install Dir["*"] }
    resource("generate-oblique").stage { buildpath.install Dir["*"] }
    resource("generate-sfmono-mod").stage { buildpath.install Dir["*"] }
    resource("modify-migu1m").stage { buildpath.install Dir["*"] }
    resource("modify-sfmono").stage { buildpath.install Dir["*"] }
    resource("font-patcher").stage { buildpath.install Dir["*"] }
    resource("font-zip").stage { (buildpath/"src/glyphs").install Dir["*"] }
    resource("changelog-md").stage { buildpath.install Dir["*"] }

    system "fontforge", "-script", buildpath/"generate-oblique.pe"
    system "fontforge", "-script", buildpath/"modify-migu1m.pe"
    system "fontforge", "-script", buildpath/"modify-sfmono.pe"
    system "fontforge", "-script", buildpath/"generate-sfmono-mod.pe"
    Dir[
      "SFMonoSquare-Regular.otf",
      "SFMonoSquare-Bold.otf",
      "SFMonoSquare-RegularItalic.otf",
      "SFMonoSquare-BoldItalic.otf",
    ].each do |ttf|
      system "fontforge", "-lang=py", "-script", buildpath/"font-patcher", "-c", "-q", "-out", "build", "--square", buildpath/ttf
    end
    (share/"fonts").install Dir["build/*.otf"]
  end
end
