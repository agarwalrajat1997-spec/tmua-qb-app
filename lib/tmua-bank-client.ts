/** Presentation order never becomes a question/progress identifier. */
export type BankQuestion = {
  qid: string;
  audit_qid?: string;
  /** Only immutable, collision-checked historical IDs supplied by the catalogue. */
  legacy_ids?: string[];
  display_order: number;
  paper: string;
  topic: string;
  subtopic: string;
  difficulty: number;
  skill_search?: string;
  content_version: string;
  source_sha256?: string;
  tags?: string[];
};

export type QuestionProgress = {
  selected_answer?: string | null;
  status?: string | null;
  flagged?: boolean;
  time_spent?: number | null;
  last_seen_at?: string | null;
  updated_at?: string | null;
  submission_id?: string | null;
  answer_elapsed_seconds?: number | null;
  answer_submitted_at?: string | null;
  answer?: string;
  assisted?: boolean;
  solutionViewed?: boolean;
};
export type ProgressMap = Record<string, QuestionProgress>;
export type ProgressSyncState = "synced" | "offline";
export type ProgressResult = { progress: ProgressMap; syncState: ProgressSyncState; warnings: string[] };
type JsonObject = Record<string, unknown>;
type Pending = {
  id: string; qid: string; displayOrder: number; at: number;
  progress: QuestionProgress; legacy: JsonObject;
  canonicalSaved: boolean; compactSaved: boolean;
  predictionEvidence?: boolean; predictionNotified?: boolean;
};

const PRODUCT = "tmua-question-bank";
const STORAGE_KEY = "ts_tmua_supabase_exact_ui_v4";
const memory = new Map<string, string>();
const sessionProgress = new Map<string, ProgressMap>();
const legacyAnswers = new Map<string, JsonObject>();
const sending = new Map<string, Promise<void>>();
const blocked = new Set<string>();
const verifiedViewers = new Set<string>();
let storageUnavailable = false;
let sequence = 0;

export class AccountChangedError extends Error {
  readonly code = "ACCOUNT_CHANGED";
  constructor() { super("Your sign-in has changed. Reload before continuing; your saved work is retained for its original account."); }
}

function object(value: unknown): value is JsonObject {
  return !!value && typeof value === "object" && !Array.isArray(value);
}
function canonical(value: string) { return value.replace(/^TMUA-JZ-/, "TMUA-TS-"); }
function prefix(viewerId: string) {
  if (!viewerId || viewerId.length > 150) throw new Error("A signed-in student is required.");
  return `ts-tmua-bank-v1:${encodeURIComponent(viewerId)}:`;
}
function read(key: string): string | null {
  if (memory.has(key)) return memory.get(key)!;
  try { return typeof localStorage === "undefined" ? null : localStorage.getItem(key); }
  catch { return null; }
}
function write(key: string, value: unknown) {
  const raw = JSON.stringify(value);
  try { localStorage.setItem(key, raw); memory.delete(key); }
  catch { memory.set(key, raw); storageUnavailable = true; }
}
function remove(key: string) {
  memory.delete(key);
  try { localStorage.removeItem(key); } catch { /* A memory journal still remains usable. */ }
}
function storageKeys() {
  const keys = new Set(memory.keys());
  try { for (let i = 0; i < localStorage.length; i++) { const key = localStorage.key(i); if (key) keys.add(key); } }
  catch { /* Storage may be disabled; retain the in-memory outbox. */ }
  return [...keys];
}
function parsed(key: string): unknown {
  try { return JSON.parse(read(key) ?? "null"); } catch { return null; }
}
function timestamp(value: unknown) {
  const time = typeof value === "string" ? Date.parse(value) : NaN;
  return Number.isFinite(time) ? time : 0;
}
function rowTime(value: QuestionProgress) {
  return Math.max(timestamp(value.updated_at), timestamp(value.answer_submitted_at), timestamp(value.last_seen_at));
}
function finiteOrNull(value: unknown) {
  if (value === null || value === undefined || value === "") return null;
  const n = Number(value);
  return Number.isFinite(n) && n >= 0 ? n : null;
}
function normalize(value: unknown): QuestionProgress {
  if (!object(value)) return {};
  let status = typeof value.status === "string" ? value.status.trim().toLowerCase() : undefined;
  if (status === "incorrect") status = "wrong";
  if (status === "right") status = "correct";
  if (status === "answered" || status === "submitted") status = "attempted";
  if (!["correct", "wrong", "attempted", "seen", "unattempted"].includes(status ?? "")) status = undefined;
  // `answer` is the old bank's answer KEY, not the student's selection.
  // An explicit null selection/unchecked retry must not resurrect an older mark.
  const selected = value.selected_answer !== undefined ? value.selected_answer : value.selected;
  const hasSelection = selected !== null && selected !== undefined && String(selected).trim() !== "";
  if (value.checked === true) status = typeof value.isCorrect === "boolean"
    ? (value.isCorrect ? "correct" : "wrong") : "attempted";
  else if (value.checked === false) status = hasSelection ? "attempted" : "unattempted";
  else if ((!status || status === "seen" || status === "unattempted") && hasSelection) status = "attempted";
  const result: QuestionProgress = {};
  if (status) result.status = status;
  if (selected !== undefined) result.selected_answer = selected === null ? null : String(selected);
  if (typeof value.flagged === "boolean") result.flagged = value.flagged;
  else if (typeof value.saved === "boolean") result.flagged = value.saved;
  for (const key of ["updated_at", "last_seen_at", "answer_submitted_at", "submission_id"] as const) {
    if (typeof value[key] === "string" || value[key] === null) result[key] = value[key] as string | null;
  }
  for (const key of ["time_spent", "answer_elapsed_seconds"] as const) {
    if (value[key] !== undefined) result[key] = finiteOrNull(value[key]);
  }
  if (typeof value.answer === "string") result.answer = value.answer;
  if (typeof value.assisted === "boolean") result.assisted = value.assisted;
  if (typeof value.solutionViewed === "boolean") result.solutionViewed = value.solutionViewed;
  return result;
}

