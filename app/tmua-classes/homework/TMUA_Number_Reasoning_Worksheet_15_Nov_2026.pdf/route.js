import { serveClassHomework } from "@/lib/tmua/class-homework";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 30;

export function GET() {
  return serveClassHomework({
    filename: "TMUA_Number_Reasoning_Worksheet_15_Nov_2026.pdf",
    objectPath: "2026-11-15-session-6/TMUA_Number_Reasoning_Worksheet_15_Nov_2026.pdf",
    size: 285326,
    sha256: "4e64da097ccef88180aee7f96588bd0c206fb0a446291c7ab1d18665a4031070",
  });
}
