from pathlib import Path
import json,re
from content_core import *
from legacy_edits import questions
R=Path(__file__).resolve().parents[2];td=R/'public/amc-practice-tests/tests'
slots={5:[1,2,3,4,5,6,8,9,11,12,13,15,16,18,19,20,21,22,23,25],6:[1,4,5,7,8,9,10,11,12,13],7:[14,22]}
# The numbered ledger is derived from the original overlap scan. These are the only changed slots.
import argparse
pa=argparse.ArgumentParser();pa.add_argument('--ledger');args=pa.parse_args()
if args.ledger:
 flagged=json.loads(Path(args.ledger).read_text(encoding='utf8'))
 for paper in (5,6):slots[paper]=sorted({int(x[2].split(' Q')[-1]) for x in flagged if x[2].startswith('amc-10-topical-test-'+str(paper)+' Q')})
 (Path(__file__).parent/'legacy-slots.json').write_text(json.dumps(slots),encoding='utf8')
else:slots={int(k):v for k,v in json.loads((Path(__file__).parent/'legacy-slots.json').read_text()).items()}
qs=questions();assert len(qs)==sum(map(len,slots.values()))==40
def fig(i):
 def ln(x,y,X,Y):return f'<line x1="{x}" y1="{y}" x2="{X}" y2="{Y}" stroke="#633648" stroke-width="2"/>'
 def arc(x,y,r):return f'<circle cx="{x}" cy="{y}" r="{r}" stroke="#6d3b48" fill="none" stroke-width="1.6"/>'
 def label(x,y,t):return f'<text x="{x}" y="{y}" font-size="12" font-family="sans-serif">{t}</text>'
 def lines(points):return ''.join(ln(*a,*b) for a,b in zip(points,points[1:]+points[:1]))
 if i==2:return svg(lines([(20,114),(110,114),(65,6)])+ln(65,6,65,114)+label(50,132,'10')+label(16,53,'13')+label(92,53,'13'),'Isosceles triangle split by its altitude',150,140)
 if i==12:return svg(arc(95,80,60)+ln(47,44,143,44)+ln(95,80,95,44)+label(106,39,'chord 16')+label(100,93,'O'),'Circle with a chord and perpendicular to its midpoint',190,145)
 if i==14:return svg(lines([(16,124),(216,124),(216,4),(16,4)])+lines([(16,124),(216,64),(116,4)])+label(84,143,'20')+label(225,69,'12'),'Rectangle with triangle to opposite side midpoints',252,150)
 if i==16:return svg(arc(75,60,50)+arc(155,60,50)+ln(115,30,115,90)+ln(75,60,155,60)+label(100,113,'centres 8 apart'),'Equal circles with their common chord',227,125)
 if i==27:return svg(lines([(20,115),(152,115),(86,1)])+lines([(64,115),(130,77),(64,39)]),'Equilateral triangle with the cyclic one-third division points joined',170,130)
 if i==38:return svg('<path d="M20 118 A80 80 0 0 1 180 118" stroke="#633648" stroke-width="2" fill="none"/>'+ln(20,118,180,118)+lines([(52,118),(148,118),(148,54),(52,54)])+label(86,139,'width 6'),'A rectangle inscribed in a semicircle above the diameter',205,150)
 return ''
ix=0
for num,ss in slots.items():
 folder=td/f'amc-10-topical-test-{num}';p=folder/'index.html';sol=folder/'solutions.html';src=p.read_text(encoding='utf8');s=sol.read_text(encoding='utf8')
 legacy=folder/'solutions-before-november-edition.html'
 if not legacy.exists():legacy.write_text(s,encoding='utf8')
 s=legacy.read_text(encoding='utf8')
 mm=re.search(r'const config = (.+?);\s*\n',src);cfg=json.loads(mm[1])
 for n in ss:
  row=qs[ix];ix+=1;k=cfg['answers'][n-1];opts=row['choices'][:];a=opts.index(row['answer']);b='ABCDE'.index(k);opts[a],opts[b]=opts[b],opts[a];assert opts[b]==row['answer']
  art=fig(ix);question=pg(row['stem'])+art+'<p>'+' &nbsp; '.join('<b>'+l+'.</b> '+html.escape(v) for l,v in zip('ABCDE',opts))+'</p>'
  cfg['specialQuestions'][str(n)]=question
  body=f'<section id="q{n}"><h2>Question {n} · Answer {k}</h2>'+question+pg(row['solution'])+'<a href="#questions">All questions ↑</a></section>'
  s,c=re.subn(r'<section id="q'+str(n)+r'">[\s\S]*?</section>',lambda _:body,s,count=1);assert c==1
 src=src[:mm.start(1)]+json.dumps(cfg,ensure_ascii=False,separators=(',',':'))+src[mm.end(1):]
 sol.write_text(s.replace('</header>','<p><a href="solutions-before-november-edition.html">Earlier edition: worked solutions</a></p></header>',1),encoding='utf8');p.write_text(src,encoding='utf8')
print('Revised',ix,'slots; kept all original keys and prior solution pages.')
