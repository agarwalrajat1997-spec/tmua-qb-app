import fs from "node:fs";
import path from "node:path";
import assert from "node:assert/strict";

const root = process.cwd();

const banks = [
  ["TMUA", path.join(root, "public", "tmua-question-bank", "index.html")],
  ["ESAT", path.join(root, "public", "esat-question-bank", "index.html")],
];

function findMatchingBrace(text, openBraceIndex, label) {
  let depth = 0;
  let quote = null;
  let escaped = false;
  let lineComment = false;
  let blockComment = false;

  for (let i = openBraceIndex; i < text.length; i++) {
    const ch = text[i];
    const next = text[i + 1] || "";

    if (lineComment) {
      if (ch === "\n") lineComment = false;
      continue;
    }

    if (blockComment) {
      if (ch === "*" && next === "/") {
        blockComment = false;
        i++;
      }
      continue;
    }

    if (quote) {
      if (escaped) {
        escaped = false;
        continue;
      }
      if (ch === "\\") {
        escaped = true;
        continue;
      }
      if (ch === quote) quote = null;
      continue;
    }

    if (ch === "/" && next === "/") {
      lineComment = true;
      i++;
      continue;
    }

    if (ch === "/" && next === "*") {
      blockComment = true;
      i++;
      continue;
    }

    if (ch === '"' || ch === "'" || ch === "`") {
      quote = ch;
      continue;
    }

    if (ch === "{") depth++;
    if (ch === "}") {
      depth--;
      if (depth === 0) return i;
    }
  }

  throw new Error(label + ": closing brace not found");
}

function functionText(text, needle, label) {
  const start = text.indexOf(needle);
  assert.ok(start >= 0, label + ": start missing");

  const open = text.indexOf("{", start + needle.length - 1);
  assert.ok(open >= 0, label + ": opening brace missing");

  const close = findMatchingBrace(text, open, label);
  return text.slice(start, close + 1);
}

function scriptText(html, id, label) {
  const open = `<script id="${id}">`;
  const start = html.indexOf(open);
  assert.ok(start >= 0, label + ": script missing");

  const contentStart = start + open.length;
  const end = html.indexOf("</script>", contentStart);
  assert.ok(end > contentStart, label + ": script closing tag missing");

  return html.slice(contentStart, end);
}

for (const [name, filename] of banks) {
  const html = fs.readFileSync(filename, "utf8");
  const progress = scriptText(
    html,
    "ts-per-question-progress-sync-v1",
    name,
  );

  const apply = functionText(
    progress,
    "function applyReattemptMode()",
    name + " applyReattemptMode",
  );

  const visit = functionText(
    progress,
    "function updateVisitQuestion()",
    name + " updateVisitQuestion",
  );

  const renderOptions = functionText(
    html,
    "function renderOptions(meta, q)",
    name + " renderOptions",
  );

  const setSelected = functionText(
    html,
    "setSelected: function(label)",
    name + " setSelected",
  );

  assert.ok(
    progress.includes("TS_QB_REATTEMPT_SELECTION_STABILITY_V3"),
    name + ": stability marker missing",
  );

  assert.ok(
    progress.includes('var reattemptPreparedQuestionId = "";'),
    name + ": per-visit state missing",
  );

  assert.ok(
    visit.includes('reattemptPreparedQuestionId = "";'),
    name + ": navigation does not reset per-visit state",
  );

  assert.ok(
    apply.includes('if (status !== "wrong") return;'),
    name + ": historical cleanup is not wrong-only",
  );

  const visitGuard = apply.indexOf(
    "if (reattemptPreparedQuestionId === qid) return;",
  );
  const radioClear = apply.indexOf("el.checked = false;");

  assert.ok(visitGuard >= 0, name + ": one-time visit guard missing");
  assert.ok(radioClear >= 0, name + ": initial old-answer clear missing");
  assert.ok(
    visitGuard < radioClear,
    name + ": periodic sync can still erase the new selected answer",
  );

  assert.ok(
    apply.includes("reattemptPreparedQuestionId = qid;"),
    name + ": prepared visit is not recorded",
  );

  assert.ok(
    /const locked\s*=\s*a\.checked\s*&&\s*a\.isCorrect\s*===\s*true\s*\?\s*"disabled"\s*:\s*""\s*;/.test(
      renderOptions,
    ),
    name + ": only-correct freeze rule missing",
  );

  assert.ok(
    setSelected.includes(
      "state.answers[key].checked && state.answers[key].isCorrect === true",
    ),
    name + ": correct question is not frozen",
  );

  assert.ok(
    setSelected.includes(
      "state.answers[key].checked && state.answers[key].isCorrect === false",
    ),
    name + ": incorrect question is not reopened",
  );

  assert.ok(
    setSelected.includes("state.answers[key].selected = label;"),
    name + ": current working selection is not stored",
  );
}

function select(answer, label) {
  if (answer.checked && answer.isCorrect === true) return answer;

  let next = { ...answer };

  if (next.checked && next.isCorrect === false) {
    next = {
      ...next,
      checked: false,
      locked: false,
      isCorrect: false,
    };
  }

  next.selected = label;
  return next;
}

function submit(answer, correctLabel) {
  assert.ok(answer.selected);
  const correct = answer.selected === correctLabel;

  return {
    ...answer,
    checked: true,
    locked: correct,
    isCorrect: correct,
    answer: correctLabel,
  };
}

// Scenario A â€” new question
let a = select({}, "B");
assert.equal(a.selected, "B");
a = submit(a, "B");
assert.equal(a.isCorrect, true);

// Scenario B â€” previously correct
const correct = {
  selected: "B",
  checked: true,
  locked: true,
  isCorrect: true,
};
assert.deepEqual(select(correct, "C"), correct);

// Scenario C â€” previously incorrect
let wrong = {
  selected: "A",
  checked: true,
  locked: false,
  isCorrect: false,
};
wrong = select(wrong, "C");
assert.equal(wrong.selected, "C");
assert.equal(wrong.checked, false);
wrong = select(wrong, "D");
assert.equal(wrong.selected, "D");
wrong = submit(wrong, "B");
assert.equal(wrong.isCorrect, false);

// Scenario D â€” wrong becomes correct
let retry = {
  selected: "A",
  checked: true,
  locked: false,
  isCorrect: false,
};
retry = select(retry, "B");
retry = submit(retry, "B");
assert.equal(retry.isCorrect, true);
assert.equal(retry.locked, true);
assert.equal(select(retry, "C").selected, "B");

// Periodic-sync regression
let preparedQuestionId = "";
let visibleSelection = "A";

function prepareHistoricalWrong(qid) {
  if (preparedQuestionId === qid) return;
  visibleSelection = null;
  preparedQuestionId = qid;
}

prepareHistoricalWrong("50");
assert.equal(visibleSelection, null);

visibleSelection = "C";
prepareHistoricalWrong("50");
assert.equal(
  visibleSelection,
  "C",
  "periodic sync erased the new re-attempt selection",
);

visibleSelection = "D";
prepareHistoricalWrong("50");
assert.equal(
  visibleSelection,
  "D",
  "periodic sync erased the changed re-attempt selection",
);

preparedQuestionId = "";
visibleSelection = "D";
prepareHistoricalWrong("50");
assert.equal(
  visibleSelection,
  null,
  "a later revisit did not reopen the incorrect question cleanly",
);

console.log(
  "PASS: TMUA + ESAT re-attempt selection regression suite.",
);