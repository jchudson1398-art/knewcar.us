"""The phone version of compose.py: the same lettering, built into Jacob's tall (768x1344) clip of the same scene.

"LOOKING FOR A NEW" and CAR? TRUCK? SUV? build into one line on the back wall behind the cars, then "ALL YOUR
OPTIONS. ONE EASY PLACE." is laid on the floor in front of them (two lines here, so it stays readable on a phone).
The clip is enlarged to 1080 wide and kept whole at 1080x1890 (an earlier version cropped it): the empty black above the set and some bare floor below
it are trimmed so the scene fills a phone screen without pushing the rest of the page too far down.

usage: python3 compose_phone.py out.mp4 [preview]      (frames of the source clip must be in fr_phone/)"""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage

SW, SH = 768, 1344                 # source size
SCALE = 1080 / SW
W, FULL_H = 1080, round(SH * SCALE)  # enlarged size before cropping
Y0, H = 0, FULL_H                  # no crop: the whole clip, so it can fill a phone screen
FPS, N = 24, 121
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_B = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
out_path, preview = sys.argv[1], len(sys.argv) > 2

def frame(i):
    im = Image.open(f"fr_phone/{i:03d}.png").convert("RGB").resize((W, FULL_H), Image.LANCZOS).crop((0, Y0, W, Y0 + H))
    return np.asarray(im).astype(np.float32)

plate = np.asarray(Image.open("fr_phone/001.png").convert("RGB")).astype(np.int16)

def car_matte(i):
    """1 where a car is, 0 where the empty set shows. The camera never moves, so the first frame is the empty set."""
    f = np.asarray(Image.open(f"fr_phone/{i:03d}.png").convert("RGB")).astype(np.int16)
    d = np.abs(f - plate).max(axis=2)
    m = d > 11  # low, because the black sedan is close in colour to the dark wall
    m = ndimage.binary_opening(m, iterations=1)
    m = ndimage.binary_closing(m, iterations=5)
    m = ndimage.binary_fill_holes(m)
    m = ndimage.binary_opening(m, iterations=2)
    lab, n = ndimage.label(m)
    if n:
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        m = np.isin(lab, [k + 1 for k, s in enumerate(sizes) if s > 3000])
    big = Image.fromarray((m * 255).astype(np.uint8)).resize((W, FULL_H), Image.BILINEAR).crop((0, Y0, W, Y0 + H)).filter(ImageFilter.GaussianBlur(1.8))
    return np.asarray(big).astype(np.float32) / 255.0

def ramp(t, a, b):
    return float(np.clip((t - a) / (b - a), 0, 1))

def ease(k):
    return k * k * (3 - 2 * k)

# ---- back wall. In the enlarged picture the lit frame's top edge is at y=634, the car roofs at about y=837 and the
# floor line at about y=990.
WALL_TOP = 658
small = ImageFont.truetype(FONT_B, 34)
WORDS = ["CAR?", "TRUCK?", "SUV?"]
WALL_RGB = np.array([196, 255, 236], np.float32)

def fit(words, size, max_w):
    while True:
        f = ImageFont.truetype(FONT, size)
        gap = size * 0.26
        widths = [f.getlength(w) for w in words]
        total = sum(widths) + gap * (len(words) - 1)
        if total <= max_w or size <= 40: break
        size -= 2
    x, xs = (W - total) / 2, []
    for w in widths:
        xs.append(x); x += w + gap
    return size, xs
# (font size, left x of each word, baseline y): the line shrinks and rises as each one pulls in
STEPS = [fit(WORDS[:1], 230, 800) + (892,), fit(WORDS[:2], 200, 930) + (856,), fit(WORDS[:3], 200, 970) + (824,)]
STEP_AT = [(1.2, 1.75), (2.9, 3.45)]  # when the truck and the SUV roll in on this clip

