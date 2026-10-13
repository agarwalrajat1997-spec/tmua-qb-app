"use client";
import { useEffect } from "react";
import { usePathname } from "next/navigation";
import Script from "next/script";

export default function TmuaFinalReminderLoader() {
  const pathname = usePathname();
  useEffect(() => {
    window.dispatchEvent(new Event("tmua-reminder-route"));
  }, [pathname]);
  return <Script src="/tmua-final-reminder.js" strategy="afterInteractive" />;
}
