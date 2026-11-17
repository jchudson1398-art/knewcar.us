// The catalog snapshot as a static file, for pages that build their content in the browser (saved, compare, estimate).
import { CATALOG } from "../lib/catalog";
export const GET = () => new Response(JSON.stringify(CATALOG), { headers: { "Content-Type": "application/json" } });
