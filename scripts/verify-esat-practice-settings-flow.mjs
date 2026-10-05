import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const root='public/esat-practice-tests/tests';
const helper=fs.readFileSync('public/shared/practice-test-options.js','utf8');
const runtime=fs.readFileSync('public/shared/esat-october-2026-runtime.js','utf8');
const portal=fs.readFileSync('public/shared/esat-october-2026-portal.js','utf8');
const clean=value=>JSON.parse(JSON.stringify(value));

// Minimal DOM contract; execute production controllers, rendering, timers and serializers.
class Element {
  constructor(tag='div') {
    this.tagName=tag.toUpperCase();this.children=[];this.style={};this.dataset={};this.listeners={};this.value='';this.className='';this._html='';this._text='';
    this.classList={add:(n)=>{this.className+=' '+n;},remove:()=>{},toggle:()=>{},contains:n=>this.className.split(' ').includes(n)};
  }
  appendChild(node){this.children.push(node);node.parentElement=this;return node;}
  append(node){return this.appendChild(node);}
  replaceChildren(...nodes){this.children=nodes;}
  addEventListener(name,fn){(this.listeners[name]||=[]).push(fn);}
  dispatch(name,event={target:this}){for(const fn of this.listeners[name]||[])fn(event);}
  setAttribute(name,value){this[name]=value;}
  getAttribute(name){return this[name]??null;}
  focus(){} close(){} showModal(){} remove(){} click(){}
  matches(selector){return selector==='input[data-ts-choice]'&&this['data-ts-choice']!==undefined;}
  get textContent(){return this._text||this._html.replace(/<[^>]*>/g,'');}
  set textContent(value){this._text=String(value);}
  get innerHTML(){return this._html;}
  set innerHTML(value){
    this._html=String(value);this.children=[];this._text='';
    const heading=this._html.match(/class="question-number"[^>]*>([^<]*)/);
    if(heading){const node=new Element();node.className='question-number';node.textContent=heading[1];this.appendChild(node);}
    for(const match of this._html.matchAll(/<input\b([^>]*)>/g)){
      const node=new Element('input');
      for(const attribute of match[1].matchAll(/([\w-]+)=["']([^"']*)["']/g))node[attribute[1]]=attribute[2];
      this.appendChild(node);
    }
    for(const name of ['ts-test-score-note','ts-test-settings-locked','ts-test-settings-grid'])if(this._html.includes(name)){const node=new Element();node.className=name;this.appendChild(node);}
  }
  querySelectorAll(selector){
    const matches=node=>{
      if(selector==='input[data-ts-choice]')return node.tagName==='INPUT'&&node['data-ts-choice'];
      if(selector==='input[type="radio"]')return node.tagName==='INPUT'&&node.type==='radio';
      const name=selector.match(/^input\[name=['"]([^'"]+)['"]\]$/);if(name)return node.name===name[1];
      const value=selector.match(/^input\[type=radio\]\[value="([^"]+)"\]$/);if(value)return node.type==='radio'&&node.value===value[1];
      if(selector.startsWith('.'))return node.className.split(' ').includes(selector.slice(1));
      if(selector.startsWith('#'))return node.id===selector.slice(1);
      return false;
    };
    const result=[];const visit=node=>node.children.forEach(child=>{if(matches(child))result.push(child);visit(child);});visit(this);return result;
  }
  querySelector(selector){return this.querySelectorAll(selector)[0]||null;}
}

