import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { ibHarness } from './ib-component-harness.mjs';

const base={id:'ib-aa-na-001',subject:'math-aa-hl',topicId:'number-algebra',collectionId:'number-algebra',number:1,title:'Expand a binomial',subtopic:'Binomial theorem',difficulty:'easy',calculator:false,marks:2,stem:'Expand $(x+3)^2$.',parts:[],markScheme:[{part:'',steps:[{code:'M1',text:'Use the binomial theorem.'},{code:'A1',text:'SECRET-SOLUTION-CANARY $x^2+6x+9$.'}]}],source:{document:'Synthetic test only',question:1},verification:{method:'symbolic',notes:'Synthetic fixture'},status:'published'};
const other={...base,id:'ib-aa-na-002',number:2,title:'A logarithm',subtopic:'Logarithms',difficulty:'hard',calculator:true,stem:'Find $\\log_3 7$.',source:{...base.source,question:2}};
const draft={...base,id:'ib-aa-na-003',number:3,status:'draft',source:{...base.source,question:3}};
const authCalls=[];
const harness=ibHarness({questions:[base,other,draft],onAuth:next=>authCalls.push(next)});
const page=harness.load('app/ib/question-bank/[collection]/page.tsx').default;
const questionPage=harness.load('app/ib/questions/[id]/page.tsx').default;
const schemePage=harness.load('app/ib/mark-scheme/[id]/page.tsx').default;
const request=query=>({params:Promise.resolve({collection:'number-algebra'}),searchParams:Promise.resolve(query)});
let html=renderToStaticMarkup(await page(request({})));
assert.match(html,/Question 1/);assert.match(html,/Question 2/);assert.doesNotMatch(html,/Question 3|SECRET-SOLUTION-CANARY|Synthetic test only|Video|AI Feedback/);
assert.match(html,/target="_blank"/);assert.match(html,/rel="noopener noreferrer"/);assert.match(html,/katex/);
html=renderToStaticMarkup(await page(request({difficulty:'hard',calculator:'yes'})));
assert.match(html,/Question 2/);assert.doesNotMatch(html,/Question 1/);
assert.match(authCalls.at(-1),/difficulty=hard&calculator=yes/);
html=renderToStaticMarkup(await page(request({subtopic:'Binomial theorem',q:'binomial'})));
assert.match(html,/Question 1/);assert.doesNotMatch(html,/Question 2/);
html=renderToStaticMarkup(await page(request({q:'nonexistent',page:'99999999'})));
assert.match(html,/No questions match these filters/);assert.doesNotMatch(html,/SECRET-SOLUTION-CANARY/);
html=renderToStaticMarkup(await page(request({difficulty:'forged',calculator:'forged',page:'NaN'})));
assert.match(html,/Question 1/);assert.match(html,/Question 2/);
html=renderToStaticMarkup(await questionPage({params:Promise.resolve({id:base.id})}));
assert.match(html,/Maximum mark/);assert.doesNotMatch(html,/SECRET-SOLUTION-CANARY|Synthetic test only/);
html=renderToStaticMarkup(await schemePage({params:Promise.resolve({id:base.id})}));
assert.match(html,/SECRET-SOLUTION-CANARY/);assert.match(html,/M1/);assert.match(html,/A1/);assert.doesNotMatch(html,/Synthetic test only/);
await assert.rejects(()=>schemePage({params:Promise.resolve({id:draft.id})}),/NOT_FOUND/);
await assert.rejects(()=>questionPage({params:Promise.resolve({id:'missing'})}),/NOT_FOUND/);

const blocked=ibHarness({questions:[base],user:null});
for(const route of ['app/ib/questions/[id]/page.tsx','app/ib/mark-scheme/[id]/page.tsx']) await assert.rejects(()=>blocked.load(route).default({params:Promise.resolve({id:base.id})}),/AUTH_REQUIRED/);
await assert.rejects(()=>blocked.load('app/ib/question-bank/[collection]/page.tsx').default(request({})),/AUTH_REQUIRED/);
assert.equal(harness.model.safeDiagram('<svg viewBox="0 0 10 10"><script>alert(1)</script></svg>'),false);
assert.equal(harness.model.safeDiagram('<svg viewBox="0 0 10 10"><image href="https://external.invalid/a"/></svg>'),false);
assert.equal(harness.model.safeDiagram('<svg viewBox="0 0 10 10"><path d="M0 0L10 10"/></svg>'),true);
for(const bad of [{...base,marks:3},{...base,calculator:'yes'},{...base,markScheme:[]},{...base,topicId:'calculus'}]) assert.equal(harness.model.ibQuestionSchema.safeParse(bad).success,false);
assert.match(readFileSync('lib/ib/content.ts','utf8'),/^import "server-only"/);
assert.match(readFileSync('app/ib-login/IBLoginClient.tsx','utf8'),/parsed\.pathname\.startsWith\("\/ib\/"\)/);

// Exercise the real page-level guard as well as the routes' dependency boundary.
let guardUser={email:'synthetic@example.invalid'},guardError=null,verifiedCalls=0;
const guardCode=ts.transpileModule(readFileSync('lib/ib/auth.ts','utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText;
const guardImports={
  'server-only':{},'react':{cache:fn=>fn},
  'next/navigation':{redirect:destination=>{throw new Error(`LOGIN:${destination}`);}},
  '@/lib/auth/login-destination':harness.load('lib/auth/login-destination.ts'),
  '@/utils/supabase/server':{supabaseServer:async()=>({auth:{getUser:async()=>{verifiedCalls++;return {data:{user:guardUser},error:guardError};}}})},
};
const guardContext=vm.createContext({exports:{},require:name=>{assert.ok(name in guardImports);return guardImports[name];},encodeURIComponent});
vm.runInContext(guardCode,guardContext);
const guard=guardContext.exports.requireIbUser;
assert.equal((await guard('/ib/questions/ib-aa-na-001')).email,guardUser.email);
for(const failure of ['no-user','no-email','provider-error']) {
  guardUser=failure==='no-user'?null:failure==='no-email'?{}:{email:'synthetic@example.invalid'};
  guardError=failure==='provider-error'?{message:'synthetic error'}:null;
  await assert.rejects(()=>guard('/ib/mark-scheme/ib-aa-na-001'),/LOGIN:\/ib-login\?next=%2Fib%2Fmark-scheme%2Fib-aa-na-001/);
}
assert.equal(verifiedCalls,4);
console.log('IB portal passed: authenticated server rendering; real Markdown/KaTeX; filters and empty states; separate-tab schemes; no solution/private metadata in question HTML; drafts and unknown IDs withheld; invalid data and active SVG rejected. Synthetic fixtures only; no emails or database writes.');
