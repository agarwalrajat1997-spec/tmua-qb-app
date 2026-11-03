import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync, readdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

export const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
export const CONTENT = 'content/ib/aa-mocks-2026';
export const DOCS = 'docs/ib-aa-mocks-2026';
export const MANIFEST = `${CONTENT}/review-manifest.json`;
export const SUMMARY = Object.freeze({
  papers: 10, questions: 90, marks: 870, diagrams: 27,
  pdfPages: 220, questionPaperPages: 109, solutionCovers: 10,
  retainedSourceSolutionPages: 101, authorChecks: 392, independentChecks: 641,
});
const EXPECTED = new Map([
  ['aa-hl-set-a-paper-1', 12], ['aa-hl-set-a-paper-2', 12], ['aa-hl-set-a-paper-3', 2],
  ['aa-hl-set-b-paper-1', 11], ['aa-hl-set-b-paper-2', 11], ['aa-hl-set-b-paper-3', 2],
  ['aa-sl-set-a-paper-1', 10], ['aa-sl-set-a-paper-2', 10],
  ['aa-sl-set-b-paper-1', 10], ['aa-sl-set-b-paper-2', 10],
]);
const GROUPS = [
  { name: 'hl-a', prefix: 'aa-hl-set-a-', questions: 26, authorChecks: 123, independentChecks: 251 },
  { name: 'hl-b', prefix: 'aa-hl-set-b-', questions: 24, authorChecks: 99, independentChecks: 152 },
  { name: 'sl', prefix: 'aa-sl-', questions: 40, authorChecks: 170, independentChecks: 238 },
];
export const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
const bytes = (root, file) => readFileSync(join(root, file));
const json = (root, file) => JSON.parse(bytes(root, file).toString('utf8'));
const sorted = values => [...values].sort();
const sameSet = (actual, expected, context) => {
  assert.equal(new Set(actual).size, actual.length, `${context}: duplicate identity`);
  assert.deepEqual(sorted(actual), sorted(expected), `${context}: missing or unexpected identity`);
};
const uniqueMap = (records, key, context) => {
  assert.ok(Array.isArray(records), `${context}: records must be an array`);
  const result = new Map();
  for (const record of records) {
    const id = key(record);
    assert.ok(!result.has(id), `${context}: duplicate ${id}`);
    result.set(id, record);
  }
  return result;
};
const passed = (record, context) => assert.equal(record.status, 'passed', `${context}: not passed`);
const empty = (value, context) => assert.deepEqual(value, [], `${context}: unresolved findings`);
const partChecks = record => Object.values(record.partChecks).flat();
const aEvidence = record => Object.values(record.parts).flatMap(part => {
  assert.equal(part.fullPromptAndSchemeManuallyVerified, true, 'HL A part was not fully read');
  return part.evidence;
});
const questionKey = record => `${record.paperId ?? record.paper}:${record.question ?? record.number}`;
// This is the compact, recursively sorted JSON used by the independent Python reviewers.
const sortObject = value => Array.isArray(value) ? value.map(sortObject) :
  value && typeof value === 'object' ? Object.fromEntries(Object.keys(value).sort().map(key => [key, sortObject(value[key])])) : value;
const questionHash = question => sha256(Buffer.from(JSON.stringify(sortObject(question)), 'utf8'));

function checkQuestionRecords(records, ids, papers, context, evidence, booleanEvidence = false) {
  const expected = ids.flatMap(id => papers.get(id).questions.map(q => `${id}:${q.number}`));
  const map = uniqueMap(records, questionKey, context);
  sameSet([...map.keys()], expected, context);
  let count = 0;
  for (const [key, record] of map) {
    passed(record, `${context} ${key}`);
    const [id, number] = key.split(':');
    const question = papers.get(id).questions.find(q => q.number === Number(number));
    assert.deepEqual(record.sourcePages, question.sourcePages, `${key}: source mapping changed`);
    if (record.marks !== undefined) assert.equal(record.marks, question.marks, `${key}: marks changed`);
    const hash = record.canonicalQuestionSha256 ?? record.questionSha256;
    if (hash !== undefined) assert.equal(questionHash(question), hash, `${key}: question differs from independent review`);
    const checks = evidence(record);
    assert.ok(Array.isArray(checks) && checks.length > 0, `${key}: missing executable evidence`);
    for (const check of checks) {
      if (booleanEvidence) assert.equal(check.passed, true, `${key}: failed evidence`);
      else passed(check, `${key}: failed evidence`);
    }
    count += checks.length;
  }
  return count;
}