function environment(folder,storage=new Map()) {
  const html=fs.readFileSync(`${root}/${folder}/index.html`,'utf8');
  const october=folder.startsWith('esat-october-');
  const elements=new Map();
  for(const match of html.matchAll(/\bid="([^\"]+)"/g)){const node=new Element();node.id=match[1];elements.set(node.id,node);}
  const body=new Element('body'),head=new Element('head'),footer=new Element(),header=new Element();
  const all=()=>[body,head,...elements.values()];
  const doc={body,head,documentElement:new Element(),visibilityState:'visible',hasFocus:()=>true,readyState:'complete',listeners:{},
    addEventListener(name,fn){(this.listeners[name]||=[]).push(fn);},createElement:tag=>new Element(tag),
    getElementById(id){
      for(const node of all()){if(node.id===id)return node;const found=node.querySelector('#'+id);if(found)return found;}
      if(october && elements.get('app').innerHTML.includes('id="'+id+'"')){const node=new Element();node.id=id;return node;}
      return null;
    },
    querySelector(selector){if(selector==='.footer')return footer;if(selector==='.header')return header;if(selector.startsWith('#'))return this.getElementById(selector.slice(1));return this.querySelectorAll(selector)[0]||null;},
    querySelectorAll(selector){return all().flatMap(node=>node.querySelectorAll(selector));}
  };
  // Persist generated settings host for change events, while recreating it after October renders.
  const get=doc.getElementById.bind(doc);let settingsHost=null,lastMarkup=null;
  doc.getElementById=id=>{
    if(october&&id==='ts-practice-settings'){
      const markup=elements.get('app').innerHTML;if(!markup.includes('id="ts-practice-settings"'))return null;
      if(markup!==lastMarkup){settingsHost=new Element();settingsHost.id=id;lastMarkup=markup;}return settingsHost;
    }return get(id);
  };
  if(!october){elements.get('student-name').value='Regression Student';elements.get('student-email').value='';elements.get('test-date').value='October 2026';elements.get('exam-interface').style.display='none';}
  let clock=1800000000000,timer=0;
  class Clock extends Date{constructor(...args){super(...(args.length?args:[clock]));}static now(){return clock;}}
  const requests=[],intervals=new Map(),alerts=[];
  const context=vm.createContext({document:doc,Date:Clock,console:{log(){},warn(){},error(){}},CSS:{escape:s=>s},URL,Blob,AbortController,
    localStorage:{getItem:key=>storage.get(key)||null,setItem:(key,value)=>storage.set(key,String(value)),removeItem:key=>storage.delete(key)},
    setInterval:(fn,ms)=>{intervals.set(++timer,{fn,ms});return timer;},clearInterval:id=>intervals.delete(id),setTimeout:()=>0,clearTimeout(){},
    confirm:()=>true,alert:message=>alerts.push(message),MathJax:{typesetPromise:async()=>{}},CustomEvent:class{},
    fetch:async(url,options)=>{requests.push({url,payload:JSON.parse(options.body)});return {ok:true,status:200,json:async()=>({ok:true,attempt:{id:'test-attempt'}})};}
  });
  context.window=context;context.addEventListener=()=>{};context.dispatchEvent=()=>{};context.scrollTo=()=>{};context.location={origin:'https://example.test'};
  vm.runInContext(helper,context);
  if(october){
    const data=JSON.parse(html.match(/<script id="test-data" type="application\/json">([\s\S]*?)<\/script>/)[1]);
    data.config={...data.config,autoEmail:false,emailjs:{enabled:false}};
    elements.get('test-data').textContent=JSON.stringify(data);
    vm.runInContext(runtime,context,{filename:folder+':runtime'});
    return {context,doc,elements,storage,requests,intervals,alerts,data,advance:seconds=>{clock+=seconds*1000;},tick:()=>{for(const {fn} of [...intervals.values()])fn();}};
  }
  const scripts=[...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)].filter(match=>!match[1].includes('src=')).map(match=>match[2]);
  for(const source of scripts.filter(s=>/const testId\s*=|const questions\s*=|const correctAnswers\s*=|TS_ESAT_ATTEMPT_SAVE_HELPER_V1|let timeSpent =|const totalQuestions =/.test(s)))vm.runInContext(source,context,{filename:folder+':inline'});
  return {context,doc,elements,storage,requests,intervals,alerts,read:code=>vm.runInContext(code,context),advance:seconds=>{clock+=seconds*1000;}};
}
function select(h,order,multiplier){
  const host=h.doc.getElementById('ts-practice-settings');
  for(const [key,value] of [['order',order],['time_multiplier',String(multiplier)]]){
    const input=host.querySelectorAll('input[data-ts-choice]').find(node=>node['data-ts-choice']===key&&node.value===value);assert.ok(input);host.dispatch('change',{target:input});
  }
}
const legacy=fs.readdirSync(root).filter(folder=>/^(?:esat-mock-(?:0[1-4]|13)|esat-.*-level-[012]|esat-recall-2024-25-.*)$/.test(folder));
let checked=0;
for(const folder of legacy)for(const multiplier of [1,1.25,1.5])for(const order of ['sequential','randomised']){
  const h=environment(folder),recall=folder.includes('recall-');select(h,order,multiplier);h.context.startExam();
  const settings=clean(h.read('practiceSettings.metadata()')),answers=Array(81).fill(null),flags=Array(81).fill(false);
  const allowance=()=>recall?h.read('(sectionDeadline-Date.now())/1000'):h.read('secondsRemaining');
  assert.equal(allowance(),2400*multiplier);assert.equal(settings.order,order);
  h.advance(1);const before=allowance();h.context.startExam();assert.equal(allowance(),before,'repeated start retains clock');
  for(let section=0;section<3;section++){
    if(section){h.context.showBreakScreen();h.advance(10);h.context.skipBreak();assert.equal(allowance(),2400*multiplier);}
    const first=settings.question_order[section*27],second=settings.question_order[section*27+1];
    assert.equal(h.read('current'),first);h.context.prevQuestion();assert.equal(h.read('current'),first);
    h.context.generateNavigatorButtons();const buttons=h.elements.get('navigator-grid').children;
    assert.deepEqual(buttons.map(b=>Number(b.dataset.index)),settings.question_order.slice(section*27,(section+1)*27));
    const answer=h.read('correctAnswers[current]');const input=h.elements.get('question-container').querySelectorAll('input[type="radio"]').find(i=>i.value===answer);assert.ok(input);input.dispatch('change');answers[first]=answer;
    h.context.toggleFlag();flags[first]=true;h.advance(7);h.context.nextQuestion();assert.equal(h.read('current'),second);assert.ok(h.read(`timeSpent[${first}]`)>=7);
    h.context.prevQuestion();assert.equal(h.read('current'),first);buttons[1].onclick();assert.equal(h.read('current'),second);
  }
  await h.context.saveRemoteAttempt(3);const submitted=h.requests.at(-1).payload;
  assert.deepEqual(submitted.answers,answers);assert.deepEqual(submitted.flags,flags);assert.deepEqual(submitted.practice_settings,settings);assert.equal(submitted.time_spent.length,81);
  if(recall){
    h.context.persistActive();const saved=clean(h.read('loadActive()'));assert.deepEqual(saved.practice_settings,settings);
    const restored=environment(folder,h.storage);restored.context.startExam();assert.deepEqual(clean(restored.read('practiceSettings.metadata()')),settings);assert.equal(restored.read('current'),h.read('current'));assert.equal(restored.read('sectionDeadline'),h.read('sectionDeadline'));assert.deepEqual(clean(restored.read('userAnswers')),answers);
  }
  assert.equal(h.alerts.length,0);checked++;
}

