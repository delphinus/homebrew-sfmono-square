"""compose.py IN OUT: cut the blank rows at the bottom of a window shot taken without shadow, round its corners and give it a shadow."""

import sys
from collections import Counter
from PIL import Image, ImageDraw, ImageFilter

src, out = sys.argv[1:3]
R, SS = 26, 4  # the corner radius of the window, and the supersampling of the mask
ML, MR, MT, MB = 112, 112, 77, 147  # the margins macOS gave the shadow
raw = Image.open(src).convert("RGBA")
W, H = raw.size
BG = Counter(p for p in raw.get_flattened_data() if p[3] == 255).most_common(1)[0][0][
    :3
]
win = Image.new("RGB", (W, H), BG)
win.paste(raw, (0, 0), raw.getchannel("A").point(lambda a: 255 if a == 255 else 0))
px = win.load()


def busy(y):
    return sum(px[x, y] != BG for x in range(70, W - 70)) > 2


first = next(y for y in range(H) if busy(y))
last = next(y for y in range(H - 1, -1, -1) if busy(y))
cut = (H - 1 - last) - first
if cut > 0:
    for y in range(last + 1, last + 1 + cut):
        assert all(px[x, y] == BG for x in range(W)), (src, y)
    t = Image.new("RGB", (W, H - cut))
    t.paste(win.crop((0, 0, W, last + 1)), (0, 0))
    t.paste(win.crop((0, last + 1 + cut, W, H)), (0, last + 1))
    win, H = t, H - cut
mask = Image.new("L", (W * SS, H * SS), 0)
ImageDraw.Draw(mask).rounded_rectangle(
    (0, 0, W * SS - 1, H * SS - 1), radius=R * SS, fill=255
)
mask = mask.resize((W, H), Image.LANCZOS)
cw, ch = W + ML + MR, H + MT + MB
canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
# a wide soft shadow below the window, and a tight one all round it
for blur, dy, alpha in ((38, 26, 0.50), (1.5, 0, 0.45)):
    sh = Image.new("L", (cw, ch), 0)
    sh.paste(mask, (ML, MT + dy))
    sh = sh.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * alpha))
    canvas = Image.alpha_composite(
        canvas, Image.merge("RGBA", (*(Image.new("L", (cw, ch), 0),) * 3, sh))
    )
w = win.convert("RGBA")
w.putalpha(mask)
canvas.alpha_composite(w, (ML, MT))
canvas.save(out)
print(f"{src}: cut {max(cut, 0)}px, gap {first}px, {canvas.size}")
