# typed: strict
# frozen_string_literal: true

# Formula to install the font: SF Mono Square
class SfmonoSquare < Formula
  desc "Square-sized SF Mono + Japanese fonts + nerd-fonts"
  homepage "https://github.com/delphinus/homebrew-sfmono-square"
  url "https://github.com/delphinus/homebrew-sfmono-square/archive/refs/tags/v3.5.1.tar.gz"
  version "3.5.1"
  sha256 "cab102100deeac81772149a09f0b6553354a7b0127d83c11d9be86c4da47aa9a"
  head "https://github.com/delphinus/homebrew-sfmono-square.git"

  depends_on "fontforge" => :build
  depends_on "fonttools" => :build
  depends_on "pod2man" => :build
  depends_on "python@3.14" => :build

  # The four fonts taken out of the dmg. The dmg is pinned by its own sha256,
  # so these are fixed too, and they are checked to make sure the fonts the
  # build reads are the fonts the dmg carries. See _stage.
  SFMONO_OTFS = {
    "SF-Mono-Regular.otf"       => "d7186273849a922b3eafbbdd8289d1e708a2c7f7893ec90961d382353c872d49",
    "SF-Mono-RegularItalic.otf" => "9fe5176e31a1ba9ba685ea3c3fab97f76c51574829bb06f2ab47c561a55dbecc",
    "SF-Mono-Bold.otf"          => "88ba41467bea5c3f29273b6b2f630a95aa03589536de54ef41ac4db250d6a0a3",
    "SF-Mono-BoldItalic.otf"    => "e177ffe6d3a27f513b54fea41a6e76c6c3d4b31a15d982a84bdc1b41972c093c",
  }.freeze

  # The first four bytes of a xar archive, which "SF Mono Fonts.pkg" is.
  XAR_MAGIC = "xar!"

  resource "migu1mfonts" do
    output = `#{Utils::Curl.curl_executable} --version`
    curl_name_and_version = output.sub(/^.*?lib(?=curl)/, "").sub(/\s+.*/m, "")
    url "https://github.com/itouhiro/mixfont-mplus-ipa/releases/download/v2020.0307/migu-1m-20200307.zip",
        user_agent: curl_name_and_version
    sha256 "e4806d297e59a7f9c235b0079b2819f44b8620d4365a8955cb612c9ff5809321"
  end

  # NOTE: The dmg is staged as it is. Homebrew opens a dmg by mounting it,
  # which the build sandbox no longer lets through. See _stage.
  resource "sfmono" do
    url "https://developer.apple.com/design/downloads/SF-Mono.dmg", using: :nounzip
    sha256 "6d4a0b78e3aacd06f913f642cead1c7db4af34ed48856d7171a2e0b55d9a7945"
  end

  def install
    _stage
    _compile

    (share / "fonts").install Dir["build/*.otf"]
    (share / "fonts/src").install Dir["*.otf"]
    (share / "fonts/src").install Dir["*.ttf"]

    dir = "script/convert_codepoints"
    system "#{formula_opt_bin("pod2man")}/pod2man", "#{dir}/convert_codepoints", "#{dir}/convert_codepoints.1"
    bin.install "#{dir}/convert_codepoints"
    man1.install "#{dir}/convert_codepoints.1"
  end

  def _stage
    resource("migu1mfonts").stage { buildpath.install Dir["*"] }

    resource("sfmono").stage do
      # NOTE: The dmg cannot be mounted. Homebrew denies mach-lookup in the
      # build sandbox since 2026-09-09, so `hdiutil attach` dies with "Device
      # not configured" without the Mach services it needs. `hdiutil convert`
      # only decodes the image, needs none of them and still works, so the
      # image is turned into a plain one and read without a filesystem.
      system "/usr/bin/hdiutil", "convert", "-quiet", "SF-Mono.dmg", "-format", "UDTO", "-o", "raw"
      _carve_pkg Pathname("raw.cdr"), Pathname("SF Mono Fonts.pkg")

      system "/usr/bin/xar", "-xf", "SF Mono Fonts.pkg"
      system "/bin/bash", "-c", "cat SFMonoFonts.pkg/Payload | gunzip -dc | cpio -i"
      SFMONO_OTFS.each do |otf, sha256|
        path = Pathname("Library/Fonts/#{otf}")
        actual = path.sha256
        odie "#{otf} is not the one the dmg carries: #{actual}" if actual != sha256

        buildpath.install path
      end
    end
  end

  # Copies "SF Mono Fonts.pkg" out of a plain disk image, without a filesystem
  # driver. The pkg is the only xar archive on the image, so it is found by its
  # magic, and everything after it is handed to xar, which reads the ranges its
  # own table of contents points at and ignores the rest. A wrong offset or a
  # pkg that is not in one piece does not pass quietly: xar carries a SHA-1 of
  # every file it holds, and the fonts are checked against SFMONO_OTFS as well.
  def _carve_pkg(image, pkg)
    offsets = _xar_offsets(image)
    odie "expected 1 xar archive on the image, found #{offsets.length}" if offsets.length != 1

    image.open("rb") do |src|
      src.seek offsets.fetch(0)
      pkg.open("wb") { |dst| IO.copy_stream(src, dst) }
    end
    image.unlink
  end

  # Where XAR_MAGIC sits in the image. The image is read in chunks, keeping the
  # last 3 bytes of each one so that a magic split across two of them is found.
  def _xar_offsets(image)
    offsets = []
    image.open("rb") do |f|
      base = 0
      tail = +""
      while (buf = f.read(8 * 1024 * 1024))
        window = tail + buf
        pos = 0
        while (i = window.index(XAR_MAGIC, pos))
          offsets << (base - tail.bytesize + i)
          pos = i + 1
        end
        base += buf.bytesize
        tail = window[-(XAR_MAGIC.bytesize - 1)..] || +""
      end
    end
    offsets
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
      sys.path.append('#{buildpath / "src"}')
      sys.path.append('#{fontforge_lib}')
      sys.path.append('#{fonttools_lib}')
      import build
      sys.exit(build.build('#{version}'))
    PYTHON
  end
end
