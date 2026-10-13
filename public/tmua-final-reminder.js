(function () {
  "use strict";
  if (window.self !== window.top || window.__tsTmuaFinalReminder) return;
  window.__tsTmuaFinalReminder = true;
  const START = Date.parse("2026-10-13T00:00:00+05:30");
  const END = Date.parse("2026-10-17T00:00:00+05:30");
  const KEY = "tmua-final-warmup-2026-10-13";
  const API = "/api/student/tmua-final-reminder";
  const PDF = "/tmua-resources/tmua-2026-mathematical-reasoning-practice.pdf";
  let modal, timer, checking = false, saving = false, authenticated = false, priorFocus;
  let dismissed = false, pending = false;
  try { dismissed = localStorage.getItem(KEY) === "dismissed"; pending = localStorage.getItem(KEY + "-pending") === "1"; } catch {}
  dismissed = dismissed || document.cookie.split("; ").includes(KEY + "=dismissed");
  function active() { return Date.now() >= START && Date.now() < END; }
  function pathIsTmua(url) {
    const path = url.pathname.replace(/\/$/, "") || "/";
    if (path === "/dashboard") return !["sat", "amc", "esat"].includes((url.searchParams.get("view") || "").toLowerCase());
    return ["/tmua", "/tmua-question-bank", "/tmua-question-bank/index.html", "/question-bank-tmua",
      "/practice-tests", "/practice-tests/index.html", "/tmua-classes", "/tmua-classes/index.html",
      "/tmua-solutions", "/tmua-solutions/index.html"].includes(path);
  }
  function eligible() {
    const url = new URL(location.href);
    const path = url.pathname.replace(/\/$/, "");
    if (path === "/dashboard") return pathIsTmua(url) && !!document.querySelector("[data-tmua-reminder-audience]");
    if (path === "/login") {
      try {
        const target = new URL(url.searchParams.get("next") || "/dashboard", location.origin);
        return target.origin === location.origin && pathIsTmua(target);
      } catch { return false; }
    }
    return pathIsTmua(url);
  }
  function hide() {
    if (modal) { modal.close(); modal.remove(); modal = undefined; }
    if (priorFocus && priorFocus.isConnected) priorFocus.focus();
  }
  function remember() {
    dismissed = true;
    try { localStorage.setItem(KEY, "dismissed"); } catch {}
    document.cookie = KEY + "=dismissed; Path=/; Max-Age=31536000; SameSite=Lax" + (location.protocol === "https:" ? "; Secure" : "");
  }
  function setPending(value) {
    pending = value;
    try { if (value) localStorage.setItem(KEY + "-pending", "1"); else localStorage.removeItem(KEY + "-pending"); } catch {}
  }
  async function saveReceipt() {
    if (saving || !pending || !active()) return;
    saving = true;
    try {
      const result = await fetch(API, {method:"POST",credentials:"same-origin",cache:"no-store",
        headers:{"Content-Type":"application/json"},body:JSON.stringify({action:"dismiss"}),signal:AbortSignal.timeout(10000)});
      if (result.ok && (await result.json()).dismissed === true) setPending(false);
    } catch { /* The local dismissal still lets the student continue; retry online. */ }
    finally { saving = false; }
  }
  function dismiss() {
    remember();
    if (authenticated) setPending(true);
    hide();
    void saveReceipt();
  }
  function show() {
    if (modal || dismissed || !active() || !eligible()) return;
    if (document.querySelector("dialog[open], [aria-modal='true']")) { schedule(1800); return; }
    if (!document.querySelector("link[data-tmua-reminder-css]")) {
      const css = document.createElement("link");
      css.rel = "stylesheet"; css.href = "/tmua-final-reminder.css";
      css.dataset.tmuaReminderCss = "true"; css.addEventListener("load", function () { schedule(0); });
      document.head.appendChild(css);
      return;
    }
    if (!document.querySelector("link[data-tmua-reminder-css]").sheet) return;
    modal = document.createElement("dialog");
    modal.className = "ts-final-reminder"; modal.setAttribute("aria-labelledby", "ts-final-reminder-title");
    modal.setAttribute("aria-describedby", "ts-final-reminder-intro");
    modal.innerHTML = `
      <button type="button" class="ts-final-close" aria-label="Close reminder and do not show again">×</button>
      <p class="ts-final-brand">THRIVING SCHOLARS · TMUA</p>
      <h2 id="ts-final-reminder-title">Your final TMUA warm-up.</h2>
      <p id="ts-final-reminder-intro">Practise familiar maths through longer, multi-step routes. Look for an efficient approach before diving into lengthy calculations.</p>
      <p class="ts-final-label">A focused revision checklist</p>
      <ul>
        <li><strong>Exact algebra</strong> — fractions, surds and manipulation.</li>
        <li><strong>Geometry</strong> — spot the useful idea before reaching for brute-force algebra.</li>
        <li><strong>Trigonometric reasoning.</strong></li>
        <li><strong>Counting and combinatorics.</strong></li>
        <li><strong>Paper 2 logic</strong> — necessary vs sufficient, contrapositives, counterexamples and errors in proofs.</li>
      </ul>
      <a class="ts-final-pdf" href="${PDF}" target="_blank" rel="noopener">Try 10 extra practice questions <span aria-hidden="true">↗</span></a>
      <p class="ts-final-meta">Free PDF · Worked solutions included · No login needed</p>
      <p class="ts-final-signoff"><strong>All the best — trust your preparation.</strong><br>Stay calm, work efficiently, and move on if a question is taking too long.</p>
      <p class="ts-final-note">General revision guidance, not a prediction of exam content.</p>
      <button type="button" class="ts-final-dismiss">Got it — don’t show again</button>`;
    modal.querySelector(".ts-final-close").addEventListener("click", dismiss);
    modal.querySelector(".ts-final-dismiss").addEventListener("click", dismiss);
    modal.addEventListener("cancel", function (event) { event.preventDefault(); dismiss(); });
    priorFocus = document.activeElement;
    document.body.appendChild(modal); modal.showModal();
  }
  async function check() {
    if (!active() || !eligible()) { hide(); return; }
    if (document.visibilityState !== "visible" || checking) return;
    if (dismissed) { hide(); if (pending) void saveReceipt(); return; }
    if (modal) return;
    checking = true;
    try {
      const result = await fetch(API, {credentials:"same-origin",cache:"no-store",signal:AbortSignal.timeout(10000)});
      if (result.status === 401) { authenticated = false; if ((await result.json()).active === true) show(); return; }
      if (!result.ok) { schedule(30000); return; }
      const payload = await result.json();
      authenticated = payload.authenticated === true;
      if (payload.dismissed === true) { remember(); hide(); return; }
      if (payload.active === true && payload.show === true) show();
    } catch { schedule(30000); }
    finally { checking = false; }
  }
  function schedule(delay) {
    clearTimeout(timer);
    if (!active() || !eligible()) { hide(); return; }
    timer = setTimeout(check, typeof delay === "number" ? delay : 800);
  }
  window.addEventListener("tmua-reminder-route", schedule);
  window.addEventListener("popstate", schedule);
  window.addEventListener("focus", schedule);
  window.addEventListener("online", schedule);
  document.addEventListener("visibilitychange", schedule);
  window.addEventListener("storage", function (event) {
    if (event.key === KEY && event.newValue === "dismissed") { dismissed = true; hide(); }
  });
  // The shared dashboard resolves programme access asynchronously.
  new MutationObserver(function () {
    if (!eligible()) { hide(); return; }
    if (!modal && !dismissed && !checking) schedule();
  }).observe(document.body, {childList:true,subtree:true});
  if (active()) setTimeout(hide, Math.min(END - Date.now(), 2147483647));
  schedule();
})();
