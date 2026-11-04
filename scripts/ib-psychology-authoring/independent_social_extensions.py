"""Reproduce root's completed independent review, without approving changed work.

The adjacent fixed pins were recorded only after all 80 full stems, indicative
answers and rubrics, and all 18 native/mobile figure pairs, were actually read.
This script recomputes numeric/geometry checks but never refreshes those pins.
Independent AI review is not human IB examiner moderation.
"""
from pathlib import Path
import hashlib
import json
import statistics
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / 'docs/ib-psychology-reviews'
GUIDE = 'https://ibo.org/globalassets/new-structure/university-admission/pdfs/subject-guides/psychology-first-assessment-2027-guide-sbs.pdf'
CHUA = 'https://pmc.ncbi.nlm.nih.gov/articles/PMC1194960/'
RAYNER = 'https://pmc.ncbi.nlm.nih.gov/articles/PMC2048814/'
REVIEWED_FILES = {
    'content/ib/psychology/sociocultural-approach.json': 'b311e134f1104ee3ffadadb107daa06d69429caf3a90c956fb3c30bf21687285',
    'content/ib/psychology/culture.json': '74f57d2ee56c6d286cc88c25c7f2babc7476a6b66d3a7682e15140ab1ceaf10a',
    'content/ib/psychology/motivation.json': 'db6bb0cbbd293970302d984009466c196b72ea6942529f63ce942e5d76a8f3a9',
}
BANDS = {3:[[0,0],[1,1],[2,2],[3,3]],4:[[0,0],[1,2],[3,4]],6:[[0,0],[1,2],[3,4],[5,6]],15:[[0,0],[1,3],[4,6],[7,9],[10,12],[13,15]]}