function topicOrder(topic: string) { return Number(topic.match(/^\s*(\d+)[_ .-]/)?.[1] ?? 999); }
export function sortQuestions<T extends BankQuestion>(questions: readonly T[]): T[] {
  return [...questions].sort((a, b) => topicOrder(a.topic) - topicOrder(b.topic)
    || a.topic.localeCompare(b.topic, undefined, { numeric: true, sensitivity: "base" })
    || (Number(a.difficulty) || 99) - (Number(b.difficulty) || 99)
    || a.display_order - b.display_order || a.qid.localeCompare(b.qid));
}

function aliases(questions: readonly BankQuestion[]) {
  const map = new Map<string, BankQuestion>();
  const ambiguous = new Set<string>();
  for (const q of questions) {
    if (!Number.isSafeInteger(q.display_order) || q.display_order <= 0) throw new Error("A question is missing its stable progress identifier.");
    for (const key of [q.qid, q.audit_qid, String(q.display_order), `SB-${q.display_order}`, ...(q.legacy_ids ?? [])]) {
      if (!key) continue;
      const id = canonical(key), prior = map.get(id);
      if (prior && prior.qid !== q.qid) { map.delete(id); ambiguous.add(id); }
      else if (!ambiguous.has(id)) map.set(id, q);
    }
  }
  return map;
}
function answersFromEnvelope(value: unknown): JsonObject {
  if (!object(value)) return {};
  let state: unknown = value.parsed;
  if (!object(state) && typeof value.raw === "string") {
    try { state = JSON.parse(value.raw); } catch { state = {}; }
  }
  return object(state) && object(state.answers) ? state.answers : {};
}

/** Pure merge used by the browser and identity/recovery regression tests. */
export function mergeProgressSources(
  questions: readonly BankQuestion[], rows: unknown, envelope: unknown,
): ProgressMap {
  const known = aliases(questions), merged: ProgressMap = {}, priorities = new Map<string, number>();
  // Stable answer-state keys predate versioned qb_progress rows. Unknown browser
  // positions are never remapped to today's easy-to-hard sequence.
  for (const [key, raw] of Object.entries(answersFromEnvelope(envelope))) {
    const q = known.get(canonical(key));
    if (!q || !object(raw)) continue;
    const incoming = normalize(raw), current = merged[q.qid];
    const priority = key === q.qid ? 3 : key === String(q.display_order) ? 2 : key.startsWith("SB-") ? 1 : 0;
    if (!current || rowTime(incoming) > rowTime(current)
      || (rowTime(incoming) === rowTime(current) && priority > (priorities.get(q.qid) ?? -1))) {
      merged[q.qid] = { ...current, ...incoming }; priorities.set(q.qid, priority);
    }
  }
  if (object(rows)) for (const [key, raw] of Object.entries(rows)) {
    const q = known.get(canonical(key));
    if (!q || !object(raw)) continue;
    const stable = String(raw.submission_id ?? "").startsWith(`tmua-stable-v1|${q.display_order}|`);
    // Old numeric progress rows sometimes used a display position. A canonical
    // catalogue ID or explicit stable-submission marker proves identity.
    if (!stable && (/^\d+$/.test(key) || /^SB-\d+$/.test(key))) continue;
    const incoming = normalize(raw), current = merged[q.qid];
    // An old app_state answer has no per-question date. Preserve its explicit
    // fields in that ambiguous case rather than resurrecting an old bookmark
    // from the secondary progress table. Known dates still resolve newer edits.
    if (!current || (rowTime(current) > 0 && rowTime(incoming) > rowTime(current))) merged[q.qid] = { ...current, ...incoming };
    else merged[q.qid] = { ...incoming, ...current };
  }
  return merged;
}

