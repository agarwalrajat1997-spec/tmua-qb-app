import type { Metadata } from "next";
import { Suspense } from "react";
import IBLoginClient from "./IBLoginClient";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "IB Sign in | Thriving Scholars", robots: { index: false, follow: false } };
export default function IbLoginPage() {
  return <Suspense fallback={<p>Loading your IB portal…</p>}><IBLoginClient /></Suspense>;
}
