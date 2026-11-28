"""Slide 2, "Every model, every trim. Real MSRP.": one Jeep Wrangler on a display stage, changing through four trims while the
trim name and its MSRP change with it.

The four pictures in src/ are Jacob's (2026-11-28): our own catalog photos of each trim, re-set by an image tool on
the same dark green stage, all from the same angle. They are square, so the wall, ceiling and floor are extended
here to fill a wide screen or a phone. The lettering is drawn here, never by the image tool.

The trim names and prices are read from src/data/configs.json (manufacturer MSRP, without destination) every time
this runs. If a Wrangler MSRP changes in the catalog, run this again so the clip matches.

usage: python3 compose.py wide|phone out.mp4 [preview]        (run from scripts/trims-video)"""
import json, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

shape, out_path, preview = sys.argv[1], sys.argv[2], len(sys.argv) > 3
PHONE = shape == "phone"
W, H = (1080, 1890) if PHONE else (1920, 1080)
FPS = 24
INTER = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
INTER_B = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
NARROW = "../intro-video/BarlowCondensed-Black.woff"
MINT = np.array([196, 255, 236], np.float32)

# ---- the four trims, in price order, with the catalog's MSRP
YEAR = 2026
TRIMS = [("1-sport", "4-Door Sport"), ("2-sahara", "4-Door Sahara"), ("3-rubicon", "4-Door Rubicon"), ("4-moab-392", "4-Door Moab 392")]
configs = json.load(open("../../src/data/configs.json"))
def msrp(trim):
    found = [c["msrp"] for c in configs if c["key"] == "jeep-wrangler" and c["year"] == YEAR and c["trim"] == trim and c["msrp"]]
    assert len(found) == 1, f"expected one priced {YEAR} Wrangler {trim}, found {found}"
    return found[0]
PRICES = [msrp(t) for _, t in TRIMS]
print({t: p for (_, t), p in zip(TRIMS, PRICES)})

# ---- the stage: the square picture, with its edges carried outward and darkened to fill the screen
SIDE = 1080
X0, Y0 = (0, 420) if PHONE else (420, 0)
def stage(name):
    sq = np.asarray(Image.open(f"src/{name}.png").convert("RGB").resize((SIDE, SIDE), Image.LANCZOS)).astype(np.float32)
    canvas = np.zeros((H, W, 3), np.float32)
    canvas[Y0:Y0 + SIDE, X0:X0 + SIDE] = sq
    if PHONE:
        top, bottom = sq[:6].mean(axis=0), sq[-6:].mean(axis=0)
        fade = np.linspace(0.45, 1.0, Y0)[:, None, None]
        canvas[:Y0] = top[None] * fade
        n = H - Y0 - SIDE
        canvas[Y0 + SIDE:] = bottom[None] * np.linspace(1.0, 0.3, n)[:, None, None]
    else:
        left, right = sq[:, :6].mean(axis=1), sq[:, -6:].mean(axis=1)
        canvas[:, :X0] = left[:, None] * np.linspace(0.5, 1.0, X0)[None, :, None]
        n = W - X0 - SIDE
        canvas[:, X0 + SIDE:] = right[:, None] * np.linspace(1.0, 0.5, n)[None, :, None]
    return canvas
STAGES = [stage(n) for n, _ in TRIMS]

def ramp(t, a, b):
    return float(np.clip((t - a) / (b - a), 0, 1))
def ease(k):
    return k * k * (3 - 2 * k)

def spaced(d, xy, text, font, gap, fill=255, anchor_mid=True):
    width = sum(font.getlength(c) for c in text) + gap * (len(text) - 1)
    x = xy[0] - width / 2 if anchor_mid else xy[0]
    for ch in text:
        d.text((x, xy[1]), ch, font=font, fill=fill, anchor="ls")
        x += font.getlength(ch) + gap

def lit(layer, glow=18, strength=0.35):
    g = layer.filter(ImageFilter.GaussianBlur(glow))
    return np.clip(np.asarray(layer).astype(np.float32) / 255 * 0.92 + np.asarray(g).astype(np.float32) / 255 * strength, 0, 1)

# ---- the headline: on the ceiling above the light on a phone (tall narrow letters, as in the phone intro), on the
# wall between the light and the roof on a wide screen
def headline():
    im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(im)
    if PHONE:
        lines, tall = ["EVERY MODEL,", "EVERY TRIM."], 138
        size = 250
        while max(ImageFont.truetype(NARROW, size).getlength(l) for l in lines) > 900: size -= 2
        font = ImageFont.truetype(NARROW, size)
        cap = -font.getbbox("E", anchor="ls")[1]
        k = tall / cap
        for text, base in zip(lines, (318, 486)):
            line = Image.new("L", (W, cap + 80), 0)
            ImageDraw.Draw(line).text((W / 2, 40 + cap), text, font=font, fill=255, anchor="ms")
            line = line.resize((W, int(line.height * k)), Image.LANCZOS)
            im.paste(line, (0, int(base - (40 + cap) * k)), line)
    else:
        text, size = "EVERY MODEL, EVERY TRIM.", 188
        while ImageFont.truetype(INTER, size).getlength(text) > 1620: size -= 2
        d.text((W / 2, 380), text, font=ImageFont.truetype(INTER, size), fill=255, anchor="ms")
    return lit(im, 20, 0.35)
HEAD = headline()

