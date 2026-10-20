import { after } from "next/server";
import type { SupabaseClient } from "@supabase/supabase-js";

type Programme = "tmua" | "esat";
const MODEL = {
  tmua: "tmua-preparation-rank-v1-20260810",
  esat: "esat-preparation-rank-v1-20260819",
};

// One bounded database lookup, with a fresh entitlement check inside the RPC.
// Only the caller's rank is returned; cohort records never leave the server.
export async function readPreparationRankSnapshot(admin: SupabaseClient, userId: string, programme: Programme, verifiedEmail: string | undefined) {
  try {
    const { data, error } = await admin.rpc("read_portal_preparation_rank", {
      p_programme: programme, p_user_id: userId, p_email: verifiedEmail ?? "",
    }).retry(false);
    if (error || !data) throw error ?? new Error("Missing ranking response");
    return data;
  } catch (error) {
    console.error(`${programme.toUpperCase()} saved ranking unavailable`, error);
    return {
      modelVersion: MODEL[programme], status: "temporarily_unavailable",
      hasGenuinePreparationEvidence: false, score: null, rank: null,
      cohortSize: 0, components: null, calculatedAt: new Date().toISOString(),
    };
  }
}

// A database lease, not process memory, prevents concurrent tabs/instances from
// starting duplicate cohort scans. A crash releases itself after ten minutes.
// Keep the last complete run visible while a refresh runs after the response.
export async function refreshPreparationRankIfDue(admin: SupabaseClient, programme: Programme) {
  const { data: token, error } = await admin.rpc("claim_portal_rank_refresh", {
    p_programme: programme,
  }).retry(false);
  if (error) throw error;
  if (!token) return { refreshed: false };
  try {
    const result = programme === "tmua"
      ? await (await import("./tmua-preparation-rank-refresh")).refreshTmuaPreparationRank(admin)
      : await (await import("./esat-preparation-rank-refresh")).refreshEsatPreparationRank(admin);
    const finished = await admin.rpc("finish_portal_rank_refresh", {
      p_programme: programme, p_token: token, p_run_id: result.runId,
    }).retry(false);
    if (finished.error || finished.data !== true) throw finished.error ?? new Error("Ranking lease expired");
    console.info(`${programme.toUpperCase()} ranking refreshed`, { cohortSize: result.cohortSize });
    return { refreshed: true, ...result };
  } catch (error) {
    try {
      const failed = await admin.rpc("fail_portal_rank_refresh", {
        p_programme: programme, p_token: token,
      }).retry(false);
      if (failed.error) console.error("Unable to release ranking refresh lease", failed.error);
    } catch (releaseError) {
      console.error("Unable to release ranking refresh lease", releaseError);
    }
    throw error;
  }
}

export function requestPreparationRankRefresh(admin: SupabaseClient, programme: Programme) {
  after(async () => {
    try { await refreshPreparationRankIfDue(admin, programme); }
    catch (error) { console.error(`${programme.toUpperCase()} ranking refresh failed`, error); }
  });
}
