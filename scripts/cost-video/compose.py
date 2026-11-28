"""Slide 3, "Know the real cost in your state.": one Toyota RAV4 stays put while the state changes, and the sales
tax, fees and estimated total change with it.

The picture in src/ is Jacob's (2026-11-28): our own catalog photo of the 2026 RAV4 XLE Premium, re-set by an image
tool in a dark green studio. It is square, so the wall, ceiling and floor are extended here to fill a wide screen or
a phone. The lettering is drawn here, never by the image tool.

Every number comes from the website's own estimator: this script runs numbers.mjs, which calls src/lib/estimate.ts.
Nothing is typed in by hand. Run this again whenever the RAV4's MSRP, the destination charge or a state rule changes.

Texas, Florida and California are shown (Jacob's choice, 2026-11-28). Texas and Florida have no county chosen, so
they are state tax and state fees only. California is shown for Los Angeles County at the county's combined rate from
the state's own rate table, because the statewide 7.25% alone understates what most Californians pay; the tax line
names the county and the note says cities may differ. The sales tax line is yellow so it stands out.

On a wide screen the car sits to the left and the headline and a large receipt fill the right, so this slide does
not look like slide 2 (car in the middle, words around it). On a phone the receipt is on the floor in front of the car.

usage: python3 compose.py wide|phone out.mp4 [preview]        (run from scripts/cost-video)"""
import json, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

shape, out_path, preview = sys.argv[1], sys.argv[2], len(sys.argv) > 3
PHONE = shape == "phone"
W, H = (1080, 1890) if PHONE else (1920, 1080)
FPS = 24
INTER = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
INTER_B = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
INTER_M = "/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf"
NARROW = "../intro-video/BarlowCondensed-Black.woff"
MINT = np.array([196, 255, 236], np.float32)

DATA = json.loads(subprocess.run(["node", "scripts/cost-video/numbers.mjs", "TX", "FL", "CA"], cwd="../..", capture_output=True, text=True, check=True).stdout)
STATES = DATA["states"]
# A state shown for one county says so on its tax line, and its note explains what the county rate covers.
def tax_label(s):
    return f"Sales tax, {s['county']} County" if s["county"] else "Sales tax"
def note(s):
    return "County rate outside city limits. Cities and local fees may differ." if s["county"] else "Local taxes and fees not included."
YELLOW = np.array([255, 196, 92], np.float32)                           # the site's warm accent, for the tax line
money = lambda cents: f"${cents / 100:,.2f}"
for s in STATES:
    assert s["gross"] + s["tax"] + s["fees"] == s["total"], s["name"]
    print(s["name"], money(s["gross"]), money(s["tax"]), money(s["fees"]), money(s["total"]))

# ---- the studio: the square picture, with its edges carried outward and darkened to fill the screen
SIDE = 1080
X0, Y0 = (0, 300) if PHONE else (-60, 0)   # on a phone the picture sits high, leaving the floor for the receipt
def stage():
    sq = np.asarray(Image.open("src/rav4-xle-premium.png").convert("RGB").resize((SIDE, SIDE), Image.LANCZOS)).astype(np.float32)
    canvas = np.zeros((H, W, 3), np.float32)
    if PHONE:
        canvas[Y0:Y0 + SIDE] = sq
        top, bottom = sq[:6].mean(axis=0), sq[-6:].mean(axis=0)
        canvas[:Y0] = top[None] * np.linspace(0.45, 1.0, Y0)[:, None, None]
        canvas[Y0 + SIDE:] = bottom[None] * np.linspace(1.0, 0.3, H - Y0 - SIDE)[:, None, None]
    else:
        canvas[:, :X0 + SIDE] = sq[:, -X0:]                                # the car sits at the left of the screen
        right = sq[:, -6:].mean(axis=1)
        canvas[:, X0 + SIDE:] = right[:, None] * np.linspace(1.0, 0.55, W - X0 - SIDE)[None, :, None]
    return canvas
STAGE = stage()

def ramp(t, a, b):
    return float(np.clip((t - a) / (b - a), 0, 1))
def ease(k):
    return k * k * (3 - 2 * k)
def spaced(d, xy, text, font, gap, fill=255):
    width = sum(font.getlength(c) for c in text) + gap * (len(text) - 1)
    x = xy[0] - width / 2
    for ch in text:
        d.text((x, xy[1]), ch, font=font, fill=fill, anchor="ls")
        x += font.getlength(ch) + gap
