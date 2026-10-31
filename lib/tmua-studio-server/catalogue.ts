import { readFileSync } from "node:fs";
import { join } from "node:path";
import { gunzipSync } from "node:zlib";
import type { SourceQuestion } from "./question-reference";

export type ReleasedQuestion = SourceQuestion & {
  exam: "tmua"; paper: string; topic: string; subtopic: string; difficulty: number;
  content_version: string; source_sha256: string; app_question_id: string;
  tags?: string[]; skill_search?: string; guide_path?: string; bank_qid?: string;
  answer_verified: boolean; audited?: boolean;
};
const root = join(process.cwd(), "content", "tmua-studio");
const read = <T,>(name: string): T => JSON.parse(readFileSync(join(root, name), "utf8")) as T;
const eligibility = read<{active_audit_ids: string[]; excluded_ids: string[]; bank_aliases: Record<string,string>}>("eligibility.json");
const main = read<ReleasedQuestion[]>("questions.json");
const versions = read<ReleasedQuestion[]>("versions.json");
const guideFiles = read<Record<string,string>>("guide-index.json");
const active = new Set(eligibility.active_audit_ids);
export const canonicalQid = (qid: string) => eligibility.bank_aliases[qid] ?? qid;
const byCanonical = new Map(main.map(q => [canonicalQid(q.qid), q]));
const byVersion = new Map(versions.map(q => [JSON.stringify([canonicalQid(q.qid), q.content_version]), q]));
if (main.length !== 2178 || active.size !== 2178 || eligibility.excluded_ids.length !== 22 || byCanonical.size !== main.length || main.some(q => !active.has(q.qid) || !guideFiles[q.content_version])) {
  throw new Error("TMUA release completeness validation failed");
}

export function resolveQuestion(qid: string, version?: string | null) {
  const canonical = canonicalQid(qid);
  if (!byCanonical.has(canonical)) return undefined;
  return version ? byVersion.get(JSON.stringify([canonical, version])) : byCanonical.get(canonical);
}
export function questionMetadata(q: ReleasedQuestion) {
  return {
    exam: "tmua" as const, qid: canonicalQid(q.qid), bank_qid: canonicalQid(q.qid), audit_qid: q.qid,
    display_order: Number(q.app_question_id), app_question_id: q.app_question_id,
    paper: q.paper, topic: q.topic, subtopic: q.subtopic, difficulty: q.difficulty,
    tags: q.tags ?? [], content_version: q.content_version, source_sha256: q.source_sha256,
    skill_search: q.skill_search ?? "", audited: true, answer_verified: true,
  };
}
export const catalogue = main.map(questionMetadata).sort((a,b) =>
  a.topic.localeCompare(b.topic, undefined, {numeric:true}) || a.difficulty-b.difficulty || a.display_order-b.display_order);
export function publicQuestion(q: ReleasedQuestion) {
  return {...questionMetadata(q), prompt_html: q.prompt_html, options: q.options, updated_at: q.updated_at,
    guide_path: `/api/tmua/studio?action=guide&qid=${encodeURIComponent(canonicalQid(q.qid))}&contentVersion=${encodeURIComponent(q.content_version)}`};
}
export function questionGuide(q: ReleasedQuestion) {
  const file = guideFiles[q.content_version];
  if (!file || !/^[a-f0-9]{64}\.json\.gz$/.test(file)) return null;
  const guide = JSON.parse(gunzipSync(readFileSync(join(root,"guides",file))).toString("utf8"));
  if (guide.qid !== q.qid || guide.version_id !== q.content_version || guide.source_sha256 !== q.source_sha256) throw new Error("Guide version mismatch");
  // Adapt public identities without rewriting the original audit archive or its hashes.
  guide.audit_qid = guide.qid;
  guide.qid = canonicalQid(q.qid);
  guide.routes = (guide.routes ?? []).filter((route: {target_qid:string; target_content_version?:string; target_source_sha256?:string}) => {
    const target = resolveQuestion(route.target_qid, route.target_content_version);
    return target && target.source_sha256 === route.target_source_sha256;
  }).map((route: Record<string,unknown>) => ({...route, audit_target_qid: route.target_qid, target_qid: canonicalQid(String(route.target_qid))}));
  return guide;
}
