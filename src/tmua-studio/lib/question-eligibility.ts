import eligibility from "../data/tmua-eligibility.json";

const active = new Set<string>([
  ...eligibility.active_audit_ids,
  ...Object.entries(eligibility.bank_aliases).filter(([id]) =>
    eligibility.active_audit_ids.includes(id)).map(([, bankId]) => bankId),
]);
export function isEligibleTmua(qid: string) {
  return active.has(qid);
}
export const bankQuestionId = (qid: string) =>
  (eligibility.bank_aliases as Record<string, string>)[qid] ?? qid;
