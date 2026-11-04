"""Print original Physics questions then their worked marking points in one PDF.

Run render_pdf_math.cjs first. The question JSON is the single source for both
the website and printable book. No production dependency is added.
"""
from pathlib import Path
import sys, os, re, json, html, hashlib
ROOT=Path(__file__).resolve().parents[2]
WORK=Path(os.environ.get('IB_PHYSICS_MOCK_WORK',ROOT.parent/'physics-mocks-2026'))
sys.path.insert(0,os.environ.get('IB_PHYSICS_PDF_DEPS',str(WORK/'python-deps')))
import fitz
import reportlab.rl_config
reportlab.rl_config.invariant=1
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle, Flowable, KeepTogether, CondPageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ASSETS=WORK/'pdf-assets';MANIFEST=json.loads((ASSETS/'manifest.json').read_text(encoding='utf8'))
PUBLIC=ROOT/'public/ib-mock-solutions';PUBLIC.mkdir(exist_ok=True,parents=True)
DELIVER=ROOT.parents[1]/'outputs/IB_Physics_Mock_Exams';DELIVER.mkdir(exist_ok=True,parents=True)
BUILD=WORK/'pdf-build';BUILD.mkdir(exist_ok=True,parents=True)
DOC=ROOT/'docs/ib-physics-mocks-2026';DOC.mkdir(exist_ok=True,parents=True)
W,H=A4;BW=W-100
BURG=colors.HexColor('#771d27');GOLD=colors.HexColor('#ffce53');INK=colors.HexColor('#202020')
for name,file in [('Exam','times.ttf'),('ExamBold','timesbd.ttf'),('Brand','arial.ttf'),('BrandBold','arialbd.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file))
S={
 'body':ParagraphStyle('body',fontName='Exam',fontSize=11.5,leading=17,spaceAfter=10,autoLeading='max',textColor=INK),
 'part':ParagraphStyle('part',fontName='Exam',fontSize=11.5,leading=17,spaceAfter=7,autoLeading='max',textColor=INK),
 'heading':ParagraphStyle('heading',fontName='BrandBold',fontSize=15,leading=21,spaceAfter=13,keepWithNext=True,textColor=BURG),
 'small':ParagraphStyle('small',fontName='Brand',fontSize=9,leading=13,spaceAfter=8,textColor=INK),
 'table':ParagraphStyle('table',fontName='Exam',fontSize=10.5,leading=16,autoLeading='max',alignment=1),
 'mark':ParagraphStyle('mark',fontName='Exam',fontSize=11.5,leading=17,autoLeading='max',spaceAfter=6),
 'code':ParagraphStyle('code',fontName='BrandBold',fontSize=9,leading=16,textColor=BURG),
}
MATH=re.compile(r'(?<!\\)\$\$([\s\S]*?)(?<!\\)\$\$|(?<!\\)\$([^$\n]+?)(?<!\\)\$')
def prose(t):return html.escape(t).replace(r'\$','$').replace(r"\'", "'")
def inline(t,size=11.5):
    out=[];start=0
    for m in MATH.finditer(t):
        out.append(prose(t[start:m.start()]));tex=(m[1] or m[2]).strip();info=MANIFEST['math'][tex]
        wi=info['widthEm']*size;he=info['heightEm']*size;depth=info['depthEm']*size
        scale=min(1,(BW-50)/wi);wi*=scale;he*=scale;depth*=scale
        out.append(f'<img src="{ASSETS/info["file"]}" width="{wi:.4f}" height="{he:.4f}" valign="{depth:.4f}"/>');start=m.end()
    out.append(prose(t[start:]));value=''.join(out)
    return re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',value)
def blocks(text,style='body'):
    out=[]
    for block in re.split(r'\n\s*\n',text.strip()):
        if not block:continue
        if block.strip().startswith('$$') and block.strip().endswith('$$'):
            tex=block.strip()[2:-2].strip();info=MANIFEST['math'][tex]
            wi=info['widthEm']*11.5;he=info['heightEm']*11.5;scale=min(1,(BW-12)/wi)
            im=Image(str(ASSETS/info['file']),width=wi*scale,height=he*scale);im.hAlign='LEFT';out.extend([im,Spacer(1,12)]);continue
        lines=block.splitlines()
        if any(l.strip().startswith('|') for l in lines):
            tables=[l for l in lines if l.strip().startswith('|') and not re.fullmatch(r'[\s|:\-]+',l)]
            other=[l for l in lines if not l.strip().startswith('|')]
            if other:out.append(Paragraph(inline(' '.join(other)),S[style]))
            rawrows=[[x.strip() for x in line.strip().strip('|').split('|')] for line in tables]
            rows=[[Paragraph(inline(x,10.5),S['table']) for x in row] for row in rawrows]
            if rows:
                nc=max(len(r) for r in rows);rows=[r+[Paragraph('',S['table'])]*(nc-len(r)) for r in rows]
                widths=[BW/nc]*nc
                if nc>=4:
                    words=[w for row in rawrows for w in re.findall(r'[A-Za-z]{5,}',row[0])]
                    needed=max([pdfmetrics.stringWidth(w,'Exam',10.5)+16 for w in words]+[0])
                    first=max(widths[0],min(BW*.35,needed));widths=[first]+[(BW-first)/(nc-1)]*(nc-1)
                tb=Table(rows,colWidths=widths,hAlign='LEFT',repeatRows=1)
                tb.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.5,colors.HexColor('#b5b5b5')),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#fff5db')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
                out.extend([tb,Spacer(1,12)])
        else:
            # Tall matrices/vectors are display objects. Inline image leading
            # can otherwise let their first row overlap a preceding text line.
            tall=[m for m in MATH.finditer(block) if MANIFEST['math'][(m[1] or m[2]).strip()]['heightEm']>2.6 or re.search(r'\\begin\{(?:[pbBvV]?matrix|cases)\}|\\binom',(m[1] or m[2]))]
            if not tall:out.append(Paragraph(inline(block).replace('\n','<br/>'),S[style]))
            else:
                cursor=0
                for m in tall:
                    before=block[cursor:m.start()].strip();items=[]
                    if before:items.append(Paragraph(inline(before).replace('\n','<br/>'),S[style]))
                    info=MANIFEST['math'][(m[1] or m[2]).strip()];wi=info['widthEm']*11.5;he=info['heightEm']*11.5;scale=min(1,(BW-50)/wi)
                    im=Image(str(ASSETS/info['file']),width=wi*scale,height=he*scale);im.hAlign='LEFT'
                    items.extend([im,Spacer(1,10)])
                    if style=='mark':out.extend(items)
                    else:out.append(KeepTogether(items))
                    cursor=m.end()
                after=block[cursor:].strip()
                if after and after not in ['.',',',';',':']:out.append(Paragraph(inline(after).replace('\n','<br/>'),S[style]))
    return out

def brand(c,label):
    c.setFillColor(GOLD);c.roundRect(36,H-43,26,26,5,stroke=0,fill=1)
    c.setFillColor(BURG);c.setFont('BrandBold',10);c.drawCentredString(49,H-35,'ts')
    c.setFont('BrandBold',10);c.drawString(71,H-32,'Thriving Scholars');c.setFont('Brand',8);c.drawRightString(W-36,H-32,label)
    c.setStrokeColor(GOLD);c.setLineWidth(1.1);c.line(36,H-53,W-36,H-53)
class Lines(Flowable):
    def __init__(self,marks):super().__init__();self.width=BW;self.height=min(100,max(28,marks*12))
    def draw(self):
        self.canv.setStrokeColor(colors.HexColor('#d5d5d5'));self.canv.setLineWidth(.4)
        for y in range(6,int(self.height),17):self.canv.line(0,y,self.width,y)
def qlabel(q):return f'{q["section"]} Question {q["number"]}'
class ExamDoc(BaseDocTemplate):
    def __init__(self,path,meta,kind):
        super().__init__(str(path),pagesize=A4,leftMargin=50,rightMargin=50,topMargin=76,bottomMargin=52,title=meta['title'],author='Thriving Scholars')
        self.meta=meta;self.kind=kind;self.qpages={};self.activeQuestion=None
        self.addPageTemplates(PageTemplate(id='exam',frames=[Frame(50,52,BW,H-128,id='body',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=self.header,onPageEnd=self.end_page))
    def header(self,c,doc):
        brand(c,f'Physics {self.meta["course"].upper()} | Set {self.meta["set"]} | Paper {self.meta["paper"]}')
        c.setFont('Brand',8);c.setFillColor(colors.HexColor('#777777'));c.drawString(50,30,self.kind);c.drawRightString(W-50,30,str(doc.page))
    def afterFlowable(self,f):
        if hasattr(f,'questionId'):self.qpages[f.questionId]=self.page;self.activeQuestion=f.questionLabel
    def end_page(self,c,doc):
        if self.activeQuestion is not None:
            label='Paper 1A' if self.activeQuestion.startswith('1A ') else self.activeQuestion
            c.setFont('Brand',8);c.setFillColor(colors.HexColor('#777777'));c.drawString(50,H-67,f'{label} | {self.kind}')
def cover(meta,solutions=False):
    paperlabel='Paper 1A and 1B' if meta['paper']=='1' else 'Paper 2'
    level='Higher Level' if meta['course']=='hl' else 'Standard Level'
    story=[Spacer(1,40),Paragraph('PHYSICS',ParagraphStyle('cap',fontName='BrandBold',fontSize=30,leading=37,textColor=BURG,spaceAfter=18)),
      Paragraph(level,ParagraphStyle('level',fontName='Brand',fontSize=19,leading=27,spaceAfter=15)),
      Paragraph(f'Set {meta["set"]} | {paperlabel}',ParagraphStyle('sub',fontName='BrandBold',fontSize=19,leading=27,spaceAfter=22)),
      Paragraph('Worked solution book' if solutions else 'Challenge mock examination',ParagraphStyle('kind',fontName='BrandBold',fontSize=17,leading=24,textColor=BURG,spaceAfter=22))]
    if solutions:
        story+=blocks('Complete the examination before consulting this book. Marking points indicate a method (M), accuracy (A) or reasoning (R) award. The number after the code gives its value. Award only points supported by the candidate\'s retained working.')
        story+=blocks('Accept valid equivalent approaches and reasonable rounding. Apply error carried forward only where the subsequent method remains physically meaningful; do not reward a contradiction of stated conditions. A correct multiple-choice letter earns one mark; no negative marks apply.')
        story+=blocks('MCQs are automatically marked on the portal. Written marks are self-assessed. Reports show these separately and do not calculate an official IB grade.','small')
    else:
        story+=blocks(f'Time allowed: **{meta["minutes"]} minutes**     Maximum mark: **{meta["marks"]}**')
        for label in ['Candidate name','Candidate number','Date']:story+=blocks(label+': __________________________________________________')
        story+=[Spacer(1,7),Paragraph('Instructions',S['heading'])]
        instructions=['A calculator and a clean current Physics data booklet are permitted throughout.','Answer all questions. Show physical reasoning, working and units in written responses.','Use the constants and assumptions given in a question. Otherwise use the data booklet and retain unrounded intermediate values.','Give numerical answers to an appropriate number of significant figures. Diagrams are schematic unless explicitly stated to be to scale.','The number in square brackets gives the maximum mark for a written part.']
        if meta['paper']=='1':instructions.insert(1,'Paper 1A and Paper 1B share one uninterrupted examination time. Paper 1A has '+str(40 if meta['course']=='hl' else 25)+' multiple-choice questions; Paper 1B has two compulsory experimental/data questions worth 20 marks altogether.')
        else:instructions.insert(1,'All structured questions are compulsory. There are no optional topics or optional questions.')
        for t in instructions:story+=blocks('• '+t,'small')
        story+=blocks('Thriving Scholars challenge practice | Current Physics syllabus | 2026','small')
    return story
def figure(q,maxheight=200):
    path=MANIFEST['diagrams'].get(q['id'])
    if not path:return []
    info=MANIFEST['diagramChecks'][q['id']]
    assert info['svgSha256']==hashlib.sha256(q['diagramSvg'].encode('utf8')).hexdigest(),'Stale SVG raster'
    assert info['pngSha256']==hashlib.sha256((ASSETS/path).read_bytes()).hexdigest(),'Changed SVG raster bytes'
    im=Image(str(ASSETS/path));scale=min(BW/im.imageWidth,maxheight/im.imageHeight)
    im.drawWidth=im.imageWidth*scale;im.drawHeight=im.imageHeight*scale;im.hAlign='CENTER'
    return [im,Spacer(1,11)]
def heading(q,small=False):
    style=S['heading'] if not small else ParagraphStyle('mcqhead',parent=S['heading'],fontSize=12,leading=17,spaceAfter=7)
    p=Paragraph(f'{qlabel(q)} <font size="9">[{q["marks"]} mark'+('s' if q['marks']!=1 else '')+']</font>',style);p.questionId=q['id'];p.questionLabel=qlabel(q);return p
def section_start(section,meta):
    title={'1A':'Paper 1A - Multiple choice','1B':'Paper 1B - Experimental and data-based questions','2':'Paper 2 - Structured questions'}[section]
    out=[Paragraph(title,S['heading'])]
    if section=='1A':out+=blocks('Select one answer, A, B, C or D, for each question. Use the answer grid or record your choices on the portal.','small')
    elif section=='1B':out+=blocks('Continue within the same examination time. Answer both questions. Use the data, graphs and uncertainty information provided.','small')
    return out+[Spacer(1,7)]
def answer_grid(meta,filled=False):
    qs=[q for q in meta['questions'] if q['section']=='1A'];out=[]
    for start in range(0,len(qs),10):
        row=qs[start:start+10]
        data=[[Paragraph(str(q['number']),S['table']) for q in row],[Paragraph(q['correctOption'] if filled else ' ',S['table']) for q in row]]
        tb=Table(data,colWidths=[BW/10]*len(row),rowHeights=[23,25]);tb.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.5,colors.grey),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#fff5db')),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
        out += [tb,Spacer(1,8)]
    return out
def trim_end_page(path,end):
    doc=fitz.open(path);page=doc[-1]
    body=' '.join(b[4].strip() for b in page.get_text('blocks') if b[1]>65 and b[3]<H-46)
    if body.strip()==end and not page.get_images() and len(doc)>1:
        doc.delete_page(len(doc)-1);raw=doc.tobytes(garbage=4,deflate=True);doc.close();path.write_bytes(raw)
    else:doc.close()
def questions(meta):
    path=BUILD/(meta['id']+'-questions.pdf');doc=ExamDoc(path,meta,'Question paper');story=cover(meta);last=None
    for q in meta['questions']:
        if q['section']!=last:
            story+=[PageBreak()]+section_start(q['section'],meta)
            if q['section']=='1A':story+=answer_grid(meta)
            last=q['section']
        elif q['section']!='1A':story.append(PageBreak())
        if q['questionType']=='multiple-choice':
            group=[heading(q,True)]+blocks(q['stem'])+figure(q,155)
            for opt in q['options']:group+=blocks(f'**{opt["label"]}.** '+opt['text'],'part')
            # Keep the complete MCQ and all four choices together.
            story+=[CondPageBreak(90),KeepTogether(group)]
            # A final spacer can spill onto a new page immediately before the
            # explicit Paper1B break, leaving a header-only blank separator.
            if q['number'] < (40 if meta['course']=='hl' else 25):story.append(Spacer(1,18))
        else:
            story+=[heading(q)];story+=blocks(q['stem'])
            compact=(meta['id'],q['number']) in {
                ('physics-hl-set-a-paper-2',1),
                ('physics-hl-set-b-paper-2',5),('physics-hl-set-b-paper-2',8),('physics-hl-set-b-paper-2',9),
                ('physics-sl-set-b-paper-2',6)
            }
            story+=figure(q,170 if compact else 220)
            for p in q['parts']:
                story.append(KeepTogether(blocks(f'({p["label"]}) {p["prompt"]} [{p["marks"]}]','part')+[Spacer(1,3),Lines(p['marks']),Spacer(1,8)]))
    story+=[CondPageBreak(42),Spacer(1,12),Paragraph('End of question paper',S['heading'])]
    doc.build(story);trim_end_page(path,'End of question paper');return path,doc.qpages
def solutions(meta):
    path=BUILD/(meta['id']+'-solutions.pdf');doc=ExamDoc(path,meta,'Worked solutions');story=cover(meta,True);last=None
    for q in meta['questions']:
        if q['section']!=last:
            story += [PageBreak(),Paragraph({'1A':'Paper 1A - Answer key and explanations','1B':'Paper 1B - Worked solutions','2':'Paper 2 - Worked solutions'}[q['section']],S['heading'])]
            if q['section']=='1A':story+=answer_grid(meta,True)
            last=q['section']
        elif q['questionType']!='multiple-choice':story.append(PageBreak())
        if q['questionType']=='multiple-choice':
            group=[heading(q,True)]+blocks(f'**Correct answer: {q["correctOption"]}**','part')
            for step in q['markScheme'][0]['steps']:group+=blocks(step['text'],'mark')
            story+=[KeepTogether(group),Spacer(1,16)]
            continue
        story+=[heading(q)]
        for index,(p,g) in enumerate(zip(q['parts'],q['markScheme'])):
            assert p['label']==g['part']
            noun='mark' if p['marks']==1 else 'marks'
            story+=[CondPageBreak(75),Paragraph(f'({p["label"]}) <font size="10">[{p["marks"]} {noun}]</font>',S['heading'])]
            rows=[[Paragraph(step['code'],S['code']),blocks(step['text'],'mark')] for step in g['steps']]
            tb=Table(rows,colWidths=[35,BW-35],hAlign='LEFT');tb.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),4)]));story.append(tb)
            if index<len(q['parts'])-1:story.append(Spacer(1,11))
    story+=[CondPageBreak(42),Spacer(1,10),Paragraph('End of worked solution book',S['heading'])]
    doc.build(story);trim_end_page(path,'End of worked solution book');return path,doc.qpages
