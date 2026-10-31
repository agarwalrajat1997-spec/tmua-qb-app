import { get, set, del } from "idb-keyval";
import type { Board, Feedback } from "../types";
import type { Notebook } from "./notebook-store";
import { restoreCloud, queueCloud } from "./cloud-storage";
const writes = new Map<string, Promise<void>>();
export async function loadBoard(id: string) {
  await writes.get(id)?.catch(() => {});
  const value = await restoreCloud<Board>(
    `board:${id}`,
    await get<Board>(`ts-board-v1:${id}`),
  );
  if (value) await set(`ts-board-v1:${id}`, value);
  return value;
}
export function saveBoard(id: string, value: Board) {
  const pending = (writes.get(id) ?? Promise.resolve())
    .catch(() => {})
    .then(async () => {
      await set(`ts-board-v1:${id}`, value);
      await queueCloud(`board:${id}`, value);
    });
  writes.set(id, pending);
  return pending;
}
export const deleteBoard = (id: string) => del(`ts-board-v1:${id}`);
export const loadReview = async (id: string) =>
  restoreCloud<Feedback>(
    `review:${id}`,
    await get<Feedback>(`ts-board-review-v1:${id}`),
  );
export const saveReview = async (id: string, review: Feedback) => {
  await set(`ts-board-review-v1:${id}`, review);
  await queueCloud(`review:${id}`, review);
};
export const loadNotebook = async (id: string) =>
  restoreCloud<Notebook>(
    `notebook:${id}`,
    await get<Notebook>(`ts-notebook-v2:${id}`),
  );
export const saveNotebook = async (id: string, value: Notebook) => {
  await set(`ts-notebook-v2:${id}`, value);
  await queueCloud(`notebook:${id}`, value);
};
export type PadView = {
  view: { x: number; y: number; w: number; h: number };
  top: number;
  left: number;
};
export const loadPadView = (id: string) => get<PadView>(`ts-pad-view:${id}`);
export const savePadView = (id: string, value: PadView) =>
  set(`ts-pad-view:${id}`, value);
export function readLocal<T>(key: string, fallback: T): T {
  try {
    return JSON.parse(localStorage.getItem(key) ?? "null") ?? fallback;
  } catch {
    return fallback;
  }
}
