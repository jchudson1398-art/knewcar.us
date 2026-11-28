// Works out the slide 3 numbers with the website's own estimator (src/lib/estimate.ts), so the clip can never show
// a figure the estimator would not. Prints JSON for compose.py.
// usage: node scripts/cost-video/numbers.mjs      (run from the repo root)
import { readFileSync, writeFileSync, mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
import { transformSync } from "esbuild";

const dir = mkdtempSync(join(tmpdir(), "est-"));
writeFileSync(join(dir, "estimate.mjs"), transformSync(readFileSync("src/lib/estimate.ts", "utf8"), { loader: "ts", format: "esm" }).code);
const { estimate, feesFor, STATE_NAMES } = await import(pathToFileURL(join(dir, "estimate.mjs")).href);
const rates = JSON.parse(readFileSync("src/data/state-rates.json", "utf8"));
const catalog = JSON.parse(readFileSync("src/data/catalog.json", "utf8"));

// The vehicle: 2026 Toyota RAV4 XLE Premium. MSRP and weight come from the site catalog. The destination charge is
// not in the site files; it was read from the catalog database on 2026-11-28 (vehicle_msrp_history, verified).
const car = catalog.find((c) => c.key === "toyota-rav4");
const trim = car.trims.find((t) => t.name === "XLE Premium");
if (!trim?.msrp || !trim.lbMax) throw new Error("RAV4 XLE Premium is missing its MSRP or weight in the catalog");
const DESTINATION = 1595;
// California is shown for one named county (Jacob, 2026-11-28), because the statewide rate alone understates what
// most Californians pay. The county's combined rate comes from the state's own table in src/data/state-rates.json.
const COUNTY = { CA: "Los Angeles" };

const out = { vehicle: `${car.year} ${car.make} ${car.model} ${trim.name}`, msrp: trim.msrp, destination: DESTINATION, states: [] };
for (const state of process.argv.slice(2).length ? process.argv.slice(2) : ["TX", "VA", "FL"]) {
  const county = COUNTY[state] ?? null;
  const place = county ? rates[state].counties.find((c) => c.name === county) : null;
  if (county && !place) throw new Error(`${county} County is not in the ${state} rate table`);
  const input = { state, price: trim.msrp * 100, destination: DESTINATION * 100, tradeValue: 0, tradePayoff: 0, localCombinedRate: place ? place.combinedRate : null, flSurtaxRate: null,
    electric: false, hasPlateToTransfer: false, nyMctd: false, weightLb: trim.lbMax, weightBasis: trim.lbMin === trim.lbMax ? "manufacturer" : "approximate", truck: false, passengerCar: false };
  const e = estimate(input, feesFor(input, rates, county));
  out.states.push({ code: state, name: STATE_NAMES[state], county, combinedRate: place ? place.combinedRate : null, gross: e.gross, tax: e.taxTotal, fees: e.feesTotal, total: e.outTheDoor,
    taxLines: e.tax.map((l) => [l.label, l.amount, l.tag]), feeLines: e.fees.map((l) => [l.label, l.amount, l.tag]), notIncluded: e.notIncluded.map((l) => l.label) });
}
console.log(JSON.stringify(out, null, 1));
