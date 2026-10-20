"use client";

import { useEffect, useRef } from "react";
import { completeImplicitLogin } from "@/lib/auth/implicit-callback";

export default function CallbackBridge() {
  const started = useRef(false);
  useEffect(() => {
    // React strict-mode remount checks must not consume a cleared fragment twice.
    if (started.current) return;
    started.current = true;
    void completeImplicitLogin().then((destination) => {
      window.location.replace(destination);
    });
  }, []);

  return (
    <main style={{ maxWidth: 520, margin: "12vh auto", padding: 24, fontFamily: "system-ui, sans-serif", color: "#5b0e0e" }}>
      <h1>Opening your Thriving Scholars portal</h1>
      <p role="status" aria-live="polite">Please wait while we verify your secure sign-in link.</p>
      <noscript>JavaScript is needed to finish signing in. Please enable it, then request a new link from the login page.</noscript>
    </main>
  );
}
