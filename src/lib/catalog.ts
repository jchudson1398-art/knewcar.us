// The cars the website shows: a snapshot of the KnewCar catalog (scripts/build-catalog.py). One entry per model,
// with its body type and powertrain. No prices, payments or offers: those live in the app.
import data from "../data/catalog.json";

export interface Car {
  key: string;
  make: string;
  model: string;
  year: number;
  type: string | null;
  fuel: string | null;
  /** How many configurations (trim, drivetrain, body) of this model the app has, across its model years. */
  configs: number;
  /** Model years in the app, newest first. */
  years: number[];
  /** Trims of the newest model year, with the drivetrains each comes in when the catalog records them. */
  /** lbMin/lbMax: lightest and heaviest published curb weight in pounds. lbThird: from a third-party source. */
  trims: { name: string; drive: string[]; msrp: number | null; photo?: boolean; lbMin?: number; lbMax?: number; lbThird?: boolean }[];
  /** Lowest and highest verified MSRP across those trims (destination excluded); null when none is verified. */
  msrpFrom: number | null;
  msrpTo: number | null;
}

export const CATALOG = data as Car[];

export const carName = (c: Car) => `${c.year} ${c.make} ${c.model}`;
export const CONFIG_TOTAL = CATALOG.reduce((n, c) => n + c.configs, 0);
export const carUrl = (c: Car) => `/cars/${c.key}/`;
export const configsLabel = (n: number) => `${n} ${n === 1 ? "configuration" : "configurations"} in the app`;
export const money = (n: number) => `$${n.toLocaleString("en-US")}`;
export const priceLabel = (c: Car) => (c.msrpFrom ? `From ${money(c.msrpFrom)} MSRP` : "MSRP in the app");
export const carImage = (c: Car) => `/img/cars/${c.key}.webp`;
const trimSlug = (s: string) => s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
/** The trim's own photo when one was exported, else the model's photo. */
export const trimImage = (c: Car, t: Car["trims"][number]) => (t.photo ? `/img/trims/${c.key}--${trimSlug(t.name)}.webp` : carImage(c));

/** Words a shopper might type for each kind of car, added to what search matches. */
const ALSO: Record<string, string> = {
  Truck: "pickup",
  SUV: "crossover",
  Minivan: "van family",
  Convertible: "sports",
  Coupe: "sports",
  Electric: "ev",
  Hybrid: "hybrid",
  "Hybrid available": "hybrid",
};

/** Lower-case text that search matches against. */
export const carSearchText = (c: Car) =>
  [c.make, c.model, c.year, c.type, c.fuel, ALSO[c.type ?? ""], ALSO[c.fuel ?? ""]].filter(Boolean).join(" ").toLowerCase();

export const FILTERS = ["All", "SUV", "Truck", "Sedan", "Hatchback", "Minivan", "Coupe", "Convertible", "Van", "Electric", "Hybrid"] as const;
