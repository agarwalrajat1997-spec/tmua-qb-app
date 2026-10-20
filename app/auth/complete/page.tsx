import type { Metadata } from "next";
import CallbackBridge from "./CallbackBridge";

export const dynamic = "force-dynamic";
export const metadata: Metadata = {
  title: "Secure sign-in | Thriving Scholars",
  referrer: "no-referrer",
  robots: { index: false, follow: false },
};

export default function CompleteSignInPage() {
  return <CallbackBridge />;
}
