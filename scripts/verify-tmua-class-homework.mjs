import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {Parser} from 'htmlparser2';

const html=readFileSync('public/tmua-classes/index.html','utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
assert.ok(script,'Actual classes renderer must exist');
const pdf='/tmua-classes/homework/TMUA_Algebra_Easier_Companion_Full_Pack.pdf';
const meeting={id:'ac00e6a5-5d96-458d-b233-19ebf8166b1f',title:'TMUA Algebra Essentials',batch_name:'TMUA Group',
  starts_at:'2026-10-31T10:30:00Z',ends_at:'2026-10-31T12:00:00Z',timezone:'Europe/London',
  description:`Algebra practice. [Homework: Algebra Easier Companion - Full Pack](${pdf})`,
  recording_url:null,recording_notes:'This session was not recorded.',computed_status:'completed'};
const next={...meeting,id:'next',title:'Next live class',description:'Existing live description',recording_notes:null,
  computed_status:'scheduled',starts_at:'2026-11-01T11:30:00Z',ends_at:'2026-11-01T13:00:00Z',zoom_url:'https://example.invalid/zoom'};
const later={...next,id:'later',title:'Later same-batch class',starts_at:'2026-11-08T11:30:00Z'};
const recording={...meeting,id:'recorded',title:'Existing recording',description:'Existing recording description',
  recording_notes:'Existing notes',recording_url:'https://example.invalid/recording',recording_title:'Watch Recording'};
const noHomework={...meeting,id:'old',title:'Unrelated past class',description:'No homework link.'};
const fixture={ok:true,upcoming:[next,later],recordings:[recording],all:[meeting,next,later,recording,noHomework]};
const unchanged=JSON.stringify(fixture),app={innerHTML:''},calls=[];
const context=vm.createContext({document:{getElementById:id=>{assert.equal(id,'app');return app;}},
  location:{origin:'https://apps.thrivingscholars.com'},URL,Intl,Date,
  fetch:async(url,options)=>{calls.push({url,options});return {ok:true,json:async()=>fixture};}});
vm.runInContext(script,context,{filename:'actual-tmua-classes-script.js'});
await new Promise(resolve=>setImmediate(resolve));
assert.equal(calls.length,1);assert.equal(calls[0].url,'/api/tmua/classes');assert.equal(calls[0].options.cache,'no-store');
assert.equal(JSON.stringify(fixture),unchanged,'Rendering must not alter stored session fields or API arrays');
assert.match(app.innerHTML,/id="homework-heading">Homework/);
assert.match(app.innerHTML,/TMUA Algebra Essentials/);
assert.match(app.innerHTML,/Sat,? 31 Oct · 10:30–12:00 UK time/);
assert.match(app.innerHTML,/This session was not recorded\./);
assert.ok(app.innerHTML.includes(`href="${pdf}"`));
assert.match(app.innerHTML,/Homework: Algebra Easier Companion - Full Pack \(PDF\)/);
assert.doesNotMatch(app.innerHTML,/\[Homework:|Later same-batch class|Unrelated past class/);
assert.match(app.innerHTML,/Upcoming Live Sessions/);assert.match(app.innerHTML,/Next live class/);
assert.match(app.innerHTML,/href="https:\/\/example.invalid\/zoom"/);
assert.match(app.innerHTML,/Existing recording/);assert.match(app.innerHTML,/href="https:\/\/example.invalid\/recording"/);
assert.equal((app.innerHTML.match(/Watch Recording/g)||[]).length,1,'Homework without recording must not invent a watch button');

const {safeHomeworkUrl,homeworkDetails,sessionCard,render}=vm.runInContext('({safeHomeworkUrl,homeworkDetails,sessionCard,render})',context);
assert.equal(safeHomeworkUrl(pdf),pdf);
assert.equal(safeHomeworkUrl('https://example.invalid/pack.pdf'),'https://example.invalid/pack.pdf');
for(const invalid of ['javascript:alert(1)','data:application/pdf;base64,AAAA','http://example.invalid/pack.pdf',
  '//example.invalid/pack.pdf','/\\example.invalid/pack.pdf','https://user:password@example.invalid/pack.pdf',
  'https://example.invalid/page.html','https://example.invalid/\npack.pdf'])assert.equal(safeHomeworkUrl(invalid),null,invalid);
assert.equal(homeworkDetails('[Homework: Unsafe](javascript:evil)').links.length,0);
const hostile=sessionCard({...meeting,title:'<script>alert(1)</script>',recording_notes:'<img src=x onerror=alert(1)>',
  description:`Untrusted <b>text</b>. [Homework: <img src=x onerror=alert(1)>](${pdf}?a=1&b=2)`},'homework');
assert.match(hostile,/&lt;script&gt;/);assert.match(hostile,/&lt;b&gt;text&lt;\/b&gt;/);
assert.match(hostile,/&lt;img/);assert.match(hostile,/\?a=1&amp;b=2/);
const anchors=[];
const parser=new Parser({onopentag(name,attrs){assert.ok(!['script','img','iframe'].includes(name));
  assert.ok(Object.keys(attrs).every(key=>!/^on/i.test(key)));if(name==='a')anchors.push(attrs);}});
parser.write(hostile);parser.end();
assert.equal(anchors.length,1);assert.equal(anchors[0].href,pdf+'?a=1&b=2');
assert.equal(anchors[0].rel,'noopener noreferrer');
render({upcoming:[],recordings:[],all:[noHomework]});
assert.doesNotMatch(app.innerHTML,/homework-heading/,'No empty homework section is introduced');
assert.match(app.innerHTML,/No upcoming TMUA class/);assert.match(app.innerHTML,/No class recordings/);
console.log('TMUA classes homework passed: actual renderer exposes completed unrecorded homework, preserves live/recording cards, accepts safe PDF links, escapes other text, rejects unsafe URLs, and does not mutate session data. All requests mocked.');
