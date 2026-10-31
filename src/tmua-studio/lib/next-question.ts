import {
  questionKey,
  type Feedback,
  type Progress,
  type Question,
} from "../types";
export function recommendNext(
  current: Question,
  questions: Question[],
  progress: Record<string, Progress>,
  feedback?: Feedback,
) {
  const available = questions.filter(
    (q) =>
      q.exam === current.exam &&
      q.qid !== current.qid &&
      q.answer_verified &&
      !q.followup_only,
  );
  const sameTopic = available.filter((q) => q.topic === current.topic);
  // This general Next action offers neutral practice; diagnostic routes have separate evidence gates.
  const candidates = sameTopic.length ? sameTopic : available;
  const target = feedback?.firstErrorLine
    ? current.difficulty
    : Math.min(5, current.difficulty + 1);
  const ranked = [...candidates].sort((a, b) => {
    const score = (q: Question) =>
      (progress[questionKey(q)]?.submitted ||
      progress[questionKey(q)]?.reviewedAt
        ? 12
        : 0) +
      (current.subtopic && q.subtopic === current.subtopic ? 0 : 4) +
      Math.abs(q.difficulty - target);
    return score(a) - score(b) || a.qid.localeCompare(b.qid);
  });
  return ranked[0]
    ? {
        question: ranked[0],
        reason: sameTopic.length
          ? "Another question in this topic"
          : "Next question in your exam bank",
      }
    : null;
}
