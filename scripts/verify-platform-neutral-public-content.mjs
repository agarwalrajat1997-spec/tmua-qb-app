import { readFile, readdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const forbidden = /(?:\bwix\b|wixstatic|\/wix-components\/)/i;
const textFile = /\.(?:css|html|js|json|mjs|ts|tsx)(?:\.|$)/i;
const failures = [];

async function scan(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if ([".next", "legacy-media", "node_modules"].includes(entry.name)) continue;
    const target = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      await scan(target);
      continue;
    }
    if (!textFile.test(entry.name)) continue;

    const content = await readFile(target, "utf8");
    const withoutEmbeddedData = content.replace(/data:[^"'\s)]+/gi, "");
    if (forbidden.test(withoutEmbeddedData)) {
      failures.push(path.relative(root, target));
    }
  }
}

await scan(path.join(root, "app"));
await scan(path.join(root, "public"));

if (failures.length > 0) {
  throw new Error(`Former-platform references remain in public app content:\n${failures.join("\n")}`);
}

console.log("Verified platform-neutral public app content.");
