(function () {
  "use strict";
  if (window.TS_TMUA_PAST_PAPER) return;

  var LETTERS = "ABCDEFGH";
  var state = null;
  var mounted = false;
  var allowedTests = /^full-(?:official-20(?:1[6-9]|2[0-3])|specimen)$/;
  var durations = { "1": 4500, "1.25": 5625, "1.5": 6750 };

  function selected(name, fallback) {
    var input = document.querySelector('input[name="' + name + '"]:checked');
    return input ? input.value : fallback;
  }

  function humanTime(seconds) {
    var minutes = Math.floor(seconds / 60);
    var remainder = seconds % 60;
    return minutes + " minutes" + (remainder ? " " + remainder + " seconds" : "");
  }

  function choices() {
    var order = selected("ts-past-order", "sequential");
    var multiplier = selected("ts-past-time", "1");
    if ((order !== "sequential" && order !== "randomised") || !durations[multiplier]) {
      throw new Error("Please choose an available question order and time allowance.");
    }
    return { order: order, multiplier: Number(multiplier), seconds: durations[multiplier] };
  }

  function updateTiming() {
    var config = choices();
    document.querySelectorAll("[data-ts-past-duration]").forEach(function (element) {
      var total = element.getAttribute("data-ts-past-duration") === "total";
      element.textContent = humanTime(config.seconds * (total ? 2 : 1));
    });
    document.querySelectorAll("[data-ts-past-timing-description]").forEach(function (element) {
      element.textContent = "You have " + humanTime(config.seconds) + " for each paper. " +
        "An optional 5-minute break separates the papers. Each paper ends when its timer reaches zero.";
    });
  }

  function mount() {
    if (mounted) return;
    var host = document.getElementById("ts-past-paper-settings");
    if (!host) return;
    host.className = "ts-past-settings";
    host.innerHTML = '<div class="ts-past-settings-heading"><span class="ts-past-eyebrow">YOUR PRACTICE, YOUR WAY</span>' +
      '<h3>Choose your test settings</h3><p>Set your question order and time before you begin.</p></div>' +
      '<div class="ts-past-settings-grid">' +
      '<fieldset><legend>Question order</legend><div class="ts-past-choice-grid">' +
      '<label class="ts-past-setting-choice"><input type="radio" name="ts-past-order" value="sequential" checked>' +
      '<span><strong>Original order</strong><small>Follow the published paper.</small></span></label>' +
      '<label class="ts-past-setting-choice"><input type="radio" name="ts-past-order" value="randomised">' +
      '<span><strong>Randomised</strong><small>Shuffle questions and answer choices within each paper.</small></span></label>' +
      '</div></fieldset><fieldset><legend>Time per paper</legend><div class="ts-past-choice-grid ts-past-time-grid">' +
      '<label class="ts-past-setting-choice"><input type="radio" name="ts-past-time" value="1" checked>' +
      '<span><strong>Standard</strong><small>75 minutes</small></span></label>' +
      '<label class="ts-past-setting-choice"><input type="radio" name="ts-past-time" value="1.25">' +
      '<span><strong>+25% time</strong><small>93 minutes 45 seconds</small></span></label>' +
      '<label class="ts-past-setting-choice"><input type="radio" name="ts-past-time" value="1.5">' +
      '<span><strong>+50% time</strong><small>112 minutes 30 seconds</small></span></label>' +
      '</div></fieldset></div><p class="ts-past-settings-note">Your results retain the original question references for the solution booklet.</p>';
    host.addEventListener("change", updateTiming);
    mounted = true;
    updateTiming();
  }

  function shuffle(values) {
    var result = values.slice();
    for (var i = result.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var previous = result[i];
      result[i] = result[j];
      result[j] = previous;
    }
    return result;
  }

  function inspectQuestion(container, originalIndex) {
    var groups = container.querySelectorAll(".options");
    var headings = container.querySelectorAll(".question-number");
    var radios = container.querySelectorAll('input[type="radio"]');
    if (groups.length !== 1 || headings.length !== 1 || radios.length < 4 || radios.length > 8) {
      throw new Error("This question could not be prepared safely. Please reload and try again.");
    }
    var labels = Array.from(groups[0].querySelectorAll("label.option"));
    if (labels.length !== radios.length) throw new Error("The answer choices could not be prepared safely.");
    var seen = new Set();
    labels.forEach(function (label) {
      var inputs = label.querySelectorAll('input[type="radio"]');
      if (inputs.length !== 1 || label.parentElement !== groups[0] ||
          inputs[0].name !== "q" + (originalIndex + 1) ||
          LETTERS.indexOf(inputs[0].value) < 0 || inputs[0].value.length !== 1 || seen.has(inputs[0].value)) {
        throw new Error("The answer choices could not be prepared safely.");
      }
      seen.add(inputs[0].value);
    });
    if (Array.from(seen).sort().join("") !== LETTERS.slice(0, labels.length)) {
      throw new Error("The answer choices could not be prepared safely.");
    }
    return { group: groups[0], heading: headings[0], labels: labels };
  }

  function metadata() {
    if (!state) throw new Error("Choose your test settings before starting.");
    return {
      version: 1,
      order: state.order,
      time_multiplier: state.multiplier,
      seconds_per_paper: state.seconds,
      question_order: state.questionOrder.slice(),
      option_order: state.optionOrder.map(function (row) { return row.slice(); })
    };
  }

  function prepare(questions, options) {
    var testId = options && options.testId;
    if (!allowedTests.test(testId || "")) throw new Error("These settings are available for TMUA past papers only.");
    if (state) {
      if (state.testId !== testId) throw new Error("A different paper has already started.");
      return metadata();
    }
    var config = choices();
    if (!Array.isArray(questions) || questions.length !== 40) throw new Error("The paper could not be prepared safely.");
    // Validate every detached question before committing any randomisation or locking the settings.
    var optionOrder = questions.map(function (html, originalIndex) {
      if (typeof html !== "string") throw new Error("The paper could not be prepared safely.");
      var detached = document.createElement("div");
      detached.innerHTML = html;
      var inspected = inspectQuestion(detached, originalIndex);
      return inspected.labels.map(function (label) { return label.querySelector('input[type="radio"]').value; });
    });
    var questionOrder = Array.from({ length: 40 }, function (_, index) { return index; });
    if (config.order === "randomised") {
      questionOrder = shuffle(questionOrder.slice(0, 20)).concat(shuffle(questionOrder.slice(20)));
      optionOrder = optionOrder.map(function (letters, originalIndex) {
        // This option explicitly references A–D. Keep E last so that its meaning is unchanged.
        if (testId === "full-official-2022" && originalIndex === 23) {
          if (letters.join("") !== "ABCDE") throw new Error("This question's answer choices have changed. Please reload.");
          return shuffle(letters.slice(0, 4)).concat("E");
        }
        return shuffle(letters);
      });
    }
    state = { testId: testId, order: config.order, multiplier: config.multiplier, seconds: config.seconds,
      questionOrder: questionOrder, optionOrder: optionOrder };
    document.querySelectorAll('#ts-past-paper-settings input').forEach(function (input) { input.disabled = true; });
    return metadata();
  }

  function positionOf(originalIndex) {
    if (!state || !Number.isInteger(originalIndex) || originalIndex < 0 || originalIndex > 39) {
      throw new Error("The question reference is unavailable.");
    }
    return state.questionOrder.indexOf(originalIndex) % 20;
  }

  function questionAt(paper, position) {
    if (!state || (paper !== 1 && paper !== 2) || !Number.isInteger(position) || position < 0 || position > 19) {
      throw new Error("The question reference is unavailable.");
    }
    return state.questionOrder[(paper - 1) * 20 + position];
  }

  function decorateQuestion(container, originalIndex) {
    var position = positionOf(originalIndex);
    var inspected = inspectQuestion(container, originalIndex);
    var byValue = new Map(inspected.labels.map(function (label) {
      return [label.querySelector('input[type="radio"]').value, label];
    }));
    var order = state.optionOrder[originalIndex];
    // All verification happens before moving any live nodes. Input values and listeners remain canonical.
    if (order.length !== byValue.size || order.some(function (letter) { return !byValue.has(letter); })) {
      throw new Error("The answer choices could not be displayed safely.");
    }
    order.forEach(function (letter, index) {
      var label = byValue.get(letter);
      var input = label.querySelector('input[type="radio"]');
      var badge = label.querySelector(".ts-past-choice-letter");
      if (!badge) {
        badge = document.createElement("span");
        badge.className = "ts-past-choice-letter";
        input.insertAdjacentElement("afterend", badge);
      }
      badge.textContent = LETTERS[index];
      inspected.group.appendChild(label);
    });
    inspected.heading.textContent = "Question " + (position + 1);
    if (state.order === "randomised") {
      var reference = document.createElement("small");
      reference.className = "ts-past-original-reference";
      reference.textContent = "Original Paper " + (originalIndex < 20 ? 1 : 2) + ", Question " + (originalIndex % 20 + 1);
      inspected.heading.appendChild(reference);
    }
  }

  function formatQuestion(originalIndex) {
    var original = originalIndex % 20 + 1;
    return state && state.order === "randomised"
      ? "Original Q" + original + " (shown as Q" + (positionOf(originalIndex) + 1) + ")"
      : "Q" + original;
  }

  function formatAnswer(originalIndex, canonicalLetter) {
    if (!state || state.order !== "randomised" || typeof canonicalLetter !== "string") return canonicalLetter;
    var order = state.optionOrder[originalIndex];
    var displayed = order ? order.indexOf(canonicalLetter) : -1;
    return displayed < 0 ? canonicalLetter : canonicalLetter + " (shown as " + LETTERS[displayed] + ")";
  }

  function summary() {
    var config = state || choices();
    return (config.order === "randomised" ? "Randomised questions and choices" : "Original question order") +
      " · " + humanTime(config.seconds) + " per paper";
  }

  window.TS_TMUA_PAST_PAPER = {
    prepare: prepare,
    questionAt: questionAt,
    positionOf: positionOf,
    decorateQuestion: decorateQuestion,
    metadata: metadata,
    durationSeconds: function () { return state ? state.seconds : choices().seconds; },
    formatQuestion: formatQuestion,
    formatAnswer: formatAnswer,
    summary: summary
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount, { once: true });
  else mount();
})();
