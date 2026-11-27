"""Builds src/data/configs.json: one entry per configuration the app has (trim, model year, drivetrain, body).

Inputs, both exported read-only from the catalog on 2026-11-23:
  scripts/configs.txt        make|model|year|trim~msrp:drive:body:photo,...;trim~...
                             msrp is the verified current MSRP without destination (empty when none is verified);
                             drive is a/4/f/r or -; body is a one-letter code or -; photo is the first six
                             characters of the photo's id.
  scripts/config-photos.txt  photo id (six characters)|path inside the public vehicle-images bucket after hero/hero_v1/

Photos are saved as public/img/cfg/<photo id>.webp (560x420) and <photo id>-lg.webp (1040x780, for sharp screens).
Ones already saved are skipped, so this can be re-run.
Run scripts/build-catalog.py first: this script reads src/data/catalog.json for model keys and trim spellings.

usage: python3 scripts/build-configs.py [--no-download]
"""
import io, json, os, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

BASE = "https://fmuyjfhucjtjzkweeqyd.supabase.co/storage/v1/object/public/vehicle-images/hero/hero_v1/"
DRIVE = {"a": "AWD", "4": "4WD", "f": "FWD", "r": "RWD", "-": None}
BODY = {"2": "2-door", "4": "4-door", "v": "Convertible", "c": "Coupe", "h": "Hatchback", "m": None, "R": "Retractable hardtop",
        "s": "Sedan", "t": "Soft top", "u": None, "k": None, "-": None}
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
norm = lambda s: re.sub(r"\s+", " ", s.replace("®", "").upper()).strip()

catalog = json.load(open("src/data/catalog.json"))
by_key = {c["key"]: c for c in catalog}
paths = dict(l.split("|") for l in open("scripts/config-photos.txt").read().strip().split("\n") if not l.startswith("#"))

def tidy(make, model, trim, known):
    """The catalog's spelling of a trim when it has one; else the manufacturer's name without the model in front."""
    short = model[len(make) + 1:] if model.lower().startswith(make.lower() + " ") else model
    for cand in (trim, re.sub("^" + re.escape(norm(model)) + " ", "", norm(trim)), re.sub("^" + re.escape(norm(short)) + " ", "", norm(trim))):
        if norm(cand) in known: return known[norm(cand)]
    rest = re.sub("^(" + re.escape(norm(model)) + "|" + re.escape(norm(short)) + ") ", "", norm(trim)) if trim.isupper() else None
    if rest is None: return trim.replace("®", "")
    return " ".join(w if re.search(r"\d", w) else w.capitalize() for w in rest.split(" ")).replace("4X4", "4x4").replace("4X2", "4x2")

out, need = [], {}
for l in open("scripts/configs.txt").read().strip().split("\n"):
    if l.startswith("#"): continue
    make, model, year, trims = l.split("|")
    key = f"{slug(make)}-{slug(model)}"
    car = by_key[key]
    known = {norm(t["name"]): t["name"] for t in car["trims"]}
    for t in trims.split(";"):
        name, items = t.split("~")
        for item in items.split(","):
            msrp, drive, body, photo = item.split(":")
            assert photo in paths, f"no photo path for {photo}"
            need[photo] = paths[photo]
            out.append({"key": key, "year": int(year), "trim": tidy(make, model, name, known), "drive": DRIVE[drive],
                        "body": BODY[body], "msrp": int(msrp) if msrp else None, "img": photo})

def fetch(job):
    photo, path = job
    dest = f"public/img/cfg/{photo}.webp"
    large = f"public/img/cfg/{photo}-lg.webp"  # for sharp screens and phones
    if os.path.exists(dest) and os.path.exists(large): return None
    for attempt in range(4):
        try:
            raw = urllib.request.urlopen(BASE + path, timeout=60).read()
            im = Image.open(io.BytesIO(raw)).convert("RGB")
            if not os.path.exists(dest): im.resize((560, 420), Image.LANCZOS).save(dest, "WEBP", quality=78)
            im.resize((1040, 780), Image.LANCZOS).save(large, "WEBP", quality=74)
            return None
        except Exception as e:
            err = str(e)
            time.sleep(20 * (attempt + 1))
    return f"{photo}: {err}"

if "--no-download" not in sys.argv:
    os.makedirs("public/img/cfg", exist_ok=True)
    with ThreadPoolExecutor(3) as pool:
        failed = [r for r in pool.map(fetch, sorted(need.items())) if r]
    print(len(need), "photos listed;", len(failed), "failed")
    for f in failed[:10]: print("FAILED", f)

missing = [p for p in need if not os.path.exists(f"public/img/cfg/{p}.webp")]
out.sort(key=lambda c: (c["key"], -c["year"], c["trim"], c["drive"] or "", c["body"] or ""))
json.dump(out, open("src/data/configs.json", "w"), separators=(",", ":"))
print(len(out), "configurations;", len(need), "distinct photos;", len(missing), "photos not downloaded yet")
sys.exit(1 if missing else 0)
