export const metadata = {
  title: "SAT Question Bank",
};

export default function SATQuestionBankPage() {
  return (
    <main style={{ margin: 0 }}>
      <iframe
        className="tsQbIframe"
        src="/sat-question-bank/index.html"
        style={{ width: "100%", height: "100vh", border: "0" }}
        title="SAT Question Bank"
      />
    </main>
  );
}
