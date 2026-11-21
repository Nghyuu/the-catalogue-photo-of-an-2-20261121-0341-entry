#!/usr/bin/env python3
"""Build-time generator for entry.png.

The Catalogue Photo of an Impossible Gadget: the CHRONO-TOAST T-3000,
a chrome studio toaster that toasts TIME. Its two slices of toast pop up
as clock faces (10:08 and 4:40), and exactly one accessory sharpens the
joke: a small red twin-bell alarm clock standing beside it.

Drawn with PIL only, at 1024x1024, as a clean catalogue studio shot:
seamless warm-grey backdrop, soft contact shadows, chrome sheen,
believable materials. Run: python3 draw.py  ->  entry.png
"""
import math
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = H = 1024
OUT = "entry.png"

# ---------------------------------------------------------------- fonts
def font(size, bold=False):
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()

# ---------------------------------------------------------------- helpers
def vgrad(size, top, bottom):
    """Vertical RGB gradient."""
    w, h = size
    strip = Image.new("RGB", (1, 256))
    px = strip.load()
    for y in range(256):
        t = y / 255.0
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return strip.resize((w, h))

def hgrad(size, stops):
    """Horizontal gradient through a list of (pos, color) stops."""
    w, h = size
    strip = Image.new("RGB", (w, 1))
    px = strip.load()
    for x in range(w):
        t = x / max(w - 1, 1)
        for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
            if p0 <= t <= p1:
                f = (t - p0) / max(p1 - p0, 1e-9)
                px[x, 0] = tuple(int(c0[i] + (c1[i] - c0[i]) * f) for i in range(3))
                break
        else:
            px[x, 0] = stops[-1][1]
    return strip.resize((w, h))

