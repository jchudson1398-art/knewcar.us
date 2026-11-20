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
  fixed: { label: string; amount: number; note?: string; tag?: Tag }[];
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
    pushLocal(tax, notIncluded, basis, rate, input.localCombinedRate, "sales tax");
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

  const feeLines: Line[] = fees.fixed.map((f) => ({ label: f.label, amount: Math.round(f.amount * 100), tag: f.tag ?? ("verified" as Tag), note: f.note }));
  feeLines.push({ label: "Dealer documentary fee", amount: doc, tag: "estimate", note: "Planning estimate. Your dealer's fee may differ." });
  for (const f of fees.notIncluded) notIncluded.push({ label: f.label, amount: null, tag: "not_included", note: f.note });

  const sum = (ls: Line[]) => ls.reduce((n, l) => n + (l.amount ?? 0), 0);
  const taxTotal = sum(tax);
  const feesTotal = sum(feeLines);
  return { gross, tax, fees: feeLines, taxTotal, feesTotal, outTheDoor: gross + taxTotal + feesTotal, notIncluded, notes };
}

// ---- Government fees -------------------------------------------------------------------------------------------
// Amounts are read from src/data/state-rates.json (extracted from the research on 2026-11-20). A fee that depends
// on something the website does not know yet (vehicle weight, MPG, county fee schedules) is listed as not included.

export interface RatesFile {
  CA: { fees: { registration: { amount: number }; chp: { amount: number }; vlfPercentOfPrice: number; transportationImprovementFee: { valueFrom: number; valueTo: number | null; fee: number }[]; smogAbatement: { amount: number }; tireFeePerTire: number; tiresCharged: number; plate: number } };
  NY: { fees: { title: number; plates: number; tireFeePerTire: number; tiresCharged: number; mctdFeeTwoYears: number; countyUseTaxTwoYears: { county: string; amount: number; amountOver3500lb: number }[] } };
  FL: { fees: { title: number; newPlate: number; initialRegistration: number; tempTag: number; tireFeePerTire: number } };
  VA: { fees: { titleDmv: number; titleCode: number; highwayUseFeeEv: number } };
}

export function feesFor(input: EstimateInput, data: RatesFile, county: string | null): StateFees {
  const fixed: StateFees["fixed"] = [];
  const notIncluded: StateFees["notIncluded"] = [];
  const dollars = input.price / 100;

  if (input.state === "TX") {
    fixed.push({ label: "Title and registration", amount: 300, tag: "estimate", note: "Planning estimate for both together." });
  }

  if (input.state === "CA") {
    const f = data.CA.fees;
    fixed.push({ label: "Registration fee", amount: f.registration.amount });
    fixed.push({ label: "California Highway Patrol fee", amount: f.chp.amount });
    fixed.push({ label: `Vehicle license fee (${f.vlfPercentOfPrice}% of the price)`, amount: Math.round(dollars * f.vlfPercentOfPrice) / 100, tag: "estimate", note: "The DMV reads this from a price table, so the exact amount may differ slightly. Charged again every year." });
    const tier = f.transportationImprovementFee.find((t) => dollars >= t.valueFrom && (t.valueTo === null || dollars < t.valueTo + 1));
    if (tier) fixed.push({ label: "Transportation improvement fee", amount: tier.fee, note: "Set by the vehicle's price." });
    if (input.electric) notIncluded.push({ label: "Smog abatement fee", note: `We have not confirmed whether an electric vehicle pays the $${f.smogAbatement.amount} fee.` });
    else fixed.push({ label: "Smog abatement fee", amount: f.smogAbatement.amount });
    fixed.push({ label: "Tire fee", amount: f.tireFeePerTire * f.tiresCharged, tag: "estimate", note: `$${f.tireFeePerTire} a tire, counting four tires and a spare.` });
    fixed.push({ label: "License plate fee", amount: f.plate });
    notIncluded.push({ label: "County fees", note: "Small fees that differ by county." });
    notIncluded.push({ label: "Title fee", note: "We have not confirmed the title fee on a new registration." });
    notIncluded.push({ label: "Weight fee", note: "Pickups pay an extra fee by weight." });
  }

  if (input.state === "VA") {
    const f = data.VA.fees;
    notIncluded.push({ label: "Title fee", note: `The DMV lists $${f.titleDmv}; the Code of Virginia lists $${f.titleCode}.` });
    notIncluded.push({ label: "Registration fee", note: "$30.75 or $35.75 a year, by vehicle weight. Higher for heavier vehicles and some pickups." });
    if (input.electric) fixed.push({ label: "Highway use fee, electric vehicle", amount: f.highwayUseFeeEv, note: "Yearly. This amount is in effect through June 30, 2027." });
    else notIncluded.push({ label: "Highway use fee", note: "Charged on fuel-efficient vehicles (25 MPG and up), by MPG." });
    notIncluded.push({ label: "Local vehicle license fee", note: "Set by your county or city." });
  }

  if (input.state === "NY") {
    const f = data.NY.fees;
    fixed.push({ label: "Title certificate fee", amount: f.title });
    fixed.push({ label: "License plates", amount: f.plates });
    fixed.push({ label: "Waste tire fee", amount: f.tireFeePerTire * f.tiresCharged, tag: "estimate", note: `$${f.tireFeePerTire.toFixed(2)} a tire, counting four tires and a spare.` });
    if (input.nyMctd) fixed.push({ label: "Commuter transportation district fee", amount: f.mctdFeeTwoYears, note: "For two years." });
    notIncluded.push({ label: "Registration fee", note: "$26 to $140 for two years, by vehicle weight." });
    const use = county ? f.countyUseTaxTwoYears.find((c) => c.county === county) : undefined;
    if (use) notIncluded.push({ label: "County vehicle use tax", note: use.amount === use.amountOver3500lb ? `$${use.amount} for two years.` : `$${use.amount} or $${use.amountOver3500lb} for two years, by vehicle weight.` });
    else if (!county) notIncluded.push({ label: "County vehicle use tax", note: "Up to $60 for two years in some counties. Choose your county." });
    notIncluded.push({ label: "Inspection", note: "Up to $10." });
  }

  if (input.state === "FL") {
    const f = data.FL.fees;
    fixed.push({ label: "Title fee", amount: f.title, note: "Electronic title, no loan. Add $2 with a loan." });
    if (!input.hasPlateToTransfer) {
      fixed.push({ label: "Initial registration fee", amount: f.initialRegistration, note: "Charged when you have no Florida plate to transfer." });
      fixed.push({ label: "New license plate", amount: f.newPlate });
    }
    fixed.push({ label: "Temporary tag", amount: f.tempTag });
    notIncluded.push({ label: "Registration fee", note: "$27.60 to $45.60 a year, by vehicle weight." });
    notIncluded.push({ label: "Tire fee", note: `$${f.tireFeePerTire} for each new tire.` });
  }

  return { fixed, notIncluded };
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