def lit(layer, glow=18, strength=0.35):
    g = layer.filter(ImageFilter.GaussianBlur(glow))
    return np.clip(np.asarray(layer).astype(np.float32) / 255 * 0.92 + np.asarray(g).astype(np.float32) / 255 * strength, 0, 1)
def arr(layer):
    return np.asarray(layer).astype(np.float32) / 255

# ---- the headline. Wide: two lines at the top right, above the receipt. Phone: two lines on the ceiling in tall
# narrow letters.
RX0, RX1 = 1064, 1822                    # wide: the right-hand column
def headline():
    im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(im)
    lines = ["KNOW THE REAL COST", "IN YOUR STATE."]
    if PHONE:
        tall, size = 104, 250
        while max(ImageFont.truetype(NARROW, size).getlength(l) for l in lines) > 940: size -= 2
        font = ImageFont.truetype(NARROW, size)
        cap = -font.getbbox("E", anchor="ls")[1]
        k = tall / cap
        for text, base in zip(lines, (278, 408)):
            line = Image.new("L", (W, cap + 80), 0)
            ImageDraw.Draw(line).text((W / 2, 40 + cap), text, font=font, fill=255, anchor="ms")
            line = line.resize((W, int(line.height * k)), Image.LANCZOS)
            im.paste(line, (0, int(base - (40 + cap) * k)), line)
    else:
        size = 120
        while ImageFont.truetype(INTER, size).getlength(lines[0]) > RX1 - RX0: size -= 1
        font = ImageFont.truetype(INTER, size)
        for text, base in zip(lines, (236, 236 + int(size * 1.08))):
            d.text((RX0, base), text, font=font, fill=255, anchor="ls")
    return lit(im, 20, 0.35)
HEAD = headline()

# ---- the receipt. Fixed parts (the card, most labels, the price) are drawn once; the state's name, its tax label
# and its three figures are drawn per state.
if PHONE:
    BOX = (110, 1052, 970, 1316)          # left, top, right, bottom of the card
    ROWS, TOTAL_Y, NOTE_Y = [1132, 1172, 1212], 1264, 1300
    F_LABEL, F_AMT, F_TOTAL, F_NOTE = ImageFont.truetype(INTER_M, 34), ImageFont.truetype(INTER_B, 36), ImageFont.truetype(INTER, 46), ImageFont.truetype(INTER_M, 22)
    PAD, RULE = 34, 16
else:
    BOX = (RX0, 386, RX1, 850)
    ROWS, TOTAL_Y, NOTE_Y = [590, 642, 694], 782, 826
    F_LABEL, F_AMT, F_TOTAL, F_NOTE = ImageFont.truetype(INTER_M, 31), ImageFont.truetype(INTER_B, 33), ImageFont.truetype(INTER, 54), ImageFont.truetype(INTER_M, 19)
    PAD, RULE = 36, 22

def card():
    im = Image.new("L", (W, H), 0)
    ImageDraw.Draw(im).rounded_rectangle(BOX, radius=22, fill=255)
    return arr(im.filter(ImageFilter.GaussianBlur(1.2)))
CARD = card()
CARD_STRENGTH = 0.62 if PHONE else 0.8

def fixed_text():
    """One layer per row, so the rows can come in one after another."""
    rows = []
    for k, label in ((0, "Price with destination"), (2, "Fees, estimated")):
        im = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(im)
        d.text((BOX[0] + PAD, ROWS[k]), label, font=F_LABEL, fill=200, anchor="ls")
        if k == 0: d.text((BOX[2] - PAD, ROWS[k]), money(STATES[0]["gross"]), font=F_AMT, fill=255, anchor="rs")
        rows.append(arr(im))
    im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(im)
    d.line([(BOX[0] + PAD, ROWS[2] + RULE), (BOX[2] - PAD, ROWS[2] + RULE)], fill=110, width=2)
    d.text((BOX[0] + PAD, TOTAL_Y), "Estimated total", font=F_LABEL, fill=255, anchor="ls")
    rows.append(arr(im))
    head = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(head)
    if PHONE:
        spaced(d, (W / 2, 520), DATA["vehicle"].upper(), ImageFont.truetype(INTER_B, 28), 8, 220)
        spaced(d, ((BOX[0] + BOX[2]) / 2, BOX[1] + 40), "EXAMPLE ESTIMATE", ImageFont.truetype(INTER_B, 24), 9, 190)
    else:
        d.text((BOX[2] - PAD, 452), "EXAMPLE ESTIMATE", font=ImageFont.truetype(INTER_B, 19), fill=190, anchor="rs")
        d.text((BOX[0] + PAD, 522), DATA["vehicle"], font=ImageFont.truetype(INTER_M, 25), fill=210, anchor="ls")
    return rows, arr(head)
