"""Build combined and question-only AI SL papers from the timed-paper records."""
from pathlib import Path
import json,math,os,re,io
from xml.etree import ElementTree as ET
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader,PdfWriter
from pypdf.generic import StreamObject,ArrayObject,NameObject,NullObject
import base64
r=Path(__file__).resolve().parents[2];data=r/'content/ib/ai-sl-mocks-2026'
def font(name,paths):
 path=next(Path(x) for x in paths if x and Path(x).is_file());pdfmetrics.registerFont(TTFont(name,str(path)))
font('Practice',[os.getenv('IB_PDF_FONT'),'C:/Windows/Fonts/arial.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'])
font('PracticeBold',[os.getenv('IB_PDF_BOLD_FONT'),'C:/Windows/Fonts/arialbd.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'])
W,H=A4;ink='#173942';teal='#006C6E';grey='#53696C';pale='#CDDBDC'
def drawsvg(c,svg,x,y,width):
 root=ET.fromstring(svg);_,_,vw,vh=map(float,root.get('viewBox').split());z=width/vw;c.saveState();c.translate(x,y-vh*z);c.scale(z,z)
 for el in root:
  tag=el.tag.split('}')[-1];g=el.attrib;v=lambda a:float(g[a]); yy=lambda key:vh-v(key)
  if tag=='line':
   c.setStrokeColor(HexColor(g['stroke']));c.setLineWidth(float(g.get('stroke-width',1)));c.line(v('x1'),yy('y1'),v('x2'),yy('y2'))
  elif tag=='circle':
   c.setFillColor(HexColor(g['fill']));c.circle(v('cx'),yy('cy'),v('r'),stroke=0,fill=1)
  elif tag=='text':
   c.setFillColor(HexColor(g['fill']));c.setFont('Practice',float(g.get('font-size',12)));c.drawString(v('x'),yy('y'),el.text or '')
  else:raise ValueError(tag)
 c.restoreState();return y-vh*z
