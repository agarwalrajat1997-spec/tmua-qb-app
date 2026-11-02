import { ERASABLE_NOTEPAD_PROMO_IMAGE } from "@/lib/erasable-notepad-image-hires";

export const dynamic = "force-static";

const DATA_URI_PREFIX = "data:image/webp;base64,";
const base64 = ERASABLE_NOTEPAD_PROMO_IMAGE.startsWith(DATA_URI_PREFIX)
  ? ERASABLE_NOTEPAD_PROMO_IMAGE.slice(DATA_URI_PREFIX.length)
  : ERASABLE_NOTEPAD_PROMO_IMAGE;
const imageBytes = Buffer.from(base64, "base64");

export function GET() {
  return new Response(imageBytes, {
    status: 200,
    headers: {
      "Content-Type": "image/webp",
      "Content-Length": String(imageBytes.byteLength),
      "Cache-Control": "public, max-age=31536000, immutable",
      "X-Content-Type-Options": "nosniff",
    },
  });
}
