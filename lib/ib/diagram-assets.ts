import "server-only";
import { createHash } from "node:crypto";
import manifest from "@/content/ib/physics-diagram-manifest.json";
import { safeDiagramUrl } from "./question";

/** Only content-hashed images verified against their Cloudflare response enter this manifest. */
export function diagramUrlForSvg(svg?: string) {
  if (!svg) return undefined;
  const hash = createHash("sha256").update(svg).digest("hex");
  const entry = (manifest.assets as Record<string, { key: string; bytes: number }>)[hash];
  if (!entry || !/^ib\/physics-hl\/2026-10-30\/[a-f0-9]{64}\.svg$/.test(entry.key)) return undefined;
  const url = manifest.origin + "/" + entry.key;
  return safeDiagramUrl(url) ? url : undefined;
}
