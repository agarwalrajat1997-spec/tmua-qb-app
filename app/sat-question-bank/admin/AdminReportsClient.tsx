"use client";

/* eslint-disable @next/next/no-img-element */

import { useCallback, useEffect, useMemo, useState } from "react";
import styles from "./admin.module.css";

type ReportStatus = "open" | "reviewing" | "resolved" | "dismissed";

type QuestionOption = {
  key?: string;
  html?: string;
  image_url?: string | null;
  image_alt?: string | null;
};

type QuestionAsset = {
  url?: string;
  image_url?: string;
  alt?: string;
  image_alt?: string;
};

type QuestionPreview = {
  qid: string;
  display_order: number;
  paper: string;
  topic: string | null;
  subtopic: string | null;
  difficulty: number | null;
  prompt_html: string;
  options: QuestionOption[];
  page_assets: QuestionAsset[];
  answer: string;
  solution_html: string | null;
  nice_tip_html: string | null;
};

type ReportRecord = {
  id: string;
  user_email: string;
  qid: string;
  report_text: string;
  context: Record<string, unknown>;
  status: ReportStatus;
  created_at: string;
  resolved_at: string | null;
  question: QuestionPreview | null;
};

const STATUS_LABELS: Record<ReportStatus, string> = {
  open: "Open",
  reviewing: "Reviewing",
  resolved: "Resolved",
  dismissed: "Dismissed",
};

function downloadFile(filename: string, type: string, content: string) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function csvCell(value: unknown) {
  return `"${String(value ?? "").replaceAll('"', '""')}"`;
}

