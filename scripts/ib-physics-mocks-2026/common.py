"""Shared authoring helpers for the standalone Physics challenge papers."""
from pathlib import Path
import json, math, html, hashlib
ROOT=Path(__file__).resolve().parents[2]
TASK=ROOT.parent/'physics-mocks-2026'
CONTENT=ROOT/'content/ib/physics-mocks-2026/papers'
DOCS=ROOT/'docs/ib-physics-mocks-2026'
CONTENT.mkdir(parents=True,exist_ok=True);DOCS.mkdir(parents=True,exist_ok=True)
INK='#202020'; GREY='#777777'
def esc(t): return html.escape(str(t),quote=True)
def text(x,y,t,size=15,anchor='start',weight='normal'):
    return f'<text x="{x:g}" y="{y:g}" font-family="Arial, sans-serif" font-size="{size:g}" text-anchor="{anchor}" font-weight="{weight}" fill="{INK}">{esc(t)}</text>'
def line(x1,y1,x2,y2,dash=False,width=2):
    return f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{INK}" stroke-width="{width:g}"'+(' stroke-dasharray="6 5"' if dash else '')+'/>'
def arrow(x1,y1,x2,y2,label=None,lx=None,ly=None):
    a=math.atan2(y2-y1,x2-x1);s=9
    p=[(x2,y2),(x2-s*math.cos(a-.4),y2-s*math.sin(a-.4)),(x2-s*math.cos(a+.4),y2-s*math.sin(a+.4))]
    out=line(x1,y1,x2,y2)+f'<polygon points="'+ ' '.join(f'{x:g},{y:g}' for x,y in p)+f'" fill="{INK}"/>'
    return out+(text(lx if lx is not None else (x1+x2)/2,ly if ly is not None else (y1+y2)/2-10,label,14,'middle') if label else '')
def rect(x,y,w,h,label=None):
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="white" stroke="{INK}" stroke-width="2"/>'+ (text(x+w/2,y+h/2+5,label,15,'middle') if label else '')
def circle(x,y,r,label=None):
    return f'<circle cx="{x:g}" cy="{y:g}" r="{r:g}" fill="white" stroke="{INK}" stroke-width="2"/>'+ (text(x,y+5,label,15,'middle') if label else '')
def svg(body,w=600,h=280):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img">'+body+'</svg>'
def plot(points,xlim,ylim,xlabel,ylabel,xticks=(),yticks=(),labels=(),w=600,h=300,curve2=None):
    l,r,t,b=80,w-35,30,h-65
    def xy(p):return (l+(p[0]-xlim[0])/(xlim[1]-xlim[0])*(r-l),b-(p[1]-ylim[0])/(ylim[1]-ylim[0])*(b-t))
    body=line(l,t,l,b)+line(l,b,r,b)
    body+=text((l+r)/2,h-15,xlabel,15,'middle')+text(l,t-12,ylabel,14)
    for v in xticks:
        x,y=xy((v,ylim[0]));body+=line(x,b,x,b+5)+text(x,b+23,f'{v:g}',13,'middle')
    for v in yticks:
        x,y=xy((xlim[0],v));body+=line(l-5,y,l,y)+text(l-10,y+4,f'{v:g}',13,'end')
    for series,dash in [(points,False),(curve2,True)]:
        if not series:continue
        body+='<polyline points="'+' '.join(f'{xy(p)[0]:.2f},{xy(p)[1]:.2f}' for p in series)+f'" fill="none" stroke="{INK}" stroke-width="2.2"'+(' stroke-dasharray="7 5"' if dash else '')+'/>'
    for p,label,dx,dy in labels:
        x,y=xy(p);body+=f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3" fill="{INK}"/>'+text(x+dx,y+dy,label,14)
    return svg(body,w,h)
def scatter(points,xlim,ylim,xlabel,ylabel,xticks=(),yticks=(),fit=None,errors=None):
    raw=plot([],xlim,ylim,xlabel,ylabel,xticks,yticks)
    l,r,t,b=80,565,30,235
    def xy(p):return (l+(p[0]-xlim[0])/(xlim[1]-xlim[0])*(r-l),b-(p[1]-ylim[0])/(ylim[1]-ylim[0])*(b-t))
    body=''
    for i,p in enumerate(points):
        x,y=xy(p);body+=line(x-4,y-4,x+4,y+4)+line(x-4,y+4,x+4,y-4)
        if errors:
            ex,ey=errors[i];x0,y0=xy((p[0]-ex,p[1]-ey));x1,y1=xy((p[0]+ex,p[1]+ey))
            body+=line(x0,y,x1,y,width=1)+line(x0,y-4,x0,y+4,width=1)+line(x1,y-4,x1,y+4,width=1)+line(x,y0,x,y1,width=1)+line(x-4,y0,x+4,y0,width=1)+line(x-4,y1,x+4,y1,width=1)
    if fit:
        a,c=map(xy,fit);body+=line(*a,*c,width=1.5)
    return raw.replace('</svg>',body+'</svg>')
