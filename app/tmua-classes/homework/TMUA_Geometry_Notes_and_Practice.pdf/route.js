import { serveClassHomework } from "@/lib/tmua/class-homework";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 30;

export function GET() {
  return serveClassHomework({
    filename: "TMUA_Geometry_Notes_and_Practice.pdf",
    objectPath: "2026-11-22-session-8/TMUA_Geometry_Notes_and_Practice.pdf",
    size: 456855,
    sha256: "b27fc2e1ac83929a7711459b0b5145fc11c8aa02745b6388db921a094b39f486",
  });
}
