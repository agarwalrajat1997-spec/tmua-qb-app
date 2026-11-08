"""Render the ten Psychology sittings using the same content used by the portal."""
from pathlib import Path
from xml.etree import ElementTree
from xml.sax.saxutils import escape,quoteattr
import json,re,os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether,Flowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab import rl_config
from reportlab.graphics.shapes import Drawing,PolyLine,Polygon,Circle,String
from reportlab.pdfgen.canvas import Canvas
rl_config.useA85=1
root=Path(__file__).resolve().parents[1]
papers=root/'content/ib/psychology-mocks-2027'
out=root/'public/ib-psychology-mocks';out.mkdir(exist_ok=True)
font_dirs=[Path(os.environ.get('PSYCHOLOGY_FONT_DIR','C:/Windows/Fonts')),Path('/usr/share/fonts/truetype/liberation2'),Path('/usr/share/fonts/truetype/dejavu')]
for name,candidates in [('Regular',['arial.ttf','LiberationSans-Regular.ttf','DejaVuSans.ttf']),('Bold',['arialbd.ttf','LiberationSans-Bold.ttf','DejaVuSans-Bold.ttf'])]:
 path=next((d/n for d in font_dirs for n in candidates if (d/n).is_file()),None)
 if not path:raise RuntimeError('Install Arial, Liberation Sans or DejaVu Sans, or set PSYCHOLOGY_FONT_DIR.')
 pdfmetrics.registerFont(TTFont(name,str(path)))
pdfmetrics.registerFontFamily('Regular',normal='Regular',bold='Bold')
ink='#163742';teal='#11696b';muted='#41565c';rule='#adbdbe'
def style(key,size,lead,font='Regular',col=ink,after=4,**kwargs):
 return ParagraphStyle(key,fontName=font,fontSize=size,leading=lead,textColor=colors.HexColor(col),spaceAfter=after,allowWidows=0,allowOrphans=0,**kwargs)
body=style('body',9.6,13.3,after=5);small=style('small',8.2,11,col=muted);head=style('head',17,21,'Bold',after=7,keepWithNext=1);display=style('display',25,29,'Bold',after=8,keepWithNext=1);label=style('label',8.1,11,'Bold',teal,after=4,keepWithNext=1);sub=style('sub',10,13,'Bold',after=6,keepWithNext=1);cell=style('cell',8.5,11,after=0)
def par(s,sty=body):return Paragraph(escape(s),sty)
def matrix(lines):
 rows=[l.strip('| ').split(' | ') for l in lines.splitlines() if not re.match(r'^\|\s*---',l)]
 tab=Table([[par(c,cell) for c in row] for row in rows],colWidths=[209]+[267/(len(rows[0])-1)]*(len(rows[0])-1),hAlign='LEFT',repeatRows=1)
 tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dae9e8')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f0f5f4')]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
 return tab
def figure(svg):
 drawing=Drawing(650,300)
 for node in ElementTree.fromstring(svg):
  tag=node.tag.split('}')[-1];v=node.attrib;col=lambda k:colors.HexColor(v[k])
  if tag=='polyline':
   pts=[tuple(map(float,p.split(','))) for p in v['points'].split()]
   shape=PolyLine([z for x,y in pts for z in (x,300-y)],strokeColor=col('stroke'),strokeWidth=float(v['stroke-width']))
   if 'stroke-dasharray' in v:shape.strokeDashArray=[5,4]
  elif tag=='polygon':
   pts=[tuple(map(float,p.split(','))) for p in v['points'].split()];shape=Polygon([z for x,y in pts for z in (x,300-y)],fillColor=col('fill'),strokeColor=None)
  elif tag=='circle':shape=Circle(float(v['cx']),300-float(v['cy']),float(v['r']),fillColor=col('fill'),strokeColor=None)
  elif tag=='text':shape=String(float(v['x']),300-float(v['y']),node.text or '',fontName='Regular',fontSize=float(v['font-size']),fillColor=col('fill'),textAnchor=v.get('text-anchor','start'))
  else:raise ValueError(tag)
  drawing.add(shape)
 drawing.scale(.70,.70);drawing.width=455;drawing.height=210
 return drawing
