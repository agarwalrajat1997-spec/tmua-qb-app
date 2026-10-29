import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { supabaseServer } from "@/utils/supabase/server";
import { getIbSummary } from "@/lib/ib/content";
import { ibSubject, ibView, ibHref } from "@/lib/ib/catalog";
import IBPortalClient from "./IBPortalClient";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "IB Student Portal | Thriving Scholars", robots: { index: false, follow: false } };

export default async function IbPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const params = await searchParams;
  const next = ibHref(ibSubject(params.subject), ibView(params.view));
  const supabase = await supabaseServer();
  const { data: { user }, error } = await supabase.auth.getUser();
  if (error || !user?.email) redirect(`/ib-login?next=${encodeURIComponent(next)}`);
  return <IBPortalClient email={user.email} summary={getIbSummary()} />;
}