def soft_shadow(canvas, box, blur, alpha):
    """Blurred black ellipse on its own layer, composited under the product."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse(box, fill=(0, 0, 0, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    canvas.alpha_composite(layer)

def clock_face(d, cx, cy, r, hour, minute, numerals=True):
    """A clock dial: white face, ticks, numerals, hands, red second hand."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 255),
              outline=(40, 40, 40, 255), width=3)
    for m in range(60):
        a = math.radians(m * 6 - 90)
        long_tick = m % 5 == 0
        r1 = r - (10 if long_tick else 5)
        d.line([cx + r1 * math.cos(a), cy + r1 * math.sin(a),
                cx + (r - 3) * math.cos(a), cy + (r - 3) * math.sin(a)],
               fill=(30, 30, 30, 255), width=3 if long_tick else 1)
    if numerals:
        f = font(max(10, r // 3), bold=True)
        for num, ang in ((12, -90), (3, 0), (6, 90), (9, 180)):
            a = math.radians(ang)
            tx = cx + (r - 17) * math.cos(a)
            ty = cy + (r - 17) * math.sin(a)
            tw = d.textlength(str(num), font=f)
            d.text((tx - tw / 2, ty - f.size / 2), str(num),
                   font=f, fill=(25, 25, 25, 255))
    ha = math.radians(((hour % 12) + minute / 60.0) * 30 - 90)
    ma = math.radians(minute * 6 - 90)
    d.line([cx, cy, cx + r * 0.52 * math.cos(ha), cy + r * 0.52 * math.sin(ha)],
           fill=(20, 20, 20, 255), width=6)
    d.line([cx, cy, cx + r * 0.78 * math.cos(ma), cy + r * 0.78 * math.sin(ma)],
           fill=(20, 20, 20, 255), width=4)
    sa = math.radians(32 * 6 - 90)
    d.line([cx, cy, cx + r * 0.85 * math.cos(sa), cy + r * 0.85 * math.sin(sa)],
           fill=(200, 40, 30, 255), width=2)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(25, 25, 25, 255))

def toast_slice(cx, top_y, height, width, tilt, hour, minute):
    """One slice of toast whose face is a clock. Returns an RGBA layer."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, x1 = cx - width // 2, cx + width // 2
    y0, y1 = top_y, top_y + height
    # soft shadow of the slice on the toaster top
    d.rounded_rectangle([x0 - 6, y1 - 14, x1 + 6, y1 + 10], radius=12,
                        fill=(0, 0, 0, 60))
    # crust: golden-brown rounded-top slice
    d.rounded_rectangle([x0, y0, x1, y1], radius=52, fill=(176, 118, 52, 255))
    d.rounded_rectangle([x0 + 7, y0 + 7, x1 - 7, y1 - 7], radius=46,
                        fill=(247, 226, 182, 255))
    # light toast browning at the edges
    d.rounded_rectangle([x0 + 7, y0 + 7, x1 - 7, y1 - 7], radius=46,
                        outline=(214, 164, 96, 255), width=4)
    # clock face on the bread (bigger, so the joke reads at a glance)
    clock_face(d, cx, y0 + 100, 52, hour, minute)
    return layer.rotate(tilt, resample=Image.BICUBIC, center=(cx, (y0 + y1) // 2))

# ---------------------------------------------------------------- scene
img = Image.new("RGB", (W, H))
img.paste(vgrad((W, H), (250, 248, 244), (224, 219, 211)), (0, 0))
canvas = img.convert("RGBA")

# soft studio glow behind the product
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([180, 120, 850, 900], fill=(255, 255, 255, 110))
canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(90)))

# floor: faint seamless-backdrop sweep below y=820
floor = Image.new("RGBA", (W, H), (0, 0, 0, 0))
fd = ImageDraw.Draw(floor)
fd.rectangle([0, 820, W, H], fill=(210, 204, 195, 70))
canvas.alpha_composite(floor)

# contact shadows
soft_shadow(canvas, [300, 822, 760, 862], 14, 95)
soft_shadow(canvas, [748, 830, 912, 856], 10, 80)

# ------------------------------------------------------------ alarm clock
# (the ONE accessory: a small red twin-bell alarm clock)
acc = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ad = ImageDraw.Draw(acc)
acx, acy, ar = 830, 742, 76
# bells
ad.ellipse([acx - 62, acy - ar - 26, acx - 18, acy - ar + 16], fill=(198, 44, 34, 255))
ad.ellipse([acx + 18, acy - ar - 26, acx + 62, acy - ar + 16], fill=(198, 44, 34, 255))
ad.ellipse([acx - 58, acy - ar - 22, acx - 30, acy - ar + 2], fill=(232, 96, 80, 255))
ad.ellipse([acx + 30, acy - ar - 22, acx + 58, acy - ar + 2], fill=(232, 96, 80, 255))
# hammer + handle
ad.line([acx - 8, acy - ar - 18, acx + 8, acy - ar - 18], fill=(120, 120, 120, 255), width=5)
ad.arc([acx - 22, acy - ar - 34, acx + 22, acy - ar - 6], 200, 340,
       fill=(150, 150, 150, 255), width=5)
# legs
ad.line([acx - 42, acy + ar - 8, acx - 56, acy + ar + 26], fill=(90, 90, 90, 255), width=7)
ad.line([acx + 42, acy + ar - 8, acx + 56, acy + ar + 26], fill=(90, 90, 90, 255), width=7)
# red case with glossy highlight
ad.ellipse([acx - ar, acy - ar, acx + ar, acy + ar], fill=(198, 44, 34, 255))
ad.ellipse([acx - ar, acy - ar, acx + ar, acy + ar], outline=(120, 20, 14, 255), width=3)
ad.arc([acx - ar + 12, acy - ar + 10, acx + ar - 34, acy + ar - 40], 200, 300,
       fill=(255, 150, 135, 255), width=10)
# white face + dial
ad.ellipse([acx - 60, acy - 60, acx + 60, acy + 60], fill=(255, 255, 255, 255),
           outline=(60, 60, 60, 255), width=2)
clock_face(ad, acx, acy, 60, 7, 0)
canvas.alpha_composite(acc)

# ------------------------------------------------------------ toast slices
canvas.alpha_composite(toast_slice(415, 318, 230, 128, -6, 10, 8))
canvas.alpha_composite(toast_slice(612, 296, 240, 128, 5, 4, 40))

# ------------------------------------------------------------ toaster body
body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bd = ImageDraw.Draw(body)
bx0, bx1, by0, by1 = 300, 724, 520, 820
# chrome: horizontal sheen gradient clipped to the rounded body
chrome = hgrad((bx1 - bx0, by1 - by0), [
    (0.00, (148, 152, 158)), (0.12, (196, 200, 206)), (0.30, (238, 240, 242)),
    (0.46, (168, 173, 180)), (0.58, (226, 229, 233)), (0.74, (188, 192, 198)),
    (0.88, (240, 242, 244)), (1.00, (150, 154, 160)),
])
mask = Image.new("L", (W, H), 0)
md = ImageDraw.Draw(mask)
md.rounded_rectangle([bx0, by0, bx1, by1], radius=36, fill=255)
chrome_full = Image.new("RGBA", (W, H), (0, 0, 0, 0))
chrome_full.paste(chrome, (bx0, by0))
body.alpha_composite(Image.composite(chrome_full, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))
bd = ImageDraw.Draw(body)
bd.rounded_rectangle([bx0, by0, bx1, by1], radius=36, outline=(105, 110, 116, 255), width=3)
# brushed-metal vertical shading at the edges
bd.rounded_rectangle([bx0 + 4, by0 + 6, bx0 + 26, by1 - 6], radius=10, fill=(255, 255, 255, 60))
bd.rounded_rectangle([bx1 - 26, by0 + 6, bx1 - 4, by1 - 6], radius=10, fill=(60, 64, 70, 60))
# top plate
bd.rounded_rectangle([bx0, by0 - 16, bx1, by0 + 26], radius=18, fill=(96, 100, 106, 255))
bd.rounded_rectangle([bx0, by0 - 16, bx1, by0 + 26], radius=18, outline=(70, 74, 80, 255), width=2)
# slots (dark openings the toast rises from)
for sx0, sx1 in ((352, 478), (548, 674)):
    bd.rounded_rectangle([sx0, by0 - 8, sx1, by0 + 18], radius=10, fill=(28, 28, 30, 255))
# brand text on the front (text belongs to the product)
f_brand = font(30, bold=True)
label = "CHRONO-TOAST"
tw = bd.textlength(label, font=f_brand)
bd.text(((bx0 + bx1) / 2 - tw / 2, 648), label, font=f_brand, fill=(52, 56, 62, 255))
f_sub = font(17)
sub = "T I M E   T O A S T E R"
tw = bd.textlength(sub, font=f_sub)
bd.text(((bx0 + bx1) / 2 - tw / 2, 690), sub, font=f_sub, fill=(92, 96, 102, 255))
# browning dial on the front
dx, dy, dr = 640, 762, 24
bd.ellipse([dx - dr, dy - dr, dx + dr, dy + dr], fill=(228, 230, 232, 255),
           outline=(90, 94, 100, 255), width=2)
for i in range(7):
    a = math.radians(150 + i * 40)
    bd.line([dx + (dr - 8) * math.cos(a), dy + (dr - 8) * math.sin(a),
             dx + (dr - 2) * math.cos(a), dy + (dr - 2) * math.sin(a)],
            fill=(70, 74, 80, 255), width=2)
pa = math.radians(150 + 4 * 40)
bd.line([dx, dy, dx + (dr - 6) * math.cos(pa), dy + (dr - 6) * math.sin(pa)],
        fill=(198, 44, 34, 255), width=3)
bd.ellipse([dx - 4, dy - 4, dx + 4, dy + 4], fill=(60, 64, 70, 255))
f_tiny = font(13)
bd.text((392, 752), "BROWN", font=f_tiny, fill=(96, 100, 106, 255))
bd.text((392, 770), "T-3000", font=f_tiny, fill=(96, 100, 106, 255))
# side lever
bd.rounded_rectangle([bx1 - 2, 636, bx1 + 30, 656], radius=8, fill=(120, 124, 130, 255))
bd.ellipse([bx1 + 14, 628, bx1 + 38, 664], fill=(228, 230, 232, 255),
           outline=(90, 94, 100, 255), width=2)
# feet
bd.rounded_rectangle([bx0 + 30, by1 - 2, bx0 + 70, by1 + 12], radius=5, fill=(50, 52, 56, 255))
bd.rounded_rectangle([bx1 - 70, by1 - 2, bx1 - 30, by1 + 12], radius=5, fill=(50, 52, 56, 255))
canvas.alpha_composite(body)

# a few crumbs on the counter, for scale and realism
cd = ImageDraw.Draw(canvas)
for (cx, cy, r) in ((286, 848, 3), (742, 852, 4), (700, 856, 2), (330, 856, 2)):
    cd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(176, 118, 52, 255))

canvas.convert("RGB").save(OUT, optimize=True)
print("wrote", OUT)
