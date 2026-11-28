"""README hero: a terminal drawn with SF Mono Square, with the cell grid shown over a table.

python hero.py OUT            # for a wide screen
python hero.py OUT --narrow   # for a phone, larger text in fewer columns
"""

import subprocess
import sys

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

FONTS = (
    subprocess.check_output(["brew", "--prefix", "sfmono-square"], text=True).strip()
    + "/share/fonts"
)
fp = lambda st: f"{FONTS}/SFMonoSquare-{st}.otf"
TT = TTFont(fp("Regular"), lazy=True)
CMAP = TT.getBestCmap()
HMTX = TT["hmtx"]
EXT = {
    k: TTFont(f"{FONTS}/SFMonoSquareExt-{k}.ttf", lazy=True).getBestCmap()
    for k in ("P1", "P2")
}

# The colours of the other images of README (GitHub's dark theme), vivid ones for the terminal too.
PAGE, WIN, TITLEBAR, EDGE = (13, 17, 23), (22, 27, 34), (33, 38, 45), (48, 54, 61)
FG, DIM = (230, 237, 243), (125, 133, 144)
BLUE, ORANGE, PURPLE, GREEN = (
    (88, 166, 255),
    (240, 136, 62),
    (188, 140, 255),
    (63, 185, 80),
)
RED, YELLOW, CYAN = (255, 123, 114), (227, 179, 65), (57, 197, 207)
BAR, BAR2, DARK = (48, 54, 61), (33, 38, 45), (13, 17, 23)
T = "│"


def cells(ch):
    c = ord(ch)
    if c >= 0x20000:
        return 2
    return HMTX[CMAP[c]][0] // 1024 if c in CMAP else 1


def L(*segs):
    """A line: a list of (text, fg, bg, style), where style is R, B, I or a style name."""
    return [s if len(s) == 4 else (s + (None, "R"))[:4] for s in segs]


def width(line):
    return sum(cells(ch) for t, *_ in line if t != "FILL" for ch in t)


def prompt():
    return [
        L(
            ("\uf07b ~/src/demo ", FG, BAR, "R"),
            ("\ue0b0", BAR, BAR2, "R"),
            (" \uf418 main ", PURPLE, BAR2, "R"),
            ("\ue0b0", BAR2, None, "R"),
            (" \uf00c", GREEN),
        ),
        L(("❯ ", GREEN, None, "B"), ("nvim 設定.lua", FG)),
        L(),
        L(("-- 全角は 2 セル、半角は 1 セル", DIM, None, "I")),
    ]


def statusline(narrow):
    if narrow:
        right = [("\ue0b2", BLUE, WIN, "R")]
    else:
        right = [
            ("\ue0b2", BAR2, WIN, "R"),
            (" utf-8 ", FG, BAR2, "R"),
            ("\ue0b2", BAR, BAR2, "R"),
            (" lua ", FG, BAR, "R"),
            ("\ue0b2", BLUE, BAR, "R"),
        ]
    return L(
        (" NORMAL ", DARK, BLUE, "B"),
        ("\ue0b0", BLUE, BAR, "R"),
        (" \ue0a0 main ", FG, BAR, "R"),
        ("\ue0b0", BAR, BAR2, "R"),
        (" \ue620 設定.lua ", FG, BAR2, "R"),
        ("\ue0b0", BAR2, WIN, "R"),
        ("FILL", FG, WIN, "R"),
        *right,
        (" 6:9 ", DARK, BLUE, "B"),
    )


def table():
    def row(weight, name, style, italic):
        return L(
            (T + " ", BLUE),
            (f"{weight:<8}", FG, None, style),
            (" " + T + " ", BLUE),
            (name + "  ", FG, None, style),
            (" " + T + " ", BLUE),
            ("漢字かな Aa ", FG, None, style),
            ("Aa", FG, None, italic),
            (" " + T, BLUE),
        )

    return [
        L(("┌──────────┬────────┬────────────────┐", BLUE)),
        L(
            (T + " ", BLUE),
            ("Weight  ", YELLOW, None, "B"),
            (" " + T + " ", BLUE),
            ("太さ  ", YELLOW, None, "B"),
            (" " + T + " ", BLUE),
            ("見本          ", YELLOW, None, "B"),
            (" " + T, BLUE),
        ),
        L(("├──────────┼────────┼────────────────┤", BLUE)),
        row("Light", "細字", "Light", "LightItalic"),
        row("Regular", "標準", "Regular", "RegularItalic"),
        row("Bold", "太字", "Bold", "BoldItalic"),
        row("Heavy", "極太", "Heavy", "HeavyItalic"),
        L(("└──────────┴────────┴────────────────┘", BLUE)),
    ]


