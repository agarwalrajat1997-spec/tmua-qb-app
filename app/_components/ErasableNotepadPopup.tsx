"use client";

import { usePathname } from "next/navigation";
import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import styles from "./erasable-notepad-popup.module.css";
import { ERASABLE_NOTEPAD_AMAZON_URL } from "@/lib/erasable-notepad-popup";

const PROMO_IMAGE_URL =
  "/announcements/erasable-notepad-amazon-announcement.webp";

const PORTAL_ROUTE_PREFIXES = [
  "/esat",
  "/esat-login",
  "/esat-question-bank",
  "/esat-practice-tests",
  "/tmua-question-bank",
  "/question-bank-tmua",
  "/practice-tests",
  "/classes",
  "/tmua-classes",
  "/group-sessions",
] as const;

const NON_TMUA_LOGIN_PREFIXES = [
  "/sat",
  "/amc",
] as const;

type Props = {
  /** Use only after the mixed dashboard router has confirmed TMUA access. */
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

function loginIsForTmuaOrEsat(search: string) {
  const rawNext =
    new URLSearchParams(search)
      .get("next") ||
    "/dashboard";

  try {
    const nextPath =
      new URL(
        rawNext,
        window.location.origin,
      ).pathname;

    return !NON_TMUA_LOGIN_PREFIXES.some(
      (prefix) =>
        matchesPrefix(
          nextPath,
          prefix,
        ),
    );
  } catch {
    return true;
  }
}

function isPortalRoute(
  pathname: string,
  search: string,
) {
  if (pathname === "/login") {
    return loginIsForTmuaOrEsat(search);
  }

  return PORTAL_ROUTE_PREFIXES.some(
    (prefix) =>
      matchesPrefix(
        pathname,
        prefix,
      ),
  );
}

export default function ErasableNotepadPopup({
  forcePortal = false,
}: Props) {
  const pathname = usePathname();
  const dialogRef =
    useRef<HTMLDialogElement>(null);
  const dismissedThisMountRef =
    useRef(false);
  const savingRef =
    useRef(false);

  const [visible, setVisible] =
    useState(false);
  const [saving, setSaving] =
    useState(false);
  const [saveError, setSaveError] =
    useState(false);

  useEffect(() => {
    let cancelled = false;
    let inFlight = false;
    let timer:
      ReturnType<typeof setTimeout> |
      undefined;

    const eligibleRoute =
      forcePortal ||
      isPortalRoute(
        pathname || "",
        window.location.search,
      );

    if (!eligibleRoute) {
      setVisible(false);
      return;
    }

    async function check() {
      if (
        cancelled ||
        inFlight ||
        dismissedThisMountRef.current ||
        document.visibilityState !== "visible"
      ) {
        return;
      }

      const otherModal = Array.from(
        document.querySelectorAll(
          "dialog[open], [aria-modal='true']",
        ),
      ).some(
        (modal) =>
          modal !== dialogRef.current,
      );

      if (otherModal) {
        timer = setTimeout(
          () => {
            void check();
          },
          1500,
        );
        return;
      }

      inFlight = true;
      let retry = true;

      try {
        const result = await fetch(
          "/api/student/erasable-notepad-popup",
          {
            method: "GET",
            credentials: "same-origin",
            cache: "no-store",
            signal: AbortSignal.timeout(15_000),
          },
        );

        if (!result.ok) return;

        const payload =
          (await result.json()) as PopupPayload;
        retry = false;

        if (
          !cancelled &&
          !dismissedThisMountRef.current
        ) {
          setVisible(payload.show === true);
        }
      } catch {
        // A promotional message must never block the student portal.
      } finally {
        inFlight = false;

        if (
          retry &&
          !cancelled &&
          !dismissedThisMountRef.current
        ) {
          clearTimeout(timer);
          timer = setTimeout(
            () => {
              void check();
            },
            30_000,
          );
        }
      }
    }

    function schedule() {
      clearTimeout(timer);
      if (
        cancelled ||
        dismissedThisMountRef.current
      ) {
        return;
      }

      // The good-luck/final-reminder messages get first priority.
      timer = setTimeout(
        () => {
          void check();
        },
        900,
      );
    }

    schedule();
    window.addEventListener(
      "focus",
      schedule,
    );
    window.addEventListener(
      "online",
      schedule,
    );
    document.addEventListener(
      "visibilitychange",
      schedule,
    );

    return () => {
      cancelled = true;
      clearTimeout(timer);
      window.removeEventListener(
        "focus",
        schedule,
      );
      window.removeEventListener(
        "online",
        schedule,
      );
      document.removeEventListener(
        "visibilitychange",
        schedule,
      );
    };
  }, [forcePortal, pathname]);

  useEffect(() => {
    if (!visible) return;

    const dialog = dialogRef.current;
    if (!dialog) return;

    if (!dialog.open) {
      if (
        typeof dialog.showModal ===
        "function"
      ) {
        dialog.showModal();
      }
      else {
        dialog.setAttribute(
          "open",
          "",
        );
      }
    }

    return () => {
      if (dialog.open) dialog.close();
    };
  }, [visible]);

  const dismiss = useCallback(async () => {
    if (
      savingRef.current ||
      dismissedThisMountRef.current
    ) {
      return;
    }

    savingRef.current = true;
    setSaving(true);
    setSaveError(false);

    try {
      const result = await fetch(
        "/api/student/erasable-notepad-popup",
        {
          method: "POST",
          credentials: "same-origin",
          cache: "no-store",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            action: "dismiss",
          }),
          signal: AbortSignal.timeout(15_000),
        },
      );

      const payload =
        (await result.json().catch(
          () => ({}),
        )) as PopupPayload;

      if (
        !result.ok ||
        payload.dismissed !== true
      ) {
        throw new Error(
          "Dismissal was not saved",
        );
      }

      // Close for this page visit. The server will offer it once more on the
      // next refresh/return, then stop after the second saved dismissal.
      dismissedThisMountRef.current = true;
      setVisible(false);
    } catch {
      setSaveError(true);
    } finally {
      savingRef.current = false;
      setSaving(false);
    }
  }, []);

  if (!visible) return null;

  return (
    <dialog
      ref={dialogRef}
      className={styles.dialog}
      aria-labelledby="erasable-notepad-popup-title"
      aria-describedby="erasable-notepad-popup-description"
      data-testid="erasable-notepad-popup"
      aria-busy={saving}
      onCancel={(event) => {
        event.preventDefault();
        void dismiss();
      }}
    >
      <article className={styles.card}>
        <button
          className={styles.close}
          type="button"
          aria-label="Close announcement"
          disabled={saving}
          onClick={() => {
            void dismiss();
          }}
        >
          <span aria-hidden="true">×</span>
        </button>

        <div className={styles.media}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            className={styles.mainImage}
            src={PROMO_IMAGE_URL}
            alt="Official exam writing experience compared with the Thriving Scholars erasable mock-practice notepad"
            width={640}
            height={640}
            loading="eager"
            decoding="async"
          />
        </div>

        <div className={styles.copy}>
          <p className={styles.eyebrow}>
            <span aria-hidden="true" />
            Now available on Amazon UK
          </p>

          <h2 id="erasable-notepad-popup-title">
            Practise on an erasable exam-style surface.
          </h2>

          <p
            id="erasable-notepad-popup-description"
            className={styles.lead}
          >
            Use the Thriving Scholars mock-practice notepad for timed
            TMUA and ESAT working, calculations and diagrams.
          </p>

          <ul className={styles.features}>
            <li>
              <span aria-hidden="true">✓</span>
              Six reusable laminated grid sheets
            </li>
            <li>
              <span aria-hidden="true">✓</span>
              Staedtler non-permanent marker included
            </li>
            <li>
              <span aria-hidden="true">✓</span>
              Designed for realistic mock practice at home
            </li>
          </ul>

          <div className={styles.amazonRow}>
            <strong>Amazon UK</strong>
            <span>Secure checkout and delivery options</span>
          </div>

          <a
            className={styles.cta}
            href={ERASABLE_NOTEPAD_AMAZON_URL}
            target="_blank"
            rel="noopener noreferrer"
            onClick={() => {
              void dismiss();
            }}
          >
            View the notepad on Amazon
            <span aria-hidden="true">↗</span>
          </a>

          {saveError && (
            <p
              className={styles.error}
              role="alert"
            >
              Couldn’t save that yet. Please try closing again when
              you’re online.
            </p>
          )}

          <div className={styles.footerRow}>
            <span>Independent mock-practice product</span>
            <button
              type="button"
              disabled={saving}
              onClick={() => {
                void dismiss();
              }}
            >
              {saving ? "Saving…" : "Not now"}
            </button>
          </div>
        </div>
      </article>
    </dialog>
  );
}
