"""The phone version of the intro: Jacob's tall (768x1344) clip of the same scene, used whole so it fills a phone.

Design (2026-11-28): the clip has empty black above the set. That space becomes a dark warehouse ceiling, and the
headline fills it: "LOOKING FOR A NEW" with CAR? TRUCK? SUV? building into one line of tall letters standing on the
top of the lit frame. The KnewCar wordmark is on the back wall, behind the cars. "ALL YOUR OPTIONS. ONE EASY PLACE."
is laid on the floor in front of the cars, in two lines.

usage: python3 compose_phone.py out.mp4 [preview]      (frames of the source clip must be in fr_phone/)"""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage

SW, SH = 768, 1344
W = 1080
H = round(SH * W / SW)  # 1890
FPS, N = 24, 121
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_B = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
out_path, preview = sys.argv[1], len(sys.argv) > 2

# Where things are in the enlarged picture.
FRAME_TOP, FRAME_L, FRAME_R = 634, 28, 1052   # the lit frame around the back wall
VP = (540, 905)                                # where the floor's parking lines meet: the room's vanishing point

def frame(i):
    return np.asarray(Image.open(f"fr_phone/{i:03d}.png").convert("RGB").resize((W, H), Image.LANCZOS)).astype(np.float32)

PLATE = frame(1)                                # the empty set
PLATE_LUM = PLATE.max(axis=2)

def ramp(t, a, b):
    return float(np.clip((t - a) / (b - a), 0, 1))

def ease(k):
    return k * k * (3 - 2 * k)

# ---- the ceiling: a dark warehouse ceiling in the style of the photo Jacob sent (2026-11-28): ribbed metal deck,
# steel cross beams, a round duct down the middle and pairs of hanging light bars. Drawn here, not copied from the
# photo. Worked out per pixel from the room's perspective. Drawn once; it never moves.
def ceiling():
    S = 2
    yy, xx = np.mgrid[0:H * S, 0:W * S].astype(np.float32) / S
    vx, vy = VP
    s = np.maximum((vy - yy) / (vy - FRAME_TOP), 0.05)   # 1 at the back wall, bigger toward the viewer
    xw = vx + (xx - vx) / s                              # where this spot would be, measured along the back wall
    D = 1 / s                                            # distance: 1 at the back wall, smaller toward the viewer
    ribs = 0.5 + 0.5 * np.cos(2 * np.pi * xw / 15.0)
    lum = 10 + 17 * ribs ** 2                             # ribbed deck
    beams_at = [1.0 - 0.115 * k for k in range(0, 7)]
    lights = np.zeros_like(lum)
    for k, d0 in enumerate(beams_at):
        face = np.clip(1 - np.abs(D - d0) / 0.016, 0, 1)                      # a cross beam
        lum = lum * (1 - np.minimum(face * 3, 1)) + np.minimum(face * 3, 1) * (5 + 9 * np.clip((d0 - D) / 0.016, 0, 1))
        dl = d0 - 0.058                                                        # light bars hang between beams
        bar = (np.abs(D - dl) < 0.004) & (((xw > 215) & (xw < 425)) | ((xw > 655) & (xw < 865)))
        if k < 5: lights = np.maximum(lights, bar.astype(np.float32))
    for px in (28, 284, 796, 1052):                                           # long beams running front to back
        g = np.clip(1 - np.abs(xw - px) / 7.0, 0, 1)
        lum = lum * (1 - np.minimum(g * 3, 1)) + np.minimum(g * 3, 1) * 8
    r = np.clip(np.abs(xw - vx) / 44.0, 0, 1)                                 # the duct
    duct = r < 1
    rings = 0.75 + 0.25 * np.cos(2 * np.pi * D / 0.018)
    lum = np.where(duct, (10 + 34 * np.sqrt(1 - r ** 2)) * rings, lum)
    def small(a):
        return np.asarray(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)).astype(np.float32)
    lum, lights = small(lum), small(lights * 255)
    L = Image.fromarray(lights.astype(np.uint8))
    halo = np.asarray(L.filter(ImageFilter.GaussianBlur(14))).astype(np.float32) / 255
    wash = np.asarray(L.filter(ImageFilter.GaussianBlur(70))).astype(np.float32) / 255
    lum = lum * (0.85 + 4.0 * wash) + 45 * halo + 0.38 * lights              # the bars light the deck around them
    y1 = np.arange(H, dtype=np.float32)[:, None]
    x1 = np.arange(W, dtype=np.float32)[None, :]
    rgb = lum[..., None] * np.array([0.88, 1.0, 0.96], np.float32)            # a touch of the site's green
    spill = np.clip(1 - (FRAME_TOP - y1) / 150.0, 0, 1) ** 2.2 * np.clip(1 - np.abs(x1 - 540) / 760.0, 0, 1)
    rgb = rgb + spill[..., None] * np.array([110, 78, 42], np.float32)        # the frame's warm light
    mask = np.clip((FRAME_TOP - 6 - y1) / 22.0, 0, 1)[..., None]              # ends just above the frame
    return rgb * mask
