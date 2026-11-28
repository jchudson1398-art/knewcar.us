"""The phone version of the intro: Jacob's tall (768x1344) clip of the same scene, used whole so it fills a phone.

Design (2026-11-28): the clip has empty black above the set. That space becomes a dark ceiling running from the top
of the lit frame toward the viewer, and the headline is lifted onto it: "LOOKING FOR A NEW" with CAR? TRUCK? SUV?
building into one line, standing just behind the top edge of the lit frame like a sign above the set. The back wall
is left clear so the cars read cleanly. "ALL YOUR OPTIONS. ONE EASY PLACE." is laid on the floor in front of the
cars, in two lines.

usage: python3 compose_phone.py out.mp4 [preview]      (frames of the source clip must be in fr_phone/)"""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

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

# ---- the ceiling: dark panels in perspective, with two faint light channels and the frame's warm light spilling
# onto the part nearest the wall. Drawn once; it never moves.
def ceiling():
    S = 2  # draw at double size, then shrink, for smooth lines
    im = Image.new("L", (W * S, H * S), 0)
    d = ImageDraw.Draw(im)
    vx, vy = VP
    def ray(x_at_wall, width, value):
        # a line from the vanishing point through (x_at_wall, FRAME_TOP), continued up to the top of the picture
        x_top = vx + (x_at_wall - vx) * (vy - 0) / (vy - FRAME_TOP)
        d.line([(x_at_wall * S, FRAME_TOP * S), (x_top * S, 0)], fill=value, width=width * S)
    for k in range(-2, 15):                     # panel seams running away from the viewer
        ray(FRAME_L + (FRAME_R - FRAME_L) * k / 12, 2, 70)
    depth = 1.0
    while True:                                 # cross seams, further apart the nearer they are
        depth *= 1.34
        y = vy - (vy - FRAME_TOP) * depth
        if y < -40: break
        x0 = vx + (FRAME_L - vx) * depth
        x1 = vx + (FRAME_R - vx) * depth
        d.line([(x0 * S - 400, y * S), (x1 * S + 400, y * S)], fill=70, width=max(2, int(1.5 * depth)) * S)
    seams = np.asarray(im.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
    lights = Image.new("L", (W * S, H * S), 0)
    d = ImageDraw.Draw(lights)
    for frac in (0.25, 0.75):                   # two recessed light channels
        ray(FRAME_L + (FRAME_R - FRAME_L) * frac, 7, 255)
    lights = lights.resize((W, H), Image.LANCZOS)
    core = np.asarray(lights).astype(np.float32) / 255
    halo = np.asarray(lights.filter(ImageFilter.GaussianBlur(26))).astype(np.float32) / 255
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    near = np.clip((FRAME_TOP - yy) / FRAME_TOP, 0, 1)        # 0 at the wall, 1 at the top of the picture
    base = np.array([11, 26, 23], np.float32) * (1.15 - 0.75 * near)[..., None]             # darker toward the viewer
    rgb = base + seams[..., None] * np.array([26, 46, 40], np.float32) * (1 - 0.5 * near)[..., None]
    rgb += (core[..., None] * 0.55 + halo[..., None] * 0.9) * np.array([95, 160, 142], np.float32) * (1 - 0.45 * near)[..., None]
    spill = np.clip(1 - (FRAME_TOP - yy) / 210.0, 0, 1) ** 2.2 * np.clip(1 - np.abs(xx - 540) / 760.0, 0, 1)
    rgb += spill[..., None] * np.array([120, 84, 46], np.float32)                           # the frame's warm light
    mask = np.clip((FRAME_TOP - 6 - yy) / 26.0, 0, 1)[..., None]                            # ends just above the frame
    return rgb * mask
CEILING = ceiling()

# ---- the headline, standing above the frame. Each step is (font size, left x of each word, baseline y, label y).
WORDS = ["CAR?", "TRUCK?", "SUV?"]
SIGN_RGB = np.array([196, 255, 236], np.float32)
small = ImageFont.truetype(FONT_B, 42)

def fit(words, size, max_w):
    while True:
        f = ImageFont.truetype(FONT, size)
        gap = size * 0.22
        widths = [f.getlength(w) for w in words]
        total = sum(widths) + gap * (len(words) - 1)
        if total <= max_w or size <= 40: break
        size -= 2
    x, xs = (W - total) / 2, []
    for w in widths:
        xs.append(x); x += w + gap
    return size, xs
STEPS = [fit(WORDS[:1], 330, 900) + (612, 286), fit(WORDS[:2], 300, 1000) + (606, 372), fit(WORDS[:3], 300, 1010) + (600, 428)]
STEP_AT = [(1.2, 1.75), (2.9, 3.45)]            # when the truck and the SUV roll in on this clip

def sign(t):
    pos = ease(ramp(t, *STEP_AT[0])) + ease(ramp(t, *STEP_AT[1]))
    lo, frac = min(int(pos), 1), pos - min(int(pos), 1)
    (s0, x0, y0, l0), (s1, x1, y1, l1) = STEPS[lo], STEPS[lo + 1]
    size, base, label_y = s0 + (s1 - s0) * frac, y0 + (y1 - y0) * frac, l0 + (l1 - l0) * frac
    font = ImageFont.truetype(FONT, max(10, int(round(size))))
    im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(im)
    label = "LOOKING FOR A NEW"
    x = (W - (small.getlength(label) + 13 * (len(label) - 1))) / 2
    lab = int(255 * ramp(t, 0.0, 0.35))
    for ch in label:
        d.text((x, label_y), ch, font=small, fill=lab, anchor="ls")
        x += small.getlength(ch) + 13
    for n, word in enumerate(WORDS[: lo + 2]):
        if n < len(x0):
            wx, alpha = x0[n] + (x1[n] - x0[n]) * frac, 1.0
        else:
            wx, alpha = x1[n] + (1 - frac) * 40, ramp(frac, 0.6, 1.0)
        if n == 0: alpha *= ramp(t, 0.05, 0.45)
        if alpha > 0: d.text((wx, base), word, font=font, fill=int(255 * alpha), anchor="ls")
    glow = im.filter(ImageFilter.GaussianBlur(20))
    a = np.asarray(im).astype(np.float32) / 255 * 0.86 + np.asarray(glow).astype(np.float32) / 255 * 0.4
    # the sign stands behind the lit frame: where the frame's own line is bright, the frame wins
    behind = 1 - np.clip((PLATE_LUM - 70) / 90.0, 0, 1)
    return np.clip(a, 0, 1) * behind

# ---- floor: the tagline in two lines, laid flat in front of the cars
def floor():
    font = ImageFont.truetype(FONT, 150)
    lines = ["ALL YOUR OPTIONS.", "ONE EASY PLACE."]
    FW = int(max(font.getlength(l) for l in lines)) + 80
    flat = Image.new("L", (FW, 400), 0)
    d = ImageDraw.Draw(flat)
    d.text((FW / 2, 105), lines[0], font=font, fill=255, anchor="mm")
    d.text((FW / 2, 295), lines[1], font=font, fill=255, anchor="mm")
    top_y, bot_y = 1150, 1372                   # kept clear of the button and dots that sit over the bottom of the clip
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
    a = sign(t)[..., None]
    f = f + (SIGN_RGB - f * SIGN_RGB / 255.0) * a             # the sign, as light
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