def write(f,meta,qs,combined):
 c=Canvas(str(f),pagesize=A4,pageCompression=1,invariant=1);label='AI SL  /  SET '+meta['set']+'  /  PAPER '+meta['paper']
 c.setTitle(meta['title']+(' · Paper and worked solutions' if combined else ' · Question booklet'));c.setAuthor('Thriving Scholars')
 def text(x,y,s,font='Practice',size=11,color=ink):
  c.setFillColor(HexColor(color));c.setFont(font,size);c.drawString(x,y,s)
 def wrap(x,y,s,width,size=11,font='Practice',gap=15,color=ink):
  line=''
  for word in s.split():
   if pdfmetrics.stringWidth((line+' '+word).strip(),font,size)>width and line:
    text(x,y,line,font,size,color);y-=gap;line=''
   line=(line+' '+word).strip()
  if line:text(x,y,line,font,size,color);y-=gap
  return y
 page=0
 def header(sec):
  nonlocal page
  page+=1;text(42,H-38,'THRIVING SCHOLARS', 'PracticeBold',9,teal);text(300,H-38,label,'PracticeBold',9,ink)
  c.setStrokeColor(HexColor(teal));c.setLineWidth(1.2);c.line(42,H-48,W-42,H-48)
  c.setStrokeColor(HexColor(pale));c.line(42,38,W-42,38);text(42,24,'Independent practice · First assessment 2021 · Exams through November 2028','Practice',8,grey)
  c.setFont('Practice',8);c.drawRightString(W-42,24,sec+'   /   '+str(page))
 def start():return H-83
 def cover(sol=False):
  header('Worked solutions' if sol else 'Question paper')
  text(43,H-122,'MARKING AND REVIEW' if sol else 'DIPLOMA PROGRAMME PRACTICE', 'PracticeBold',10,teal)
  text(42,H-178,'Worked solutions' if sol else 'Mathematics', 'PracticeBold',34)
  text(43,H-215,'Applications and interpretation SL', 'Practice',21)
  text(44,H-248,'Set '+meta['set']+'   /   Paper '+meta['paper']+'   /   '+('Short response' if meta['paper']=='1' else 'Extended response'),'PracticeBold',15,teal)
  y=H-320
  info=['90 minutes  ·  80 marks  ·  All questions compulsory','Use a graphic display calculator and a clean Mathematics formula booklet.','Write your reasoning and working in a separate answer booklet. Unless stated otherwise, give exact answers or round numerical results to three significant figures.','Diagrams are illustrative unless coordinates or dimensions are specified.'] if not sol else ['Maximum mark: 80. The allocations are for independent self-assessment.','M = method, A = accuracy or stated result, R = reasoning. Award equivalent valid methods. Follow through from an earlier numerical slip when the subsequent method is correct and the task is not simplified.','Keep unrounded calculator values until the final answer. Accept sensible equivalent accuracy unless the question specifies otherwise.','Read the student’s written interpretation as well as their numerical result. A calculator output alone may not justify a conclusion.']
  if not sol and meta['paper']=='1':info[2]=info[2].replace('in a separate answer booklet','in the spaces provided; use additional answer paper if needed')
  for s in info:y=wrap(45,y,s,W-98,12,gap=17)-16
  c.showPage()
 def drawq(y,q,sol):
  text(43,y,('SOLUTION ' if sol else 'QUESTION ')+str(q['number']),'PracticeBold',11,teal);c.setFillColor(HexColor(grey));c.setFont('PracticeBold',10);c.drawRightString(W-43,y,str(q['marks'])+' marks');y-=22
  if not sol:
   y=wrap(44,y,q['stem'],W-90,11.2,gap=15.7)-7
   if q.get('diagramSvg'):y=drawsvg(c,q['diagramSvg'],60,y,285)-13
  for part,group in zip(q['parts'],q['markScheme']):
   text(44,y,'('+part['label']+')','PracticeBold',10.5,teal)
   c.setFillColor(HexColor(grey));c.setFont('PracticeBold',9);c.drawRightString(W-44,y,'['+str(part['marks'])+']')
   y=wrap(65,y,part['prompt'],W-142,10.25 if sol else 11,'PracticeBold' if sol else 'Practice',14.2)-3
   if sol:
    for step in group['steps']:
     text(65,y,step['code'],'PracticeBold',8.8,teal);y=wrap(89,y,step['text'],W-140,9.6,gap=12.5)-2
   elif meta['paper']=='1':
    c.setStrokeColor(HexColor(pale));c.setLineWidth(.4)
    for _ in range(2+int(part['marks']>=4)):
     y-=13;c.line(65,y,W-47,y)
   y-=6
  assert y>44,(f,q['number'],sol,y);return y
 cover()
 for sol in ([False,True] if combined else [False]):
  if sol:cover(True)
  # Keep every problem and its marking notes together. Long responses get a full page.
  for i in range(0,len(qs),2 if meta['paper']=='1' else 1):
   header('Worked solutions' if sol else 'Question paper');y=start();batch=qs[i:i+(2 if meta['paper']=='1' else 1)]
   for j,q in enumerate(batch):
    if j:
     y-=12;c.setStrokeColor(HexColor(pale));c.setLineWidth(.6);c.line(43,y,W-43,y);y-=26
    y=drawq(y,q,sol)
   c.showPage()
 c.save()
 # ASCII85 streams keep PDF assets portable through the source repository connector.
 raw=f.read_bytes();writer=PdfWriter();writer.clone_document_from_reader(PdfReader(io.BytesIO(raw)))
 for o in writer._objects:
  if not isinstance(o,StreamObject):continue
  o._data=base64.a85encode(o._data)+b'~>';k=NameObject('/Filter');filters=o.get(k);o[k]=ArrayObject([NameObject('/ASCII85Decode')]+(list(filters) if isinstance(filters,ArrayObject) else [filters] if filters else []))
  if '/DecodeParms' in o:
   old=o['/DecodeParms'];o[NameObject('/DecodeParms')]=ArrayObject([NullObject()]+(list(old) if isinstance(old,ArrayObject) else [old]))
 out=io.BytesIO();writer.write(out);payload=out.getvalue().replace(b'%\xe2\xe3\xcf\xd3',b'%ABCD');assert payload.isascii()
 assert len(PdfReader(io.BytesIO(payload)).pages)==page;f.write_bytes(payload);print(f.name,page,'pages',len(payload),'bytes')
for m in json.loads((data/'catalog.json').read_text(encoding='utf8')):
 questions=json.loads((data/'papers'/(m['id']+'.json')).read_text(encoding='utf8'))['questions']
 for field in ['questionPdfUrl','pdfUrl']:
  f=r/('public'+m[field]);f.parent.mkdir(parents=True,exist_ok=True);write(f,m,questions,field=='pdfUrl')
