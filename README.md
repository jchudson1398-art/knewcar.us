# knewcar.us — KnewCar website

The public site for knewcar.us: Home, Explore (search every model), a page per car with its trims, How it works + FAQ, Pricing, Privacy, Terms. Built with Astro as a static site.

## Run it locally

```
npm install
npm run dev      # http://localhost:4321
npm run build    # static files in dist/
```

## Where things are

- `src/site.ts`: prices, contact email, and the Supabase project the waitlist form uses.
- `src/pages/`: one file per page.
- `src/components/`: header, footer, phone frame, waitlist form, icons.
- `public/img/`: app screenshots, the mountain photo, and the social share image.
- `public/img/cars/`, `src/data/catalog.json`: the car snapshot the Home and Explore grids use (below).
- `public/img/app/`, `public/video/`: the app screens in the home slider and the launch video.

## Car catalog snapshot

Home, Explore and the car pages (`/cars/<make-model>/`) come from a snapshot, not a live query: the catalog tables
are not readable by logged-out visitors. `src/data/catalog.json` holds, for the eleven brands the app shows, each
model's make, latest model year, body type, powertrain, the trims of that year with their drivetrains and verified MSRP (destination excluded), and how many
configurations the app has for the model. `public/img/cars/<key>.webp` is each model's published card photo at
560px. The site shows MSRP only; no offers.

To refresh after the catalog changes, re-export `scripts/catalog-rows.txt`, `scripts/catalog-categories.json` and
`scripts/trims.txt` and `scripts/msrp.txt` (formats are in each file and in the script header), run
`python3 scripts/build-catalog.py scripts/catalog-rows.txt scripts/catalog-categories.json`, and replace the photos.

## Free site and website upgrade

Free: browse, search, every trim, verified MSRP and search by MSRP. Website upgrade ($2.99/mo or $19.99/yr, set in
`src/site.ts` as `WEB_PLAN`): saved cars (`/saved`), compare (`/compare`), and the tax, fee and payment estimator
(`/estimate`, Texas only, using the approved Texas rule: 6.25% on price less trade-in value, $225 documentary fee
and $300 title and registration as estimates). `/sign-in` uses the same Supabase accounts as the app.

**Not finished, on purpose:** `PAYMENTS_LIVE` is false. Until RevenueCat web checkout and a server-side entitlement
check exist, the upgrade is a flag in the visitor's browser set by a "test access" button on `/upgrade`, and saved
and compare lists live in that browser only (`src/lib/plus.ts`). Do not treat this as access control.

## Waitlist

"Join the beta" calls `public.join_waitlist(email, zip, source)` in Supabase with the publishable (public) key.
The table and function are defined in vehicle-intelligence-platform
`supabase/migrations/20261014200000_website_waitlist.sql`. The site currently points at the Zone 2 sandbox;
switch `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` in `src/site.ts` to production at launch.

## Before going live

- Privacy and Terms are live without draft notes (Jacob, 2026-10-16); an attorney review is still owed.
- Apply the waitlist migration to production and point `src/site.ts` at it.
