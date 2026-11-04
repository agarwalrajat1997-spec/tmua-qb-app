import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import {ibHarness} from './ib-component-harness.mjs';
export const ORIGIN='https://media.thrivingscholars.com';
export const BUCKET='thriving-scholars-media';
export const PREFIX='ib/psychology/2026-11-04/';
export const MANIFEST='content/ib/psychology-diagram-manifest.json';
export const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
export function ordered(value){if(Array.isArray(value))return value.map(ordered);if(value&&typeof value==='object')return Object.fromEntries(Object.keys(value).sort().map(key=>[key,ordered(value[key])]));return value;}
export const questionHash=q=>sha(JSON.stringify(ordered(q)));
export function readQuestions({partial=false}={}){
  const h=ibHarness(),{PSYCHOLOGY_TOPICS}=h.load('lib/ib/psychology-catalog.ts'),questions=[];
  for(const topic of PSYCHOLOGY_TOPICS){
    const file=`content/ib/psychology/${topic.id}.json`;
    if(!existsSync(file)){assert.ok(partial,`Missing authored bank: ${file}`);continue;}
    const values=JSON.parse(readFileSync(file,'utf8'));assert.ok(Array.isArray(values));
    for(const q of values){h.model.ibQuestionSchema.parse(q);assert.equal(q.topicId,topic.id);questions.push({q,file});}
  }
  assert.ok(questions.length,'No authored Psychology questions are available');
  assert.equal(new Set(questions.map(({q})=>q.id)).size,questions.length,'Duplicate Psychology question IDs');
  return questions;
}
export function validateObject(item){
  assert.match(item.sha256,/^[a-f0-9]{64}$/);assert.equal(item.key,PREFIX+item.sha256+'.svg');assert.ok(Number.isSafeInteger(item.bytes)&&item.bytes>0);
  assert.ok(Array.isArray(item.uses)&&item.uses.length);
  for(const use of item.uses){assert.match(use.questionId,/^ib-psy-(?:bio|cog|soc|res|cul|mot|tec)-\d{3}$/);assert.ok(['question','scheme'].includes(use.role));assert.match(use.questionSha256,/^[a-f0-9]{64}$/);}
}
export function readStage(directory){const stage=JSON.parse(readFileSync(resolve(directory,'staged-manifest.json'),'utf8'));assert.equal(stage.origin,ORIGIN);assert.equal(stage.bucket,BUCKET);assert.equal(stage.schemaVersion,1);assert.ok(Number.isSafeInteger(stage.questions)&&stage.questions>0&&stage.questions<=240);assert.equal(new Set(stage.objects.map(o=>o.sha256)).size,stage.objects.length);stage.objects.forEach(validateObject);return stage;}
