// Check published content against the assessment model for its exam cohort.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {ibHarness} from './ib-component-harness.mjs';
const read = path => JSON.parse(readFileSync(path,'utf8'));
const sum = (rows, f) => rows.reduce((n,q)=>n+f(q),0);
const h=ibHarness(), content=h.load('lib/ib/content.ts');
const index=read('content/ib/content-index.json');
const seen=new Set();
const catalogue=h.load('lib/ib/catalog.ts');
for(const course of ['sl','hl']){
 for(const [subject,summary] of Object.entries(index.summaries[course])){
  if(subject.startsWith('math-'))continue;
  for(const c of summary.collections){
   const expected=catalogue.ibSyllabusSubtopics(subject,c.topicId,course);
   for(const topic of expected){
    const row=c.syllabus.find(x=>x.code===topic.code);
    assert(row?.count>0,subject+' '+course+' missing practice for '+topic.code+' '+topic.title);
   }
  }
 }
}
for (const c of h.model.IB_COLLECTIONS) {
  const rows=await content.getIbQuestions(c.id,'hl');
  for(const q of rows){
    assert(!seen.has(q.id),q.id);seen.add(q.id);
    assert.equal(index.questionCollections[q.id],c.id,q.id);
    if(!q.subject.startsWith('math-')){
      const lv=['sl','core'].includes(q.level)?'sl':'hl';
      assert(catalogue.ibSyllabusSubtopics(q.subject,q.topicId,lv).some(t=>t.code===q.syllabusCode),q.id+' has an unavailable syllabus code');
    }
    if(q.subject.startsWith('math-') && ['sl','core'].includes(q.level) && /^\d\.\d+$/.test(q.syllabusCode)){
      const [t,n]=q.syllabusCode.split('.').map(Number);
      const max=q.subject.startsWith('math-aa-')?[9,11,8,12,11]:[8,6,6,11,8];
      assert(n>0 && n<=max[t-1],q.id+' includes an AHL syllabus statement: '+q.syllabusCode);
    }
  }
}
assert.equal(seen.size,Object.keys(index.questionCollections).length);
assert.equal((await content.getIbQuestion('ib-aihl-na-702')).level,'ahl');
for(const id of ['ib-econ-ma-101','ib-econ-ma-102']){
  const q=await content.getIbQuestion(id,'sl');assert.equal(q.syllabusCode,'3.6');assert.equal(q.level,'sl');
}
const eq=await content.getIbQuestion('ib-chem-r2-829','sl');
assert.match(eq.stem,/reverse reaction.+0\.03125/);assert.match(eq.markScheme[0].steps[1].text,/32\.0/);
let count=0, questions=0;
for (const [subject,year] of Object.entries({aa:2026,ai:2026,biology:2025,chemistry:2025,physics:2026,economics:2022,psychology:2027})){
 const dir='content/ib/'+subject+'-mocks-'+year;
 const catalogs=subject==='ai'?[dir,'content/ib/ai-sl-mocks-2026']:[dir];
 for(const selected of catalogs) for(const group of read(selected+'/catalog.json').filter(g=>g.status==='published')){
  for(const meta of (group.papers??[group]).filter(m=>m.status==='published')){
   const p=read(selected+'/papers/'+meta.id+'.json'), n=Number(meta.paper), hl=meta.course==='hl', q=p.questions;
   assert.equal(p.course,meta.course);assert.equal(p.paper,meta.paper);
   let minutes,marks,calc,attempt=sum(q,x=>x.marks);
   if(subject==='aa'||subject==='ai'){
    assert(n===1||n===2||(hl&&n===3));minutes=hl?(n===3?75:120):90;marks=hl?(n===3?55:110):80;calc=subject==='ai'||n!==1;
    if(n===3)assert.equal(q.length,2);
    if(subject==='aa'&&n<3)assert.deepEqual([...new Set(q.map(x=>x.section))],['A','B']);
   }else if(['physics','chemistry','biology'].includes(subject)){
    assert(n===1||n===2);calc=true;minutes=hl?(n===1?120:150):90;
    if(n===1){
     const counts=subject==='physics'?(hl?[40,20]:[25,20]):(hl?[40,35]:[30,25]);
     marks=counts[0]+counts[1];const a=q.filter(x=>x.section==='1A'), b=q.filter(x=>x.section==='1B');
     assert.equal(a.length,counts[0]);assert(a.every(x=>x.marks===1&&x.options.length===4));assert.equal(sum(b,x=>x.marks),counts[1]);assert.equal(a.length+b.length,q.length);
    }else{
     marks=hl?(subject==='biology'?80:90):50;
     if(subject==='biology'){
      const opt=q.filter(x=>x.sectionB);assert.equal(opt.length,hl?3:2);assert(opt.every(x=>x.marks===16));
      const compulsory=sum(q.filter(x=>!x.sectionB),x=>x.marks);assert.equal(compulsory,hl?48:34);attempt=compulsory+16*(hl?2:1);
     }
    }
   }else if(subject==='economics'){
    minutes=n===1?75:105;marks=[25,40,60][n-1];calc=n!==1;
    assert.deepEqual(q.map(x=>x.marks),n===1?[25,25,25]:n===2?[40,40]:[30,30]);
    if(n===1)for(const x of q)assert.deepEqual(x.parts.map(y=>y.marks),[10,15]);
    if(n===3)assert(hl);else attempt=q[0].marks;
   }else{
    minutes=n===3?105:90;marks=n===3?30:35;
    assert.deepEqual(q.map(x=>x.marks),n===1?[4,4,6,6,15,15]:n===2?[4,4,6,6,15]:[3,6,6,15]);
    if(n===1)attempt-=15;if(n===3){assert(hl);assert(p.resources.length>=4);}
   }
   for(const spec of [p,meta]){assert.equal(spec.minutes,minutes,meta.id);assert.equal(spec.marks,marks,meta.id);if(calc!==undefined)assert.equal(spec.calculator,calc,meta.id);}
   assert.equal(attempt,marks,meta.id+' attempted marks');count++;questions+=q.length;
  }
 }
}
for (const m of read('content/ib/practice-2027/ai-catalog.json')) {
 const p=read('content/ib/practice-2027/ai/'+m.id+'.json');
 assert.equal(p.questions.length,2);assert.equal(p.minutes,75);assert.equal(p.marks,55);
 assert.equal(sum(p.questions,q=>q.marks),55);count++;questions+=p.questions.length;
}
for (const m of read('content/ib/practice-2027/business-catalog.json')) {
 const p=read('content/ib/practice-2027/business/'+m.id+'.json');
 const options=p.questions.filter(q=>q.optional);
 assert.equal(options.length,p.number===3?0:2);
 if(options.length)assert.equal(options[0].marks,options[1].marks);
 assert.equal(sum(p.questions.filter(q=>!q.optional),q=>q.marks)+(options[0]?.marks??0),p.marks);
 assert.deepEqual([p.minutes,p.marks],p.number===1?[90,30]:p.number===3?[75,25]:p.course==='sl'?[90,40]:[105,50]);
 count++;questions+=p.questions.length;
}
assert(count>0);console.log(JSON.stringify({publishedQuestions:seen.size,publishedPapers:count,mockQuestionAppearances:questions,assessmentModel:'exams in 2027 and 2028'}));
