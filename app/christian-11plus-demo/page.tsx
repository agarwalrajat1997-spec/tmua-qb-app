export const metadata = {
  title: "Christian 11+ Demo | PDFtoCode",
  description: "Student-facing 11+ practice quiz demo.",
};

export const dynamic = "force-static";

export default function Christian11PlusDemoPage() {
  return (
    <main style={{ minHeight: "100vh", margin: 0, padding: 0, background: "#faf8f2" }}>
      <iframe
        id="live-demo"
        src="/pdftocode-11-plus/index.html#live-demo"
        title="Christian 11+ Demo"
        style={{
          width: "100%",
          height: "100vh",
          border: "0",
          display: "block",
          background: "#faf8f2",
        }}
      />
    </main>
  );
}
