// Mechanical source integration for the TMUA engines. Question packs and answer keys are never rewritten.
import fs from 'node:fs';
import path from 'node:path';
import ts from 'typescript';

const base = 'public/practice-tests/tests';
const marker = 'TS_TMUA_PRACTICE_SETTINGS_V1';
const dependency = '<script src="/shared/practice-test-options.js?v=20261005-1"></script>\n<script src="/shared/tmua-practice-settings.js?v=20261005-1"></script>\n';
const read = file => fs.readFileSync(path.join(base, file), 'utf8').replace(/\r\n/g, '\n');
function save(file, source) {
  source=source.replace(/\n[ \t]+\n(?=(?:window\.TS_TMUA_PRACTICE|syncPracticeNavigation\(|function (?:canEditPractice|expirePracticePaper)\())/g,'\n\n');
  const target=path.join(base,file);
  if(fs.readFileSync(target,'utf8')!==source)fs.writeFileSync(target,source);
}
function functions(source, names) {
  const ast = ts.createSourceFile('engine.js', source, ts.ScriptTarget.Latest, true, ts.ScriptKind.JS);
  const found = [];
  function visit(node) {
    if (ts.isFunctionDeclaration(node) && node.name && Object.hasOwn(names, node.name.text)) {
      found.push({start:node.getStart(ast),end:node.end,name:node.name.text,text:node.getText(ast)});
    }
    ts.forEachChild(node, visit);
  }
  visit(ast);
  for (const name of Object.keys(names)) if (!found.some(x=>x.name===name)) throw Error('Missing function '+name);
  for (const item of found.sort((a,b)=>b.start-a.start)) {
    const replacement = typeof names[item.name] === 'function' ? names[item.name](item.text) : names[item.name];
    source = source.slice(0,item.start)+replacement+source.slice(item.end);
  }
  return source;
}
function engine(source, sentinel, transform) {
  let matched = false;
  source = source.replace(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g,(all,js)=>{
    if(!js.includes(sentinel))return all;
    if(matched)throw Error('Multiple engine scripts');matched=true;
    return all.replace(js,transform(js));
  });
  if(!matched)throw Error('Missing engine '+sentinel);
  return source;
}
const append = (source, code) => source.slice(0,source.lastIndexOf('}')).trimEnd()+'\n'+code+'\n}';
function injectHead(source) { return source.replace('</head>',dependency+'</head>'); }

const topicFiles = ['p1-mock-01-algebra-sequences-functions-geometry.html','p1-mock-02-graphs-trig-logs.html','p1-mock-03-calculus.html','p1-mock-05-all-topics.html','p2-mock-04-logic-proofs.html','p2-mock-06-all-topics.html'];
for(const file of topicFiles){
  let source=read(file);if(source.includes(marker))continue;
  source=injectHead(source);
  source=engine(source,'const QUESTIONS',js=>{
    const init=`\n/* ${marker} */\nconst practiceOptions=window.TS_TMUA_PRACTICE.create(TEST.id,[20]);\nwindow.TS_TMUA_PRACTICE.mount(practiceOptions,document.querySelector('#instructions .candidate-row'));\nfunction practiceQuestionLabel(index){return window.TS_TMUA_PRACTICE.questionLabel(practiceOptions,index);}\nfunction syncPracticeNavigation(){\n  if(!state.started)return;\n  practiceOptions.sequence().forEach((index,position)=>{const button=document.getElementById('nav-btn-'+index);if(!button)return;button.textContent=(state.flags[index]?'⚑ ':'')+(position+1);button.setAttribute('aria-label','Question '+(position+1)+(state.userAnswers[index]?', answered':', unanswered')+(state.flags[index]?', flagged':''));els.navigatorGrid.appendChild(button);});\n}\n`;
    js=js.replace(/(const correctAnswers\s*=\s*Object\.freeze\(QUESTIONS\.map\(q\s*=>\s*q\.answer\)\);)/,'$1'+init);
    if(!js.includes(marker))throw Error('Topic initialization failed '+file);
    js=functions(js,{
      startExam:text=>text.replace(/state\.started\s*=\s*true;/,'practiceOptions.start();state.current=practiceOptions.questionAt(0,0);state.started=true;').replace('TEST.durationSeconds','practiceOptions.durationSeconds()'),
      nextQuestion:'function nextQuestion(){const position=practiceOptions.positionOf(state.current);if(position<QUESTIONS.length-1)goToQuestion(practiceOptions.questionAt(0,position+1));}',
      prevQuestion:'function prevQuestion(){const position=practiceOptions.positionOf(state.current);if(position>0)goToQuestion(practiceOptions.questionAt(0,position-1));}',
      renderQuestion:text=>append(text,`\nwindow.TS_TMUA_PRACTICE.decorate(practiceOptions,els.question,state.current,Number(TEST.paper));\nconst position=practiceOptions.positionOf(state.current);els.counter.textContent='Question '+(position+1)+' of '+QUESTIONS.length;els.prev.disabled=position===0;els.next.disabled=position===QUESTIONS.length-1;syncPracticeNavigation();`),
      updateNavigator:text=>append(text,'\nsyncPracticeNavigation();'),
      estimateTmuaScore:text=>text.replace('{','{rawCorrect=practiceOptions.adjustedRaw(rawCorrect,QUESTIONS.length);'),
      buildAnalysisRows:text=>text.replaceAll('${q.number}','${practiceQuestionLabel(index)}'),
      buildPlainTextAnalysis:text=>text.replace('return ','return practiceOptions.summary()+". "+practiceOptions.scoreNote()+"\\n"+').replaceAll('${q.number}','${practiceQuestionLabel(index)}'),
      renderResults:text=>append(text,"\nwindow.TS_TMUA_PRACTICE.resultNote(practiceOptions,els.question.querySelector('.result-card'));"),
      saveAttempt:text=>text.replace(/test_id\s*:\s*TEST\.id,/,'test_id:TEST.id,practice_settings:practiceOptions.metadata(),')
    });
    return js;
  });
  save(file,source);
}

// Full mocks use the same canonical-array controller as official papers. Reuse its bounded clocks and paper locking.
const official=read('full-official-2022.html');
const officialEngine=Array.from(official.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)).map(m=>m[1]).find(x=>x.includes('const questions'));
const controllerNames=['recordQuestionTime','resetPaperTimer','toggleFlag','updateFlagButton','startBreak','updateBreakTimer','nextQuestion','openNavigator','closeNavigator','jumpTo','renderQuestion','confirmSubmit','startExam','updateTimer','prevQuestion','generateNavigatorButtons','showBreakScreen','skipBreak','updateNavigatorButton'];
const replacements={};
functions(officialEngine,Object.fromEntries(controllerNames.map(name=>[name,text=>{replacements[name]=text;return text;}])));
for(const file of ['full-mock-01-all-topics.html','full-mock-02-all-topics.html']){
  let source=read(file);if(source.includes(marker))continue;
  source=injectHead(source);
  source=engine(source,'const questions',js=>{
    const id=file.replace('.html','');
    const init=`\n/* ${marker} */\nconst practiceOptions=window.TS_TMUA_PRACTICE.create('${id}',[20,20]);\nwindow.TS_TMUA_PRACTICE.mount(practiceOptions,document.querySelector('#instructions button[onclick="startExam()"]')||document.querySelector('#instructions button'));\nlet examStage='instructions',paperDeadline=0,breakDeadline=0;\nlet studentEmail='';\nconst practicePresentation={durationSeconds:()=>practiceOptions.durationSeconds(),positionOf:index=>practiceOptions.positionOf(index),questionAt:(paper,position)=>practiceOptions.questionAt(paper-1,position),prepare:()=>practiceOptions.start(),decorateQuestion:(container,index)=>window.TS_TMUA_PRACTICE.decorate(practiceOptions,container,index,Math.floor(index/20)+1)};\n`;
    js=init+js;
    const existing={};for(const [name,text]of Object.entries(replacements))if(!['recordQuestionTime','resetPaperTimer'].includes(name))existing[name]=text.replaceAll('window.TS_TMUA_PAST_PAPER','practicePresentation');
    js=functions(js,existing);
    js+= '\n'+replacements.recordQuestionTime+'\n'+replacements.resetPaperTimer.replaceAll('window.TS_TMUA_PAST_PAPER','practicePresentation');
    js=functions(js,{submitExam:text=>text.replace(/timeSpent\[current\]\s*\+=\s*\(Date\.now\(\)\s*-\s*lastTimestamp\)\s*\/\s*1000;/,"if(examStage!=='paper'||paper!==2)return;recordQuestionTime();examStage='complete';closeNavigator();")
      .replace(/test_id:\s*"[^"]+",/,'test_id: "'+id+'",\n    practice_settings:practiceOptions.metadata(),')
      .replace('${(i % 20) + 1}','${window.TS_TMUA_PRACTICE.questionLabel(practiceOptions,i)}')
      .replace('let paper1Analysis = "Paper 1 Analysis\\n";','let paper1Analysis = "Paper 1 Analysis\\n"+practiceOptions.summary()+". "+practiceOptions.scoreNote()+"\\n";')
      .replace('let paper2Analysis = "Paper 2 Analysis\\n";','let paper2Analysis = "Paper 2 Analysis\\n"+practiceOptions.summary()+". "+practiceOptions.scoreNote()+"\\n";')
      .replace('${score9Block}','${score9Block}<p>${practiceOptions.summary()}. ${practiceOptions.scoreNote()}</p>')});
    return js;
  });
  // The legacy save helper deliberately copies known fields into a new request.
  source=source.replace('test_id: String(opts.test_id || \'\').trim(),','test_id: String(opts.test_id || \'\').trim(),\n        practice_settings:opts.practice_settings,');
  save(file,source);
}

// Challenge has a separate full-test controller, with canonical identities retained in its arrays.
{
  const file='tmua-2024-2025-challenging-mock/index.html';let source=read(file);
  if(!source.includes(marker)){
    source=injectHead(source);
    source=engine(source,'const questions',js=>{
      js=js.replace(/(const TEST_ID=[^;]+;)/,`$1\n/* ${marker} */\nconst practiceOptions=window.TS_TMUA_PRACTICE.create(TEST_ID,[20,20]);\nwindow.TS_TMUA_PRACTICE.mount(practiceOptions,document.querySelector('#instructions button'));\n`);
      js=functions(js,{
        startExam:text=>text.replace('userAnswers.fill(null);','practiceOptions.start();userAnswers.fill(null);').replace('current=0','current=practiceOptions.questionAt(0,0)').replace('secondsRemaining=75*60','secondsRemaining=practiceOptions.durationSeconds()'),
        skipBreak:text=>text.replace('current=20','current=practiceOptions.questionAt(1,0)').replace('secondsRemaining=75*60','secondsRemaining=practiceOptions.durationSeconds()'),
        renderQuestion:text=>append(text,"\nwindow.TS_TMUA_PRACTICE.decorate(practiceOptions,container,current,paper);const position=practiceOptions.positionOf(current);counter.textContent='Q'+(position+1)+' of 20 (Paper '+paper+')';prevBtn.disabled=position===0;nextBtn.disabled=position===19;"),
        nextQuestion:"function nextQuestion(){if(!isExamActive())return;const position=practiceOptions.positionOf(current);if(position>=19)return;recordCurrentTime();current=practiceOptions.questionAt(paper-1,position+1);renderQuestion();}",
        prevQuestion:"function prevQuestion(){if(!isExamActive())return;const position=practiceOptions.positionOf(current);if(position<=0)return;recordCurrentTime();current=practiceOptions.questionAt(paper-1,position-1);renderQuestion();}",
        generateNavigatorButtons:text=>text.replace('const idx=offset+i','const idx=practiceOptions.questionAt(paper-1,i)'),
        updateNavigatorButton:text=>text.replaceAll('localQuestionNumber(index)','(practiceOptions.positionOf(index)+1)'),
        submitExam:text=>text.replace('test_id:TEST_ID,','test_id:TEST_ID,practice_settings:practiceOptions.metadata(),').replace('${localQuestionNumber(i)}','${window.TS_TMUA_PRACTICE.questionLabel(practiceOptions,i)}').replace('${score9Block(total,p1,p2)}','${score9Block(total,p1,p2)}<p>${practiceOptions.summary()}. ${practiceOptions.scoreNote()}</p>')
      });
      return js;
    });save(file,source);
  }
}

// Predictive v3 persists canonical answers/times separately from its display permutation.
{
  const file='tmua-2026-predictive-paper/index.html';let source=read(file);
  if(!source.includes(marker)){
    source=injectHead(source);
    source=engine(source,'const defaultPack',js=>{
      js=js.replace("const defaultPack = JSON.parse($('tmua-data').textContent);",`const defaultPack = JSON.parse($('tmua-data').textContent);\n/* ${marker} */\nlet practiceOptions=window.TS_TMUA_PRACTICE.create(defaultPack.id,[20,20]);\nfunction practicePosition(){return practiceOptions.positionOf(state.paperIndex*20+state.questionIndex);}\nfunction practiceCanonical(position,pi=state.paperIndex){return practiceOptions.questionAt(pi,position)-pi*20;}\nfunction practiceSequence(pi=state.paperIndex){return practiceOptions.sequence().slice(pi*20,pi*20+20).map(index=>index-pi*20);}\nfunction practiceQuestionLabel(pi,qi){return window.TS_TMUA_PRACTICE.questionLabel(practiceOptions,pi*20+qi);}\nfunction resetPracticeOptions(){practiceOptions=window.TS_TMUA_PRACTICE.create(pack.id,[20,20]);}\n`);
      js=functions(js,{
        freshState:text=>text.replace('return {','practiceOptions.start();return {practiceSettings:practiceOptions.metadata(),').replace('questionIndex:0','questionIndex:practiceOptions.questionAt(0,0)').replace('Date.now()+4500000','Date.now()+practiceOptions.durationSeconds()*1000'),
        readSaved:text=>text.replace('prefs={...prefs,...v.prefs};return s;','practiceOptions.restore(s.practiceSettings??null);s.practiceSettings=practiceOptions.metadata();prefs={...prefs,...v.prefs};return s;'),
        advancePaper:text=>text.replace('Math.min(4500,','Math.min(practiceOptions.durationSeconds(),').replace('state.questionIndex=0','state.questionIndex=practiceCanonical(0,1)').replace('at+4500000','at+practiceOptions.durationSeconds()*1000'),
        renderInstructions:text=>text.replace('150 minutes in total','<span data-tmua-practice-total></span> in total').replace('<ol class="instruction-list">','<div id="tmua-practice-settings"></div><ol class="instruction-list">').replace('<strong>75-minute</strong>','<strong data-tmua-practice-duration></strong>')
          .replace("$('backWelcome').onclick=renderWelcome;",`practiceOptions.mount('#tmua-practice-settings');const refreshPracticeTiming=()=>{document.querySelectorAll('[data-tmua-practice-duration]').forEach(el=>el.textContent=window.TS_TEST_OPTIONS.humanTime(practiceOptions.durationSeconds()));document.querySelectorAll('[data-tmua-practice-total]').forEach(el=>el.textContent=window.TS_TEST_OPTIONS.humanTime(practiceOptions.durationSeconds()*2));};$('tmua-practice-settings').addEventListener('change',refreshPracticeTiming);refreshPracticeTiming();$('backWelcome').onclick=renderWelcome;`),
        questionFooter:text=>text.replaceAll('state.questionIndex===0','practicePosition()===0').replaceAll('state.questionIndex===19','practicePosition()===19'),
        renderQuestion:text=>text.replaceAll('${state.questionIndex+1}','${practicePosition()+1}').replace("(state.questionIndex+1)+' of 20'","(practicePosition()+1)+' of 20'")
          .replace("if(navOpen)renderNavigator();","window.TS_TMUA_PRACTICE.decorate(practiceOptions,$('main'),state.paperIndex*20+state.questionIndex,state.paperIndex+1);if(navOpen)renderNavigator();"),
        navigate:text=>text.replace('const next=state.questionIndex+delta','const next=practicePosition()+delta').replace('jumpTo(next);','jumpTo(practiceCanonical(next));'),
        renderNavigator:text=>text.replace('pack.papers[state.paperIndex].questions.map((q,i)=>','practiceSequence().map((i,position)=>').replaceAll('${i+1}','${position+1}'),
        renderReview:text=>text.replace('paper.questions.map((q,i)=>','practiceSequence(pi).map((i,position)=>').replaceAll('${i+1}','${position+1}')
          .replace("$('reviewAll').onclick=()=>jumpTo(0)","$('reviewAll').onclick=()=>jumpTo(practiceCanonical(0))")
          .replace('jumpTo(state.answers[pi].findIndex(v=>v===null))','jumpTo(practiceSequence(pi).find(i=>state.answers[pi][i]===null))')
          .replace('jumpTo(state.flags[pi].findIndex(Boolean))','jumpTo(practiceSequence(pi).find(i=>state.flags[pi][i]))')
          .replace('starts the 75-minute Paper 2 timer immediately','starts the selected Paper 2 timer immediately')
          .replace("toast('Paper 2 has started. You have 75 minutes.')","toast('Paper 2 has started. You have '+window.TS_TEST_OPTIONS.humanTime(practiceOptions.durationSeconds())+'.')")
          .replace('Math.min(4500,','Math.min(practiceOptions.durationSeconds(),'),
        prediction:text=>text.replace('value:estimateRaw(raw,pack.predictor.table)','value:estimateRaw(practiceOptions.adjustedRaw(raw,40),pack.predictor.table)'),
        predictionMarkup:text=>text.replace('<div class="predictor-box">','<div class="predictor-box"><p class="small-note">${esc(practiceOptions.summary())}. ${esc(practiceOptions.scoreNote())}</p>'),
        renderResults:text=>text.replace('${i+1}</button>','${practiceQuestionLabel(reviewPaper,i)}</button>').replace('state=null;savedAttempt=null;reviewPaper=0;renderWelcome();','state=null;savedAttempt=null;reviewPaper=0;resetPracticeOptions();renderWelcome();'),
        renderWelcome:text=>text.replace('savedAttempt=null;renderWelcome();','savedAttempt=null;resetPracticeOptions();renderWelcome();'),
        buildReport:text=>text.replace('schemaVersion:1,attemptId:state.attemptId,','schemaVersion:1,practice_settings:practiceOptions.metadata(),practice_summary:practiceOptions.summary(),practice_score_note:practiceOptions.scoreNote(),attemptId:state.attemptId,').replace('id:q.id,number:i+1,','id:q.id,number:i+1,displayNumber:practiceOptions.positionOf(pi*20+i)+1,'),
        paperDetailsPlain:text=>text.replace('return ','return practiceOptions.summary()+". "+practiceOptions.scoreNote()+"\\n"+')
      });
      return js;
    });save(file,source);
  }
}

// Keep the printed instruction timings in step with the chosen allowance.
for(const file of [...topicFiles,'full-mock-01-all-topics.html','full-mock-02-all-topics.html','tmua-2024-2025-challenging-mock/index.html']){
  let source=read(file);
  source=source.split(/(<script(?:\s[^>]*)?>[\s\S]*?<\/script>)/g).map(part=>part.startsWith('<script')?part:part
    .replace(/(Time allowed:<\/strong>\s*)(1 hour 15 minutes)/g,'$1<span data-tmua-duration="paper">$2</span>')
    .replace(/>75 minutes</g,'><span data-tmua-duration="paper">75 minutes</span><')
    .replace(/>1 hour 15 minutes</g,'><span data-tmua-duration="paper">1 hour 15 minutes</span><')
    .replace(/>150 minutes</g,'><span data-tmua-duration="total">150 minutes</span><')).join('');
  // Do not nest markers on subsequent runs.
  while(/<span data-tmua-duration="(paper|total)"><span data-tmua-duration="\1">/.test(source))source=source.replace(/<span data-tmua-duration="(paper|total)"><span data-tmua-duration="\1">([^<]+)<\/span><\/span>/g,'<span data-tmua-duration="$1">$2</span>');
  save(file,source);
}
console.log('Integrated settings for all ten TMUA mock/topic/predictive tests.');

// Official papers retain their established question-and-option shuffle mappings.
for(const file of Array.from({length:8},(_,i)=>'full-official-'+(2016+i)+'.html').concat('full-specimen.html')){
  let source=read(file);
  if(source.includes('TS_TMUA_OFFICIAL_POLICY_V1'))continue;
  source=source.replace('</head>','<!-- TS_TMUA_OFFICIAL_POLICY_V1 -->\n<script src="/shared/practice-test-options.js?v=20261005-1"></script>\n</head>');
  source=source.replaceAll('tmua-past-paper-options.js?v=20261005-1','tmua-past-paper-options.js?v=20261005-2');
  source=source.replaceAll('tmua-score-conversions.js?v=20260806-1','tmua-score-conversions.js?v=20261005-1');
  source=source.replace('window.TS_TMUA_PAST_PAPER.summary() + "\\n"','window.TS_TMUA_PAST_PAPER.summary() + ". " + window.TS_TMUA_PAST_PAPER.scoreNote() + "\\n"');
  source=source.replace('<p>${window.TS_TMUA_PAST_PAPER.summary()}</p>','<p>${window.TS_TMUA_PAST_PAPER.summary()}. ${window.TS_TMUA_PAST_PAPER.scoreNote()}</p>');
  save(file,source);
}

for(const file of fs.readdirSync(base).filter(x=>x.endsWith('.html')).concat('tmua-2024-2025-challenging-mock/index.html')){
  let source=read(file);
  source=source.replaceAll("if(examStage!=='paper')return;recordQuestionTime();examStage='submitted';","if(examStage!=='paper'||paper!==2)return;recordQuestionTime();examStage='complete';closeNavigator();");
  source=source.replace(/tmua-past-paper-options\.js\?v=[^"']+/g,'tmua-past-paper-options.js?v=20261005-2');
  source=source.replaceAll('tmua-score-conversions.js?v=20260806-1','tmua-score-conversions.js?v=20261005-1');
  save(file,source);
}

// Deadline-capped time accounting excludes elapsed time after automatic submission.
for(const file of topicFiles){
  let source=read(file);
  source=engine(source,'const QUESTIONS',js=>functions(js,{
    recordCurrentTime:'function recordCurrentTime(){if(!state.started||state.submitted||!state.lastQuestionTimestamp)return;const now=Math.min(Date.now(),state.timerEndAt);state.timeSpent[state.current]+=Math.max(0,(now-state.lastQuestionTimestamp)/1000);state.lastQuestionTimestamp=now;}',
    startExam:text=>text.replaceAll('performance.now()','Date.now()'),
    goToQuestion:text=>(text.includes('if(!state.started||state.submitted)return;')?text:text.replace('{','{if(!state.started||state.submitted)return;')).replaceAll('performance.now()','Date.now()'),
    nextQuestion:'function nextQuestion(){if(!state.started||state.submitted)return;const position=practiceOptions.positionOf(state.current);if(position<QUESTIONS.length-1)goToQuestion(practiceOptions.questionAt(0,position+1));}',
    prevQuestion:'function prevQuestion(){if(!state.started||state.submitted)return;const position=practiceOptions.positionOf(state.current);if(position>0)goToQuestion(practiceOptions.questionAt(0,position-1));}'
  }));save(file,source);
}
{
  const file='tmua-2024-2025-challenging-mock/index.html';let source=read(file);
  source=engine(source,'const questions',js=>{
    if(!js.includes('let practicePaperDeadline='))js=js.replace('const practiceOptions=','let practicePaperDeadline=0;\nconst practiceOptions=');
    return functions(js,{
      startExam:text=>text.replace('{',"{if(document.getElementById('instructions').style.display==='none')return;").replaceAll("if(document.getElementById('instructions').style.display==='none')return;if(document.getElementById('instructions').style.display==='none')return;","if(document.getElementById('instructions').style.display==='none')return;").replaceAll('performance.now()','Date.now()'),
      renderQuestion:text=>text.replaceAll('performance.now()','Date.now()'),
      skipBreak:text=>text.replaceAll('performance.now()','Date.now()'),
      recordCurrentTime:'function recordCurrentTime(){const now=Math.min(Date.now(),practicePaperDeadline);if(isExamActive())timeSpent[current]+=Math.max(0,(now-lastTimestamp)/1000);lastTimestamp=now;}',
      startPaperTimer:'function startPaperTimer(){clearInterval(timerInterval);practicePaperDeadline=Date.now()+secondsRemaining*1000;renderTimer();timerInterval=setInterval(()=>{secondsRemaining=Math.max(0,Math.ceil((practicePaperDeadline-Date.now())/1000));renderTimer();if(secondsRemaining===0){clearInterval(timerInterval);recordCurrentTime();if(paper===1)showBreakScreen(true);else{automaticSubmission=true;submitExam();}}},1000);}',
      jumpTo:'function jumpTo(index){if(!isExamActive()||!Number.isInteger(index)||index<(paper-1)*20||index>=paper*20)return;recordCurrentTime();current=index;closeNavigator();renderQuestion();}'
    });
  });save(file,source);
}

// User events must enforce the deadline even while the browser throttles timer callbacks.
for(const file of topicFiles){
  let source=read(file);
  source=engine(source,'const QUESTIONS',js=>{
    if(!js.includes('function canEditPractice('))js+='\nfunction canEditPractice(){if(!state.started||state.submitted)return false;if(Date.now()>=state.timerEndAt){submitExam(true);return false;}return true;}\nfunction setPracticeAnswer(value){if(!canEditPractice())return false;state.userAnswers[state.current]=value;updateNavigator();return true;}\n';
    const guard=text=>text.includes('if(!canEditPractice())return;')?text:text.replace('{','{if(!canEditPractice())return;');
    return functions(js,{
      renderQuestion:text=>text.replace(/state\.userAnswers\[state\.current\]\s*=\s*event\.target\.value;\s*updateNavigator\(\);?/g,'setPracticeAnswer(event.target.value);'),
      goToQuestion:guard,nextQuestion:guard,prevQuestion:guard,toggleFlag:guard,openNavigator:guard,
      confirmSubmit:text=>guard(text).replace(/if\s*\(window\.confirm\(message\)\)\s*submitExam\(false\)/,'if(window.confirm(message)&&canEditPractice())submitExam(false)')
    });
  });save(file,source);
}
{
  const file='tmua-2024-2025-challenging-mock/index.html';let source=read(file);
  source=engine(source,'const questions',js=>{
    if(!js.includes('function canEditPractice('))js+='\nfunction expirePracticePaper(){if(!isExamActive())return;recordCurrentTime();clearInterval(timerInterval);secondsRemaining=0;renderTimer();if(paper===1)showBreakScreen(true);else{automaticSubmission=true;submitExam();}}\nfunction canEditPractice(){if(!isExamActive())return false;if(Date.now()>=practicePaperDeadline){expirePracticePaper();return false;}return true;}\nfunction setPracticeAnswer(value){if(!canEditPractice())return false;userAnswers[current]=value;updateNavigatorButton(current);return true;}\n';
    const guard=text=>text.includes('if(!canEditPractice())return;')?text:text.replace('{','{if(!canEditPractice())return;');
    return functions(js,{
      renderQuestion:text=>text.replace('userAnswers[current]=input.value;updateNavigatorButton(current);','setPracticeAnswer(input.value);'),
      nextQuestion:guard,prevQuestion:guard,jumpTo:guard,toggleFlag:guard,openNavigator:guard,
      startPaperTimer:'function startPaperTimer(){clearInterval(timerInterval);practicePaperDeadline=Date.now()+secondsRemaining*1000;renderTimer();timerInterval=setInterval(()=>{if(!canEditPractice())return;secondsRemaining=Math.max(0,Math.ceil((practicePaperDeadline-Date.now())/1000));renderTimer();},1000);}',
      confirmSubmit:text=>guard(text).replace(')){recordCurrentTime();showBreakScreen(false);',')){if(!canEditPractice())return;recordCurrentTime();showBreakScreen(false);').replace(')){recordCurrentTime();submitExam();',')){if(!canEditPractice())return;recordCurrentTime();submitExam();')
    });
  });save(file,source);
}
{
  const file='tmua-2026-predictive-paper/index.html';let source=read(file);
  source=engine(source,'const defaultPack',js=>functions(js,{
    prediction:text=>text.replace("label:'Reference score estimate'","label:practiceOptions.metadata().time_multiplier===1?'Reference score estimate':'Estimated standard-time equivalent'"),
    predictionMarkup:text=>text.replace('<h2>Practice score reference</h2>',"<h2>${practiceOptions.metadata().time_multiplier===1?'Practice score reference':'Estimated standard-time equivalent'}</h2>").replace("p.available?'Reference estimate · not difficulty-calibrated'","p.available?(practiceOptions.metadata().time_multiplier===1?'Reference estimate · not difficulty-calibrated':'Provisional extra-time adjustment · not validated')")
  }));save(file,source);
}
