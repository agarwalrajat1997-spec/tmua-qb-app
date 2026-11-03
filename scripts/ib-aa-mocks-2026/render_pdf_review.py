"""Render every final PDF page and bounded contact sheets for visual review."""
from pathlib import Path
import sys,os,json
ROOT=Path(__file__).resolve().parents[2]
WORK=Path(os.environ.get('IB_AA_MOCK_WORK',ROOT.parent/'aa-mocks-2026'))
sys.path.insert(0,str(WORK/'python-deps'))
import fitz
from PIL import Image,ImageOps,ImageDraw
DEST=WORK/'pdf-review';DEST.mkdir(parents=True,exist_ok=True)
reports=[]
selected=sys.argv[1:]
for pdf in sorted((ROOT/'public/ib-mock-solutions').glob('aa-*.pdf')):
    if selected and pdf.stem not in selected:continue
    doc=fitz.open(pdf);out=DEST/pdf.stem;out.mkdir(exist_ok=True)
    thumbs=[];bounds=[]
    for i,page in enumerate(doc):
        pix=page.get_pixmap(matrix=fitz.Matrix(1.6,1.6),alpha=False)
        file=out/f'page-{i+1:03}.png';pix.save(file)
        image=Image.open(file).convert('RGB');image.thumbnail((300,425))
        cell=Image.new('RGB',(310,452),'#ededed');cell.paste(image,((310-image.width)//2,24));ImageDraw.Draw(cell).text((8,6),f'Page {i+1}',fill='black');thumbs.append(cell)
        for b in page.get_text('blocks'):
            if b[0]<-1 or b[1]<-1 or b[2]>page.rect.width+1 or b[3]>page.rect.height+1:bounds.append({'page':i+1,'bbox':list(b[:4])})
    for start in range(0,len(thumbs),12):
        cells=thumbs[start:start+12];sheet=Image.new('RGB',(930,452*((len(cells)+2)//3)),'#ddd')
        for j,im in enumerate(cells):sheet.paste(im,((j%3)*310,(j//3)*452))
        sheet.save(out/f'contact-{start//12+1:02}.png')
    assert not bounds,(pdf.name,bounds)
    reports.append({'id':pdf.stem,'pagesRendered':len(doc),'outOfPageText':bounds})
ledger_path=ROOT/'docs/ib-aa-mocks-2026/pdf-render-checks.json'
if selected and ledger_path.exists():reports=sorted([r for r in json.loads(ledger_path.read_text(encoding='utf8'))['records'] if r['id'] not in selected]+reports,key=lambda r:r['id'])
ledger={'status':'rendered; human-visible AI inspection pending','papers':len(reports),'pages':sum(r['pagesRendered'] for r in reports),'records':reports}
(ROOT/'docs/ib-aa-mocks-2026/pdf-render-checks.json').write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps({'papers':len(reports),'pages':ledger['pages'],'allTextWithinPages':True,'folder':str(DEST)}))
