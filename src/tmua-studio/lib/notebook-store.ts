import type { Board, Exam, Feedback, StoredSolution } from "../types";
import type { PreparedBoard } from "./board-preparation";
import { ReviewNotAcceptedError, type ReviewStatus } from "./review-status";

export type ReviewRecovery = {
  requestId: string;
  status: ReviewStatus["status"] | "unknown";
  retryable: boolean;
  checkedAt: number;
  error?: string;
  code?: string;
  previousReview?: {
    requestId: string;
    status: ReviewStatus["status"] | "unknown";
    error?: string;
    summary?: string;
  };
};

export type AttemptPad = {
  id: string;
  storageKey: string;
  createdAt: number;
  status:
    | "draft"
    | "preparing"
    | "queued"
    | "reviewing"
    | "complete"
    | "failed";
  submittedAt?: number;
  requestId?: string;
  requestHistory?: { requestId: string; error?: string; retriedAt: number }[];
  rejectedRequests?: { requestId: string; error: string; rejectedAt: number }[];
  recovery?: ReviewRecovery;
  error?: string;
  source?: Feedback["source"];
  revision?: number;
  feedback?: Feedback;
  clarifications?: { regionIds: string[]; text: string }[];
  reviewHistory?: Feedback[];
};
export type Notebook = {
  version: 2;
  visits: number;
  active: string;
  pads: AttemptPad[];
  solutionUnlocked: boolean;
  solution?: StoredSolution;
  solutionError?: string;
};
type Dependencies = {
  read: (key: string) => Promise<Notebook | undefined>;
  write: (key: string, value: Notebook) => Promise<void>;
  loadBoard: (key: string) => Promise<Board | undefined>;
  loadReview: (key: string) => Promise<Feedback | undefined>;
  saveBoard: (key: string, value: Board) => Promise<void>;
  saveReview: (key: string, value: Feedback) => Promise<void>;
  hash: (board: Board) => Promise<string>;
  assess: (body: unknown) => Promise<Feedback>;
  solution: (
    exam: Exam,
    qid: string,
    contentVersion?: string,
  ) => Promise<StoredSolution>;
  checkpoint?: (notebookKey: string, boardKey: string) => Promise<void>;
  recover?: (id: string) => Promise<ReviewStatus>;
};
type NotebookContext = { exam: Exam; qid: string; contentVersion?: string };
// App-lifetime ownership: navigating away unsubscribes the view, never the job.
export function createNotebookStore(deps: Dependencies) {
  const records = new Map<string, Notebook>(),
    loads = new Map<string, Promise<Notebook>>(),
    writes = new Map<string, Promise<void>>();
  const listeners = new Map<string, Set<() => void>>(),
    entries = new Set<string>(),
    jobs = new Set<string>(),
    solutions = new Map<string, Promise<void>>();
  let queue = Promise.resolve();
  function persist(key: string) {
    const value = records.get(key)!;
    const task = (writes.get(key) ?? Promise.resolve())
      .catch(() => {})
      .then(() => deps.write(key, value));
    writes.set(key, task);
    return task;
  }
  function change(key: string, update: (n: Notebook) => Notebook) {
    records.set(key, update(records.get(key)!));
    listeners.get(key)?.forEach((fn) => fn());
    return persist(key);
  }
  function padChange(key: string, id: string, patch: Partial<AttemptPad>) {
    return change(key, (n) => ({
      ...n,
      pads: n.pads.map((p) => (p.id === id ? { ...p, ...patch } : p)),
    }));
  }
  function recoveryState(
    requestId: string,
    result?: ReviewStatus,
  ): ReviewRecovery {
    return {
      requestId,
      status: result?.status ?? "unknown",
      retryable: result?.status === "failed" && result.retryable === true,
      checkedAt: Date.now(),
      ...(result?.error ? { error: result.error } : {}),
      ...(result?.code ? { code: result.code } : {}),
    };
  }
  function restoreRejected(
    key: string,
    previous: AttemptPad,
    error: ReviewNotAcceptedError,
    recovery = previous.recovery,
  ) {
    // Replace the pad, rather than merge, so fields introduced for the rejected
    // request (including history) do not survive when previously absent.
    return change(key, (n) => ({
      ...n,
      pads: n.pads.map((pad) =>
        pad.id === previous.id
          ? {
              ...previous,
              recovery,
              error: error.message,
              rejectedRequests: [
                ...(previous.rejectedRequests ?? []),
                {
                  requestId: error.requestId,
                  error: error.message,
                  rejectedAt: Date.now(),
                },
              ],
            }
          : pad,
      ),
    }));
  }
  async function missingRecovery(pad: AttemptPad, recovery: ReviewRecovery) {
    // Historical status is context only. A missing latest request is never
    // authorized for retry by a previous request's terminal status.
    const previous = pad.requestHistory
      ?.slice()
      .reverse()
      .find((entry) => entry.requestId !== pad.requestId);
    if (previous && deps.recover) {
      try {
        const result = await deps.recover(previous.requestId);
        recovery.previousReview = {
          requestId: previous.requestId,
          status: result.status,
          error: result.error,
          ...(result.status === "complete" && result.feedback
            ? { summary: result.feedback.summary }
            : {}),
        };
      } catch {
        recovery.previousReview = {
          requestId: previous.requestId,
          status: "unknown",
          error: "The earlier review could not be checked.",
        };
      }
    }
    return recovery;
  }
  const missingReviewMessage =
    "The latest review cannot be found in saved tracking, so its outcome cannot be verified. Your working is saved; no new API request was sent. Retry remains unavailable.";
  async function ensure(key: string): Promise<Notebook> {
    if (records.has(key)) return records.get(key)!;
    let promise = loads.get(key);
    if (!promise) {
      promise = (async () => {
        let n = await deps.read(key);
        if (!n) {
          const [board, feedback] = await Promise.all([
            deps.loadBoard(key),
            deps.loadReview(key),
          ]);
          const valid =
            !!board &&
            !!feedback?.source &&
            feedback.revision === board.revision &&
            feedback.source.hash === (await deps.hash(board));
          n = {
            version: 2,
            visits: board ? 1 : 0,
            active: "first",
            solutionUnlocked: valid,
            pads: [
              {
                id: "first",
                storageKey: key,
                createdAt: Date.now(),
                status: valid ? "complete" : "draft",
                ...(valid
                  ? {
                      submittedAt: Date.now(),
                      feedback,
                      source: feedback!.source,
                      revision: board!.revision,
                    }
                  : {}),
              },
            ],
          };
        }
        // This legacy response was returned before reserving a job or calling AI.
        // Preserve its working and let the student submit it manually now.
        n = {
          ...n,
          pads: n.pads.map((p) =>
            p.status === "failed" &&
            !p.feedback &&
            p.error ===
              "A review is already running, or today's preview allowance is used up. No AI request was sent."
              ? {
                  id: p.id,
                  storageKey: p.storageKey,
                  createdAt: p.createdAt,
                  status: "draft" as const,
                }
              : p,
          ),
        };
        n.pads = n.pads.map((p) =>
          p.status === "preparing" && !p.requestId
            ? {
                ...p,
                status: "draft" as const,
                error:
                  "Your working was saved before a review was sent. You can submit it now.",
              }
            : p,
        );
        records.set(key, n);
        return n;
      })();
      loads.set(key, promise);
      void promise.catch(() => loads.delete(key));
    }
    return promise;
  }
  async function restorePending(key: string, pad: AttemptPad) {
    if (
      !deps.recover ||
      !pad.requestId ||
      !pad.source ||
      jobs.has(`${key}/${pad.id}`)
    )
      return;
    jobs.add(`${key}/${pad.id}`);
    let recovery = recoveryState(pad.requestId);
    try {
      await padChange(key, pad.id, { recovery });
      // Recovery only reads job status. It never resubmits paid work.
      for (let i = 0; i < 40; i++) {
        recovery = recoveryState(pad.requestId);
        const result = await deps.recover(pad.requestId);
        recovery = recoveryState(pad.requestId, result);
        await padChange(key, pad.id, { recovery });
        if (result.status === "complete" && result.feedback) {
          const feedback = {
            ...result.feedback,
            revision: pad.revision!,
            source: pad.source,
            reviewId: pad.requestId,
          };
          await deps.saveReview(pad.storageKey, feedback);
          await padChange(key, pad.id, {
            status: "complete",
            feedback,
            error: undefined,
          });
          return;
        }
        if (result.status === "failed")
          throw Error(
            result.error ??
              "This review could not finish. Your submitted working is saved.",
          );
        if (result.status === "complete")
          throw Error(
            "The saved review has no readable feedback. Your working is saved; no new API request was sent.",
          );
        if (
          result.status === "missing" &&
          (i >= 2 || pad.requestHistory?.length)
        ) {
          recovery = await missingRecovery(pad, recovery);
          throw Error(missingReviewMessage);
        }
        await new Promise((r) => setTimeout(r, Math.min(6000, 2000 + i * 500)));
      }
      throw Error(
        "This review is taking longer than expected. Reopen this question to check for a saved result.",
      );
    } catch (e) {
      await padChange(key, pad.id, {
        status: "failed",
        error: (e as Error).message,
        recovery,
      });
    } finally {
      jobs.delete(`${key}/${pad.id}`);
    }
  }
  function loadSolution(
    key: string,
    exam: Exam,
    qid: string,
    contentVersion?: string,
  ) {
    if (records.get(key)?.solution) return Promise.resolve();
    if (solutions.has(key)) return solutions.get(key)!;
    const task = deps
      .solution(exam, qid, contentVersion)
      .then((solution) =>
        change(key, (n) => ({ ...n, solution, solutionError: undefined })),
      )
      .catch((e) =>
        change(key, (n) => ({ ...n, solutionError: (e as Error).message })),
      )
      .then(() => {})
      .finally(() => solutions.delete(key));
    solutions.set(key, task);
    return task;
  }
  return {
    get: (key: string) => records.get(key),
    subscribe(key: string, fn: () => void) {
      let set = listeners.get(key);
      if (!set) {
        set = new Set();
        listeners.set(key, set);
      }
      set.add(fn);
      return () => {
        set!.delete(fn);
      };
    },
    async open(key: string, entry: string, context: NotebookContext) {
      await ensure(key);
      if (!entries.has(entry)) {
        entries.add(entry);
        await change(key, (n) => ({ ...n, visits: n.visits + 1 }));
      }
      const n = records.get(key)!;
      if (n.solutionUnlocked)
        void loadSolution(
          key,
          context.exam,
          context.qid,
          context.contentVersion,
        ).catch(() => {});
      for (const p of n.pads)
        if (
          (p.status === "reviewing" ||
            p.status === "preparing" ||
            p.status === "queued" ||
            p.status === "failed") &&
          !jobs.has(`${key}/${p.id}`)
        )
          void restorePending(key, p).catch(() => {});
      return records.get(key)!;
    },
    async select(key: string, id: string) {
      const n = records.get(key)!;
      if (
        id === "solution"
          ? !n.solutionUnlocked
          : !n.pads.some((p) => p.id === id)
      )
        return;
      await change(key, (n) => ({ ...n, active: id }));
    },
    async fresh(key: string) {
      const n = records.get(key)!;
      if (n.visits < 2)
        throw Error("A fresh pad is available when you revisit this question.");
      const id = crypto.randomUUID();
      await change(key, (n) => ({
        ...n,
        active: id,
        pads: [
          ...n.pads,
          {
            id,
            storageKey: `${key}:pad:${id}`,
            createdAt: Date.now(),
            status: "draft",
          },
        ],
      }));
      return id;
    },
    loadSolution,
    async clarify(
      key: string,
      id: string,
      regionIds: string[],
      text: string,
      capture: () => Promise<PreparedBoard>,
      context: NotebookContext,
    ) {
      const p = records.get(key)?.pads.find((p) => p.id === id);
      if (!p?.feedback || p.status !== "complete" || jobs.has(`${key}/${id}`))
        throw Error("Wait for the current review to finish.");
      const known = new Set(p.source?.regions.map((r) => r.id));
      if (
        !text.trim() ||
        text.length > 700 ||
        regionIds.some((id) => !known.has(id))
      )
        throw Error("Please clarify the marked area in a short sentence.");
      jobs.add(`${key}/${id}`);
      let attemptedRequestId: string | undefined;
      try {
        const snapshot = await capture();
        if (snapshot.hash !== p.source?.hash)
          throw Error("The saved working no longer matches this review.");
        const clarifications = [
          ...(p.clarifications ?? []),
          { regionIds, text: text.trim() },
        ].slice(-6);
        const requestId = crypto.randomUUID();
        attemptedRequestId = requestId;
        await padChange(key, id, {
          status: "queued",
          requestId,
          clarifications,
          error: undefined,
          recovery: recoveryState(requestId),
          reviewHistory: [...(p.reviewHistory ?? []), p.feedback],
        });
        const run = async () => {
          await padChange(key, id, { status: "reviewing" });
          await deps.checkpoint?.(key, p.storageKey);
          const result = await deps.assess({
            ...context,
            requestId,
            revision: snapshot.board.revision,
            image: snapshot.image || undefined,
            note: snapshot.board.note,
            structure: snapshot.structure,
            regions: p.source!.regions,
            groups: p.source!.groups,
            clarifications,
          });
          const feedback = {
            ...result,
            source: p.source,
            revision: p.revision!,
            reviewId: requestId,
          };
          await deps.saveReview(p.storageKey, feedback);
          await padChange(key, id, {
            status: "complete",
            feedback,
            error: undefined,
          });
        };
        const task = queue.then(run, run);
        queue = task.catch(() => {});
        await task;
      } catch (e) {
        if (
          e instanceof ReviewNotAcceptedError &&
          e.requestId === attemptedRequestId
        ) {
          await restoreRejected(key, p, e);
          throw e;
        }
        await padChange(key, id, {
          status: "failed",
          error: (e as Error).message,
        });
        throw e;
      } finally {
        jobs.delete(`${key}/${id}`);
      }
    },
    recover(key: string, id: string) {
      const p = records.get(key)?.pads.find((p) => p.id === id);
      return p ? restorePending(key, p) : Promise.resolve();
    },
    async retry(
      key: string,
      id: string,
      capture: () => Promise<PreparedBoard>,
      context: NotebookContext,
    ) {
      const pad = records.get(key)?.pads.find((p) => p.id === id);
      if (!pad || pad.status !== "failed" || jobs.has(`${key}/${id}`)) return;
      jobs.add(`${key}/${id}`);
      let attemptedRequestId: string | undefined;
      let recovery = pad.requestId ? recoveryState(pad.requestId) : undefined;
      try {
        await padChange(key, id, { recovery });
        if (!deps.recover || !pad.requestId || !pad.source)
          throw Error(
            "The original review cannot be verified. Check the saved review before trying again.",
          );
        // A disconnected browser is not evidence that paid work has stopped.
        const previous = await deps.recover(pad.requestId);
        recovery = recoveryState(pad.requestId, previous);
        await padChange(key, id, { recovery });
        if (previous.status === "complete" && previous.feedback) {
          const feedback = {
            ...previous.feedback,
            source: pad.source,
            revision: pad.revision!,
            reviewId: pad.requestId,
          };
          await deps.saveReview(pad.storageKey, feedback);
          await padChange(key, id, {
            status: "complete",
            feedback,
            error: undefined,
          });
          return;
        }
        if (previous.status === "missing") {
          recovery = await missingRecovery(pad, recovery);
          throw Error(missingReviewMessage);
        }
        if (previous.status !== "failed" || previous.retryable !== true)
          throw Error(
            [
              previous.error,
              previous.status === "pending"
                ? "The original review is still processing. Check saved review later; no new API request was sent."
                : "The original review is not confirmed safe to retry. Check saved review for its status; no new API request was sent.",
            ]
              .filter(Boolean)
              .join(" "),
          );
        const saved = await deps.loadBoard(pad.storageKey);
        const snapshot = structuredClone(await capture());
        if (
          !saved ||
          snapshot.hash !== pad.source.hash ||
          snapshot.board.revision !== pad.revision ||
          saved.revision !== pad.revision ||
          (await deps.hash(saved)) !== pad.source.hash ||
          (await deps.hash(snapshot.board)) !== pad.source.hash ||
          JSON.stringify(snapshot.capture) !==
            JSON.stringify(pad.source.capture)
        )
          throw Error(
            "The saved working no longer matches the submitted attempt. No new API request was sent.",
          );
        const requestId = crypto.randomUUID();
        attemptedRequestId = requestId;
        await padChange(key, id, {
          status: "queued",
          requestId,
          error: undefined,
          recovery: recoveryState(requestId),
          requestHistory: [
            ...(pad.requestHistory ?? []),
            {
              requestId: pad.requestId,
              error: previous.error ?? pad.error,
              retriedAt: Date.now(),
            },
          ],
        });
        const run = async () => {
          await padChange(key, id, { status: "reviewing" });
          await deps.checkpoint?.(key, pad.storageKey);
          const result = await deps.assess({
            ...context,
            requestId,
            revision: pad.revision,
            image: snapshot.image || undefined,
            note: snapshot.board.note,
            structure: snapshot.structure,
            regions: pad.source!.regions,
            groups: pad.source!.groups,
            ...(pad.clarifications?.length
              ? { clarifications: pad.clarifications }
              : {}),
          });
          const feedback = {
            ...result,
            source: pad.source,
            revision: pad.revision!,
            reviewId: requestId,
          };
          await deps.saveReview(pad.storageKey, feedback);
          await padChange(key, id, {
            status: "complete",
            feedback,
            error: undefined,
          });
        };
        const task = queue.then(run, run);
        queue = task.catch(() => {});
        await task;
      } catch (e) {
        if (
          e instanceof ReviewNotAcceptedError &&
          e.requestId === attemptedRequestId
        ) {
          await restoreRejected(key, pad, e, recovery);
          throw e;
        }
        await padChange(key, id, {
          status: "failed",
          error: (e as Error).message,
          recovery: attemptedRequestId
            ? recoveryState(attemptedRequestId)
            : recovery,
        });
        throw e;
      } finally {
        jobs.delete(`${key}/${id}`);
      }
    },
    async submit(
      key: string,
      id: string,
      capture: () => Promise<PreparedBoard>,
      context: NotebookContext,
      releaseUnsubmitted?: () => void,
    ) {
      const pad = records.get(key)?.pads.find((p) => p.id === id);
      if (!pad || pad.status !== "draft" || jobs.has(`${key}/${id}`)) return;
      jobs.add(`${key}/${id}`);
      // Freeze immediately before the first await; the capture belongs to this pad forever.
      let accepted = false;
      try {
        const captured = Promise.resolve(capture()).then(
          (snapshot) => ({ snapshot }),
          (error) => ({ error }),
        );
        const result = await captured;
        if ("error" in result) throw result.error;
        await padChange(key, id, { status: "preparing", error: undefined });
        const snapshot = result.snapshot;
        await deps.saveBoard(pad.storageKey, snapshot.board);
        accepted = true;
        const source = {
          hash: snapshot.hash,
          capture: snapshot.capture,
          regions: snapshot.regions,
          groups: snapshot.groups,
        };
        const requestId = crypto.randomUUID();
        await padChange(key, id, {
          status: "queued",
          submittedAt: Date.now(),
          requestId,
          source,
          revision: snapshot.board.revision,
          recovery: recoveryState(requestId),
        });
        await change(key, (n) => ({
          ...n,
          solutionUnlocked: true,
        }));
        void loadSolution(
          key,
          context.exam,
          context.qid,
          context.contentVersion,
        ).catch(() => {});
        const run = async () => {
          try {
            await padChange(key, id, { status: "reviewing" });
            await deps.checkpoint?.(key, pad.storageKey);
            const result = await deps.assess({
              ...context,
              requestId,
              revision: snapshot.board.revision,
              image: snapshot.image || undefined,
              note: snapshot.board.note,
              structure: snapshot.structure,
              regions: snapshot.regions,
              groups: snapshot.groups,
            });
            const feedback = {
              ...result,
              revision: snapshot.board.revision,
              source,
              reviewId: requestId,
            };
            await deps.saveReview(pad.storageKey, feedback);
            await padChange(key, id, {
              status: "complete",
              feedback,
              error: undefined,
            });
          } catch (e) {
            if (
              e instanceof ReviewNotAcceptedError &&
              e.requestId === requestId
            ) {
              await restoreRejected(key, pad, e);
              releaseUnsubmitted?.();
              return;
            }
            await padChange(key, id, {
              status: "failed",
              error: (e as Error).message,
            });
          } finally {
            jobs.delete(`${key}/${id}`);
          }
        };
        const task = queue.then(run, run);
        queue = task.catch(() => {});
        await task;
      } catch (e) {
        jobs.delete(`${key}/${id}`);
        try {
          await padChange(key, id, {
            status: accepted ? "failed" : "draft",
            ...(accepted ? { submittedAt: Date.now() } : {}),
            error: (e as Error).message,
          });
        } finally {
          if (!accepted) releaseUnsubmitted?.();
        }
      }
    },
  };
}
