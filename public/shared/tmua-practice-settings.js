(function (root) {
  "use strict";
  function create(testId, sectionSizes) {
    var options = root.TS_TEST_OPTIONS.create({ testId: testId, sectionSizes: sectionSizes, baseSeconds: 4500, programme: "TMUA" });
    root.TS_TMUA_ACTIVE_OPTIONS = options;
    return options;
  }
  function mount(options, anchor) {
    var host = document.createElement("div");
    host.id = "tmua-practice-settings";
    anchor.parentNode.insertBefore(host, anchor);
    options.mount(host);
    function timing() {
      document.querySelectorAll('[data-tmua-duration]').forEach(function (element) {
        element.textContent = root.TS_TEST_OPTIONS.humanTime(options.durationSeconds() * (element.getAttribute('data-tmua-duration') === 'total' ? 2 : 1));
      });
    }
    host.addEventListener('change', timing);
    timing();
  }
  function questionLabel(options, index) {
    var original = index % 20 + 1;
    return options.metadata().order === "randomised"
      ? "Original Q" + original + " (shown as Q" + (options.positionOf(index) + 1) + ")"
      : "Q" + original;
  }
  function decorate(options, container, index, paperNumber) {
    var heading = container.querySelector(".question-number");
    if (!heading) return;
    heading.textContent = "Question " + (options.positionOf(index) + 1);
    if (options.metadata().order === "randomised") {
      var reference = document.createElement("small");
      reference.style.cssText = "display:block;margin-top:6px;font:400 12px/1.5 Arial,sans-serif;color:#657583";
      reference.textContent = "Original Paper " + paperNumber + ", Question " + (index % 20 + 1);
      heading.appendChild(reference);
    }
  }
  function resultNote(options, host) {
    if (!host) return;
    var previous = host.querySelector(".tmua-practice-result-note");
    if (previous) previous.remove();
    var note = document.createElement("p");
    note.className = "tmua-practice-result-note";
    note.style.cssText = "font:14px/1.6 Arial,sans-serif;color:#334155;padding:14px;border:1px solid #cbd5e1;border-radius:10px;background:#f8fafc";
    note.textContent = options.summary() + ". " + options.scoreNote();
    host.insertBefore(note, host.firstChild);
  }
  root.TS_TMUA_PRACTICE = { create: create, mount: mount, decorate: decorate, questionLabel: questionLabel, resultNote: resultNote };
})(window);
