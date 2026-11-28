"""README image: glyphs of SF Mono Square coloured by the font they come from."""

import subprocess, sys
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

FONTS = (
    subprocess.check_output(["brew", "--prefix", "sfmono-square"], text=True).strip()
    + "/share/fonts"
)
SQUARE = f"{FONTS}/SFMonoSquare-Regular.otf"
EXT = {"P1": f"{FONTS}/SFMonoSquareExt-P1.ttf", "P2": f"{FONTS}/SFMonoSquareExt-P2.ttf"}
# The fonts SF Mono Square is built from, which the formula installs too, tell where a glyph comes from.
SFMONO, MIGU = f"{FONTS}/src/SF-Mono-Regular.otf", f"{FONTS}/src/migu-1m-regular.ttf"
OUT = sys.argv[1]

W = 1600
BG, LINE, CELLC = (13, 17, 23), (48, 54, 61), (30, 36, 44)
FG, DIM, GREEN = (230, 237, 243), (125, 133, 144), (63, 185, 80)
SOURCES = [
    ("SF Mono", (88, 166, 255), "Latin letters, digits and symbols"),
    ("Migu 1M", FG, "kana and the kanji of JIS X 0213"),
    (
        "Source Han Sans",
        (240, 136, 62),
        "18,243 other kanji, radicals and strokes in the BMP",
    ),
    (
        "Plangothic",
        (188, 140, 255),
        "74,991 of Extension B to J, in SF Mono Square Ext P1/P2",
    ),
]
ROWS = [
    'let s = "漢字とかな"; // SF Mono + Migu 1M',
    "四角号碼 1010 一 丄 丅 㐀 㒵 䶵 龘 鿐 鿕 鿖",
    "Ext B-J: 𠀀 𠂉 𡚸 𪜀 𫝀 𫠠 𬺰 𮯰 𰀀 𱍐 𲎰 𳀀",
]
SIZE = 64
CELL, LH, GAP = SIZE // 2, SIZE, 36  # a cell is half an em wide and an em high

cmap = lambda p: set(TTFont(p, lazy=True).getBestCmap())
sfmono, migu, square = cmap(SFMONO), cmap(MIGU), cmap(SQUARE)
ext = {k: cmap(v) for k, v in EXT.items()}


def source(c):
    return 3 if c >= 0x20000 else 0 if c in sfmono else 1 if c in migu else 2


ui = lambda s: ImageFont.truetype(SQUARE, s)
M, top = 56, 176
lt = top + 44 + len(ROWS) * (LH + GAP) + 20
H = lt + len(SOURCES) * 58 + 28 + 56
img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
d.text((M, 40), "SF Mono Square — kanji beyond JIS X 0213", font=ui(52), fill=FG)
d.text(
    (M, 112),
    "Each glyph is coloured by the font it comes from · all share one size and baseline",
    font=ui(28),
    fill=DIM,
)
left, right, bottom = M, W - M, H - 56
d.rounded_rectangle((left, top, right, bottom), radius=12, outline=LINE, width=2)
d.line((left + 12, top, right - 12, top), fill=GREEN, width=4)

fonts = {
    "sq": ImageFont.truetype(SQUARE, SIZE),
    **{k: ImageFont.truetype(v, SIZE) for k, v in EXT.items()},
}
x0, y = left + 40, top + 40
for row in ROWS:
    x = x0
    for ch in row:
        c = ord(ch)
        w = CELL * (2 if c > 0x2E7F else 1)
        if ch != " ":
            d.rectangle((x, y, x + w - 1, y + LH - 1), outline=CELLC)
            f = (
                fonts["sq"]
                if c < 0x20000
                else fonts["P1"] if c in ext["P1"] and c < 0x30000 else fonts["P2"]
            )
            assert c in square or any(c in e for e in ext.values()), hex(c)
            d.text(
                (x, y + round(SIZE * 1638 / 2048)),
                ch,
                font=f,
                fill=SOURCES[source(c)][1],
                anchor="ls",
            )
        x += w
    print("row right", x, "box right", right)
    y += LH + GAP

y = lt
for name, color, desc in SOURCES:
    d.rectangle((x0, y + 6, x0 + 26, y + 32), fill=color)
    d.text((x0 + 44, y), name, font=ui(32), fill=color)
    d.text((x0 + 44 + 300, y + 2), desc, font=ui(28), fill=DIM)
    print("legend right", x0 + 344 + d.textlength(desc, font=ui(28)))
    y += 58
img.save(OUT)
