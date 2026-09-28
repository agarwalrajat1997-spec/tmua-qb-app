import type { Metadata } from "next";
import type { ReactNode } from "react";
import ErasableNotepadPopup from "./_components/ErasableNotepadPopup";

export const metadata: Metadata = {
  title: "Thriving Scholars Apps",
  description: "Thriving Scholars Apps",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        {children}
        <ErasableNotepadPopup />
      </body>
    </html>
  );
}