CUL = [
    'The chart correctly displays fictional community means24 and32 on the0–40 scale. A mean contrast cannot rank most individuals: valid integer samples within the scale can have the lower-mean community with the higher median. No individual distribution or clinical threshold is supplied.',
    'The revised demand analyzes Source B alone. The same12 bilingual participants average31 with literal wording and25 with localized wording, a6-point paired contrast. Counterbalancing helps order effects but cannot establish which translation measures a true culture difference or resolve unknown paired uncertainty.',
    'The clinic employee’s question presupposes both cultural difficulty and pathological worry. The scheme connects interviewer authority and leading wording to accounts that distinguish ordinary concern from disrupted sleep; neutral prompts, reflexivity and contrasting accounts address this specific bias.',
    'The synthesis genuinely uses A, B and C to distinguish construct meaning from deterministic cultural ranking. Emic and etic interpretations can inform measurement without treating localized wording as automatically correct or dismissing genuine impairment when distress is understood differently.',
    'Helping percentages count20 opportunities per age/community, not20 independent children. Two opportunities per each of10 children leave consistency unknown:12 helping events could come from six children helping twice or all ten helping at least once. The model preserves that unit limitation.',
    'The revised analysis is confined to Source A: the age contrasts are20 and40 percentage points, with a20-point community contrast at age4 and none at age8. Cross-sectional groups do not demonstrate within-child development or establish that one community cares less.',
    'Caregiver accounts describe noticing a need versus waiting for permission; the director’s lack-of-caring code assumes one interpretation. The credibility discussion considers role, recruitment and neutral comparison of divergent accounts, rather than treating a cultural label as a validated motive measure.',
    'Spontaneous helping does not uniquely measure developmental speed. The separate older sample receiving invitation plus demonstration changes both participants and procedure, so its90% cannot isolate one mechanism. The synthesis uses cultural meanings and functional measurement without ranking inherent caring.',
    'The Source A axis intentionally starts at3 on the1–5 belonging scale, making4.2 versus3.6 look twice as tall above the displayed baseline. The answer correctly treats this as visual amplification, not evidence that either psychological belonging or the underlying numerical score is doubled.',
    'Source A alone supports a0.6-point extreme-profile difference and0.2-point adjacent contrasts. Measured profiles were not randomly assigned, with no uncertainty or equivalence evidence, so the conclusion remains an association rather than an effect of freely choosing acculturation or a prescribed best identity.',
    'The clarified participant can manage this daytime event while shift and bus constraints prevent other activities. Coding limited participation as rejection ignores feasible opportunity and omitted nonattenders. The bias analysis proposes broader access and neutral prompts without assuming heritage-language use means exclusion.',
    'The synthesis differentiates belonging associations, the uncontrolled before–after service change and qualitative constraints. It does not equate integration with unconstrained choice or prescribe abandonment of heritage practices. Institutional opportunities are relevant, but a bus change is not an isolated causal finding.',
    'Public matching38/50 versus later private24/50 is a net14-person decline in matching, not proof that exactly14 individuals changed belief. Overlapping transition tables can produce14 or38 total response switches with the same margins; the model correctly requires individual transitions and distinguishes response from belief.',
    'The one-source analysis uses76% public and48% later private matching, a28-percentage-point difference. Because public responding comes first for everyone, privacy is confounded with order and time. The answer does not identify either a precise number of belief changes or a unique conformity motive.',
    'The tutor labels matching obedience despite the absence of an authority command, and their own students may manage impressions. The qualitative bias answer contrasts embarrassment and expertise, examines coding assumptions and proposes voluntary independent interviewing without claiming all matching is irrational.',
    'Three sources distinguish public approval, ambiguous-task information and interview meaning. Culture is not directly measured or manipulated in these constructed studies. The synthesis therefore cannot establish inevitable culturally fixed conformity and allows rational reliance on others under uncertainty.',
    'The object/context chart contains only20-person group averages with repeated trials. A group advantage cannot guarantee any pair of individuals or a context-independent cognitive type. The diagram omits individual distributions rather than supplying evidence of universal nationality-based differences.',
    'Source A alone has a10-point object advantage for A, a13-point relational advantage for B, and within-group task contrasts15 and8 points. The same people complete repeated trials, so trial totals do not become independent participants or support an overall ranking of intelligence.',
    'The revised credibility discussion seeks varied performance and less-confident accounts without asserting that recruitment selected high scorers. Translation and task interpretation can alter apparent attention differences; national-label coding needs reflexive scrutiny and cannot override contradictory bilingual accounts.',
    'The two primary articles were independently opened: Chua reports group differences in scene viewing, while Rayner did not reproduce the main object/background pattern under its procedures. That qualifies generality, not proof culture never matters; the synthesis also uses simulated tasks/accounts and avoids innate fixed cognitive types.',
]
MOT = [
    'The four bars encode original group means across two months; both groups receive a fixed schedule in month2. Without individual distributions, first-month6 versus4 cannot establish every participant benefits from choice or identify who improves, even though random assignment helps the group comparison.',
    'Analyzing A alone gives2 more sessions, or25 percentage points of the eight offered, in month1 and no group difference in month2. The assigned package can affect attendance, but does not isolate autonomy as mediator; a changed follow-up schedule is not proof a psychological benefit vanished.',
    'Only regular attendees are interviewed by their leader using a question that assumes choice is beneficial. The bias answer considers absent barriers and authority, proposes neutral independent interviewing, and retains feasibility versus volition as distinct meanings rather than recoding every account as autonomy.',
    'The synthesis distinguishes self-determination theory’s volition from simple absence of structure. Separate autonomy ratings do not mediate the attendance experiment, and the fixed second month does not establish enduring benefit. A feasible meaningful choice may help, with conditions and competing explanations explicit.',
    'The scatterplot is confined to observed confidence10–70 and has a high18-minute observation influencing the pattern. Extrapolation to unobserved extremes is unsupported; the model separates confidence, time and achievement and does not call all greater time better learning.',
    'Source A has51 minutes over7 people, mean51/7 or7.29; excluding18 leaves33/6 or5.5. The valid high observation should not be removed merely to tidy a pattern. The revised answer calls the sample nonrandom with recruitment unspecified and avoids claiming a convenience procedure not supplied.',
    'The instructor interviews confident participants and interprets all long practice as intrinsic motivation. Accounts of being stuck versus quick competence undermine that unitary code. The credibility answer asks for transparent coding and contrasting experience, without treating short duration as low motivation.',
    'Confidence, expectancy, perceived competence and intrinsic interest are related but distinct. The separate randomized encouragement study raises reported confidence by2 on its scale with equal skill gain, so the synthesis cannot infer universal achievement improvement or convert the measured correlation into causation.',
    'The repaired graph question targets permanence: a ten-minute optional phase immediately after rewards stop cannot demonstrate lasting loss of interest. The model considers fatigue or transient reactions and distinguishes observed minutes from intrinsic motivation, avoiding a repeated generic group-mean limitation.',
    'A alone shows reward-minus-comparison differences0 at baseline,+4 during and−2 immediately after; reward falls1 below its own baseline while comparison rises1. Random assignment helps compare the sequence, but does not isolate intrinsic interest as mechanism or establish a lasting effect beyond the immediate phase.',
    'The token distributor has a stake in interpreting interviews and codes pressure or needing a break as permanent interest loss. Credibility requires alternative interpretations, confidential independent interviewing and attention to timing; the answer does not assume fatigue proves either preserved or lost intrinsic interest.',
    'The source synthesis evaluates controlling versus informational reward meanings using self-determination theory. Separate feedback/autonomy ratings do not demonstrate mediation in the token study, and immediate behavior plus pressure/fatigue accounts do not support the universal claim that all rewards destroy interest.',
    'Buddy stayers’8.5 and usual stayers’7.0 concern10/40 and30/40 of self-selected original groups. Different missing fractions mean the graph cannot represent all original volunteers. Valid0–10 values for leavers can reverse full-cohort rankings, so the mean advantage is not a program benefit.',
    'The Source A analysis calculates a1.5-point stayer difference alongside25% versus75% retention. Initial self-selection and differential attrition prevent a causal buddy conclusion. Retention can reflect practical burdens and is not itself a direct measure of intrinsic motivation or relatedness.',
    'The repaired answer treats qualitative transferability as a contextual judgment rather than statistical representativeness. Two enthusiastic stayers illuminate connection and appointment burdens; information about setting and former/current participants can reveal relevance elsewhere without guaranteeing the same experience.',
    'Relatedness is a plausible conditional explanation, not a universal response to a buddy scheme. The synthesis weighs self-selection, missing leavers, unequal meeting demands and two positive accounts. Following all original participants and describing opportunity costs matters before asserting greater motivation for everyone.',
    'All recorded8-minute values are explicitly children still waiting at the cap, not completed choices at exactly8. The display therefore censors possible later choices; it cannot estimate unconstrained waiting duration. The answer keeps recorded behavior separate from pure self-control or a diagnosis.',
    'A alone yields23/8=2.875 and44/8=5.5 minutes, with one versus three of eight records censored,12.5% versus37.5%. The cross-sectional age contrast is2.625 minutes and does not isolate maturation from comprehension or reward value, nor reveal how long capped children would actually wait.',
    'The interviewer’s impatient-young-child framing biases the caregiver accounts and stable-deficit code. Unclear instructions and an unwanted sticker offer competing interpretations, but caregivers are indirect witnesses to child motives. Neutral prompts and reflexivity improve the account without treating either quote as proof.',
    'The synthesis combines capped observed duration, a separate within-person availability manipulation and contextual caregiver accounts. Expectancy and reward value are relevant to choices; age is not randomized or longitudinal. The ethical description supplies permission, assent and withdrawal and no pure self-control ranking follows.',
]

