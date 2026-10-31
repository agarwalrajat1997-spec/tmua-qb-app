import taxonomy from "../data/shortcut-taxonomy.json";

export type StudentMethod = {
  id: string;
  title: string;
  label: "Shortcut" | "Useful method";
  explanation: string;
  conditions: string[];
  limitations: string[];
};

export function studentText(value: unknown): string {
  if (typeof value !== "string") return "";
  return value
    .replace(/\(\s*SC\d{2}\s*\)/g, "")
    .replace(/\bSC\d{2}\b\s*[—–:-]\s*/g, "")
    .replace(/\bSC\d{2}\b/g, (id) =>
      taxonomy.find((entry) => entry.id === id)?.name ?? "this method")
    .trim();
}

function textList(value: unknown): string[] {
  const items = Array.isArray(value) ? value : typeof value === "string" ? [value] : [];
  return items.map(studentText).filter(Boolean);
}

// Positive classifications are explicit. Missing/unknown/rejected assessments
// never become student recommendations, and an ordinary method is not a shortcut.
export function studentMethods(value: unknown): StudentMethod[] {
  if (!Array.isArray(value)) return [];
  return value.flatMap((item, index) => {
    if (!item || typeof item !== "object") return [];
    const method = item as Record<string, unknown>;
    if (!["material_shortcut", "useful_ordinary_method"].includes(String(method.classification)) ||
        method.applicable === false || method.applies === false ||
        ["rejected", "not_applicable", "unsafe_here", "insufficient_information"].includes(String(method.status)))
      return [];
    const explanation = studentText(method.method_here);
    if (!explanation) return [];
    const label = method.classification === "material_shortcut" ? "Shortcut" : "Useful method";
    const family = taxonomy.find((entry) => entry.id === method.shortcut_id);
    return [{
      id: typeof method.shortcut_id === "string" ? method.shortcut_id : `method-${index}`,
      title: studentText(family?.name ?? method.title) || label,
      label,
      explanation,
      conditions: textList(method.conditions_checked),
      limitations: textList(method.limitations),
    } satisfies StudentMethod];
  });
}

// Presentation only: keep original saved errors and machine codes for recovery.
export function studentErrorMessage(value: unknown): string {
  const message = value instanceof Error ? value.message : typeof value === "string" ? value : "";
  if (/openai|\bapi\b|provider|credits?|quota|billing|not configured|unconfigured|service.?tier|rate.?limit/i.test(message))
    return "Feedback is temporarily unavailable. Your working is saved. Please try again later, or contact your teacher if this continues.";
  if (/source.?hash|snapshot|different question version|version does not match|reference belongs|exact audited|reference could not/i.test(message))
    return "This question could not be opened. Please reopen it from the question bank. Your saved working is unchanged.";
  if (/outcome cannot be verified|saved tracking|latest request|no new request|may still be running/i.test(message))
    return "Your working is saved. Use “Check saved review” to see whether your feedback is ready before trying again.";
  return message || "Something went wrong. Your saved working is unchanged. Please try again.";
}
