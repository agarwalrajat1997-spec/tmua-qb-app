export type PracticeSettings = {
  version: 1;
  order: "sequential" | "randomised";
  time_multiplier: 1 | 1.25 | 1.5;
  question_order: number[];
  section_sizes: number[];
  base_seconds_per_section: number;
};

export type StandardTimeUnit = {
  label: string; actual_raw: number; total_questions: number;
  deduction: number; adjusted_raw: number; estimated_score: number | null;
};
export type StandardTimeEstimate = {
  policy_version: "ts-standard-time-equivalent-v1";
  label: "Estimated standard-time equivalent";
  provisional: true; official: false; test_id: string;
  time_multiplier: PracticeSettings["time_multiplier"];
  actual_raw: number; total_questions: number; deduction_per_40: number;
  adjusted_raw: number; estimated_score: number | null; units: StandardTimeUnit[];
  note: string; canonical_key_sha256: string; answers_sha256: string;
  conversion_profile: string | null; conversion_version: string | null;
};

export function validatePracticeSettings(
  value: unknown,
  sectionSizes: readonly number[],
  baseSeconds: number,
): PracticeSettings | null {
  if (value === undefined) return null;
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error("practice_settings must be an object.");
  const input = value as Record<string, unknown>;
  if (input.version !== 1 || (input.order !== "sequential" && input.order !== "randomised") ||
      ![1, 1.25, 1.5].includes(input.time_multiplier as number)) throw new Error("Invalid practice settings version, question order or time allowance.");
  if (!Array.isArray(input.section_sizes) || input.section_sizes.length !== sectionSizes.length ||
      input.section_sizes.some((size, i) => size !== sectionSizes[i]) || input.base_seconds_per_section !== baseSeconds) {
    throw new Error("Practice settings do not match this test's sections and standard time.");
  }
  const order = input.question_order;
  const total = sectionSizes.reduce((sum, size) => sum + size, 0);
  if (!Array.isArray(order) || order.length !== total || new Set(order).size !== total) throw new Error("Question order must contain every original question once.");
  let offset = 0;
  for (const size of sectionSizes) {
    for (let displayed = offset; displayed < offset + size; displayed += 1) {
      const original = order[displayed];
      if (!Number.isInteger(original) || original < offset || original >= offset + size ||
          (input.order === "sequential" && original !== displayed)) throw new Error("Questions must retain their original section; sequential mode must retain original order.");
    }
    offset += size;
  }
  return {
    version: 1, order: input.order as PracticeSettings["order"],
    time_multiplier: input.time_multiplier as PracticeSettings["time_multiplier"],
    question_order: order.slice(), section_sizes: [...sectionSizes], base_seconds_per_section: baseSeconds,
  };
}

export function formatPracticeSettings(settings: PracticeSettings | null | undefined): string {
  if (!settings) return "";
  const seconds = settings.base_seconds_per_section * settings.time_multiplier;
  const minutes = Math.floor(seconds / 60);
  const remainder = seconds % 60;
  return `${settings.order === "randomised" ? "Randomised questions" : "Original order"} · ${settings.time_multiplier === 1 ? "Standard time" : `+${Math.round((settings.time_multiplier - 1) * 100)}% extra time`} · ${minutes} min${remainder ? ` ${remainder} sec` : ""} per section`;
}
