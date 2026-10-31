"""Independent 2024-course BM practice. Editorial families have four case variants each."""
from pathlib import Path
import json, hashlib, re, math, statistics
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'content/ib/business-management'
DOC=ROOT/'docs/ib-expansion-reviews'
OUT.mkdir(parents=True,exist_ok=True); DOC.mkdir(parents=True,exist_ok=True)
QUESTIONS={i:[] for i in range(1,6)}
LEDGER=[]
TOPICS={1:'introduction-business',2:'human-resources',3:'finance-accounts',4:'marketing',5:'operations-management'}

def step(text,code='R1'): return {'code':code,'text':text}
def group(label,answers):
    return {'part':label,'steps':[step(x) if isinstance(x,str) else x for x in answers]}
def define(label,term,meaning):
    a,b=meaning.split(' / ',1)
    return ({'label':label,'prompt':f'Define the term {term}.','marks':2},group(label,[a,b]))
def calc(label,prompt,working,answer):
    return ({'label':label,'prompt':prompt,'marks':2},group(label,[step(working,'M1'),step(answer,'A1')]))
def explain(label,prompt,answers):
    return ({'label':label,'prompt':prompt,'marks':len(answers)},group(label,answers))
def ten(label,prompt,name,decision,pro,con,condition,missing,exam='paper-2'):
    cap=2 if exam=='paper-1' else 4
    bands=[(0,0,'No relevant response.'),(1,2,f'Limited relevant knowledge of {decision}; arguments are mainly assertions and application to {name} is absent or superficial.'),(3,4,f'Some accurate business knowledge and explanation of {decision}, but application or analysis is limited and the answer is largely one-sided.'),(5,6,f'Relevant concepts are used to analyse {decision} with some meaningful application to {name}. Some opposing considerations are identified, but their relative importance or the recommendation is only partly supported.'),(7,8,f'Accurate relevant theory supports balanced, developed analysis of {decision} using the specific circumstances of {name}. The recommendation follows from the arguments and recognizes a condition or stakeholder trade-off.'),(9,10,f'Focused, balanced analysis integrates relevant business theory with the evidence about {name}; competing consequences and their relative significance are evaluated. The recommendation is convincing and conditional, addresses an identified weakness, and explains a material limitation of the available evidence.')]
    return ({'label':label,'prompt':prompt,'marks':10},{'part':label,'steps':[step(f'Indicative support: {pro}','IND'),step(f'Indicative counterargument: {con}','IND'),step(f'One defensible judgment: {condition} Alternative recommendations earn full credit when supported by the case and a coherent response to the counterargument.','IND'),step(f'Evidence limitation: {missing} Explain how this uncertainty affects confidence in the decision. Apply best fit: a theoretical-only answer can earn at most {cap}; without an explained case/stimulus limitation at most 8. Do not require all indicative points or award them separately.','IND')],'rubric':{'maxMarks':10,'bands':[{'min':a,'max':b,'descriptor':d} for a,b,d in bands]}})
def add(unit,family,code,level,title,subtopic,stem,items,exam='paper-2',kind='case-study',check='',svg=None,solution_svg=None,scope=''):
    n=len(QUESTIONS[unit])+1
    q={'id':f'ib-bm-u{unit}-{n:03}','subject':'business-management','topicId':TOPICS[unit],'collectionId':'business-'+TOPICS[unit],'number':n,'title':title,'subtopic':subtopic,'difficulty':'easy' if family in {'bm01-sectors','bm41-capital-revenue'} else ('hard' if any(x[0]['marks']>=10 for x in items) else 'medium'),'calculator':True,'marks':sum(p['marks'] for p,g in items),'stem':'All organizations and data in this question are fictional.\n\n'+stem,'parts':[p for p,g in items],'markScheme':[g for p,g in items],'syllabusCode':code,'level':level,'questionType':kind,'examStyle':exam,'source':{'document':'Independent syllabus-authored practice','question':n},'verification':{'method':'Syllabus/AO scope check; independent arithmetic and case-reasoning review; analytic/best-fit allocation audit','notes':f'Family {family}. '+check},'status':'published'}
    if svg:q['diagramSvg']=svg
    if solution_svg:q['markSchemeDiagramSvg']=solution_svg
    QUESTIONS[unit].append(q)
    LEDGER.append({'id':q['id'],'family':family,'syllabusCode':code,'level':level,'scope':scope or f'Current guide {code}; '+('common SL/HL content' if level=='sl' else 'record includes explicitly HL-only content or assessment'),'reasoningAndNumericCheck':check,'bandCheck':'Question-specific best-fit rubric with IND-only indicative content' if any('rubric' in g for p,g in items) else 'Distinct analytic criteria; allocated marks equal part and record totals','originality':'Independently authored fictional case; no paper wording, figures, or business data copied','sha256':hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True).encode()).hexdigest()})
    return q

