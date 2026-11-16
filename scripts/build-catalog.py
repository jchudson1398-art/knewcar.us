"""Builds src/data/catalog.json, the website's snapshot of the cars KnewCar shows.

Input: a rows file exported from the catalog (one line per model, latest model year with a published photo):
  make|model|year|body_style|trim_count|...   plus a JSON list of body categories in the same order, resolved
with the app's own rule (vehicle-intelligence-platform supabase/functions/_shared/catalog/body_category.ts).
Photos are saved separately as public/img/cars/<key>.webp. No prices, payments or offers are exported.

usage: python3 scripts/build-catalog.py rows.txt categories.json
"""
import json, re, sys

rows = [l.split("|") for l in open(sys.argv[1]).read().strip().split("\n")]
cats = json.load(open(sys.argv[2]))
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

# Powertrain: from the catalog where it records one, else from the manufacturer's own model name.
ELECTRIC = {"Honda Prologue", "Hyundai IONIQ 5", "Hyundai IONIQ 5 N", "Hyundai IONIQ 9", "Toyota bZ", "Toyota bZ Woodland",
            "Toyota C-HR", "Volkswagen ID.4",
            # Electric-only models whose powertrain the catalog does not record yet:
            "Chevrolet Bolt", "Nissan Nissan LEAF", "Ford Mustang Mach-E", "Subaru Solterra", "Subaru Trailseeker",
            "Subaru Uncharted", "Jeep Jeep Recon"}
HYBRID = {"Honda Prelude", "Toyota Camry", "Toyota Land Cruiser", "Toyota Prius", "Toyota RAV4", "Toyota Sequoia",
          "Toyota Sienna", "Toyota Toyota Crown", "Toyota Toyota Crown Signia"}
HYBRID_AVAILABLE = {"Ford Maverick", "Honda Accord", "Honda Civic", "Honda CR-V", "Mazda CX-50", "Mazda CX-70",
                    "Mazda CX-90", "Toyota 4Runner", "Toyota Corolla", "Toyota Corolla Cross", "Toyota Grand Highlander",
                    "Toyota Highlander", "Toyota Tacoma", "Toyota Tundra"}

def fuel(make, model):
    full = f"{make} {model}"
    if full in ELECTRIC or re.search(r"(^| )EV\d*( |$)|^EV\d", model): return "Electric"
    if full in HYBRID or re.search(r"hybrid|i-force max", model, re.I): return "Hybrid"
    if full in HYBRID_AVAILABLE: return "Hybrid available"
    return None

out = []
for (make, model, year, _bs, ntrims, *_), cat in zip(rows, cats):
    display = model[len(make) + 1:] if model.lower().startswith(make.lower() + " ") else model
    out.append({"key": f"{slug(make)}-{slug(model)}", "make": make, "model": display, "year": int(year),
                "type": cat, "fuel": fuel(make, model), "trims": int(ntrims)})
json.dump(out, open("src/data/catalog.json", "w"), indent=1)
print(len(out), "models;", sorted({c["type"] or "none" for c in out}))
