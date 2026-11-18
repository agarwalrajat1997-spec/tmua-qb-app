import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { gunzipSync } from 'node:zlib';
import {
  TMUA_TAXONOMY_VERSION,
  canonicalTmuaQuestionTaxonomy,
  canonicalTmuaSubtopic,
  canonicalTmuaTopic,
  normalizeTmuaTaxonomyLabel,
  normalizeTmuaTopicLabel,
  tmuaTaxonomyAliasKey,
} from '../lib/tmua-taxonomy.ts';
import {
  canonicalQid,
  catalogue,
  publicQuestion,
  questionMetadata,
  resolveQuestion,
} from '../lib/tmua-studio-server/catalogue.ts';

const root = new URL('../content/tmua-studio/', import.meta.url);
const read = name => JSON.parse(readFileSync(new URL(name, root), 'utf8'));
const manifest = read('taxonomy-20261118.json');
const eligibility = read('eligibility.json');
const originals = read('questions.json');
const replacements = JSON.parse(gunzipSync(
  readFileSync(new URL('originals-20261108.json.gz', root)),
).toString('utf8'));
const replacementsById = new Map(replacements.map(release => [canonicalQid(release.question.qid), release]));

// Read the immutable releases independently of the presentation adapter. The
// 447 replacements, rather than their superseded prompts, are the current bank.
const effectiveSources = originals.map(original => {
  const release = replacementsById.get(canonicalQid(original.qid));
  if (!release) return original;
  assert.equal(release.previous_version, original.content_version);
  assert.equal(release.question.app_question_id, original.app_question_id);
  assert.equal(release.guide.version_id, release.question.content_version);
  assert.equal(release.guide.source_sha256, release.question.source_sha256);
  return release.question;
});
assert.equal(replacementsById.size, 447);
assert.equal(effectiveSources.length, 2178);
const activeIds = new Set(eligibility.active_audit_ids.map(canonicalQid));
const excludedIds = new Set(eligibility.excluded_ids.map(canonicalQid));
assert.equal(activeIds.size, 2178);
assert.equal(excludedIds.size, 22);
assert.deepEqual(new Set(effectiveSources.map(q => canonicalQid(q.qid))), activeIds);
assert.deepEqual(new Set(catalogue.map(q => q.qid)), activeIds);
assert.equal(catalogue.length, activeIds.size, 'No released question can disappear or be duplicated by a merge.');
assert.deepEqual(new Set(Object.keys(manifest.questions)), activeIds,
  'Every released question needs one explicit mapping; excluded questions stay excluded.');
for (const qid of excludedIds) {
  assert.ok(!Object.hasOwn(manifest.questions, qid), `Excluded question mapped: ${qid}`);
  assert.equal(resolveQuestion(qid), undefined);
}

assert.equal(typeof manifest.version, 'string');
assert.ok(manifest.version.trim());
assert.equal(TMUA_TAXONOMY_VERSION, manifest.version);
const topics = Object.entries(manifest.topics);
assert.equal(topics.length, 11);
assert.equal(new Set(topics.map(([topic]) => normalizeTmuaTopicLabel(topic))).size, topics.length,
  'Topic labels that display the same must not create separate filters.');
for (const [topic, subtopics] of topics) {
  assert.ok(topic.trim() === topic && topic.length > 0);
  assert.ok(Array.isArray(subtopics) && subtopics.length > 0, `Missing subtopics for ${topic}`);
  assert.ok(subtopics.every(label => typeof label === 'string' && label.trim() === label && label.length > 0));
  assert.equal(new Set(subtopics.map(normalizeTmuaTaxonomyLabel)).size, subtopics.length,
    `Duplicate normalized subtopic in ${topic}`);
}
const validTarget = (target, context) => {
  assert.ok(target && typeof target === 'object', `Missing taxonomy pair: ${context}`);
  assert.ok(Object.hasOwn(manifest.topics, target.topic), `Unknown topic: ${context}`);
  assert.ok(manifest.topics[target.topic].includes(target.subtopic), `Unknown subtopic: ${context}`);
};
for (const [qid, pair] of Object.entries(manifest.questions)) validTarget(pair, qid);
for (const [qid, pair] of Object.entries(manifest.database_overrides ?? {})) {
  assert.ok(activeIds.has(qid), `Database override is not a released question: ${qid}`);
  validTarget(pair, `database override ${qid}`);
}
for (const [key, pair] of Object.entries(manifest.aliases ?? {})) {
  validTarget(pair, `alias ${key}`);
  const labels = JSON.parse(key);
  assert.ok(Array.isArray(labels) && labels.length === 2);
  assert.equal(tmuaTaxonomyAliasKey(...labels), key, 'Alias keys must use the shared normalization.');
  const fallback = canonicalTmuaQuestionTaxonomy({ qid: 'future-unmapped-question', topic: labels[0], subtopic: labels[1] });
  assert.deepEqual({ topic: fallback.topic, subtopic: fallback.subtopic }, pair,
    `Known historical alias does not resolve: ${key}`);
}

