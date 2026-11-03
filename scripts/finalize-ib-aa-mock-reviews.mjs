import assert from 'node:assert/strict';
import { readFileSync, writeFileSync, renameSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { ROOT, DOCS, MANIFEST, sha256, readReviewEvidence, protectedFilePaths, verifyReviewManifest } from './verify-ib-aa-mock-reviews.mjs';

const writeJSON = (file, value) => {
  const target = join(ROOT, file), temporary = `${target}.tmp`;
  writeFileSync(temporary, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
  renameSync(temporary, target);
};

export function finalizeReviewManifest() {
  // Nothing is promoted until every actual paper/PDF hash and every review record passes.
  readReviewEvidence({ allowPendingSummary: true });
  for (const file of [`${DOCS}/pdf-checks.json`, `${DOCS}/pdf-render-checks.json`]) {
    const report = JSON.parse(readFileSync(join(ROOT, file), 'utf8'));
    report.status = 'passed';
    writeJSON(file, report);
  }
  const evidence = readReviewEvidence();
  const files = protectedFilePaths().map(file => {
    const raw = readFileSync(join(ROOT, file));
    return { file, bytes: raw.length, sha256: sha256(raw) };
  });
  const manifest = {
    schemaVersion: 1, status: 'passed', hashAlgorithm: 'sha256', canonicalLineEndings: 'LF',
    finalizedAtUTC: new Date().toISOString(),
    reviewScope: 'Reconstructed questions, schemes, original diagrams, corrected combined PDFs, and recorded release evidence. Computational and AI review; not human IB examiner moderation.',
    ...evidence, files,
  };
  writeJSON(MANIFEST, manifest);
  verifyReviewManifest();
  return manifest;
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  try {
    assert.equal(process.argv.length, 2, 'Finalization accepts no bypass arguments');
    const manifest = finalizeReviewManifest();
    console.log(`Frozen ${manifest.summary.papers} IB AA mocks and ${manifest.files.length} reviewed release files. Read-only verification passed.`);
  } catch (error) {
    console.error(`IB AA mock finalization failed: ${error.message}`);
    process.exitCode = 1;
  }
}