export function getQuestionState(progress: ProgressMap, question: BankQuestion | string): QuestionProgress {
  return progress[typeof question === "string" ? canonical(question) : question.qid] ?? {};
}

async function request(viewerId: string, url: string, body?: unknown): Promise<JsonObject> {
  if (blocked.has(viewerId)) throw new AccountChangedError();
  const response = await fetch(url, {
    method: body === undefined ? "GET" : "POST", credentials: "same-origin", cache: "no-store",
    headers: body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body), signal: AbortSignal.timeout(15_000),
  });
  const payload: unknown = await response.json().catch(() => ({}));
  const data = object(payload) ? payload : {};
  const returnedOwner = data.user_id ?? (object(data.saved) ? data.saved.user_id : undefined);
  if ((returnedOwner !== undefined && returnedOwner !== viewerId)
    || (response.status === 409 && (data.code === "ACCOUNT_CHANGED" || data.error === "ACCOUNT_CHANGED"))) {
    blocked.add(viewerId); verifiedViewers.delete(viewerId); throw new AccountChangedError();
  }
  if (!response.ok || data.ok === false) {
    throw new Error(typeof data.error === "string" ? data.error : "Progress syncing is temporarily unavailable.");
  }
  if (body === undefined && returnedOwner !== viewerId) throw new Error("Could not verify the account for saved progress.");
  return data;
}

function pending(viewerId: string): Pending[] {
  const start = prefix(viewerId) + "pending:";
  return storageKeys().filter(key => key.startsWith(start)).flatMap(key => {
    const item = parsed(key);
    if (!object(item) || typeof item.id !== "string" || typeof item.qid !== "string"
      || !Number.isSafeInteger(item.displayOrder) || !object(item.progress)) return [];
    return [item as unknown as Pending];
  }).sort((a, b) => a.at - b.at || a.id.localeCompare(b.id));
}
function remember(viewerId: string, qid: string, value: QuestionProgress) {
  const state = sessionProgress.get(viewerId) ?? {};
  state[qid] = value; sessionProgress.set(viewerId, state);
  write(prefix(viewerId) + "question:" + qid, value);
}
function makeLegacy(value: QuestionProgress, original: JsonObject): JsonObject {
  const answer: JsonObject = { ...original, ...value, selected: value.selected_answer ?? null,
    checked: value.status === "correct" || value.status === "wrong",
    isCorrect: value.status === "correct", flagged: value.flagged ?? false };
  delete answer.solution_html;
  return answer;
}

async function flushUnlocked(viewerId: string) {
  if (blocked.has(viewerId)) throw new AccountChangedError();
  for (const item of pending(viewerId)) {
    const key = prefix(viewerId) + "pending:" + item.id;
    // Another tab may have completed this journal while this tab waited for a lock.
    if (!read(key)) continue;
    if (!item.canonicalSaved) {
      const p = item.progress;
      await request(viewerId, "/api/qb/progress/save", {
        product: PRODUCT, expected_user_id: viewerId, identity_version: "tmua-display-order-v1",
        updates: [{ question_id: String(item.displayOrder), status: p.status ?? "seen",
          selected_answer: p.selected_answer ?? null, flagged: p.flagged ?? false,
          time_spent: p.time_spent ?? null, last_seen_at: p.last_seen_at ?? p.updated_at,
          submission_id: p.submission_id ?? null, answer_elapsed_seconds: p.answer_elapsed_seconds ?? null,
          answer_submitted_at: p.answer_submitted_at ?? null }],
      });
      item.canonicalSaved = true; write(key, item);
    }
    // Prediction evidence already exists once qb_progress acknowledges the
    // checked attempt, even when its separate compact dashboard mirror fails.
    // Historical restores/bookmarks have no new checked-action marker.
    if (item.predictionEvidence && !item.predictionNotified) {
      item.predictionNotified = true; write(key, item);
      if (typeof window !== "undefined") window.dispatchEvent(new CustomEvent("ts-tmua-attempt-saved", {
        detail: { viewerId, submissionId: item.progress.submission_id },
      }));
    }
    if (!item.compactSaved) {
      await request(viewerId, "/api/qb/user-progress", {
        product: PRODUCT, key: "app_state", expected_user_id: viewerId, version: 2,
        patch: { answers: { [String(item.displayOrder)]: item.legacy } },
      });
      item.compactSaved = true; write(key, item);
    }
    remove(key);
  }
}

