class SfmonoSquare < Formula
  desc ""
  homepage ""
  url "https://github.com/ZulwiyozaPutra/SF-Mono-Font/archive/c18d1be46975d55039c3f058cf148742ddeb2723.zip"
  sha256 "d42e21f0696df0be75ea99ab669135ec5cf757b5f3fcf002abf49d284da7b0b8"
  depends_on "fontforge" => :build
  depends_on "python@2" => :build

  resource "migu1mfonts" do
    url "https://osdn.jp/frs/redir.php?m=gigenet&f=%2Fmix-mplus-ipa%2F63545%2Fmigu-1m-20150712.zip"
    sha256 "d4c38664dd57bc5927abe8f4fbea8f06a8ece3fea49ea02354d4e03ac6d15006"
  end

  resource "generate-oblique" do
    url "https://github.com/delphinus/homebrew-sfmono-square/raw/master/src/generate-oblique.pe"
    sha256 "d8e1a54bfab7633f35630939aeae242bf16b3f11a747f451d4e02843141a19cb"
  end

  resource "generate-sfmono-mod" do
    url "https://github.com/delphinus/homebrew-sfmono-square/raw/master/src/generate-sfmono-mod.pe"
    sha256 "b2fa06022a16205746d9350a1e2ad18c1b1bfd099729da7fad093674a3fa6968"
  end

  resource "modify-migu1m" do
    url "https://github.com/delphinus/homebrew-sfmono-square/raw/master/src/modify-migu1m.pe"
    sha256 "157b48ed38dd4ad10622fe2e48a843b1c5ff2698f07d71c497ae584334bfbb59"
  end

  resource "modify-sfmono" do
    url "https://github.com/delphinus/homebrew-sfmono-square/raw/master/src/modify-sfmono.pe"
    sha256 "07d4356c864b76e5b58212872ee12d492ab334b3e7248b3a535006bca84439ad"
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
    # ENV.deparallelize  # if your formula fails when building in parallel
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

  test do
    # `test do` will create, run in and delete a temporary directory.
    #
    # This test will fail and we won't accept that! For Homebrew/homebrew-core
    # this will need to be a test that verifies the functionality of the
    # software. Run the test with `brew test homebrew`. Options passed
    # to `brew install` such as `--HEAD` also need to be provided to `brew test`.
    #
    # The installed folder is not in the path, so use the entire path to any
    # executables being tested: `system "#{bin}/program", "do", "something"`.
    system "false"
  end
end
