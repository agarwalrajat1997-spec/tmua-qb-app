"""Independent conceptual, assessment and graphical review of RES60/TEC20.

The reviewer read every prompt and complete indicative answer, then inspected
29 distinct rendered figures at native and 360 px widths. Numerical evidence
below is derived from the supplied stimuli, never imported from author checks.
Final binding requires the portable canonical-bound media index. A separate
reviewed-content pin prevents this script silently approving later text edits.
"""
from pathlib import Path
import hashlib, json, math, re, sys, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
DOCS=ROOT/'docs/ib-psychology-reviews'
TASK=ROOT.parents[1]
WORK=TASK/'work/psychology-bank-2026/methods-technology-independent-preview'
GUIDE='https://ibo.org/globalassets/new-structure/university-admission/pdfs/subject-guides/psychology-first-assessment-2027-guide-sbs.pdf'
REVIEWER='mock_exam_spec'

RES={
1:'The common opening list supplies structure while neutral discretionary probes supply flexibility. The answer correctly distinguishes semi-structured from a wholly fixed interview rather than treating privacy or sample size as the defining feature.',
2:'The coordinator relationship creates a concrete social-desirability pathway and could also alter probing. The proposed separation and reflexivity reduce specified influences without claiming that consent or a new interviewer abolishes bias.',
3:'Both procedures collect self-reports in the participant’s words, but only the live interview permits immediate clarification. The scheme develops candour, follow-up and anonymity trade-offs in the actual coordinator setting.',
4:'An independent interviewer, piloted neutral probes and permission for recording are feasible changes while preserving a semi-structured account. The answer retains withdrawal, secure handling and a reflexive rather than purportedly objective interpretation.',
5:'The first available consenting staffroom occupants are an opportunity sample; no chance selection from a complete frame occurs. The worked distinction correctly separates the invitation mechanism from later consent or refusal.',
6:'Lunchtime availability can shape what convenient movement means to these staff. The answer treats omitted work roles as a perspective boundary without invalidating the six participants’ own accounts or asserting a known population preference.',
7:'The comparison develops both voluntary-selection similarities and the role-group coverage difference. Stratified random invitations require an adequate frame and can still suffer nonresponse; no claim that sampling cures the fixed items’ validity is made.',
8:'Recruitment through all-site channels and role-based invitations can reach duty-bound staff without supervisor nomination or compulsion. Replacement rules and disclosure of remaining omissions make the proposed coverage improvement auditable.',
9:'Unequal probing is linked specifically to the interviewer’s device preference. A reflexive record exposes decisions and their consequences; it cannot retrospectively create missing depth in already-produced transcripts.',
10:'The worked response identifies unequal opportunities to explain a preference as the responsibility problem. It proposes disclosure and optional neutral follow-up while protecting participants from pressure to endorse the interviewer’s preferred habit.',
11:'A log reveals the researcher’s own reasoning, while a second reviewer adds scrutiny of what was actually asked. The answer compares their complementary limits and does not confuse researcher agreement with a uniquely true qualitative account.',
12:'Balanced openings and comparable neutral prompts retain room for unexpected meanings while addressing asymmetric exploration. Pilot feedback, optional recording and an audit of departures make the design concrete and ethically coherent.',
13:'Pointing versus speech illustrates the absence of a shared observable definition. The answer specifies a possible event boundary yet correctly limits its interpretation to selected helping behaviours rather than a global helpful personality.',
14:'The explanation separates consistent application of categories from adequate coverage of support. Excluding useful quiet gestures is a construct problem even if coders apply the narrower rule perfectly.',
15:'Both approaches can observe the same real activity with the same overt/non-participant role. Their difference lies in preselected categories versus open recording; the exploratory-to-structured sequence is a justified application rather than a universal ranking.',
16:'Separate observable categories, start/end rules, independent pilot coding and treatment of ambiguous or overlapping events address real coding inconsistencies. The answer does not replace independent records with negotiated simultaneous judgements.',
17:'Agreement on two-second turns supports consistency of that record, not validity as a measure of all participation. Non-verbal task contributions provide the specific reason why a reliable coding rule can be incomplete.',
18:'Insider accounts can identify contributions outsiders overlook, but one confident club member cannot speak for all members. The answer uses consultation to refine interpretation without treating participant perspective as automatically decisive.',
19:'Joining the activity defines participant observation independently of overt/covert disclosure. The scheme develops contextual access, divided recording attention and observer influence for both roles, avoiding the false idea of an influence-free outsider.',
20:'The revision first clarifies the target construct, then adds piloted observable non-verbal categories and rules against double-counting. Separate consistency and coverage arguments make the design responsive to both reliability and validity.',
21:'Advance knowledge defines overt observation; not joining the task defines non-participation. The worked answer accurately keeps those independent classifications separate from the possible reactivity of visible observers.',
22:'Formality during visible observation is a possible temporary measurement-induced change, not proof of lasting developmental change. Familiarisation is qualified rather than represented as a guarantee of natural behaviour.',
23:'Both settings can retain the same task and coding, while a research room changes control and contextual meaning. The answer links the choice to the aim without inferring that one observational setting causes a general developmental difference.',
24:'The design reduces novelty through consenting familiarisation and a stable restrained role, not secret recording. It retains the right to decline and acknowledges that observation reactivity can remain after repeated visits.',
25:'Dividing a complete list by schedule and chance-selecting within strata is accurately distinguished from quota convenience. The scheme also distinguishes sampling from treatment allocation and recognizes later refusal.',
26:'Different meanings of regular contact undermine equivalence despite identical wording. Piloting with both schedules and specifying a period/form clarifies the intended construct without assuming greater precision captures every meaningful relationship.',
27:'Both procedures are chance-based invitations from a frame, but stratification explicitly plans schedule coverage. Preparation and nonresponse limitations are developed, without making either approach responsible for fixing ambiguous item wording.',
28:'Cognitive pilot interviews check the item’s interpretation rather than testing whether respondents are clever enough. Separate pilot data, varied schedules and rechecking revised wording support an implementable measurement improvement.',
29:'With no retained identifiers or codes the stipulated researcher cannot locate a submitted response. Confidential identifiable material is distinguished from anonymous records; the answer does not promise impossible retrospective tracing.',
30:'Accurate consent requires stating the post-submission anonymity limit, with an alternative coded withdrawal window clearly explained. The solution preserves informed choice rather than promising incompatible tracing and immediate unlinkability.',
31:'The comparison keeps question content and voluntary participation constant while weighing a protected temporary linkage against an untraceable submission. It makes coding/deletion purposes explicit instead of treating coded material as already fully anonymous.',
32:'The proposed anonymous procedure checks actual collection settings, indirect identifiers and small-category disclosure as well as names. A clear pre-submission withdrawal choice and truthful tracing limit address the case’s impossible promise.',
33:'Temporal consistency presumes sufficient stability in the underlying experience. The new group activities offer a substantive alternative to questionnaire unreliability, and an unchanged response would not by itself establish validity.',
34:'The answer distinguishes real opportunity change, changed interpretation and inconsistency. It correctly identifies that repeating a questionnaire cannot isolate measurement failure while the setting itself is changing.',
35:'Both formats remain self-report, while fixed categories trade comparability against missed meanings and open items trade flexibility against burden. The mixed-format suggestion is tied to a defined reference period rather than an assumption that more text is better.',
36:'A plausibly stable interval, consistent administration, contextual-change checks and protected matching support a fairer temporal-consistency assessment. The recall-versus-genuine-change timing trade-off is explicitly acknowledged.',
37:'Chance allocation changes which format a volunteer receives; it does not change volunteer recruitment into random sampling. The answer correctly separates internal comparison from the population to which results may generalize.',
38:'Font size changes with spacing, so balanced participant characteristics cannot isolate spacing alone. The worked solution permits a whole-format causal comparison while rejecting attribution to one bundled component.',
39:'Repeated measures controls stable participant differences but introduces material/order effects; independent groups has the complementary limitation. Neither participant design repairs the original font-and-spacing confound.',
40:'Holding text/font/colour constant while changing spacing, random allocation and masked predefined scoring form a coherent revision. Low stakes and withdrawal are retained, while volunteer generalization remains appropriately restricted.',
41:'The answer explains rotating condition and list order and accurately identifies asymmetric strategy transfer as a limitation that counterbalancing need not cancel. Equivalent-list terminology is not taken as evidence of actual equivalence.',
42:'Continued imagery in the rehearsal condition creates a mismatch between nominal condition and enacted strategy. The scheme treats a strategy check as fallible evidence, not direct access to cognition or an excuse to call participants dishonest.',
43:'Both designs require valid manipulations and matched outcomes, but only repeated measures exposes a person to both strategies. The answer weighs stable differences against asymmetric carry-over rather than asserting one universally better design.',
44:'Independent groups with chance assignment and rotated material removes within-person sequence exposure. Equal practice, blind scoring and neutral adherence questions are feasible controls; between-person variation remains acknowledged.',
45:'An immediate prediction of tomorrow’s performance is a confidence measure, not observed next-day recall. The operational distinction is correct and does not assume that fluency or confidence must accurately represent retained material.',
46:'A randomized procedure can strengthen a causal inference about its recorded confidence outcome, subject to implementation. It cannot establish a causal effect on an outcome never measured, so design strength does not repair construct mismatch.',
47:'The comparison makes allocation versus naturally chosen strategy the key causal difference while retaining shared confidence measurement. Self-selected experience or motivation are specific alternatives, and neither design acquires delayed recall by its label.',
48:'A standardized delayed recall task with predefined ideas/scoring directly measures the missing outcome. Matched follow-up conditions, recording extra study, informed follow-up consent and protected matching address concrete threats without promising certainty.',
49:'Random routes and matched instructions support a bounded whole-setting comparison, not a greenery-only mechanism. Immediate self-report, visible expectations, preregistration and voluntary reimbursement are weighed through distinct concepts and a qualified conclusion.',
50:'Referral chains provide access without establishing a representative population. The answer distinguishes network coverage, reflexive interpretation and self-reported routines, and treats leaflet forwarding as privacy protection rather than permission to share others’ details.',
51:'Bus, timetable and leader changes are concurrent explanations, so a before/after archive cannot isolate transport causation. Multiple accounts, secondary-use permission and recognizable journeys are evaluated without equating public raw records with responsible transparency.',
52:'The quasi-experimental age grouping is distinguished from random allocation and from within-person ageing. Cohort experience, task accessibility, speed interpretations and complementary accounts support a bounded comparison rather than a deterministic age deficit.',
53:'Following the same adults supports within-person descriptions but repeats the same materials, allowing task practice. Clarification counts need construct justification; coder agreement and hidden coordinator ratings do not remove narrow measurement or selective attrition.',
54:'Random invitations are random only within the organization’s frame, with later nonresponse. The response also separates present reconstruction of work life from prospective change measurement and evaluates mode and cultural meanings of independence.',
55:'Attendance and belonging are unassigned measures, permitting reverse direction and common causes. Recorded covariates and random invitations do not remove all confounding or frame/nonresponse limits, and the public causal claim is appropriately rejected.',
56:'Separate accounts can illuminate meanings of fairness without establishing which partner owns the true account. Quotation checking is distinguished from validation of every interpretation, and relational confidentiality is treated as more than replacing names.',
57:'Observable offers and independent coding can be consistent yet fail to measure cooperative relationship quality. Camera coverage, opportunity, prior familiarity and participants’ meanings are specific limitations, with consent to recording and restricted claims preserved.',
58:'Random learning allocation and a masked transfer-test scorer support a limited educational comparison. Preregistration does not guarantee construct validity or adherence, and map-symbol volunteers cannot establish a universal best method across learners and aims.',
59:'Natural switching cannot isolate its effect on learning because difficulty and work demands may influence both. Diary definitions, reactivity, omitted entries and limited private information are addressed without treating missing records as zero behaviour.',
60:'The selected finished-work archive omits abandoned processes, and a new observation cannot reconstruct them. Differing learner/teacher accounts, dependent evidence and recognizable creative work are examined without converting triangulation into proof or private access into publication permission.'
}
TEC={
1:'The SD bars describe dispersion, not precision of the mean or a significance test. The worked limitation properly rejects a uniform individual effect while preserving the randomized comparison of mean task errors.',
2:'The two-point contrast is a percentage-point difference, with a wholly positive supplied interval. Repeated measures addresses stable differences but not all carry-over; the conclusion stays with task errors rather than unmeasured course retention.',
3:'Only selecting interruption excerpts excludes an explicitly helpful reminder account. Reflexivity, negative cases, audit trail and participant comment are correctly offered as scrutiny rather than guaranteed elimination of researcher perspective.',
4:'All three distinct sources are integrated: average attention costs, a paired positive contrast and contrasting qualitative meanings. Switching/resources and external prospective cues provide relevant own knowledge, while the universal learning claim is rejected for precise outcome and context reasons.',
5:'The three cross-sectional time categories are different people, not an intervention trajectory. The causal limitation is concrete, preserving the non-monotonic descriptive pattern without inferring a direction of influence or an effect for each individual.',
6:'The completer contrast is one point on the now-explicit 0–40 scale, and its interval spans zero. Differential missing outcomes can undermine the randomized comparison; the revised answer correctly states that practical importance has no supplied threshold.',
7:'Rich setting description assists conditional transfer, while long-term active members with access omit former or excluded users. The answer correctly distinguishes qualitative contextual relevance from statistical representativeness or a sample-size guarantee.',
8:'The answer combines a non-monotonic survey, uncertain and attrition-limited trial, and contrasting kinds of online contact. The scope of the 0–40 non-diagnostic measure is now explicit, and no necessary individual benefit or clinical instruction is inferred.',
9:'Resource-assisted correct responding is not an equivalent unaided retention measure. The answer preserves the practical value of using notes while explaining why relabelling the axis cannot turn the supplied comparison into a memory test.',
10:'The negative factual difference and positive location difference refer to separate bounded scales and supplied intervals. Random expectations support a limited causal comparison, while the encoding-priority mechanism is kept as an interpretation rather than observed mental fact.',
11:'Labelling every check as dependency imposes one interpretation and omits error-prevention possibilities. The proposed alternative coding, reflexivity and transcript scrutiny are specific to these excerpts and do not turn participant feedback into a vote on truth.',
12:'The response separates internal factual retention, location memory and available-resource performance, then synthesizes all three sources. Offloading/transactive organization is a relevant explanation, with system availability and incorrect information retained as genuine costs.',
13:'Unknown sample sizes and spread prevent judging precision behind the descriptive 1.2-point difference. The answer neither invents a significance result nor treats absent uncertainty information as evidence that the two population means are equal.',
14:'Squaring the positive correlation gives about 0.10, referring to a simple linear sample association rather than percent causation. The positive interval does not establish direction or remove background causes, and worry is correctly distinguished from diagnosis.',
15:'The insider’s role can supply context while advocacy and selective quotations limit credibility. Transparent selection, contradictory accounts and outside scrutiny are linked to the actual source without making agreement or representativeness the credibility criterion.',
16:'The synthesis keeps connection, comparison worry and community meanings distinct. It uses all three sources and relevant social/learning mechanisms, weighs insider access against selection, and correctly rejects inevitable harm rather than claiming universal benefit.',
17:'Both plotted mean trajectories rise, but everyone uses the application and repeats a test form. The worked limitation concerns absence of a causal control, not a false denial of the displayed changes or a claim that group means are individual trajectories.',
18:'The four-point difference compares adaptive with fixed practice, with a wholly positive supplied interval. Equal practice and random assignment support that feature contrast, while trained outcomes at six weeks do not establish general transfer or durability.',
19:'Context and device experience support conditional qualitative transfer among completers. Excluding discontinuers and less confident users directly limits age/access scope, and enjoyment is not interpreted as evidence of a lasting performance effect.',
20:'The answer distinguishes starting level, gain, adaptive-feature advantage, broad transfer and durability across all three sources. Learning/plasticity is used as explanatory knowledge without claiming an unmeasured neural change or universal benefit across ages.'
}