/** Read-only validation. Pending summary labels are allowed only while finalizing already-passed reviews. */
export function readReviewEvidence({ root = ROOT, allowPendingSummary = false } = {}) {
  const catalog = json(root, `${CONTENT}/catalog.json`);
  sameSet(catalog.map(p => p.id), [...EXPECTED.keys()], 'catalogue');
  sameSet(readdirSync(join(root, CONTENT, 'papers')).filter(f => f.endsWith('.json')),
    [...EXPECTED.keys()].map(id => `${id}.json`), 'paper files');
  const papers = new Map(), bindings = new Map();
  const totals = { ...SUMMARY, questions: 0, marks: 0, diagrams: 0, pdfPages: 0,
    questionPaperPages: 0, retainedSourceSolutionPages: 0, authorChecks: 0, independentChecks: 0 };
  for (const meta of catalog) {
    const file = `${CONTENT}/papers/${meta.id}.json`, raw = bytes(root, file);
    assert.ok(!raw.includes(13), `${file}: reviewed canonical JSON must retain LF line endings`);
    const paper = JSON.parse(raw.toString('utf8'));
    for (const key of ['id', 'course', 'set', 'paper', 'minutes', 'marks', 'calculator'])
      assert.deepEqual(paper[key], meta[key], `${meta.id}: catalogue ${key} differs`);
    const title = value => value.replace(/\s*[·-]\s*/g, ' | ');
    assert.equal(title(paper.title), title(meta.title), `${meta.id}: catalogue title differs`);
    assert.equal(meta.status, 'published');
    assert.equal(meta.year, 2025);
    assert.equal(meta.questionCount, EXPECTED.get(meta.id));
    assert.equal(paper.questions.length, meta.questionCount);
    sameSet(paper.questions.map(q => q.number), Array.from({ length: meta.questionCount }, (_, i) => i + 1), `${meta.id} questions`);
    assert.equal(paper.minutes, paper.course === 'sl' ? 90 : paper.paper === '3' ? 75 : 120);
    assert.equal(paper.marks, paper.course === 'sl' ? 80 : paper.paper === '3' ? 55 : 110);
    assert.equal(paper.calculator, paper.paper !== '1');
    assert.equal(paper.questions.reduce((n, q) => n + q.marks, 0), paper.marks);
    papers.set(meta.id, paper);
    bindings.set(meta.id, { id: meta.id, questionFile: file, canonicalSha256: sha256(raw),
      questions: paper.questions.length, marks: paper.marks, minutes: paper.minutes, calculator: paper.calculator });
    totals.questions += paper.questions.length; totals.marks += paper.marks;
    totals.diagrams += paper.questions.filter(q => q.diagramSvg).length;
  }

  const pdfChecks = json(root, `${DOCS}/pdf-checks.json`);
  const renderChecks = json(root, `${DOCS}/pdf-render-checks.json`);
  if (allowPendingSummary) {
    assert.ok(['passed', 'built; visual review pending'].includes(pdfChecks.status), 'Unexpected PDF summary status');
    assert.ok(['passed', 'rendered; human-visible AI inspection pending'].includes(renderChecks.status), 'Unexpected render summary status');
  } else { passed(pdfChecks, 'PDF summary'); passed(renderChecks, 'render summary'); }
  assert.equal(pdfChecks.papers, 10); assert.equal(renderChecks.papers, 10); assert.equal(renderChecks.pages, 220);
  const pdfMap = uniqueMap(pdfChecks.records, p => p.id, 'PDF checks');
  const renderMap = uniqueMap(renderChecks.records, p => p.id, 'render checks');
  sameSet([...pdfMap.keys()], [...EXPECTED.keys()], 'PDF checks');
  sameSet([...renderMap.keys()], [...EXPECTED.keys()], 'render checks');

  for (const group of GROUPS) {
    const ids = [...EXPECTED.keys()].filter(id => id.startsWith(group.prefix));
    const independentFile = `${DOCS}/${group.name}-independent-review.json`;
    const authorFile = `${DOCS}/${group.name}-author-review.json`;
    const pdfReviewFile = `${DOCS}/${group.name}-pdf-review.json`;
    const independent = json(root, independentFile), author = json(root, authorFile), review = json(root, pdfReviewFile);
    passed(independent, independentFile); passed(review, pdfReviewFile);
    assert.equal(independent.questions, group.questions); assert.equal(author.questions, group.questions);
    let independentHashes, authorHashes, independentRecords, authorRecords, independentCount, authorCount, pdfRecords;
    if (group.name === 'hl-a') {
      assert.equal(independent.independentOfAuthorScript, true); empty(independent.unresolvedFindings, independentFile);
      empty(review.unresolvedFindings, pdfReviewFile);
      independentHashes = independent.papers.map(p => [p.id, p.sha256]);
      authorHashes = author.paperChecks.map(p => [p.id, p.sha256]);
      independentRecords = independent.questionsReviewed; authorRecords = author.records; pdfRecords = review.records;
      independentCount = independent.executableCalculationChecks; authorCount = author.executableCheckCount;
      assert.equal(author.status, 'passed author mathematical reconstruction checks; separate review required');
    } else if (group.name === 'hl-b') {
      independentHashes = independent.paperChecks.map(p => [p.id, p.sha256]);
      authorHashes = Object.entries(author.paperHashes);
      independentRecords = independent.records; authorRecords = author.records; pdfRecords = review.papers;
      independentCount = independent.numericalCheckCount; authorCount = author.executableChecks;
      passed(author, authorFile);
      assert.ok(review.findings.every(f => f.status === 'resolved and visually rechecked'), 'HL B PDF finding remains open');
    } else {
      empty(review.openFindings, pdfReviewFile);
      independentHashes = Object.entries(independent.paperHashes);
      authorHashes = author.batches.map(p => [p.paper, p.sha256]);
      independentRecords = independent.records;
      authorRecords = author.batches.flatMap(batch => batch.records.map(q => ({ ...q, paper: batch.paper })));
      pdfRecords = review.papers; independentCount = independent.independentCheckCount; authorCount = author.executableChecks;
      assert.equal(author.status, 'author verification passed; separate review pending');
    }
    for (const [label, hashes] of [['independent', independentHashes], ['author', authorHashes]]) {
      sameSet(hashes.map(([id]) => id), ids, `${group.name} ${label} hashes`);
      for (const [id, hash] of hashes) assert.equal(bindings.get(id).canonicalSha256, hash, `${id}: changed since ${label} review`);
    }
    const independentEvidence = group.name === 'hl-a' ? aEvidence : group.name === 'hl-b' ? q => q.independentChecks : partChecks;
    const authorEvidence = group.name === 'sl' ? partChecks : q => q.checks;
    assert.equal(checkQuestionRecords(independentRecords, ids, papers, independentFile, independentEvidence, group.name === 'hl-a'), group.independentChecks);
    assert.equal(checkQuestionRecords(authorRecords, ids, papers, authorFile, authorEvidence), group.authorChecks);
    assert.equal(independentCount, group.independentChecks); assert.equal(authorCount, group.authorChecks);
    totals.independentChecks += independentCount; totals.authorChecks += authorCount;
    sameSet(pdfRecords.map(p => p.id), ids, `${group.name} final PDF reviews`);
    for (const reviewed of pdfRecords) {
      passed(reviewed, `${pdfReviewFile} ${reviewed.id}`);
      if (reviewed.unresolvedFindings !== undefined) empty(reviewed.unresolvedFindings, reviewed.id);
      const id = reviewed.id, rec = pdfMap.get(id), render = renderMap.get(id), meta = catalog.find(p => p.id === id);
      passed(rec, `${id} PDF checks`); empty(render.outOfPageText, `${id} out-of-page text`);
      const file = `public/ib-mock-solutions/${id}.pdf`, raw = bytes(root, file), hash = sha256(raw);
      assert.equal(raw.subarray(0, 5).toString('ascii'), '%PDF-', `${file}: not a PDF`);
      assert.equal(hash, reviewed.pdfSha256 ?? reviewed.sha256, `${id}: PDF changed since visual review`);
      assert.equal(hash, rec.sha256, `${id}: PDF differs from builder checks`);
      assert.equal(raw.length, rec.bytes); assert.equal(raw.length, reviewed.pdfBytes ?? reviewed.bytes);
      assert.equal(rec.totalPages, reviewed.totalPages ?? reviewed.pages); assert.equal(rec.totalPages, render.pagesRendered);
      assert.equal(rec.questions, EXPECTED.get(id)); assert.equal(rec.marks, meta.marks); assert.equal(rec.minutes, meta.minutes);
      assert.equal(rec.diagrams, papers.get(id).questions.filter(q => q.diagramSvg).length);
      assert.equal(rec.solutionBookStartsAtPage, rec.questionPaperPages + 1);
      assert.equal(rec.totalPages, rec.questionPaperPages + 1 + rec.sourceSolutionsRetained);
      assert.equal(meta.pdfUrl, `/ib-mock-solutions/${id}.pdf`); assert.equal(rec.pdfUrl, meta.pdfUrl);
      if (reviewed.canonicalPaperSha256) assert.equal(reviewed.canonicalPaperSha256, bindings.get(id).canonicalSha256);
      if (reviewed.solutionBookStartsAtPage !== undefined) assert.equal(reviewed.solutionBookStartsAtPage, rec.solutionBookStartsAtPage);
      const starts = Object.entries(rec.questionStartPages);
      sameSet(starts.map(([q]) => Number(q)), papers.get(id).questions.map(q => q.number), `${id} question bookmarks`);
      assert.ok(starts.every(([, page]) => Number.isInteger(page) && page >= 2 && page <= rec.questionPaperPages));
      Object.assign(bindings.get(id), { independentReview: independentFile, pdfReview: pdfReviewFile,
        pdfFile: file, pdfSha256: hash, pdfPages: rec.totalPages, questionPaperPages: rec.questionPaperPages,
        solutionBookStartsAtPage: rec.solutionBookStartsAtPage });
      totals.pdfPages += rec.totalPages; totals.questionPaperPages += rec.questionPaperPages;
      totals.retainedSourceSolutionPages += rec.sourceSolutionsRetained;
    }
  }
  const database = json(root, `${DOCS}/database-checks.json`);
  passed(database, 'database checks');
  for (const key of ['schemaApplied', 'rowLevelSecurityEnabled', 'explicitOwnerPolicies', 'columnRestrictedInsertAndUpdate', 'noAnonymousAccess'])
    assert.equal(database[key], true, `Database release evidence: ${key}`);
  assert.deepEqual(totals, SUMMARY, 'Release totals differ from the reviewed set');
  return { summary: totals, papers: [...bindings.values()].sort((a, b) => a.id.localeCompare(b.id)) };
}