export async function flushPendingProgress(viewerId: string): Promise<ProgressSyncState> {
  const previous = sending.get(viewerId) ?? Promise.resolve();
  const task = previous.catch(() => {}).then(async () => {
    if (typeof navigator !== "undefined" && navigator.locks) {
      await navigator.locks.request(`ts-tmua-bank-progress:${viewerId}`, () => flushUnlocked(viewerId));
    } else await flushUnlocked(viewerId);
  });
  sending.set(viewerId, task);
  try { await task; return pending(viewerId).length ? "offline" : "synced"; }
  catch (error) { if (error instanceof AccountChangedError) throw error; return "offline"; }
  finally { if (sending.get(viewerId) === task) sending.delete(viewerId); }
}

export async function loadProgress(viewerId: string, questions: readonly BankQuestion[]): Promise<ProgressResult> {
  const known = aliases(questions), warnings: string[] = [];
  const results = await Promise.allSettled([
    request(viewerId, "/api/qb/progress/load?product=tmua-question-bank"),
    request(viewerId, "/api/qb/user-progress?product=tmua-question-bank&key=app_state&format=compact-v2"),
  ]);
  for (const result of results) if (result.status === "rejected" && result.reason instanceof AccountChangedError) throw result.reason;
  const rows = results[0].status === "fulfilled" ? results[0].value.progress : null;
  const envelope = results[1].status === "fulfilled" ? results[1].value.data : null;
  const fullyLoaded = results.every(result => result.status === "fulfilled");
  if (!fullyLoaded) warnings.push("Some saved progress could not be loaded. Your local work is retained; retry when connected.");
  if (results.some(result => result.status === "fulfilled")) verifiedViewers.add(viewerId);
  const progress = mergeProgressSources(questions, rows, envelope);
  const oldScope = `${STORAGE_KEY}__account_v3:${viewerId}:`;
  // The earlier account-scoped full state is useful during an outage or when no
  // cloud app_state exists. It is a read-only fallback, never an unsent delta:
  // another device may already have saved a newer answer or removed a bookmark.
  if (results[1].status === "rejected" || envelope === null || envelope === undefined) {
    const oldState = parsed(oldScope + "state"), oldAck = parsed(oldScope + "ack");
    const fallback = mergeProgressSources(questions, {}, { parsed: object(oldState) ? oldState : oldAck });
    for (const [qid, value] of Object.entries(fallback)) if (!progress[qid]) progress[qid] = value;
  }
  for (const [key, value] of Object.entries(answersFromEnvelope(envelope))) {
    const q = known.get(canonical(key));
    if (q && object(value)) legacyAnswers.set(`${viewerId}:${q.qid}`, value);
  }
  for (const q of questions) {
    const cached = normalize(parsed(prefix(viewerId) + "question:" + q.qid));
    if (Object.keys(cached).length && ((!fullyLoaded && !progress[q.qid])
      || (progress[q.qid] && rowTime(progress[q.qid]) > 0 && rowTime(cached) > rowTime(progress[q.qid])))) {
      progress[q.qid] = { ...progress[q.qid], ...cached };
    }
  }
  // Recover only explicitly owned legacy browser journals; unowned global keys
  // are deliberately left untouched for manual recovery.
  const oldJournals = storageKeys().filter(key => key.startsWith(oldScope + "pending:"))
    .map(key => ({ key, journal: parsed(key) }))
    .sort((a, b) => Number(object(a.journal) ? a.journal.at : 0) - Number(object(b.journal) ? b.journal.at : 0)
      || a.key.localeCompare(b.key));
  for (const { key, journal } of oldJournals) {
    if (!object(journal) || !object(journal.patch) || !object(journal.patch.answers)) continue;
    const local = mergeProgressSources(questions, {}, { parsed: journal.patch });
    for (const [qid, value] of Object.entries(local)) {
      const q = known.get(qid), at = Number(journal.at ?? 0);
      if (!q || !Number.isFinite(at) || at <= 0 || (progress[qid] && at <= rowTime(progress[qid]))) continue;
      const id = `legacy-${encodeURIComponent(key)}-${at}-${encodeURIComponent(qid)}`;
      const marker = prefix(viewerId) + "imported:" + id;
      // Once acknowledged, the retained original is an archive, not a fresh
      // edit. Any still-pending imported journal is applied separately below.
      if (read(marker)) continue;
      const merged = { ...progress[qid], ...value, updated_at: new Date(at).toISOString() };
      progress[qid] = merged;
      // Import an explicitly owned old journal once. Keep the original intact;
      // rollback to the earlier UI remains possible without assigning its data
      // to any other account.
      if (!read(marker)) {
        // An old compact journal proves a pending progress edit, but does not
        // prove a newly observed timed answer. Preserve an original stable
        // attempt ID where present; never manufacture a historical exposure.
        if (!merged.submission_id?.startsWith(`tmua-stable-v1|${q.display_order}|`)) merged.submission_id = null;
        write(prefix(viewerId) + "pending:" + id, { id, qid, displayOrder: q.display_order, at,
          progress: merged, legacy: makeLegacy(merged, legacyAnswers.get(`${viewerId}:${qid}`) ?? {}),
          canonicalSaved: false, compactSaved: false } satisfies Pending);
        write(marker, true);
      }
    }
  }
  for (const item of pending(viewerId)) {
    const q = known.get(item.qid);
    if (q && q.display_order === item.displayOrder) progress[q.qid] = { ...progress[q.qid], ...item.progress };
  }
  sessionProgress.set(viewerId, progress);
  for (const [qid, value] of Object.entries(progress)) remember(viewerId, qid, value);
  const synced = verifiedViewers.has(viewerId) ? await flushPendingProgress(viewerId) : "offline";
  if (storageUnavailable) warnings.push("This browser cannot keep a durable offline copy. Keep this page open until progress syncs.");
  return { progress, syncState: fullyLoaded && synced === "synced" ? "synced" : "offline", warnings };
}

