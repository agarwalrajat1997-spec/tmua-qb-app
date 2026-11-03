import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { supabaseServer } from "@/utils/supabase/server";
import { getIbAccessState } from "@/lib/ib/access";
import { IBTrialForm } from "../ib-login/IBTrialForm";
import styles from "../ib/ib.module.css";
export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Your IB access | Thriving Scholars", robots: {index:false,follow:false} };
export default async function IbAccessPage() {
  const db = await supabaseServer();
  const {data:{user},error} = await db.auth.getUser();
  if (error || !user?.email) redirect("/ib-login?next=%2Fib");
  const access = await getIbAccessState();
  if (access === "active") redirect("/ib");
  return <div className={styles.app}><main style={{maxWidth:760,margin:"0 auto",padding:"72px 24px"}}>
    <a href="https://www.thrivingscholars.com/ib-prep">Thriving Scholars · IB Prep Portal</a>
    <p className={styles.eyebrow}>YOUR NEXT CHAPTER</p>
    <h1>{access === "unavailable" ? "Let’s check your access." : access === "trial_expired" ? "Two days down. More progress ahead." : "Your IB study space is waiting."}</h1>
    <p>{access === "unavailable" ? "We could not check your access just now. Please try again shortly." : access === "trial_expired" ? "Your free 48-hour trial has ended. Continue with full portal access, or talk to us about 1:1 Maths and Physics tutoring." : "Start your free two-day trial below, using the email you signed in with."}</p>
    <p>Signed in as {user.email}</p>
    {access !== "unavailable" ? <><a className={styles.primaryButton} href="https://wa.me/447459070019?text=Hi%20Thriving%20Scholars!%20I%27d%20like%20full%20IB%20Prep%20Portal%20access%20at%20US%2499.%20My%20student%20email%20is%20%5Bemail%5D.%20Please%20help%20me%20get%20started.">Ask about full access · US$99 ↗</a><p>One-time portal access. Message us with your student email to arrange access.</p><a href="https://www.thrivingscholars.com/ib-prep#tutoring">Looking for 1:1 IB tutoring? Let’s talk ↗</a></> : <a href="/ib-access">Try again</a>}
  </main>{access === "trial_required" ? <IBTrialForm /> : null}</div>;
}
