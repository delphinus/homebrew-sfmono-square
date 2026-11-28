"""README hero: a terminal drawn with SF Mono Square, with the cell grid shown over a table."""

import subprocess, sys
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

FONTS = (
    subprocess.check_output(["brew", "--prefix", "sfmono-square"], text=True).strip()
    + "/share/fonts"
)
OUT = sys.argv[1]
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
RED, YELLOW, CYAN, PINK = (
    (255, 123, 114),
    (227, 179, 65),
    (57, 197, 207),
    (247, 120, 186),
)
BAR, BAR2, DARK = (48, 54, 61), (33, 38, 45), (13, 17, 23)

W = 1600
SIZE = 40
CW, CH = SIZE // 2, SIZE
COLS = 66


def cells(ch):
    c = ord(ch)
    if c >= 0x20000:
        return 2
    return HMTX[CMAP[c]][0] // 1024 if c in CMAP else 1


def L(*segs):
    return [s if len(s) == 4 else (s + (None, "R"))[:4] for s in segs]


T = "│"


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


TREE = [
    L(("    ", FG), ("\uf07b", BLUE), (" ~/src/demo", BLUE, None, "B")),
    L(("    ", FG), ("├── ", DIM), ("\uf07b", BLUE), (" lua/", BLUE)),
    L(("    ", FG), ("│   └── ", DIM), ("\ue620", BLUE), (" 設定.lua", FG)),
    L(("    ", FG), ("├── ", DIM), ("\uf48a", CYAN), (" README.md", FG)),
    L(("    ", FG), ("├── ", DIM), ("\uf15c", FG), (" 日本語のメモ.txt", FG)),
    L(("    ", FG), ("├── ", DIM), ("\uf1d3", ORANGE), (" .gitignore", FG)),
    L(("    ", FG), ("└── ", DIM), ("\uf308", BLUE), (" Dockerfile", FG)),
]
TABLE = [
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
LINES = (
    [
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
    + [TABLE[i] + (TREE[i - 1] if 1 <= i <= 7 else []) for i in range(8)]
    + [
        L(),
        L(
            (" NORMAL ", DARK, BLUE, "B"),
            ("\ue0b0", BLUE, BAR, "R"),
            (" \ue0a0 main ", FG, BAR, "R"),
            ("\ue0b0", BAR, BAR2, "R"),
            (" \ue620 設定.lua ", FG, BAR2, "R"),
            ("\ue0b0", BAR2, WIN, "R"),
            ("FILL", FG, WIN, "R"),
            ("\ue0b2", BAR2, WIN, "R"),
            (" utf-8 ", FG, BAR2, "R"),
            ("\ue0b2", BAR, BAR2, "R"),
            (" lua ", FG, BAR, "R"),
            ("\ue0b2", BLUE, BAR, "R"),
            (" 6:9 ", DARK, BLUE, "B"),
        ),
    ]
)
GRID_ROWS = (7, 15)  # the rows of the table
GRID_COLS = (0, 38)

FONTCACHE = {}


def font_for(ch, st):
    c = ord(ch)
    key = st
    if c >= 0x20000:
        key = "P1" if c in EXT["P1"] and c < 0x30000 else "P2"
        path = f"{FONTS}/SFMonoSquareExt-{key}.ttf"
    else:
        name = {
            "R": "Regular",
            "B": "Bold",
            "I": "RegularItalic",
            "BI": "BoldItalic",
        }.get(st, st)
        path = fp(name)
    if key not in FONTCACHE:
        FONTCACHE[key] = ImageFont.truetype(path, SIZE)
    return FONTCACHE[key]


def width(line):
    return sum(cells(ch) for t, *_ in line if t != "FILL" for ch in t)


ui = lambda s, st="Regular": ImageFont.truetype(fp(st), s)
TW, TH = COLS * CW, len(LINES) * CH
PAD, BARH = 28, 50
wx0 = (W - TW - 2 * PAD) // 2
wy0 = 232
wx1, wy1 = wx0 + TW + 2 * PAD, wy0 + BARH + TH + 2 * PAD
H = wy1 + 200
img = Image.new("RGB", (W, H), PAGE)
d = ImageDraw.Draw(img)
M = wx0
d.text((M, 44), "SF Mono Square", font=ui(80, "Semibold"), fill=FG)
d.text(
    (M + d.textlength("SF Mono Square  ", font=ui(80, "Semibold")), 72),
    "SF Mono + Migu 1M + Nerd Fonts",
    font=ui(40),
    fill=DIM,
)
d.text(
    (M, 152),
    "A Japanese letter takes exactly two cells, so every column lines up.",
    font=ui(34),
    fill=FG,
)

d.rounded_rectangle((wx0, wy0, wx1, wy1), radius=16, fill=WIN, outline=EDGE, width=2)
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
(r0, r1), (c0, c1) = GRID_ROWS, GRID_COLS
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

feats = [
    ("6 weights", "with italics", BLUE),
    ("Kanji", "up to Extension J", ORANGE),
    ("Nerd Fonts", "v3 codepoints", PURPLE),
    ("1 : 2", "half to full width", GREEN),
]
fy = wy1 + 48
fw = (wx1 - wx0) // len(feats)
for i, (a, b, c) in enumerate(feats):
    x = wx0 + i * fw
    d.text((x, fy), a, font=ui(48, "Semibold"), fill=c)
    d.text((x, fy + 64), b, font=ui(32), fill=DIM)
print(W, H, "terminal", TW, "x", TH, [width(l) for l in LINES])
img.save(OUT)
