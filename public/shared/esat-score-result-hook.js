(function () {
  "use strict";

  var running = false;

  function rawScoresFromResult(resultRoot) {
    return Array.prototype.slice.call(
      resultRoot.querySelectorAll(".result-mini div"),
      0,
      3
    ).map(function (element) {
      var match = String(element.textContent || "").match(/\d+/);
      return match ? Number(match[0]) : NaN;
    });
  }

  async function enhanceExistingResult() {
    if (running || !window.TS_ESAT_SCORE_ESTIMATES) return;
    var resultCard = document.querySelector(".result-card");
    if (!resultCard || resultCard.querySelector(".ts-esat-estimate")) return;

    var scores = rawScoresFromResult(resultCard);
    if (scores.length !== 3 || scores.some(function (score) { return !Number.isFinite(score); })) {
      return;
    }

    running = true;
    try {
      var profileTestId = typeof testId === "string" ? testId : "";
      var markup = await window.TS_ESAT_SCORE_ESTIMATES.fetchAndRender({
        testId: profileTestId,
        rawScores: scores
      });
      var target = resultCard.querySelector(".result-grid");
      if (target && !resultCard.querySelector(".ts-esat-estimate")) {
        target.insertAdjacentHTML("beforebegin", markup);
      }
    } finally {
      running = false;
    }
  }

  var observer = new MutationObserver(function () {
    enhanceExistingResult();
  });

  observer.observe(document.documentElement, {
    childList: true,
    subtree: true
  });
  enhanceExistingResult();
})();

