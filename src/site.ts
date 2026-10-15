// Site-wide settings. Change these in one place.

/**
 * Waitlist sign-ups go to Supabase: the form calls public.join_waitlist(email, zip, source), which is the only
 * thing this public key can do with the waitlist (vehicle-intelligence-platform
 * supabase/migrations/20261014200000_website_waitlist.sql). The publishable key is meant to be public.
 * Currently the Zone 2 SANDBOX project; switch both values to production when Jacob approves.
 */
export const SUPABASE_URL = "https://fmuyjfhucjtjzkweeqyd.supabase.co";
export const SUPABASE_PUBLISHABLE_KEY = "sb_publishable_UJp_9QSmhxb6jnk5U68TRQ_Zd17Doyk";
export const WAITLIST_ENDPOINT = `${SUPABASE_URL}/rest/v1/rpc/join_waitlist`;

/** Public contact address shown in the footer, Privacy and Terms. */
export const CONTACT_EMAIL = "jake@knewcar.us";

/** Launch prices (owner, 2026-10-14). */
export const PRICES = {
  monthly: "$19.99",
  pass: "$44.99",
  yearly: "$99.99",
} as const;

export const NAV = [
  { href: "/how-it-works", label: "How it works" },
  { href: "/pricing", label: "Pricing" },
  { href: "/how-it-works#faq", label: "FAQ" },
] as const;
