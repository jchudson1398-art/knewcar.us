// Browser-side state for the website upgrade: whether this visitor has it, and their saved and compare lists.
//
// TEMPORARY while payments are not connected (PAYMENTS_LIVE = false in src/site.ts): the upgrade is a flag in this
// browser set by the test unlock on /upgrade, and lists are kept in this browser only. When RevenueCat checkout
// and server-side entitlements exist, isPlus() must ask the server and the lists must move to the account.
const PLUS = "kc_plus";
const read = (k: string): string[] => {
  try { return JSON.parse(localStorage.getItem(k) ?? "[]"); } catch { return []; }
};
const write = (k: string, v: string[]) => {
  try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* storage unavailable: nothing is kept */ }
};

export const isPlus = (): boolean => {
  try { return localStorage.getItem(PLUS) === "1"; } catch { return false; }
};
export const setPlus = (on: boolean) => {
  try { on ? localStorage.setItem(PLUS, "1") : localStorage.removeItem(PLUS); } catch { /* ignore */ }
};

export const saved = () => read("kc_saved");
export const compared = () => read("kc_compare");
const toggle = (k: string, key: string, limit = 0): boolean => {
  const list = read(k);
  const i = list.indexOf(key);
  if (i >= 0) list.splice(i, 1);
  else { if (limit && list.length >= limit) list.shift(); list.push(key); }
  write(k, list);
  return i < 0;
};
export const toggleSaved = (key: string) => toggle("kc_saved", key);
/** Compare holds at most four cars; adding a fifth drops the oldest. */
export const toggleCompared = (key: string) => toggle("kc_compare", key, 4);

/** Send a visitor without the upgrade to the upgrade page, remembering where they were. */
export const requirePlus = (feature: string): boolean => {
  if (isPlus()) return true;
  location.href = `/upgrade?for=${encodeURIComponent(feature)}&back=${encodeURIComponent(location.pathname + location.search)}`;
  return false;
};
