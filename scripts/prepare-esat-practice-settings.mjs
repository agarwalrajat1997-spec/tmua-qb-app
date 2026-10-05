import fs from 'node:fs';
import path from 'node:path';

// Idempotent maintenance transform for the committed standalone ESAT test clients.
const root = path.join(process.cwd(), 'public/esat-practice-tests/tests');
const folders = fs.readdirSync(root).filter(folder => /^(?:esat-mock-(?:0[1-4]|13)|esat-.*-level-[012]|esat-recall-2024-25-.*)$/.test(folder));
const helper = '/shared/practice-test-options.js?v=20261005-1';
const bridge = `
// TS_ESAT_PRACTICE_SETTINGS_V1: display order never changes canonical answer identities.
const practiceSettings = window.TS_TEST_OPTIONS.create({testId,sectionSizes:[27,27,27],baseSeconds:2400,programme:"ESAT"});
window.TS_ESAT_PRACTICE_SETTINGS = practiceSettings;
practiceSettings.mount("#ts-practice-settings");
function updatePracticeTiming(){
  document.querySelectorAll("[data-esat-duration]").forEach(el=>{el.textContent=String(practiceSettings.durationSeconds()/60*(el.dataset.esatDuration==="total"?3:1))+" minutes";});
}
document.getElementById("ts-practice-settings").addEventListener("change",updatePracticeTiming);
updatePracticeTiming();
function esatQuestionReference(index){
  const original=index%27+1,shown=practiceSettings.positionOf(index)+1;
  return practiceSettings.metadata().order==="randomised"?"Original Q"+original+" (shown as Q"+shown+")":"Q"+original;
}
function decoratePracticeQuestion(){
  const heading=container.querySelector(".question-number");
  if(heading)heading.textContent="Question "+(practiceSettings.positionOf(current)+1)+(practiceSettings.metadata().order==="randomised"?" · Original Q"+(current%27+1):"");
}
function practiceResultNote(){return '<p class="ts-practice-result-note">'+practiceSettings.summary()+'</p><p>'+practiceSettings.scoreNote()+'</p>';}
`;

