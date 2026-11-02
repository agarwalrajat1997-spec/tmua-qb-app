"use client";

import Link from "next/link";
import { useState, type ComponentProps } from "react";

/** Warm the intended destination without fetching every question on the page. */
export default function IbLink({ href, onMouseEnter, onFocus, onTouchStart, ...props }: ComponentProps<typeof Link>) {
  const [warmed, setWarmed] = useState<string | null>(null);
  function prefetch() {
    if (typeof href !== "string" || !href.startsWith("/ib") || warmed === href) return;
    setWarmed(href);
  }
  return <Link {...props} href={href} prefetch={warmed === href}
    onMouseEnter={event => { prefetch(); onMouseEnter?.(event); }}
    onFocus={event => { prefetch(); onFocus?.(event); }}
    onTouchStart={event => { prefetch(); onTouchStart?.(event); }} />;
}
