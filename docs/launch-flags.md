# Launch flag log

Every item that was flagged while building the new knewcar.us, with what was done about it.
Status is one of: **Resolved** (fixed, nothing needed), **Needs Jacob** (a question only Jacob can answer),
**Open** (known, being worked, no answer needed yet).

Target: free version ready Tuesday 2026-11-24.

## Needs Jacob

| # | Flagged | What was flagged | What I need |
|---|---------|------------------|-------------|
| F-01 | 2026-11-18 | Real payments need a Stripe account connected to RevenueCat. None exists yet. | Jacob (2026-11-18): no time yet, maybe tonight. Opening a Stripe account has no setup or monthly charge; Stripe keeps 2.9% + 30 cents of each card payment. Blocks the paid upgrade only, not the free site. |
| F-02 | 2026-11-18 | Payments and "payment search" in the upgrade need one interest rate per credit range and loan length. | Jacob (2026-11-18): build the table from the rates the app already has. Proposed table sent for his choice (Experian averages by credit range, or the app's per-loan-length method). Until chosen, the estimator uses the rate the shopper types in. |
| F-11 | 2026-11-18 | RevenueCat's own pages disagree on whether web purchases carry an extra RevenueCat charge (one says none, one says the usual 1% above $2,500 a month). | Check the charge shown in your RevenueCat account when connecting Stripe. |
| F-12 | 2026-11-18 | The app's lender rate observations were last collected 2026-10-13. The app's own rule treats rates older than 14 days as too old. | Decide whether to refresh them before the website uses them. Affects the app's standard rate too. |
| F-04 | 2026-11-18 | Terms and Privacy pages do not yet cover a website subscription. | Jacob agreed 2026-11-18: I draft the wording, his attorney reviews it before real payments are switched on. Draft not written yet. |

## Open

| # | Flagged | What was flagged | Plan |
|---|---------|------------------|------|
| F-06 | 2026-11-18 | 9 of 145 models have no verified MSRP. | They show "MSRP in the app" instead of a price, and are left out of price searches. No price is guessed. |
| F-07 | 2026-11-18 | The upgrade is unlocked by a test button, and saved/compare lists live only in the browser. | Replaced by real checkout and account storage in the payments step. `PAYMENTS_LIVE` stays off until then. |
| F-08 | 2026-11-18 | App screenshots on the site show details from a demo account. | Check each screenshot before launch; retake any that show something that should not be public. |
| F-09 | 2026-11-16 | State tax research has open facts (examples: whether destination is taxed in CA and VA; CA doc fee cap; VA title fee; trade-in with a loan in NY and FL). | The calculator shows only verified lines. A line that depends on an open fact is marked "not confirmed, not included". Full lists are in each state's RESEARCH.md in the platform repo. |
| F-10 | 2026-11-18 | Local tax by ZIP needs a ZIP-to-county rate table for CA, NY, VA, FL. | Use each state's published rate table; label the result "assumed, not verified" as decided. |

## Resolved

| # | Flagged | What was flagged | Resolution |
|---|---------|------------------|------------|
| R-01 | 2026-11-18 | Home page slideshow was too tall on a phone (shopping tool was more than a full screen down). | Tightened the phone layout; search bar now starts about one screen down. |
| R-02 | 2026-11-18 | Car cards on the "Every trim" slide overlapped and cut off car names. | Changed to a clean three-card layout with no overlap. |
| R-03 | 2026-11-18 | F-03: the launch video said "coming soon" and "in the works". | Jacob: take it off. Reworded to "now live" in both the wide video and the reel. |
| R-04 | 2026-11-18 | F-05: a photo for every trim seemed to need a database change. | Not needed. The photos are already public in the sandbox; the site only lacked the list of which photo belongs to which trim. That list is exported into the site's snapshot, with no change to the database. The snapshot must be re-exported when the catalog changes. |
