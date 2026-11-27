"""Puts the headline inside Jacob's intro video: a giant word on the back wall, behind the cars, and a caption laid
on the floor in front of them. The camera never moves, so the first frame (empty lot) is a clean background plate and
anything that differs from it is a car. Output: 1920x1080 frames piped to ffmpeg."""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage

W, H, FPS, N = 1920, 1080, 24, 121
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_B = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
out_path, preview = sys.argv[1], len(sys.argv) > 2

def frame(i):
    return np.asarray(Image.open(f"fr/{i:03d}.png").convert("RGB").resize((W, H), Image.LANCZOS)).astype(np.float32)

plate720 = np.asarray(Image.open("fr/001.png").convert("RGB")).astype(np.int16)

def car_matte(i):
    """1 where a car is, 0 where the empty set shows. Worked out at 720p, then enlarged and feathered."""
    f = np.asarray(Image.open(f"fr/{i:03d}.png").convert("RGB")).astype(np.int16)
    d = np.abs(f - plate720).max(axis=2)
    m = d > 20
    m = ndimage.binary_opening(m, iterations=1)
    m = ndimage.binary_closing(m, iterations=5)
    m = ndimage.binary_fill_holes(m)
    m = ndimage.binary_opening(m, iterations=2)
    # the drifting haze also differs a little from the empty set: keep only car-sized shapes
    lab, n = ndimage.label(m)
    if n:
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        m = np.isin(lab, [k + 1 for k, s in enumerate(sizes) if s > 6000])
    big = Image.fromarray((m * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2.2))
    return np.asarray(big).astype(np.float32) / 255.0

def text_layer(draw_fn):
    im = Image.new("L", (W, H), 0)
    draw_fn(ImageDraw.Draw(im))
    return im

# ---- back wall: "LOOKING FOR A NEW" and the words CAR? TRUCK? SUV? building into one line as each one pulls in.
# CAR? starts large; it shrinks and slides over when TRUCK? joins, and both shrink again when SUV? joins. Each
# step also sits a little higher, because the cars fill more of the picture.
WALL_TOP = 104
small = ImageFont.truetype(FONT_B, 46)
WORDS = ["CAR?", "TRUCK?", "SUV?"]
WALL_RGB = np.array([196, 255, 236], np.float32)  # pale mint light

def fit(words, size, max_w):
    """Largest size up to `size` at which the words, set in one line, fit max_w. Returns size and each word's left x."""
    while True:
        f = ImageFont.truetype(FONT, size)
        gap = size * 0.26
        widths = [f.getlength(w) for w in words]
        total = sum(widths) + gap * (len(words) - 1)
        if total <= max_w or size <= 60: break
        size -= 4
    x, xs = (W - total) / 2, []
    for w in widths:
        xs.append(x); x += w + gap
    return size, xs
# One layout per step: (font size, left x of each word, baseline y)
STEPS = [fit(WORDS[:1], 340, 1380) + (462,), fit(WORDS[:2], 300, 1560) + (404,), fit(WORDS[:3], 300, 1660) + (352,)]
STEP_AT = [(0.95, 1.5), (2.05, 2.6)]  # when the truck and the SUV roll in: start and end of each move

def ease(k):
    return k * k * (3 - 2 * k)

