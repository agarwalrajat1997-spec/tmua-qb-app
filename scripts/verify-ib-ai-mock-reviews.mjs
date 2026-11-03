import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { lstatSync, readFileSync, readdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

export const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
export const CONTENT = 'content/ib/ai-mocks-2026';
export const DOCS = 'docs/ib-ai-mocks-2026';
export const MANIFEST = `${CONTENT}/review-manifest.json`;
export const EXPECTED = new Map('ABCD'.split('').flatMap(set =>
  (set < 'C' ? ['1', '2', '3'] : ['1', '2']).map(paper =>
    [`ai-hl-set-${set.toLowerCase()}-paper-${paper}`, paper === '1' ? 16 : paper === '2' ? 6 : 2])));
export const sha256 = value => createHash('sha256').update(value).digest('hex');
const read = (root, file) => {
  assert.ok(lstatSync(join(root, file)).isFile(), `${file}: regular file required`);
  return readFileSync(join(root, file));
};
const json = (root, file) => JSON.parse(read(root, file).toString('utf8'));
const sorted = values => [...values].sort();
const sameSet = (values, expected, context) => {
  assert.equal(new Set(values).size, values.length, `${context}: duplicate identity`);
  assert.deepEqual(sorted(values), sorted(expected), `${context}: missing or unexpected identity`);
};
const unique = (records, key, context) => {
  assert.ok(Array.isArray(records) && records.length, `${context}: missing records`);
  const map = new Map();
  for (const record of records) {
    const id = key(record);
    assert.ok(typeof id === 'string' && id.length && !map.has(id), `${context}: duplicate/invalid ${id}`);
    map.set(id, record);
  }
  return map;
};
const passed = (record, context) => assert.equal(record.status, 'passed', `${context}: not passed`);
const noFindings = (value, context) => assert.deepEqual(value, [], `${context}: unresolved findings`);
const has = (object, key) => Object.hasOwn(object, key);
const meaningful = (value, context, min = 20) => {
  assert.ok(typeof value === 'string' && value.trim().length >= min, `${context}: missing substantive explanation`);
  assert.ok(!/^(?:passed|reviewed|verified|checked|all good|ok|done)[.\s!]*$/i.test(value.trim()), `${context}: canned review`);
};
const sortObject = value => Array.isArray(value) ? value.map(sortObject) :
  value && typeof value === 'object' ? Object.fromEntries(Object.keys(value).sort().map(k => [k, sortObject(value[k])])) : value;
export const questionHash = q => sha256(Buffer.from(JSON.stringify(sortObject(q)), 'utf8'));
const idsFor = paper => [...EXPECTED.keys()].filter(id => id.endsWith(`-${paper}`));
const qKey = (id, number) => `${id}:${number}`;
const partKey = (id, number, part) => `${id}:${number}:${part}`;

// Rational strings are emitted by the exact-arithmetic P1 reviewer. No eval.
function scalar(value) {
  if (typeof value === 'number') { assert.ok(Number.isFinite(value), 'Non-finite evidence'); return value; }
  if (typeof value === 'string' && /^[-+]?\d+\s*\/\s*[-+]?\d+$/.test(value)) {
    const [a, b] = value.split('/').map(Number); assert.notEqual(b, 0, 'Zero evidence denominator'); return a / b;
  }
  if (typeof value === 'string' && /^[-+]?(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?$/i.test(value)) {
    const result = Number(value); assert.ok(Number.isFinite(result)); return result;
  }
  return undefined;
}
function numericLeaves(value) {
  const number = scalar(value);
  if (number !== undefined) return 1;
  if (Array.isArray(value)) return value.reduce((n, item) => n + numericLeaves(item), 0);
  if (value && typeof value === 'object') return Object.values(value).reduce((n, item) => n + numericLeaves(item), 0);
  return 0;
}
function booleanResults(value) {
  if (typeof value === 'boolean') return true;
  if (Array.isArray(value)) return value.length > 0 && value.every(booleanResults);
  if (value && typeof value === 'object') {
    const values = Object.values(value); return values.length > 0 && values.every(booleanResults);
  }
  return false;
}
function equivalent(actual, expected, tolerance, context) {
  const a = scalar(actual), b = scalar(expected);
  if (a !== undefined && b !== undefined) {
    assert.ok(Math.abs(a - b) <= tolerance, `${context}: recorded calculation does not meet its tolerance`);
  } else if (Array.isArray(actual) || Array.isArray(expected)) {
    assert.ok(Array.isArray(actual) && Array.isArray(expected) && actual.length > 0, `${context}: empty/mismatched numeric array`);
    assert.equal(actual.length, expected.length, `${context}: array shape`);
    actual.forEach((value, i) => equivalent(value, expected[i], tolerance, context));
  } else if (actual && expected && typeof actual === 'object' && typeof expected === 'object') {
    sameSet(Object.keys(actual), Object.keys(expected), `${context} value fields`);
    assert.ok(Object.keys(actual).length, `${context}: empty numeric object`);
    for (const key of Object.keys(actual)) equivalent(actual[key], expected[key], tolerance, context);
  } else {
    assert.notEqual(actual, null, `${context}: null evidence`);
    assert.notEqual(actual, undefined, `${context}: missing evidence`);
    assert.deepEqual(actual, expected, `${context}: recorded evidence mismatch`);
  }
}

/** Validate a recorded assertion, not merely its passed badge. */
export function validateAssertion(check, context, { allowCalculatedOnly = false } = {}) {
  if (has(check, 'status')) passed(check, context);
  else assert.equal(check.passed, true, `${context}: assertion not passed`);
  meaningful(check.test ?? check.calculation ?? check.check ?? check.name, `${context} description`, 3);
  const field = has(check, 'actual') ? 'actual' : 'calculated';
  assert.ok(has(check, field), `${context}: calculation value missing`);
  const actual = check[field];
  const expectedField = has(check, 'expected') ? 'expected' : has(check, 'reference') ? 'reference' : undefined;
  // An independently enumerated odd-vertex set is valid discrete evidence.
  // It contributes no quantitative leaves, so every question must still have
  // other numeric work. General prose cannot masquerade as a calculation.
  const vertexSet = expectedField && Array.isArray(actual) && actual.length > 0 &&
    actual.every(value => typeof value === 'string' && /^[A-Z][A-Z0-9_]{0,7}$/.test(value));
  assert.ok(numericLeaves(actual) > 0 || booleanResults(actual) || vertexSet, `${context}: empty/nonmathematical value`);
  if (expectedField) {
    const tolerance = check.absoluteTolerance ?? check.tolerance ?? 0;
    assert.ok(typeof tolerance === 'number' && Number.isFinite(tolerance) && tolerance >= 0 && tolerance <= 0.01,
      `${context}: invalid/unreasonably large tolerance`);
    equivalent(actual, check[expectedField], tolerance, context);
  } else assert.ok(allowCalculatedOnly, `${context}: independent assertion lacks expected/reference value`);
  return { assertions: 1, quantitative: numericLeaves(actual) };
}

function checkHashRecords(records, ids, bindings, context) {
  const map = unique(records, r => r.id, context);
  sameSet([...map.keys()], ids, context);
  for (const [id, record] of map) {
    assert.equal(record.sha256, bindings.get(id).canonicalSha256, `${id}: changed since ${context}`);
    if (record.questions !== undefined) assert.equal(record.questions, bindings.get(id).questions);
    if (record.marks !== undefined) assert.equal(record.marks, bindings.get(id).marks);
  }
}
function expectedQuestions(ids, papers) {
  return ids.flatMap(id => papers.get(id).questions.map(q => qKey(id, q.number)));
}
function getQuestion(papers, id, number) {
  const q = papers.get(id)?.questions.find(q => q.number === number);
  assert.ok(q, `Unexpected question ${id}:${number}`); return q;
}
function schemeParts(question) { return new Map(question.markScheme.map(p => [p.part, p])); }

function validateP1(author, independent, papers, bindings) {
  const ids = idsFor('1'), expected = expectedQuestions(ids, papers);
  assert.equal(author.status, 'author verification passed; independent review required');
  passed(independent, 'P1 independent'); noFindings(independent.openFindings, 'P1 independent');
  assert.equal(author.questions, 64); assert.equal(independent.questions, 64); assert.equal(independent.papers, 4);
  assert.equal(independent.parts, ids.reduce((n, id) => n + bindings.get(id).parts, 0));
  assert.equal(independent.marks, 440);
  meaningful(author.method, 'P1 author method'); meaningful(independent.method, 'P1 independent method');
  checkHashRecords(author.papers, ids, bindings, 'P1 author');
  checkHashRecords(Object.entries(independent.paperHashes).map(([id, sha256]) => ({ id, sha256 })), ids, bindings, 'P1 independent');
  let authorCount = 0, independentCount = 0;
  for (const [label, report, key] of [['author', author, r => qKey(r.paper, r.question)], ['independent', independent, r => qKey(r.paperId, r.question)]]) {
    const records = unique(report.records, key, `P1 ${label} questions`); sameSet([...records.keys()], expected, `P1 ${label} coverage`);
    for (const record of records.values()) {
      const id = record.paperId ?? record.paper, q = getQuestion(papers, id, record.question); passed(record, `P1 ${label} ${id}:${q.number}`);
      sameSet(record.syllabusRefs, q.syllabusRefs, `P1 ${label} refs`);
      sameSet(Object.keys(record.partChecks), q.parts.map(p => p.label), `P1 ${label} part coverage`);
      if (label === 'independent') {
        assert.equal(record.stemAndEveryMarkingPointRead, true); assert.equal(record.marks, q.marks);
        assert.equal(record.canonicalQuestionSha256, questionHash(q), `${id}:${q.number}: changed since P1 independent question review`);
        sameSet(Object.keys(record.partMathematicalReview), q.parts.map(p => p.label), 'P1 per-part reasoning coverage');
        meaningful(record.nativeDiagramReview, 'P1 diagram judgment'); meaningful(record.markAllocationReview, 'P1 marking judgment');
      }
      let quantitative = 0;
      for (const part of q.parts) {
        const checks = record.partChecks[part.label]; assert.ok(Array.isArray(checks) && checks.length, 'P1 missing per-part calculations');
        if (label === 'independent') meaningful(record.partMathematicalReview[part.label], 'P1 mathematical reasoning');
        for (const check of checks) {
          const verified = validateAssertion(check, `${id}:${q.number}(${part.label}) ${label}`, { allowCalculatedOnly: label === 'author' });
          quantitative += verified.quantitative;
          if (label === 'author') authorCount++; else independentCount++;
        }
      }
      assert.ok(quantitative > 0, 'P1 question has no quantitative evidence');
    }
  }
  assert.equal(authorCount, author.executableCheckCount); assert.equal(independentCount, independent.independentCheckCount);
  return { authorChecks: authorCount, independentChecks: independentCount };
}

function validateP2(author, independent, papers, bindings) {
  const ids = idsFor('2'); passed(author, 'P2 author'); passed(independent, 'P2 independent');
  noFindings(independent.unresolvedFindings, 'P2 independent'); assert.equal(author.questionCount, 24); assert.equal(independent.questions, 24);
  checkHashRecords(author.papers, ids, bindings, 'P2 author'); checkHashRecords(independent.papers, ids, bindings, 'P2 independent');
  const aMap = unique(author.records, r => qKey(`ai-hl-set-${r.set.toLowerCase()}-paper-2`, r.question), 'P2 author');
  const iMap = unique(independent.questionReviews, r => qKey(`ai-hl-set-${r.id[0].toLowerCase()}-paper-2`, Number(r.id.slice(1))), 'P2 independent');
  const expected = expectedQuestions(ids, papers); sameSet([...aMap.keys()], expected, 'P2 author coverage'); sameSet([...iMap.keys()], expected, 'P2 independent coverage');
  let authorCount = 0, independentCount = 0, parts = 0;
  for (const id of ids) for (const q of papers.get(id).questions) {
    const key = qKey(id, q.number), ar = aMap.get(key), ir = iMap.get(key); passed(ir, key);
    assert.equal(ir.completeStemAndSchemeRead, true); assert.equal(ir.marks, q.marks);
    assert.equal(ir.diagramInspected, Boolean(q.diagramSvg)); meaningful(ir.reasoning, `${key} independent reasoning`);
    sameSet(ar.syllabusRefs, q.syllabusRefs, `${key} author refs`); sameSet(ir.syllabusRefs, q.syllabusRefs, `${key} independent refs`);
    assert.deepEqual(ar.parts, q.parts.map(p => ({ label: p.label, marks: p.marks })), `${key}: author part marks`);
    meaningful(ar.reviewFocus, `${key} author focus`);
    assert.ok(ar.computedEvidence && typeof ar.computedEvidence === 'object' && numericLeaves(ar.computedEvidence) > 0, `${key}: no author numeric data`);
    authorCount += Object.values(ar.computedEvidence).filter(v => typeof v === 'number' && Number.isFinite(v)).length;
    const derivations = unique(ar.partChecks, p => p.part, `${key} author derivations`);
    sameSet([...derivations.keys()], q.parts.map(p => p.label), `${key} author derivation coverage`);
    sameSet(Object.keys(ir.parts), q.parts.map(p => p.label), `${key} independent part coverage`);
    const schemes = schemeParts(q); let quantitative = 0;
    for (const part of q.parts) {
      parts++; const ap = derivations.get(part.label), ip = ir.parts[part.label]; passed(ap, key);
      assert.equal(ap.marks, part.marks); assert.equal(ap.markCodeSum, part.marks);
      meaningful(ap.evidenceKind, `${key} author evidence kind`);
      assert.deepEqual(ap.workedReasoning, schemes.get(part.label).steps.map(s => s.text), `${key} author derivation differs`);
      assert.equal(ip.marks, part.marks); assert.equal(ip.fullPromptAndSchemeRead, true);
      assert.ok(Array.isArray(ip.evidence) && ip.evidence.length, `${key}(${part.label}): empty independent review`);
      for (const evidence of ip.evidence) {
        if (evidence.type === 'executable') {
          const result = validateAssertion(evidence, `${key}(${part.label})`); quantitative += result.quantitative; independentCount++;
        } else {
          assert.equal(evidence.type, 'analytic/contextual review'); assert.equal(evidence.reviewed, true);
          meaningful(evidence.rationale, `${key}(${part.label}) reasoning`, 35);
        }
      }
    }
    assert.ok(quantitative > 0, `${key}: no independent quantitative evidence`);
  }
  assert.equal(parts, independent.parts); assert.equal(authorCount, author.numericEvidenceCount); assert.equal(independentCount, independent.calculationAssertions);
  return { authorChecks: authorCount, independentChecks: independentCount };
}

function validateP3(author, independent, papers, bindings) {
  const ids = idsFor('3');
  assert.equal(author.status, 'author calculations and content checks passed; independent and final visual reviews pending');
  passed(independent, 'P3 independent'); noFindings(author.unresolvedFindings, 'P3 author'); noFindings(independent.openFindings, 'P3 independent');
  assert.equal(author.questions, 4); assert.equal(independent.questionCount, 4); assert.equal(author.parts, 28); assert.equal(independent.partCount, 28);
  checkHashRecords(author.papers, ids, bindings, 'P3 author'); checkHashRecords(independent.papers, ids, bindings, 'P3 independent');
  meaningful(independent.reviewType, 'P3 independent method'); meaningful(independent.scopeReview, 'P3 scope'); meaningful(independent.diagramReview, 'P3 diagrams');
  const qr = unique(author.questionReviews, r => r.id, 'P3 author question reviews'); sameSet([...qr.keys()], ['A1', 'A2', 'B1', 'B2'], 'P3 author question coverage');
  const expected = ids.flatMap(id => papers.get(id).questions.flatMap(q => q.parts.map(p => partKey(id, q.number, p.label))));
  const imap = unique(independent.records, r => partKey(r.paper, r.question, r.part), 'P3 independent parts'); sameSet([...imap.keys()], expected, 'P3 independent coverage');
  const authorParts = new Map(expected.map(key => [key, []])); let authorCount = 0, independentCount = 0;
  assert.ok(Array.isArray(author.checks) && author.checks.length);
  for (const check of author.checks) {
    const id = `ai-hl-set-${check.question[0].toLowerCase()}-paper-3`, number = Number(check.question.slice(1));
    const key = partKey(id, number, check.part); assert.ok(authorParts.has(key), `Unexpected P3 author evidence ${key}`);
    validateAssertion(check, key); authorParts.get(key).push(check); authorCount++;
  }
  for (const [key, checks] of authorParts) assert.ok(checks.length, `${key}: empty P3 author evidence`);
  for (const id of ids) for (const q of papers.get(id).questions) {
    const authored = qr.get(`${papers.get(id).set}${q.number}`); passed(authored, id);
    meaningful(authored.thinking, 'P3 intellectual demand'); meaningful(authored.reasoningVerified, 'P3 author reasoning');
    assert.ok(Array.isArray(authored.boundaryChecks) && authored.boundaryChecks.length >= 3);
    let quantitative = 0;
    for (const part of q.parts) {
      const key = partKey(id, q.number, part.label), record = imap.get(key); passed(record, key);
      assert.ok(Array.isArray(record.checks) && Array.isArray(record.reasoning));
      assert.ok(record.checks.length + record.reasoning.length > 0, `${key}: empty independent part`);
      for (const check of record.checks) { quantitative += validateAssertion(check, key).quantitative; independentCount++; }
      record.reasoning.forEach(reason => meaningful(reason, `${key} reasoning`, 35));
    }
    assert.ok(quantitative > 0, `${id}:${q.number}: no quantitative evidence`);
  }
  assert.equal(authorCount, author.calculationChecks); assert.equal(independentCount, independent.independentCheckCount);
  return { authorChecks: authorCount, independentChecks: independentCount };
}

// Controlled ReportLab/MuPDF output uses visible, uncompressed page dictionaries.
// Reject object-stream/encrypted exports rather than pretending this is a general PDF parser.
export function visiblePdfPageCount(raw) {
  const text = raw.toString('latin1'); assert.equal(text.slice(0, 5), '%PDF-');
  assert.ok(!/\/Type\s*\/ObjStm\b|\/Encrypt\b/.test(text), 'Unsupported PDF object-stream/encrypted export');
  const objects = [...text.matchAll(/\b\d+\s+\d+\s+obj\b([\s\S]*?)endobj/g)];
  const count = objects.filter(m => /\/Type\s*\/Page\b/.test(m[1].split(/\bstream\b/)[0])).length;
  assert.ok(count > 0, 'No visible PDF pages found'); return count;
}

export function readReviewEvidence({ root = ROOT } = {}) {
  const spec = json(root, `${DOCS}/specification.json`); assert.equal(spec.strand, 'ai'); assert.equal(spec.level, 'hl');
  assert.equal(spec.status, 'verified against official current guide');
  assert.equal(spec.syllabus.firstAssessment, 2021); assert.equal(spec.syllabus.lastAssessment, 2028);
  assert.equal(spec.sources.find(s => s.id === 'current-guide')?.url,
    'https://xmltwo.ibo.org/publications/EAD/2026_EN/GR5/GR5-Maths_AI_EN.pdf');
  for (const n of ['1', '2', '3']) {
    assert.equal(spec.paperTypes[n].minutes, n === '3' ? 75 : 120);
    assert.equal(spec.paperTypes[n].marks, n === '3' ? 55 : 110);
    assert.equal(spec.paperTypes[n].calculator, true);
  }
  const validRefs = new Set(Object.values(spec.referenceCatalogue).flatMap(group => Object.keys(group)));
  assert.equal(validRefs.size, 78); meaningful(read(root, `${DOCS}/research.md`).toString('utf8'), 'Research file', 200);
  meaningful(read(root, `${DOCS}/README.md`).toString('utf8'), 'Release README', 200);
  const catalog = json(root, `${CONTENT}/catalog.json`); sameSet(catalog.map(p => p.id), [...EXPECTED.keys()], 'Catalog');
  sameSet(readdirSync(join(root, CONTENT, 'papers')).filter(f => f.endsWith('.json')), [...EXPECTED.keys()].map(id => `${id}.json`), 'Canonical files');
  const papers = new Map(), bindings = new Map();
  const totals = { papers: 10, questions: 0, parts: 0, marks: 0, diagrams: 0, authorChecks: 0, independentChecks: 0, pdfPages: 0, questionPages: 0, solutionPages: 0 };
  for (const meta of catalog) {
    const file = `${CONTENT}/papers/${meta.id}.json`, raw = read(root, file), paper = JSON.parse(raw.toString('utf8'));
    assert.ok(!raw.includes(13), `${file}: canonical LF bytes required`);
    for (const key of ['id', 'strand', 'course', 'set', 'paper', 'minutes', 'marks', 'calculator']) assert.deepEqual(paper[key], meta[key], `${meta.id} catalog ${key}`);
    const normalize = s => s.replace(/[·|—–-]/g, ' ').replace(/\s+/g, ' ').trim(); assert.equal(normalize(paper.title), normalize(meta.title));
    assert.equal(meta.status, 'published'); assert.equal(meta.year, 2026); assert.deepEqual(meta.sections, []);
    const identity = /^ai-hl-set-([a-d])-paper-([1-3])$/.exec(meta.id);
    assert.ok(identity); assert.equal(paper.set, identity[1].toUpperCase()); assert.equal(paper.paper, identity[2]);
    assert.equal(paper.strand, 'ai'); assert.equal(paper.course, 'hl'); assert.equal(paper.calculator, true);
    assert.equal(paper.minutes, paper.paper === '3' ? 75 : 120); assert.equal(paper.marks, paper.paper === '3' ? 55 : 110);
    assert.equal(meta.questionCount, EXPECTED.get(meta.id)); assert.equal(paper.questions.length, meta.questionCount);
    sameSet(paper.questions.map(q => q.number), Array.from({ length: meta.questionCount }, (_, i) => i + 1), `${meta.id} question numbers`);
    assert.equal(paper.questions.reduce((n, q) => n + q.marks, 0), paper.marks);
    if (paper.paper === '3') assert.deepEqual(paper.questions.map(q => q.marks), [27, 28]);
    for (const q of paper.questions) {
      assert.equal(q.section, ''); meaningful(q.stem, `${meta.id}:${q.number} stem`, 10);
      assert.ok(Array.isArray(q.syllabusRefs) && q.syllabusRefs.length); sameSet(q.syllabusRefs, [...new Set(q.syllabusRefs)], 'Unique references');
      q.syllabusRefs.forEach(ref => assert.ok(validRefs.has(ref), `Unknown syllabus reference ${ref}`));
      const schemes = unique(q.markScheme, s => s.part || '(unparted)', `${meta.id}:${q.number} mark groups`);
      sameSet([...schemes.keys()], q.parts.map(p => p.label || '(unparted)'), 'Part/markscheme coverage');
      assert.ok(q.parts.length > 0); assert.equal(q.parts.reduce((n, p) => n + p.marks, 0), q.marks);
      for (const part of q.parts) {
        assert.ok(Number.isInteger(part.marks) && part.marks > 0); meaningful(part.prompt, 'Part prompt', 4);
        const steps = schemes.get(part.label || '(unparted)').steps; assert.ok(steps.length);
        assert.equal(steps.reduce((n, step) => {
          assert.match(step.code, /^[MAR][1-9]\d*$/); meaningful(step.text, 'Worked marking point', 1); return n + Number(step.code.slice(1));
        }, 0), part.marks, `${meta.id}:${q.number}(${part.label}) marking total`);
      }
      if (q.diagramSvg) {
        assert.match(q.diagramSvg, /^<svg\b/); assert.ok(!/<(?:script|foreignObject|image|defs|style)\b|\bon\w+\s*=|(?:href|url)\s*[:=(]/i.test(q.diagramSvg), 'Unsafe scientific SVG');
      }
      totals.parts += q.parts.length;
    }
    papers.set(meta.id, paper); bindings.set(meta.id, { id: meta.id, questionFile: file, canonicalSha256: sha256(raw), questions: paper.questions.length, parts: paper.questions.reduce((n, q) => n + q.parts.length, 0), marks: paper.marks, minutes: paper.minutes, calculator: true });
    totals.questions += paper.questions.length; totals.marks += paper.marks; totals.diagrams += paper.questions.filter(q => q.diagramSvg).length;
  }
  assert.equal(totals.questions, 92); assert.equal(totals.marks, 990);
  const assets = json(root, `${DOCS}/math-assets-checks.json`); passed(assets, 'Scientific render assets');
  sameSet(Object.keys(assets.papers), [...EXPECTED.keys()], 'Scientific render paper coverage');
  const diagrams = new Map(), expressions = new Set();
  for (const [id, paper] of papers) {
    assert.equal(assets.papers[id], bindings.get(id).canonicalSha256, `${id}: stale mathematical render source`);
    for (const q of paper.questions) {
      if (q.diagramSvg) diagrams.set(`${id}-q${q.number}`, q.diagramSvg);
      const texts = [q.stem, ...q.parts.map(p => p.prompt), ...q.markScheme.flatMap(g => g.steps.map(s => s.text))];
      for (const text of texts) for (const m of text.matchAll(/(?<!\\)\$\$([\s\S]*?)(?<!\\)\$\$|(?<!\\)\$([^$\n]+?)(?<!\\)\$/g))
        expressions.add((m[1] ?? m[2]).trim());
    }
  }
  sameSet(Object.keys(assets.diagrams), [...diagrams.keys()], 'Scientific diagram coverage');
  assert.equal(assets.diagramCount, totals.diagrams); assert.equal(assets.mathExpressions, expressions.size);
  meaningful(assets.method, 'Scientific asset verification method');
  for (const [id, svg] of diagrams) {
    assert.equal(assets.diagrams[id].svgSha256, sha256(svg), `${id}: raster was made from different SVG content`);
    // The builder checks the scratch PNG bytes before embedding them. This
    // portable release guard freezes that evidence and the final PDF bytes.
    assert.match(assets.diagrams[id].pngSha256, /^[a-f0-9]{64}$/);
  }
  totals.mathExpressions = expressions.size;
  for (const [n, validate] of [[1, validateP1], [2, validateP2], [3, validateP3]]) {
    const counts = validate(json(root, `${DOCS}/p${n}-author-review.json`), json(root, `${DOCS}/p${n}-independent-review.json`), papers, bindings);
    totals.authorChecks += counts.authorChecks; totals.independentChecks += counts.independentChecks;
  }
  const pdfChecks = json(root, `${DOCS}/pdf-checks.json`), renders = json(root, `${DOCS}/pdf-render-checks.json`);
  passed(pdfChecks, 'PDF build checks'); passed(renders, 'PDF rendering checks');
  const pdfMap = unique(pdfChecks.papers, p => p.id, 'PDF builder records'); sameSet([...pdfMap.keys()], [...EXPECTED.keys()], 'Built PDFs');
  const renderMap = unique(renders.records, p => p.id, 'PDF render records'); sameSet([...renderMap.keys()], [...EXPECTED.keys()], 'Rendered PDFs');
  const visual = new Map();
  for (const n of [1, 2, 3]) {
    const file = `${DOCS}/p${n}-pdf-review.json`, report = json(root, file); passed(report, file);
    const map = unique(report.papers, p => p.id, file); sameSet([...map.keys()], idsFor(String(n)), file);
    for (const [id, review] of map) { passed(review, id); assert.equal(review.allPagesInspected, true); noFindings(review.findings, id); visual.set(id, { ...review, reviewFile: file }); }
  }
  for (const meta of catalog) {
    const id = meta.id, rec = pdfMap.get(id), render = renderMap.get(id), review = visual.get(id), file = `public/ib-mock-solutions/${id}.pdf`, raw = read(root, file), hash = sha256(raw);
    passed(rec, id); assert.equal(rec.sha256, hash, `${id}: builder PDF hash differs`); assert.equal(rec.bytes, raw.length);
    assert.equal(review.sha256, hash, `${id}: PDF changed since visual review`); assert.equal(rec.pages, review.pages);
    assert.equal(rec.pages, visiblePdfPageCount(raw), `${id}: actual page-object count`);
    assert.equal(rec.canonicalQuestionSha256, bindings.get(id).canonicalSha256, `${id}: PDF built from different content`);
    assert.equal(review.canonicalQuestionSha256, bindings.get(id).canonicalSha256, `${id}: PDF visual review content differs`);
    assert.equal(rec.brandingTextCheck, true); assert.equal(rec.sourceAndDiagramAssetHashesVerified, true);
    assert.equal(rec.solutionsStartPage, rec.questionPages + 1);
    assert.equal(rec.bookmarks, 2 * papers.get(id).questions.length + 2);
    assert.equal(rec.pages, rec.questionPages + rec.solutionPages); assert.ok(rec.questionPages >= 2 && rec.solutionPages >= 2);
    assert.equal(meta.pdfUrl, `/ib-mock-solutions/${id}.pdf`);
    sameSet(Object.keys(rec.questionStartPages).map(Number), papers.get(id).questions.map(q => q.number), `${id} question bookmarks`);
    sameSet(Object.keys(rec.solutionStartPages).map(Number), papers.get(id).questions.map(q => q.number), `${id} solution bookmarks`);
    assert.ok(Object.values(rec.questionStartPages).every(p => Number.isInteger(p) && p >= 2 && p <= rec.questionPages));
    assert.ok(Object.values(rec.solutionStartPages).every(p => Number.isInteger(p) && p > rec.solutionsStartPage && p <= rec.pages));
    assert.equal(render.pagesRendered, rec.pages); noFindings(render.outOfPageText, `${id} clipping`);
    if (render.sha256 !== undefined) assert.equal(render.sha256, hash);
    Object.assign(bindings.get(id), { independentReview: `${DOCS}/p${papers.get(id).paper}-independent-review.json`, pdfReview: review.reviewFile, pdfFile: file, pdfSha256: hash, pdfPages: rec.pages, questionPages: rec.questionPages, solutionsStartPage: rec.solutionsStartPage });
    totals.pdfPages += rec.pages; totals.questionPages += rec.questionPages; totals.solutionPages += rec.solutionPages;
  }
  assert.equal(renders.papers, 10); assert.equal(renders.pages, totals.pdfPages);
  const db = json(root, `${DOCS}/database-checks.json`); passed(db, 'Database release evidence');
  for (const key of ['schemaApplied', 'rowLevelSecurityEnabled', 'explicitOwnerPolicies', 'columnRestrictedInsertAndUpdate', 'noAnonymousAccess']) assert.equal(db[key], true, `Database evidence ${key}`);
  assert.equal(db.remainingQaRows, 0); assert.equal(db.savedRowsBeforeVerification, db.savedRowsAfterVerification);
  assert.equal(db.verification.expressionCasesPassed, db.verification.expressionCases);
  assert.ok(db.verification.checks.length >= 10); db.verification.checks.forEach(c => { passed(c, 'Database check'); meaningful(c.test, 'Database check detail'); });
  assert.equal(sha256(read(root, db.migration.file)), db.migration.sha256, 'Database migration changed');
  read(root, db.verification.script);
  return { summary: totals, papers: [...bindings.values()].sort((a, b) => a.id.localeCompare(b.id)) };
}

function filesBelow(root, folder, accept) {
  return readdirSync(join(root, folder), { withFileTypes: true }).flatMap(entry => {
    const file = `${folder}/${entry.name}`;
    return entry.isDirectory() ? filesBelow(root, file, accept) : entry.isFile() && accept(file) ? [file] : [];
  });
}
export function protectedFilePaths(root = ROOT) {
  const scripts = filesBelow(root, 'scripts/ib-ai-mocks-2026', f => /\.(?:py|cjs|mjs|sql)$/.test(f));
  for (const name of ['p1_author.py', 'p1_independent.py', 'p2_author.py', 'p2_independent.py', 'p3_author.py', 'p3_independent.py', 'build_pdfs.py', 'render_pdf_math.cjs', 'verify_database.sql'])
    assert.ok(scripts.includes(`scripts/ib-ai-mocks-2026/${name}`), `Missing scientific/release script ${name}`);
  const db = json(root, `${DOCS}/database-checks.json`);
  return sorted([...new Set([
    `${CONTENT}/catalog.json`, ...[...EXPECTED.keys()].map(id => `${CONTENT}/papers/${id}.json`),
    ...[...EXPECTED.keys()].map(id => `public/ib-mock-solutions/${id}.pdf`),
    ...filesBelow(root, DOCS, f => /\.(?:json|md)$/.test(f)), ...scripts, db.migration.file,
    'scripts/finalize-ib-ai-mock-reviews.mjs', 'scripts/verify-ib-ai-mock-reviews.mjs', 'scripts/verify-ib-ai-mocks.mjs',
  ])]);
}

/** Read-only. The optional in-memory candidate is used before an atomic freeze. */
export function verifyReviewManifest(root = ROOT, candidate = undefined) {
  const manifest = candidate ?? json(root, MANIFEST);
  assert.equal(manifest.schemaVersion, 1); passed(manifest, 'Manifest'); assert.equal(manifest.hashAlgorithm, 'sha256'); assert.equal(manifest.canonicalLineEndings, 'LF');
  const evidence = readReviewEvidence({ root }); assert.deepEqual(manifest.summary, evidence.summary); assert.deepEqual(manifest.papers, evidence.papers);
  sameSet(manifest.files.map(f => f.file), protectedFilePaths(root), 'Protected release files');
  for (const record of manifest.files) { const raw = read(root, record.file); assert.equal(record.bytes, raw.length, `${record.file}: size changed after review`); assert.equal(record.sha256, sha256(raw), `${record.file}: changed after review`); }
  return evidence;
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  try {
    assert.equal(process.argv.length, 2, 'Read-only verification accepts no bypass arguments');
    const { summary } = verifyReviewManifest();
    console.log(`IB AI review guard passed: ${summary.papers} papers, ${summary.questions} questions, ${summary.parts} fully covered parts, ${summary.pdfPages} PDF pages.`);
  } catch (error) { console.error(`IB AI review guard failed: ${error.message}`); process.exitCode = 1; }
}
