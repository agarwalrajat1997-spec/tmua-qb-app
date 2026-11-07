import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { requireIbUser } from "@/lib/ib/auth";
import { getChemistryPaperMeta } from "@/lib/ib/chemistry-mock-model";
import { getChemistryMockPaper, chemistryMockPrompt } from "@/lib/ib/chemistry-mocks";
import ChemistryMockRunner from "../../ChemistryMockRunner";
export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "IB Chemistry Mock | Thriving Scholars", robots: { index: false, follow: false } };
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
    if (paper !== "1" && paper !== "2")
        notFound();
    const meta = getChemistryPaperMeta(id, paper);
    if (!meta || query.attempt && !/^[0-9a-f-]{36}$/i.test(query.attempt)) notFound();
    const destination = `/ib/chemistry-mocks/${id}/${paper}?course=${meta.course}${query.attempt ? `&attempt=${encodeURIComponent(query.attempt)}` : ""}`;
    const user = await requireIbUser(destination);
    const full = await getChemistryMockPaper(id, paper);
    if (!full)
        notFound();
    return <ChemistryMockRunner key={`${id}-${paper}-${query.attempt ?? "new"}`} paper={chemistryMockPrompt(full, meta)} email={user.email} accountId={user.id} initialAttempt={query.attempt}/>;
}
