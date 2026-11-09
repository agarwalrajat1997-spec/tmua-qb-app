"""Emit student materials and a server-only versioned key. Supply --export to stage the SQL import data."""
import argparse
from content_core import *
import level8,level10,level12,mocks8,mocks10,mocks12
from figures import attach
ROOT=Path(__file__).resolve().parents[2];TESTS=ROOT/'public/amc-practice-tests/tests';LIB=ROOT/'lib/amc-edition';LIB.mkdir(exist_ok=True);H=lambda s:html.escape(str(s))
def dump(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf8')
parser=argparse.ArgumentParser();parser.add_argument('--export');args=parser.parse_args()
dest=Path(args.export).resolve() if args.export else None
bank=[r for b in (level8,level10,level12) for k in range(15) for r in b.make(k)]
mock=[r for b in (mocks8,mocks10,mocks12) for r in b.build()]
for r in mock:r['diagram']=attach(r['level'],int(r['id'].split('-')[-1]))
assert len({r['id'] for r in bank+mock})==525
ban=[]
for i,r in enumerate(bank):
 exam='AMC '+str(r['level']);letter=r['key'];subject=r['subtopic'];uid='TS-AMC-26-'+r['id'].upper()
 ban.append(dict(qid=uid,original_index=100000+i,display_order=100000+i,kind='mcq',difficulty=r['difficulty'],topic=r['topic'],subtopic=subject,tags=[r['topic'],subject,exam.lower().replace(' ','-'),'original-2026'],prompt_html=pg(r['stem'])+r['diagram'],options=[dict(label=l,html=H(v)) for l,v in zip('ABCDE',r['choices'])],answer=letter,solution_html=pg(r['solution']),answer_verified=True,amc_exams=[exam],amc_categories=[exam],amc_primary=exam,amc_8=r['level']==8,amc_10=r['level']==10,amc_12=r['level']==12,amc_checker_reason='Original contest practice; the edition build checks a second calculation before assigning the key.',raw=dict(edition='TS26-11',item=r['id'],stem=r['stem']),is_active=False))
tests={}
for p in TESTS.glob('*/index.html'):
 src=p.read_text(encoding='utf8')
 if p.parent.name.startswith('november-'):continue
 arr=re.search(r'"answers":(\[[^\]]+\])|const correctAnswers\s*=\s*(\[[^\]]+\])',src)
 if not arr:continue
 answers=json.loads(arr[1] or arr[2]);assert len(answers)==25
 slug=p.parent.name;lv=8 if 'amc-8' in slug else 10
 tests[slug]=dict(level=lv,minutes=40 if lv==8 else 75,key=''.join(answers),title=re.search(r'<title>([^<]+)',src,re.I)[1].split('|')[0].strip(),version='2026-11-a')
for lv in (8,10,12):
 rr=[r for r in mock if r['level']==lv];slug=f'november-amc-{lv}-full-mock';td=TESTS/slug;td.mkdir(exist_ok=True);title=f'AMC {lv} · November Full Mock'
 dump(td/'questions.json',dict(title=title,level=lv,minutes=40 if lv==8 else 75,items=[dict(stem=r['stem'],choices=r['choices'],diagram=r['diagram']) for r in rr]))
 key=''.join(r['key'] for r in rr);tests[slug]=dict(level=lv,minutes=40 if lv==8 else 75,key=key,title=title,version='2026-11-a')
 page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'+title+'</title><link rel="stylesheet" href="../../edition.css"><main id="app" aria-live="polite"><a href="/amc?exam='+str(lv)+'&amp;section=practice-tests">← AMC '+str(lv)+' practice tests</a><h1>'+title+'</h1><p>Loading your paper…</p></main><script defer src="https://cdn.jsdelivr.net/npm/emailjs-com@3/dist/email.min.js"></script><script defer src="../../email-report.js"></script><script defer src="../../attempt.js"></script><script defer src="../../edition-player.js"></script></html>'
 (td/'index.html').write_text(page,encoding='utf8')
 css='*{box-sizing:border-box}body{margin:0 auto;max-width:820px;color:#292328;padding:22px;font:16px/1.55 system-ui}h1,h2{font-family:Georgia,serif;line-height:1.15;color:#632c3c}header{padding-bottom:14px;border-bottom:2px solid #be9e5c}h2{font-size:22px;margin:0 0 8px}section{padding:17px 0;border-bottom:1px solid #d9cfc2}p{margin:8px 0}.tag{font-weight:650;color:#723447}.qtext{font-weight:550}a{color:#712b40}svg{max-width:100%;height:auto} @media print{@page{size:A4;margin:14mm 14mm 15mm}body{max-width:none;padding:0;font-size:10.5pt}section{break-inside:avoid}nav,.screen{display:none}header{break-after:avoid}h2{font-size:15pt}svg{max-height:32mm}}'
 sections=[]
 for n,r in enumerate(rr,1):
  sections.append(f'<section id="q{n}"><h2>Question {n} · Answer {r["key"]}</h2><p class="qtext">{H(r["stem"])}</p>'+r['diagram']+f'<p><b>Choices:</b> '+ ' &nbsp; '.join(l+' '+H(t) for l,t in zip('ABCDE',r['choices']))+f'</p><p>{H(r["solution"])}</p><p class="tag">Answer: {r["key"]} · {H(r["answer"])}</p></section>')
 review='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+title+' · Worked solutions</title><style>'+css+'</style><body><header><div>THRIVING SCHOLARS · ORIGINAL CONTEST PRACTICE</div><h1>'+title+'</h1><p>Worked solutions • 25 questions • '+str(tests[slug]['minutes'])+' minutes</p><p class="screen"><a href="worked-solutions.pdf">Download the worked-solutions PDF</a> · <a href="index.html">Open paper</a></p></header>'+''.join(sections)+'</body></html>'
 (td/'solutions.html').write_text(review,encoding='utf8')
dump(LIB/'tests.json',tests)
if dest:
 dest.mkdir(parents=True,exist_ok=True);dump(dest/'canon.json',bank+mock)
 for i in range(0,len(ban),15):dump(dest/f'bank-{i//15:02}.json',ban[i:i+15])
print('Independently checked option values:',len(bank),'bank +',len(mock),'mock;',len(tests),'paper keys')
