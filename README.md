# knewcar.us — KnewCar website

The public site for knewcar.us: Home, How it works + FAQ, Pricing, Privacy, Terms. Built with Astro as a static site.

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

## Waitlist

"Join the beta" calls `public.join_waitlist(email, zip, source)` in Supabase with the publishable (public) key.
The table and function are defined in vehicle-intelligence-platform
`supabase/migrations/20261014200000_website_waitlist.sql`. The site currently points at the Zone 2 sandbox;
switch `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` in `src/site.ts` to production at launch.

## Before going live

- Privacy and Terms are drafts and must be reviewed by an attorney; then remove the "Draft for review" notes.
- Apply the waitlist migration to production and point `src/site.ts` at it.
