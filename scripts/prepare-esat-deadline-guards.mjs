import fs from 'node:fs';
import path from 'node:path';

// Keep standalone controllers' absolute deadlines and action guards in step.
const root=path.join(process.cwd(),'public/esat-practice-tests/tests');
const folders=fs.readdirSync(root).filter(folder=>/^(?:esat-mock-(?:0[1-4]|13)|esat-.*-level-[012]|esat-recall-2024-25-.*)$/.test(folder));
for(const folder of folders){
  const file=path.join(root,folder,'index.html');
  let html=fs.readFileSync(file,'utf8');
  if(html.includes('TS_ESAT_DEADLINE_GUARD_V1'))continue;
  const newline=html.includes('\r\n')?'\r\n':'\n';html=html.replace(/\r\n/g,'\n');
  const replace=(from,to)=>{
    if(!(typeof from==='string'?html.includes(from):from.test(html)))throw new Error(folder+': missing deadline transform '+from);
    html=html.replace(from,to);
  };
  if(folder.includes('recall-')){
    replace(/function commitVisibleTime\(\)\{[^\n]+\}/,`// TS_ESAT_DEADLINE_GUARD_V1: actions sync expiry before changing canonical answers.
function commitVisibleTime(){
  const now=Date.now(),end=Math.min(now,sectionDeadline||now);
  if(!window.__ESAT_SUBMIT_DONE&&!breakDeadline&&document.getElementById("exam-interface").style.display!=="none")timeSpent[current]+=Math.max(0,end-lastTimestamp)/1000;
  lastTimestamp=now;
}
function ensureSectionOpen(){
  if(window.__ESAT_SUBMIT_DONE||breakDeadline||document.getElementById("exam-interface").style.display==="none")return false;
  if(Date.now()>=sectionDeadline){updateTimer();return false;}
  return true;
}`);
    replace('function startSectionTimer(){ clearInterval(timerInterval); updateTimer(); timerInterval=setInterval(updateTimer,250); }','function startSectionTimer(){ clearInterval(timerInterval); updateTimer(); if(!breakDeadline&&!window.__ESAT_SUBMIT_DONE)timerInterval=setInterval(updateTimer,250); }');
    replace('function updateTimer(){','function updateTimer(){\n  if(window.__ESAT_SUBMIT_DONE||breakDeadline||document.getElementById("exam-interface").style.display==="none")return;');
    replace('()=>{userAnswers[current]=r.value;', '()=>{if(!ensureSectionOpen())return;userAnswers[current]=r.value;');
    for(const name of ['goTo','prevQuestion','nextQuestion','toggleFlag','openNavigator','confirmSubmit'])replace(new RegExp('function '+name+'\\(([^)]*)\\)\\{'),'function '+name+'($1){ if(!ensureSectionOpen())return;');
    replace('function showBreakScreen(){','function showBreakScreen(){\n  if(breakDeadline||window.__ESAT_SUBMIT_DONE)return;\n  commitVisibleTime();clearInterval(timerInterval);closeNavigator();');
    replace('function beginNextSection(){','function beginNextSection(){ if(!breakDeadline||window.__ESAT_SUBMIT_DONE)return;');
    replace('if(window.__ESAT_SUBMIT_DONE)return;window.__ESAT_SUBMIT_DONE=true;clearInterval(timerInterval);clearInterval(breakInterval);commitVisibleTime();','if(window.__ESAT_SUBMIT_DONE)return;commitVisibleTime();window.__ESAT_SUBMIT_DONE=true;clearInterval(timerInterval);clearInterval(breakInterval);closeNavigator();');
  }else{
    replace('function updateTimer() {',`// TS_ESAT_DEADLINE_GUARD_V1: timer refresh frequency must never extend the allowance.
let sectionDeadline = 0;
let esatStage = "instructions";
function commitVisibleTime() {
  const now = Date.now();
  if (esatStage === "section") timeSpent[current] += Math.max(0, Math.min(now, sectionDeadline) - lastTimestamp) / 1000;
  lastTimestamp = now;
}
function ensureSectionOpen() {
  if (esatStage !== "section" || window.__ESAT_SUBMIT_DONE) return false;
  if (Date.now() >= sectionDeadline) { updateTimer(); return false; }
  return true;
}
function updateTimer() {
  if (esatStage !== "section" || window.__ESAT_SUBMIT_DONE) return;
  secondsRemaining = Math.max(0, Math.ceil((sectionDeadline - Date.now()) / 1000));`);
    replace(/timeSpent\[current\] \+= \(Date\.now\(\) - lastTimestamp\) \/ 1000;/g,'commitVisibleTime();');
    replace('  secondsRemaining--;','');
    replace(/(  secondsRemaining = practiceSettings.durationSeconds\(\);\n  timerDisplay.textContent = formatTime\(secondsRemaining\);\n  lastTimestamp = Date.now\(\);)/g,'$1\n  sectionDeadline = lastTimestamp + secondsRemaining * 1000;\n  esatStage = "section";');
    replace('input.addEventListener("change", () => {','input.addEventListener("change", () => {\n      if (!ensureSectionOpen()) return;');
    for(const name of ['nextQuestion','prevQuestion','toggleFlag','openNavigator','confirmSubmit','jumpTo'])replace(new RegExp('function '+name+'\\(([^)]*)\\) \\{'),'function '+name+'($1) {\n  if (!ensureSectionOpen()) return;');
    replace('function showBreakScreen() {','function showBreakScreen() {\n  if (esatStage !== "section") return;\n  commitVisibleTime();\n  esatStage = "break";\n  closeNavigator();');
    replace('function updateBreakTimer() {','function updateBreakTimer() {\n  if (esatStage !== "break") return;');
    replace('function skipBreak() {','function skipBreak() {\n  if (esatStage !== "break" || window.__ESAT_SUBMIT_DONE) return;');
    replace('  window.__ESAT_SUBMIT_DONE = true;','  commitVisibleTime();\n  esatStage = "complete";\n  closeNavigator();\n  window.__ESAT_SUBMIT_DONE = true;');
  }
  fs.writeFileSync(file,newline==='\r\n'?html.replace(/\n/g,'\r\n'):html);
}
console.log(`Checked absolute deadlines and action guards for ${folders.length} standalone ESAT clients.`);
