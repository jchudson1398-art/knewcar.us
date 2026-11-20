// Tax and fee estimate for a new-car purchase, for the website upgrade.
//
// One calculator, one set of facts per state. Every fact comes from the official-source research in the platform
// repository (docs/evidence/state-tax-fee/*-2026-11-16) or is a planning number Jacob approved on 2026-11-17.
// Rules that research could not confirm are never guessed: the line is returned with amount null and the tag
// "not_included", so the page can say so. Money is whole cents throughout.

export type StateCode = "TX" | "CA" | "VA" | "NY" | "FL";
export type Tag = "verified" | "assumed" | "estimate" | "not_included";

export interface Line {
  label: string;
  /** Cents. null means the amount is not part of the total. */
  amount: number | null;
  tag: Tag;
  note?: string;
}

export interface EstimateInput {
  state: StateCode;
  /** Vehicle price in cents (MSRP or agreed price), before destination. */
  price: number;
  destination: number;
  tradeValue: number;
  tradePayoff: number;
  /** Combined state and local rate, in percent, for the shopper's county or city. null when none is chosen. */
  localCombinedRate: number | null;
  /** Florida only: the county surtax rate in percent. null when no county is chosen. */
  flSurtaxRate: number | null;
  electric: boolean;
  /** Florida only: the shopper has a Florida plate to transfer. */
  hasPlateToTransfer: boolean;
  /** New York only: the county is in the Metropolitan Commuter Transportation District. */
  nyMctd: boolean;
}

export interface Estimate {
  gross: number;
  tax: Line[];
  fees: Line[];
  taxTotal: number;
  feesTotal: number;
  outTheDoor: number;
  /** Lines left out of the total because the rule or an input is not confirmed. */
  notIncluded: Line[];
  notes: string[];
}

/** Planning numbers for the dealer documentary fee, approved by Jacob Hudson on 2026-11-17. Estimates. */
export const DOC_FEE: Record<StateCode, number> = { TX: 22500, CA: 8500, VA: 85000, NY: 17500, FL: 99500 };

export const STATE_NAMES: Record<StateCode, string> = {
  TX: "Texas",
  CA: "California",
  VA: "Virginia",
  NY: "New York",
  FL: "Florida",
};

/** State rates in percent. */
const STATE_RATE: Record<StateCode, number> = { TX: 6.25, CA: 7.25, VA: 4.15, NY: 4, FL: 6 };

/** Exact percent of a cents amount: the rate is carried as thousandths of a percent. */
export const pct = (cents: number, rate: number) => Math.round((cents * Math.round(rate * 1000)) / 100000);

