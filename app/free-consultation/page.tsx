export const metadata = {
  title: "Find Your University Pathway | Thriving Scholars",
  description: "A personalised academic and university pathway for students and parents.",
};

const PATHWAY_APP =
  "https://thriving-scholars-pathway.raj1291241.chatgpt.site/free-consultation";

export default function FreeConsultationPage() {
  return (
    <main
      style={{
        margin: 0,
        width: "100%",
        height: "100dvh",
        minHeight: "100vh",
        overflow: "hidden",
        background: "#FFF8EF",
      }}
    >
      <iframe
        src={PATHWAY_APP}
        title="Thriving Scholars University Pathway"
        style={{
          display: "block",
          width: "100%",
          height: "100%",
          border: 0,
          background: "#FFF8EF",
        }}
        allow="clipboard-write"
        referrerPolicy="strict-origin-when-cross-origin"
      />
    </main>
  );
}
