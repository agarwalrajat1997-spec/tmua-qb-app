(function (root) {
  "use strict";
  if (root.TS_TEST_OPTIONS) return;

  // Presentation only: canonical question/answer/timing arrays must never be reordered.
  // Sections and positions are zero-based. start() shuffles once and locks choices.
  // restore() validates before replacing state; absent metadata means a legacy 1x sitting.
  var instanceCount = 0;
  var multipliers = [1, 1.25, 1.5];

  function humanTime(seconds) {
    return Math.floor(seconds / 60) + " minutes" + (seconds % 60 ? " " + seconds % 60 + " seconds" : "");
  }

  function deduction(count, multiplier) {
    var base = multiplier === 1.25 ? 3 : multiplier === 1.5 ? 5 : 0;
    return Math.round(count * base / 40);
  }

  function adjustedRaw(raw, count, multiplier) {
    return Math.max(0, Math.min(count, Number(raw) || 0) - deduction(count, multiplier));
  }

  function scoreNote(multiplier, programme, sizes) {
    if (multiplier === 1) return "Original raw marks are retained. Shuffling does not affect marking or the score conversion.";
    sizes = sizes || (programme === "ESAT" ? [27, 27, 27] : [20, 20]);
    var count = programme === "ESAT" ? sizes[0] : sizes.reduce(function (a, b) { return a + b; }, 0);
    var unit = programme === "ESAT" ? "each " + count + "-question module" : "this " + count + "-question test";
    return "With +" + Math.round((multiplier - 1) * 100) + "% time, your actual raw mark stays unchanged. " +
      "For the estimated standard-time equivalent, we deduct " + deduction(count, multiplier) +
      " marks from " + unit + " (minimum zero), then use the existing score conversion. " +
      "This can lower the practice prediction linked to this attempt. It is a provisional, unvalidated practice estimate—not an official " +
      (programme === "ESAT" ? "ESAT" : "TMUA") + " adjustment or a measure of entitlement to access arrangements.";
  }

  function summary(settings, programme) {
    var unit = programme === "ESAT" ? "module" : "paper";
    return (settings.order === "randomised" ? "Jumbled questions" : "Original question order") + " · " +
      (settings.time_multiplier === 1 ? "Standard time" : "+" + Math.round((settings.time_multiplier - 1) * 100) + "% time") +
      " · " + humanTime(Math.round(settings.base_seconds_per_section * settings.time_multiplier)) + " per " + unit;
  }

  function copy(settings) {
    return {
      version: 1, order: settings.order, time_multiplier: settings.time_multiplier,
      question_order: settings.question_order.slice(), section_sizes: settings.section_sizes.slice(),
      base_seconds_per_section: settings.base_seconds_per_section
    };
  }

  function shuffled(values) {
    var result = values.slice();
    for (var i = result.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var previous = result[i]; result[i] = result[j]; result[j] = previous;
    }
    return result;
  }

  function installStyle(doc) {
    if (doc.getElementById("ts-test-options-style")) return;
    var style = doc.createElement("style");
    style.id = "ts-test-options-style";
    style.textContent = ".ts-test-settings{box-sizing:border-box;margin:20px 0;padding:20px;border:1px solid #dfc8b6;border-radius:16px;background:#fffbf4;color:#352b29;font:15px/1.5 Arial,sans-serif;text-align:left}.ts-test-settings *{box-sizing:border-box}.ts-test-settings h3{margin:2px 0 4px;color:#681b20;font-size:20px}.ts-test-settings p{margin:6px 0 14px}.ts-test-settings .ts-test-eyebrow{font-size:11px;letter-spacing:.12em;font-weight:800;color:#7c2429}.ts-test-settings-grid{display:grid;grid-template-columns:1fr 1.4fr;gap:18px}.ts-test-settings fieldset{min-width:0;border:0;margin:0;padding:0}.ts-test-settings legend{padding:0;margin-bottom:8px;font-weight:700}.ts-test-choices{display:flex;flex-wrap:wrap;gap:8px}.ts-test-choice{display:flex!important;flex:1 1 105px;align-items:flex-start;gap:8px;padding:11px!important;border:1px solid #dfd4c9;border-radius:10px;background:#fff;cursor:pointer;line-height:1.35}.ts-test-choice:has(input:checked){background:#fff0c4;border-color:#86282e;box-shadow:0 0 0 1px #86282e}.ts-test-choice input[type=radio]{appearance:auto;width:16px!important;min-width:16px;height:16px!important;margin:2px 0 0!important;padding:0;accent-color:#86282e}.ts-test-choice:focus-within{outline:3px solid #e8a438;outline-offset:2px}.ts-test-choice strong{display:block;font-size:14px}.ts-test-choice small{display:block;margin-top:4px;font-size:12px;color:#655b56}.ts-test-settings .ts-test-score-note{margin:15px 0 0;padding:12px;border-left:3px solid #e6a129;border-radius:0 8px 8px 0;background:#fff4db;font-size:13px;line-height:1.55}.ts-test-settings .ts-test-settings-locked{margin:10px 0 0;color:#685d55;font-size:12px}.ts-test-choice:has(input:disabled){cursor:default}@media(max-width:680px){.ts-test-settings{padding:15px}.ts-test-settings-grid{grid-template-columns:1fr}.ts-test-choice{flex-basis:90px}}";
    doc.head.appendChild(style);
  }

  function create(config) {
    config = config || {};
    var sizes = config.sectionSizes && config.sectionSizes.slice();
    if (!sizes || !sizes.length || sizes.some(function (n) { return !Number.isInteger(n) || n <= 0; }) ||
        !Number.isInteger(config.baseSeconds) || config.baseSeconds <= 0) throw new Error("Invalid test settings configuration.");
    var programme = config.programme === "ESAT" ? "ESAT" : "TMUA";
    var offsets = [], count = 0;
    sizes.forEach(function (n) { offsets.push(count); count += n; });
    var identity = Array.from({ length: count }, function (_, index) { return index; });
    var state = { version: 1, order: "sequential", time_multiplier: 1, question_order: identity.slice(), section_sizes: sizes.slice(), base_seconds_per_section: config.baseSeconds };
    var locked = false, host = null;
    var namespace = "ts-test-options-" + (++instanceCount);

    function validate(value) {
      if (value == null) return { version: 1, order: "sequential", time_multiplier: 1, question_order: identity.slice(), section_sizes: sizes.slice(), base_seconds_per_section: config.baseSeconds };
      if (value.version !== 1 || ["sequential", "randomised"].indexOf(value.order) < 0 || multipliers.indexOf(value.time_multiplier) < 0 ||
          value.base_seconds_per_section !== config.baseSeconds || !Array.isArray(value.section_sizes) ||
          value.section_sizes.length !== sizes.length || sizes.some(function (n, i) { return value.section_sizes[i] !== n; }) ||
          !Array.isArray(value.question_order) || value.question_order.length !== count || new Set(value.question_order).size !== count) {
        throw new Error("The saved test settings are invalid. Start a new attempt instead.");
      }
      sizes.forEach(function (length, section) {
        for (var p = 0; p < length; p++) {
          var position = offsets[section] + p, original = value.question_order[position];
          if (!Number.isInteger(original) || original < offsets[section] || original >= offsets[section] + length ||
              (value.order === "sequential" && original !== position)) throw new Error("Saved questions must remain within their original paper or module.");
        }
      });
      return copy(value);
    }

    function syncHost() {
      if (!host) return;
      host.querySelectorAll("input[data-ts-choice]").forEach(function (input) {
        var key = input.getAttribute("data-ts-choice");
        input.checked = String(state[key]) === input.value;
        input.disabled = locked;
      });
      host.querySelector(".ts-test-score-note").textContent = scoreNote(state.time_multiplier, programme, sizes);
      host.querySelector(".ts-test-settings-locked").textContent = locked ? "Settings are locked for this attempt. Original question references stay with your results and solutions." :
        "Choose before starting. Questions stay within their original paper or module; answer choices keep their original labels.";
    }

    function mount(target) {
      var nextHost = typeof target === "string" ? document.querySelector(target) : target;
      if (!nextHost) throw new Error("The test settings panel could not be found.");
      if (nextHost === host && host.querySelector(".ts-test-settings-grid")) { syncHost(); return; }
      host = nextHost;
      installStyle(host.ownerDocument || document);
      host.classList.add("ts-test-settings");
      var unit = programme === "ESAT" ? "module" : "paper";
      var noteId = namespace + "-note";
      function choice(key, value, title, caption) {
        return '<label class="ts-test-choice"><input type="radio" name="' + namespace + '-' + key + '" data-ts-choice="' + key +
          '" value="' + value + '" aria-describedby="' + noteId + '"><span><strong>' + title + '</strong><small>' + caption + '</small></span></label>';
      }
      host.innerHTML = '<span class="ts-test-eyebrow">YOUR PRACTICE, YOUR WAY</span><h3>Choose your test settings</h3><p>Keep the original order or jumble the questions. Choose the time that suits your practice.</p>' +
        '<div class="ts-test-settings-grid"><fieldset><legend>Question order</legend><div class="ts-test-choices">' +
        choice("order", "sequential", "Original order", "Follow the published sequence.") +
        choice("order", "randomised", "Jumble questions", "A fresh order within each " + unit + ".") +
        '</div></fieldset><fieldset><legend>Time per ' + unit + '</legend><div class="ts-test-choices">' +
        multipliers.map(function (m) { return choice("time_multiplier", m, m === 1 ? "Standard" : "+" + Math.round((m - 1) * 100) + "% time", humanTime(Math.round(config.baseSeconds * m))); }).join("") +
        '</div></fieldset></div><p class="ts-test-score-note" id="' + noteId + '" role="status" aria-live="polite"></p><p class="ts-test-settings-locked"></p>';
      host.addEventListener("change", function (event) {
        if (locked) { syncHost(); return; }
        var input = event.target;
        if (!input || !input.matches("input[data-ts-choice]")) return;
        var key = input.getAttribute("data-ts-choice");
        var value = key === "time_multiplier" ? Number(input.value) : input.value;
        if ((key === "order" && ["sequential", "randomised"].indexOf(value) >= 0) ||
            (key === "time_multiplier" && multipliers.indexOf(value) >= 0)) state[key] = value;
        syncHost();
      });
      syncHost();
    }

    function start() {
      if (!locked) {
        state.question_order = state.order === "randomised" ? sizes.flatMap(function (length, s) { return shuffled(identity.slice(offsets[s], offsets[s] + length)); }) : identity.slice();
        locked = true;
        syncHost();
      }
      return copy(state);
    }

    return {
      mount: mount, start: start,
      restore: function (value) { var verified = validate(value); state = verified; locked = true; syncHost(); return copy(state); },
      metadata: function () { return copy(state); },
      durationSeconds: function () { return Math.round(config.baseSeconds * state.time_multiplier); },
      questionAt: function (section, position) {
        if (!Number.isInteger(section) || section < 0 || section >= sizes.length || !Number.isInteger(position) || position < 0 || position >= sizes[section]) throw new Error("Invalid display question position.");
        return state.question_order[offsets[section] + position];
      },
      positionOf: function (canonical) {
        if (!Number.isInteger(canonical) || canonical < 0 || canonical >= count) throw new Error("Invalid original question reference.");
        var position = state.question_order.indexOf(canonical);
        var section = offsets.findLastIndex(function (offset) { return offset <= position; });
        return position - offsets[section];
      },
      sequence: function () { return state.question_order.slice(); },
      summary: function () { return summary(state, programme); },
      scoreNote: function () { return scoreNote(state.time_multiplier, programme, sizes); },
      adjustedRaw: function (raw, total) { return adjustedRaw(raw, total, state.time_multiplier); },
      deduction: function (total) { return deduction(total, state.time_multiplier); }
    };
  }

  root.TS_TEST_OPTIONS = { create: create, deduction: deduction, adjustedRaw: adjustedRaw, scoreNote: scoreNote, summary: summary, humanTime: humanTime };
})(typeof window !== "undefined" ? window : globalThis);
