export const dynamic = "force-dynamic";
export const revalidate = 0;

export default function ESATQuestionBankPage() {
  return (
    <>
      <style
        dangerouslySetInnerHTML={{
          __html: `
            html,
            body {
              margin: 0 !important;
              padding: 0 !important;
              overflow: hidden !important;
              width: 100% !important;
              height: 100% !important;
              background: #f8fafc !important;
            }
          `,
        }}
      />

      <main
        style={{
          position: "fixed",
          inset: 0,
          width: "100%",
          height: "100dvh",
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
            overflow: "hidden",
          }}
        />
      </main>
    </>
  );
}
