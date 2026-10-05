/** Source-owned practice conversions matching the six standalone /20 test
 * result screens. These are NOT official overall TMUA conversions and are
 * deliberately separate from the predictor's twelve-profile partial prior.
 */
const topicOne = Object.freeze([1,1,1,1,1,1,1,1.6,2.1,2.7,3.3,3.9,4.4,5,5.6,6.1,6.7,7.3,7.9,8.4,9]);
const hard = Object.freeze([1,1.2,1.5,1.8,2.2,2.6,3,3.5,4,4.5,4.9,5.3,5.7,6.1,6.6,7,7.4,7.8,8.2,8.6,9]);
const mixed = Object.freeze([1,1.3,1.6,1.9,2.3,2.7,3.1,3.6,4.1,4.6,5,5.4,5.8,6.2,6.7,7.1,7.5,7.9,8.3,8.7,9]);
const paperTwo = Object.freeze([1,1.2,1.5,1.8,2.1,2.4,2.8,3.2,3.6,4,4.5,4.9,5.3,5.7,6.2,6.6,7.1,7.6,8.1,8.6,9]);
export const TMUA_TOPIC_SCORE_PROFILES: Readonly<Record<string, { version: string; scores: readonly number[] }>> = Object.freeze({
  "p1-mock-01-algebra-sequences-functions-geometry": { version: "topic-test-1-threshold-6-linear-v1", scores: topicOne },
  "p1-mock-02-graphs-trig-logs": { version: "topic-test-2-hard-complete-map-v1", scores: hard },
  "p1-mock-03-calculus": { version: "topic-test-3-calculus-hard-complete-map-v1", scores: hard },
  "p2-mock-04-logic-proofs": { version: "topic-test-4-logic-proofs-hard-complete-map-v1", scores: mixed },
  "p1-mock-05-all-topics": { version: "topic-test-5-mixed-topics--complete-map-v1", scores: mixed },
  "p2-mock-06-all-topics": { version: "mock-test-6-paper-2-all-topics--complete-map-v1", scores: paperTwo },
});

export function estimateTmuaTopicScore(testId: string, raw: number) {
  const profile = Object.hasOwn(TMUA_TOPIC_SCORE_PROFILES, testId) ? TMUA_TOPIC_SCORE_PROFILES[testId] : null;
  if (!profile || !Number.isInteger(raw) || raw < 0 || raw > 20) throw new Error("A recognised /20 TMUA practice conversion is required.");
  return { score: profile.scores[raw], profile: profile.version };
}