def digest(data):return hashlib.sha256(data).hexdigest()
def canon(q):return json.dumps(q,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
def semantic(q):return canon({k:v for k,v in q.items() if k!='diagramUrl'})
def load(p):return json.loads(Path(p).read_text(encoding='utf8'))
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf8',newline='\n')

def check(name,actual,expected,tolerance=1e-9,reason=''):
    assert all(math.isfinite(float(v)) for v in (actual,expected,tolerance)) and tolerance>=0
    assert abs(actual-expected)<=tolerance,(name,actual,expected,tolerance)
    assert len(reason)>30
    return dict(name=name,actual=actual,expected=expected,tolerance=tolerance,reason=reason)

def numbers(stem,pattern):
    m=re.search(pattern,stem);assert m,pattern
    return [float(x.rstrip('.')) for x in m.groups()]

def numerical(q):
    """Reported intervals are checked for interpretation, not claimed re-estimated."""
    if q['id'].startswith('ib-psy-res'):return []
    n=q['number'];s=q['stem'];out=[]
    def c(name,a,e,t=1e-9,why='Derived independently from the actual supplied stimulus values.'):
        out.append(check(name,a,e,t,why))
    if n in (2,4):
        blocked,enabled=numbers(s,r'mean error percentages are ([\d.]+)%.*?and ([\d.]+)%')
        lo,hi=numbers(s,r'interval from ([\d.]+) to ([\d.]+) percentage')
        c('enabled minus blocked percentage points',enabled-blocked,2)
        c('reported interval lower bound',lo,.6);c('reported interval upper bound',hi,3.4)
        c('positive reported interval excludes zero',float(lo>0 and hi>0),1)
        c('relative change differs from percentage points',100*(enabled-blocked)/blocked,40)
    if n in (6,8):
        assert '0–40 scale' in s and 'higher scores indicating greater reported well-being' in s
        a,b=numbers(s,r'mean improvements are ([\d.]+) and ([\d.]+) scale')
        lo,hi=numbers(s,r'interval from (-?[\d.]+) to ([\d.]+) points')
        c('completer mean improvement contrast',a-b,1)
        c('reported interval spans zero',float(lo<0<hi),1)
        c('reduction-group final respondents',100/2-12,38)
        c('usual-use final respondents',100/2-4,46)
        c('differential attrition percentage points',100*(12-4)/(100/2),16)
        c('reported interval midpoint',(lo+hi)/2,1)
    if n in (10,12):
        a,b=numbers(s,r'factual scores out of 20 are ([\d.]+).*?and ([\d.]+) without')
        x,y=numbers(s,r'location scores out of 6 are ([\d.]+) and ([\d.]+)')
        c('factual-score contrast',a-b,-3);c('location-score contrast',x-y,2)
        c('both factual means within scale',float(0<=a<=20 and 0<=b<=20),1)
        c('both location means within scale',float(0<=x<=6 and 0<=y<=6),1)
        lo,hi=numbers(s,r'interval of (-?[\d.]+) to (-?[\d.]+)')
        c('factual interval wholly negative',float(lo<hi<0),1)
        lo,hi=numbers(s,r'interval of ([\d.]+) to ([\d.]+)')
        c('location interval wholly positive',float(0<lo<hi),1)
    if n in (14,16):
        r,=numbers(s,r'correlation is r = ([\d.]+)')
        lo,hi=numbers(s,r'interval from ([\d.]+) to ([\d.]+)')
        c('linear squared correlation',r*r,.1024)
        c('reported rounded squared correlation',round(r*r,2),.10)
        c('positive correlation interval',float(0<lo<r<hi<1),1)
    if n in (18,20):
        a,b=numbers(s,r'improve by means of ([\d.]+) and ([\d.]+) percentage')
        lo,hi=numbers(s,r'interval of ([\d.]+) to ([\d.]+)')
        c('adaptive minus fixed gain',a-b,4)
        c('reported interval midpoint',(lo+hi)/2,4)
        c('positive reported adaptive contrast interval',float(0<lo<hi),1)
        c('allocated people per condition',90/2,45)
    if n in (17,20):
        a,b,c0,d=numbers(s,r'accuracies are ([\d.]+)% then ([\d.]+)%.*?and ([\d.]+)% then ([\d.]+)%')
        c('younger mean gain',b-a,18);c('older mean gain',d-c0,14)
        c('gain contrast differs from final-level contrast',(b-a)-(d-c0),4)
        c('older-minus-younger final mean',d-b,3)
    if q.get('diagramSvg'):
        r=ET.fromstring(q['diagramSvg']);elements=list(r)
        if n in (1,4,5,8,9,12,13,16):
            maximum={1:15,4:15,5:40,8:40,9:20,12:20,13:8,16:8}[n]
            expected={1:[4,7],4:[4,7],5:[27,29,25],8:[27,29,25],9:[19,14],12:[19,14],13:[6.2,5],16:[6.2,5]}[n]
            bars=[e for e in elements if e.tag.endswith('rect') and e.attrib.get('fill')=='#f5db7e']
            assert len(bars)==len(expected)
            for i,(bar,value) in enumerate(zip(bars,expected),1):
                c(f'bar {i} inverse-mapped mean',(325-float(bar.attrib['y']))*maximum/210,value,1e-9,'Independent inverse mapping from the plotted zero and maximum grid coordinates; compared with the read figure/stimulus.')
                c(f'bar {i} bottom equals zero',float(bar.attrib['y'])+float(bar.attrib['height']),325,1e-9,'Checked geometric bar baseline against the numeric zero gridline.')
            if n in (1,4):
                errors=[e for e in elements if e.tag.endswith('line') and e.attrib.get('x1')==e.attrib.get('x2') and e.attrib.get('x1')!='80']
                assert len(errors)==2
                for i,(e,mean,sd) in enumerate(zip(errors,[4,7],[2,4]),1):
                    c(f'bar {i} upper one-SD endpoint',(325-float(e.attrib['y1']))*15/210,mean+sd)
                    c(f'bar {i} lower one-SD endpoint',(325-float(e.attrib['y2']))*15/210,mean-sd)
        elif n in (17,20):
            dots=[e for e in elements if e.tag.endswith('circle')]
            assert len(dots)==4
            for i,(dot,value) in enumerate(zip(dots,[55,73,62,76]),1):
                c(f'line point {i} inverse-mapped accuracy',(310-float(dot.attrib['cy']))*100/215,value,1e-9,'Independent inverse mapping from the line graph zero/100 coordinates, compared with the supplied before–after means.')
    return out

def main():
    files=['content/ib/psychology/research-methodology.json','content/ib/psychology/technology.json']
    qs=[q for f in files for q in load(ROOT/f)]
    assert len(qs)==80 and len({q['id'] for q in qs})==80
    reviewed=load(DOCS/'methods-technology-independent-pins.json')
    pins=reviewed['questionSemanticSha256']
    index=load(DOCS/'native-diagram-index.json')
    native={(r['questionId'],r['role']):r for r in index['records']}
    recs=[];seen={};allchecks=[]
    bands={3:[(0,0),(1,1),(2,2),(3,3)],4:[(0,0),(1,2),(3,4)],6:[(0,0),(1,2),(3,4),(5,6)],15:[(0,0),(1,3),(4,6),(7,9),(10,12),(13,15)]}
    for q in qs:
        qid=q['id'];n=q['number'];isres=qid.startswith('ib-psy-res')
        assert pins[qid]==digest(semantic(q)),f'Content changed after actual independent read: {qid}'
        assert q['firstAssessment']==2027 and q['calculator'] is False
        assert q['level']==('sl' if isres else 'ahl')
        assert q['parts']==[] and len(q['markScheme'])==1
        ms=q['markScheme'][0];assert ms['part']=='' and all(s['code']=='IND' for s in ms['steps'])
        assert ms['rubric']['maxMarks']==q['marks']
        assert [(b['min'],b['max']) for b in ms['rubric']['bands']]==bands[q['marks']]
        assert all(len(b['descriptor'])>20 for b in ms['rubric']['bands'])
        assert len(ms['steps'])>=(4 if q['marks']==15 else 2)
        if isres:
            if n<=48:
                section=['p2-a-knowledge','p2-a-application','p2-a-comparison','p2-a-design'][(n-1)%4]
                assert q['examSection']==section and q['marks']==[4,4,6,6][(n-1)%4]
                assert 'class practical' in q['stem'] and 'you actually studied' in q['stem']
            else:
                assert q['examSection']=='p2-b' and q['marks']==15 and len(q['concepts'])>=4
                assert 'at least two' in q['stem'] and 'constructed for practice' in q['stem']
        else:
            assert q['examSection']==['p3-graph','p3-data','p3-qualitative','p3-synthesis'][(n-1)%4]
            assert q['marks']==[3,6,6,15][(n-1)%4]
            assert 'simulated for practice' in q['stem']
            if n%4==0:assert all(x in q['stem'] for x in ['Source A','Source B','Source C','at least three','own knowledge'])
        reasoning=(RES if isres else TEC)[n];assert len(reasoning)>100
        checks=numerical(q);allchecks.extend(checks)
        rec=dict(questionId=qid,questionSha256=digest(canon(q)),status='passed',reviewer=REVIEWER,
            fullQuestionAndSchemeRead=True,reasoning=reasoning,numericChecks=checks,
            assessment=dict(examSection=q['examSection'],marks=q['marks'],scopeChecked=True),
            sourceChecks=[dict(url=GUIDE,note='Checked the 2027 assessment/methodology scope and holistic bands. All empirical study details in this question are explicitly constructed stimuli, not claimed published findings.')],openFindings=[])
        if q.get('diagramSvg'):
            r=native[(qid,'question')];h=digest(q['diagramSvg'].encode())
            assert r['svgSha256']==h and r['questionSha256']==digest(canon(q))
            for k in ['nativePng','mobilePng']:
                assert digest((ROOT/r[k+'Path']).read_bytes())==r[k+'Sha256']
            proof=reviewed['visualReviewedSvg'];assert h in proof,'New/repaired SVG requires actual visual reread'
            for k in ['nativePngSha256','mobilePngSha256']:
                assert r[k]==proof[h][k],'Raster bytes differ from the actually inspected image'
            rec['figureReview']=dict(svgSha256=h,nativePngSha256=r['nativePngSha256'],mobilePngSha256=r['mobilePngSha256'],scientificGeometryChecked=True,legible=True,reasoning=proof[h]['reasoning'])
            if h in seen:rec['figureReview']['sameAssetAs']=seen[h]
            else:seen[h]=qid
        recs.append(rec)
    resolved=[dict(questionIds=['ib-psy-tec-006','ib-psy-tec-008'],finding='Standalone Source B omitted its scale while the worked answer judged practical magnitude.',resolution='Explicit 0–40 higher-is-better scale added; answer now states no practical-importance threshold is supplied.',reread=True),dict(questionIds=['ib-psy-res-010','ib-psy-res-012'],finding='Reflective label was less precise than the intended methodological term.',resolution='Reflexive review label independently reread after repair.',reread=True),dict(questionIds=['ib-psy-res-056'],finding='Figure title called project partners friends without a corresponding source given.',resolution='Shared-project wording independently reread after repair.',reread=True)]
    report=dict(status='passed',reviewer=REVIEWER,questions=80,files=[dict(file=f,sha256=digest((ROOT/f).read_bytes()),questions=len(load(ROOT/f))) for f in files],records=recs,numericAssertions=len(allchecks),uniqueFiguresReviewed=len(seen),figureUses=sum('figureReview' in r for r in recs),resolvedFindings=resolved,openFindings=[],reviewBoundary='Separate independent assessment/scientific review of all full prompts, IND worked answers and best-fit rubrics. Supplied inferential intervals are interpreted and checked for internal direction/scale consistency; no false claim of recomputation from unavailable raw observations. Native/mobile images inspected, with identical SVG assets explicitly shared between related items.')
    dump(DOCS/'methods-technology-independent.json',report)
    print(json.dumps(dict(status='passed',questions=80,numericAssertions=len(allchecks),uniqueFiguresReviewed=len(seen),figureUses=report['figureUses'])))

if __name__=='__main__':main()
