(() => {
  "use strict";

  if (window.__TS_TEST_FULLSCREEN_V1__) return;
  window.__TS_TEST_FULLSCREEN_V1__ = true;

  const documentRoot = document.documentElement;

  function currentFullscreenElement() {
    return (
      document.fullscreenElement ||
      document.webkitFullscreenElement ||
      document.msFullscreenElement ||
      null
    );
  }

  function enterFullscreen() {
    if (currentFullscreenElement()) {
      return Promise.resolve(true);
    }

    const request =
      documentRoot.requestFullscreen ||
      documentRoot.webkitRequestFullscreen ||
      documentRoot.msRequestFullscreen;

    if (typeof request !== "function") {
      console.info("[TS fullscreen] Fullscreen is not supported by this browser.");
      return Promise.resolve(false);
    }

    try {
      const result = request.call(documentRoot);

      if (result && typeof result.then === "function") {
        return result
          .then(() => true)
          .catch((error) => {
            console.info("[TS fullscreen] Fullscreen request was declined.", error);
            return false;
          });
      }

      return Promise.resolve(true);
    } catch (error) {
      console.info("[TS fullscreen] Fullscreen request failed.", error);
      return Promise.resolve(false);
    }
  }

  function exitFullscreen() {
    if (!currentFullscreenElement()) {
      return Promise.resolve(true);
    }

    const exit =
      document.exitFullscreen ||
      document.webkitExitFullscreen ||
      document.msExitFullscreen;

    if (typeof exit !== "function") {
      return Promise.resolve(false);
    }

    try {
      const result = exit.call(document);

      if (result && typeof result.then === "function") {
        return result
          .then(() => true)
          .catch((error) => {
            console.info("[TS fullscreen] Could not exit fullscreen.", error);
            return false;
          });
      }

      return Promise.resolve(true);
    } catch (error) {
      console.info("[TS fullscreen] Could not exit fullscreen.", error);
      return Promise.resolve(false);
    }
  }

  window.TS_TEST_FULLSCREEN = {
    enter: enterFullscreen,
    exit: exitFullscreen
  };

  const START_IDS = new Set([
    "start-button",
    "start-btn",
    "start-test",
    "start-exam",
    "start-paper",
    "begin-button",
    "begin-btn",
    "begin-test",
    "begin-exam",
    "begin-paper",
    "startButton",
    "startBtn",
    "startTest",
    "startExam"
  ]);

  const SUBMIT_IDS = new Set([
    "submit-btn",
    "submit-button",
    "submit-test",
    "submit-exam",
    "finish-btn",
    "finish-button",
    "finish-test",
    "finish-exam",
    "end-test",
    "end-exam",
    "complete-test",
    "final-submit",
    "submitBtn",
    "submitButton",
    "finishTest"
  ]);

  const START_LABEL =
    /^(start|start exam|start test|start paper|begin|begin exam|begin test|begin paper)$/i;

  const SUBMIT_LABEL =
    /^(submit|submit test|submit exam|finish|finish test|finish exam|end test|end exam|complete test|final submit)$/i;

  const CONTROL_SELECTOR = [
    "button",
    "input[type='button']",
    "input[type='submit']",
    "[role='button']",
    "a"
  ].join(",");

  function getControl(target) {
    if (!(target instanceof Element)) return null;
    return target.closest(CONTROL_SELECTOR);
  }

  function getControlLabel(control) {
    return String(
      control.getAttribute("aria-label") ||
      control.getAttribute("title") ||
      control.value ||
      control.textContent ||
      ""
    )
      .replace(/\s+/g, " ")
      .trim();
  }

  function isStartControl(control) {
    if (!control) return false;

    return (
      START_IDS.has(control.id) ||
      control.dataset.fullscreenStart === "true" ||
      START_LABEL.test(getControlLabel(control))
    );
  }

  function isSubmitControl(control) {
    if (!control) return false;

    return (
      SUBMIT_IDS.has(control.id) ||
      control.dataset.fullscreenSubmit === "true" ||
      SUBMIT_LABEL.test(getControlLabel(control))
    );
  }

  function isVisible(element) {
    if (!element || !(element instanceof Element)) return false;
    if (element.hidden) return false;
    if (element.getAttribute("aria-hidden") === "true") return false;

    const style = window.getComputedStyle(element);

    if (
      style.display === "none" ||
      style.visibility === "hidden" ||
      Number(style.opacity) === 0
    ) {
      return false;
    }

    return element.getClientRects().length > 0;
  }

  function resultScreenIsVisible() {
    const selectors = [
      "#results-screen",
      "#result-screen",
      "#results-page",
      "#score-screen",
      "#review-screen",
      ".results-screen",
      ".result-screen",
      ".results-page",
      ".score-screen",
      ".submission-results",
      "[data-screen='results']",
      "[data-view='results']",
      "[data-page='results']"
    ];

    for (const selector of selectors) {
      const element = document.querySelector(selector);

      if (isVisible(element)) {
        return true;
      }
    }

    const headings = document.querySelectorAll("h1, h2, h3");

    for (const heading of headings) {
      if (!isVisible(heading)) continue;

      const text = String(heading.textContent || "")
        .replace(/\s+/g, " ")
        .trim();

      if (
        /^(test results|exam results|your results|test complete|exam complete|submission complete|score summary)$/i.test(
          text
        )
      ) {
        return true;
      }
    }

    return false;
  }

  /*
   * Fullscreen must be requested directly inside the user's Start click.
   * Capturing phase ensures this runs before each template's own handler.
   */
  document.addEventListener(
    "click",
    (event) => {
      const control = getControl(event.target);

      if (isStartControl(control)) {
        void enterFullscreen();
        return;
      }

      if (!isSubmitControl(control)) return;

      /*
       * Do not exit immediately because some tests show a confirmation box.
       * After confirmation, the submit control normally becomes disabled,
       * disappears, or the results screen becomes visible.
       */
      window.setTimeout(() => {
        if (
          resultScreenIsVisible() ||
          !control.isConnected ||
          control.disabled ||
          !isVisible(control)
        ) {
          void exitFullscreen();
        }
      }, 500);
    },
    true
  );

  /*
   * Covers templates that use a real HTML form submission.
   */
  document.addEventListener(
    "submit",
    () => {
      void exitFullscreen();
    },
    true
  );

  /*
   * Covers asynchronous submissions and automatic timer submissions.
   */
  const observer = new MutationObserver(() => {
    if (currentFullscreenElement() && resultScreenIsVisible()) {
      void exitFullscreen();
    }
  });

  function startObserver() {
    if (!document.body) return;

    observer.observe(document.body, {
      subtree: true,
      childList: true,
      attributes: true,
      attributeFilter: [
        "class",
        "style",
        "hidden",
        "aria-hidden",
        "disabled"
      ]
    });
  }

  if (document.body) {
    startObserver();
  } else {
    document.addEventListener("DOMContentLoaded", startObserver, {
      once: true
    });
  }

  /*
   * Navigation naturally exits fullscreen, but this handles browsers
   * where the page is placed in the back-forward cache.
   */
  window.addEventListener("pagehide", () => {
    void exitFullscreen();
  });
})();