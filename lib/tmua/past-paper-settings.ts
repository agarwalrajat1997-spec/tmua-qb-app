/** Presentation settings only. Answers always retain their original question and option identities. */
export type TmuaPastPaperSettings = {
  version: 1;
  order: "sequential" | "randomised";
  time_multiplier: 1 | 1.25 | 1.5;
  seconds_per_paper: 4500 | 5625 | 6750;
  question_order: number[];
  option_order: string[][];
};

// Original option counts, verified against all 360 question templates by the regression check.
// No answer keys or scoring policy are exposed by this shared presentation module.
export const TMUA_PAST_PAPER_OPTION_COUNTS: Readonly<Record<string, readonly number[]>> = {
  "full-official-2016": [8, 6, 6, 7, 6, 6, 5, 8, 6, 7, 6, 6, 5, 6, 5, 5, 6, 6, 5, 5, 6, 4, 6, 5, 5, 8, 8, 8, 8, 6, 8, 6, 6, 5, 5, 5, 8, 6, 7, 8],
  "full-official-2017": [6, 6, 5, 5, 8, 6, 4, 4, 8, 6, 5, 6, 6, 6, 8, 7, 5, 6, 6, 5, 6, 5, 7, 5, 8, 8, 8, 5, 7, 5, 7, 6, 8, 8, 6, 4, 8, 6, 8, 5],
  "full-official-2018": [7, 6, 5, 7, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 5, 5, 6, 6, 6, 6, 8, 6, 4, 5, 7, 8, 7, 8, 8, 8, 6, 8, 8, 8, 4, 6, 4, 6],
  "full-official-2019": [6, 8, 8, 8, 6, 5, 7, 5, 7, 6, 8, 6, 6, 6, 6, 8, 8, 7, 6, 6, 5, 6, 8, 8, 4, 7, 4, 8, 6, 4, 8, 6, 4, 8, 5, 8, 4, 8, 7, 7],
  "full-official-2020": [6, 6, 7, 6, 5, 6, 6, 6, 6, 8, 6, 7, 6, 6, 6, 8, 6, 6, 6, 6, 6, 8, 7, 8, 6, 8, 8, 5, 6, 8, 8, 6, 4, 4, 6, 6, 6, 8, 8, 6],
  "full-official-2021": [7, 7, 8, 6, 6, 6, 8, 6, 7, 6, 7, 6, 6, 6, 6, 5, 5, 8, 6, 6, 7, 6, 8, 8, 5, 4, 8, 4, 8, 7, 6, 8, 8, 8, 6, 6, 6, 8, 8, 8],
  "full-official-2022": [8, 6, 6, 7, 8, 7, 6, 5, 7, 8, 8, 5, 8, 6, 8, 6, 6, 6, 6, 5, 5, 5, 8, 5, 8, 4, 7, 6, 7, 8, 5, 6, 6, 7, 8, 8, 5, 8, 5, 6],
  "full-official-2023": [7, 6, 6, 5, 6, 7, 7, 5, 6, 6, 6, 7, 7, 8, 6, 7, 6, 8, 8, 8, 8, 8, 8, 8, 4, 8, 6, 8, 8, 7, 8, 4, 5, 7, 8, 8, 6, 6, 8, 8],
  "full-specimen": [6, 7, 5, 5, 6, 5, 6, 8, 4, 4, 5, 5, 5, 5, 5, 8, 5, 7, 4, 7, 5, 5, 5, 5, 6, 6, 4, 5, 6, 6, 5, 8, 6, 4, 8, 6, 6, 6, 7, 8],
};

export function validateTmuaPastPaperSettings(testId: string, value: unknown): TmuaPastPaperSettings | null {
  if (value === undefined) return null; // Existing clients and historical attempts stay compatible.
  const counts = Object.prototype.hasOwnProperty.call(TMUA_PAST_PAPER_OPTION_COUNTS, testId)
    ? TMUA_PAST_PAPER_OPTION_COUNTS[testId] : undefined;
  if (!counts) throw new Error("attempt_settings are supported only for TMUA past papers.");
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("attempt_settings must be an object.");
  }
  const input = value as Record<string, unknown>;
  if (input.version !== 1 || (input.order !== "sequential" && input.order !== "randomised")) {
    throw new Error("Invalid past-paper settings version or question order.");
  }
  if (![1, 1.25, 1.5].includes(input.time_multiplier as number) ||
      input.seconds_per_paper !== 4500 * (input.time_multiplier as number)) {
    throw new Error("Invalid past-paper time allowance.");
  }
  const order = input.question_order;
  if (!Array.isArray(order) || order.length !== 40 || new Set(order).size !== 40 ||
      order.some((original, displayed) => !Number.isInteger(original) || original < 0 || original >= 40 ||
        Math.floor(original / 20) !== Math.floor(displayed / 20))) {
    throw new Error("Question order must include each question once within its original paper.");
  }
  const options = input.option_order;
  if (!Array.isArray(options) || options.length !== 40 || options.some((letters, index) => {
    const expected = "ABCDEFGH".slice(0, counts[index]);
    return !Array.isArray(letters) || letters.length !== expected.length ||
      letters.some(letter => typeof letter !== "string" || !expected.includes(letter) || letter.length !== 1) ||
      new Set(letters).size !== expected.length;
  })) {
    throw new Error("Option order must include each original answer option exactly once.");
  }
  // This option explicitly refers to A–D. Its meaning depends on E staying last.
  if (testId === "full-official-2022" && options[23][4] !== "E") {
    throw new Error("The final option of 2022 Paper 2 Question 4 must retain its original position.");
  }
  if (input.order === "sequential" &&
      (order.some((original, displayed) => original !== displayed) ||
       options.some((letters, index) => letters.join("") !== "ABCDEFGH".slice(0, counts[index])))) {
    throw new Error("Sequential mode must retain the original question and answer order.");
  }
  return {
    version: 1,
    order: input.order as TmuaPastPaperSettings["order"],
    time_multiplier: input.time_multiplier as TmuaPastPaperSettings["time_multiplier"],
    seconds_per_paper: input.seconds_per_paper as TmuaPastPaperSettings["seconds_per_paper"],
    question_order: order.slice(),
    option_order: options.map(letters => letters.slice()),
  };
}

/** Validate stored metadata defensively without making older attempt histories unreadable. */
export function readTmuaPastPaperSettings(testId: string, metadata: unknown): TmuaPastPaperSettings | null {
  if (!metadata || typeof metadata !== "object" || Array.isArray(metadata)) return null;
  try {
    return validateTmuaPastPaperSettings(testId, (metadata as Record<string, unknown>).tmua_past_paper_settings);
  } catch {
    return null;
  }
}

export function formatTmuaPastPaperSettings(settings: TmuaPastPaperSettings | null | undefined): string {
  if (!settings) return "";
  const order = settings.order === "randomised" ? "Randomised questions and options" : "Original order";
  const time = settings.time_multiplier === 1 ? "Standard time" : `+${Math.round((settings.time_multiplier - 1) * 100)}% extra time`;
  const minutes = Math.floor(settings.seconds_per_paper / 60);
  const seconds = settings.seconds_per_paper % 60;
  return `${order} · ${time} · ${minutes} min${seconds ? ` ${seconds} sec` : ""} per paper`;
}
