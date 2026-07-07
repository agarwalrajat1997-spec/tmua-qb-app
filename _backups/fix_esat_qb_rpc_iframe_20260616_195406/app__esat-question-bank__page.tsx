export const dynamic = "force-dynamic";
export const revalidate = 0;

export default function ESATQuestionBankPage() {
  return (
    <main
      style={{
        margin: 0,
        height: "100vh",
        width: "100vw",
        overflow: "hidden",
        background: "#f8fafc",
      }}
    >
      <iframe
        src="/esat-question-bank/index.html"
        title="ESAT Question Bank"
        style={{
          border: 0,
          width: "100%",
          height: "100%",
          display: "block",
        }}
      />
    </main>
  );
}
