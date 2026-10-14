(function () {
  "use strict";
  if (window.self !== window.top || window.__tsEsatFinalReminder) return;
  window.__tsEsatFinalReminder = true;
  const START = Date.parse("2026-10-14T00:00:00+05:30");
  const END = Date.parse("2026-10-17T00:00:00+05:30");
  const KEY = "esat-final-warmup-2026-10-14";
  const API = "/api/student/esat-final-reminder";
  const PDF = "/esat-resources/esat-2026-extra-practice-pack.pdf";
  let modal, timer, checking = false, saving = false, authenticated = false, priorFocus;
  let dismissed = false, pending = false;
  try { dismissed = localStorage.getItem(KEY) === "dismissed"; pending = localStorage.getItem(KEY + "-pending") === "1"; } catch {}
  dismissed = dismissed || document.cookie.split("; ").includes(KEY + "=dismissed");
  function active() { return Date.now() >= START && Date.now() < END; }
  function pathIsEsat(url) {
    const path = url.pathname.replace(/\/$/, "") || "/";
    return ["/esat", "/esat-login", "/esat-question-bank", "/esat-question-bank/index.html",
      "/esat-practice-tests", "/esat-classes", "/esat-classes/index.html"].includes(path);
  }
  function eligible() {
    const url = new URL(location.href);
    const path = url.pathname.replace(/\/$/, "");
    if (path === "/login") {
      try {
        const target = new URL(url.searchParams.get("next") || "/", location.origin);
        return target.origin === location.origin && pathIsEsat(target);
      } catch { return false; }
    }
    return pathIsEsat(url);
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
      <p class="ts-final-brand">THRIVING SCHOLARS · ESAT</p>
      <h2 id="ts-final-reminder-title">Your final ESAT warm-up.</h2>
      <p id="ts-final-reminder-intro">A final, focused revision check. Practise only the modules you are sitting, and look for efficient routes before starting lengthy calculations.</p>
      <p class="ts-final-label">A focused revision checklist</p>
      <ul>
        <li><strong>Maths 1</strong> — probability, ratios and scaling, bounds, bearings, proportion and quick algebra. Aim for speed and smooth topic switches.</li>
        <li><strong>Maths 2</strong> — give algebra and geometry a focused review: manipulation, functions and graphs, trigonometry, sequences, logarithms and expansions. Keep calculus on your checklist too.</li>
        <li><strong>Physics</strong> — identify the principle, set up the equation, calculate accurately. Revisit electricity and look for efficient shortcuts.</li>
        <li><strong>Chemistry</strong> — apply your knowledge: tests and observations, reactivity, equilibrium, electrolysis, acids, halogens and ions.</li>
        <li><strong>Biology</strong> — precise concepts, experimental reasoning, osmosis, inheritance and enzymes.</li>
      </ul>
      <a class="ts-final-pdf" href="${PDF}" target="_blank" rel="noopener">Try 20 extra ESAT practice questions <span aria-hidden="true">↗</span></a>
      <p class="ts-final-meta">Free PDF · Worked solutions included · No login needed</p>
      <p class="ts-final-signoff"><strong>All the best — trust your preparation.</strong><br>Recognise the route, work efficiently, and move on if a question is taking too long.</p>
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
  window.addEventListener("esat-reminder-route", schedule);
  window.addEventListener("popstate", schedule);
  window.addEventListener("focus", schedule);
  window.addEventListener("online", schedule);
  document.addEventListener("visibilitychange", schedule);
  window.addEventListener("storage", function (event) {
    if (event.key === KEY && event.newValue === "dismissed") { dismissed = true; hide(); }
  });
  // React navigation and async page content can change route eligibility.
  new MutationObserver(function () {
    if (!eligible()) { hide(); return; }
    if (!modal && !dismissed && !checking) schedule();
  }).observe(document.body, {childList:true,subtree:true});
  if (active()) setTimeout(hide, Math.min(END - Date.now(), 2147483647));
  schedule();
})();