(ROW_PRICE, ROW_FEES, ROW_TOTAL), FIXED_HEAD = fixed_text()

def state_text(s):
    name = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(name)
    if PHONE: d.text((W / 2, 642), s["name"].upper(), font=ImageFont.truetype(INTER, 112), fill=255, anchor="ms")
    else: d.text((BOX[0] + PAD, 478), s["name"].upper(), font=ImageFont.truetype(INTER, 70), fill=255, anchor="ls")
    tax = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(tax)
    d.text((BOX[0] + PAD, ROWS[1]), tax_label(s), font=F_LABEL, fill=235, anchor="ls")
    d.text((BOX[2] - PAD, ROWS[1]), money(s["tax"]), font=F_AMT, fill=255, anchor="rs")
    fees = Image.new("L", (W, H), 0)
    ImageDraw.Draw(fees).text((BOX[2] - PAD, ROWS[2]), money(s["fees"]), font=F_AMT, fill=255, anchor="rs")
    total = Image.new("L", (W, H), 0)
    ImageDraw.Draw(total).text((BOX[2] - PAD, TOTAL_Y), money(s["total"]), font=F_TOTAL, fill=255, anchor="rs")
    foot = Image.new("L", (W, H), 0)
    ImageDraw.Draw(foot).text((BOX[0] + PAD, NOTE_Y), note(s), font=F_NOTE, fill=150, anchor="ls")
    return lit(name, 16, 0.3), [arr(tax), arr(fees), arr(foot)], lit(total, 12, 0.25)
PER_STATE = [state_text(s) for s in STATES]

# ---- timing: the receipt writes itself for the first state, then the state changes twice
FIRST, HOLD, MELT, LAST = 2.7, 1.6, 0.4, 2.0
CHANGES = [FIRST, FIRST + MELT + HOLD]
LENGTH = CHANGES[-1] + MELT + LAST
N = int(round(LENGTH * FPS))
ROW_IN = [0.5, 0.9, 1.3, 1.7]                                           # when each row of the receipt comes in

def white(f, a):
    return f + (255 - f) * a[..., None]
def mint(f, a):
    return f + (MINT - f * MINT / 255.0) * a[..., None]

def compose(i):
    t = i / FPS
    f = STAGE.copy()
    f = mint(f, HEAD * ramp(t, 0.0, 0.4))
    c = (CARD * CARD_STRENGTH * ramp(t, 0.3, 0.7))[..., None]
    f = f * (1 - c) + np.array([4, 16, 12], np.float32) * c              # the dark card behind the receipt
    f = white(f, FIXED_HEAD * ramp(t, 0.3, 0.7))
    f = white(f, ROW_PRICE * ramp(t, ROW_IN[0], ROW_IN[0] + 0.3))
    f = white(f, ROW_FEES * ramp(t, ROW_IN[2], ROW_IN[2] + 0.3))
    f = white(f, ROW_TOTAL * ramp(t, ROW_IN[3], ROW_IN[3] + 0.3))
    pos = sum(ease(ramp(t, c0, c0 + MELT)) for c0 in CHANGES)            # 0..2, which state is showing
    for k, (name_a, rows, total_a) in enumerate(PER_STATE):
        w = 1.0
        if k > 0: w *= ramp(pos, k - 0.45, k - 0.05)
        if k < len(PER_STATE) - 1: w *= 1 - ramp(pos, k + 0.05, k + 0.45)
        if w <= 0: continue
        f = mint(f, name_a * w * ramp(t, 0.2, 0.6))
        ta = (rows[0] * w * ramp(t, ROW_IN[1], ROW_IN[1] + 0.3))[..., None]
        f = f * (1 - ta) + YELLOW * ta                                   # the tax line, in yellow
        f = white(f, rows[2] * w * ramp(t, ROW_IN[3], ROW_IN[3] + 0.3))
        f = white(f, rows[1] * w * ramp(t, ROW_IN[2], ROW_IN[2] + 0.3))
        f = mint(f, total_a * w * ramp(t, ROW_IN[3], ROW_IN[3] + 0.3))
    return np.clip(f, 0, 255).astype(np.uint8)

if preview:
    picks = [int(1.2 * FPS), int((CHANGES[0] - 0.1) * FPS), int((CHANGES[1] - 0.1) * FPS), N - 1]
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
    Image.fromarray(compose(int(2.3 * FPS))).save(out_path.replace(".mp4", "-start.jpg"), quality=85)
    print("wrote", out_path, f"{LENGTH:.1f}s")