function listFiles(root, folder, accept) {
  return readdirSync(join(root, folder), { withFileTypes: true }).flatMap(entry => {
    const file = `${folder}/${entry.name}`;
    return entry.isDirectory() ? listFiles(root, file, accept) : entry.isFile() && accept(file) ? [file] : [];
  });
}

export function protectedFilePaths(root = ROOT) {
  const scientificScripts = listFiles(root, 'scripts/ib-aa-mocks-2026', file => /\.(?:py|cjs|mjs)$/.test(file));
  for (const name of ['hl_a_author.py', 'hl_b_author.py', 'sl_author.py', 'hl_a_independent.py',
    'hl_b_independent.py', 'sl_independent.py', 'build_pdfs.py', 'render_pdf_math.cjs', 'render_pdf_review.py'])
    assert.ok(scientificScripts.includes(`scripts/ib-aa-mocks-2026/${name}`), `Missing required scientific script: ${name}`);
  return sorted([
    `${CONTENT}/catalog.json`, ...[...EXPECTED.keys()].map(id => `${CONTENT}/papers/${id}.json`),
    ...[...EXPECTED.keys()].map(id => `public/ib-mock-solutions/${id}.pdf`),
    `${DOCS}/README.md`, ...listFiles(root, DOCS, file => file.endsWith('.json')),
    ...scientificScripts,
    'scripts/finalize-ib-aa-mock-reviews.mjs', 'scripts/verify-ib-aa-mock-reviews.mjs', 'scripts/verify-ib-aa-mocks.mjs',
  ]);
}

