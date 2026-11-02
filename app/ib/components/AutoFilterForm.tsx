"use client";

import { createContext, useContext, useEffect, useRef, useState, useTransition, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import styles from "../questions.module.css";

const FilterContext = createContext<{ pending: boolean; change: (name: string, values: string[]) => void } | null>(null);
export const useAutoFilters = () => useContext(FilterContext);

/** Keep the current form and question list mounted during client-side navigation. */
export default function AutoFilterForm({ action, children, className }: { action: string; children: ReactNode; className: string }) {
  const router = useRouter();
  const form = useRef<HTMLFormElement>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [pending, startTransition] = useTransition();
  const [typing, setTyping] = useState(false);
  useEffect(() => () => { if (timer.current) clearTimeout(timer.current); }, []);

  function navigate(name?: string, values: string[] = []) {
    if (!form.current) return;
    if (timer.current) clearTimeout(timer.current);
    timer.current = null;
    setTyping(false);
    const query = new URLSearchParams();
    for (const [key, value] of new FormData(form.current)) if (typeof value === "string" && value.trim()) query.append(key, value.trim());
    if (name) { query.delete(name); for (const value of values) query.append(name, value); }
    query.delete("page");
    // FormData includes all current controls, even when an earlier request is pending.
    // This prevents a rapid second checkbox click from dropping the first choice.
    startTransition(() => router.replace(action + (query.size ? "?" + query : ""), { scroll: false }));
  }
  return <FilterContext.Provider value={{ pending: pending || typing, change: navigate }}>
    <form ref={form} className={className} method="GET" action={action} aria-busy={pending || typing} onSubmit={event => { event.preventDefault(); navigate(); }} onChange={event => {
      if (!(event.target instanceof HTMLInputElement) || event.target.type !== "search") return;
      if (timer.current) clearTimeout(timer.current);
      setTyping(true);
      timer.current = setTimeout(() => navigate(), 300);
    }}>
      {children}
      <span role="status" aria-live="polite" className={styles.filterStatus}>{pending || typing ? "Updating questions…" : "Filters update automatically"}</span>
    </form>
  </FilterContext.Provider>;
}

export function AutoSearchInput({ search }: { search: string }) {
  const context = useAutoFilters();
  const [draft, setDraft] = useState({ source: search, value: search });
  if (!context?.pending && draft.source !== search) setDraft({ source: search, value: search });
  return <input name="q" type="search" value={draft.value} onChange={event => setDraft({ ...draft, value: event.target.value })} placeholder="Keyword or question number" maxLength={160} />;
}