// Deadline enforcement must not depend on the next scheduled timer callback.
// A late answer, navigation click or duplicated break callback cannot reopen a module.
let deadlineChecks=0;
for(const folder of legacy)for(const multiplier of [1,1.25,1.5])for(const order of ['sequential','randomised']){
  const h=environment(folder);select(h,order,multiplier);h.context.startExam();
  const duration=2400*multiplier,settings=clean(h.read('practiceSettings.metadata()'));
  for(let section=0;section<3;section++){
    const first=settings.question_order[section*27];assert.equal(h.read('current'),first);
    const input=h.elements.get('question-container').querySelectorAll('input[type="radio"]')[0];
    h.advance(duration+45);input.dispatch('change');
    assert.equal(h.read(`userAnswers[${first}]`),null,'answer at an expired deadline is rejected');
    assert.equal(h.read(`timeSpent[${first}]`),duration,'question time is capped at its selected module deadline');
    h.context.nextQuestion();h.context.prevQuestion();h.context.toggleFlag();h.context.jumpTo(first+1);
    assert.equal(h.read('current'),first);assert.equal(h.read(`flags[${first}]`),false);
    if(section<2){
      assert.notEqual(h.elements.get('break-screen').style.display,'none');
      h.context.skipBreak();const deadline=h.read('sectionDeadline');
      h.context.skipBreak();h.context.updateBreakTimer();
      assert.equal(h.read('sectionIndex'),section+1);assert.equal(h.read('sectionDeadline'),deadline);
      assert.equal(h.read('(sectionDeadline-Date.now())/1000'),duration);
    }
  }
  const submitted=h.requests.at(-1).payload;
  assert.equal(submitted.score,0);assert.deepEqual(submitted.answers,Array(81).fill(null));
  assert.equal(submitted.time_spent.reduce((sum,t)=>sum+t,0),duration*3);
  assert.deepEqual(submitted.practice_settings,settings);
  assert.equal([...h.intervals.values()].filter(timer=>timer.ms===250||timer.ms===1000).length,0,'completion clears active timers');
  deadlineChecks++;
}

