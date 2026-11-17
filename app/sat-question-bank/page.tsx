export const metadata = {
  title: "SAT Question Bank",
};

import { redirect } from "next/navigation";

export default function SATQuestionBankPage() {
  // Top-level navigation preserves topic/category links on refresh and sharing.
  // Both routes retain their existing SAT access checks in proxy.ts.
  redirect("/sat-question-bank-app.html");
}

