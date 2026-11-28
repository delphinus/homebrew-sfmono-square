"""README image: the 6 weights of SF Mono Square, upright and italic.

python weights.py OUT            # for a wide screen
python weights.py OUT --narrow   # for a phone, the italics below the uprights
"""

import subprocess, sys
from PIL import Image, ImageDraw, ImageFont

FONTS = (
    subprocess.check_output(["brew", "--prefix", "sfmono-square"], text=True).strip()
    + "/share/fonts"
)
OUT = sys.argv[1]
W = 1600
BG, LINE, CELLC = (13, 17, 23), (48, 54, 61), (30, 36, 44)
FG, DIM, GREEN = (230, 237, 243), (125, 133, 144), (63, 185, 80)
WEIGHTS = ["Light", "Regular", "Medium", "Semibold", "Bold", "Heavy"]
SAMPLE = "Ag 0O 1lI {} 漢字かな"
SIZE, ROW = 56, 80


def draw_narrow():
    W, M, SIZE, ROW = 1080, 36, 60, 84
    f = lambda w, s: ImageFont.truetype(f"{FONTS}/SFMonoSquare-{w}.otf", s)
    ui = lambda s: f("Regular", s)
    heads = [
        ("SF Mono Square", 76, FG, 36),
        ("six weights, each with its italic", 50, FG, 132),
        ("Light, Medium and Semibold kana and", 44, DIM, 212),
        ("kanji are made from Migu 1M Regular", 44, DIM, 266),
    ]
    top = 360
    section = 72 + ROW * len(WEIGHTS)
    H = top + 2 * section + 32 + 40 + 40
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for text, size, colour, y in heads:
        d.text((M, y), text, font=ui(size), fill=colour)
    left, right, bottom = M, W - M, H - 40
    d.rounded_rectangle((left, top, right, bottom), radius=12, outline=LINE, width=2)
    d.line((left + 12, top, right - 12, top), fill=GREEN, width=4)
    lx, ux = left + 28, left + 300
    y = top + 24
    for k, (label, suffix) in enumerate((("UPRIGHT", ""), ("ITALIC", "Italic"))):
        y += 32 * k
        d.text((lx, y), label, font=ui(40), fill=GREEN)
        y += 72
        for i, w in enumerate(WEIGHTS):
            if i:
                d.line((lx, y - 4, right - 28, y - 4), fill=CELLC, width=1)
            d.text((lx, y + (ROW - 44) // 2 - 6), w, font=ui(44), fill=DIM)
            d.text((ux, y + 6), SAMPLE, font=f(w + suffix, SIZE), fill=FG)
            y += ROW
    sw = sum(SIZE // 2 * (2 if ord(ch) > 0x2E7F else 1) for ch in SAMPLE)
    print(W, H, "sample right", ux + sw, "box right", right)
    return img


if "--narrow" in sys.argv[2:]:
    draw_narrow().save(OUT)
else:
    f = lambda w, s: ImageFont.truetype(f"{FONTS}/SFMonoSquare-{w}.otf", s)
    ui = lambda s: f("Regular", s)
    H = 176 + 70 + ROW * len(WEIGHTS) + 24 + 56
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    M = 56
    x = M
    for t, c in (("SF Mono Square ", FG), ("— six weights, each with its italic", FG)):
        d.text((x, 40), t, font=ui(52), fill=c)
        x += d.textlength(t, font=ui(52))
    d.text(
        (M, 112),
        "Light, Medium and Semibold kana and kanji are made from Migu 1M Regular",
        font=ui(28),
        fill=DIM,
    )

    left, top, right, bottom = M, 176, W - M, H - 56
    d.rounded_rectangle((left, top, right, bottom), radius=12, outline=LINE, width=2)
    d.line((left + 12, top, right - 12, top), fill=GREEN, width=4)
    cell = SIZE // 2
    sw = sum(cell * (2 if ord(ch) > 0x2E7F else 1) for ch in SAMPLE)
    lx, ux = left + 32, left + 200
    ix = ux + sw + 60
    d.text((ux, top + 24), "UPRIGHT", font=ui(26), fill=GREEN)
    d.text((ix, top + 24), "ITALIC", font=ui(26), fill=GREEN)
    y = top + 70
    for i, w in enumerate(WEIGHTS):
        if i:
            d.line((lx, y - 4, right - 32, y - 4), fill=CELLC, width=1)
        d.text((lx, y + (ROW - 32) // 2 - 6), w, font=ui(32), fill=DIM)
        for x0, name in ((ux, w), (ix, w + "Italic")):
            d.text((x0, y + 4), SAMPLE, font=f(name, SIZE), fill=FG)
        y += ROW
    print(W, H, "sample width", sw, "right edge", ix + sw, "box right", right)
    img.save(OUT)
