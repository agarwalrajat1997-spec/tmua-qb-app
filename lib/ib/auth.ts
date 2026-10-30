import "server-only";
import { cache } from "react";
import { redirect } from "next/navigation";
import { supabaseServer } from "@/utils/supabase/server";
import { safeLoginDestination } from "@/lib/auth/login-destination";

const verifiedUser = cache(async () => {
  const supabase = await supabaseServer();
  const { data, error } = await supabase.auth.getUser();
  return error ? null : data.user;
});
export async function requireIbUser(destination: string) {
  const user = await verifiedUser();
  if (!user?.email) redirect(`/ib-login?next=${encodeURIComponent(safeLoginDestination(destination))}`);
  return user as typeof user & { email: string };
}