TREE = [
    L(("    ", FG), ("\uf07b", BLUE), (" ~/src/demo", BLUE, None, "B")),
    L(("    ", FG), ("├── ", DIM), ("\uf07b", BLUE), (" lua/", BLUE)),
    L(("    ", FG), ("│   └── ", DIM), ("\ue620", BLUE), (" 設定.lua", FG)),
    L(("    ", FG), ("├── ", DIM), ("\uf48a", CYAN), (" README.md", FG)),
    L(("    ", FG), ("├── ", DIM), ("\uf15c", FG), (" 日本語のメモ.txt", FG)),
    L(("    ", FG), ("├── ", DIM), ("\uf1d3", ORANGE), (" .gitignore", FG)),
    L(("    ", FG), ("└── ", DIM), ("\uf308", BLUE), (" Dockerfile", FG)),
]


def wide():
    tab = table()
    lines = (
        prompt()
        + [
            L(
                ("local ", RED, None, "I"),
                ("fonts", FG),
                (" = { ", FG),
                ('"SF Mono"', GREEN),
                (", ", FG),
                ('"Migu 1M"', GREEN),
                (", ", FG),
                ('"Plangothic"', GREEN),
                (" }", FG),
            ),
            L(
                ("local ", RED, None, "I"),
                ("ext_b", FG),
                (" = ", FG),
                ('"𠀋𡈽𡌛𡑮𡢽𠮟𡚴𡸴𣇄𣗄"', GREEN),
                ("  ", FG),
                ("-- 拡張 B", DIM, None, "I"),
            ),
            L(),
        ]
        + [tab[i] + (TREE[i - 1] if 1 <= i <= 7 else []) for i in range(8)]
        + [L(), statusline(False)]
    )
    return dict(W=1600, SIZE=40, COLS=66, LINES=lines, GRID=((7, 15), (0, 38)))


def narrow():
    lines = (
        prompt()
        + [
            L(
                ("local ", RED, None, "I"),
                ("ext_b", FG),
                (" = ", FG),
                ('"𠀋𡈽𡌛𡑮𡢽𠮟"', GREEN),
            ),
            L(),
        ]
        + table()
        + [L(), statusline(True)]
    )
    return dict(W=1080, SIZE=48, COLS=40, LINES=lines, GRID=((6, 14), (0, 38)))