# ---- the tag: trim name and MSRP. Under the light on a phone; on a wide screen, the name on the wall to the left
# of the car and the price to the right.
def tag(k):
    im_name, im_price = Image.new("L", (W, H), 0), Image.new("L", (W, H), 0)
    name, price = TRIMS[k][1].upper(), f"${PRICES[k]:,}"
    if PHONE:
        spaced(ImageDraw.Draw(im_name), (W / 2, 662), f"{YEAR} JEEP WRANGLER", ImageFont.truetype(INTER_B, 30), 10)
        spaced(ImageDraw.Draw(im_name), (W / 2, 716), name, ImageFont.truetype(INTER_B, 44), 9)
        pf, sf = ImageFont.truetype(INTER, 86), ImageFont.truetype(INTER_B, 34)
        total = pf.getlength(price) + 18 + sf.getlength("MSRP")
        x = (W - total) / 2
        ImageDraw.Draw(im_price).text((x, 806), price, font=pf, fill=255, anchor="ls")
        ImageDraw.Draw(im_name).text((x + pf.getlength(price) + 18, 806), "MSRP", font=sf, fill=255, anchor="ls")
    else:
        # the description stands on the wall left of the car and the price on the right, level with each other
        lx, rx = 285, 1635
        d = ImageDraw.Draw(im_name)
        spaced(d, (lx, 498), f"{YEAR} JEEP WRANGLER", ImageFont.truetype(INTER_B, 24), 7)
        spaced(d, (lx, 554), name, ImageFont.truetype(INTER, 36), 3)
        spaced(d, (rx, 590), "MSRP", ImageFont.truetype(INTER_B, 24), 9)
        ImageDraw.Draw(im_price).text((rx, 552), price, font=ImageFont.truetype(INTER, 88), fill=255, anchor="ms")
    return np.asarray(im_name).astype(np.float32) / 255 * 0.9, lit(im_price, 16, 0.3)
TAGS = [tag(k) for k in range(len(TRIMS))]

# ---- "REAL MSRP." laid flat on the floor in front of the car
def floor():
    font = ImageFont.truetype(INTER, 150)
    text = "REAL MSRP."
    FW = int(font.getlength(text)) + 80
    flat = Image.new("L", (FW, 220), 0)
    ImageDraw.Draw(flat).text((FW / 2, 110), text, font=font, fill=255, anchor="mm")
    if PHONE: quad = [(262, 1236), (818, 1236), (858, 1338), (222, 1338)]
    else: quad = [(600, 846), (1320, 846), (1372, 950), (548, 950)]
    src = [(0, 0), (FW, 0), (FW, 220), (0, 220)]
    A = []
    for (x, y), (u, v) in zip(quad, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    coef = np.linalg.solve(np.array(A, np.float64), np.array([c for p in src for c in p], np.float64))
    laid = flat.transform((W, H), Image.PERSPECTIVE, tuple(coef), Image.BICUBIC)
    return np.asarray(laid).astype(np.float32) / 255, np.asarray(laid.filter(ImageFilter.GaussianBlur(8))).astype(np.float32) / 255
FLOOR, FLOOR_GLOW = floor()

# ---- timing: each trim holds, then melts into the next. The last one holds longest.
HOLD, MELT = 1.25, 0.4
CHANGES = [HOLD + k * (HOLD + MELT) for k in range(len(TRIMS) - 1)]      # when each change starts
LENGTH = CHANGES[-1] + MELT + 1.6
N = int(round(LENGTH * FPS))

def compose(i):
    t = i / FPS
    pos = sum(ease(ramp(t, c, c + MELT)) for c in CHANGES)                # 0..3, which trim is showing
    lo = min(int(pos), len(TRIMS) - 2)
    frac = pos - lo
    f = STAGES[lo] * (1 - frac) + STAGES[lo + 1] * frac
    a = (HEAD * ramp(t, 0.0, 0.4))[..., None]
    f = f + (MINT - f * MINT / 255.0) * a
    for k, (name_a, price_a) in enumerate(TAGS):                          # the tag swaps at the middle of each change
        w = 1.0
        if k > 0: w *= ramp(pos, k - 0.45, k - 0.1)
        if k < len(TAGS) - 1: w *= 1 - ramp(pos, k + 0.2, k + 0.55)
        if k == 0: w *= ramp(t, 0.25, 0.6)
        if w <= 0: continue
        f = f + (255 - f) * (name_a * w)[..., None]
        pa = (price_a * w)[..., None]
        f = f + (MINT - f * MINT / 255.0) * pa
    k = ramp(t, 0.5, 1.2)
    if k > 0:
        wipe = np.clip((k * 1.25 * W - np.arange(W)) / 130.0, 0, 1)[None, :]
        fa = (FLOOR * 0.95 * wipe)[..., None]
        ga = (FLOOR_GLOW * 0.25 * wipe)[..., None]
        f = f + (255 - f) * ga * 0.6
        f = f * (1 - fa) + (255 * 0.78 + f * 0.35) * fa
    return np.clip(f, 0, 255).astype(np.uint8)

if preview:
    picks = [int((c - 0.2) * FPS) for c in CHANGES] + [N - 1]
    tiles = [Image.fromarray(compose(i)) for i in picks]
    tw = 432 if PHONE else 960
    th = tw * H // W
    cols = 4 if PHONE else 2
    sheet = Image.new("RGB", (tw * cols, th * ((len(tiles) + cols - 1) // cols)))
    for n, tl in enumerate(tiles):
        sheet.paste(tl.resize((tw, th)), ((n % cols) * tw, (n // cols) * th))
    sheet.save(out_path, quality=90)
else:
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-crf", "22", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out_path], stdin=subprocess.PIPE)
    last = None
    for i in range(N):
        last = compose(i)
        ff.stdin.write(last.tobytes())
    ff.stdin.close(); ff.wait()
    Image.fromarray(last).save(out_path.replace(".mp4", "-end.jpg"), quality=88)
    Image.fromarray(compose(int(0.9 * FPS))).save(out_path.replace(".mp4", "-start.jpg"), quality=85)
    print("wrote", out_path, f"{LENGTH:.1f}s")
