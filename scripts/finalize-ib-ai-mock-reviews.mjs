import assert from 'node:assert/strict';
import { readFileSync, writeFileSync, renameSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { ROOT, MANIFEST, sha256, readReviewEvidence, protectedFilePaths, verifyReviewManifest } from './verify-ib-ai-mock-reviews.mjs';

/** No review is generated, promoted, or approved here. Every prerequisite must already pass. */
export function finalizeReviewManifest(root = ROOT) {
  const evidence = readReviewEvidence({ root });
  const files = protectedFilePaths(root).map(file => {
    const raw = readFileSync(join(root, file)); return { file, bytes: raw.length, sha256: sha256(raw) };
  });
  const manifest = {
    schemaVersion: 1, status: 'passed', hashAlgorithm: 'sha256', canonicalLineEndings: 'LF',
    finalizedAtUTC: new Date().toISOString(),
    reviewScope: 'Original AI HL questions, complete worked marking schemes, scientific SVGs, combined PDFs, and recorded scientific/visual/database release evidence. Computational and AI review, not human IB examiner moderation.',
    ...evidence, files,
  };
  // Validate the complete candidate against current bytes before writing anything.
  verifyReviewManifest(root, manifest);
  const target = join(root, MANIFEST), temporary = `${target}.tmp`;
  writeFileSync(temporary, `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');
  renameSync(temporary, target);
  verifyReviewManifest(root);
  return manifest;
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  try {
    assert.equal(process.argv.length, 2, 'Finalization accepts no bypass arguments');
    const manifest = finalizeReviewManifest();
    console.log(`Frozen ${manifest.summary.papers} original IB AI HL papers and ${manifest.files.length} reviewed release files. Read-only verification passed.`);
  } catch (error) { console.error(`IB AI finalization failed: ${error.message}`); process.exitCode = 1; }
}
