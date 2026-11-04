import assert from 'node:assert/strict';
import {existsSync,readFileSync,writeFileSync,renameSync} from 'node:fs';
import {join,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {sha} from './psychology-media.mjs';
import {ROOT,DOCS,MANIFEST,readReviewEvidence,protectedFilePaths,verifyReviewManifest,validateMutationProof} from './verify-ib-psychology-reviews.mjs';

/** Refuse to freeze incomplete evidence or silently replace an existing frozen release. */
export function finalizeReviewManifest(root=ROOT){
  const path=join(root,MANIFEST);
  if(existsSync(path)){verifyReviewManifest(root);return JSON.parse(readFileSync(path,'utf8'));}
  const evidence=readReviewEvidence({root});
  const mutations=JSON.parse(readFileSync(join(root,DOCS,'review-guard-mutation-checks.json'),'utf8'));
  validateMutationProof(root,mutations);
  const files=protectedFilePaths(root).map(file=>{const bytes=readFileSync(join(root,file));return {file,bytes:bytes.length,sha256:sha(bytes)};});
  const manifest={schemaVersion:1,status:'passed',hashAlgorithm:'sha256',finalizedAtUTC:new Date().toISOString(),scope:'Original first-assessment2027 Psychology SL/HL practice, independently reviewed question by question and native/mobile stimulus by stimulus. Computational and AI review; no claim of IB endorsement or human examiner moderation.',...evidence,files};
  verifyReviewManifest(root,manifest);
  const temporary=path+'.tmp';writeFileSync(temporary,JSON.stringify(manifest,null,2)+'\n');renameSync(temporary,path);verifyReviewManifest(root);return manifest;
}
if(process.argv[1]&&pathToFileURL(resolve(process.argv[1])).href===import.meta.url){try{assert.equal(process.argv.length,2,'Finalization accepts no bypass flags');const m=finalizeReviewManifest();console.log(`Frozen ${m.summary.questions} Psychology questions with ${m.files.length} protected files.`);}catch(error){console.error(`IB Psychology finalization failed: ${error.message}`);process.exitCode=1;}}
