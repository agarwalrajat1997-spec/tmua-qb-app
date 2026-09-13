(function (root) {
  "use strict";

  const VERSION = "20260806-1";

  const OFFICIAL = {
    "official-2016": [
      1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.6,2.1,2.6,
      3.0,3.4,3.8,4.2,4.5,4.8,5.2,5.5,5.8,6.1,
      6.4,6.7,7.1,7.4,7.7,8.0,8.3,8.7,9.0,9.0,
      9.0,9.0,9.0,9.0,9.0,9.0,9.0,9.0,9.0,9.0,9.0
    ],
    "official-2017": [
      1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.5,1.9,
      2.2,2.6,3.0,3.3,3.6,3.9,4.2,4.5,4.8,5.1,
      5.4,5.6,5.9,6.2,6.5,6.8,7.1,7.4,7.7,8.0,
      8.4,8.8,9.0,9.0,9.0,9.0,9.0,9.0,9.0,9.0,9.0
    ],
    "official-2018": [
      1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.5,1.9,
      2.3,2.6,3.0,3.3,3.6,3.9,4.2,4.5,4.8,5.1,
      5.4,5.6,5.9,6.2,6.5,6.8,7.1,7.4,7.7,8.0,
      8.4,8.8,9.0,9.0,9.0,9.0,9.0,9.0,9.0,9.0,9.0
    ],
    "official-2019": [
      1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.1,1.5,1.9,
      2.3,2.6,3.0,3.3,3.6,3.9,4.2,4.5,4.8,5.1,
      5.4,5.7,5.9,6.2,6.5,6.6,6.7,6.8,7.0,7.1,
      7.2,7.4,7.5,7.7,7.9,8.1,8.3,8.6,9.0,9.0,9.0
    ],
    "official-2020": [
      1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.4,1.8,
      2.2,2.6,2.9,3.3,3.6,3.9,4.2,4.5,4.8,5.1,
      5.3,5.6,5.9,6.2,6.5,6.6,6.7,6.8,7.0,7.1,
      7.2,7.4,7.5,7.7,7.8,8.1,8.3,8.6,9.0,9.0,9.0
    ],
    "official-2021": [
      1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.1,1.5,1.9,
      2.3,2.6,3.0,3.3,3.6,3.9,4.2,4.5,4.8,5.1,
      5.4,5.6,5.9,6.2,6.5,6.6,6.7,6.8,7.0,7.1,
      7.2,7.4,7.5,7.7,7.9,8.1,8.3,8.6,9.0,9.0,9.0
    ],
    "official-2022": [
      1.0,1.0,1.0,1.0,1.0,1.0,1.2,1.6,2.1,2.5,
      2.9,3.2,3.6,3.9,4.2,4.5,4.8,5.1,5.4,5.7,
      5.9,6.2,6.5,6.6,6.7,6.8,6.9,7.0,7.1,7.2,
      7.4,7.5,7.6,7.8,8.0,8.1,8.4,8.6,9.0,9.0,9.0
    ],
    "official-2023": [
      1.0,1.0,1.0,1.0,1.0,1.0,1.5,1.9,2.4,2.8,
      3.2,3.5,3.9,4.2,4.5,4.8,5.1,5.4,5.7,6.0,
      6.2,6.5,6.6,6.7,6.8,6.9,7.0,7.1,7.2,7.3,
      7.4,7.6,7.7,7.8,8.0,8.2,8.4,8.6,9.0,9.0,9.0
    ]
  };

  const ANCHORS = {
    mock1: [
      [0,1.0],[5,1.0],[7,1.5],[9,2.2],[11,3.0],[12,3.6],
      [14,4.2],[15,4.5],[17,5.0],[19,5.5],[21,6.0],
      [24,6.5],[26,7.0],[29,7.5],[31,8.0],[34,8.5],
      [36,9.0],[40,9.0]
    ],
    mock2: [
      [0,1.0],[7,1.0],[9,1.5],[11,2.2],[13,2.8],[15,3.5],
      [17,4.1],[18,4.5],[20,5.0],[23,5.5],[25,6.0],
      [27,6.5],[30,7.0],[32,7.5],[34,8.0],[37,8.5],
      [39,9.0],[40,9.0]
    ],
    "informed2024-2025": [
      [0,1.0],[4,1.0],[6,1.5],[8,2.3],[9,3.0],[10,3.7],
      [12,4.5],[13,5.0],[15,5.5],[18,6.0],[20,6.5],
      [23,7.0],[26,7.5],[29,8.0],[32,8.5],[34,9.0],
      [40,9.0]
    ]
  };

  const META = {
    "official-2016": { kind: "official", year: "2016" },
    "official-2017": { kind: "official", year: "2017" },
    "official-2018": { kind: "official", year: "2018" },
    "official-2019": { kind: "official", year: "2019" },
    "official-2020": { kind: "official", year: "2020" },
    "official-2021": { kind: "official", year: "2021" },
    "official-2022": { kind: "official", year: "2022" },
    "official-2023": { kind: "official", year: "2023" },
    "specimen-estimate": { kind: "specimen", year: "Specimen" },
    mock1: { kind: "mock", year: "Thriving Scholars Mock 1" },
    mock2: { kind: "mock", year: "Thriving Scholars Mock 2" },
    "informed2024-2025": { kind: "mock", year: "2024-2025 Informed Test" }
  };

  function roundedRaw(raw) {
    const number = Number(raw);
    if (!Number.isFinite(number)) return 0;
    return Math.max(0, Math.min(40, Math.round(number)));
  }

  function round1(value) {
    return Math.round((Number(value) + Number.EPSILON) * 10) / 10;
  }

  function interpolate(anchors, raw) {
    const x = roundedRaw(raw);

    for (let index = 0; index < anchors.length - 1; index += 1) {
      const left = anchors[index];
      const right = anchors[index + 1];

      if (x < left[0] || x > right[0]) continue;
      if (right[0] === left[0]) return round1(right[1]);

      const fraction = (x - left[0]) / (right[0] - left[0]);
      return round1(left[1] + fraction * (right[1] - left[1]));
    }

    return round1(anchors[anchors.length - 1][1]);
  }

  function convert(profile, raw) {
    const x = roundedRaw(raw);

    if (Object.prototype.hasOwnProperty.call(OFFICIAL, profile)) {
      return round1(OFFICIAL[profile][x]);
    }

    if (profile === "specimen-estimate") {
      return round1(OFFICIAL["official-2018"][x]);
    }

    if (Object.prototype.hasOwnProperty.call(ANCHORS, profile)) {
      return interpolate(ANCHORS[profile], x);
    }

    throw new Error(`Unknown TMUA score profile: ${profile}`);
  }

  function note(profile) {
    const meta = META[profile];
    if (!meta) return "";

    if (meta.kind === "official") {
      return (
        `Official historical ${meta.year} overall conversion. ` +
        "Paper 1 and Paper 2 correct answers are added to give one raw " +
        "score out of 40 before applying the published table."
      );
    }

    if (meta.kind === "specimen") {
      return (
        "The early specimen paper has no official published conversion; " +
        "this estimated score uses the 2017-2018 overall conversion tables."
      );
    }

    return (
      "Independent estimated TMUA score. The official test uses statistical " +
      "equating, so the conversion may vary between sittings."
    );
  }

  function heading(profile) {
    const meta = META[profile];
    return meta && meta.kind === "official"
      ? "Official historical TMUA score"
      : "Estimated TMUA score";
  }

  function render(profile, overallRaw, p1Raw, p2Raw) {
    const raw = roundedRaw(overallRaw);
    const p1 = Number.isFinite(Number(p1Raw)) ? Math.max(0, Math.round(Number(p1Raw))) : null;
    const p2 = Number.isFinite(Number(p2Raw)) ? Math.max(0, Math.round(Number(p2Raw))) : null;
    const score = convert(profile, raw);
    const paperCards = p1 != null && p2 != null
      ? (
          '<div class="ts-score9-card"><h4>Paper 1 raw mark</h4>' +
          `<div class="ts-score9-big">${p1}/20</div>` +
          '<div class="ts-score9-small">Raw mark only</div></div>' +
          '<div class="ts-score9-card"><h4>Paper 2 raw mark</h4>' +
          `<div class="ts-score9-big">${p2}/20</div>` +
          '<div class="ts-score9-small">Raw mark only</div></div>'
        )
      : "";

    return (
      `<div class="ts-score9-wrap" data-ts-score-profile="${profile}">` +
      '<div class="ts-score9-row"><div>' +
      `<div class="ts-score9-title">${heading(profile)}</div>` +
      '<div class="ts-score9-sub">One combined score from the total raw mark out of 40.</div>' +
      '</div>' +
      `<div class="ts-score9-chip">${score.toFixed(1)} / 9.0</div></div>` +
      '<div class="ts-score9-grid">' +
      '<div class="ts-score9-card"><h4>Combined raw score</h4>' +
      `<div class="ts-score9-big">${raw}/40</div>` +
      '<div class="ts-score9-small">Paper 1 + Paper 2</div></div>' +
      paperCards +
      '</div>' +
      `<div class="ts-score9-note"><strong>Scoring note:</strong> ${note(profile)}</div>` +
      '</div>'
    );
  }

  const api = Object.freeze({
    version: VERSION,
    officialTables: OFFICIAL,
    anchors: ANCHORS,
    meta: META,
    convert,
    interpolate,
    note,
    render
  });

  root.TS_TMUA_SCORE_CONVERSIONS = api;

  if (!root.document) return;

  const profile = String(root.TS_TMUA_SCORE_PROFILE || "").trim();
  if (!META[profile]) {
    console.error("[TMUA scoring] Missing or invalid score profile.", profile);
    return;
  }

  function scoreFromAnyTotal(raw, totalQuestions) {
    const total = Number(totalQuestions);
    const value = Number(raw);
    if (!Number.isFinite(value)) return convert(profile, 0);
    if (!Number.isFinite(total) || total <= 0 || total === 40) {
      return convert(profile, value);
    }
    return convert(profile, (value / total) * 40);
  }

  root.TS_TMUA_SCORE9 = function (rawCorrect, totalQuestions) {
    return scoreFromAnyTotal(rawCorrect, totalQuestions);
  };

  root.TS_TMUA_SCORE9_BLOCK = function (opts) {
    const options = opts || {};
    const overall = Number.isFinite(Number(options.overallRaw))
      ? Number(options.overallRaw)
      : Number(options.p1Raw || 0) + Number(options.p2Raw || 0);

    return render(
      profile,
      overall,
      options.p1Raw,
      options.p2Raw
    );
  };

  root.estimatedTmuaScore = function (raw) {
    return convert(profile, raw);
  };

  root.score9Block = function (total, p1, p2) {
    return render(profile, total, p1, p2);
  };

  function paperScores(payload) {
    const answers = Array.isArray(payload.answers) ? payload.answers : [];
    const correct = Array.isArray(payload.correct_answers)
      ? payload.correct_answers
      : [];

    if (answers.length < 40 || correct.length < 40) {
      return { p1: null, p2: null };
    }

    let p1 = 0;
    let p2 = 0;

    for (let index = 0; index < 40; index += 1) {
      if (answers[index] !== correct[index]) continue;
      if (index < 20) p1 += 1;
      else p2 += 1;
    }

    return { p1, p2 };
  }

  function resultHost() {
    const selectors = [
      ".result-title",
      ".result-wrap",
      "#results-screen",
      "#result-screen",
      "#results-page",
      "#score-screen",
      ".results-screen",
      ".result-screen",
      ".results-page",
      ".submission-results"
    ];

    for (const selector of selectors) {
      const element = root.document.querySelector(selector);
      if (element) return element;
    }

    return null;
  }

  function renderIntoResults(result) {
    if (!result) return;
    const host = resultHost();
    if (!host) return;

    const existing = root.document.querySelectorAll(".ts-score9-wrap");
    existing.forEach((element) => element.remove());

    const shell = root.document.createElement("div");
    shell.innerHTML = render(
      profile,
      result.raw,
      result.p1,
      result.p2
    );

    const block = shell.firstElementChild;
    if (!block) return;

    if (host.classList && host.classList.contains("result-title")) {
      host.appendChild(block);
    } else {
      host.insertBefore(block, host.firstChild);
    }
  }

  if (typeof root.fetch === "function" && !root.__TS_TMUA_SCORE_FETCH_V1__) {
    root.__TS_TMUA_SCORE_FETCH_V1__ = true;
    const nativeFetch = root.fetch.bind(root);

    root.fetch = async function (input, init) {
      let nextInit = init;

      try {
        const url = typeof input === "string"
          ? input
          : String(input && input.url ? input.url : "");

        if (
          url.includes("/api/practice-tests/submit") &&
          init &&
          typeof init.body === "string"
        ) {
          const payload = JSON.parse(init.body);
          const raw = roundedRaw(payload.score);
          const converted = convert(profile, raw);
          const papers = paperScores(payload);

          payload.estimated_tmua_score = converted;
          payload.tmua_score9 = converted;
          payload.score_conversion_profile = profile;
          payload.score_conversion_version = VERSION;
          payload.score_conversion_kind = META[profile].kind;

          nextInit = Object.assign({}, init, {
            body: JSON.stringify(payload)
          });

          root.__TS_TMUA_LAST_RESULT__ = {
            raw,
            p1: papers.p1,
            p2: papers.p2,
            score: converted
          };

          root.setTimeout(function () {
            renderIntoResults(root.__TS_TMUA_LAST_RESULT__);
          }, 0);
        }
      } catch (error) {
        console.warn("[TMUA scoring] Could not rewrite submission payload.", error);
      }

      return nativeFetch(input, nextInit);
    };
  }
})(typeof window !== "undefined" ? window : globalThis);