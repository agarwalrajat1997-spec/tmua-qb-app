import AMCDashboardClient from "@/app/dashboard/AMCDashboardClient";
import { supabaseServer } from "@/utils/supabase/server";
import { redirect } from "next/navigation";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export const metadata = {
  title: "AMC Student Portal | Thriving Scholars",
};

function activeProducts(
  rows: Array<{ product?: string | null; expires_at?: string | null }>,
) {
  const now = Date.now();

  return new Set(
    rows
      .filter((row) => {
        if (!row.expires_at) return true;
        const expiry = Date.parse(row.expires_at);
        return Number.isFinite(expiry) && expiry > now;
      })
      .map((row) => String(row.product || "")),
  );
}

type Props = {
  searchParams: Promise<{ section?: string }>;
};

export default async function AMCPortalPage({ searchParams }: Props) {
  const { section } = await searchParams;
  const supabase = await supabaseServer();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user?.email) redirect("/amc-login");

  const { data, error } = await supabase
    .from("student_access")
    .select("product, expires_at")
    .ilike("email", user.email)
    .eq("approved", true);

  const products = activeProducts(data || []);

  if (error || !products.has("amc-question-bank")) {
    return (
      <main style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: 24, background: "#fffdf7" }}>
        <section style={{ width: "min(100%, 620px)", padding: 32, border: "1px solid #e7e7e7", borderRadius: 18, background: "#fff", fontFamily: "ui-sans-serif, system-ui" }}>
          <p style={{ color: "#7a1f24", fontWeight: 900, letterSpacing: ".1em" }}>THRIVING SCHOLARS AMC</p>
          <h1>AMC access is not enabled</h1>
          <p>Signed in as <b>{user.email}</b>. Contact outreach@thrivingscholars.com if you purchased AMC access.</p>
          <a href="/api/logout" style={{ color: "#7a1f24", fontWeight: 900 }}>Sign out</a>
        </section>
      </main>
    );
  }

  return (
    <AMCDashboardClient
      email={user.email}
      hasTmua={false}
      initialSection={section === "practice-tests" ? "practice-tests" : null}
    />
  );
}
