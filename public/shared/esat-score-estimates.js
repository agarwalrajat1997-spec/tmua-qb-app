(function (root) {
  "use strict";

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function unavailable(message) {
    return (
      '<section class="ts-esat-estimate ts-esat-estimate--unavailable">' +
      '<div class="ts-esat-estimate__heading">Estimated ESAT profile</div>' +
      '<p>' + escapeHtml(message || "Score estimate unavailable.") + '</p>' +
      '</section>'
    );
  }

  function render(estimate) {
    if (!estimate || !Array.isArray(estimate.modules)) {
      return unavailable();
    }

    var cards = estimate.modules.map(function (item) {
      return (
        '<article class="ts-esat-estimate__card">' +
        '<h3>' + escapeHtml(item.module) + '</h3>' +
        '<div class="ts-esat-estimate__score">' +
        Number(item.estimatedScore).toFixed(1) +
        '<span>/9.0</span></div>' +
        '<p>' + Number(item.raw) + '/27 raw</p>' +
        '</article>'
      );
    }).join("");

    return (
      '<section class="ts-esat-estimate" data-version="' +
      escapeHtml(estimate.version) + '">' +
      '<div class="ts-esat-estimate__top"><div>' +
      '<div class="ts-esat-estimate__heading">Predicted ESAT profile</div>' +
      '<div class="ts-esat-estimate__sub">Evidence-calibrated · ' +
      escapeHtml(estimate.difficulty) + ' source form</div></div>' +
      '<div class="ts-esat-estimate__average"><span>Predicted combined practice score</span>' +
      '<strong>' + Number(
        estimate.predictedCombinedPracticeScore == null
          ? estimate.averageModuleEstimate
          : estimate.predictedCombinedPracticeScore
      ).toFixed(1) +
      ' <small>/9.0</small></strong></div></div>' +
      '<div class="ts-esat-estimate__grid">' + cards + '</div>' +
      '<div class="ts-esat-estimate__raw">Total raw mark: <strong>' +
      Number(estimate.rawTotal) + '/81</strong></div>' +
      '<p class="ts-esat-estimate__note">' + escapeHtml(estimate.note) + '</p>' +
      '</section>'
    );
  }

  async function fetchEstimate(options) {
    var opts = options || {};
    var response = await fetch("/api/esat/score-estimate", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        test_id: String(opts.testId || ""),
        raw_scores: Array.isArray(opts.rawScores) ? opts.rawScores : []
      })
    });
    var payload = {};
    try { payload = await response.json(); } catch (_) {}
    if (!response.ok || payload.ok !== true) {
      throw new Error(payload.error || "Score estimate unavailable.");
    }
    return payload.estimate;
  }

  async function fetchAndRender(options) {
    try {
      return render(await fetchEstimate(options));
    } catch (error) {
      console.error("ESAT score estimate failed:", error);
      return unavailable("The ESAT estimate could not be loaded. Your raw marks are shown below.");
    }
  }

  root.TS_ESAT_SCORE_ESTIMATES = Object.freeze({
    fetch: fetchEstimate,
    render: render,
    fetchAndRender: fetchAndRender,
    unavailable: unavailable
  });
})(window);
