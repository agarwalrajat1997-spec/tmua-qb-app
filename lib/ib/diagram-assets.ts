import "server-only";
import { createHash } from "node:crypto";
import manifest from "@/content/ib/physics-diagram-manifest.json";
import chemistryManifest from "@/content/ib/chemistry-diagram-manifest.json";
import biologyManifest from "@/content/ib/biology-diagram-manifest.json";
import { safeDiagramUrl } from "./question";

/** Only content-hashed images verified against their Cloudflare response enter this manifest. */
export function diagramUrlForSvg(svg?: string) {
  if (!svg) return undefined;
  const hash = createHash("sha256").update(svg).digest("hex");
  for (const [assets, prefix] of [[manifest, "ib/physics-hl/2026-10-30/"], [chemistryManifest, "ib/chemistry/2026-10-30/"], [biologyManifest, "ib/biology/2026-10-30/"]] as const) {
    const entry = (assets.assets as Record<string, { key: string; bytes: number }>)[hash];
    if (!entry || entry.key !== prefix + hash + ".svg" || entry.bytes !== Buffer.byteLength(svg)) continue;
    const url = assets.origin + "/" + entry.key;
    if (safeDiagramUrl(url)) return url;
  }
  return undefined;
}

/** Original raster illustrations retain a byte-identical local fallback. */
export function diagramFallbackForUrl(url?: string) {
  if (!url || !safeDiagramUrl(url)) return undefined;
  for (const [hash, entry] of Object.entries(biologyManifest.assets as Record<string, { key: string; publicPath?: string }>)) {
    if (!/^[a-f0-9]{64}$/.test(hash) || entry.key !== `ib/biology/2026-10-30/${hash}.png`) continue;
    if (url === biologyManifest.origin + "/" + entry.key && entry.publicPath === `/ib-assets/biology/${hash}.png`) return entry.publicPath;
  }
  return undefined;
}
