"use client";

import { SERVICE_RETRY_MESSAGE } from "@/lib/auth/service-recovery";

export default function ServiceRetry({ onRetry }: { onRetry: () => void }) {
  return <main role="alert" style={{ maxWidth: 560, margin: "12vh auto", padding: 28, lineHeight: 1.6 }}>
    <strong style={{ color: "#75252b" }}>Thriving Scholars</strong>
    <h1>Your portal is temporarily unavailable</h1>
    <p>{SERVICE_RETRY_MESSAGE}</p>
    <button type="button" onClick={onRetry} style={{ padding: "12px 22px", border: 0, borderRadius: 8, background: "#75252b", color: "white", cursor: "pointer" }}>Try again</button>
    <p>If you need help, <a href="https://wa.me/447459070019">WhatsApp us on +44 7459 070019</a>.</p>
  </main>;
}
