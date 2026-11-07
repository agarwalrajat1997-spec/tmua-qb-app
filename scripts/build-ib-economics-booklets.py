"""Render the ten Economics sittings using the same content used by the portal."""
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
papers=root/'content/ib/economics-mocks-2022'
out=root/'public/ib-economics-mocks';out.mkdir(exist_ok=True)
font_dirs=[Path(os.environ.get('ECONOMICS_FONT_DIR','C:/Windows/Fonts')),Path('/usr/share/fonts/truetype/liberation2'),Path('/usr/share/fonts/truetype/dejavu')]
for name,candidates in [('Regular',['arial.ttf','LiberationSans-Regular.ttf','DejaVuSans.ttf']),('Bold',['arialbd.ttf','LiberationSans-Bold.ttf','DejaVuSans-Bold.ttf'])]:
 path=next((d/n for d in font_dirs for n in candidates if (d/n).is_file()),None)
 if not path:raise RuntimeError('Install Arial, Liberation Sans or DejaVu Sans, or set ECONOMICS_FONT_DIR.')
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
class SpaceForAnswer(Flowable):
 def __init__(self,marks,graph=False):
  super().__init__();self.height=100 if graph else min(186,15*marks+7);self.graph=graph
 def wrap(self,aw,ah):self.width=aw;return aw,self.height
 def draw(self):
  c=self.canv;c.setStrokeColor(colors.HexColor('#c5d4d4'));c.setLineWidth(.4)
  if self.graph:c.rect(1,6,self.width-2,self.height-10)
  else:
   for y in range(7,int(self.height),15):c.line(1,y,self.width-2,y)
def build(m,p,solutions):
 data=json.loads((papers/'papers'/(p['id']+'.json')).read_text(encoding='utf8'));num=p['paper'];typ='Worked mark scheme' if solutions else 'Question booklet'
 title=p['title']+' · '+typ;path=out/(p['id']+('-solutions.pdf' if solutions else '-questions.pdf'))
 doc=SimpleDocTemplate(str(path),pagesize=A4,leftMargin=48,rightMargin=48,topMargin=49,bottomMargin=45,title=title,author='Thriving Scholars',pageCompression=1)
 story=[par('DIPLOMA PROGRAMME PRACTICE   /   '+m['course'].upper()+'   /   SET '+m['set'],label),par('Economics / Paper '+num,display),par(typ+'   ·   '+str(p['minutes'])+' minutes   ·   '+str(p['marks'])+' marks',sub)]
 instructions={'1':'Choose one of the three questions and answer both parts. No calculator is permitted. Use real-world examples in part (b) and fully labelled diagrams where relevant. Write on separate answer paper.',
 '2':'Choose one of the two cases and answer all parts (a) to (g) of that case. A calculator is permitted. Use the extracts and data in your answers. Show workings and units, and draw fully labelled diagrams on separate answer paper.',
 '3':'Answer all parts of both questions. A calculator is permitted. Write your answers and diagrams in the spaces provided. Show working and units. Give exact values or round to two decimal places unless otherwise instructed.'}
 story += [par(instructions[num])]
 if solutions:story += [par('Judge extended responses as a whole using the markband for that part. Award valid alternative analysis and diagrams. In linked calculations, credit correct use of an earlier result. The suggested judgements are examples.',small)]
 if solutions:
  story+=[Spacer(1,12),par('HOW TO MARK THIS PAPER',label)]
  if num=='1':story.append(par('Use the 10-mark scale for each explanation and the 15-mark scale for the evaluation. Only the two parts of the selected essay contribute to the score.'))
  elif num=='2':story.append(par('Use the question-specific marking notes for parts (a) to (f). Apply the 15-mark scale to part (g). Only the selected case contributes to the score.'))
  else:story.append(par('Use the analytic scheme in part (a). Apply the 10-mark policy scale to each part (b). Add the marks for both compulsory questions.'))
  seen=set()
  for q in data['questions']:
   for a,g in zip(q['parts'],q['markScheme']):
    for st in g['steps']:
     if st['code']=='Markband' and st['text'] not in seen:
      seen.add(st['text']);story+= [par(str(a['marks'])+'-MARK SCALE',label),par(st['text'].split('. ',1)[1],body)]
  story+=[Spacer(1,10),par('QUESTIONS IN THIS SCHEME',label)]
  for q in data['questions']:story.append(par(str(q['number'])+'   '+q['title']+'   ['+str(q['marks'])+']'))
  story.append(PageBreak())
 for ix,q in enumerate(data['questions']):
  if ix and (solutions or num!='1'):story.append(PageBreak())
  story += [Spacer(1,9),par('QUESTION '+str(ix+1)+'   /   '+str(q['marks'])+' MARKS',label),par(q['title'],head)]
  if not solutions:
   if num!='1':
    for para in q['stem'].split('\n\n'):
     story.append(matrix(para) if para.startswith('|') else par(para,small if para.startswith('Background reading:') else body))
    if q.get('stimulusSvg'):story.append(KeepTogether([par('FIGURE 1',label),figure(q['stimulusSvg'])]))
    story.append(Spacer(1,8))
   for a in q['parts']:
    question=Paragraph('<b>'+escape(a['label'])+'</b> &nbsp; '+escape(a['prompt'])+' &nbsp; <b>['+str(a['marks'])+']</b>',body)
    block=[question,Spacer(1,4)]
    if num=='3':block.append(SpaceForAnswer(a['marks'],'diagram' in a['prompt'].lower()))
    story.append(KeepTogether(block))
  else:
   if q.get('background'):
    b=q['background'];story.append(Paragraph('<b>Background reading.</b> <a color="#11696b" href='+quoteattr(b['url'])+'>'+escape(b['label'])+'</a>',small))
   for j,(a,g) in enumerate(zip(q['parts'],q['markScheme'])):
    story.append(par('PART '+a['label']+'   /   '+str(a['marks'])+' MARKS',label));story.append(par(a['prompt'],sub))
    for step in g['steps']:
     if step['code']=='Markband':
      story.append(par('Apply the '+str(a['marks'])+'-mark scale on the first page to this response as a whole.',small));continue
     story.append(Paragraph('<b>'+escape(step['code'])+'.</b> '+escape(step['text']),body))
    target={'water':'c','copper':'c','solar':'c','tourism':'c','levy':'a(vi)','fiscal':'a(vii)','wheat':'a(vii)','reserves':'a(vi)'}.get(q['figureKey'],'a')
    if a['label']==target:story.append(KeepTogether([par('WORKED REPRESENTATION   /   '+a['label'],label),figure(q['solutionSvg'])]))
    story.append(Spacer(1,6))
 def frame(c,d):
  W,H=A4;c.setFillColor(colors.HexColor(teal));c.setFont('Bold',8);c.drawString(48,H-29,'THRIVING SCHOLARS');c.drawRightString(W-48,H-29,'ECONOMICS   /   '+m['course'].upper()+'   /   SET '+m['set'])
  c.setStrokeColor(colors.HexColor(rule));c.line(48,H-35,W-48,H-35);c.line(48,33,W-48,33);c.setFont('Regular',8);c.drawString(48,20,'Independent practice · Economics · First assessment 2022');c.drawRightString(W-48,20,'Paper '+num+'  ·  '+typ+'  |  '+str(d.page))
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
   for s in (False,True):build(m,p,s)
