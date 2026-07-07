import { redirect } from "next/navigation";
import { supabaseServer } from "@/utils/supabase/server";
import styles from "./page.module.css";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export default async function ESATWorkspacePage() {
  const supabase = await supabaseServer();

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user || !user.email) {
    redirect("/login?next=/esat");
  }

  const email = user.email;

  return (
    <main className={styles.page}>
      <section className={styles.shell}>
        <header className={styles.header}>
          <div>
            <div className={styles.kicker}>Thriving Scholars</div>
            <h1>ESAT Workspace</h1>
            <p>
              Your ESAT preparation dashboard. Start with the digital question bank below.
            </p>
            <div className={styles.emailPill}>
              Logged in as <span>{email}</span>
            </div>
          </div>

          <a href="/api/logout" className={styles.logoutBtn}>
            Logout
          </a>
        </header>

        <section className={styles.hero}>
          <div className={styles.heroText}>
            <div className={styles.badge}>ESAT Question Bank</div>

            <h2>Practise ESAT-style questions online</h2>

            <p>
              Access your ESAT digital question bank with a clean practice interface,
              question navigation, topic practice, and worked solutions.
            </p>

            <a href="/esat-question-bank" className={styles.primaryBtn}>
              Open ESAT Question Bank →
            </a>
          </div>

          <div className={styles.previewCard}>
            <div className={styles.previewTop}>
              <span></span>
              <span></span>
              <span></span>
            </div>

            <div className={styles.previewBody}>
              <div className={styles.previewTitle}>Question Bank</div>
              <div className={styles.previewLine}></div>
              <div className={styles.previewLineSmall}></div>

              <div className={styles.optionGrid}>
                <div>A</div>
                <div>B</div>
                <div>C</div>
                <div>D</div>
                <div>E</div>
              </div>

              <div className={styles.previewFooter}>
                <span>Check</span>
                <span>Solution</span>
                <span>Navigator</span>
              </div>
            </div>
          </div>
        </section>

        <footer className={styles.footer}>
          Access is linked to your login email. If you cannot open the question bank,
          contact Thriving Scholars using the same email address.
        </footer>
      </section>
    </main>
  );
}
