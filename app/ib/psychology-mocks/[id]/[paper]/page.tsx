import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { requireIbUser } from "@/lib/ib/auth";
import { getPsychologyPaperMeta } from "@/lib/ib/psychology-mock-model";
import { getPsychologyMockPaper, psychologyMockPrompt } from "@/lib/ib/psychology-mocks";
import PsychologyMockRunner from "../../PsychologyMockRunner";
export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "IB Psychology Mock | Thriving Scholars", robots: { index: false, follow: false } };
export default async function MockPage({ params, searchParams }: {
    params: Promise<{
        id: string;
        paper: string;
    }>;
    searchParams: Promise<{
        attempt?: string;
    }>;
}) {
    const [{ id, paper }, query] = await Promise.all([params, searchParams]);
    if (paper !== "1" && paper !== "2" && paper !== "3")
        notFound();
    const meta = getPsychologyPaperMeta(id, paper);
    if (!meta || query.attempt && !/^[0-9a-f-]{36}$/i.test(query.attempt)) notFound();
    const destination = `/ib/psychology-mocks/${id}/${paper}?course=${meta.course}${query.attempt ? `&attempt=${encodeURIComponent(query.attempt)}` : ""}`;
    const user = await requireIbUser(destination);
    const full = await getPsychologyMockPaper(id, paper);
    if (!full)
        notFound();
    return <PsychologyMockRunner key={`${id}-${paper}-${query.attempt ?? "new"}`} paper={psychologyMockPrompt(full, meta)} email={user.email} accountId={user.id} initialAttempt={query.attempt}/>;
}
