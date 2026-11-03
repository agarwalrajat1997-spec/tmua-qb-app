import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { requireIbUser } from "@/lib/ib/auth";
import { getMathsMock } from "@/lib/ib/maths-mock-model";
import { getMathsMockPaper, mathsMockPrompt } from "@/lib/ib/maths-mocks";
import MathsMockRunner from "../MathsMockRunner";

export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "IB Mathematics Mock | Thriving Scholars", robots: { index: false, follow: false } };
export default async function MathsMockPage({ params, searchParams }: { params: Promise<{ id: string }>; searchParams: Promise<{ attempt?: string }> }) {
  const [{ id }, query] = await Promise.all([params, searchParams]);
  const meta = getMathsMock(id);
  if (!meta) notFound();
  const destination = `/ib/maths-mocks/${id}${query.attempt ? `?attempt=${encodeURIComponent(query.attempt)}` : ""}`;
  const user = await requireIbUser(destination);
  const paper = await getMathsMockPaper(id);
  if (!paper) notFound();
  return <MathsMockRunner key={`${id}:${query.attempt ?? "new"}`} paper={mathsMockPrompt(paper, meta)} email={user.email} accountId={user.id} initialAttempt={query.attempt} />;
}
