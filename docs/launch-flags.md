# Launch flag log

Every item that was flagged while building the new knewcar.us, with what was done about it.
Status is one of: **Resolved** (fixed, nothing needed), **Needs Jacob** (a question only Jacob can answer),
**Open** (known, being worked, no answer needed yet).

Target: free version ready Tuesday 2026-11-24.

## Needs Jacob

| # | Flagged | What was flagged | What I need |
|---|---------|------------------|-------------|
| F-01 | 2026-11-18 | Real payments need a Stripe account connected to RevenueCat. None exists yet. | Open a Stripe account and connect it in RevenueCat. I will give exact steps. Blocks the paid upgrade only, not the free site. |
| F-02 | 2026-11-18 | Payments and "payment search" in the upgrade need one interest rate per credit range and loan length. | The rate table (you said you will provide it). Until then the estimator uses the rate the shopper types in. |
| F-03 | 2026-11-18 | The launch video on the home page still says "coming soon" and "in the works". | After launch that is wrong. Choose: recut the video without those words, or take the video off the home page at launch. |
| F-04 | 2026-11-18 | Terms and Privacy pages do not yet cover a website subscription. | Wording to be drafted by me, then reviewed by your attorney before real payments are switched on. |
| F-05 | 2026-11-18 | Per-trim photos and live prices need a new read-only view in the database. That is a database change. | Your explicit approval before it is applied. Until then the site uses a saved snapshot and one photo per model. |

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