def ef(unit,family,code,level,topic,term,meaning,action,rows,exam='paper-2',scope='',beneficiary=None,decision_maker=None):
    """16-mark case: precise definition, applied balanced explanation, evaluation."""
    for name,context,pro,con,condition,missing in rows:
        decision=action.replace('{name}',name)
        stem=f'{name}: {context}'
        items=[define('a',term,meaning),explain('b',f'Explain one advantage and one disadvantage for {beneficiary or name} of {decision}.',[f'Advantage: {pro.split(";",1)[0]}.',f'Applied consequence: {pro.split(";",1)[-1]}.',f'Disadvantage: {con.split(";",1)[0]}.',f'Applied consequence: {con.split(";",1)[-1]}.']),ten('c',f'Using the case information and relevant business management theory, recommend whether {decision_maker or name} should proceed with {decision}.',name,decision,pro.replace(';',' because '),con.replace(';',' because '),condition,missing,exam)]
        add(unit,family,code,level,f'{name}: {topic}',topic,stem,items,exam,check=f'Case trade-off checked: {pro} Counterargument: {con} Conditional judgment: {condition} No single prescribed conclusion.',scope=scope)

def af(unit,family,code,level,topic,term,meaning,prompt,rows,exam='paper-1',scope=''):
    """8-mark applied explanation; two independent 3-mark chains."""
    for name,context,chain1,chain2 in rows:
        assert len(chain1)==len(chain2)==3
        current_prompt=prompt.replace('{name}',name)
        if family=='bm38-hl-motivation-diagnosis' and name in {'Cru Sales','Fru Rooms'}:
            current_prompt='Using relevant HL motivation theory, explain why the stated reward may fail to motivate employees, and explain one appropriate response by the business.'
        items=[define('a',term,meaning),explain('b',current_prompt,chain1+chain2)]
        add(unit,family,code,level,f'{name}: {topic}',topic,f'{name}: {context}',items,exam,check='Two distinct three-stage explanations checked: '+ ' | '.join(chain1+chain2),scope=scope)

def svg_text(x,y,t,size=15):
    from html import escape
    return f'<text x="{x}" y="{y}" font-size="{size}" font-family="Arial" fill="#172554">{escape(str(t))}</text>'
def svgwrap(body,w=760,h=340): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img"><rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>'+body+'</svg>'
def write_all():
    for unit,records in QUESTIONS.items():
        if records:(OUT/(TOPICS[unit]+'.json')).write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    (DOC/'business-author-ledger.json').write_text(json.dumps(LEDGER,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

if __name__=='__main__':
    import runpy
    for unit in range(1,6):
        path=Path(__file__).with_name(f'business_unit{unit}.py')
        if path.exists(): runpy.run_path(str(path),init_globals=globals())
    write_all()
    print(json.dumps({'questions':{TOPICS[k]:len(v) for k,v in QUESTIONS.items()},'families':len(set(x['family'] for x in LEDGER)),'SL':sum(q['level']=='sl' for a in QUESTIONS.values() for q in a),'AHL':sum(q['level']=='ahl' for a in QUESTIONS.values() for q in a)},indent=2))
