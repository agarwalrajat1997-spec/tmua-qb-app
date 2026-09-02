import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const RELEASE = "sat-qb-phase4-root-static-v1";

export async function GET() {
  return NextResponse.json(
    { ok: true, release: RELEASE },
    {
      headers: {
        "Cache-Control": "no-store, max-age=0",
      },
    }
  );
}
