"use client";

import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import styles from "./erasable-notepad-popup.module.css";
import { isTmuaFinalReminderActive } from "@/lib/tmua-final-reminder";
import { isEsatFinalReminderActive } from "@/lib/esat-final-reminder";
import { ERASABLE_NOTEPAD_AMAZON_URL } from "@/lib/erasable-notepad-popup";
import {
  ERASABLE_NOTEPAD_IMAGE_DATA_URL,
  ERASABLE_NOTEPAD_IMAGE_HEIGHT,
  ERASABLE_NOTEPAD_IMAGE_WIDTH,
} from "@/lib/erasable-notepad-image";

const PORTAL_ROUTE_PREFIXES = [
  "/dashboard",
  "/esat",
  "/esat-question-bank",
  "/esat-practice-tests",
  "/tmua-question-bank",
  "/question-bank-tmua",
  "/practice-tests",
  "/classes",
  "/tmua-classes",
  "/group-sessions",
] as const;

// The root layout and the TMUA dashboard router can both mount this component.
// Only one instance should query or open the announcement on a page.
let popupInstanceActive = false;

type Props = {
  /** Mount after the mixed dashboard router has confirmed TMUA access. */
  forcePortal?: boolean;
};

type PopupPayload = {
  show?: boolean;
  dismissed?: boolean;
  dismissals?: number;
  remaining?: number;
};

function matchesPrefix(
  pathname: string,
  prefix: string,
) {
  return (
    pathname === prefix ||
    pathname.startsWith(`${prefix}/`)
  );
}

function isEligiblePortalRoute(pathname: string) {
  return PORTAL_ROUTE_PREFIXES.some(
    (prefix) => matchesPrefix(pathname, prefix),
  );
}

