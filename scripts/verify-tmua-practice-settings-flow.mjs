import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';

const root='public/practice-tests/tests/';
const topicFiles=['p1-mock-01-algebra-sequences-functions-geometry.html','p1-mock-02-graphs-trig-logs.html','p1-mock-03-calculus.html','p1-mock-05-all-topics.html','p2-mock-04-logic-proofs.html','p2-mock-06-all-topics.html'];
const files=[...topicFiles,'full-mock-01-all-topics.html','full-mock-02-all-topics.html','tmua-2024-2025-challenging-mock/index.html','tmua-2026-predictive-paper/index.html'];
const clean=value=>JSON.parse(JSON.stringify(value));
const noop=()=>{};
// Rendering is exercised separately in the browser and the existing official-paper DOM suite.
// Here only visual functions are stubbed: clocks, state, navigation, scoring, storage and actual submit serializers execute unchanged.
function visualStubs(source,names){
  const ast=ts.createSourceFile('controller.js',source,ts.ScriptTarget.Latest,true,ts.ScriptKind.JS), edits=[];
  function visit(node){if(ts.isFunctionDeclaration(node)&&node.name&&names.includes(node.name.text))edits.push([node.getStart(ast),node.end,`function ${node.name.text}(){}`]);ts.forEachChild(node,visit);}visit(ast);
  for(const[a,b,text]of edits.sort((x,y)=>y[0]-x[0]))source=source.slice(0,a)+text+source.slice(b);return source;
}
function fixture(file,storage=new Map()){
  const html=fs.readFileSync(root+file,'utf8'),predictive=file.includes('predictive'),topic=topicFiles.includes(file),challenge=file.includes('challenging');
  const scripts=[...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)];
  for(const match of scripts)if(!match[1].includes('application/json'))new vm.Script(match[2],{filename:file});
  let controller=scripts.map(m=>m[2]).find(s=>s.includes(predictive?'const defaultPack':topic?'const QUESTIONS':'const questions'));
  assert(controller,file);
  const elements=new Map();
  function element(id=''){
    if(id&&elements.has(id))return elements.get(id);
    const e={id,value:'Practice student',textContent:'',innerHTML:'',style:{},dataset:{},className:'',children:[],open:false,
      checkValidity:()=>true,focus:noop,setAttribute:noop,getAttribute:()=>null,addEventListener:noop,remove:noop,close(){this.open=false;},
      classList:{add:noop,remove:noop,toggle:noop,contains:()=>false},querySelector:()=>element(),querySelectorAll:()=>[],
      appendChild(n){this.children.push(n);n.parentNode=this;return n;},insertBefore:noop,insertAdjacentHTML:noop,
      getBoundingClientRect:()=>({width:100,height:100}),getClientRects:()=>[1]};e.parentNode=e;if(id)elements.set(id,e);return e;
  }
  element('student-name').value='Regression student';element('student-email').value='qa@example.invalid';element('exam-interface').style.display='none';
  if(predictive)element('tmua-data').textContent=scripts.find(m=>m[1].includes('id="tmua-data"'))[2];
  const document={body:element('body'),head:element('head'),documentElement:{outerHTML:html},readyState:'loading',getElementById:element,querySelector:()=>element(),querySelectorAll:()=>[],createElement:()=>element(),addEventListener:noop};
  let clock=1700000000000,intervalId=0;const intervals=new Map(),requests=[],emails=[],alerts=[];
  class Clock extends Date{constructor(...args){super(...(args.length?args:[clock]));}static now(){return clock;}}
  const context=vm.createContext({document,Date:Clock,performance:{now:()=>clock},console:{log:noop,warn:noop,error:noop},URL,AbortController,TextEncoder,solutionPDF:'https://qa.invalid/solutions.pdf',
    location:{protocol:'https:',origin:'https://apps.thrivingscholars.com',href:'https://apps.thrivingscholars.com/practice-tests/tests/'+file,hash:''},
    localStorage:{getItem:key=>storage.get(key)??null,setItem:(key,value)=>storage.set(key,value),removeItem:key=>storage.delete(key)},
    setInterval:(fn,ms)=>{intervals.set(++intervalId,{fn,ms});return intervalId;},clearInterval:id=>intervals.delete(id),setTimeout:()=>0,clearTimeout:noop,
    alert:message=>alerts.push(message),confirm:()=>true,MathJax:{typesetPromise:async()=>{},typesetClear:noop},
    emailjs:{init:noop,send:async(_service,_template,payload)=>{emails.push(clean(payload));return{status:200};}},
    fetch:async(url,init)=>{requests.push({url,payload:JSON.parse(init.body)});return{ok:true,status:200,json:async()=>({ok:true,status:'saved'})};}
  });
  context.window=context;context.addEventListener=noop;context.scrollTo=noop;
  vm.runInContext(fs.readFileSync('public/shared/practice-test-options.js','utf8'),context);
  vm.runInContext(fs.readFileSync('public/shared/tmua-practice-settings.js','utf8'),context);
  context.TS_TMUA_PRACTICE.mount=noop;context.TS_TMUA_PRACTICE.resultNote=noop;
  controller=visualStubs(controller,['renderQuestion','buildNavigator','updateNavigator','syncPracticeNavigation','renderResults','setResultStatus','generateNavigatorButtons','updateNavigatorButton','updateFlagButton','typesetMath','safeTypeset','renderWelcome','render','renderReview','renderNavigator','toast']);
  if(predictive){
    const ast=ts.createSourceFile('predictive.js',controller,ts.ScriptTarget.Latest,true,ts.ScriptKind.JS);let item;
    function find(node){if(ts.isFunctionDeclaration(node)&&node.name?.text==='safeHtml')item=node;ts.forEachChild(node,find);}find(ast);
    controller=controller.slice(0,item.getStart(ast))+'function safeHtml(value){return String(value??"");}'+controller.slice(item.end);
    controller=controller.replace(/\}\)\(\);\s*$/,'window.__flow={start:()=>{state=freshState({name:"Regression student",email:"qa@example.invalid",session:"Practice"});},snapshot:()=>({state,pack,savedAttempt}),answer:updateAnswer,next:()=>navigate(1),previous:()=>navigate(-1),flag:toggleFlag,advancePaper:()=>advancePaper(Date.now(),"submitted"),syncClock,persist,readSaved,buildReport,prediction,resume:()=>{state=savedAttempt;},options:()=>practiceOptions};})();');
  }
  vm.runInContext(controller,context,{filename:file});
  const serializer=scripts.map(m=>m[2]).find(s=>s.includes('window.TS_SAVE_ATTEMPT = async function'));
  if(serializer)vm.runInContext(serializer,context);
  const get=expression=>vm.runInContext(expression,context);
  const kind=predictive?'predictive':topic?'topic':challenge?'challenge':'legacy';
  return{context,get,kind,storage,requests,emails,alerts,elements,intervals,
    advance:seconds=>{clock+=seconds*1000;},options:()=>context.TS_TMUA_ACTIVE_OPTIONS,
    start:()=>predictive?context.__flow.start():context.startExam(),
    current:()=>predictive?context.__flow.snapshot().state.paperIndex*20+context.__flow.snapshot().state.questionIndex:get(topic?'state.current':'current'),
    keys:()=>clean(predictive?context.__flow.snapshot().pack.papers.flatMap(p=>p.questions.map(q=>q.correctAnswer)):get('correctAnswers')),
    answer:value=>predictive?context.__flow.answer(value):(topic||challenge)?context.setPracticeAnswer(value):get(`userAnswers[current]=${JSON.stringify(value)}`),
    next:()=>predictive?context.__flow.next():context.nextQuestion(),previous:()=>predictive?context.__flow.previous():context.prevQuestion(),
    flag:()=>predictive?context.__flow.flag():context.toggleFlag(),
    times:()=>clean(predictive?context.__flow.snapshot().state.times.flat():get(topic?'state.timeSpent':'timeSpent')),
    async finishPaper(){if(predictive){context.__flow.advancePaper();return;}if(topic){await context.submitExam();return;}if(get('paper')===1){context.confirmSubmit();const before=this.times().reduce((a,b)=>a+b,0);this.advance(37);context.skipBreak();assert.equal(this.times().reduce((a,b)=>a+b,0),before,'Break time excluded');}else{context.confirmSubmit();for(let i=0;i<8;i++)await Promise.resolve();}}
  };
}
function settings(count,multiplier,order){return{version:1,order,time_multiplier:multiplier,section_sizes:count===40?[20,20]:[20],base_seconds_per_section:4500,question_order:Array.from({length:count},(_,i)=>order==='randomised'?Math.floor(i/20)*20+(i%20+7)%20:i)};}
let completed=0;
for(const file of files)for(const multiplier of [1,1.25,1.5])for(const order of ['sequential','randomised']){
  const h=fixture(file),count=h.kind==='topic'?20:40,label=`${file}/${multiplier}/${order}`,metadata=settings(count,multiplier,order);
  h.options().restore(metadata);h.advance(120);h.start();assert.equal(h.alerts.length,0,label);
  assert.equal(h.options().durationSeconds(),4500*multiplier,label);
  if(h.kind==='topic')assert.equal(h.get('state.timerEndAt-Date.now()'),4500000*multiplier,label);
  if(h.kind==='legacy')assert.equal(h.get('paperDeadline-Date.now()'),4500000*multiplier,label);
  if(h.kind==='challenge')assert.equal(h.get('secondsRemaining'),4500*multiplier,label);
  if(h.kind==='predictive')assert.equal(h.context.__flow.snapshot().state.endAt-h.context.Date.now(),4500000*multiplier,label);
  assert.equal(h.times().reduce((a,b)=>a+b,0),0,'Instruction time excluded');
  const expected=Array(count).fill(null),keys=h.keys(),expectedTimes=Array(count).fill(3),expectedFlags=Array(count).fill(false);
  for(let section=0;section<count/20;section++){
    for(let position=0;position<20;position++){
      const canonical=metadata.question_order[section*20+position];assert.equal(h.current(),canonical,label);
      if(position===0){h.previous();assert.equal(h.current(),canonical,'Previous locks section boundary');}
      const answer=canonical%3===0?null:canonical%3===1?keys[canonical]:(keys[canonical]==='A'?'B':'A');
      if(answer!==null)h.answer(answer);expected[canonical]=answer;
      if(canonical%7===0){h.flag();expectedFlags[canonical]=true;}
      h.advance(3);
      if(position<19)h.next();
    }
    await h.finishPaper();
  }
  let report;
  if(h.kind==='predictive')report=clean(h.context.__flow.buildReport());
  else{assert.equal(h.requests.length,1,label);report=h.requests[0].payload;}
  assert.deepEqual(report.answers,expected,label);assert.deepEqual(report.correct_answers,keys,label);assert.deepEqual(report.flags,expectedFlags,label);assert.deepEqual(report.time_spent,expectedTimes,label);
  assert.deepEqual(report.practice_settings,metadata,label);assert.equal(report.score,expected.filter((a,i)=>a===keys[i]).length,label);
  assert.equal(h.options().adjustedRaw(count,count),count-Math.round(count*(multiplier===1.25?3:multiplier===1.5?5:0)/40));
  if(h.kind==='predictive')assert.equal(h.context.__flow.prediction().value,h.context.__flow.snapshot().pack.predictor.table[h.options().adjustedRaw(report.score,40)],label);
  completed++;
}
let expired=0;
for(const file of files)for(const multiplier of [1,1.25,1.5]){
  const h=fixture(file),count=h.kind==='topic'?20:40,metadata=settings(count,multiplier,'randomised'),duration=4500*multiplier;
  h.options().restore(metadata);h.advance(125);h.start();
  const first=h.current();h.advance(duration+45);
  if(h.kind==='predictive')h.context.__flow.syncClock();
  else if(h.kind==='challenge')h.intervals.values().next().value.fn();
  else await h.context.updateTimer();
  assert.equal(h.times()[first],duration,file+': late timer cannot add time beyond deadline');
  if(count===40){
    if(h.kind!=='predictive')h.context.skipBreak();
    const second=h.current();assert.equal(second,metadata.question_order[20]);h.advance(duration+45);
    if(h.kind==='predictive')h.context.__flow.syncClock();
    else if(h.kind==='challenge')h.intervals.values().next().value.fn();
    else await h.context.updateTimer();
    assert.equal(h.times()[second],duration,file+': second paper deadline');
  }
  for(let i=0;i<12;i++)await Promise.resolve();
  const report=h.kind==='predictive'?h.context.__flow.buildReport():h.requests[0]?.payload;
  assert(report,file+': automatic submission produced report');assert.equal(report.score,0);assert.equal(report.time_spent.reduce((a,b)=>a+b,0),duration*(count/20));
  assert.equal(h.intervals.size,0,file+': automatic submission clears timer');expired++;
}
// Deliver a user input before any timer callback after expiry. The previous answer must survive.
let guarded=0;
for(const file of [...topicFiles,'tmua-2024-2025-challenging-mock/index.html'])for(const multiplier of [1,1.25,1.5]){
  const h=fixture(file),count=h.kind==='topic'?20:40,metadata=settings(count,multiplier,'randomised');h.options().restore(metadata);h.start();
  const first=h.current(),correct=h.keys()[first];assert.equal(h.answer(correct),true);h.advance(4500*multiplier+1);
  assert.equal(h.answer(correct==='A'?'B':'A'),false,file+': reject late answer before tick');h.next();h.previous();h.flag();
  assert.equal(h.current(),first,file+': reject late navigation');assert.equal(h.get(h.kind==='topic'?`state.userAnswers[${first}]`:`userAnswers[${first}]`),correct,file+': retain original answer');
  if(h.kind==='challenge'){
    assert.equal(h.elements.get('exam-interface').style.display,'none');h.context.skipBreak();const second=h.current();h.answer(h.keys()[second]);h.advance(4500*multiplier+1);
    h.context.jumpTo(metadata.question_order[21]);assert.equal(h.current(),second,'late navigator cannot cross deadline');assert.equal(h.answer('A'),false);
  }
  for(let i=0;i<12;i++)await Promise.resolve();assert.equal(h.requests.length,1,file+': one automatic submission');
  assert.equal(h.requests[0].payload.answers[first],correct);assert.equal(h.requests[0].payload.time_spent[first],4500*multiplier);guarded++;
}
// Predictive reload keeps exactly the same permutation, time allowance, canonical answer and timers.
for(const multiplier of [1,1.25,1.5]){
  const file='tmua-2026-predictive-paper/index.html',h=fixture(file),metadata=settings(40,multiplier,'randomised');h.options().restore(metadata);h.start();
  const first=h.current();h.answer(h.keys()[first]);h.advance(7);h.next();h.context.__flow.persist();const saved=clean(h.context.__flow.snapshot().state);
  const resumed=fixture(file,h.storage);resumed.context.__flow.resume();assert.deepEqual(clean(resumed.context.__flow.snapshot().state),saved);assert.deepEqual(clean(resumed.options().metadata()),metadata);
  resumed.advance(4500*multiplier+50);resumed.context.__flow.syncClock();assert.equal(resumed.context.__flow.snapshot().state.paperIndex,1);assert.equal(resumed.current(),metadata.question_order[20]);
  const prior=fixture(file,h.storage);const entry=[...prior.storage.entries()][0];const legacy=JSON.parse(entry[1]);delete legacy.state.practiceSettings;prior.storage.set(entry[0],JSON.stringify(legacy));const old=fixture(file,prior.storage);assert.equal(old.options().metadata().time_multiplier,1,'Historical attempts default to standard time');
}
console.log(`TMUA practice settings: ${completed} complete real-controller submissions, ${expired} timer-expiry flows, ${guarded} late-input guards and 3 predictive reloads verified across all 10 new tests.`);
