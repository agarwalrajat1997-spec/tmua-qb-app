import "server-only";
import { supabaseServer } from "@/utils/supabase/server";
export async function getIbAccessState(): Promise<"active" | "trial_expired" | "trial_required" | "unavailable"> {
  try {
    const db = await supabaseServer();
    const { data, error } = await db.rpc("ib_access_state");
    if (error || !["active", "trial_expired", "trial_required"].includes(data)) return "unavailable";
    return data;
  } catch { return "unavailable"; }
}