export default function ErasableNotepadPopup({ forcePortal = false }: Props) {
  const pathname = usePathname();
  const dialogRef = useRef<HTMLDialogElement>(null);
  const dismissedThisViewRef = useRef(false);
  const savingRef = useRef(false);
  const [visible, setVisible] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState(false);

  useEffect(() => {
    const eligibleRoute =
      forcePortal ||
      isEligiblePortalRoute(pathname || "");

    if (!eligibleRoute) {
      setVisible(false);
      return;
    }

    if (popupInstanceActive) return;
    popupInstanceActive = true;

    let cancelled = false;
    let inFlight = false;
    let timer: ReturnType<typeof setTimeout> | undefined;

    async function check() {
      if (
        cancelled ||
        inFlight ||
        dismissedThisViewRef.current ||
        document.visibilityState !== "visible"
      ) {
        return;
      }

      // Exam reminders take priority while they are active. Recheck rather than
      // permanently suppressing this campaign for the current page visit.
      if (isTmuaFinalReminderActive() || isEsatFinalReminderActive()) {
        timer = setTimeout(() => {
          void check();
        }, 30_000);
        return;
      }

      // Do not put a product announcement over another open modal. Keep
      // checking after the higher-priority modal has been closed.
      const otherModal = Array.from(
        document.querySelectorAll("dialog[open], [aria-modal='true']"),
      ).some((modal) => modal !== dialogRef.current);

      if (otherModal) {
        timer = setTimeout(() => {
          void check();
        }, 1500);
        return;
      }

      inFlight = true;
      let shouldRetry = false;

      try {
        const result = await fetch("/api/student/erasable-notepad-popup", {
          method: "GET",
          credentials: "same-origin",
          cache: "no-store",
          signal: AbortSignal.timeout(15_000),
        });

        if (!result.ok) {
          shouldRetry = true;
          return;
        }

        const payload = (await result.json()) as PopupPayload;
        if (!cancelled && !dismissedThisViewRef.current) {
          setVisible(payload.show === true);
        }
      } catch {
        // An optional announcement must never block the portal.
        shouldRetry = true;
      } finally {
        inFlight = false;

        if (
          shouldRetry &&
          !cancelled &&
          !dismissedThisViewRef.current
        ) {
          clearTimeout(timer);
          timer = setTimeout(() => {
            void check();
          }, 30_000);
        }
      }
    }

    function schedule() {
      clearTimeout(timer);
      if (cancelled || dismissedThisViewRef.current) return;

      // Let the dashboard and any higher-priority announcement settle first.
      timer = setTimeout(() => {
        void check();
      }, 1100);
    }

    schedule();
    window.addEventListener("focus", schedule);
    window.addEventListener("online", schedule);
    document.addEventListener("visibilitychange", schedule);

    return () => {
      cancelled = true;
      popupInstanceActive = false;
      clearTimeout(timer);
      window.removeEventListener("focus", schedule);
      window.removeEventListener("online", schedule);
      document.removeEventListener("visibilitychange", schedule);
    };
  }, [forcePortal, pathname]);

  useEffect(() => {
    if (!visible) return;

    const dialog = dialogRef.current;
    if (!dialog) return;

    if (!dialog.open) {
      if (typeof dialog.showModal === "function") dialog.showModal();
      else dialog.setAttribute("open", "");
    }

    return () => {
      if (dialog.open && typeof dialog.close === "function") dialog.close();
    };
  }, [visible]);

  async function dismiss() {
    if (savingRef.current || dismissedThisViewRef.current) return;

    savingRef.current = true;
    setSaving(true);
    setSaveError(false);

    try {
      const result = await fetch("/api/student/erasable-notepad-popup", {
        method: "POST",
        credentials: "same-origin",
        cache: "no-store",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "dismiss" }),
        signal: AbortSignal.timeout(15_000),
      });

      const payload = (await result.json().catch(() => null)) as
        | PopupPayload
        | null;

      if (!result.ok || payload?.dismissed !== true) {
        throw new Error("Dismissal was not saved");
      }

      // One dismissal is recorded per page view. A refresh or later visit may
      // show the second and final announcement.
      dismissedThisViewRef.current = true;
      setVisible(false);
    } catch {
      setSaveError(true);
    } finally {
      savingRef.current = false;
      setSaving(false);
    }
  }

  if (!visible) return null;

  return (
    <dialog
      ref={dialogRef}
      className={styles.dialog}
      aria-labelledby="erasable-notepad-popup-title"
      aria-describedby="erasable-notepad-popup-description"
      data-testid="erasable-notepad-popup"
      onCancel={(event) => {
        event.preventDefault();
        void dismiss();
      }}
      aria-busy={saving}
    >
      <article className={styles.card}>
        <button
          className={styles.close}
          type="button"
          aria-label="Close announcement"
          onClick={() => {
            void dismiss();
          }}
          disabled={saving}
        >
          <span aria-hidden="true">×</span>
        </button>

        <div className={styles.media}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            className={styles.mainImage}
            src={ERASABLE_NOTEPAD_IMAGE_DATA_URL}
            alt="Comparison of an official exam erasable booklet and the Thriving Scholars erasable mock-practice notepad"
            width={ERASABLE_NOTEPAD_IMAGE_WIDTH}
            height={ERASABLE_NOTEPAD_IMAGE_HEIGHT}
            loading="eager"
            decoding="sync"
          />
        </div>

        <div className={styles.copy}>
          <p className={styles.eyebrow}>
            <span aria-hidden="true" /> Now available on Amazon UK
          </p>

          <h2 id="erasable-notepad-popup-title">
            Make mock practice feel closer to test day.
          </h2>

          <p id="erasable-notepad-popup-description" className={styles.lead}>
            Practise TMUA, ESAT and TARA working on a reusable erasable grid
            notepad inspired by the official exam-writing experience.
          </p>

          <ul className={styles.features}>
            <li>
              <span aria-hidden="true">✓</span> Six reusable erasable sheets
            </li>
            <li>
              <span aria-hidden="true">✓</span> Staedtler non-permanent marker
            </li>
            <li>
              <span aria-hidden="true">✓</span> Built for calculations and diagrams
            </li>
          </ul>

          <div className={styles.amazonRow}>
            <strong>Buy on Amazon UK</strong>
            <span>★★★★★</span>
          </div>

          <a
            className={styles.cta}
            href={ERASABLE_NOTEPAD_AMAZON_URL}
            target="_blank"
            rel="noopener noreferrer"
          >
            View the erasable practice notepad
            <span aria-hidden="true">↗</span>
          </a>

          {saveError ? (
            <p className={styles.error} role="alert">
              Couldn’t save that. Please try closing again when you’re online.
            </p>
          ) : null}

          <div className={styles.footerRow}>
            <span>Available directly from Amazon UK</span>
            <button
              type="button"
              onClick={() => {
                void dismiss();
              }}
              disabled={saving}
            >
              {saving ? "Saving…" : "Not now"}
            </button>
          </div>
        </div>
      </article>
    </dialog>
  );
}