def build(m,p,kind):
 data=json.loads((papers/'papers'/(p['id']+'.json')).read_text(encoding='utf8'));num=p['paper'];typ={'questions':'Question booklet','solutions':'Worked mark scheme','resources':'Resource booklet'}[kind]
 title=p['title']+' · '+typ;path=out/(p['id']+'-'+kind+'.pdf')
 doc=SimpleDocTemplate(str(path),pagesize=A4,leftMargin=48,rightMargin=48,topMargin=49,bottomMargin=45,title=title,author='Thriving Scholars',pageCompression=1)
 story=[par('DIPLOMA PROGRAMME PRACTICE   /   '+m['course'].upper()+'   /   SET '+m['set'],label),par('Psychology / Paper '+num,display),par(typ+'   ·   '+str(p['minutes'])+' minutes   ·   '+str(p['marks'])+' marks',sub)]
 directions={'1':'Answer Questions 1–4 in Sections A and B. In Section C answer either Question 5 or Question 6. Use psychological knowledge and accurate terminology throughout.','2':'Answer all five questions. For Section A draw on the specified practical you conducted in class. For Section B, use the unseen study in this booklet.','3':'Answer all four questions. Source 1 appears with Question 1. Use the accompanying resource booklet for Sources 2–5. In Question 4 integrate at least three of Sources 2–5 and your own psychological knowledge.'}
 story.append(par('Use with the matching Set '+m['set']+' Paper 3 question booklet. The studies and data are constructed for this practice paper.' if kind=='resources' else directions[num]))
 if kind=='solutions':story.append(par('Judge the whole response against the question-specific markband. Award zero for no creditworthy material. The worked answers illustrate one route; credit other scientifically defensible answers. Class-practical examples are illustrative.',small))
 elif kind=='questions':story.append(par('Write your responses on separate answer paper. Use the marks beside each question to guide your time.',small))
 def paragraphs(s):return [matrix(x) if x.startswith('|') else par(x) for x in s.split('\n\n') if x]
 if kind=='resources':
  for res in data['resources']:
   block=[Spacer(1,10),par('SOURCE '+str(res['number']),label),par(res['title'],head),*paragraphs(res['text'])]
   if res.get('svg'):block.append(figure(res['svg']))
   story.append(KeepTogether(block))
 else:
  prev=None
  for q in data['questions']:
   div=q['division'];block=[Spacer(1,8)]
   if prev!=div and div!='R':
    headings={'1':{'A':'Knowledge and understanding','B':'Application to new situations','C':'Conceptual essays · choose one'},'2':{'A':'Your class practical','B':'Evaluation of an unseen study'}}
    if prev and kind=='questions' and (num=='2' or div=='C'):story.append(PageBreak())
    block.extend([par('SECTION '+div,label),par(headings[num][div],head)])
   prev=div;block.extend([par('QUESTION '+str(q['number'])+'   /   '+str(q['marks'])+' MARKS',label),*paragraphs(q['stem'])])
   if q.get('stimulusSvg'):block.append(figure(q['stimulusSvg']))
   block.append(par(q['parts'][0]['prompt'],sub))
   if kind=='solutions':
    for st in q['markScheme'][0]['steps']:
     block.append(Paragraph('<b>'+escape(st['code'])+'.</b> '+escape(st['text']),small if st['code']=='Markband' else body))
   story.append(KeepTogether(block))
 def frame(c,d):
  W,H=A4;c.setFillColor(colors.HexColor(teal));c.setFont('Bold',8);c.drawString(48,H-29,'THRIVING SCHOLARS');c.drawRightString(W-48,H-29,'PSYCHOLOGY   /   '+m['course'].upper()+'   /   SET '+m['set'])
  c.setStrokeColor(colors.HexColor(rule));c.line(48,H-35,W-48,H-35);c.line(48,33,W-48,33);c.setFont('Regular',8);c.drawString(48,20,'Independent practice · Psychology · First assessment 2027');c.drawRightString(W-48,20,'Paper '+num+'  ·  '+typ+'  |  '+str(d.page))
 doc.build(story,onFirstPage=frame,onLaterPages=frame)
 # Use ASCII85 for the embedded font streams as well as the drawing streams.
 import io,base64
 from pypdf import PdfReader,PdfWriter
 from pypdf.generic import StreamObject,NameObject,ArrayObject,NullObject
 reader=PdfReader(path);writer=PdfWriter();writer.clone_document_from_reader(reader)
 for obj in writer._objects:
  if not isinstance(obj,StreamObject):continue
  key=NameObject('/Filter');filters=obj.get(key)
  obj._data=base64.a85encode(obj._data)+b'~>'
  obj[key]=ArrayObject([NameObject('/ASCII85Decode')]+(list(filters) if isinstance(filters,ArrayObject) else [filters] if filters else []))
  params=NameObject('/DecodeParms')
  if params in obj:
   previous=obj[params];obj[params]=ArrayObject([NullObject()]+(list(previous) if isinstance(previous,ArrayObject) else [previous]))
 buf=io.BytesIO();writer.write(buf)
 data=buf.getvalue().replace(bytes([37,226,227,207,211]),b'%ABCD')
 assert data.isascii() and len(PdfReader(io.BytesIO(data)).pages)==len(reader.pages)
 path.write_bytes(data)
 print(path.name)
if __name__=='__main__':
 for m in json.loads((papers/'catalog.json').read_text(encoding='utf8')):
  for p in m['papers']:
   for kind in (['questions','solutions','resources'] if p['paper']=='3' else ['questions','solutions']):build(m,p,kind)
