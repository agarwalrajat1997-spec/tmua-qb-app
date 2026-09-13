const TESTS = [
  ["SAT Full-Length Test 1", "Reading & Writing + Math", "/sat-practice-tests/tests/sat-full-length-1/index.html"],
  ["SAT Full-Length Test 2", "Reading & Writing + Math", "/sat-practice-tests/tests/sat-full-length-2/index.html"],
  ["SAT Math Test 1", "Math only", "/sat-practice-tests/tests/sat-math-1/index.html"],
  ["SAT Math Test 2", "Math only", "/sat-practice-tests/tests/sat-math-2/index.html"],
  ["SAT Reading Test 1", "Reading and Writing only", "/sat-practice-tests/tests/sat-reading-1/index.html"],
  ["SAT Reading Test 2", "Reading and Writing only", "/sat-practice-tests/tests/sat-reading-2/index.html"],
];

export const metadata = {
  title: "SAT Practice Tests",
};

export default function SATPracticeTestsPage() {
  return (
    <main
      style={{
        minHeight: "100vh",
        background: "#f8fafc",
        padding: 28,
        fontFamily: "ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial",
      }}
    >
      <section style={{ maxWidth: 1100, margin: "0 auto" }}>
        <p style={{ margin: 0, fontWeight: 900, letterSpacing: ".12em", textTransform: "uppercase", color: "#8a1020" }}>
          Thriving Scholars
        </p>
        <h1 style={{ fontSize: 44, margin: "8px 0 10px", letterSpacing: "-.03em" }}>
          SAT Practice Tests
        </h1>
        <p style={{ color: "#475569", fontWeight: 700 }}>
          2 full-length tests, 2 Math tests and 2 Reading and Writing tests.
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 14, marginTop: 22 }}>
          {TESTS.map(([title, meta, href]) => (
            <a
              key={href}
              href={href}
              style={{
                background: "#fff",
                border: "1px solid #e5e7eb",
                borderRadius: 18,
                padding: 18,
                color: "inherit",
                textDecoration: "none",
                boxShadow: "0 10px 28px rgba(15,23,42,.08)",
              }}
            >
              <h2 style={{ margin: 0, fontSize: 20 }}>{title}</h2>
              <p style={{ margin: "8px 0 16px", color: "#64748b", fontWeight: 700 }}>{meta}</p>
              <span style={{ display: "inline-block", background: "#8a1020", color: "#fff", padding: "10px 14px", borderRadius: 12, fontWeight: 900 }}>
                Start →
              </span>
            </a>
          ))}
        </div>
      </section>
    </main>
  );
}
