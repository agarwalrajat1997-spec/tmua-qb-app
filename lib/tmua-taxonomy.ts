import { readFileSync } from "node:fs";
import { join } from "node:path";

export type TmuaTaxonomyPair = { topic: string; subtopic: string };
type TaxonomyManifest = {
  version: string;
  topics: Record<string, string[]>;
  questions: Record<string, TmuaTaxonomyPair>;
  /** Only unambiguous historical label pairs belong in this fallback map. */
  aliases?: Record<string, TmuaTaxonomyPair>;
};

// A presentation overlay: audited prompts, versions, hashes and progress IDs
// remain in their original archives. Keep this module on the server so the
// browser receives only the already-normalised catalogue, not the whole map.
const manifest = JSON.parse(readFileSync(
  join(process.cwd(), "content", "tmua-studio", "taxonomy-20261118.json"), "utf8",
)) as TaxonomyManifest;

export const TMUA_TAXONOMY_VERSION = manifest.version;
export const TMUA_TAXONOMY_TOPICS: Readonly<Record<string, readonly string[]>> = manifest.topics;
export const TMUA_QUESTION_TAXONOMY: Readonly<Record<string, TmuaTaxonomyPair>> = manifest.questions;

function cleanLabel(value: unknown): string {
  return String(value ?? "").normalize("NFKC")
    .replace(/&(?:amp|#0*38|#x0*26);/gi, "&")
    .replaceAll("â€”", "—").replaceAll("â€“", "–")
    .replaceAll("_", " ").replace(/\s+/g, " ").trim();
}

function cleanTopicLabel(value: unknown): string {
  return cleanLabel(value).replace(/^\s*\d+[.\-):\s]+/, "").trim();
}

/** Syntax-only normalisation; semantic merges are explicit in the manifest. */
export function normalizeTmuaTaxonomyLabel(value: unknown): string {
  return cleanLabel(value).toLowerCase().replace(/\band\b/g, "&")
    .replace(/[\s&,:/()\-–—]+/g, " ").trim();
}

export function normalizeTmuaTopicLabel(value: unknown): string {
  return normalizeTmuaTaxonomyLabel(cleanTopicLabel(value));
}

export function tmuaTaxonomyAliasKey(topic: unknown, subtopic: unknown): string {
  return JSON.stringify([normalizeTmuaTopicLabel(topic), normalizeTmuaTaxonomyLabel(subtopic)]);
}

const topicAliases = new Map(Object.keys(manifest.topics).map(topic =>
  [normalizeTmuaTopicLabel(topic), topic] as const));
for (const [alias, target] of Object.entries({
  "Algebra": "1_Algebra & Functions",
  "Sequences & Series": "2_Sequences",
  "Coordinate Geometry": "3_Geometry",
  "Exponents & Logarithms": "5_Exponentials and Logarithms",
  "Miscellaneous": "10_Number & Counting",
  "Misc": "10_Number & Counting",
})) {
  if (Object.hasOwn(manifest.topics, target)) topicAliases.set(normalizeTmuaTopicLabel(alias), target);
}
const subtopicAliases = new Map(Object.entries(manifest.topics).map(([topic, subtopics]) =>
  [topic, new Map(subtopics.map(subtopic => [normalizeTmuaTaxonomyLabel(subtopic), subtopic]))] as const));
const pairAliases = new Map(Object.entries(manifest.aliases ?? {}));

export function canonicalTmuaTopic(value: unknown): string {
  return topicAliases.get(normalizeTmuaTopicLabel(value)) ?? (cleanTopicLabel(value) || "General practice");
}

export function canonicalTmuaSubtopic(topic: unknown, subtopic: unknown): string {
  return subtopicAliases.get(canonicalTmuaTopic(topic))?.get(normalizeTmuaTaxonomyLabel(subtopic))
    ?? (cleanLabel(subtopic) || "General practice");
}

export function canonicalTmuaQuestionTaxonomy(question: {
  qid: string;
  topic?: unknown;
  subtopic?: unknown;
  skill_search?: unknown;
}): TmuaTaxonomyPair & { skill_search: string; taxonomy_version: string } {
  const explicit = Object.hasOwn(manifest.questions, question.qid) ? manifest.questions[question.qid] : undefined;
  const topic = canonicalTmuaTopic(question.topic);
  const knownPair = pairAliases.get(tmuaTaxonomyAliasKey(question.topic, question.subtopic))
    ?? pairAliases.get(tmuaTaxonomyAliasKey(topic, question.subtopic));
  // Current questions are exhaustively mapped and checked at release time.
  // Unexpected future content still renders without silently disappearing.
  const resolved = explicit ?? knownPair ?? {
    topic,
    subtopic: canonicalTmuaSubtopic(topic, question.subtopic),
  };
  const search = [...new Set([
    String(question.skill_search ?? "").trim(),
    String(question.topic ?? "").trim(),
    String(question.subtopic ?? "").trim(),
    cleanTopicLabel(question.topic),
    cleanLabel(question.subtopic),
  ].filter(Boolean))].join(" · ");
  return { ...resolved, skill_search: search, taxonomy_version: manifest.version };
}