CEILING = ceiling()

# ---- cars: the camera never moves, so anything that differs from the first frame is a car
plate_small = np.asarray(Image.open("fr_phone/001.png").convert("RGB")).astype(np.int16)
def car_matte(i):
    f = np.asarray(Image.open(f"fr_phone/{i:03d}.png").convert("RGB")).astype(np.int16)
    m = np.abs(f - plate_small).max(axis=2) > 11
    m = ndimage.binary_opening(m, iterations=1)
    m = ndimage.binary_closing(m, iterations=5)
    m = ndimage.binary_fill_holes(m)
    m = ndimage.binary_opening(m, iterations=2)
    lab, n = ndimage.label(m)
    if n:
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        m = np.isin(lab, [k + 1 for k, sz in enumerate(sizes) if sz > 3000])
    big = Image.fromarray((m * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.8))
    return np.asarray(big).astype(np.float32) / 255.0

# ---- the KnewCar wordmark on the back wall, behind the cars, built the way the site draws it: the logo's K, then
# "new" in white and "Car" in mint.
def logo():
    size = 176
    font = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf", size)
    k = Image.open("../../public/img/logo-k-letter.png").convert("RGBA")
    kh = int(size * 0.8)
    k = k.resize((int(k.width * kh / k.height), kh), Image.LANCZOS)
    track = -0.03 * size
    total = k.width + sum(font.getlength(c) + track for c in "newCar")
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, base = (W - total) / 2, LOGO_BASE
    layer.alpha_composite(k, (int(x), int(base - kh + size * 0.035)))
    x += k.width
    for text, colour in (("new", (255, 255, 255, 255)), ("Car", (92, 235, 196, 255))):
        for ch in text:
            d.text((x, base), ch, font=font, fill=colour, anchor="ls")
            x += font.getlength(ch) + track
    arr = np.asarray(layer).astype(np.float32)
    glow = np.asarray(layer.getchannel("A").filter(ImageFilter.GaussianBlur(22))).astype(np.float32) / 255
    return arr[..., :3], arr[..., 3] / 255.0, glow
LOGO_BASE = 792
LOGO_RGB, LOGO_A, LOGO_GLOW = logo()

# ---- the headline, filling the ceiling above the frame. Tall narrow letters (Barlow Condensed Black, open licence),
# stretched taller still so one line fills the space. Each step is (font size, left x of each word, letter height).
WORDS = ["CAR?", "TRUCK?", "SUV?"]
SIGN_RGB = np.array([196, 255, 236], np.float32)
SIGN_FONT = "BarlowCondensed-Black.woff"
small = ImageFont.truetype(FONT_B, 54)
BASE_Y = 604                                    # the letters stand on the top of the lit frame

def fit(words, size, max_w):
    while True:
        f = ImageFont.truetype(SIGN_FONT, size)
        gap = size * 0.2
        widths = [f.getlength(w) for w in words]
        total = sum(widths) + gap * (len(words) - 1)
        if total <= max_w or size <= 40: break
        size -= 2
    x, xs = (W - total) / 2, []
    for w in widths:
        xs.append(x); x += w + gap
    return size, xs
STEPS = [fit(WORDS[:1], 520, 860) + (390,), fit(WORDS[:2], 400, 1000) + (310,), fit(WORDS[:3], 400, 1020) + (255,)]
STEP_AT = [(1.2, 1.75), (2.9, 3.45)]            # when the truck and the SUV roll in on this clip

