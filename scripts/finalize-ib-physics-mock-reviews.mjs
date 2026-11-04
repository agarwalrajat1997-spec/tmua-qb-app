import assert from 'node:assert/strict';
import { readFileSync, writeFileSync, renameSync, existsSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { ROOT, MANIFEST, sha256, readReviewEvidence, protectedFilePaths, verifyReviewManifest } from './verify-ib-physics-mock-reviews.mjs';

/** No review is generated or promoted. A frozen release is never rebaselined. */
export function finalizeReviewManifest(root=ROOT) {
  const target=join(root,MANIFEST);
  if(existsSync(target)){verifyReviewManifest(root);return JSON.parse(readFileSync(target,'utf8'));}
  const evidence=readReviewEvidence({root});
  const files=protectedFilePaths(root).map(file=>{const raw=readFileSync(join(root,file));return {file,bytes:raw.length,sha256:sha256(raw)};});
  const manifest={schemaVersion:1,status:'passed',hashAlgorithm:'sha256',finalizedAtUTC:new Date().toISOString(),reviewScope:'Original current-course Physics SL/HL questions, complete schemes, independent every-part scientific review, scientific SVG/raster binding, question-first combined PDFs and final visual/portal/database evidence. Computational and AI review; no claim of human IB examiner moderation.',...evidence,files};
  verifyReviewManifest(root,manifest);
  const temporary=`${target}.tmp`;writeFileSync(temporary,`${JSON.stringify(manifest,null,2)}\n`,'utf8');renameSync(temporary,target);verifyReviewManifest(root);return manifest;
}
if(process.argv[1]&&pathToFileURL(resolve(process.argv[1])).href===import.meta.url){try{assert.equal(process.argv.length,2,'Finalization accepts no bypass arguments');const m=finalizeReviewManifest();console.log(`Frozen ${m.summary.papers} Physics papers and ${m.files.length} protected release files. Read-only verification passed.`);}catch(e){console.error(`IB Physics finalization failed: ${e.message}`);process.exitCode=1;}}
