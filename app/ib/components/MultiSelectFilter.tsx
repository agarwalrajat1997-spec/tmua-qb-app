"use client";

import { useEffect, useId, useRef, useState } from "react";
import { useAutoFilters } from "./AutoFilterForm";
import styles from "./multi-select-filter.module.css";

export type FilterOption = { value: string; label: string; detail?: string };

export default function MultiSelectFilter({ name, label, options, selected, allLabel = "All", wide = false }: {
  name: string; label: string; options: FilterOption[]; selected: string[]; allLabel?: string; wide?: boolean;
}) {
  const context = useAutoFilters();
  const source = JSON.stringify(selected);
  const [draft, setDraft] = useState({ source, values: selected });
  if (!context?.pending && draft.source !== source) setDraft({ source, values: selected });
  const values = draft.values;
  function change(next: string[]) {
    setDraft({ source, values: next });
    context?.change(name, next);
  }
  const id = useId();
  const details = useRef<HTMLDetailsElement>(null);
  const summary = useRef<HTMLElement>(null);
  useEffect(() => {
    let dismissFrame: number | null = null;
    function cancelDismissal() {
      if (dismissFrame !== null) cancelAnimationFrame(dismissFrame);
      dismissFrame = null;
    }
    function dismissAfterFocusSettles(pointer: boolean) {
      cancelDismissal();
      dismissFrame = requestAnimationFrame(() => {
        dismissFrame = null;
        const menu = details.current;
        if (!menu?.open || (!pointer && menu.contains(document.activeElement))) return;
        // Hiding a focused native details child during blur can crash Chromium.
        // Move any remaining internal focus before closing, after the event ends.
        if (menu.contains(document.activeElement)) summary.current?.focus();
        menu.open = false;
      });
    }
    function outsidePointer(event: PointerEvent) {
      const menu = details.current;
      if (!(event.target instanceof Node) || !menu?.open) return;
      if (menu.contains(event.target)) cancelDismissal();
      else dismissAfterFocusSettles(true);
    }
    function outsideFocus(event: FocusEvent) {
      const menu = details.current;
      if (!(event.target instanceof Node) || !menu?.open) return;
      if (menu.contains(event.target)) cancelDismissal();
      else dismissAfterFocusSettles(false);
    }
    // Null-related-target blurs from padding, scrollbars or window switching are
    // deliberately ignored. Only a real outside pointer/focus target dismisses.
    document.addEventListener("pointerdown", outsidePointer, true);
    document.addEventListener("focusin", outsideFocus, true);
    return () => {
      cancelDismissal();
      document.removeEventListener("pointerdown", outsidePointer, true);
      document.removeEventListener("focusin", outsideFocus, true);
    };
  }, []);
  return <div className={`${styles.field} ${wide ? styles.wide : ""}`}>
    <span id={id} className={styles.label}>{label}</span>
    <details ref={details} className={styles.dropdown} onKeyDown={event => {
      if (event.key === "Escape" && details.current) {
        event.preventDefault();
        summary.current?.focus();
        details.current.open = false;
      }
    }}>
      <summary ref={summary} aria-labelledby={`${id} ${id}-selection`}><span id={`${id}-selection`}>{values.length ? `${values.length} selected` : allLabel}</span><span aria-hidden="true">⌄</span></summary>
      <div className={styles.panel}>
        <div className={styles.toolbar}><span>Select any that apply</span><button type="button" onClick={() => change([])}>Clear</button></div>
        <fieldset aria-labelledby={id}>
          {options.map(option => <label key={option.value} className={styles.option}>
            <input type="checkbox" name={name} value={option.value} checked={values.includes(option.value)} onChange={event => change(event.target.checked ? [...values, option.value] : values.filter(value => value !== option.value))} />
            <span>{option.label}{option.detail ? <small>{option.detail}</small> : null}</span>
          </label>)}
        </fieldset>
      </div>
    </details>
  </div>;
}