const byId = new Map(catalogue.map(question => [question.qid, question]));
let changedPairs = 0;
for (const source of effectiveSources) {
  const qid = canonicalQid(source.qid);
  const expected = manifest.questions[qid];
  const selected = resolveQuestion(qid);
  assert.ok(selected, `Question no longer resolves: ${qid}`);
  assert.equal(resolveQuestion(source.qid), selected, `Audit alias changed: ${qid}`);
  const metadata = questionMetadata(selected);
  const payload = publicQuestion(selected);
  const rows = [byId.get(qid), metadata, payload];
  for (const row of rows) {
    assert.equal(row.qid, qid);
    assert.equal(row.bank_qid, qid);
    assert.equal(row.audit_qid, qid);
    assert.equal(row.app_question_id, source.app_question_id, `Progress identity changed: ${qid}`);
    assert.equal(row.display_order, Number(source.app_question_id));
    assert.equal(row.paper, source.paper);
    assert.equal(row.difficulty, source.difficulty);
    assert.equal(row.content_version, source.content_version, `Question version changed: ${qid}`);
    assert.equal(row.source_sha256, source.source_sha256, `Source hash changed: ${qid}`);
    assert.deepEqual({ topic: row.topic, subtopic: row.subtopic }, expected);
    assert.equal(row.taxonomy_version, manifest.version);
    for (const label of [source.topic, source.subtopic, source.skill_search]) {
      if (typeof label === 'string' && label.trim()) {
        assert.ok(row.skill_search.includes(label.trim()), `Historical search label lost: ${qid}`);
      }
    }
  }
  assert.ok(payload.prompt_html === source.prompt_html, `Prompt changed: ${qid}`);
  // A pre-existing display correction fixes this one malformed English option;
  // the taxonomy overlay must preserve the established question payload.
  const expectedOptions = source.qid === 'TMUA-P2-0528-38785261' && Array.isArray(source.options)
    ? source.options.map(option => option.label === 'E' && option.html === '\\(\\text{infinitely many\\)'
      ? { ...option, html: 'infinitely many' } : option)
    : source.options;
  assert.deepEqual(payload.options, expectedOptions, `Options changed: ${qid}`);
  assert.equal(selected.topic, source.topic, `Archived topic was mutated: ${qid}`);
  assert.equal(selected.subtopic, source.subtopic, `Archived subtopic was mutated: ${qid}`);
  const versioned = resolveQuestion(qid, source.content_version);
  assert.equal(versioned?.source_sha256, source.source_sha256, `Versioned progress lookup changed: ${qid}`);
  assert.ok(versioned?.prompt_html === source.prompt_html, `Versioned prompt changed: ${qid}`);
  if (source.topic !== expected.topic || source.subtopic !== expected.subtopic) changedPairs++;
}

// Regression cases for the observed duplicate display labels and imported
// entities. Number prefixes belong to topics, not to mathematical subtopics.
for (const [raw, expected] of [
  ['Calculus', '7_Calculus'], ['7_Calculus', '7_Calculus'],
  [' 3_Geometry ', '3_Geometry'], ['Geometry', '3_Geometry'],
  ['6_Trigonometry', '6_Trigonometry'], ['Trigonometry', '6_Trigonometry'],
  ['1_Algebra_and_Functions', '1_Algebra & Functions'],
  ['1_Algebra &amp; Functions', '1_Algebra & Functions'],
  ['Algebra &#38; Functions', '1_Algebra & Functions'],
  ['Algebra &#x26; Functions', '1_Algebra & Functions'],
  ['Miscellaneous', '10_Number & Counting'], ['10_Miscellaneous', '10_Number & Counting'],
  ['Number and Counting', '10_Number & Counting'],
]) assert.equal(canonicalTmuaTopic(raw), expected, `Topic alias failed: ${raw}`);
assert.equal(canonicalTmuaSubtopic('Algebra', 'Indices_and_surds'), 'Indices & surds');
assert.equal(canonicalTmuaSubtopic('Algebra', '  INDICES &amp; SURDS '), 'Indices & surds');
assert.notEqual(normalizeTmuaTaxonomyLabel('2-adic valuation'), normalizeTmuaTaxonomyLabel('3-adic valuation'));
assert.notEqual(normalizeTmuaTaxonomyLabel('2D geometry'), normalizeTmuaTaxonomyLabel('3D geometry'));
assert.equal(tmuaTaxonomyAliasKey('7_Calculus', 'Tangents & normals'),
  tmuaTaxonomyAliasKey('calculus', '  tangents_and_normals '));

const sampleId = effectiveSources[0] && canonicalQid(effectiveSources[0].qid);
const explicit = canonicalTmuaQuestionTaxonomy({ qid: sampleId, topic: 'Unexpected topic', subtopic: 'Unrelated label' });
assert.deepEqual({ topic: explicit.topic, subtopic: explicit.subtopic }, manifest.questions[sampleId],
  'The reviewed question mapping must take precedence over stale source labels.');
const unknown = canonicalTmuaQuestionTaxonomy({ qid: 'future-unmapped-question', topic: 'New subject', subtopic: 'New technique' });
assert.equal(unknown.topic, 'New subject');
assert.equal(unknown.subtopic, 'New technique');
assert.ok(unknown.skill_search.includes('New technique'));
const absent = canonicalTmuaQuestionTaxonomy({ qid: 'future-empty-question' });
assert.equal(absent.topic, 'General practice');
assert.equal(absent.subtopic, 'General practice');

console.log(`PASS: TMUA taxonomy covers all ${activeIds.size} released questions (${changedPairs} regrouped), ` +
  `${topics.length} unique topics, preserved content/progress identities and search labels, ` +
  `${excludedIds.size} retained exclusions, and historical aliases.`);
