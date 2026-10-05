import { formatPracticeSettings, type PracticeSettings, type StandardTimeEstimate } from "@/lib/practice-settings";

type Props = {
  settings?: PracticeSettings | null;
  estimate?: StandardTimeEstimate | null;
  detailed?: boolean;
  programme?: "TMUA" | "ESAT";
};

/** Keep the earned mark separate from the explicitly provisional extra-time estimate. */
export default function PracticeAttemptSettings({ settings, estimate, detailed = false, programme = "TMUA" }: Props) {
  if (!settings) return null;
  const adjusted = estimate && estimate.time_multiplier > 1 ? estimate : null;
  return (
    <div style={{ marginTop: 7, marginBottom: 10, fontSize: 12, lineHeight: 1.5 }}>
      <div>{formatPracticeSettings(settings)}</div>
      {adjusted ? (
        <div style={{ marginTop: 6, padding: "8px 10px", background: "#fff6df", color: "#601c20", borderRadius: 8, borderLeft: "3px solid #e8a132" }}>
          <strong>Estimated standard-time equivalent{adjusted.estimated_score != null ? `: ${Number(adjusted.estimated_score).toFixed(1)}/9` : ""}</strong>
          <div>Provisional practice estimate · actual raw mark unchanged.</div>
          {adjusted.estimated_score == null ? <div>Converted estimate temporarily unavailable; your raw marks are retained.</div> : null}
          {programme === "ESAT" ? <div>Mean of module estimates—not an official combined ESAT score.</div> : null}
          {detailed ? (
            <>
              <p style={{ margin: "6px 0" }}>{adjusted.note}</p>
              <div>{adjusted.units.map((unit) => `${unit.label}: ${unit.actual_raw}/${unit.total_questions} actual → ${unit.adjusted_raw}/${unit.total_questions} estimated`).join(" · ")}</div>
            </>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
