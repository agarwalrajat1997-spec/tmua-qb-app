"use client";

import { useEffect, useState } from "react";

export default function NoProductsLogoutButton() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    function checkNoProductsPage() {
      const text = document.body?.innerText || "";
      setShow(
        text.includes("No products enabled") &&
        text.includes("no active product access")
      );
    }

    checkNoProductsPage();

    const observer = new MutationObserver(checkNoProductsPage);
    observer.observe(document.body, {
      childList: true,
      subtree: true,
      characterData: true,
    });

    return () => observer.disconnect();
  }, []);

  if (!show) return null;

  return (
    <a
      id="ts-no-products-logout-btn"
      href="/api/logout"
      style={{
        position: "fixed",
        top: "18px",
        right: "24px",
        zIndex: 9999,
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "10px 16px",
        borderRadius: "999px",
        border: "1px solid rgba(15, 23, 42, 0.16)",
        background: "#ffffff",
        color: "#0f172a",
        fontSize: "14px",
        fontWeight: 700,
        textDecoration: "none",
        boxShadow: "0 10px 24px rgba(15, 23, 42, 0.14)",
      }}
    >
      Logout
    </a>
  );
}
