import type { Metadata } from "next";
import type { ReactNode } from "react";
import ErasableNotepadPopup from "./_components/ErasableNotepadPopup";
import TmuaFinalReminderLoader from "./_components/TmuaFinalReminderLoader";
import EsatFinalReminderLoader from "./_components/EsatFinalReminderLoader";

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
        <TmuaFinalReminderLoader />
        <EsatFinalReminderLoader />
      </body>
    </html>
  );
}
