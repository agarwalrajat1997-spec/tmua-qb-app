"use client";

import { useEffect, useState } from "react";
import DashboardClient from "./DashboardClient";
import AMCDashboardClient from "./AMCDashboardClient";
import SATDashboardClient from "./SATDashboardClient";
import styles from "./dashboard.module.css";
import { supabaseBrowser } from "@/utils/supabase/browser";

type RouteState =
  | {
      mode: "loading";
      email?: string | null;
    }
  | {
      mode: "sat";
      email?: string | null;
      hasSatBank: boolean;
      hasSatTests: boolean;
      hasAmc: boolean;
      hasTmua: boolean;
    }
  | {
      mode: "amc";
      email?: string | null;
      hasTmua: boolean;
    }
  | {
      mode: "tmua";
      email?: string | null;
    }
  | {
      mode: "none";
      email?: string | null;
      error?: string;
    };

export default function DashboardAccessRouterClient() {
  const [state, setState] = useState<RouteState>({ mode: "loading" });

  useEffect(() => {
    let cancelled = false;

    async function run() {
      try {
        const requestedView =
          typeof window !== "undefined"
            ? new URLSearchParams(window.location.search).get("view")
            : "";

        const supabase = supabaseBrowser();

        const {
          data: { user },
          error: userErr,
        } = await supabase.auth.getUser();

        if (userErr || !user?.email) {
          window.location.href = "/login?next=/dashboard";
          return;
        }

        const { data, error } = await supabase
          .from("student_access")
          .select("product, approved")
          .ilike("email", user.email)
          .eq("approved", true);

        if (cancelled) return;

        if (error) {
          console.error("Dashboard access load failed:", error);
          setState({
            mode: "none",
            email: user.email,
            error: error.message || "Could not load product access.",
          });
          return;
        }

        const products = Array.from(
          new Set((data || []).map((r: any) => String(r.product || "")))
        );

        const hasSatBank = products.includes("sat-question-bank");
        const hasSatTests = products.includes("sat-practice-tests");
        const hasSAT = hasSatBank || hasSatTests;

        const hasAMC = products.includes("amc-question-bank");

        const tmuaProducts = ["practice-tests", "tmua-question-bank", "tmua-classes"];
        const hasTMUA = products.some((p) => tmuaProducts.includes(p));

        if (requestedView === "sat" && hasSAT) {
          setState({
            mode: "sat",
            email: user.email,
            hasSatBank,
            hasSatTests,
            hasAmc: hasAMC,
            hasTmua: hasTMUA,
          });
          return;
        }

        if (requestedView === "amc" && hasAMC) {
          setState({ mode: "amc", email: user.email, hasTmua: hasTMUA });
          return;
        }

        if (requestedView === "tmua" && hasTMUA) {
          setState({ mode: "tmua", email: user.email });
          return;
        }

        // Default priority for mixed-access users.
        if (hasSAT) {
          setState({
            mode: "sat",
            email: user.email,
            hasSatBank,
            hasSatTests,
            hasAmc: hasAMC,
            hasTmua: hasTMUA,
          });
          return;
        }

        if (hasAMC) {
          setState({ mode: "amc", email: user.email, hasTmua: hasTMUA });
          return;
        }

        if (hasTMUA) {
          setState({ mode: "tmua", email: user.email });
          return;
        }

        setState({ mode: "none", email: user.email });
      } catch (e: any) {
        console.error("Dashboard router crashed:", e);
        setState({
          mode: "none",
          error: String(e?.message || e),
        });
      }
    }

    run();

    return () => {
      cancelled = true;
    };
  }, []);

  if (state.mode === "loading") {
    return (
      <div className={styles.page} data-ui="TS_DASH_SAFE_ROUTER_LOADING">
        <div className={styles.topbar}>
          <div className={styles.brand}>
            <div className={styles.brandName}>Thriving Scholars</div>
            <div className={styles.brandTag}>Student Portal</div>
          </div>
          <div className={styles.right}>
            <div className={styles.pill}>Loading...</div>
          </div>
        </div>

        <div className={styles.main}>
          <div className={styles.card}>
            <div className={styles.cardTitle}>Loading your portal...</div>
            <div className={styles.muted}>Checking your product access.</div>
          </div>
        </div>
      </div>
    );
  }

  if (state.mode === "sat") {
    return (
      <SATDashboardClient
        email={state.email}
        hasSatBank={state.hasSatBank}
        hasSatTests={state.hasSatTests}
        hasAmc={state.hasAmc}
        hasTmua={state.hasTmua}
      />
    );
  }

  if (state.mode === "amc") {
    return <AMCDashboardClient email={state.email} hasTmua={state.hasTmua} />;
  }

  if (state.mode === "tmua") {
    return <DashboardClient uiMark="TS_DASH_PORTAL_20260227142744" />;
  }

  return (
    <div className={styles.page} data-ui="TS_DASH_NO_ACCESS_SAFE">
      <div className={styles.topbar}>
        <div className={styles.brand}>
          <div className={styles.brandName}>Thriving Scholars</div>
          <div className={styles.brandTag}>Student Portal</div>
        </div>
      </div>

      <div className={styles.main}>
        <div className={styles.card}>
          <div className={styles.cardTitle}>No products enabled</div>
          <div className={styles.muted}>
            Signed in as <b>{state.email || "—"}</b>, but no active product access was found.
            <br />
            {state.error ? (
              <>
                <br />
                Error: <b>{state.error}</b>
              </>
            ) : null}
            <br />
            Contact <b>outreach@thrivingscholars.com</b>.
          </div>
        </div>
      </div>
    </div>
  );
}


