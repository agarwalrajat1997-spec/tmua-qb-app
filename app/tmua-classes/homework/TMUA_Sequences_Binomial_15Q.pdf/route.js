import { serveClassHomework } from "@/lib/tmua/class-homework";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 30;

export function GET() {
  return serveClassHomework({
    filename: "TMUA_Sequences_Binomial_15Q.pdf",
    objectPath: "2026-11-07-session-3/47e614cefcebb7790c23a195bb3720010bc73e19857877a0/TMUA_Sequences_Binomial_15Q.pdf",
    size: 927586,
    sha256: "be9b5c2a0aff5288aa25a396c60349b263650eaa54b38ecbe2eefdfb386eb2f0",
  });
}
