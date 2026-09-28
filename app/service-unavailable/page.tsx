import { safeLoginDestination } from "@/lib/auth/login-destination";

export const dynamic = "force-dynamic";

export default async function ServiceUnavailable({ searchParams }: {
  searchParams: Promise<{ next?: string }>;
}) {
  const { next } = await searchParams;
  const retry = safeLoginDestination(next);
  return <main style={{ maxWidth: 560, margin: "12vh auto", padding: 28, fontFamily: "Arial, sans-serif", lineHeight: 1.6 }}>
    <strong style={{ color: "#75252b" }}>Thriving Scholars</strong>
    <h1>We’re having trouble loading your portal</h1>
    <p>We couldn’t check your access just now. Please wait a moment and try again.</p>
    <p><a href={retry} style={{ display: "inline-block", padding: "12px 22px", background: "#75252b", color: "white", borderRadius: 8 }}>Try again</a></p>
    <p>If this continues, <a href="https://wa.me/447459070019">message us on WhatsApp: +44 7459 070019</a>.</p>
  </main>;
}
