import { serveClassHomework } from "@/lib/tmua/class-homework";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 30;

export function GET() {
  return serveClassHomework({
    filename: "TMUA_Functions_and_Graphs_Notes_and_15_Questions.pdf",
    objectPath: "2026-11-14-session-5/TMUA_Functions_and_Graphs_Notes_and_15_Questions.pdf",
    size: 162983,
    sha256: "6e2453369cefa54d986fa58d0916e5b309d2dbaa07991db44e2d802f2405e855",
  });
}
