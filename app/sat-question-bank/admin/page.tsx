import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { requireSATAdmin } from "../../api/sat/qb/admin/_server";
import AdminReportsClient from "./AdminReportsClient";

export const metadata: Metadata = {
  title: "SAT Report Queue | Thriving Scholars",
  robots: { index: false, follow: false },
};

export default async function SATQuestionReportsAdminPage() {
  const access = await requireSATAdmin();
  if (!access.ok) notFound();

  return <AdminReportsClient adminEmail={access.email} />;
}
