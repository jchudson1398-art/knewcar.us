# knewcar.us — KnewCar website

The public site for knewcar.us: Home, Explore (search every model), How it works + FAQ, Pricing, Privacy, Terms. Built with Astro as a static site.

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

Home and Explore list one card per model from a snapshot, not a live query: the catalog tables are not readable
by logged-out visitors. `src/data/catalog.json` holds make, model, latest model year, body type and powertrain for
the eleven brands the app shows; `public/img/cars/<key>.webp` is each model's published card photo at 560px. The
site shows no prices, payments or offers. To refresh after the catalog changes, export the rows and body categories
again and run `python3 scripts/build-catalog.py rows.txt categories.json` (the script's header explains the input),
then replace the photos.

## Waitlist

"Join the beta" calls `public.join_waitlist(email, zip, source)` in Supabase with the publishable (public) key.
The table and function are defined in vehicle-intelligence-platform
`supabase/migrations/20261014200000_website_waitlist.sql`. The site currently points at the Zone 2 sandbox;
switch `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` in `src/site.ts` to production at launch.

## Before going live

- Privacy and Terms are live without draft notes (Jacob, 2026-10-16); an attorney review is still owed.
- Apply the waitlist migration to production and point `src/site.ts` at it.
