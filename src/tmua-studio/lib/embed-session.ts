export type EmbedOpenHistory = { received: boolean; openId?: string };

// The ready reply can repeat the first open request, especially during hydration.
// Only a subsequent, distinct open is a revisit; visits never create pads by themselves.
export function consumeStudioOpen(
  history: EmbedOpenHistory,
  qid: string,
  openId: unknown,
  currentQuestionKey: string,
) {
  const id = typeof openId === "string" && openId.length > 0 && openId.length <= 200
    ? openId : undefined;
  const repeated = id !== undefined && history.openId === id;
  return {
    history: { received: true, openId: id },
    revisit: history.received && !repeated && currentQuestionKey.startsWith(`tmua:${qid}@`),
  };
}
