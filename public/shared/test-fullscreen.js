(() => {
  "use strict";
  if (window.__TS_TEST_FULLSCREEN_V3__) return;
  window.__TS_TEST_FULLSCREEN_V3__ = true;

  const root = document.documentElement;
  const nativeFetch = window.fetch.bind(window);
  const APP_ORIGIN = "https://app.thrivingscholars.com";

  // The 15 recombined ESAT papers expose three section fields, while the
  // existing EmailJS template renders paper1 and paper2. Match the working
  // original ESAT mocks by combining sections 2 and 3 into paper2. Keep
  // paper3 as well for any future three-field template.
  const recombinedEsatPath = /^\/esat-practice-tests\/tests\/esat-(?:physics-chemistry|physics-biology|maths2-chemistry|maths2-biology|chemistry-biology)-level-[012](?:\/index\.html|\/)?$/;

  const absoluteEsatSolutionUrl = value => {
    const raw = String(value || "").trim();
    if (!raw) return raw;
    try {
      const url = new URL(raw, APP_ORIGIN);
      if (url.pathname.startsWith("/esat-practice-tests/solutions/")) {
        return `${APP_ORIGIN}${url.pathname}${url.search}${url.hash}`;
      }
      return url.href;
    } catch {
      return raw;
    }
  };

  const rewriteEsatSolutionLinks = () => {
    if (!recombinedEsatPath.test(location.pathname)) return;
    document.querySelectorAll(
      'a[href^="/esat-practice-tests/solutions/"],iframe[src^="/esat-practice-tests/solutions/"]'
    ).forEach(el => {
      const attr = el.tagName === "IFRAME" ? "src" : "href";
      const value = el.getAttribute(attr);
      const absolute = absoluteEsatSolutionUrl(value);
      if (absolute && absolute !== value) el.setAttribute(attr, absolute);
    });
  };

  const installEsatEmailReportAdapter = () => {
    if (!recombinedEsatPath.test(location.pathname)) return true;
    const client = window.emailjs;
    if (!client || typeof client.send !== "function") return false;
    if (client.__tsThreeSectionAdapter) return true;

    const nativeSend = client.send.bind(client);
    client.send = (serviceId, templateId, templateParams, ...rest) => {
      const payload = templateParams && typeof templateParams === "object"
        ? { ...templateParams }
        : templateParams;

      if (payload) {
        payload.solution_link = absoluteEsatSolutionUrl(payload.solution_link);

        const paper1 = String(payload.paper1 || "").trim();
        const paper2 = String(payload.paper2 || "").trim();
        const paper3 = String(payload.paper3 || "").trim();

        payload.paper1 = paper1;
        if (paper3 && !paper2.includes(paper3)) {
          payload.paper2 = `${paper2}\n\n${paper3}`;
        } else {
          payload.paper2 = paper2;
        }
        payload.paper3 = paper3;
      }

      return nativeSend(serviceId, templateId, payload, ...rest);
    };
    client.__tsThreeSectionAdapter = true;
    return true;
  };

  if (!installEsatEmailReportAdapter()) {
    let attempts = 0;
    const retry = setInterval(() => {
      attempts += 1;
      if (installEsatEmailReportAdapter() || attempts >= 40) {
        clearInterval(retry);
      }
    }, 250);
  }

  const current = () =>
    document.fullscreenElement ||
    document.webkitFullscreenElement ||
    document.msFullscreenElement ||
    null;

  async function enter() {
    if (current()) return true;
    const fn =
      root.requestFullscreen ||
      root.webkitRequestFullscreen ||
      root.msRequestFullscreen;
    if (typeof fn !== "function") return false;
    try { await fn.call(root); return true; }
    catch (e) { console.info("[TS fullscreen] Request declined.", e); return false; }
  }

  async function exit() {
    if (!current()) return true;
    const fn =
      document.exitFullscreen ||
      document.webkitExitFullscreen ||
      document.msExitFullscreen;
    if (typeof fn !== "function") return false;
    try { await fn.call(document); return true; }
    catch (e) { console.info("[TS fullscreen] Exit failed.", e); return false; }
  }

  window.TS_TEST_FULLSCREEN = { enter, exit };

  const selector = [
    "button",
    "input[type='button']",
    "input[type='submit']",
    "[role='button']",
    "a"
  ].join(",");

  const startIds = new Set([
    "start-button","start-btn","start-test","start-exam","start-paper",
    "begin-button","begin-btn","begin-test","begin-exam",
    "startButton","startBtn","startTest","startExam"
  ]);

  const submitIds = new Set([
    "submit-btn","submit-button","submit-test","submit-exam",
    "finish-btn","finish-button","finish-test","finish-exam",
    "complete-test","final-submit","submitBtn","submitButton","finishTest"
  ]);

  const startLabel =
    /^(start|begin)(?:\s+(?:test|exam|paper|mock|paper\s*[12]))?\s*$/i;
  const submitLabel =
    /^(submit|finish|complete|end)(?:\s+(?:test|exam|paper|mock|answers|paper\s*[12]))?\s*$/i;
  const skipBreakLabel =
    /^(skip\s+break|start\s+(?:paper\s*2|math)(?:\s+now)?)\s*$/i;
  const skipBreakHandler = /(?:^|[^\w$])skipBreak\s*\(/;

  const control = target =>
    target instanceof Element ? target.closest(selector) : null;

  const label = el => String(
    el?.getAttribute("aria-label") ||
    el?.getAttribute("title") ||
    el?.value ||
    el?.textContent ||
    ""
  ).replace(/\s+/g, " ").trim();

  const visible = el => {
    if (!el || !(el instanceof Element) || el.hidden) return false;
    const s = getComputedStyle(el);
    return s.display !== "none" &&
      s.visibility !== "hidden" &&
      Number(s.opacity) !== 0 &&
      el.getClientRects().length > 0;
  };

  const resultsVisible = () => {
    const selectors = [
      "#results-screen","#result-screen","#results-page","#score-screen",
      "#review-screen",".results-screen",".result-screen",".results-page",
      ".score-screen",".submission-results","[data-screen='results']",
      "[data-view='results']","[data-page='results']"
    ];
    if (selectors.some(x => visible(document.querySelector(x)))) return true;
    return [...document.querySelectorAll("h1,h2,h3")].some(h =>
      visible(h) &&
      /^(test results|exam results|your results|test complete|exam complete|submission complete|score summary)$/i
        .test(label(h))
    );
  };

  document.addEventListener("click", event => {
    const el = control(event.target);
    if (!el) return;
    const onclick = el.getAttribute("onclick") || "";

    if (
      el.dataset.fullscreenBreak === "true" ||
      skipBreakHandler.test(onclick) ||
      skipBreakLabel.test(label(el))
    ) {
      void enter();
      return;
    }

    if (
      startIds.has(el.id) ||
      el.dataset.fullscreenStart === "true" ||
      startLabel.test(label(el))
    ) {
      void enter();
      return;
    }

    const isSubmit =
      submitIds.has(el.id) ||
      el.dataset.fullscreenSubmit === "true" ||
      submitLabel.test(label(el));

    if (!isSubmit) return;

    let checks = 0;
    const timer = setInterval(() => {
      checks += 1;
      rewriteEsatSolutionLinks();
      if (
        resultsVisible() ||
        !el.isConnected ||
        el.disabled ||
        !visible(el)
      ) {
        clearInterval(timer);
        void exit();
      } else if (checks >= 20) {
        clearInterval(timer);
      }
    }, 250);
  }, true);

  window.fetch = async (...args) => {
    const response = await nativeFetch(...args);
    try {
      const input = args[0];
      const url = typeof input === "string"
        ? input
        : String(input?.url || "");
      if (response.ok && url.includes("/api/practice-tests/submit")) {
        rewriteEsatSolutionLinks();
        void exit();
      }
    } catch {}
    return response;
  };

  const observer = new MutationObserver(() => {
    rewriteEsatSolutionLinks();
    if (current() && resultsVisible()) void exit();
  });

  const observe = () => {
    if (!document.body) return;
    rewriteEsatSolutionLinks();
    observer.observe(document.body, {
      subtree: true,
      childList: true,
      attributes: true,
      attributeFilter: ["class","style","hidden","aria-hidden","disabled"]
    });
  };

  if (document.body) observe();
  else document.addEventListener("DOMContentLoaded", observe, { once: true });

  addEventListener("pagehide", () => void exit());
})();
