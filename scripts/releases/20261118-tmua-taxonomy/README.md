# TMUA question-bank taxonomy — 18 November 2026

The question bank had 14 raw topic labels and 1,239 active topic/subtopic pairs for 2,178 active questions. Numbered and unnumbered Geometry, Trigonometry and Calculus created duplicate topic cards; many subtopics were descriptions of single exercises, spelling variants or overlapping skills. Twenty-nine active questions had no subtopic.

The reviewed taxonomy has 11 topics and 84 populated subtopics. Its schema reserves three additional syllabus categories for future content. It relabels 2,162 active records and preserves every question, identity, content version and progress record. The 22 excluded questions remain unchanged.

## Source of truth

- `content/tmua-studio/taxonomy-20261118.json` contains the canonical vocabulary, an explicit mapping for each released question and 1,173 unambiguous historical label aliases.
- `lib/tmua-taxonomy.ts` normalizes spelling and presentation variants. Semantic merges are explicit in the manifest. Ambiguous old labels are resolved by question ID rather than a broad default rule.
- `questionMetadata()` applies the taxonomy to both the catalogue and question details. Original topic/subtopic names remain in the search text.
- `database_overrides` records three older database question versions whose actual tasks differ from the current portal version: `TMUA-P1-0256-12DD2C25`, `TMUA-P1-0825-7930B5F9` and `TMUA-P1-0933-C203902C`. Each version is classified by its own question content.

The effective portal catalogue uses the 447 releases from `originals-20261108.json.gz` before classification. Comparing only `questions.json` would classify superseded content for those IDs. The original archives and the database's `source_json` remain immutable provenance, so their old labels can intentionally differ from current navigation metadata.

## Main consolidation decisions

- Geometry, Trigonometry and Calculus each have one canonical topic.
- Powers, rational indices, radicals and surd manipulation are grouped under **Indices & surds** when those are the actual skill being tested.
- Quadratic equations, the discriminant and completing the square are grouped under **Quadratics & discriminants**.
- Tangent/normal questions, conditional probability/independence and arithmetic/geometric sequence variants have shared skill categories.
- **Miscellaneous** becomes **Number & Counting**, with separate categories for divisibility, remainders, integer constraints, digits, ratios, counting and rates.
- Misplaced questions move by their actual task: for example, errors in an argument go to **Errors in proofs**, and a counting question belongs under Probability only when it actually asks for a probability.

## Publish and rollback

`publish.sql` is an atomic, repeatable-read metadata update. It accepts only the reviewed old labels or the intended final labels, checks exact question coverage, locks the active rows and verifies a hash of **every column except `topic` and `subtopic`**. It also checks all excluded rows and TMUA progress before and after. It never updates question bodies, answers, IDs, timestamps, source JSON, difficulty, assets or progress. A mismatching question aborts the entire transaction. A retry after successful publication is a no-op.

`rollback.sql` applies the inverse label mapping with the same coverage and content guards. Keep the database and the app taxonomy release together when rolling back. `audit.json` records counts and the three intentional version-specific differences.

## Verification and future additions

`npm run verify:tmua-studio` runs the taxonomy gate before existing Studio checks. It enforces complete released-question coverage, valid unique labels, preserved IDs/content versions/source hashes, unchanged question payloads, retained search aliases and exclusion of inactive questions. The normal production build already runs this gate.

Add new questions to the explicit taxonomy map and an existing canonical skill, or deliberately extend the schema. Do not add a new one-question label to bypass the shared vocabulary. A new released question without a mapping fails the release verification.
