"use client";

import { useEffect, useState } from "react";

type Exam = "AMC8" | "AMC10" | "AMC12";

type Summary = {
  qid: string;
  display_order: number;
  difficulty: number;
  topic: string;
  subtopic: string;
};

type Option = {
  label: string;
  html: string;
};

type Question = {
  qid: string;
  difficulty: number;
  topic: string;
  subtopic: string;
  prompt_html: string;
  options: Option[];
  page_assets?: any[];
  question_assets?: any[];
};

function labelFor(exam: Exam) {
  if (exam === "AMC8") return "AMC 8";
  if (exam === "AMC10") return "AMC 10";
  return "AMC 12";
}

function renderAsset(asset: any, idx: number) {
  const url = typeof asset === "string" ? asset : asset?.url || asset?.src;
  const label = typeof asset === "string" ? "" : asset?.label || asset?.caption || "";

  if (!url) return null;

  return (
    <figure key={idx} className="qa-figure">
      <img src={url} alt={label || "Question image"} />
      {label ? <figcaption>{label}</figcaption> : null}
    </figure>
  );
}

export default function AmcQuestionBankClient({
  exam,
  title,
}: {
  exam: Exam;
  title: string;
}) {
  const [list, setList] = useState<Summary[]>([]);
  const [index, setIndex] = useState(0);
  const [question, setQuestion] = useState<Question | null>(null);
  const [selected, setSelected] = useState("");
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const current = list[index];

  useEffect(() => {
    async function loadList() {
      setLoading(true);
      setError("");

      const res = await fetch(`/api/amc/list?exam=${exam}`, {
        cache: "no-store",
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        setError(data.error || "Could not load questions.");
        setLoading(false);
        return;
      }

      setList(data.questions || []);
      setIndex(0);
      setLoading(false);
    }

    loadList();
  }, [exam]);

  useEffect(() => {
    async function loadQuestion() {
      if (!current?.qid) return;

      setQuestion(null);
      setSelected("");
      setResult(null);
      setError("");

      const res = await fetch(`/api/amc/question?exam=${exam}&qid=${encodeURIComponent(current.qid)}`, {
        cache: "no-store",
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        setError(data.error || "Could not load question.");
        return;
      }

      setQuestion(data.question);

      setTimeout(() => {
        // @ts-ignore
        window.MathJax?.typesetPromise?.();
      }, 80);
    }

    loadQuestion();
  }, [exam, current?.qid]);

  useEffect(() => {
    setTimeout(() => {
      // @ts-ignore
      window.MathJax?.typesetPromise?.();
    }, 80);
  }, [question, result]);

  async function checkAnswer() {
    if (!question || !selected) return;

    const res = await fetch("/api/amc/check", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        exam,
        qid: question.qid,
        selected,
      }),
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      setError(data.error || "Could not check answer.");
      return;
    }

    setResult(data);
  }

  return (
    <main>
      <script
        dangerouslySetInnerHTML={{
          __html: `
            window.MathJax = {
              tex: {
                inlineMath: [['\\\\(','\\\\)']],
                displayMath: [['\\\\[','\\\\]']]
              },
              options: {
                skipHtmlTags: ['script','noscript','style','textarea','pre','code']
              }
            };
          `,
        }}
      />
      <script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" />

      <style jsx global>{`
        body {
          margin: 0;
          font-family: Georgia, serif;
          background: white;
          color: #0b1220;
        }

        .top {
          background: #0074c1;
          color: white;
          padding: 12px 18px;
          display: flex;
          justify-content: space-between;
          gap: 12px;
          flex-wrap: wrap;
          align-items: center;
        }

        .brand {
          font-weight: 900;
          font-size: 19px;
        }

        .tabs {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }

        .tabs a {
          color: white;
          border: 1px solid rgba(255,255,255,.55);
          border-radius: 999px;
          padding: 7px 11px;
          text-decoration: none;
          font-size: 14px;
        }

        .tabs a.active {
          background: white;
          color: #111827;
          font-weight: 900;
        }

        .wrap {
          max-width: 1150px;
          margin: 0 auto;
          padding: 20px 22px 90px;
        }

        .card {
          border: 1px solid #cbd5e1;
          border-radius: 14px;
          box-shadow: 0 10px 24px rgba(15,23,42,.10);
          padding: 18px;
        }

        .head {
          display: flex;
          justify-content: space-between;
          gap: 12px;
          flex-wrap: wrap;
          margin-bottom: 14px;
        }

        .title {
          margin: 0;
          font-size: 24px;
          font-weight: 900;
        }

        .pill {
          display: inline-block;
          border: 1px solid #e5e7eb;
          background: #f9fafb;
          border-radius: 999px;
          padding: 6px 10px;
          font-size: 13px;
          margin: 3px;
        }

        .prompt {
          font-size: 19px;
          line-height: 1.65;
        }

        .option {
          display: block;
          border: 1px solid #e5e7eb;
          border-radius: 12px;
          margin: 10px 0;
          padding: 10px 12px;
          cursor: pointer;
        }

        .option.selected {
          border-color: #0074c1;
          background: #eef6ff;
        }

        .option.correct {
          border-color: rgba(34,197,94,.45);
          background: rgba(34,197,94,.10);
        }

        .option.wrong {
          border-color: rgba(239,68,68,.45);
          background: rgba(239,68,68,.10);
        }

        .option-row {
          display: flex;
          gap: 10px;
          align-items: flex-start;
        }

        .option-letter {
          font-weight: 900;
          min-width: 24px;
        }

        .btns {
          display: flex;
          gap: 10px;
          flex-wrap: wrap;
          margin-top: 18px;
        }

        button {
          border: none;
          background: #005fa3;
          color: white;
          border-radius: 8px;
          padding: 9px 13px;
          cursor: pointer;
          font-size: 14px;
        }

        button.secondary {
          background: #f3f4f6;
          color: #111827;
          border: 1px solid #d1d5db;
        }

        button:disabled {
          opacity: .55;
          cursor: not-allowed;
        }

        .solution {
          margin-top: 14px;
          padding: 13px;
          border: 1px dashed #94a3b8;
          background: #fbfdff;
          border-radius: 12px;
          font-size: 17px;
          line-height: 1.6;
        }

        .error {
          border: 1px solid rgba(239,68,68,.35);
          background: rgba(239,68,68,.10);
          padding: 12px;
          border-radius: 12px;
          margin-bottom: 14px;
        }

        .qa-figure {
          text-align: center;
          margin: 14px 0 18px;
        }

        .qa-figure img {
          max-width: 360px;
          width: 100%;
          height: auto;
          border: 1.5px solid #e5e7eb;
          border-radius: 12px;
          padding: 10px;
          background: white;
        }

        .footer {
          position: fixed;
          bottom: 0;
          left: 0;
          right: 0;
          background: #0074c1;
          color: white;
          padding: 10px 18px;
        }

        .footer-inner {
          max-width: 1150px;
          margin: 0 auto;
          display: flex;
          justify-content: space-between;
          gap: 12px;
          flex-wrap: wrap;
        }
      `}</style>

      <div className="top">
        <div>
          <div className="brand">Thriving Scholars</div>
          <div>{title}</div>
        </div>

        <div className="tabs">
          <a className={exam === "AMC8" ? "active" : ""} href="/amc-8-question-bank">AMC 8</a>
          <a className={exam === "AMC10" ? "active" : ""} href="/amc-10-question-bank">AMC 10</a>
          <a className={exam === "AMC12" ? "active" : ""} href="/amc-12-question-bank">AMC 12</a>
        </div>
      </div>

      <div className="wrap">
        {error ? <div className="error">{error}</div> : null}

        {loading ? (
          <div className="card">Loading {labelFor(exam)} questions...</div>
        ) : !list.length ? (
          <div className="card">No questions found for {labelFor(exam)}.</div>
        ) : (
          <div className="card">
            <div className="head">
              <div>
                <h1 className="title">Question {index + 1}</h1>
                <span className="pill">{index + 1} / {list.length}</span>
              </div>

              <div>
                <span className="pill">{labelFor(exam)}</span>
                {question?.topic ? <span className="pill">{question.topic}</span> : null}
                {question?.subtopic ? <span className="pill">{question.subtopic}</span> : null}
                {question?.difficulty ? <span className="pill">Difficulty {question.difficulty}</span> : null}
              </div>
            </div>

            {!question ? (
              <p>Loading question...</p>
            ) : (
              <>
                <div className="prompt" dangerouslySetInnerHTML={{ __html: question.prompt_html }} />

                {Array.isArray(question.page_assets) ? question.page_assets.map(renderAsset) : null}
                {Array.isArray(question.question_assets) ? question.question_assets.map(renderAsset) : null}

                <div>
                  {question.options.map((opt) => {
                    const isSelected = selected === opt.label;
                    const isCorrect = result?.answer === opt.label;
                    const isWrong = result && isSelected && !isCorrect;

                    return (
                      <label
                        key={opt.label}
                        className={[
                          "option",
                          isSelected ? "selected" : "",
                          isCorrect ? "correct" : "",
                          isWrong ? "wrong" : "",
                        ].join(" ")}
                      >
                        <div className="option-row">
                          <input
                            type="radio"
                            checked={isSelected}
                            disabled={!!result}
                            onChange={() => setSelected(opt.label)}
                          />
                          <span className="option-letter">{opt.label}</span>
                          <span dangerouslySetInnerHTML={{ __html: opt.html }} />
                        </div>
                      </label>
                    );
                  })}
                </div>

                <div className="btns">
                  <button disabled={!selected || !!result} onClick={checkAnswer}>
                    Check Answer
                  </button>

                  <button className="secondary" disabled={index <= 0} onClick={() => setIndex(index - 1)}>
                    Previous
                  </button>

                  <button className="secondary" disabled={index >= list.length - 1} onClick={() => setIndex(index + 1)}>
                    Next
                  </button>
                </div>

                {result ? (
                  <div className="solution">
                    <p>
                      <strong>
                        {result.correct ? "Correct." : `Incorrect. Correct answer: ${result.answer}.`}
                      </strong>
                    </p>
                    <div dangerouslySetInnerHTML={{ __html: result.solution_html || "" }} />
                  </div>
                ) : null}
              </>
            )}
          </div>
        )}
      </div>

      <div className="footer">
        <div className="footer-inner">
          <div>{list.length ? `${index + 1} / ${list.length}` : "0 / 0"}</div>
          <div>{labelFor(exam)} Question Bank</div>
        </div>
      </div>
    </main>
  );
}
