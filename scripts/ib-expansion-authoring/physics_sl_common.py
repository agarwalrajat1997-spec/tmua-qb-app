from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
import json, math, hashlib, html
ROOT=Path(__file__).resolve().parents[2]
BASE={'space-time-motion':200,'particulate-matter':120,'wave-behaviour':120,'fields':100,'nuclear-quantum':100}
CODES={'space-time-motion':'a','particulate-matter':'b','wave-behaviour':'c','fields':'d','nuclear-quantum':'e'}
TITLES={'A.1':'Kinematics','A.2':'Forces and momentum','A.3':'Work, energy and power','B.1':'Thermal energy transfers','B.2':'Greenhouse effect','B.3':'Gas laws','B.5':'Current and circuits','C.1':'Simple harmonic motion','C.2':'Wave model','C.3':'Wave phenomena','C.4':'Standing waves and resonance','C.5':'Doppler effect','D.1':'Gravitational fields','D.2':'Electric and magnetic fields','D.3':'Motion in electromagnetic fields','E.1':'Structure of the atom','E.3':'Radioactive decay','E.4':'Fission','E.5':'Fusion and stars'}
def fmt(value,sf=3):
 d=Decimal(str(value))
 if not d:return '0'
 e=d.copy_abs().adjusted();r=d.quantize(Decimal(1).scaleb(e-sf+1),rounding=ROUND_HALF_UP)
 if abs(r)>=Decimal('100000') or abs(r)<Decimal('0.001'):
  exponent=r.copy_abs().adjusted();mantissa=r.scaleb(-exponent);return format(mantissa,'f')+r'\times10^{'+str(exponent)+'}'
 return format(r,'f')
def table(headers,rows):return '\n\n| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in rows)+'\n\n'
def M(text):return {'code':'M1','text':text}
def A(text):return {'code':'A1','text':text}
def R(text):return {'code':'R1','text':text}
def P(prompt,*steps):return {'prompt':prompt,'steps':list(steps)}
def rec(topic,family,variant,title,code,stem,parts,notes,diagram=None,scheme_diagram=None,difficulty='medium'):
 number=BASE[topic]+family*4+variant+1;label=CODES[topic]
 q={'id':f'ib-phy-{label}-{number:03d}','subject':'physics-hl','topicId':topic,'collectionId':'physics-'+topic,'number':number,'title':title,'subtopic':TITLES[code],'syllabusCode':code,'level':'core','difficulty':difficulty,'calculator':True,'questionType':'data-based' if 'simulated' in stem.lower() else 'structured','marks':sum(len(p['steps']) for p in parts),'stem':stem+'\n\nGive calculated numerical answers to three significant figures unless stated otherwise.','parts':[],'markScheme':[],'source':{'document':'Independent syllabus-authored practice','question':number},'verification':{'method':'Author numerical, dimensional and model-consistency checks; independent review recorded separately','notes':notes},'status':'published'}
 for j,p in enumerate(parts):
  letter=chr(97+j);q['parts'].append({'label':letter,'prompt':p['prompt'],'marks':len(p['steps'])});q['markScheme'].append({'part':letter,'steps':p['steps']})
 if diagram:q['diagramSvg']=diagram
 if scheme_diagram:q['markSchemeDiagramSvg']=scheme_diagram
 return q
def svg(body,width=640,height=360):return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"><rect width="{width}" height="{height}" fill="white"/>'+body+'</svg>'
def text(x,y,value,size=16,anchor='start'):return f'<text x="{x}" y="{y}" font-family="Arial" font-size="{size}" text-anchor="{anchor}" fill="#292522">{html.escape(str(value))}</text>'
def line(x1,y1,x2,y2,color='#3c4b5b',width=2):return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>'
def plot(points,xlabel,ylabel,title='Simulated measurements'):
 def limit(value):
  if value<=0:return 1
  exponent=math.floor(math.log10(value));scale=10**exponent;mantissa=value/scale
  return next(n for n in [1,1.2,1.5,2,2.5,3,4,5,6,8,10] if n>=mantissa)*scale
 xs=[p[0] for p in points];ys=[p[1] for p in points];xmax=limit(max(xs)*1.1);ymax=limit(max(ys)*1.1)
 X=lambda x:80+490*x/xmax;Y=lambda y:285-220*y/ymax
 body=text(80,28,title)+line(80,285,580,285)+line(80,285,80,52)+text(580,337,xlabel,15,'end')+text(16,48,ylabel,15)
 for k in range(5):
  xx=xmax*k/4;yy=ymax*k/4;body+=line(X(xx),285,X(xx),290)+text(round(X(xx),2),312,f'{xx:.3g}',12,'middle')+line(75,Y(yy),80,Y(yy))+text(68,round(Y(yy)+4,2),f'{yy:.3g}',12,'end')
 body+='<polyline points="'+' '.join(f'{X(x):.2f},{Y(y):.2f}' for x,y in points)+'" fill="none" stroke="#7a1f24" stroke-width="2"/>'
 for x,y in points:body+=f'<circle cx="{X(x):.2f}" cy="{Y(y):.2f}" r="4" fill="#7a1f24"/>'
 return svg(body)
def save(topic,questions):
 assert len(questions)==20
 path=ROOT/'content/ib/physics-hl'/f'{topic}.json';current=json.loads(path.read_text(encoding='utf-8'));old=[q for q in current if q['number']<=BASE[topic]]
 assert len(old)==BASE[topic]
 path.write_text(json.dumps(old+sorted(questions,key=lambda q:q['number']),ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
 report=ROOT/'docs/ib-expansion-reviews';report.mkdir(parents=True,exist_ok=True)
 ledger={'status':'author-checked','topic':topic,'questions':20,'families':5,'fileSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'scope':'First-assessment2025 Physics SL; all additions use core content. Existing values and IDs retained.','records':[{'id':q['id'],'syllabusCode':q['syllabusCode'],'marks':q['marks'],'method':q['verification']['notes']} for q in questions]}
 (report/f'physics-sl-{topic}-author.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
