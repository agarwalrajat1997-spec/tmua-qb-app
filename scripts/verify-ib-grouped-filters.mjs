import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { renderToStaticMarkup as render } from 'react-dom/server';
import { parseDocument } from 'htmlparser2';
import { ibHarness } from './ib-component-harness.mjs';
const seed=ibHarness(), catalog=seed.load('lib/ib/catalog.ts');
const questions=Object.keys(catalog.IB_COURSES).flatMap(subject=>readdirSync('content/ib/'+subject).filter(f=>f.endsWith('.json')).flatMap(f=>JSON.parse(readFileSync(`content/ib/${subject}/${f}`,'utf8')))).filter(q=>q.status==='published');
const auth=[],h=ibHarness({questions,onAuth:destination=>auth.push(destination)});
const {ibTopicGroups,questionInTopicGroup}=h.load('lib/ib/topic-groups.ts');
const {queryValues,selectedValues}=h.load('lib/ib/question-filters.ts');
const order=h.load('lib/ib/practice-order.ts').variedPracticeOrder;
const bank=h.load('app/ib/question-bank/[collection]/page.tsx').default;
const args=(collection,query={})=>({params:Promise.resolve({collection}),searchParams:Promise.resolve(query)});
function elements(html,predicate){const found=[];function visit(node){if(predicate(node))found.push(node);for(const child of node.children??[])visit(child);}visit(parseDocument(html));return found;}
const ids=html=>elements(html,node=>node.name==='article'&&node.attribs.class==='questionCard').map(node=>node.attribs.id);
const inputValues=(html,name)=>elements(html,node=>node.name==='input'&&node.attribs.name===name&&'checked'in node.attribs).map(node=>node.attribs.value);
const report=[];
for(const subject of Object.keys(catalog.IB_COURSES))for(const course of catalog.ibHasCourseChoice(subject)?['sl','hl']:['hl']){
  const available=questions.filter(q=>q.subject===subject&&h.model.questionAvailableForCourse(q,course));
  const collections=h.model.IB_COLLECTIONS.filter(c=>c.subject===subject);let before=0,after=0;
  for(const collection of collections){
    const items=available.filter(q=>q.collectionId===collection.id),groups=ibTopicGroups(collection,items,course);
    const original=catalog.ibIsMathSubject(subject)?new Set(items.map(q=>q.subtopic)).size:catalog.ibSyllabusSubtopics(subject,collection.topicId,course).length;
    before+=original;after+=groups.length;
    assert.ok(groups.length>0,collection.id);
    assert.equal(new Set(groups.map(g=>g.id)).size,groups.length,'unique category IDs');
    assert.ok(groups.every(g=>!g.id.startsWith('syllabus:')&&!g.id.startsWith('subtopic:')),'all current content explicitly curated');
    for(const q of items)assert.equal(groups.filter(g=>questionInTopicGroup(q,g)).length,1,`${q.id} belongs to exactly one category`);
    assert.equal(groups.reduce((sum,g)=>sum+g.count,0),items.length,'category counts preserve every question');
    if(!catalog.ibIsMathSubject(subject))assert.deepEqual(Array.from(groups.flatMap(g=>g.syllabusCodes)).sort(),Array.from(catalog.ibSyllabusSubtopics(subject,collection.topicId,course),t=>t.code).sort(),'syllabus coverage, including sections with no questions');
    const chosen=groups.slice(0,2),query={course,category:chosen.map(g=>g.id),difficulty:['easy','hard']};
    const expected=items.filter(q=>chosen.some(g=>questionInTopicGroup(q,g))&&['easy','hard'].includes(q.difficulty));
    const sorted=subject==='math-aa-sl'||subject==='math-ai-sl'?order(expected):expected;
    const html=render(await bank(args(collection.id,query)));
    assert.deepEqual(ids(html),Array.from(sorted.slice(0,8),q=>q.id),'OR within category/difficulty and AND across filters');
    assert.deepEqual(inputValues(html,'category'),Array.from(chosen,g=>g.id));
    assert.deepEqual(inputValues(html,'difficulty'),['easy','hard']);
    assert.equal(elements(html,node=>node.name==='select').length,0,'no single-select filters');
    assert.ok(!html.includes('Apply filters'),'all courses apply filters automatically');
    if(expected.length>8){
      const link=elements(html,node=>node.name==='a'&&node.attribs.href?.includes('page=2'))[0];assert.ok(link,'pagination');
      const url=new URL(link.attribs.href,'https://example.invalid');assert.deepEqual(url.searchParams.getAll('category'),query.category);assert.deepEqual(url.searchParams.getAll('difficulty'),query.difficulty);
      assert.deepEqual(ids(render(await bank(args(collection.id,{...query,page:'2'})))),Array.from(sorted.slice(8,16),q=>q.id),'pagination preserves union');
    }
  }
  assert.ok(after/before>=.43&&after/before<=.57,`${subject}/${course}: ${before} -> ${after} is approximately half`);
  report.push(`${catalog.ibCourseLabel(subject,course)}: ${before} -> ${after} (${available.length} questions)`);
  const collection=collections.find(c=>available.some(q=>q.collectionId===c.id));
  const items=available.filter(q=>q.collectionId===collection.id);
  const query={course,difficulty:['easy','hard'],level:course==='sl'?[catalog.ibCoreLevel(subject)]:[catalog.ibCoreLevel(subject),'ahl']};
  if(catalog.ibIsMathSubject(subject)){query.calculator=['yes','no'];query.style=['short-response','extended-response'];}
  else if(catalog.ibIsHumanitiesSubject(subject)){query.style=['paper-1','paper-2'];}
  else query.type=['multiple-choice','data-based'];
  const expected=items.filter(q=>query.difficulty.includes(q.difficulty)&&(!query.style||query.style.includes(q.examStyle))&&(!query.type||query.type.includes(q.questionType)));
  const sorted=subject==='math-aa-sl'||subject==='math-ai-sl'?order(expected):expected;
  assert.deepEqual(ids(render(await bank(args(collection.id,query)))),Array.from(sorted.slice(0,8),q=>q.id),'combined response/type/level/calculator facets');
  // Legacy syllabus and raw-subtopic bookmarks stay exact, including repeated values.
  const legacy=catalog.ibIsMathSubject(subject)?{subtopic:[...new Set(items.map(q=>q.subtopic))].slice(0,2)}:{syllabus:[...new Set(items.map(q=>q.syllabusCode))].slice(0,2)};
  const legacyItems=items.filter(q=>legacy.subtopic?.includes(q.subtopic)||legacy.syllabus?.includes(q.syllabusCode));
  const legacyOrder=subject==='math-aa-sl'||subject==='math-ai-sl'?order(legacyItems):legacyItems;
  assert.deepEqual(ids(render(await bank(args(collection.id,{course,...legacy})))),Array.from(legacyOrder.slice(0,8),q=>q.id));
}
// Sign-in returns preserve repeated filters. Unknown and duplicate values cannot create extra options.
const blocked=ibHarness({questions:[],user:null,onAuth:destination=>auth.push(destination)});
await assert.rejects(()=>blocked.load('app/ib/question-bank/[collection]/page.tsx').default(args('physics-space-time-motion',{course:'sl',category:['motion-forces-and-momentum','work-energy-and-power'],difficulty:['easy','hard'],type:['multiple-choice','structured'],page:'2'})),/AUTH_REQUIRED/);
const login=new URL(auth.at(-1),'https://example.invalid');assert.deepEqual(login.searchParams.getAll('difficulty'),['easy','hard']);assert.equal(login.searchParams.getAll('category').length,2);assert.equal(login.searchParams.getAll('type').length,2);assert.equal(login.searchParams.get('page'),'2');
assert.deepEqual(Array.from(selectedValues(['easy','forged','easy','hard'],['easy','medium','hard'])),['easy','hard']);assert.equal(queryValues(Array.from({length:200},(_,i)=>String(i))).length,100);
const slHtml=render(await bank(args('physics-space-time-motion',{course:'sl',category:['syllabus:A.4'],level:['ahl'],type:['forged']})));
assert.ok(ids(slHtml).every(id=>questions.find(q=>q.id===id).level==='core'),'invalid SL filters cannot expose HL records');
const noResults=render(await bank(args('physics-space-time-motion',{q:'UNMATCHABLE-QUERY-XYZ',difficulty:['easy','hard']})));assert.equal(ids(noResults).length,0);assert.match(noResults,/No questions match these filters/);
// Removing one applied category preserves the other facets and category choices.
const removeHtml=render(await bank(args('physics-space-time-motion',{category:['motion-and-relativity','forces-momentum-and-rotation'],difficulty:['easy','hard']})));
const removeLink=elements(removeHtml,node=>node.name==='a'&&node.attribs['aria-label']==='Remove Motion and relativity')[0];assert.ok(removeLink);
const removed=new URL(removeLink.attribs.href,'https://example.invalid');assert.deepEqual(removed.searchParams.getAll('category'),['forces-momentum-and-rotation']);assert.deepEqual(removed.searchParams.getAll('difficulty'),['easy','hard']);
// A selected HL category maps to its relevant SL category without retaining AHL-only values.
const slSwitch=elements(removeHtml,node=>node.name==='a'&&node.attribs.href?.startsWith('/ib/question-bank/physics-space-time-motion?course=sl'))[0];assert.ok(slSwitch);
const switched=new URL(slSwitch.attribs.href,'https://example.invalid');assert.deepEqual(switched.searchParams.getAll('category'),['motion-forces-and-momentum']);assert.deepEqual(switched.searchParams.getAll('difficulty'),['easy','hard']);
console.log(report.join('\n'));
console.log('Grouped filters passed: all 45 collections, every course, complete unique question/syllabus coverage, category counts, multiselect unions/intersections, legacy links, pagination, sign-in returns, invalid inputs and SL boundaries. No live account or writes.');
