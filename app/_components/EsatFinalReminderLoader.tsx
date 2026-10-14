"use client";
import { useEffect } from "react";
import { usePathname } from "next/navigation";
import Script from "next/script";

export default function EsatFinalReminderLoader() {
  const pathname = usePathname();
  useEffect(() => {
    window.dispatchEvent(new Event("esat-reminder-route"));
  }, [pathname]);
  return <Script src="/esat-final-reminder.js" strategy="afterInteractive" />;
}
