import type { Metadata } from "next";
import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { requireIbUser } from "@/lib/ib/auth";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { getPhysicsPaperMeta } from "@/lib/ib/physics-mock-model";
import { getPhysicsMockPaper, physicsMockPrompt } from "@/lib/ib/physics-mocks";
import PhysicsMockRunner from "../../PhysicsMockRunner";
export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "IB Physics Mock | Thriving Scholars", robots: { index: false, follow: false } };
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
    const destination = `/ib/mocks/${id}/${paper}${query.attempt ? `?attempt=${encodeURIComponent(query.attempt)}` : ""}`;
    const user = await requireIbUser(destination), meta = getPhysicsPaperMeta(id, paper);
    if (!meta) {
        if (!/^physics-(sl|hl)-mock-0[1-3]$/.test(id))
            notFound();
        if (!query.attempt)
            redirect(`/ib?subject=physics-hl&course=${id.includes("-sl-") ? "sl" : "hl"}&view=mocks`);
        if (!/^[0-9a-f-]{36}$/i.test(query.attempt))
            notFound();
        const db = await createSupabaseServerClient();
        const { data, error } = await db.from("ib_physics_mock_attempts").select("id,mock_id,paper,answers,elapsed_seconds,submitted_at,self_marks").eq("user_id", user.id).eq("mock_id", id).eq("paper", paper).eq("id", query.attempt).maybeSingle();
        if (error)
            throw new Error("Saved attempt is temporarily unavailable.");
        if (!data)
            notFound();
        const [{ legacyReview }, { getMockItems }, { default: QuestionBody }, { questionPrompt }, { default: MathContent }] = await Promise.all([import("@/lib/ib/physics-mock-archive"), import("@/lib/ib/physics-mock-legacy"), import("@/app/ib/components/QuestionBody"), import("@/lib/ib/question"), import("@/app/ib/components/MathContent")]);
        const review = legacyReview(data), items = getMockItems(id, paper);
        return <main style={{ maxWidth: 960, margin: "auto", padding: 24 }}><Link href={`/ib?subject=physics-hl&course=${id.includes("-sl-") ? "sl" : "hl"}&view=mocks`}>← Physics mocks</Link><h1>Earlier saved Physics attempt</h1><p>Paper {paper} · {review.spec.minutes} minutes · {review.spec.marks} marks · {new Date(review.submittedAt).toLocaleDateString()}</p><h2>{review.score.total === null ? "Written marking pending" : `${review.score.total} / ${review.score.maximum}`}</h2><p>This saved attempt uses the earlier practice series and its original timing and marks. Written scores, where saved, are self-assessed.</p>{items.map(({ question: q, number, section }) => <details key={q.id}><summary>{section} · Question {number} · {q.marks} marks</summary><QuestionBody question={{ ...questionPrompt(q), number }}/>{q.markScheme.map(group => <section key={group.part}><h3>{group.part ? `Part (${group.part})` : "Worked solution"}</h3><p>Your response: {review.answers[group.part ? `${q.id}:${group.part}` : q.id] || "No typed response saved."}</p>{group.steps.map((step, i) => <div key={i}><strong>{step.code}</strong><MathContent>{step.text}</MathContent></div>)}</section>)}</details>)}</main>;
    }
    const full = await getPhysicsMockPaper(id, paper);
    if (!full)
        notFound();
    return <PhysicsMockRunner key={`${id}-${paper}-${query.attempt ?? "new"}`} paper={physicsMockPrompt(full, meta)} email={user.email} accountId={user.id} initialAttempt={query.attempt}/>;
}