def draw(layout, out, is_narrow):
    W, SIZE, COLS, LINES = layout["W"], layout["SIZE"], layout["COLS"], layout["LINES"]
    CW, CH = SIZE // 2, SIZE
    cache = {}

    def font_for(ch, st):
        c = ord(ch)
        key = st
        if c >= 0x20000:
            key = "P1" if c in EXT["P1"] and c < 0x30000 else "P2"
            path = f"{FONTS}/SFMonoSquareExt-{key}.ttf"
        else:
            name = {"R": "Regular", "B": "Bold", "I": "RegularItalic"}.get(st, st)
            path = fp(name)
        if key not in cache:
            cache[key] = ImageFont.truetype(path, SIZE)
        return cache[key]

    ui = lambda s, st="Regular": ImageFont.truetype(fp(st), s)
    TW, TH = COLS * CW, len(LINES) * CH
    PAD, BARH = 28, 50
    wx0 = (W - TW - 2 * PAD) // 2
    title = ui(80, "Semibold")
    if is_narrow:
        # The subtitle and the caption go on lines of their own.
        heads = [
            ("SF Mono Square", title, FG, 44),
            ("SF Mono + Migu 1M + Nerd Fonts", ui(44), DIM, 150),
            ("A Japanese letter takes exactly", ui(42), FG, 226),
            ("two cells, so every column lines up.", ui(42), FG, 282),
        ]
        wy0 = 380
    else:
        heads = [
            ("SF Mono Square", title, FG, 44),
            (
                "A Japanese letter takes exactly two cells, so every column lines up.",
                ui(34),
                FG,
                152,
            ),
        ]
        wy0 = 232
    wx1, wy1 = wx0 + TW + 2 * PAD, wy0 + BARH + TH + 2 * PAD
    feats = [
        ("6 weights", "with italics", BLUE),
        ("Kanji", "up to Extension J", ORANGE),
        ("Nerd Fonts", "v3 codepoints", PURPLE),
        ("1 : 2", "half to full width", GREEN),
    ]
    per_row = 2 if is_narrow else 4
    H = (
        wy1
        + 48
        + (len(feats) // per_row) * (150 if is_narrow else 128)
        + (40 if is_narrow else 24)
    )
    img = Image.new("RGB", (W, H), PAGE)
    d = ImageDraw.Draw(img)
    for text, font, colour, y in heads:
        d.text((wx0, y), text, font=font, fill=colour)
    if not is_narrow:
        d.text(
            (wx0 + d.textlength("SF Mono Square  ", font=title), 72),
            "SF Mono + Migu 1M + Nerd Fonts",
            font=ui(40),
            fill=DIM,
        )

    d.rounded_rectangle(
        (wx0, wy0, wx1, wy1), radius=16, fill=WIN, outline=EDGE, width=2
    )
    d.rounded_rectangle((wx0, wy0, wx1, wy0 + BARH), radius=16, fill=TITLEBAR)
    d.rectangle((wx0 + 2, wy0 + 30, wx1 - 2, wy0 + BARH), fill=TITLEBAR)
    for i, c in enumerate(((255, 95, 87), (254, 188, 46), (40, 200, 64))):
        d.ellipse((wx0 + 22 + i * 30, wy0 + 16, wx0 + 40 + i * 30, wy0 + 34), fill=c)
    tx0, ty0 = wx0 + PAD, wy0 + BARH + PAD
    asc = round(SIZE * 1638 / 2048)
    for r, line in enumerate(LINES):
        fill = COLS - width(line)
        x = 0
        y = ty0 + r * CH
        for text, fg, bg, st in line:
            if text == "FILL":
                text = " " * fill
            for ch in text:
                n = cells(ch)
                if bg:
                    d.rectangle(
                        (tx0 + x * CW, y, tx0 + (x + n) * CW - 1, y + CH - 1), fill=bg
                    )
                if 0xE0A0 <= ord(ch) <= 0xE0D7:
                    # Clip a Powerline glyph to its row, as a terminal does.
                    layer = Image.new("RGBA", (n * CW + 2 * CW, CH), (0, 0, 0, 0))
                    ImageDraw.Draw(layer).text(
                        (CW, asc), ch, font=font_for(ch, st), fill=fg, anchor="ls"
                    )
                    img.paste(layer, (tx0 + x * CW - CW, y), layer)
                elif ch != " ":
                    d.text(
                        (tx0 + x * CW, y + asc),
                        ch,
                        font=font_for(ch, st),
                        fill=fg,
                        anchor="ls",
                    )
                x += n
        assert x <= COLS, (r, x)

    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    o = ImageDraw.Draw(ov)
    (r0, r1), (c0, c1) = layout["GRID"]
    for cx in range(c0, c1 + 1):
        o.line(
            (tx0 + cx * CW, ty0 + r0 * CH, tx0 + cx * CW, ty0 + r1 * CH),
            fill=ORANGE + (120,),
        )
    for ry in range(r0, r1 + 1):
        o.line(
            (tx0 + c0 * CW, ty0 + ry * CH, tx0 + c1 * CW, ty0 + ry * CH),
            fill=ORANGE + (120,),
        )
    img.paste(Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"))
    d = ImageDraw.Draw(img)

    fw = (wx1 - wx0) // per_row
    for i, (a, b, c) in enumerate(feats):
        x = wx0 + (i % per_row) * fw
        y = wy1 + 48 + (i // per_row) * (150 if is_narrow else 128)
        d.text((x, y), a, font=ui(56 if is_narrow else 48, "Semibold"), fill=c)
        d.text(
            (x, y + (74 if is_narrow else 64)),
            b,
            font=ui(38 if is_narrow else 32),
            fill=DIM,
        )
    print(W, H, "terminal", TW, "x", TH, [width(l) for l in LINES])
    img.save(out)


def main():
    is_narrow = "--narrow" in sys.argv[2:]
    draw(narrow() if is_narrow else wide(), sys.argv[1], is_narrow)


if __name__ == "__main__":
    main()
