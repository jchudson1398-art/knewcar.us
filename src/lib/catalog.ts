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
  trims: number;
}

export const CATALOG = data as Car[];

export const carName = (c: Car) => `${c.year} ${c.make} ${c.model}`;
export const carImage = (c: Car) => `/img/cars/${c.key}.webp`;

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
