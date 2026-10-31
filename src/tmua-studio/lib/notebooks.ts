import { createNotebookStore } from "./notebook-store";
import {
  loadNotebook,
  saveNotebook,
  loadBoard,
  loadReview,
  saveBoard,
  saveReview,
} from "./storage";
import { contentHash } from "./board-preparation";
import { checkWorking, getStoredSolution, recoverReview } from "./api";
import { flushCloud } from "./cloud-storage";
export const notebooks = createNotebookStore({
  read: loadNotebook,
  write: saveNotebook,
  loadBoard,
  loadReview,
  saveBoard,
  saveReview,
  hash: contentHash,
  assess: checkWorking,
  solution: getStoredSolution,
  recover: recoverReview,
  checkpoint: async (notebookKey, boardKey) => {
    // Give the snapshot and its recovery ID a chance to reach the account before
    // paid submission. An offline cloud service never destroys the device copy.
    for (let i = 0; i < 2; i++)
      await Promise.all([
        flushCloud(`board:${boardKey}`),
        flushCloud(`notebook:${notebookKey}`),
      ]);
  },
});