def build(meta):
    canonical=(ROOT/'content/ib/physics-mocks-2026/papers'/(meta['id']+'.json')).read_bytes()
    assert json.loads(canonical)==meta,'Content changed during PDF build'
    canonical_sha=hashlib.sha256(canonical).hexdigest();assert MANIFEST['sourcePapers'][meta['id']]==canonical_sha,'Stale math/figure assets'
    qp,qpages=questions(meta);sp,spages=solutions(meta);out=fitz.open();qd=fitz.open(qp);sd=fitz.open(sp);nq=len(qd)
    out.insert_pdf(qd);out.insert_pdf(sd)
    lookup={q['id']:qlabel(q) for q in meta['questions']}
    toc=[[1,'Question paper',1]]+[[2,lookup[i],p] for i,p in qpages.items()]+[[1,'Worked solution book',nq+1]]+[[2,lookup[i]+' solutions',nq+p] for i,p in spages.items()]
    out.set_toc(toc);out.set_metadata({'title':meta['title']+' - Question paper and worked solutions','author':'Thriving Scholars','subject':'Physics '+meta['course'].upper()+' - Challenge practice','creator':'Thriving Scholars','producer':'Thriving Scholars','keywords':'Physics, mock examination, worked solutions, 2026'})
    for i,page in enumerate(out):
        page.add_redact_annot(fitz.Rect(W-90,H-45,W-35,H-14),fill=(1,1,1),cross_out=False);page.apply_redactions(images=0,graphics=0,text=0)
        page.insert_text((W-65,H-30),str(i+1),fontname='helv',fontsize=8,color=(.45,.45,.45))
    raw=out.tobytes(garbage=4,deflate=True,no_new_id=True);name=meta['id']+'.pdf';(PUBLIC/name).write_bytes(raw);(DELIVER/name).write_bytes(raw)
    text='\n'.join(p.get_text() for p in out)
    assert not re.search(r'Christos|Nikolaidis|Revision Village|_SOLUTIONS|Microsoft Word|8825|2225|8826|2226',text,re.I)
    assert len(qpages)==len(meta['questions']) and len(spages)==len(meta['questions']),('Missing question bookmarks',meta['id'],len(qpages),len(spages))
    record={'id':meta['id'],'status':'passed','sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'pages':len(out),'questionPages':nq,'solutionPages':len(sd),'solutionsStartPage':nq+1,'questionStartPages':qpages,'solutionStartPages':{k:v+nq for k,v in spages.items()},'canonicalQuestionSha256':canonical_sha,'sourceAndDiagramAssetHashesVerified':True,'scientificAssetReportSha256':hashlib.sha256((DOC/'math-assets-checks.json').read_bytes()).hexdigest(),'brandingTextCheck':True,'bookmarks':len(toc),'publicFile':str(PUBLIC/name),'outputFile':str(DELIVER/name)}
    out.close();qd.close();sd.close();return record
if __name__=='__main__':
    records=[];selected=set(sys.argv[1:])
    for path in sorted((ROOT/'content/ib/physics-mocks-2026/papers').glob('*.json')):
        if selected and path.stem not in selected:continue
        meta=json.loads(path.read_text(encoding='utf8'));records.append(build(meta));print(json.dumps({k:records[-1][k] for k in ['id','pages','bytes']}),flush=True)
    ledger=DOC/'pdf-checks.json'
    if selected and ledger.exists():records=sorted([r for r in json.loads(ledger.read_text(encoding='utf8'))['papers'] if r['id'] not in selected]+records,key=lambda r:r['id'])
    ledger.write_text(json.dumps({'status':'passed','papers':records,'totalPages':sum(r['pages'] for r in records),'questionsFirst':True,'visualReviewRequired':True},indent=2)+'\n',encoding='utf8',newline='\n')
