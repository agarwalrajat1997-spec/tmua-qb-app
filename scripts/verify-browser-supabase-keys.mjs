import { readdir, readFile } from "node:fs/promises";
import path from "node:path";

async function walk(directory) {
  const files = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const name = path.join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await walk(name));
    else if (/\.(js|json|html|map)$/.test(entry.name)) files.push(name);
  }
  return files;
}

const files = await walk(".next/static");
const unsafeFiles = new Set();
for (const file of files) {
  const text = await readFile(file, "utf8");
  if (/sb_secret_[A-Za-z0-9_-]{15,}/.test(text)) unsafeFiles.add(file);
  for (const match of text.matchAll(/eyJ[A-Za-z0-9_-]+\.([A-Za-z0-9_-]+)\.[A-Za-z0-9_-]+/g)) {
    try {
      const payload = JSON.parse(Buffer.from(match[1], "base64url").toString());
      if (payload.role === "service_role") unsafeFiles.add(file);
    } catch { /* Not a JWT payload. */ }
  }
}
if (unsafeFiles.size) {
  // Never print the offending credential, even in private build logs.
  throw new Error(`Server-only Supabase keys found in browser output: ${[...unsafeFiles].join(", ")}`);
}
console.log(`Verified ${files.length} browser files: no Supabase server keys exposed.`);
