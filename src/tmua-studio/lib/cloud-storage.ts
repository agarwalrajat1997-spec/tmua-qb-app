import { get, set, keys, update } from "idb-keyval";
import { STUDIO_API, studioUrl, studioViewerId } from "./api";
export type SyncState = "device" | "saving" | "synced" | "offline" | "conflict";
type Entry = {
  version: number;
  dirty: boolean;
  generation: string;
  value: unknown;
};
const states = new Map<string, SyncState>(),
  listeners = new Set<() => void>();
const timers = new Map<string, ReturnType<typeof setTimeout>>(),
  sending = new Map<string, Promise<void>>();
const supported = () => typeof window !== "undefined" && !!studioViewerId();
const ownedKey = (key: string) => !!studioViewerId() &&
  /^(board|notebook|review|view|session):/.test(key) &&
  key.split(":")[1] === "user" && key.split(":")[2] === studioViewerId();
const storageKey = (key: string) => `ts-cloud-v1:${key}`;
const emit = (key: string, state: SyncState) => {
  states.set(key, state);
  listeners.forEach((fn) => fn());
};
export const subscribeSync = (fn: () => void) => {
  listeners.add(fn);
  return () => {
    listeners.delete(fn);
  };
};
export function syncState(key: string): SyncState {
  return states.get(key) ?? "device";
}
export function syncLabel(state: SyncState) {
  return {
    device: "Saved on this device",
    saving: "Saved on this device · syncing…",
    synced: "Synced to your private account",
    offline: "Saved on this device · sync pending",
    conflict: "Saved on this device · another device has changes",
  }[state];
}
async function cloudRead(key: string) {
  if (!ownedKey(key)) throw Error("This notebook belongs to a different signed-in account.");
  const r = await fetch(studioUrl("notebook", { key, expectedUserId: studioViewerId() }), {
    credentials: "same-origin",
    cache: "no-store",
    signal: AbortSignal.timeout(5000),
  });
  if (!r.ok) throw Error("Cloud copy unavailable");
  return r.json() as Promise<{ version: number; value?: unknown }>;
}
export async function restoreCloud<T>(
  key: string,
  local: T | undefined,
): Promise<T | undefined> {
  if (!supported() || !ownedKey(key)) return local;
  const meta = await get<Entry>(storageKey(key));
  if (meta?.dirty) {
    scheduleCloud(key);
    return meta.value as T;
  }
  try {
    const remote = await cloudRead(key);
    if (remote.version && remote.value !== undefined) {
      // Never replace a new edit that happened while the request was in flight.
      let dirtyValue: T | undefined;
      await update<Entry>(storageKey(key), (current) => {
        if (current?.dirty) {
          dirtyValue = current.value as T;
          return current;
        }
        return {
          version: remote.version,
          dirty: false,
          generation: crypto.randomUUID(),
          value: remote.value,
        };
      });
      if (dirtyValue !== undefined) return dirtyValue;
      emit(key, "synced");
      return remote.value as T;
    }
    if (local !== undefined) await queueCloud(key, local);
  } catch {
    emit(key, "offline");
  }
  return (meta?.value as T | undefined) ?? local;
}
export async function queueCloud(key: string, value: unknown) {
  if (!supported() || !ownedKey(key)) return;
  let changed = false,
    dirty = false;
  await update<Entry>(storageKey(key), (old) => {
    if (old && JSON.stringify(old.value) === JSON.stringify(value)) {
      dirty = old.dirty;
      return old;
    }
    changed = true;
    dirty = true;
    return {
      version: old?.version ?? 0,
      dirty: true,
      generation: crypto.randomUUID(),
      value,
    };
  });
  if (changed) emit(key, "saving");
  if (dirty) scheduleCloud(key);
}
function scheduleCloud(key: string) {
  clearTimeout(timers.get(key));
  timers.set(
    key,
    setTimeout(() => {
      timers.delete(key);
      void flushCloud(key);
    }, 900),
  );
}
export async function flushCloud(key: string): Promise<void> {
  if (!supported() || !ownedKey(key)) return;
  if (sending.has(key)) {
    await sending.get(key);
    return;
  }
  const task = (async () => {
    const entry = await get<Entry>(storageKey(key));
    if (!entry?.dirty) return;
    if (typeof navigator !== "undefined" && !navigator.onLine) {
      emit(key, "offline");
      return;
    }
    try {
      const r = await fetch(STUDIO_API, {
        method: "PUT",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-TS-Studio": "1" },
        body: JSON.stringify({
          action: "notebook",
          expectedUserId: studioViewerId(),
          key,
          baseVersion: entry.version,
          value: entry.value,
        }),
        signal: AbortSignal.timeout(15_000),
      });
      if (r.status === 409) {
        emit(key, "conflict");
        return;
      }
      if (!r.ok) throw Error("Sync failed");
      const remote = (await r.json()) as { version: number };
      let dirty = false;
      await update<Entry>(storageKey(key), (latest) => {
        if (!latest) return { ...entry, version: remote.version, dirty: false };
        dirty = latest.generation !== entry.generation;
        return { ...latest, version: remote.version, dirty };
      });
      emit(key, dirty ? "saving" : "synced");
      if (dirty) scheduleCloud(key);
    } catch {
      emit(key, "offline");
    }
  })().finally(() => sending.delete(key));
  sending.set(key, task);
  await task;
}
// A conflict never overwrites either device's working. Keep a local recovery copy
// before choosing the account copy; it remains exportable as JSON.
export async function resolveCloudConflict(
  key: string,
  choice: "account" | "device",
) {
  const local = await get<Entry>(storageKey(key));
  const remote = await cloudRead(key);
  if (local) await set(`ts-recovery:${key}:${Date.now()}`, local.value);
  if (remote.value !== undefined)
    await set(`ts-recovery-account:${key}:${Date.now()}`, remote.value);
  if (choice === "account") {
    await set(storageKey(key), {
      version: remote.version,
      dirty: false,
      generation: crypto.randomUUID(),
      value: remote.value,
    });
  } else if (local) {
    await set(storageKey(key), {
      ...local,
      version: remote.version,
      dirty: true,
      generation: crypto.randomUUID(),
    });
    await flushCloud(key);
  }
  return remote.value;
}
export async function resumeCloudSync() {
  if (!supported()) return;
  for (const key of await keys())
    if (typeof key === "string" && key.startsWith("ts-cloud-v1:")) {
      const doc = key.slice("ts-cloud-v1:".length);
      const value = await get<Entry>(key);
      if (ownedKey(doc) && value?.dirty && states.get(doc) !== "conflict") scheduleCloud(doc);
    }
}
if (typeof window !== "undefined")
  window.addEventListener("online", () => void resumeCloudSync());
