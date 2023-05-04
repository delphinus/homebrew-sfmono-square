# NAME

convert\_codepoints

# SYNOPSIS

    # convert files from v2 => v3 (default values)
    % bin/convert_codepoints

    # specify versions
    % bin/convert_codepoints -f v1 -t v3

# DESCRIPTION

This is a script to convert glyphs in your dotfiles according to versions of SF
Mono Square. Now this font has 3 versions that has some codepoints without
compatibility. This script can search any file in the current directory and
convert characters that have such codepoints according to supplied options.

Here is an outline of changes in v1, v2, v3, nerd-fonts v2 and nerd-fonts v3.

## v1

Material glyphs in U+F500 .. U+F8FF and U+E800 .. U+EC46. They overwrites Apple
glyphs (U+F6D5 .. U+F6D8, U+F8FF), so v1 has no such ones.

Also, there are no glyphs from Codicons.

## v2

To use Apple glyphs, some glyphs in Material have moved.

    U+F6D5 .. U+F6D8 => U+FF6D5 .. U+FF6D8
    U+F8FF => U+FF8FF

So this time Material glyphs in U+F500 .. U+F6D4, U+FF6D5 .. U+FF6D8, U+F6D9 =>
U+F8FE, U+E800 .. U+EC46.

Now v2 has Codicons glyphs in U+FEA60 .. U+FEBEB not to overwrite Material ones.

## v3

v3 uses completely the same codepoints as nerd-fonts v3 ones.

Material => U+F0001 .. U+F1AF0
Apple    => U+F6D5 .. U+F6D8, U+F8FF
Codicons => U+EA60 .. U+EBEB

## nerd-fonts v2

nerd-fonts v2 has errros on codepoints. That overwrites some codepoints except
PUA (Private USE Area - U+E000 .. U+F8FF).

## nerd-fonts v3

This solves errors above. It uses the same as ["v3"](#v3).

# OPTIONS

    --from, -f [version]    This specifies a version string to convert from.
                            This accepts "v1", "v2", "v3", "nerd_fonts_v2" or
                            "nerd_fonts_v3". "nerd_fonts_XX" means the
                            codepoints from nerd-fonts. Default: "v2"
    --to, -t [version]      This is the one to convert to. Default: "v3"
    --dry-run, -n           Dry-run. With this, it prints the diff only.

# COPYRIGHT & LICENSE

JINNOUCHI Yasushi <me@delphinus.dev>

MIT License
