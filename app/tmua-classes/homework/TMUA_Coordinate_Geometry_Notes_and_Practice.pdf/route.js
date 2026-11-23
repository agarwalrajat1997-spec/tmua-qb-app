import { serveClassHomework } from "@/lib/tmua/class-homework";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 30;

export function GET() {
  return serveClassHomework({
    filename: "TMUA_Coordinate_Geometry_Notes_and_Practice.pdf",
    objectPath: "2026-11-21-session-7/TMUA_Coordinate_Geometry_Notes_and_Practice.pdf",
    size: 868011,
    sha256: "faf3195ab4e52e273f3d5c9a648680fd1bf02625d84076c013f0f5014692795e",
  });
}
