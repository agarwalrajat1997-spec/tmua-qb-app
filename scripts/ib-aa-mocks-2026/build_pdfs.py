"""Build branded question papers followed by corrected supplied solution books.

Run render_pdf_math.cjs first. Source PDFs are never overwritten. Dependencies
live in IB_AA_MOCK_WORK/python-deps; no production dependency is introduced.
"""
from pathlib import Path
import sys,os,json,re,html,math,hashlib,io
ROOT=Path(__file__).resolve().parents[2]
WORK=Path(os.environ.get('IB_AA_MOCK_WORK',ROOT.parent/'aa-mocks-2026'))
sys.path.insert(0,str(WORK/'python-deps'))
import fitz
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate,Frame,PageTemplate,Paragraph,Spacer,PageBreak,Image,Table,TableStyle,Flowable,KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ASSETS=WORK/'pdf-assets';MANIFEST=json.loads((ASSETS/'manifest.json').read_text(encoding='utf8'))
INVENTORY=json.loads((WORK/'source-inventory/inventory.json').read_text(encoding='utf8'))
SOURCES={p['key']:p for p in INVENTORY['papers']}
BUILD=WORK/'pdf-build';BUILD.mkdir(exist_ok=True,parents=True)
PUBLIC=ROOT/'public/ib-mock-solutions';PUBLIC.mkdir(exist_ok=True,parents=True)
DELIVER=ROOT.parents[1]/'outputs/IB_AA_Mock_Exams';DELIVER.mkdir(exist_ok=True,parents=True)
W,H=A4;BURG=colors.HexColor('#771d27');GOLD=colors.HexColor('#ffce53');INK=colors.HexColor('#202020');GREY=colors.HexColor('#777777')
for name,file in [('Exam','times.ttf'),('ExamBold','timesbd.ttf'),('Brand','arial.ttf'),('BrandBold','arialbd.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+file))
STYLES={
 'body':ParagraphStyle('body',fontName='Exam',fontSize=11.5,leading=17,spaceAfter=10,autoLeading='max',textColor=INK),
 'part':ParagraphStyle('part',fontName='Exam',fontSize=11.5,leading=17,spaceAfter=6,autoLeading='max',textColor=INK),
 'heading':ParagraphStyle('heading',fontName='BrandBold',fontSize=15,leading=21,spaceAfter=14,textColor=BURG),
 'small':ParagraphStyle('small',fontName='Brand',fontSize=9,leading=13,spaceAfter=8,textColor=INK),
 'table':ParagraphStyle('table',fontName='Exam',fontSize=10.5,leading=16,autoLeading='max',alignment=1),
}
class Lines(Flowable):
    def __init__(self,marks):Flowable.__init__(self);self.width=W-116;self.height=min(88,max(24,marks*8))
    def draw(self):
        self.canv.setStrokeColor(colors.HexColor('#d8d8d8'));self.canv.setLineWidth(.45)
        for y in range(5,int(self.height),16):self.canv.line(0,y,self.width,y)
def brand(c,label=''):
    c.setFillColor(GOLD);c.roundRect(36,H-42,26,26,5,stroke=0,fill=1)
    c.setFillColor(BURG);c.setFont('BrandBold',10);c.drawCentredString(49,H-34,'ts')
    c.setFont('BrandBold',10);c.drawString(71,H-31,'Thriving Scholars')
    c.setFont('Brand',8);c.drawRightString(W-36,H-31,label)
    c.setStrokeColor(GOLD);c.setLineWidth(1.1);c.line(36,H-52,W-36,H-52)
class ExamDoc(BaseDocTemplate):
    def __init__(self,path,meta):
        BaseDocTemplate.__init__(self,str(path),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=74,bottomMargin=49,title=meta['title'],author='Thriving Scholars')
        self.meta=meta;self.qpages={}
        self.addPageTemplates(PageTemplate(id='exam',frames=[Frame(48,49,W-96,H-123,id='main',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=self.header))
    def header(self,c,doc):brand(c,f"AA {self.meta['course'].upper()}  |  Set {self.meta['set']}  |  Paper {self.meta['paper']}")
    def afterFlowable(self,f):
        if hasattr(f,'questionNumber'):self.qpages[f.questionNumber]=self.page
def inline(text,size=11.5):
    result=[];start=0
    for m in re.finditer(r'\$\$([\s\S]*?)\$\$|\$([^$\n]+?)\$',text):
        result.append(html.escape(text[start:m.start()]))
        tex=(m.group(1) or m.group(2)).strip();info=MANIFEST['math'][tex]
        wi=info['widthEm']*size;he=info['heightEm']*size;depth=info['depthEm']*size
        scale=min(1,(W-110)/wi);wi*=scale;he*=scale;depth*=scale
        result.append(f'<img src="{ASSETS/info["file"]}" width="{wi:.4f}" height="{he:.4f}" valign="{depth:.4f}"/>')
        start=m.end()
    result.append(html.escape(text[start:]));v=''.join(result)
    v=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',v);v=re.sub(r'`([^`]+)`',r'\1',v)
    return v
def blocks(text,style='body'):
    output=[]
    for block in re.split(r'\n\s*\n',text.strip()):
        if not block:continue
        if block.strip().startswith('$$') and block.strip().endswith('$$'):
            tex=block.strip()[2:-2].strip();info=MANIFEST['math'][tex]
            wi=info['widthEm']*11.5;he=info['heightEm']*11.5;scale=min(1,(W-110)/wi)
            im=Image(str(ASSETS/info['file']),width=wi*scale,height=he*scale);im.hAlign='LEFT'
            output.extend([im,Spacer(1,13)]);continue
        lines=block.splitlines()
        if any(l.strip().startswith('|') for l in lines):
            tables=[l for l in lines if l.strip().startswith('|') and not re.fullmatch(r'[\s|:\-]+',l)]
            prose=[l for l in lines if not l.strip().startswith('|')]
            if prose:output.append(Paragraph(inline(' '.join(prose)),STYLES[style]))
            rows=[[Paragraph(inline(x.strip(),10.5),STYLES['table']) for x in l.strip().strip('|').split('|')] for l in tables]
            if rows:
                cols=max(len(r) for r in rows);rows=[r+[Paragraph('',STYLES['table'])]*(cols-len(r)) for r in rows]
                tb=Table(rows,colWidths=[(W-102)/cols]*cols,hAlign='LEFT')
                tb.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.5,colors.HexColor('#b5b5b5')),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#fff5db')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
                output.extend([tb,Spacer(1,12)])
        else:output.append(Paragraph(inline('<br/>'.join(lines).replace('<br/>','\n')).replace('\n','<br/>'),STYLES[style]))
    return output
def cover(meta,solutions=False):
    story=[Spacer(1,52),Paragraph('MATHEMATICS',ParagraphStyle('cap',fontName='BrandBold',fontSize=12,leading=18,textColor=BURG,spaceAfter=13)),
      Paragraph('Analysis and approaches',ParagraphStyle('ttl',fontName='BrandBold',fontSize=28,leading=35,spaceAfter=17,textColor=INK)),
      Paragraph(('Higher Level' if meta['course']=='hl' else 'Standard Level')+f"  |  Set {meta['set']}  |  Paper {meta['paper']}",ParagraphStyle('sub',fontName='Brand',fontSize=15,leading=23,spaceAfter=22)),
      Paragraph('Worked solution book' if solutions else 'Mock examination · 2025 series',ParagraphStyle('book',fontName='BrandBold',fontSize=16,leading=23,textColor=BURG,spaceAfter=26))]
    if solutions:
        story+=blocks('This section contains the worked solutions and marking points. Use it after completing the question paper. Award method, accuracy and reasoning marks separately, and accept mathematically equivalent valid methods.','body')
        story+=blocks('Mark your written working against the solution book before entering self-assessed marks in the portal. A correct final answer does not always earn every method or proof mark.','body')
    else:
        timing={75:'1 hour 15 minutes',90:'1 hour 30 minutes',120:'2 hours'}[meta['minutes']]
        story+=[Paragraph(f'Time allowed: <b>{timing}</b> &nbsp;&nbsp;&nbsp; Maximum mark: <b>{meta["marks"]}</b>',STYLES['body']),Spacer(1,12)]
        for label in ['Candidate name','Candidate number','Date']:
            story+=[Paragraph(label+': __________________________________________________',STYLES['body'])]
        instructions=[('A graphic display calculator is required.' if meta['calculator'] else 'A calculator is not permitted.'),
          'Answer every question. Show all working and give sufficient mathematical reasoning.',
          'A clean Mathematics: analysis and approaches formula booklet may be used.',
          'Give exact answers where appropriate. Otherwise give numerical answers to three significant figures unless instructed differently.',
          'Diagrams are not necessarily drawn to scale. Use the stated measurements and conditions.',
          'The number in square brackets shows the maximum mark for each part.']
        if meta['paper']!='3':instructions.insert(1,'This paper has Section A and Section B. Both sections are compulsory.')
        else:instructions.insert(1,'This paper contains two compulsory extended problem-solving questions.')
        story+=[Spacer(1,15),Paragraph('Instructions',STYLES['heading'])]
        for item in instructions:story+=blocks('• '+item,'small')
    return story
def question_paper(meta):
    file=BUILD/(meta['id']+'-questions.pdf');doc=ExamDoc(file,meta);story=cover(meta)
    for q in meta['questions']:
        story.append(PageBreak())
        if q['section']:story.append(Paragraph('SECTION '+q['section'],STYLES['small']))
        heading=Paragraph(f'Question {q["number"]} <font size="10">[Maximum mark: {q["marks"]}]</font>',STYLES['heading']);heading.questionNumber=q['number'];story.append(heading)
        stem=q['stem']
        if meta['id']=='aa-hl-set-b-paper-1' and q['number']==11:
            stem=re.sub(r'\$(\\displaystyle I_n=.*?)\$',lambda m:'\n\n$$'+m[1]+'$$',stem)
        story+=blocks(stem)
        image=MANIFEST['diagrams'].get(meta['id']+'-q'+str(q['number']))
        if image:
            im=Image(str(ASSETS/image));ratio=min(1,(W-118)/im.imageWidth,230/im.imageHeight);im.drawWidth=im.imageWidth*ratio;im.drawHeight=im.imageHeight*ratio;im.hAlign='CENTER';story.extend([im,Spacer(1,12)])
        for part in q['parts']:
            label=('('+part['label'].replace('(',')(')+')') if part['label'] else ''
            text=(label+' '+part['prompt']).strip()+f' [{part["marks"]}]'
            ps=blocks(text,'part');story.append(KeepTogether(ps+[Spacer(1,3),Lines(part['marks']),Spacer(1,8)]))
    story.extend([Spacer(1,12),Paragraph('End of question paper',STYLES['heading'])]);doc.build(story)
    rendered=fitz.open(file);tail=' '.join(rendered[-1].get_text().split())
    label=f"AA {meta['course'].upper()} | Set {meta['set']} | Paper {meta['paper']}"
    tail=tail.replace('Thriving Scholars','').replace(label,'').replace('ts','').replace('End of question paper','').strip()
    if not tail and len(rendered)>1:
        rendered.delete_page(len(rendered)-1);data=rendered.tobytes(garbage=4,deflate=True);rendered.close();file.write_bytes(data)
    else:rendered.close()
    return file,doc.qpages
def rawchars(page):
    rows=[]
    for block in page.get_text('rawdict')['blocks']:
        for line in block.get('lines',[]):
            for span in line['spans']:
                for char in span['chars']:rows.append({**char,'size':span['size'],'font':span['font'],'color':span['color']})
    return rows
def glyph_patch(page,rect,newtext):
    rect=fitz.Rect(rect);chars=[c for c in rawchars(page) if rect.contains(fitz.Point((c['bbox'][0]+c['bbox'][2])/2,(c['bbox'][1]+c['bbox'][3])/2)) and c['c'].strip()]
    if not chars:raise ValueError('No glyph at '+str(rect))
    baseline=sum(c['origin'][1] for c in chars)/len(chars);size=max(c['size'] for c in chars)
    x0=min(c['bbox'][0] for c in chars);x1=max(c['bbox'][2] for c in chars)
    for c in chars:
        r=fitz.Rect(c['bbox']);cx=(r.x0+r.x1)/2;cy=(r.y0+r.y1)/2
        page.add_redact_annot(fitz.Rect(cx-r.width*.22,cy-r.height*.22,cx+r.width*.22,cy+r.height*.22),fill=(1,1,1),cross_out=False)
    page.apply_redactions(images=2,graphics=0,text=0)
    font='tiit' if any('Italic' in c['font'] for c in chars) or newtext in ['p','h','y'] else 'tiro'
    width=fitz.get_text_length(newtext,fontname=font,fontsize=size)
    rgb=tuple(((chars[0]['color']>>s)&255)/255 for s in [16,8,0])
    page.insert_text(((x0+x1-width)/2,baseline),newtext,fontname=font,fontsize=size,color=rgb)
def text_patch(page,rect,text='',size=11,font='helv',color=(0,0,0)):
    r=fitz.Rect(rect);page.add_redact_annot(r,fill=(1,1,1),cross_out=False);page.apply_redactions(images=2,graphics=0,text=0)
    if text:page.insert_text((r.x0+1,r.y1-2.5),text,fontname=font,fontsize=size,color=color)
def patch_source(meta,source):
    applied=[]
    sl=json.loads((ROOT/'docs/ib-aa-mocks-2026/sl-author-review.json').read_text(encoding='utf8'))['sourceErrata']
    for err in sl:
        if err['paper']!=meta['id']:continue
        page=source[err['sourcePage']-1]
        if 'replaceGlyphRegions' in err:
            for region in err['replaceGlyphRegions']:glyph_patch(page,region,err['replacementGlyph'])
        elif 'removeTextRegion' in err:text_patch(page,err['removeTextRegion'])
        elif meta['id']=='aa-sl-set-b-paper-1':text_patch(page,err['replaceTextRegion'],'x-intercept at -4')
        elif meta['id']=='aa-sl-set-a-paper-2':
            boxes=[r for r in page.search_for('(d)') if fitz.Rect(err['replaceTextRegion']).intersects(r)]
            if not boxes:raise ValueError('Cannot locate corrected area part-reference')
            glyph_patch(page,boxes[0],'(e)')
        applied.append({'sourcePage':err['sourcePage'],'question':err['question'],'correction':err['correction']})
    config=json.loads((WORK/'source-inventory/hl-a-b-source-patch-coordinates.json').read_text(encoding='utf8'))
    for patch in config['patches']:
        if patch['paper']!=meta['id']:continue
        page=source[patch['sourcePage']-1]
        if patch['question']==8 and 'minimumGlyphBox' in patch:glyph_patch(page,patch['minimumGlyphBox'],'+')
        elif patch['question']==5:glyph_patch(page,patch['minimumGlyphBox'],'6')
        elif patch.get('replacementText')=='P':text_patch(page,patch['textBox'],'P',size=7,font='tiro')
        else:text_patch(page,patch['textBox'],patch['replacementText'])
        applied.append({'sourcePage':patch['sourcePage'],'question':patch['question'],'correction':patch.get('replacementText',patch.get('replacementLatex'))})
    if meta['id']=='aa-hl-set-b-paper-1':
        for region in [(135,303,140,315),(135,362,140,375)]:glyph_patch(source[1],region,'y')
        text_patch(source[10],(96.8,425.5,176,438),'x-intercept at -4')
        text_patch(source[10],(162.8,695,197,710))
        text_patch(source[12],(96.8,221,226,236),'Prove it is true for n = k + 1,')
        applied.extend([{'sourcePage':2,'question':1,'correction':'Both plane equations use6y, not6z.'},{'sourcePage':11,'question':10,'correction':'Inverse intercept -4 and false intermediate identity removed.'},{'sourcePage':13,'question':11,'correction':'Induction target n=k+1.'}])
    if meta['id']=='aa-hl-set-b-paper-2':
        text_patch(source[9],(278.5,238.3,305,251),'9.34°',size=12,font='tiro')
        glyph_patch(source[11],(245.4,621,251.5,633.2),'6');glyph_patch(source[11],(222.5,658.3,228.6,670.5),'6')
        glyph_patch(source[11],(208,530,216,542.4),'h')
        applied.extend([{'sourcePage':10,'question':9,'correction':'Angle9.34degrees.'},{'sourcePage':12,'question':11,'correction':'Derivative coefficient6a² and height symbolh.'}])
    # Remove obsolete alternative-version editorial prose, not mathematical content.
    if meta['id']=='aa-sl-set-a-paper-1':text_patch(source[9],(65,678,580,742))
    for page in source:
        page.add_redact_annot(fitz.Rect(0,0,page.rect.width,58),fill=(1,1,1),cross_out=False)
        for block in page.get_text('blocks'):
            if re.search(r'Christos|Nikolaidis|CN/MOCK25',block[4],re.I):page.add_redact_annot(fitz.Rect(block[:4]),fill=(1,1,1),cross_out=False)
        page.apply_redactions(images=2,graphics=0,text=0)
    return applied
def overlay_page(meta,number,total):
    buf=io.BytesIO();c=canvas.Canvas(buf,pagesize=A4);brand(c,f"AA {meta['course'].upper()}  |  Set {meta['set']}  |  Paper {meta['paper']}")
    c.setFont('Brand',8);c.setFillColor(GREY);c.drawString(36,25,'Thriving Scholars · Mathematics AA');c.drawRightString(W-36,25,f'Page {number} of {total}');c.save()
    return fitz.open(stream=buf.getvalue(),filetype='pdf')
def build(meta):
    qp,qpages=question_paper(meta)
    solcover=BUILD/(meta['id']+'-solution-cover.pdf');ExamDoc(solcover,meta).build(cover(meta,True))
    srcinfo=SOURCES[meta['id']];srcpath=Path(srcinfo['path'])
    assert hashlib.sha256(srcpath.read_bytes()).hexdigest()==srcinfo['sha256'],'Source changed since inventory'
    source=fitz.open(srcpath);patches=patch_source(meta,source)
    final=fitz.open(qp);question_pages=len(final);final.insert_pdf(fitz.open(solcover));solution_intro=question_pages+1
    for ix in range(1,len(source)):
        page=final.new_page(width=W,height=H)
        page.show_pdf_page(fitz.Rect(0,25,W,H-25),source,ix,keep_proportion=True)
    for ix,page in enumerate(final):
        overlay=overlay_page(meta,ix+1,len(final));page.show_pdf_page(page.rect,overlay,0)
    final.set_metadata({'title':meta['title']+' — Question paper and worked solutions','author':'Thriving Scholars','creator':'Thriving Scholars','producer':'Thriving Scholars','subject':'Timed mock examination, followed by the corrected worked solution book'})
    final.del_xml_metadata();toc=[[1,'Question paper',1]]+[[2,'Question '+str(n),page] for n,page in qpages.items()]+[[1,'Worked solution book',solution_intro]]
    final.set_toc(toc)
    file=PUBLIC/(meta['id']+'.pdf');final.save(file,garbage=4,deflate=True);final.close()
    reopened=fitz.open(file);text='\n'.join(p.get_text() for p in reopened)
    assert not re.search(r'Christos|Nikolaidis|CN/MOCK25|_SOLUTIONS|Microsoft Word|PrimoPDF',text,re.I),meta['id']+' residual notation'
    assert all(abs(p.rect.width-W)<.01 and abs(p.rect.height-H)<.01 for p in reopened)
    assert reopened.metadata['author']=='Thriving Scholars'
    (DELIVER/file.name).write_bytes(file.read_bytes())
    return {'id':meta['id'],'status':'passed','questions':len(meta['questions']),'marks':meta['marks'],'minutes':meta['minutes'],'questionPaperPages':question_pages,'solutionBookStartsAtPage':solution_intro,'totalPages':len(reopened),'diagrams':sum(bool(q.get('diagramSvg')) for q in meta['questions']),'sourceSolutionsRetained':len(source)-1,'sourceCorrections':patches,'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'questionStartPages':qpages,'pdfUrl':'/ib-mock-solutions/'+file.name}
if __name__=='__main__':
    selected=sys.argv[1:];records=[]
    for file in sorted((ROOT/'content/ib/aa-mocks-2026/papers').glob('*.json')):
        meta=json.loads(file.read_text(encoding='utf8'))
        if selected and meta['id'] not in selected:continue
        r=build(meta);records.append(r);print(json.dumps({k:r[k] for k in ['id','questions','questionPaperPages','totalPages','sourceSolutionsRetained']}),flush=True)
    ledger=ROOT/'docs/ib-aa-mocks-2026/pdf-checks.json'
    if selected and ledger.exists():
        old=json.loads(ledger.read_text(encoding='utf8'))['records']
        records=sorted([r for r in old if r['id'] not in selected]+records,key=lambda r:r['id'])
    ledger.write_text(json.dumps({'status':'built; visual review pending','papers':len(records),'records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
