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

# ---- back wall: small line and a giant word. The word runs down behind the car roofs.
WALL_TOP, WORD_BASE = 104, 462
small = ImageFont.truetype(FONT_B, 46)
def wall(word):
    size = 340
    font = ImageFont.truetype(FONT, size)
    while font.getlength(word) > 1380:
        size -= 10
        font = ImageFont.truetype(FONT, size)
    def draw(d):
        label = "LOOKING FOR A NEW"
        x = (W - (small.getlength(label) + 14 * (len(label) - 1))) / 2
        for ch in label:  # letter-spaced
            d.text((x, WALL_TOP), ch, font=small, fill=255)
            x += small.getlength(ch) + 14
        d.text((W / 2, WORD_BASE), word, font=font, fill=255, anchor="ms")
    crisp = text_layer(draw)
    glow = crisp.filter(ImageFilter.GaussianBlur(26))
    a = np.asarray(crisp).astype(np.float32) / 255 * 0.78 + np.asarray(glow).astype(np.float32) / 255 * 0.42
    # sinks into the haze near the floor
    fade = np.clip((600 - np.arange(H)) / 260.0, 0, 1)[:, None]
    return np.clip(a, 0, 1) * (0.35 + 0.65 * fade)
WALL = {w: wall(w) for w in ("CAR?", "TRUCK?", "SUV?")}
WALL_RGB = np.array([196, 255, 236], np.float32)  # pale mint light

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
    # word changes as each one rolls in: car 0s, truck 1.0s, SUV 2.1s
    weights = {"CAR?": ramp(t, 0.05, 0.45) * (1 - ramp(t, 0.9, 1.15)), "TRUCK?": ramp(t, 0.95, 1.2) * (1 - ramp(t, 2.0, 2.25)), "SUV?": ramp(t, 2.05, 2.3)}
    a = sum(WALL[w] * k for w, k in weights.items() if k > 0)
    if not np.isscalar(a):
        a = (a * keep)[..., None]
        f = f + (WALL_RGB - f * WALL_RGB / 255.0) * a  # screen: light on the wall
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
