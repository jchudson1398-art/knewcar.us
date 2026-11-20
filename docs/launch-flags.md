# Launch flag log

Every item that was flagged while building the new knewcar.us, with what was done about it.
Status is one of: **Resolved** (fixed, nothing needed), **Needs Jacob** (a question only Jacob can answer),
**Open** (known, being worked, no answer needed yet).

Target: free version ready Tuesday 2026-11-24.

## Needs Jacob

| # | Flagged | What was flagged | What I need |
|---|---------|------------------|-------------|
| F-01 | 2026-11-18 | Real payments need a Stripe account connected to RevenueCat. None exists yet. | Jacob (2026-11-18): no time yet, maybe tonight. Opening a Stripe account has no setup or monthly charge; Stripe keeps 2.9% + 30 cents of each card payment. Blocks the paid upgrade only, not the free site. |
| F-15 | 2026-11-20 | LOCKED NEXT STEP (Jacob, 2026-11-20): as soon as the new website is posted, rework the app's rate estimate to use the website's rate table. Not started; the app's current method is a locked decision, so the rework needs Jacob's go-ahead at that time, a decision record and re-testing. Also written in the platform repo's website launch roadmap. | Nothing now. I raise it the first working session after launch. |
| F-11 | 2026-11-18 | RevenueCat's own pages disagree on whether web purchases carry an extra RevenueCat charge (one says none, one says the usual 1% above $2,500 a month). | Check the charge shown in your RevenueCat account when connecting Stripe. |
| F-12 | 2026-11-18 | The app's own stored lender rates are still from 2026-10-13. I collected fresh ones on 2026-11-19 for the website only and did not write them into the database. | Say so if you want the fresh rates saved into the app's database too. That is a data change and needs your go-ahead. |
| F-04 | 2026-11-18 | Terms and Privacy pages do not yet cover a website subscription. | Jacob agreed 2026-11-18: I draft the wording, his attorney reviews it before real payments are switched on. Draft not written yet. |
| F-13 | 2026-11-18 | The launch video shows a row of car photos that appears to include a GMC. GMC is hidden in the app. | Is it fine for a GMC to appear in the video, or should I swap that photo? |
| F-16 | 2026-11-20 | Estimator: local tax is chosen by county from a list, not looked up from a ZIP. The ZIP-to-county file is on the Census site, which this session cannot reach. | Approve access to the Census site when I ask, and I will add the ZIP lookup. Until then the shopper picks a county. |
| F-17 | 2026-11-20 | Estimator: registration fees in VA, NY and FL depend on vehicle weight, which the catalog does not have. They are listed under "Not included" with the published range. | Decided earlier: weight comes from manufacturer specs. Not started. Say if you want an optional "vehicle weight" box in the meantime. |
| F-18 | 2026-11-20 | Estimator: government fees change on 2027-01-01 in California (registration, highway patrol, improvement fee) and Florida's 2027 county surtax table is not published yet. The page uses 2026 amounts. | Nothing now. I must update the data file before January 1. |
| F-19 | 2026-11-20 | Estimator: California county rates are for areas outside city limits. Many cities charge more (up to 11.75%), so the assumed local tax can be low for city addresses. The page says so. | Tell me if you want cities added to the list (about 500 more entries). |

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
| R-05 | 2026-11-18 | F-14: trim photos were only on 4 of 11 brands. | Jacob approved the read-only export. All 739 trims across the 11 brands now have their own photo; each brand's list was checked as an exact copy. |
| R-06 | 2026-11-19 | F-02 (part): which rate table to use. | Jacob chose the app's method (a starting rate per loan length plus Experian's credit-range gap). Built into the estimator for 60 and 72 months from rates collected 2026-11-19; sources are in `src/data/rates.json`. |
| R-07 | 2026-11-19 | F-02: 36, 48 and 84 month loans had no rate estimate. | Jacob changed the method: Experian's average per credit range, adjusted for loan length by what Navy Federal, Consumers Credit Union and Capital One advertise. All five loan lengths now have an estimate. Numbers and sources are in `src/data/rates.json`. |
| R-08 | 2026-11-20 | F-02: which loan length Experian's average stands for. | Jacob confirmed 60 months. |
| R-09 | 2026-11-20 | The Pricing and How it works pages described only the app, with nothing saying so, next to a website that is now free to browse. | Labeled both pages as about the app (iPhone, Texas), added links to the free website and the website upgrade, and stated that app plans include the website upgrade (decided 2026-11-18). |
| R-10 | 2026-11-20 | Phone and computer check of all 15 page types: no errors, no sideways scrolling, 156 internal links all working. One button (Clear search) was slightly too short to tap comfortably. | Made it full tap height. |
| R-11 | 2026-11-20 | The estimator worked for Texas only. | Built for Texas, California, Virginia, New York and Florida purchases. State tax verified, local tax assumed from the county and labeled, fixed government fees from the research, approved doc fees. Anything not confirmed is listed as not included and never guessed: destination tax in CA and VA, trade-in with a loan in NY, any trade-in in FL. Tested on a phone for all five states. |
| R-12 | 2026-11-20 | Four tax rules were open in the research: destination tax in CA and VA; trade-in with a loan in NY; how FL measures a trade-in. | Jacob ruled on all four (2026-11-20): CA and VA tax the destination charge; NY taxes the new vehicle less the trade-in's value; FL taxes the purchase price less the trade allowance. The estimator now applies them. These rest on Jacob's ruling; the research did not confirm them from an official page, so the official citation for each is still to be attached. |
| R-13 | 2026-11-20 | County fees and title fees: scrape every county now, or later? | Later. State tax, county sales tax and state fees first. The per-county fees are small (a few dollars to about $60) and stay listed as not included. |
