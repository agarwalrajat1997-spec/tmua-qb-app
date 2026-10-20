// Operational seed/verification. Uses the same worker/cache as production.
// Run with the explicitly scoped Vercel server environment; never print keys,
// emails, student IDs, answers, or individual ranks.
import { createRequire, Module } from "node:module";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import ts from "typescript";
import { createClient } from "@supabase/supabase-js";

if (!process.argv.includes("apply")) throw new Error("Pass apply to refresh the saved production ranking cohorts");
const root = process.cwd();
const url = process.env.NEXT_PUBLIC_SUPABASE_URL ?? process.env.SUPABASE_URL;
const key = process.env.SUPABASE_SERVICE_ROLE_KEY ?? process.env.SUPABASE_SERVICE_KEY;
if (!url || !key) throw new Error("Existing server environment is required; credentials were not printed");
if (new URL(url).hostname !== "pnkzxzigpkvhlmhsmzdd.supabase.co") throw new Error("Unexpected Supabase project");

const originalResolve = Module._resolveFilename;
Module._resolveFilename = function(request, parent, ...rest) {
  return originalResolve.call(this, request.startsWith("@/") ? resolve(root, request.slice(2)) : request, parent, ...rest);
};
Module._extensions[".ts"] = (module, filename) => module._compile(ts.transpileModule(readFileSync(filename, "utf8"), {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022, esModuleInterop: true },
  fileName: filename,
}).outputText, filename);
const require = createRequire(import.meta.url);
const { refreshPreparationRankIfDue } = require("../lib/server/preparation-rank-cache.ts");
const admin = createClient(url, key, {
  auth: { persistSession: false, autoRefreshToken: false },
  global: { fetch: (input, init) => fetch(input, { ...init, signal: AbortSignal.timeout(30_000) }) },
});
for (const programme of ["tmua", "esat"]) {
  const started = Date.now();
  const result = await refreshPreparationRankIfDue(admin, programme);
  console.log(JSON.stringify({ programme, refreshed: result.refreshed, cohortSize: result.cohortSize,
    calculatedAt: result.calculatedAt, durationMs: Date.now() - started }));
}