export async function saveQuestionProgress(
  viewerId: string, question: BankQuestion, patch: QuestionProgress,
): Promise<{ syncState: ProgressSyncState; progress: QuestionProgress; warnings: string[] }> {
  if (blocked.has(viewerId)) throw new AccountChangedError();
  if (!Number.isSafeInteger(question.display_order) || question.display_order <= 0) throw new Error("A stable question identifier is required.");
  const now = new Date().toISOString();
  const previous = sessionProgress.get(viewerId)?.[question.qid];
  const freshStableId = typeof patch.submission_id === "string"
    && patch.submission_id.startsWith(`tmua-stable-v1|${question.display_order}|`)
    && patch.submission_id !== previous?.submission_id;
  const checkedAction = (patch.status === "correct" || patch.status === "wrong")
    && typeof patch.selected_answer === "string" && patch.selected_answer.trim() !== ""
    && (freshStableId || (timestamp(patch.answer_submitted_at) > 0
      && patch.answer_submitted_at !== previous?.answer_submitted_at));
  const progress = { ...previous, ...normalize(patch), updated_at: now };
  progress.last_seen_at ??= now;
  // Only a new checked action can mint an observed attempt. In particular,
  // bookmarking a restored answer must not manufacture its first exposure.
  if (checkedAction && !freshStableId) {
    progress.submission_id = `tmua-stable-v1|${question.display_order}|${crypto.randomUUID()}`;
  } else if (!progress.submission_id?.startsWith(`tmua-stable-v1|${question.display_order}|`)) {
    progress.submission_id = null;
  }
  const legacy = makeLegacy(progress, legacyAnswers.get(`${viewerId}:${question.qid}`) ?? {});
  legacyAnswers.set(`${viewerId}:${question.qid}`, legacy);
  const id = `${String(Date.now()).padStart(15, "0")}-${String(++sequence).padStart(8, "0")}-${crypto.randomUUID()}`;
  write(prefix(viewerId) + "pending:" + id, { id, qid: question.qid, displayOrder: question.display_order,
    at: Date.now(), progress, legacy, canonicalSaved: false, compactSaved: false,
    predictionEvidence: checkedAction, predictionNotified: false } satisfies Pending);
  remember(viewerId, question.qid, progress);
  const syncState = await flushPendingProgress(viewerId);
  return { progress, syncState, warnings: storageUnavailable
    ? ["This browser cannot keep a durable offline copy. Keep this page open until progress syncs."] : [] };
}

if (typeof window !== "undefined") window.addEventListener("online", () => {
  for (const viewerId of verifiedViewers) void flushPendingProgress(viewerId).catch(() => {});
});