def anchor(doc,page,q,focus):
    assert (TASK/'sources'/Path(doc).stem/f'page-{page:03}.png').exists(),(doc,page)
    return {'document':doc,'page':page,'question':str(q),'focus':focus}
def paper(course,set_,paper_,questions):
    minutes=(120 if course=='hl' else 90) if paper_=='1' else (150 if course=='hl' else 90)
    marks=(60 if course=='hl' else 45) if paper_=='1' else (90 if course=='hl' else 50)
    out={'id':f'physics-{course}-set-{set_.lower()}-paper-{paper_}','mockId':f'physics-{course}-challenge-{set_.lower()}', 'course':course,'set':set_,'paper':paper_,'title':f'Physics {course.upper()} - Set {set_} - Paper '+('1A and 1B' if paper_=='1' else '2'),'minutes':minutes,'marks':marks,'calculator':True,'questions':questions}
    assert sum(q['marks'] for q in questions)==marks,(out['id'],sum(q['marks'] for q in questions),marks)
    for sec in sorted({q['section'] for q in questions}):
        assert [q['number'] for q in questions if q['section']==sec]==list(range(1,1+sum(q['section']==sec for q in questions)))
    (CONTENT/(out['id']+'.json')).write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf8',newline='\n')
    return out
class Author:
    def __init__(self,course,set_):self.course=course;self.set=set_;self.checks=[]
    def check(self,name,actual,expected,tol=1e-9):
        assert math.isfinite(actual) and abs(actual-expected)<=tol,(name,actual,expected,tol)
        self.checks.append({'name':name,'actual':actual,'expected':expected,'absoluteTolerance':tol,'passed':True});return actual
    def base(self,section,number,title,code,stem,source,changes,figure=None,level='core',demand=None):
        q={'id':f'phy-{self.course}-{self.set.lower()}-{section.lower()}-{number:02}', 'section':section,'number':number,'title':title,'syllabusCode':code,'syllabusRefs':[code],'level':level,'subtopic':title,'difficulty':'hard','stem':stem,'sourceAnchors':source if isinstance(source,list) else [source],'changeNotes':changes,'cognitiveDemand':demand or 'Link physical models, interpret conditions and justify the result.','verification':{'method':'Author calculation, dimensional and limiting-case checks','notes':'See the named reproducible author checks and worked solution for this question.'}}
        if figure:q['diagramSvg']=figure
        return q
    def mcq(self,number,title,code,stem,options,correct,solution,source,changes,figure=None,level='core',demand=None):
        q=self.base('1A',number,title,code,stem,source,changes,figure,level,demand)
        assert len(options)==4 and correct in 'ABCD' and len(set(options))==4
        q.update(questionType='multiple-choice',marks=1,parts=[],options=[{'label':l,'text':t} for l,t in zip('ABCD',options)],correctOption=correct,markScheme=[{'part':'','steps':[{'code':'A1','text':solution}]}],answerSummary=f'{correct}: {options["ABCD".index(correct)]}')
        return q
    def written(self,section,number,title,code,stem,parts,solutions,source,changes,figure=None,level='core',demand=None):
        q=self.base(section,number,title,code,stem,source,changes,figure,level,demand)
        q.update(questionType='data-based' if section=='1B' else 'structured',parts=[{'label':l,'prompt':p,'marks':m} for l,p,m in parts],marks=sum(x[2] for x in parts),markScheme=[{'part':p,'steps':[{'code':c,'text':t} for c,t in steps]} for p,steps in solutions],answerSummary='; '.join(f'({p}) '+steps[-1][1] for p,steps in solutions))
        assert [p['label'] for p in q['parts']]==[g['part'] for g in q['markScheme']]
        for p,g in zip(q['parts'],q['markScheme']):assert p['marks']==sum(int(s['code'][1:]) for s in g['steps']),(q['id'],p['label'])
        return q
    def save_checks(self,name):
        (DOCS/(name+'-author-checks.json')).write_text(json.dumps({'status':'passed','course':self.course,'set':self.set,'method':'Reproducible authored calculations; independent review required before publication.','checks':self.checks},indent=2)+'\n',encoding='utf8',newline='\n')