def sign(t):
    pos = ease(ramp(t, *STEP_AT[0])) + ease(ramp(t, *STEP_AT[1]))
    lo, frac = min(int(pos), 1), pos - min(int(pos), 1)
    (s0, x0, h0), (s1, x1, h1) = STEPS[lo], STEPS[lo + 1]
    size, tall = s0 + (s1 - s0) * frac, h0 + (h1 - h0) * frac
    font = ImageFont.truetype(SIGN_FONT, max(10, int(round(size))))
    cap = font.getbbox("C", anchor="ls")
    cap_h = -cap[1]
    stretch = tall / cap_h
    pad = 40
    line = Image.new("L", (W, int(cap_h + 2 * pad)), 0)
    d = ImageDraw.Draw(line)
    for n, word in enumerate(WORDS[: lo + 2]):
        if n < len(x0):
            wx, alpha = x0[n] + (x1[n] - x0[n]) * frac, 1.0
        else:
            wx, alpha = x1[n] + (1 - frac) * 40, ramp(frac, 0.6, 1.0)
        if n == 0: alpha *= ramp(t, 0.05, 0.45)
        if alpha > 0: d.text((wx, pad + cap_h), word, font=font, fill=int(255 * alpha), anchor="ls")
    line = line.resize((W, int(round(line.height * stretch))), Image.LANCZOS)
    im = Image.new("L", (W, H), 0)
    im.paste(line, (0, int(round(BASE_Y - (pad + cap_h) * stretch))))
    d = ImageDraw.Draw(im)
    label = "LOOKING FOR A NEW"
    label_y = BASE_Y - tall - 44
    x = (W - (small.getlength(label) + 16 * (len(label) - 1))) / 2
    lab = int(255 * ramp(t, 0.0, 0.35))
    for ch in label:
        d.text((x, label_y), ch, font=small, fill=lab, anchor="ls")
        x += small.getlength(ch) + 16
    glow = im.filter(ImageFilter.GaussianBlur(20))
    shadow = np.asarray(im.filter(ImageFilter.GaussianBlur(34))).astype(np.float32) / 255
    a = np.asarray(im).astype(np.float32) / 255 * 0.9 + np.asarray(glow).astype(np.float32) / 255 * 0.35
    behind = 1 - np.clip((PLATE_LUM - 70) / 90.0, 0, 1)   # the frame's own bright line stays in front
    return np.clip(a, 0, 1) * behind, np.clip(shadow * 1.6, 0, 1)

# ---- floor: the tagline in two lines, laid flat in front of the cars
def floor():
    font = ImageFont.truetype(FONT, 150)
    lines = ["ALL YOUR OPTIONS.", "ONE EASY PLACE."]
    FW = int(max(font.getlength(l) for l in lines)) + 80
    flat = Image.new("L", (FW, 400), 0)
    d = ImageDraw.Draw(flat)
    d.text((FW / 2, 105), lines[0], font=font, fill=255, anchor="mm")
    d.text((FW / 2, 295), lines[1], font=font, fill=255, anchor="mm")
    top_y, bot_y = 1092, 1292                   # kept clear of the button and dots that sit over the bottom of the clip
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
    f = f + CEILING * (1 - f / 255.0)                         # the ceiling, wherever the clip is dark
    keep = 1 - car_matte(i)
    show = ramp(t, 0.0, 0.5) * keep                           # the logo on the back wall, behind the cars
    f = f + (255 - f) * (LOGO_GLOW * 0.10 * show)[..., None]
    la = (LOGO_A * 0.74 * show)[..., None]
    f = f * (1 - la) + LOGO_RGB * la
    a, shadow = sign(t)
    f = f * (1 - 0.85 * shadow[..., None])                     # the ceiling dims behind the letters so they read
    f = f + (SIGN_RGB - f * SIGN_RGB / 255.0) * a[..., None]  # the letters, as light
    k = ramp(t, 3.7, 4.6)
    if k > 0:
        wipe = np.clip((k * 1.25 * W - np.arange(W)) / 130.0, 0, 1)[None, :]
        fa = (FLOOR * 0.95 * wipe)[..., None]
        ga = (FLOOR_GLOW * 0.25 * wipe)[..., None]
        f = f + (255 - f) * ga * 0.6
        f = f * (1 - fa) + (255 * 0.78 + f * 0.35) * fa
    return np.clip(f, 0, 255).astype(np.uint8)

if preview:
    tiles = [Image.fromarray(compose(i)).resize((432, 756)) for i in (12, 50, 121)]
    sheet = Image.new("RGB", (432 * 3, 756))
    for n, tl in enumerate(tiles):
        sheet.paste(tl, (n * 432, 0))
    sheet.save(out_path, quality=90)
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