function action(h,name,index){
  const button={dataset:{action:name,index:String(index??0)},disabled:false};
  h.elements.get('app').dispatch('click',{target:{closest:()=>button}});
}
function octoberStart(h){
  // Drive actual form listener without requiring a browser's FormData implementation.
  h.context.FormData=class{get(key){return {studentName:'Regression Student',studentEmail:'',studentSession:'October 2026'}[key];}};
  h.elements.get('app').dispatch('submit',{target:{id:'start-form'},preventDefault(){}});action(h,'begin');
}
for(const folder of fs.readdirSync(root).filter(f=>f.startsWith('esat-october-2026-')))for(const multiplier of [1,1.25,1.5])for(const order of ['sequential','randomised']){
  const h=environment(folder);select(h,order,multiplier);octoberStart(h);
  let state=h.context.ESATRuntime.getState();const metadata=state.practice_settings;assert.equal(metadata.order,order);assert.equal(metadata.time_multiplier,multiplier);
  for(let mi=0;mi<3;mi++){
    state=h.context.ESATRuntime.getState();const first=metadata.question_order[mi*27]-mi*27,second=metadata.question_order[mi*27+1]-mi*27;
    assert.equal(state.questionIndex,first);assert.equal(state.modules[mi].deadline-state.modules[mi].startedAt,2400000*multiplier);
    const answer=h.data.modules[mi].questions[first].correctAnswer;
    const button={dataset:{action:'select',label:answer},disabled:false};h.elements.get('app').dispatch('click',{target:{closest:()=>button}});
    h.advance(7);action(h,'next');state=h.context.ESATRuntime.getState();assert.equal(state.questionIndex,second);assert.equal(state.modules[mi].answers[first],answer);assert.equal(state.modules[mi].timesMs[first],7000);
    action(h,'prev');assert.equal(h.context.ESATRuntime.getState().questionIndex,first);
    action(h,'confirm-submit');
  }
  const report=h.context.ESATRuntime.getReport();assert.equal(report.totalScore,3);assert.deepEqual(clean(report.practice_settings),clean(metadata));
  report.modules.forEach((m,mi)=>{assert.equal(m.questions.length,27);assert.equal(m.rawScore,1);assert.equal(m.adjustedRaw,multiplier===1?1:0);assert.equal(m.questions[metadata.question_order[mi*27]-mi*27].selectedAnswer,h.data.modules[mi].questions[metadata.question_order[mi*27]-mi*27].correctAnswer);});
  if(multiplier!==1)assert.equal(report.scoreLabel,'Estimated standard-time equivalent');
  vm.runInContext(portal,h.context);const saved=await h.context.TS_ESAT_PORTAL.onComplete(report);assert.equal(saved.status,'sent');
  const submitted=h.requests.at(-1).payload;assert.deepEqual(submitted.practice_settings,clean(metadata));assert.deepEqual(submitted.answers,clean(report.modules.flatMap(m=>m.questions.map(q=>q.selectedAnswer||''))));assert.deepEqual(submitted.time_spent,clean(report.modules.flatMap(m=>m.questions.map(q=>q.timeSpentSeconds))));assert.equal(submitted.score,3);
  const restored=environment(folder,h.storage);assert.deepEqual(clean(restored.context.ESATRuntime.getState().practice_settings),clean(metadata));assert.equal(restored.context.ESATRuntime.getReport().totalScore,3);
  checked++;
}