export default function AdminReportsClient({
  adminEmail,
}: {
  adminEmail: string;
}) {
  const [reports, setReports] = useState<ReportRecord[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<"all" | ReportStatus>(
    "open"
  );
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const loadReports = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const response = await fetch("/api/sat/qb/admin/reports", {
        cache: "no-store",
      });
      const payload = await response.json();
      if (!response.ok || !payload.ok) {
        throw new Error(payload.error || "Could not load reports");
      }
      const nextReports = payload.reports as ReportRecord[];
      setReports(nextReports);
      setSelectedId((current) =>
        current && nextReports.some((report) => report.id === current)
          ? current
          : nextReports[0]?.id || null
      );
    } catch (loadError) {
      setError(
        loadError instanceof Error ? loadError.message : String(loadError)
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadReports();
  }, [loadReports]);

  const counts = useMemo(() => {
    const value: Record<ReportStatus, number> = {
      open: 0,
      reviewing: 0,
      resolved: 0,
      dismissed: 0,
    };
    reports.forEach((report) => {
      value[report.status] += 1;
    });
    return value;
  }, [reports]);

  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return reports.filter((report) => {
      if (statusFilter !== "all" && report.status !== statusFilter) return false;
      if (!needle) return true;
      const question = report.question;
      return [
        report.qid,
        report.user_email,
        report.report_text,
        question?.paper,
        question?.topic,
        question?.subtopic,
        question?.display_order,
      ]
        .filter((value) => value !== null && value !== undefined)
        .some((value) => String(value).toLowerCase().includes(needle));
    });
  }, [query, reports, statusFilter]);

  const selected =
    filtered.find((report) => report.id === selectedId) || filtered[0] || null;

  async function updateStatus(status: ReportStatus) {
    if (!selected || saving) return;
    setSaving(true);
    setError("");
    try {
      const response = await fetch(
        `/api/sat/qb/admin/reports/${encodeURIComponent(selected.id)}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ status }),
        }
      );
      const payload = await response.json();
      if (!response.ok || !payload.ok) {
        throw new Error(payload.error || "Could not update report");
      }
      await loadReports();
    } catch (saveError) {
      setError(
        saveError instanceof Error ? saveError.message : String(saveError)
      );
    } finally {
      setSaving(false);
    }
  }

  function exportJson() {
    downloadFile(
      `sat-question-reports-${new Date().toISOString().slice(0, 10)}.json`,
      "application/json",
      JSON.stringify(reports, null, 2)
    );
  }

  function exportCsv() {
    const rows = [
      [
        "id",
        "status",
        "created_at",
        "user_email",
        "qid",
        "display_order",
        "paper",
        "topic",
        "report_text",
      ],
      ...reports.map((report) => [
        report.id,
        report.status,
        report.created_at,
        report.user_email,
        report.qid,
        report.question?.display_order || "",
        report.question?.paper || "",
        report.question?.topic || "",
        report.report_text,
      ]),
    ];
    downloadFile(
      `sat-question-reports-${new Date().toISOString().slice(0, 10)}.csv`,
      "text/csv;charset=utf-8",
      rows.map((row) => row.map(csvCell).join(",")).join("\r\n")
    );
  }

  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <div>
          <p className={styles.eyebrow}>Thriving Scholars · SAT operations</p>
          <h1>SAT Question Report Queue</h1>
          <p className={styles.subtle}>Signed in as {adminEmail}</p>
        </div>
        <div className={styles.headerActions}>
          <a className={styles.secondaryButton} href="/sat-question-bank">
            Open question bank
          </a>
          <button className={styles.secondaryButton} onClick={exportCsv}>
            Export CSV
          </button>
          <button className={styles.secondaryButton} onClick={exportJson}>
            Export JSON
          </button>
        </div>
      </header>

      <section className={styles.stats} aria-label="Report totals">
        {(Object.keys(STATUS_LABELS) as ReportStatus[]).map((status) => (
          <button
            className={statusFilter === status ? styles.statActive : styles.stat}
            key={status}
            onClick={() => setStatusFilter(status)}
          >
            <span>{STATUS_LABELS[status]}</span>
            <strong>{counts[status]}</strong>
          </button>
        ))}
        <button
          className={statusFilter === "all" ? styles.statActive : styles.stat}
          onClick={() => setStatusFilter("all")}
        >
          <span>All</span>
          <strong>{reports.length}</strong>
        </button>
      </section>

      <section className={styles.toolbar}>
        <label>
          <span>Search reports</span>
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Question ID, student, topic or description"
          />
        </label>
        <button className={styles.primaryButton} onClick={() => void loadReports()}>
          Refresh
        </button>
      </section>

      {error ? <div className={styles.error}>{error}</div> : null}

      <section className={styles.workspace}>
        <aside className={styles.queue}>
          {loading ? <p className={styles.empty}>Loading reports…</p> : null}
          {!loading && filtered.length === 0 ? (
            <p className={styles.empty}>No reports match this view.</p>
          ) : null}
          {filtered.map((report) => (
            <button
              className={
                report.id === selected?.id ? styles.queueItemActive : styles.queueItem
              }
              key={report.id}
              onClick={() => setSelectedId(report.id)}
            >
              <span className={styles.queueTopline}>
                <strong>Q{report.question?.display_order || "?"}</strong>
                <span data-status={report.status}>{STATUS_LABELS[report.status]}</span>
              </span>
              <span>{report.qid}</span>
              <span>{report.user_email}</span>
              <small>{new Date(report.created_at).toLocaleString()}</small>
            </button>
          ))}
        </aside>

        <article className={styles.detail}>
          {!selected ? (
            <p className={styles.empty}>Select a report to inspect it.</p>
          ) : (
            <>
              <div className={styles.detailHeader}>
                <div>
                  <p className={styles.eyebrow}>{selected.qid}</p>
                  <h2>
                    Question {selected.question?.display_order || "?"} · {selected.question?.paper || "Unknown paper"}
                  </h2>
                  <p className={styles.subtle}>
                    {selected.question?.topic || "No topic"}
                    {selected.question?.subtopic
                      ? ` · ${selected.question.subtopic}`
                      : ""}
                    {selected.question?.difficulty
                      ? ` · Difficulty ${selected.question.difficulty}`
                      : ""}
                  </p>
                </div>
                <div className={styles.statusActions}>
                  <button disabled={saving} onClick={() => void updateStatus("reviewing")}>
                    Mark reviewing
                  </button>
                  <button disabled={saving} onClick={() => void updateStatus("resolved")}>
                    Resolve
                  </button>
                  <button disabled={saving} onClick={() => void updateStatus("dismissed")}>
                    Dismiss
                  </button>
                  <button disabled={saving} onClick={() => void updateStatus("open")}>
                    Reopen
                  </button>
                </div>
              </div>

              <section className={styles.reportCard}>
                <h3>Student report</h3>
                <p>{selected.report_text}</p>
                <dl>
                  <div><dt>Student</dt><dd>{selected.user_email}</dd></div>
                  <div><dt>Submitted</dt><dd>{new Date(selected.created_at).toLocaleString()}</dd></div>
                  <div><dt>Status</dt><dd>{STATUS_LABELS[selected.status]}</dd></div>
                </dl>
              </section>

              {selected.question ? (
                <section className={styles.questionCard}>
                  <h3>Question preview</h3>
                  {selected.question.page_assets?.map((asset, index) => {
                    const src = asset.url || asset.image_url;
                    return src ? (
                      <img
                        className={styles.questionImage}
                        key={`${src}-${index}`}
                        src={src}
                        alt={asset.alt || asset.image_alt || "Question diagram"}
                      />
                    ) : null;
                  })}
                  <div
                    className={styles.richText}
                    dangerouslySetInnerHTML={{
                      __html: selected.question.prompt_html || "",
                    }}
                  />
                  <ol className={styles.options}>
                    {selected.question.options?.map((option, index) => (
                      <li key={`${option.key || index}-${index}`}>
                        <strong>{option.key || String.fromCharCode(65 + index)}</strong>
                        <div
                          dangerouslySetInnerHTML={{ __html: option.html || "" }}
                        />
                        {option.image_url ? (
                          <img
                            className={styles.optionImage}
                            src={option.image_url}
                            alt={option.image_alt || `Option ${option.key || index + 1}`}
                          />
                        ) : null}
                      </li>
                    ))}
                  </ol>
                  <div className={styles.answer}>Correct answer: {selected.question.answer}</div>
                  <h3>Solution</h3>
                  <div
                    className={styles.richText}
                    dangerouslySetInnerHTML={{
                      __html: selected.question.solution_html || "No solution supplied.",
                    }}
                  />
                  {selected.question.nice_tip_html ? (
                    <div
                      className={styles.tip}
                      dangerouslySetInnerHTML={{
                        __html: selected.question.nice_tip_html,
                      }}
                    />
                  ) : null}
                </section>
              ) : (
                <div className={styles.error}>The linked question could not be loaded.</div>
              )}
            </>
          )}
        </article>
      </section>
    </main>
  );
}
