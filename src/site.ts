// Site-wide settings. Change these in one place.

/**
 * Waitlist sign-ups go to Supabase: the form calls public.join_waitlist(email, zip, source), which is the only
 * thing this public key can do with the waitlist (vehicle-intelligence-platform
 * supabase/migrations/20261014200000_website_waitlist.sql). The publishable key is meant to be public.
 * This is the launch environment (vehicle-intelligence-platform-sandbox, Jacob 2026-10-15): there is no separate
 * production project to switch to.
 */
export const SUPABASE_URL = "https://fmuyjfhucjtjzkweeqyd.supabase.co";
export const SUPABASE_PUBLISHABLE_KEY = "sb_publishable_UJp_9QSmhxb6jnk5U68TRQ_Zd17Doyk";
export const WAITLIST_ENDPOINT = `${SUPABASE_URL}/rest/v1/rpc/join_waitlist`;

/** KnewCar on the App Store (live 2026-11-06). */
export const APP_STORE_URL = "https://apps.apple.com/us/app/knewcar/id6822044416";

/** Public contact address shown in the footer, Privacy and Terms. */
export const CONTACT_EMAIL = "jake@knewcar.us";

/** Launch prices (owner, 2026-10-14). */
export const PRICES = {
  monthly: "$19.99",
  pass: "$44.99",
  yearly: "$99.99",
} as const;

/** Website upgrade plan (owner, 2026-11-16; yearly price changed to $19.99 on 2026-11-18). Separate from the app's plans in PRICES. */
export const WEB_PLAN = { monthly: "$2.99", yearly: "$19.99" } as const;
/** False until RevenueCat web checkout is connected: the upgrade page then offers a test unlock, no charge. */
export const PAYMENTS_LIVE = false;

export const NAV = [
  { href: "/explore", label: "Explore" },
  { href: "/how-it-works", label: "How it works" },
  { href: "/upgrade", label: "Upgrade" },
  { href: "/pricing", label: "App pricing" },
  { href: "/how-it-works#faq", label: "FAQ" },
] as const;
