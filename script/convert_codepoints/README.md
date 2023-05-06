# NAME

convert\_codepoints - convert files according to changes in SF Mono Square

# SYNOPSIS

    # convert all files below the current directory
    # from v2 => v3 (default values)
    % convert_codepoints .

    # specify versions
    % convert_codepoints -f v1 -t v3 .

    # specify a file
    % convert_codepoints -f v1 -t v3 /path/to/file

    # not show diffs, but execute
    % convert_codepoints -e /path/to/dir

# DESCRIPTION

This is a script to convert glyphs in your dotfiles according to versions of SF
Mono Square. Now this font has 3 versions that has some codepoints without
compatibility. This script can search a directory or file and convert
characters that have such codepoints according to supplied options.

You can specify dotfiles git directory for the typical usecase.

    % convert_codepoints /path/to/dotfiles

You can also check one file.

    % convert_codepoints /path/to/file

It does not edit files in examples above. Use **-e** to edit (carefully!).

    % convert_codepoints -e /path/to/file

In default, it ignores files below.

- Files under the directory `.git`.
- Non-text files.
- Large files that size is over 1MB.
- Count over 1000 files.
- Files in submodules.

## Changes In Codepoints For Versions

Here is an outline of changes in v1, v2, v3, nerd-fonts v2 and nerd-fonts v3.

### v1

Material glyphs in U+F500 .. U+F8FF and U+E800 .. U+EC46. They overwrites Apple
glyphs (U+F6D5 .. U+F6D8, U+F8FF), so v1 has no such ones.

Also, there are no glyphs from Codicons.

### v2

To use Apple glyphs, some glyphs in Material have moved.

    U+F6D5 .. U+F6D8 => U+FF6D5 .. U+FF6D8
    U+F8FF => U+FF8FF

So this time Material glyphs in U+F500 .. U+F6D4, U+FF6D5 .. U+FF6D8, U+F6D9 =>
U+F8FE, U+E800 .. U+EC46.

Now v2 has Codicons glyphs in U+FEA60 .. U+FEBEB not to overwrite Material ones.

### v3

v3 uses completely the same codepoints as nerd-fonts v3 ones.

    Material => U+F0001 .. U+F1AF0
    Apple    => U+F6D5 .. U+F6D8, U+F8FF
    Codicons => U+EA60 .. U+EBEB

### nerd-fonts v2

nerd-fonts v2 has errros on codepoints. That overwrites some codepoints except
PUA (Private USE Area - U+E000 .. U+F8FF).

### nerd-fonts v3

This solves errors above. It uses the same as ["v3"](#v3).

# OPTIONS

- **--from** _version_, **-f** _version_

    This specifies a version string to convert from. This accepts `"v1"`, `"v2"`,
    `"v3"`, `"nerd_fonts_v2"` or `"nerd_fonts_v3"`. `"nerd_fonts_XX"` means the
    codepoints from nerd-fonts.

    Default: `"v2"`

- **--to** _version_, **-t** _version_

    This is the one to convert to.

    Default: `"v3"`

- **--ignore-regex** _regex_, **-r** _regex_

    Ignore files matched this RegEx (Perl style).

    Default: `undef`

- **--max-files** _count_

    Finish if the file count is over this.

    Default: `1000`

- **--max-size** _size_

    Ignore if the file is larger than this bytes.

    Default: `1000000` (1MB)

- **--submodules**

    Search files in submodules.

- **--gitignore**

    Consider `.gitignore` file.

- **--execute**, **-e**

    Without this, it prints the diff only.

- **--help**, **-h**

    Show this document and exit.

# COPYRIGHT & LICENSE

Copyright 2023 JINNOUCHI Yasushi <me@delphinus.dev>

This library is free software; you may redistribute it and/or modify it under
the same terms as Perl itself.

# SEE ALSO

- [https://github.com/delphinus/homebrew-sfmono-square](https://github.com/delphinus/homebrew-sfmono-square)
- [https://www.nerdfonts.com](https://www.nerdfonts.com)