// An in-progress shuffled October attempt retains its order and adjusted allowance after reload,
// including automatic transitions across multiple elapsed module deadlines.
const octoberFolder='esat-october-2026-engineering';
const active=environment(octoberFolder);select(active,'randomised',1.5);octoberStart(active);active.advance(7);action(active,'next');
const activeState=active.context.ESATRuntime.getState(),resumed=environment(octoberFolder,active.storage);
assert.deepEqual(clean(resumed.context.ESATRuntime.getState().practice_settings),clean(activeState.practice_settings));
assert.equal(resumed.context.ESATRuntime.getState().questionIndex,activeState.questionIndex);
action(resumed,'resume');resumed.advance(3601);resumed.tick();
const advanced=resumed.context.ESATRuntime.getState();assert.equal(advanced.moduleIndex,1);assert.equal(advanced.modules[1].deadline-advanced.modules[1].startedAt,3600000);assert.equal(advanced.questionIndex,advanced.practice_settings.question_order[27]-27);

for(const folder of legacy.filter(f=>f.includes('recall-'))){
  const h=environment(folder);select(h,'randomised',1.25);h.context.startExam();h.context.confirmSubmit();
  const deadline=h.read('breakDeadline'),restored=environment(folder,h.storage);restored.context.startExam();
  assert.equal(restored.read('breakDeadline'),deadline);assert.equal(restored.elements.get('exam-interface').style.display,'none');assert.equal(restored.elements.get('break-screen').style.display,'flex');
  restored.context.skipBreak();assert.equal(restored.read('(sectionDeadline-Date.now())/1000'),3000);assert.equal(restored.read('current'),restored.read('practiceSettings.questionAt(1,0)'));

  // Resuming an expired active module must not install a stale section timer after opening the break.
  const expired=environment(folder);select(expired,'randomised',1.5);expired.context.startExam();
  const key=expired.read('ACTIVE_KEY'),saved=JSON.parse(expired.storage.get(key));saved.sectionDeadline=1799999999000;expired.storage.set(key,JSON.stringify(saved));
  const expiredResume=environment(folder,expired.storage);expiredResume.context.startExam();
  const breakDeadline=expiredResume.read('breakDeadline');assert.ok(breakDeadline);
  assert.equal([...expiredResume.intervals.values()].filter(timer=>timer.ms===250).length,1,'only the break timer remains after expired resume');
  expiredResume.context.updateTimer();assert.equal(expiredResume.read('breakDeadline'),breakDeadline,'a stale section callback cannot restart the break');
}

const oldOctober=environment(octoberFolder);octoberStart(oldOctober);
const oldKey=oldOctober.context.ESATRuntime.storageKey,oldState=JSON.parse(oldOctober.storage.get(oldKey));delete oldState.practice_settings;oldOctober.storage.set(oldKey,JSON.stringify(oldState));
const legacyResume=environment(octoberFolder,oldOctober.storage);assert.equal(legacyResume.context.ESATRuntime.getState().practice_settings.time_multiplier,1);assert.equal(legacyResume.context.ESATRuntime.getState().practice_settings.order,'sequential');

console.log(`ESAT settings flow passed: ${checked} real-controller settings scenarios across all 32 clients, plus ${deadlineChecks} late-action deadline scenarios; original/shuffled order, all allowances, canonical answers/flags/times, resume and automatic October transitions. No network writes or emails.`);
