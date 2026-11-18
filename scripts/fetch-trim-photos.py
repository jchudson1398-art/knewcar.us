"""Downloads one photo per trim and saves it as public/img/trims/<model key>--<trim>.webp (560x420).

Input: scripts/trim-photos.txt, exported read-only from the catalog. One line per model:
  Make|Model|year|Trim~path;Trim~path;...
where path is the photo's location in the public vehicle-images bucket after hero/hero_v1/.
Photos already saved are skipped, so this can be re-run. Then run scripts/build-catalog.py.

usage: python3 scripts/fetch-trim-photos.py
"""
import io, os, re, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

BASE = "https://fmuyjfhucjtjzkweeqyd.supabase.co/storage/v1/object/public/vehicle-images/hero/hero_v1/"
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
os.makedirs("public/img/trims", exist_ok=True)

jobs = []
for l in open("scripts/trim-photos.txt").read().strip().split("\n"):
    if l.startswith("#"): continue
    make, model, _year, items = l.split("|")
    for item in filter(None, items.split(";")):
        trim, path = item.split("~")
        jobs.append((f"public/img/trims/{slug(make)}-{slug(model)}--{slug(trim)}.webp", path))

def fetch(job):
    out, path = job
    if os.path.exists(out): return None
    try:
        raw = urllib.request.urlopen(BASE + path, timeout=60).read()
        Image.open(io.BytesIO(raw)).convert("RGB").resize((560, 420), Image.LANCZOS).save(out, "WEBP", quality=78)
        return None
    except Exception as e:
        return f"{out}: {path}: {e}"

with ThreadPoolExecutor(2) as pool:
    failed = [r for r in pool.map(fetch, jobs) if r]
# Short failure lines only; a re-run picks up where this one stopped.
print(len(jobs), "trim photos listed;", len(failed), "failed")
for f in failed: print("FAILED", f)
sys.exit(1 if failed else 0)