def wall(t):
    k1, k2 = ease(ramp(t, *STEP_AT[0])), ease(ramp(t, *STEP_AT[1]))
    pos = k1 + k2  # 0 = CAR? alone, 1 = two words, 2 = all three
    lo, frac = min(int(pos), 1), pos - min(int(pos), 1)
    (s0, x0, y0), (s1, x1, y1) = STEPS[lo], STEPS[lo + 1]
    size = s0 + (s1 - s0) * frac
    base = y0 + (y1 - y0) * frac
    font = ImageFont.truetype(FONT, max(10, int(round(size))))
    im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(im)
    label = "LOOKING FOR A NEW"
    x = (W - (small.getlength(label) + 14 * (len(label) - 1))) / 2
    lab = int(255 * ramp(t, 0.0, 0.35))
    for ch in label:
        d.text((x, WALL_TOP), ch, font=small, fill=lab)
        x += small.getlength(ch) + 14
    for n, word in enumerate(WORDS[: lo + 2]):
        if n < len(x0):      # already on the wall: slide and shrink
            wx, alpha = x0[n] + (x1[n] - x0[n]) * frac, 1.0
        else:                # the new word: comes in at its place, from a little to the right
            wx, alpha = x1[n] + (1 - frac) * 60, ramp(frac, 0.6, 1.0)  # only once the others have made room
        if n == 0: alpha *= ramp(t, 0.05, 0.45)
        if alpha > 0: d.text((wx, base), word, font=font, fill=int(255 * alpha), anchor="ls")
    glow = im.filter(ImageFilter.GaussianBlur(26))
    a = np.asarray(im).astype(np.float32) / 255 * 0.78 + np.asarray(glow).astype(np.float32) / 255 * 0.42
    fade = np.clip((600 - np.arange(H)) / 260.0, 0, 1)[:, None]  # sinks into the haze near the floor
    return np.clip(a, 0, 1) * (0.35 + 0.65 * fade)

# ---- floor: one caption line laid flat on the ground in front of the cars
def floor():
    font = ImageFont.truetype(FONT, 132)
    FW = int(font.getlength("ALL YOUR OPTIONS. ONE EASY PLACE.")) + 80
    flat = Image.new("L", (FW, 260), 0)
    ImageDraw.Draw(flat).text((FW / 2, 130), "ALL YOUR OPTIONS. ONE EASY PLACE.", font=font, fill=255, anchor="mm")
    # squash and widen toward the camera so it lies on the floor
    top_y, bot_y = 852, 962
    quad = [(190, top_y), (W - 190, top_y), (W - 110, bot_y), (110, bot_y)]
    src = [(0, 0), (FW, 0), (FW, 260), (0, 260)]
    A = []
    for (x, y), (u, v) in zip(quad, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    coef = np.linalg.solve(np.array(A, np.float64), np.array([c for p in src for c in p], np.float64))
    laid = flat.transform((W, H), Image.PERSPECTIVE, tuple(coef), Image.BICUBIC)
    return np.asarray(laid).astype(np.float32) / 255, np.asarray(laid.filter(ImageFilter.GaussianBlur(10))).astype(np.float32) / 255
FLOOR, FLOOR_GLOW = floor()

def ramp(t, a, b):
    return float(np.clip((t - a) / (b - a), 0, 1))

def compose(i):
    t = (i - 1) / FPS
    f = frame(i)
    keep = 1 - car_matte(i)
    a = (wall(t) * keep)[..., None]
    f = f + (WALL_RGB - f * WALL_RGB / 255.0) * a  # screen: light on the wall, hidden where a car is
    # floor caption wipes in from the left once everything has arrived
    k = ramp(t, 2.7, 3.7)
    if k > 0:
        wipe = np.clip((k * 1.25 * W - np.arange(W)) / 160.0, 0, 1)[None, :]
        fa = (FLOOR * 0.95 * wipe)[..., None]
        ga = (FLOOR_GLOW * 0.25 * wipe)[..., None]
        f = f + (255 - f) * ga * 0.6
        f = f * (1 - fa) + (255 * 0.78 + f * 0.35) * fa  # painted on the glossy floor: reflections still show through
    return np.clip(f, 0, 255).astype(np.uint8)

if preview:
    tiles = [Image.fromarray(compose(i)).resize((960, 540)) for i in (8, 22, 40, 62, 80, 121)]
    sheet = Image.new("RGB", (1920, 1620))
    for n, tl in enumerate(tiles):
        sheet.paste(tl, ((n % 2) * 960, (n // 2) * 540))
    sheet.save(out_path, quality=88)
else:
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-crf", "21", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out_path], stdin=subprocess.PIPE)
    last = None
    for i in range(1, N + 1):
        last = compose(i)
        ff.stdin.write(last.tobytes())
    ff.stdin.close(); ff.wait()
    Image.fromarray(last).save(out_path.replace(".mp4", "-end.jpg"), quality=88)
    Image.fromarray(compose(1)).save(out_path.replace(".mp4", "-start.jpg"), quality=85)
    print("wrote", out_path)
