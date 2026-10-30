/** Rotate subtopics so the first practice page includes a range of skills. */
export function variedPracticeOrder<T extends { subtopic: string }>(questions: T[]): T[] {
  const groups = new Map<string, T[]>();
  for (const question of questions) {
    const group = groups.get(question.subtopic);
    if (group) group.push(question);
    else groups.set(question.subtopic, [question]);
  }
  const ordered: T[] = [];
  for (let round = 0; ordered.length < questions.length; round++) {
    for (const group of groups.values()) if (group[round]) ordered.push(group[round]);
  }
  return ordered;
}