def wall(t):
    pos = ease(ramp(t, *STEP_AT[0])) + ease(ramp(t, *STEP_AT[1]))
    lo, frac = min(int(pos), 1), pos - min(int(pos), 1)
    (s0, x0, y0), (s1, x1, y1) = STEPS[lo], STEPS[lo + 1]
    size, base = s0 + (s1 - s0) * frac, y0 + (y1 - y0) * frac
    font = ImageFont.truetype(FONT, max(10, int(round(size))))
    im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(im)
    label = "LOOKING FOR A NEW"
    x = (W - (small.getlength(label) + 10 * (len(label) - 1))) / 2
    lab = int(255 * ramp(t, 0.0, 0.35))
    for ch in label:
        d.text((x, WALL_TOP), ch, font=small, fill=lab)
        x += small.getlength(ch) + 10
    for n, word in enumerate(WORDS[: lo + 2]):
        if n < len(x0):
            wx, alpha = x0[n] + (x1[n] - x0[n]) * frac, 1.0
        else:
            wx, alpha = x1[n] + (1 - frac) * 40, ramp(frac, 0.6, 1.0)
        if n == 0: alpha *= ramp(t, 0.05, 0.45)
        if alpha > 0: d.text((wx, base), word, font=font, fill=int(255 * alpha), anchor="ls")
    glow = im.filter(ImageFilter.GaussianBlur(18))
    a = np.asarray(im).astype(np.float32) / 255 * 0.78 + np.asarray(glow).astype(np.float32) / 255 * 0.42
    fade = np.clip((990 - np.arange(H)) / 170.0, 0, 1)[:, None]  # sinks into the haze near the floor
    return np.clip(a, 0, 1) * (0.35 + 0.65 * fade)

# ---- floor: the tagline in two lines, laid flat in front of the cars
def floor():
    font = ImageFont.truetype(FONT, 150)
    lines = ["ALL YOUR OPTIONS.", "ONE EASY PLACE."]
    FW = int(max(font.getlength(l) for l in lines)) + 80
    flat = Image.new("L", (FW, 400), 0)
    d = ImageDraw.Draw(flat)
    d.text((FW / 2, 105), lines[0], font=font, fill=255, anchor="mm")
    d.text((FW / 2, 295), lines[1], font=font, fill=255, anchor="mm")
    top_y, bot_y = 1150, 1372  # kept clear of the button and dots that sit over the bottom of the clip
    quad = [(150, top_y), (W - 150, top_y), (W - 60, bot_y), (60, bot_y)]
    src = [(0, 0), (FW, 0), (FW, 400), (0, 400)]
    A = []
    for (x, y), (u, v) in zip(quad, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    coef = np.linalg.solve(np.array(A, np.float64), np.array([c for p in src for c in p], np.float64))
    laid = flat.transform((W, H), Image.PERSPECTIVE, tuple(coef), Image.BICUBIC)
    return np.asarray(laid).astype(np.float32) / 255, np.asarray(laid.filter(ImageFilter.GaussianBlur(8))).astype(np.float32) / 255
FLOOR, FLOOR_GLOW = floor()

def compose(i):
    t = (i - 1) / FPS
    f = frame(i)
    keep = 1 - car_matte(i)
    a = (wall(t) * keep)[..., None]
    f = f + (WALL_RGB - f * WALL_RGB / 255.0) * a
    k = ramp(t, 3.7, 4.6)
    if k > 0:
        wipe = np.clip((k * 1.25 * W - np.arange(W)) / 130.0, 0, 1)[None, :]
        fa = (FLOOR * 0.95 * wipe)[..., None]
        ga = (FLOOR_GLOW * 0.25 * wipe)[..., None]
        f = f + (255 - f) * ga * 0.6
        f = f * (1 - fa) + (255 * 0.78 + f * 0.35) * fa
    return np.clip(f, 0, 255).astype(np.uint8)

if preview:
    tiles = [Image.fromarray(compose(i)).resize((540, 600)) for i in (10, 26, 40, 60, 80, 96, 108, 121)]
    sheet = Image.new("RGB", (2160, 1040))
    for n, tl in enumerate(tiles):
        sheet.paste(tl, ((n % 4) * 540, (n // 4) * 520))
    sheet.save(out_path, quality=88)
else:
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-crf", "22", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out_path], stdin=subprocess.PIPE)
    last = None
    for i in range(1, N + 1):
        last = compose(i)
        ff.stdin.write(last.tobytes())
    ff.stdin.close(); ff.wait()
    Image.fromarray(last).save(out_path.replace(".mp4", "-end.jpg"), quality=88)
    Image.fromarray(compose(1)).save(out_path.replace(".mp4", "-start.jpg"), quality=85)
    print("wrote", out_path)