/** Verify only: this function and the CLI never write, regenerate or approve evidence. */
export function verifyReviewManifest(root = ROOT) {
  const manifest = json(root, MANIFEST);
  assert.equal(manifest.schemaVersion, 1); assert.equal(manifest.status, 'passed');
  assert.equal(manifest.hashAlgorithm, 'sha256'); assert.equal(manifest.canonicalLineEndings, 'LF');
  const evidence = readReviewEvidence({ root });
  assert.deepEqual(manifest.summary, evidence.summary); assert.deepEqual(manifest.papers, evidence.papers);
  sameSet(manifest.files.map(f => f.file), protectedFilePaths(root), 'Protected release files');
  for (const record of manifest.files) {
    const raw = bytes(root, record.file);
    assert.equal(raw.length, record.bytes, `${record.file}: size changed after release review`);
    assert.equal(sha256(raw), record.sha256, `${record.file}: changed after release review`);
  }
  return evidence;
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  try {
    assert.equal(process.argv.length, 2, 'This read-only guard accepts no bypass arguments');
    const evidence = verifyReviewManifest();
    console.log(`IB AA mock review guard passed: ${evidence.summary.papers} papers, ${evidence.summary.questions} independently reviewed questions, ${evidence.summary.pdfPages} PDF pages; frozen raw hashes match.`);
  } catch (error) {
    console.error(`IB AA mock review guard failed: ${error.message}`);
    process.exitCode = 1;
  }
}