for (const folder of folders) {
  const file = path.join(root, folder, 'index.html');
  let html = fs.readFileSync(file, 'utf8');
  if (html.includes('TS_ESAT_PRACTICE_SETTINGS_V1')) continue;
  const newline = html.includes('\r\n') ? '\r\n' : '\n';
  html = html.replace(/\r\n/g, '\n');
  const recall = folder.includes('recall-');
  const replace = (from, to, required = true) => {
    if (required && !(typeof from === 'string' ? html.includes(from) : from.test(html))) throw new Error(folder + ': missing transform ' + from);
    html = html.replace(from, to);
  };
  replace('</head>', `<script src="${helper}"></script>\n</head>`);
  replace(/(<h2 id="test-title">[^<]*<\/h2>)/, '$1\n<div id="ts-practice-settings"></div>');
  // Change timing copy only in the instruction markup, never inside question content.
  const instructionEnd = html.indexOf('<div id="exam-interface">');
  html = html.slice(0, instructionEnd).replace(/2 hours\s*[-–—]\s*three sections of 40 minutes each/g, '<span data-esat-duration="total">120 minutes</span> - three sections of <span data-esat-duration="section">40 minutes</span> each').replace(/(?<![>\w])40 minutes(?=<\/td>)/g, '<span data-esat-duration="section">40 minutes</span>') + html.slice(instructionEnd);
  replace(/(const testId\s*=\s*"[^"]+";)/, '$1\n' + bridge);
  replace(/secondsRemaining = SECTION_SECONDS/g, 'secondsRemaining = practiceSettings.durationSeconds()', !recall);
  replace(/Date\.now\(\)\+SECTION_SECONDS\*1000/g, 'Date.now()+practiceSettings.durationSeconds()*1000', recall);
  replace(/: SECTION_SECONDS;/g, ': practiceSettings.durationSeconds();', false);
  replace(/current-currentSectionStart\(\)\+1/g, 'practiceSettings.positionOf(current)+1', recall);
  replace(/current - currentSectionStart\(\) \+ 1/g, 'practiceSettings.positionOf(current) + 1', !recall);
  replace(/container\.innerHTML\s*=\s*questions\[current\];/g, '$& decoratePracticeQuestion();');
  replace(/current===currentSectionStart\(\)/g, 'practiceSettings.positionOf(current)===0', recall);
  replace(/current === currentSectionStart\(\)/g, 'practiceSettings.positionOf(current) === 0', !recall);
  replace(/current===currentSectionEnd\(\)/g, 'practiceSettings.positionOf(current)===SECTION_SIZE-1', recall);
  replace(/current === currentSectionEnd\(\)/g, 'practiceSettings.positionOf(current) === SECTION_SIZE - 1', !recall);
  if (recall) {
    replace('function restoreActive(s){', 'function restoreActive(s){\n  practiceSettings.restore(s.practice_settings); updatePracticeTiming();');
    replace('restoreActive(saved);', 'try{restoreActive(saved);}catch(error){alert(error.message);return;}');
    replace('clearActive(); studentName=', 'practiceSettings.start(); clearActive(); studentName=');
    replace('sectionIndex=0; current=0;', 'sectionIndex=0; current=practiceSettings.questionAt(0,0);');
    replace('current=currentSectionStart();', 'current=practiceSettings.questionAt(sectionIndex,0);');
    replace('if(current>currentSectionStart())goTo(current-1);', 'if(practiceSettings.positionOf(current)>0)goTo(practiceSettings.questionAt(sectionIndex,practiceSettings.positionOf(current)-1));');
    replace('if(current<currentSectionEnd()){ goTo(current+1); return; }', 'if(practiceSettings.positionOf(current)<SECTION_SIZE-1){ goTo(practiceSettings.questionAt(sectionIndex,practiceSettings.positionOf(current)+1)); return; }');
    replace('const a=currentSectionStart()+i,b=', 'const a=practiceSettings.questionAt(sectionIndex,i),b=');
    replace('${i-currentSectionStart()+1}', '${practiceSettings.positionOf(i)+1}');
    replace('version:3,testId,studentName', 'version:3,testId,practice_settings:practiceSettings.metadata(),studentName');
    replace('const payload={testId,attemptNumber', 'const payload={testId,practice_settings:practiceSettings.metadata(),attemptNumber');
    replace('const payload={test_id:String', 'const payload={practice_settings:practiceSettings.metadata(),test_id:String');
    replace('return window.TS_SAVE_ATTEMPT({test_id:', 'return window.TS_SAVE_ATTEMPT({practice_settings:practiceSettings.metadata(),test_id:');
    replace('<td>${i-start+1}</td>', '<td>${esatQuestionReference(i)}</td>');
    replace('Q.${i-start+1} Correct:', '${esatQuestionReference(i)} Correct:');
  } else {
    replace('function startExam() {', 'function startExam() {\n  practiceSettings.start();');
    replace('sectionIndex = 0;\n  current = 0;', 'sectionIndex = 0;\n  current = practiceSettings.questionAt(0, 0);');
    replace('current = sectionIndex * SECTION_SIZE;', 'current = practiceSettings.questionAt(sectionIndex, 0);');
    replace('  current++;', '  current = practiceSettings.questionAt(sectionIndex, practiceSettings.positionOf(current) + 1);');
    replace('  current--;', '  current = practiceSettings.questionAt(sectionIndex, practiceSettings.positionOf(current) - 1);');
    replace('const actualIndex = offset + i;', 'const actualIndex = practiceSettings.questionAt(sectionIndex, i);');
    replace('const label = index - sectionStart + 1;', 'const label = practiceSettings.positionOf(index) + 1;');
    replace('    testId,\n    attemptNumber,', '    testId,\n    practice_settings: practiceSettings.metadata(),\n    attemptNumber,');
    replace('var payload = {\n        test_id:', 'var payload = {\n        practice_settings: practiceSettings.metadata(),\n        test_id:');
    replace('return window.TS_SAVE_ATTEMPT({\n    test_id:', 'return window.TS_SAVE_ATTEMPT({\n    practice_settings: practiceSettings.metadata(),\n    test_id:');
    replace('<td>${i - start + 1}</td>', '<td>${esatQuestionReference(i)}</td>');
    replace('Q.${i - start + 1} Correct:', '${esatQuestionReference(i)} Correct:');
  }
  replace('<h1>Exam Completed</h1>', '<h1>Exam Completed</h1>${practiceResultNote()}');
  // Every supported email template renders paper1; put the settings and estimate caveat there.
  replace(/(let out\s*=\s*`)(\$\{title\} Analysis)/, '$1${practiceSettings.summary()}\\n${practiceSettings.scoreNote()}\\n$2');
  fs.writeFileSync(file, newline === '\r\n' ? html.replace(/\n/g, '\r\n') : html);
}
for (const folder of fs.readdirSync(root).filter(folder => folder.startsWith('esat-october-2026-'))) {
  const file = path.join(root, folder, 'index.html');
  let html = fs.readFileSync(file, 'utf8');
  if (!html.includes(helper)) html = html.replace('</head>', `<script src="${helper}"></script></head>`);
  html = html.replace(/esat-october-2026-runtime\.js\?v=[^"']+/g, 'esat-october-2026-runtime.js?v=20261005-1').replace(/esat-october-2026-portal\.js\?v=[^"']+/g, 'esat-october-2026-portal.js?v=20261005-1');
  fs.writeFileSync(file, html);
}
for (const folder of folders) {
  const file = path.join(root,folder,'index.html');
  let html = fs.readFileSync(file,'utf8');
  html = html.replace(/esat-score-estimates\.js\?v=[^"']+/g,'esat-score-estimates.js?v=20261005-1');
  const instructionEnd=html.indexOf('<div id="exam-interface">');
  html=html.slice(0,instructionEnd).replace(/>40 minutes<\/td>/g,'><span data-esat-duration="section">40 minutes</span></td>')+html.slice(instructionEnd);
  html=html.replace(/(\n  secondsRemaining = practiceSettings.durationSeconds\(\);)(?!\r?\n  timerDisplay.textContent)/g,'$1\n  timerDisplay.textContent = formatTime(secondsRemaining);');
  html=html.replace('function persistActive(){\n  try{','function persistActive(){\n  if(window.__ESAT_SUBMIT_DONE)return;\n  try{').replace('function persistActive(){\r\n  try{','function persistActive(){\r\n  if(window.__ESAT_SUBMIT_DONE)return;\r\n  try{');
  if(folder.includes('recall-') && !html.includes('TS_ESAT_RESTORE_BREAK_V1')) {
    html=html.replace('  document.getElementById("instructions").style.display="none";', `  document.getElementById("instructions").style.display="none";
  // TS_ESAT_RESTORE_BREAK_V1: submitted modules remain locked across a break reload.
  if(breakDeadline){
    document.getElementById("exam-interface").style.display="none";
    document.getElementById("break-screen").style.display="flex";
    document.getElementById("break-title").textContent=\`End of \${sectionNames[sectionIndex]}\`;
    document.getElementById("break-copy").textContent=\`You can take a 5-minute break before starting \${sectionNames[sectionIndex+1]}.\`;
    lastTimestamp=Date.now(); clearInterval(breakInterval); updateBreakTimer();
    if(breakDeadline)breakInterval=setInterval(updateBreakTimer,250);
    persistActive(); return;
  }`);
  }
  if (!html.includes('window.__ESAT_STARTED = true')) {
    html = html.replace(/function startExam\(\) \{/, 'function startExam() {\n  if (window.__ESAT_STARTED) return;\n  window.__ESAT_STARTED = true;');
    html = html.replace(/function startExam\(\)\{/, 'function startExam(){\n  if (window.__ESAT_STARTED) return;');
    if (folder.includes('recall-')) html = html.replace('  document.getElementById("instructions").style.display="none";', '  window.__ESAT_STARTED = true;\n  document.getElementById("instructions").style.display="none";');
  }
  fs.writeFileSync(file,html);
}
console.log(`Prepared ${folders.length} legacy/recall and 6 October ESAT clients.`);
await import('./prepare-esat-deadline-guards.mjs');