const usd = (cents: number) => `$${(cents / 100).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

export interface StateFees {
  /** Fixed government fees that apply to every new purchase, in dollars. */
  fixed: { label: string; amount: number; note?: string }[];
  /** Government fees that could not be worked out here, with the reason. */
  notIncluded: { label: string; note: string }[];
}

export function estimate(input: EstimateInput, fees: StateFees): Estimate {
  const { state, price, destination, tradeValue, tradePayoff } = input;
  const gross = price + destination;
  const doc = DOC_FEE[state];
  const tax: Line[] = [];
  const notIncluded: Line[] = [];
  const notes: string[] = [];
  const rate = STATE_RATE[state];
  const hasTrade = tradeValue > 0;
  let basis = 0;

  if (state === "TX") {
    // Tax on price with destination, less the trade-in's value. Doc fee is not taxed.
    basis = Math.max(0, gross - tradeValue);
    tax.push({ label: `Texas motor vehicle tax (${rate}%)`, amount: pct(basis, rate), tag: "verified", note: "State tax, included" });
    tax.push({ label: "Local tax", amount: 0, tag: "verified", note: "None on vehicles in Texas" });
    if (hasTrade) notes.push("Texas taxes the price with destination, less your trade-in's value.");
  }

  if (state === "CA" || state === "VA") {
    // Doc fee is taxed. A trade-in does not reduce the tax. Whether destination is taxed is not confirmed.
    basis = price + doc;
    if (destination > 0) {
      notIncluded.push({
        label: "Tax on the destination charge",
        amount: null,
        tag: "not_included",
        note: `We have not confirmed from official sources whether ${STATE_NAMES[state]} taxes the destination charge. If it does, add about ${usd(pct(destination, input.localCombinedRate ?? rate))}.`,
      });
    }
    if (hasTrade) notes.push(`${STATE_NAMES[state]} does not reduce sales tax for a trade-in. Your trade-in still lowers what you finance.`);
  }

  if (state === "CA") {
    tax.push({ label: `California sales tax, statewide (${rate}%)`, amount: pct(basis, rate), tag: "verified", note: "State tax, included" });
    pushLocal(tax, notIncluded, basis, rate, input.localCombinedRate, "district tax");
    notes.push("California taxes the dealer documentary fee, so it is part of the taxed amount.");
  }

  if (state === "VA") {
    const amount = Math.max(pct(basis, rate), 7500);
    tax.push({ label: `Virginia motor vehicle sales and use tax (${rate}%, $75 minimum)`, amount, tag: "verified", note: "State tax, included" });
    tax.push({ label: "Local sales tax", amount: 0, tag: "verified", note: "None on vehicles in Virginia" });
    notes.push("Virginia counties and cities charge a yearly personal property tax on vehicles. It is not part of the purchase and is not shown here.");
  }

  if (state === "NY") {
    // Destination is taxed, the doc fee is not. A trade-in is deducted, but whether a trade-in with a loan is
    // counted at full value or at equity is not confirmed, so that case is left out.
    const deduct = hasTrade && tradePayoff === 0 ? tradeValue : 0;
    basis = Math.max(0, gross - deduct);
    if (hasTrade && tradePayoff > 0) {
      notIncluded.push({
        label: "Tax savings from your trade-in",
        amount: null,
        tag: "not_included",
        note: "New York reduces tax for a trade-in, but we have not confirmed whether a trade-in with a loan counts at its full value or only your equity. No reduction is applied, so the real tax may be lower.",
      });
    } else if (hasTrade) {
      notes.push("New York taxes the price with destination, less your trade-in's value.");
    }
    tax.push({ label: `New York State sales tax (${rate}%)`, amount: pct(basis, rate), tag: "verified", note: "State tax, included" });
    pushLocal(tax, notIncluded, basis, rate, input.localCombinedRate, "local sales tax");
  }

  if (state === "FL") {
    // Destination and the doc fee are taxed. Official sources conflict on how a trade-in is measured.
    basis = gross + doc;
    if (hasTrade) {
      notIncluded.push({
        label: "Tax savings from your trade-in",
        amount: null,
        tag: "not_included",
        note: "Florida reduces tax for a trade-in, but official sources disagree on how the trade-in is measured. No reduction is applied, so the real tax may be lower.",
      });
    }
    tax.push({ label: `Florida sales tax (${rate}%)`, amount: pct(basis, rate), tag: "verified", note: "State tax, included" });
    if (input.flSurtaxRate === null) {
      notIncluded.push({ label: "County surtax", amount: null, tag: "not_included", note: "Choose your county to add it. It is at most 2% of the first $5,000, so no more than $100." });
    } else {
      tax.push({
        label: `County surtax (${input.flSurtaxRate}% of the first $5,000)`,
        amount: pct(Math.min(basis, 500000), input.flSurtaxRate),
        tag: "assumed",
        note: "Local tax, assumed from your county, not verified",
      });
    }
    notes.push("Florida taxes the dealer fee, so it is part of the taxed amount.");
  }

  const feeLines: Line[] = fees.fixed.map((f) => ({ label: f.label, amount: Math.round(f.amount * 100), tag: "verified" as Tag, note: f.note }));
  feeLines.push({ label: "Dealer documentary fee", amount: doc, tag: "estimate", note: "Planning estimate. Your dealer's fee may differ." });
  for (const f of fees.notIncluded) notIncluded.push({ label: f.label, amount: null, tag: "not_included", note: f.note });

  const sum = (ls: Line[]) => ls.reduce((n, l) => n + (l.amount ?? 0), 0);
  const taxTotal = sum(tax);
  const feesTotal = sum(feeLines);
  return { gross, tax, fees: feeLines, taxTotal, feesTotal, outTheDoor: gross + taxTotal + feesTotal, notIncluded, notes };
}

/** Local tax from the published combined rate for the shopper's county or city. Labeled as assumed. */
function pushLocal(tax: Line[], notIncluded: Line[], basis: number, stateRate: number, combined: number | null, name: string) {
  if (combined === null) {
    notIncluded.push({ label: `Local ${name}`, amount: null, tag: "not_included", note: "Choose your county to add it." });
    return;
  }
  const local = Math.round((combined - stateRate) * 1000) / 1000;
  tax.push({
    label: `Local ${name} (${local}%)`,
    amount: pct(basis, local),
    tag: "assumed",
    note: "Local tax, assumed from your county, not verified",
  });
}
