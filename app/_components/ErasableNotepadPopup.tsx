"use client";

import { usePathname } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import styles from "./erasable-notepad-popup.module.css";

const DISMISSAL_KEY = "erasable_notepad_promo_dismissed";
const PRODUCT_URL =
  "https://www.thrivingscholars.com/tmua-esat-tara-erasable-practice-notepad";
const KIT_IMAGE_URL =
  "https://media.thrivingscholars.com/products/erasable-notepad/erasable-practice-notepad-kit.png";
const GRID_IMAGE_URL =
  "https://media.thrivingscholars.com/products/erasable-notepad/erasable-practice-notepad-grid-pages.png";

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

const NON_TMUA_LOGIN_PREFIXES = ["/sat", "/amc"] as const;

type Props = {
  /** Use only after the mixed dashboard router has confirmed TMUA access. */
  forcePortal?: boolean;
};

function matchesPrefix(pathname: string, prefix: string) {
  return pathname === prefix || pathname.startsWith(`${prefix}/`);
}

function loginIsForTmuaOrEsat(search: string) {
  const rawNext = new URLSearchParams(search).get("next") || "/dashboard";

  try {
    const nextPath = new URL(rawNext, window.location.origin).pathname;
    return !NON_TMUA_LOGIN_PREFIXES.some((prefix) =>
      matchesPrefix(nextPath, prefix),
    );
  } catch {
    return true;
  }
}

function isPortalRoute(pathname: string, search: string) {
  if (pathname === "/login") return loginIsForTmuaOrEsat(search);

  return PORTAL_ROUTE_PREFIXES.some((prefix) =>
    matchesPrefix(pathname, prefix),
  );
}

function hasDismissalCookie() {
  return document.cookie
    .split(";")
    .some((value) => value.trim() === `${DISMISSAL_KEY}=1`);
}

function wasDismissed() {
  try {
    if (window.localStorage.getItem(DISMISSAL_KEY) === "1") return true;
  } catch {
    // A first-party cookie remains available when localStorage is restricted.
  }

  return hasDismissalCookie();
}

function saveDismissal() {
  try {
    window.localStorage.setItem(DISMISSAL_KEY, "1");
  } catch {
    // The cookie below provides the persistence fallback.
  }

  document.cookie = `${DISMISSAL_KEY}=1; Max-Age=315360000; Path=/; SameSite=Lax; Secure`;
}

export default function ErasableNotepadPopup({ forcePortal = false }: Props) {
  const pathname = usePathname();
  const dialogRef = useRef<HTMLDialogElement>(null);
  const [shouldRender, setShouldRender] = useState(false);

  const dismiss = useCallback(() => {
    saveDismissal();

    const dialog = dialogRef.current;
    if (dialog?.open && typeof dialog.close === "function") {
      dialog.close();
    } else {
      dialog?.removeAttribute("open");
    }

    setShouldRender(false);
  }, []);

  useEffect(() => {
    const eligible =
      forcePortal || isPortalRoute(pathname || "", window.location.search);

    setShouldRender(eligible && !wasDismissed());
  }, [forcePortal, pathname]);

  useEffect(() => {
    if (!shouldRender) return;

    const dialog = dialogRef.current;
    if (!dialog) return;
    const activeDialog = dialog;

    if (!activeDialog.open) {
      if (typeof activeDialog.showModal === "function") activeDialog.showModal();
      else activeDialog.setAttribute("open", "");
    }

    function closeFromAnotherTab(event: StorageEvent) {
      if (event.key === DISMISSAL_KEY && event.newValue === "1") {
        if (activeDialog.open && typeof activeDialog.close === "function") {
          activeDialog.close();
        }
        setShouldRender(false);
      }
    }

    window.addEventListener("storage", closeFromAnotherTab);
    return () => window.removeEventListener("storage", closeFromAnotherTab);
  }, [shouldRender]);

  if (!shouldRender) return null;

  return (
    <dialog
      ref={dialogRef}
      className={styles.dialog}
      aria-labelledby="erasable-notepad-popup-title"
      aria-describedby="erasable-notepad-popup-description"
      data-testid="erasable-notepad-popup"
      onCancel={(event) => {
        event.preventDefault();
        dismiss();
      }}
    >
      <article className={styles.card}>
        <button
          className={styles.close}
          type="button"
          aria-label="Close and do not show this again"
          onClick={dismiss}
        >
          <span aria-hidden="true">×</span>
        </button>

        <div className={styles.media} aria-hidden="true">
          <div className={styles.mainImageFrame}>
            <img
              className={styles.mainImage}
              src={KIT_IMAGE_URL}
              alt=""
              width={941}
              height={1672}
              loading="eager"
              decoding="async"
            />
          </div>
          <div className={styles.insetImageFrame}>
            <img
              src={GRID_IMAGE_URL}
              alt=""
              width={941}
              height={1672}
              loading="eager"
              decoding="async"
            />
          </div>
        </div>

        <div className={styles.copy}>
          <p className={styles.eyebrow}>
            <span aria-hidden="true" /> TMUA · ESAT · TARA home practice
          </p>
          <h2 id="erasable-notepad-popup-title">
            Make the working surface familiar before test day.
          </h2>
          <p id="erasable-notepad-popup-description" className={styles.lead}>
            Practise with six reusable erasable grid sheets, a Staedtler
            non-permanent marker and a quick-use guide.
          </p>

          <ul className={styles.features}>
            <li><span aria-hidden="true">✓</span> Six erasable grid sheets</li>
            <li><span aria-hidden="true">✓</span> Non-permanent marker</li>
            <li><span aria-hidden="true">✓</span> Quick-use guide</li>
          </ul>

          <div className={styles.priceRow}>
            <strong>£28.99</strong>
            <span>One complete practice kit</span>
          </div>

          <a
            className={styles.cta}
            href={PRODUCT_URL}
            target="_blank"
            rel="noopener noreferrer"
            onClick={dismiss}
          >
            See the erasable practice kit <span aria-hidden="true">↗</span>
          </a>

          <div className={styles.footerRow}>
            <span>UK delivery via Royal Mail</span>
            <button type="button" onClick={dismiss}>Not now</button>
          </div>
        </div>
      </article>
    </dialog>
  );
}