def sha(data): return hashlib.sha256(data).hexdigest()
def qhash(q): return sha(json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
def check(name,actual,expected,reason,tolerance=1e-10):
    assert abs(actual-expected)<=tolerance,(name,actual,expected)
    return {'name':name,'actual':actual,'expected':expected,'tolerance':tolerance,'reason':reason}

def pack_checks(token,pack):
    c=[]
    def add(name,actual,expected,reason): c.append(check(name,actual,expected,reason))
    if token=='cul' and pack==1:
        add('Community mean contrast',32-24,8,'Scale-point contrast is not a majority-of-individuals ranking.')
        add('Within-person translation contrast',31-25,6,'Same bilingual participants provide the paired wording contrast.')
        a=[30]*21+[18]*7+[17]*12;b=[29]*21+[36]*6+[35]*13
        add('Counterexample sample A mean',statistics.mean(a),24,'Constructed in-range integers independently test the universal group-ordering claim.')
        add('Counterexample sample B mean',statistics.mean(b),32,'Higher group mean can coexist with a lower median.')
        add('Counterexample median reversal',statistics.median(a)-statistics.median(b),1,'Most A values30 exceed most B values29 despite the reversed mean ordering.')
    elif token=='cul' and pack==2:
        for name,pct,want in [('A age4',60,12),('A age8',80,16),('B age4',40,8),('B age8',80,16)]:
            add(name+' helping events',pct*20/100,want,'Twenty opportunities are two repeated opportunities for each of ten children.')
        add('A age contrast percentage points',80-60,20,'Cross-sectional mean difference does not establish within-child change.')
        add('B age contrast percentage points',80-40,40,'Different opportunities and cultural meanings can affect observed helping.')
        x=[2]*6+[0]*4;y=[2]*2+[1]*8
        add('Counterexample equal helping totals',sum(x)-sum(y),0,'Both ten-child allocations contain twelve events but different individual consistency.')
        add('Counterexample ever-helping difference',sum(v>0 for v in y)-sum(v>0 for v in x),4,'Same event total permits ten versus six children ever helping.')
        add('Separate instructed-sample event count',90*20/100,18,'Different participants plus invitation and demonstration do not isolate one mechanism.')
    elif token=='cul' and pack==3:
        add('Extreme belonging profile contrast',4.2-3.6,.6,'Point difference on the one-to-five scale; profiles were measured, not assigned.')
        add('Adjacent belonging profile contrast',4.2-4,.2,'No uncertainty or equivalence evidence is supplied for the group means.')
        add('Separate before-after contrast',4-3.5,.5,'The uncontrolled change accompanies service and transport changes.')
        add('Truncated visible-height ratio',(4.2-3)/(3.6-3),2,'Ratio concerns height above the displayed baseline3, not twice the psychological belonging.')
    elif token=='cul' and pack==4:
        add('Public matching percent',38/50*100,76,'Denominator is the same fifty participants, not independent samples.')
        add('Private matching percent',24/50*100,48,'Later private responses are confounded with order and time.')
        add('Net matching percentage-point decline',(38-24)/50*100,28,'Net response margins do not identify every individual transition or belief.')
        add('Minimum-switch transition counterexample',(38-24)+(24-24),14,'With24 matching on both occasions, fourteen responses change and no reverse switches occur.')
        add('Alternative-switch transition counterexample',(38-12)+(24-12),38,'With12 matching on both occasions,26 stop and12 start matching; margins remain unchanged.')
        add('Separate ambiguity contrast',(14/20-4/20)*100,50,'Random clear/ambiguous groups differ50 points; this is not a measured cultural contrast.')
    elif token=='cul' and pack==5:
        for name,actual,expected in [('Object group contrast',80-70,10),('Relational group contrast',78-65,13),('Within A task contrast',80-65,15),('Within B task contrast',78-70,8)]:
            add(name,actual,expected,'Percentage-point comparison is task-specific and does not establish global intelligence or individual ordering.')
        for label,pct,total in [('A object',80,160),('A relational',65,130),('B object',70,140),('B relational',78,156)]:
            add(label+' implied correct trials',20*10*pct/100,total,'Two hundred repeated trials per type remain twenty participants, not two hundred independent people.')
    elif token=='mot' and pack==1:
        add('First month session contrast',6-4,2,'Attendance contrast under randomized packages does not isolate autonomy as mediator.')
        add('First month opportunity percentage-point contrast',(6/8-4/8)*100,25,'Both groups are offered eight sessions.')
        add('Second month contrast',3-3,0,'Both original groups now receive fixed schedules; no permanence claim follows.')
        add('Separate autonomy contrast',6-4,2,'Same-scale reported autonomy difference is from a separate sample.')
        add('Separate competence contrast',4-4,0,'No competence difference is supplied; mediation is not established.')
    elif token=='mot' and pack==2:
        values=[3,4,5,6,7,8,18]
        add('Observed practice sum',sum(values),51,'All seven valid observations contribute; a high value is not automatically an error.')
        add('Observed practice mean',statistics.mean(values),51/7,'Time is not a direct achievement or intrinsic-interest score.')
        add('Mean without high observation',statistics.mean(values[:-1]),5.5,'Sensitivity calculation does not justify deleting a valid observation.')
        add('Separate encouragement confidence contrast',6-4,2,'Randomized encouragement concerns reported confidence, not Source A causation.')
        add('Separate encouragement skill-gain contrast',2-2,0,'Equal measured skill gains do not support universal confidence-driven achievement.')
    elif token=='mot' and pack==3:
        for label,a,b,want in [('Baseline',4,4,0),('During reward',9,5,4),('Immediately after',3,5,-2)]:
            add(label+' group contrast',a-b,want,'Each phase lasts ten minutes; an immediate difference is not evidence of lasting interest loss.')
        add('Reward after-minus-baseline',3-4,-1,'Within-group change requires its comparison condition for contextual interpretation.')
        add('Comparison after-minus-baseline',5-4,1,'The comparison group also changes, so reward-group trajectory alone is insufficient.')
        add('Separate feedback autonomy contrast',6-3,3,'Separate feedback conditions do not test mediation in the token sequence.')
    elif token=='mot' and pack==4:
        add('Stayer mean contrast',8.5-7,1.5,'Means concern different selected fractions of the original self-selected cohorts.')
        add('Buddy retention percent',10/40*100,25,'Thirty buddy leavers have unobserved motivation scores.')
        add('Usual retention percent',30/40*100,75,'Ten usual leavers have unobserved motivation scores.')
        add('Retention percentage-point contrast',(30-10)/40*100,50,'Retention does not itself directly measure intrinsic motivation.')
        for label,actual,expected in [('Buddy lower bound',10*8.5/40,2.125),('Buddy upper bound',(10*8.5+30*10)/40,9.625),('Usual lower bound',30*7/40,5.25),('Usual upper bound',(30*7+10*10)/40,7.75)]:
            add(label,actual,expected,'Fresh zero-to-ten missing-value bounds demonstrate that full-cohort rankings cannot be determined from stayer means.')
    elif token=='mot' and pack==5:
        younger=[0,1,1,2,3,4,4,8];older=[2,3,4,5,6,8,8,8]
        add('Younger recorded duration mean',statistics.mean(younger),2.875,'Recorded capped durations are not unconstrained waiting times.')
        add('Older recorded duration mean',statistics.mean(older),5.5,'Every eight-minute observation is explicitly still waiting at the cap.')
        add('Recorded age-group mean contrast',statistics.mean(older)-statistics.mean(younger),2.625,'Different cross-sectional children do not isolate individual maturation.')
        add('Younger censored percentage',younger.count(8)/8*100,12.5,'Censor counts are unambiguous after the explicit still-waiting clarification.')
        add('Older censored percentage',older.count(8)/8*100,37.5,'More capped observations make unconstrained waiting particularly uncertain.')
        add('Separate availability mean contrast',6-3,3,'Within-person availability conditions are a separate study, not an age intervention.')
    return c

BAR_SPECS={('cul',1):([24,32],0,40),('cul',2):([60,80,40,80],0,100),('cul',3):([4.2,4,3.8,3.6],3,5),('cul',4):([76,48],0,100),('cul',5):([80,65,70,78],0,100),('mot',1):([6,4,3,3],0,8),('mot',4):([8.5,7],0,10),('mot',5):([2.875,5.5],0,8)}
def geometry_checks(q,token,pack):
    tree=ET.fromstring(q['diagramSvg']);items=list(tree);checks=[]
    if (token,pack) in BAR_SPECS:
        values,lo,hi=BAR_SPECS[token,pack]
        bars=[e for e in items if e.tag.rsplit('}',1)[-1]=='rect' and e.attrib.get('fill')=='#f5db7e']
        assert len(bars)==len(values)
        for i,(bar,value) in enumerate(zip(bars,values),1):
            height=(value-lo)*210/(hi-lo)
            checks.append(check(f'Actual SVG bar{i} top',float(bar.attrib['y']),325-height,'Independent coordinates encode the supplied value on the stated axis, including an intentional truncated baseline where applicable.',.01))
            checks.append(check(f'Actual SVG bar{i} height',float(bar.attrib['height']),height,'Actual bar height is independently recomputed from the source value and axis endpoints.',.01))
    elif token=='mot' and pack==2:
        pts=[e for e in items if e.tag.rsplit('}',1)[-1]=='circle'];data=list(zip([10,20,30,40,50,60,70],[3,4,5,6,7,8,18]));assert len(pts)==7
        for i,(p,(x,y)) in enumerate(zip(pts,data),1):
            checks.append(check(f'Scatter point{i} x',float(p.attrib['cx']),100+x*7.25,'Actual point encodes observed confidence on the zero-to-eighty axis.'))
            checks.append(check(f'Scatter point{i} y',float(p.attrib['cy']),300-y*11,'Actual point encodes practice minutes on the zero-to-twenty axis, including the valid high observation.'))
    elif token=='mot' and pack==3:
        pts=[e for e in items if e.tag.rsplit('}',1)[-1]=='circle'];values=[4,9,3,4,5,5];assert len(pts)==6
        for i,(p,value) in enumerate(zip(pts,values)):
            checks.append(check(f'Phase point{i+1} x',float(p.attrib['cx']),[150,390,630][i%3],'Phase positions preserve baseline, reward and immediate-after order.'))
            checks.append(check(f'Phase point{i+1} y',float(p.attrib['cy']),300-value*22,'Actual ten-minute phase plot matches Source A group mean, not an inferred long-term interest level.'))
    return checks

def main():
    pins=json.loads((DOCS/'social-extensions-independent-pins.json').read_text(encoding='utf-8'))
    index=json.loads((DOCS/'native-diagram-index.json').read_text(encoding='utf-8'))
    figures={r['questionId']:r for r in index['records']}
    notes={r['questionId']:r['reasoning'] for r in pins['socReadingRecords']}
    records=[];files=[];unique_figures=set()
    assert len(notes)==40 and len(CUL)==len(MOT)==20
    for file,expected in REVIEWED_FILES.items():
        raw=(ROOT/file).read_bytes();assert sha(raw)==expected,'Edited content requires fresh independent full reading: '+file
        assert b'\r' not in raw
        qs=json.loads(raw);token=qs[0]['id'].split('-')[2];count=40 if token=='soc' else 20
        assert len(qs)==count
        files.append({'file':file,'sha256':expected,'questions':count})
        for i,q in enumerate(qs,1):
            qid=q['id'];assert qid==f'ib-psy-{token}-{i:03}'
            assert qhash(q)==pins['questions'][qid],'Changed question requires actual new reading: '+qid
            section=('p1-a' if i<=8 else 'p1-b' if i<=24 else 'p1-c') if token=='soc' else ['p3-graph','p3-data','p3-qualitative','p3-synthesis'][(i-1)%4]
            assert q['examSection']==section and q['subject']=='psychology' and q['firstAssessment']==2027
            assert q['level']==('sl' if token=='soc' else 'ahl') and q['parts']==[] and q['calculator'] is False
            scheme=q['markScheme'];assert len(scheme)==1 and scheme[0]['part']==''
            assert all(s['code']=='IND' for s in scheme[0]['steps'])
            assert scheme[0]['rubric']['maxMarks']==q['marks']
            assert [[b['min'],b['max']] for b in scheme[0]['rubric']['bands']]==BANDS[q['marks']]
            reasoning=notes[qid] if token=='soc' else (CUL if token=='cul' else MOT)[i-1]
            assert len(reasoning)>=100
            pack=(i-1)//4+1;numeric=[]
            if token!='soc':
                if section in ['p3-data','p3-synthesis']:numeric.extend(pack_checks(token,pack))
                if q.get('diagramSvg'):numeric.extend(geometry_checks(q,token,pack))
            if section in ['p3-graph','p3-data']:assert numeric
            source_checks=[{'url':GUIDE,'note':'Official first-assessment2027 course, Paper1 or HL Paper3 demand, prescribed scope and holistic maximum checked against the guide.'}]
            if token=='cul' and pack==5:
                source_checks += [{'url':CHUA,'note':'Primary article independently opened: scene-viewing eye movement contrasts in25 European-American and27 international Chinese students, not an innate fixed cognitive type.'},{'url':RAYNER,'note':'Primary article independently opened: main object/background viewing pattern was not reproduced in its scene task; other eye-movement differences do not justify claiming culture has no effect.'}]
            r={'questionId':qid,'questionSha256':qhash(q),'status':'passed','reviewer':'root','fullQuestionAndSchemeRead':True,'reasoning':reasoning,'numericChecks':numeric,'assessment':{'examSection':section,'marks':q['marks'],'scopeChecked':True},'sourceChecks':source_checks,'openFindings':[]}
            if q.get('diagramSvg'):
                f=figures[qid];assert f['questionSha256']==qhash(q)
                expected_figure=pins['figures'][sha(q['diagramSvg'].encode())]
                for k in ['svgSha256','nativePngSha256','mobilePngSha256']:assert f[k]==expected_figure[k],'Changed figure requires native/mobile reading: '+qid
                assert f['svgSha256']==sha(q['diagramSvg'].encode())
                for role in ['native','mobile']:assert sha((ROOT/f[role+'PngPath']).read_bytes())==f[role+'PngSha256']
                r['figureReview']={k:f[k] for k in ['svgSha256','nativePngSha256','mobilePngSha256','nativePngPath','mobilePngPath']}
                r['figureReview'].update({'scientificGeometryChecked':True,'legible':True,'nativeInspected':True,'mobile360Inspected':True,'reasoning':expected_figure['reasoning']})
                unique_figures.add(f['svgSha256'])
            records.append(r)
    assert len(records)==80 and len(unique_figures)==18
    assert len({r['reasoning'] for r in records})==80
    report={'status':'passed','reviewer':'root','questions':80,'files':files,'records':records,
        'method':{'fullStemsAndAllIndicativeAnswerParagraphsRead':80,'bestFitRubricsReadAndExactBandBoundariesChecked':80,'native1200DistinctFiguresActuallyRead':18,'mobile360DistinctFiguresActuallyRead':18,'illustratedQuestionRecords':sum('figureReview' in r for r in records),'numericAssertions':sum(len(r['numericChecks']) for r in records),'independentNumericMethod':'Fresh arithmetic from supplied literal data, transition-table and missing-data counterexamples, and parsing actual SVG geometry; not copied author assertions. Reused source packs yield repeated bindings, not unique datasets.','limits':'Independent AI scientific/content and visual review, not human IB-examiner moderation. Most data and accounts are clearly simulated; CUL05 primary summaries were checked against the two opened articles.'},
        'resolvedFindings':pins['resolvedFindings'],'openFindings':[]}
    out=DOCS/'social-extensions-independent.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'status':'passed','questions':80,'uniqueFigures':18,'illustratedRecords':report['method']['illustratedQuestionRecords'],'numericAssertions':report['method']['numericAssertions'],'reportSha256':sha(out.read_bytes())}))

if __name__=='__main__':main()
