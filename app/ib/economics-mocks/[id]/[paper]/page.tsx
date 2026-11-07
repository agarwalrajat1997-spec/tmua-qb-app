import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { requireIbUser } from "@/lib/ib/auth";
import { getEconomicsPaperMeta } from "@/lib/ib/economics-mock-model";
import { getEconomicsMockPaper, economicsMockPrompt } from "@/lib/ib/economics-mocks";
import EconomicsMockRunner from "../../EconomicsMockRunner";
export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "IB Economics Mock | Thriving Scholars", robots: { index: false, follow: false } };
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
    const meta = getEconomicsPaperMeta(id, paper);
    if (!meta || query.attempt && !/^[0-9a-f-]{36}$/i.test(query.attempt)) notFound();
    const destination = `/ib/economics-mocks/${id}/${paper}?course=${meta.course}${query.attempt ? `&attempt=${encodeURIComponent(query.attempt)}` : ""}`;
    const user = await requireIbUser(destination);
    const full = await getEconomicsMockPaper(id, paper);
    if (!full)
        notFound();
    return <EconomicsMockRunner key={`${id}-${paper}-${query.attempt ?? "new"}`} paper={economicsMockPrompt(full, meta)} email={user.email} accountId={user.id} initialAttempt={query.attempt}/>;
}
