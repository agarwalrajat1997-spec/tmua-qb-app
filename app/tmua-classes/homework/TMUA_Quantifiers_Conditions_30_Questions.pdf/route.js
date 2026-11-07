import { serveClassHomework } from "@/lib/tmua/class-homework";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 30;

export function GET() {
  return serveClassHomework({
    filename: "TMUA_Quantifiers_Conditions_30_Questions.pdf",
    objectPath: "2026-11-01-session-2/TMUA_Quantifiers_Conditions_30_Questions.pdf",
    size: 855748,
    sha256: "baa34d611150514b804de461ad9ab3835457d02230a2952333e1bb2d6aa46428",
  });
}
