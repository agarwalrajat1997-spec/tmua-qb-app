"""Bind the independent case/scope review and serialized-input arithmetic to files."""
from pathlib import Path
from collections import Counter
import json,hashlib,re

ROOT=Path(__file__).resolve().parents[2];DOC=ROOT/'docs/ib-expansion-reviews'
FILES=sorted((ROOT/'content/ib/business-management').glob('*.json'))
QS=[q for p in FILES for q in json.loads(p.read_text(encoding='utf8'))]
OLD={q['id']:q for q in json.loads((DOC/'business-independent-input.json').read_text(encoding='utf8'))}
AUTH=json.loads((DOC/'business-author-ledger.json').read_text(encoding='utf8'))
FAMILY={r['id']:r['family'] for r in AUTH}
NUM=json.loads((DOC/'business-independent-numeric.json').read_text(encoding='utf8'))
assert NUM['status']=='passed' and NUM['questionCount']==400 and not NUM['errors']
MATH={r['id']:r['checks'] for r in NUM['records']}
FIG=json.loads((DOC/'business-independent-figures/render-ledger.json').read_text(encoding='utf8'))
assert FIG['rendered']==44
FIGS={}
for r in FIG['records']:FIGS.setdefault(r['id'],[]).append(r)
def digest(obj):return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest()
def save(name,obj):(DOC/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')

# Written after reading the 100 complete families and each of their four cases.
# These are reviewer judgments, not copied author ledger statements.
NOTES={
1:'Shared 1.1, AO2. Two distinct sectors explain value creation rather than just naming activities. Copper/sensors/data, cocoa/tastings, salt/electrolytes and frames/repair have different activity combinations. Routine explicit classification supports easy difficulty.',
2:'Shared 1.1, AO2. Each startup faces two independent constraints: cash versus adoption, credit timing versus selling skills, kiln dependence versus seasonality, or skills versus incumbent competition. No unsupported success forecast.',
3:'Shared 1.2, AO3. Sole-trader control and unlimited liability are applied to the stated financing/exposure decision; the recommendation does not assume incorporation removes every personal guarantee.',
4:'Shared 1.2, AO3. Partnership resource/skill benefits are weighed against shared responsibility and disagreements; no automatic claim that additional partners guarantee adequate finance.',
5:'Shared 1.2, AO3. Private-company ownership/control and finance consequences are conditional on case arrangements. Limited liability is distinguished from absence of all business risk.',
6:'Shared 1.2, AO3. Public share ownership can broaden finance but dilutes control and creates disclosure/return pressures. A listing is not treated as a guarantee of available funds or safe investment.',
7:'Shared 1.2, AO3. Cooperative member participation and mutual benefit are distinguished from pure shareholder-return objectives; coordination and reinvestment constraints remain case dependent.',
8:'Shared 1.2, AO3. NGO trading/funding decisions preserve the non-profit mission and do not imply that receiving revenue makes an organization for-profit. Donor restrictions and continuity are material.',
9:'Shared 1.3 with shared SWOT toolkit. Strategic/tactical objectives are tested against the particular business capabilities and external conditions; listing SWOT labels alone does not constitute evaluation.',
10:'Shared 1.3, AO3 plus shared circular-business-model toolkit. Ethical/environmental benefits are weighed against feasible costs, genuine recovery/reuse and customer evidence; no HL lean-production demand is smuggled into SL.',
11:'Shared 1.4, AO2. Two different stakeholder conflicts are explained in each night-shift, ticket-office, seed-supply and profiling case. The existing eight-mark format correctly avoids an AO3 demand.',
12:'Shared 1.5, AO2. Purchasing/technical/external economies are distinguished from internal control/communication diseconomies across all four cases. Discount and delay figures are contextual facts, not unasked calculation marks.',
13:'Shared 1.5, AO3. Reasons to remain small are weighed against scale/growth benefits in the actual niche/capacity setting. Small size is not assumed automatically efficient or sustainable.',
14:'Shared 1.5, AO3 and shared Ansoff toolkit. Joint ventures and growth routes address partner resources, control and market uncertainty; four cases require different conditions rather than one generic expansion judgment.',
15:'Shared 1.5, AO3. Franchise replication, support and control/royalty constraints are applied; the franchisee does not receive ownership of the franchisor’s entire business.',
16:'Shared 1.6, AO3. Corrected the four prompts to the host-country/host-government perspective actually supported by jobs, pollution, farmer dependence and public-guarantee evidence. Alternatives and enforceable conditions are accepted.',
17:'Shared decision-tree toolkit integrated with 1.5. Displayed probabilities sum to one; contribution terminal payoffs exclude the single launch cost. Compare net EV, certain alternative and downside without claiming guaranteed returns.',
18:'AHL because Porter generic strategies is an HL-only toolkit item. Broad-market cost leadership is distinguished from merely cutting price, and finance, retaliation and lost service differentiation vary between cases.',
19:'AHL because Porter generic strategies is HL only. Focused differentiation is tied to a narrow segment and real valued attributes; a specialist strategy does not ensure sufficient demand or remove imitation risk.',
20:'AHL because the complete Paper 3 assessment is HL only. All four 2+6+17 sets address different social needs and operating bottlenecks. Unrestricted cash and training-only grants are separated; the post-expansion two-month buffer is reconstructed. A/B/C/D criteria are 4/4/6/3 and use current OR-tool/theory guidance.',
21:'Shared 2.1, AO2. Workforce planning concerns skills, demographic/mobility effects and timing. It does not require HL-only recruitment-method or labour-turnover calculations.',
22:'Shared 2.1, AO3. Employee participation/change strategies address identifiable causes of resistance rather than assuming resistance is irrational. Consultation benefits and time/urgency constraints differ by case.',
23:'Shared 2.2, AO2/AO4. Each diagram has director, three functional managers and staff: three levels. Delayering removes the managers rather than counting them among retained staff; independently count all shown staff.',
24:'Shared 2.2 with AO3 appropriateness of structure. Delegation grants authority within case limits while the manager retains accountability; limits on refunds/purchases are not mistaken for full decentralization.',
25:'Shared 2.2 with AO3 appropriateness of structure. Local responsiveness is balanced against coordination, consistent standards and control. Different branch circumstances do not justify unrestricted authority in every case.',
26:'Shared 2.3, AO3. Democratic, autocratic, laissez-faire and paternalistic cases depend on urgency, staff capability and safety. A style is not labelled universally superior.',
27:'Shared Taylor motivation, AO3. Piece-rate/output incentives are conditional on quality and controllability of tasks. The cases’ different task difficulty and input constraints are not treated as worker laziness.',
28:'Shared Maslow motivation, AO3. Different employee groups can prioritize different needs; the models do not enforce a universal fixed sequence or presume pay alone resolves every need.',
29:'Shared Herzberg motivation, AO3. Enrichment/motivators are distinguished from poor hygiene conditions. Responsibility without time, support or safe conditions is not automatically motivating.',
30:'Shared training, AO2. On-job, off-job, induction and online delivery are applied to trainer workload, peak cover, actual machine practice and after-hours access. Existing eight-mark explanatory demand is appropriate.',
31:'Shared 2.6, AO3. App acknowledgement/connectivity, time zones/searchable records, checklist nuance and participation fear generate different communication trade-offs. Sending a message is not assumed to mean understanding.',
32:'AHL: shamrock organization and force-field reference are HL-only material. Flexible labour/contractor benefits are balanced against integration, confidentiality, service consistency and escalation.',
33:'AHL: scientific/intuitive management. AO2 explanations distinguish observable evidence from contextual managerial knowledge; six-week history, old rooms, new music and holiday traffic limit representativeness.',
34:'AHL: labour turnover and replacement-cost application. Average employment is expressly estimated as endpoint mean; every departure is replaced once. Retirement, relocation and timing prevent a causal inference of poor motivation.',
35:'AHL: appraisal. Corrected all four records from AO3 recommendation to AO2 applied explanation, matching the guide’s maximum demand. Two three-stage chains address coaching, confidentiality, expertise/case mix and project comparability.',
36:'AHL: internal/external recruitment at AO3. Technical capability, digital skills, vacancy chains and factional conflict support different appointments; seniority alone is not proof of suitability.',
37:'AHL: Deci/Ryan at AO3. Autonomy, competence and relatedness are distinguished. Junior isolation, crop handling, remote help and time-only care ratings show why freedom without support is insufficient.',
38:'AHL: equity, expectancy and McClelland. Corrected the equity and valence cases to one failure plus one explained response, avoiding duplicate reasons. Other two cases retain genuinely distinct expectancy/instrumentality or achievement/affiliation chains.',
39:'AHL: culture and Hofstede toolkit. Cultural clashes after mergers justify AO3. National/cultural dimensions are treated as testable tendencies, not deterministic stereotypes of every employee.',
40:'AHL: industrial relations. Negotiation, conciliation, arbitration and no-strike/single-union agreements are distinct. Conciliation is not automatically binding arbitration; bargaining rights and independent resolution remain material.',
41:'Shared 3.1, AO2. Each case explicitly distinguishes a durable acquisition/improvement from a current consumed service/input. No ambiguous life-extending repair is misclassified. Routine clear classification supports easy difficulty.',
42:'Shared 3.2, AO3 appropriateness of finance. Loan seasonality, retained-cash working capital, angel ownership and leasing flexibility produce different conditions. Retained profit is not assumed automatically liquid except where the case says cash.',
43:'Shared 3.2, AO3 appropriateness of short-term finance. Seasonal overdraft is distinguished from long-lived warehouse finance; 45/75-day credit leaves a gap. The supplied invoice-discounting mechanics require no unprovided specialist formula.',
44:'Shared 3.3, AO2 with arithmetic. Total monthly cost and average cost use consistent output units. More production does not imply sales; demand and selling price remain necessary for a profit conclusion.',
45:'Shared 3.3, AO2 with arithmetic. Explicitly non-overlapping services and subscriptions prevent double-counted revenue. Subscription share is relative to total earned revenue, and predictable receipts do not imply certain profit.',
46:'Shared 3.4, AO2/AO4. Gross profit, PBIT and after-tax profit follow the displayed statement. Timing of credit receipts, assets and debt payments prevents equating profit with a positive monthly cash balance.',
47:'Shared 3.4, AO2/AO4. Current assets, equity/net assets and working capital reconcile all displayed items. Positive working capital does not guarantee immediately available cash.',
48:'Shared 3.5, AO2/AO4. PBIT is expressly the profit-margin numerator. Recomputed both years of both ratios; rising revenue alone cannot establish better margins, including the case where both margins actually rise.',
49:'Shared 3.5 ratio calculation and AO3 financial strategy. Expansion comparisons use equity plus non-current liabilities and the stated forecast base. Higher absolute profit and a changed or unchanged ROCE do not settle capital allocation without risk and strategic evidence.',
50:'Shared 3.5, AO2/AO4. Cash payments are feasible and reduce assets and current liabilities equally. Corrected the two exact 1.625 ratios to 1.63; higher current ratio is not interpreted as higher cash.',
51:'Shared 3.7 with AO3 response to cash-flow risk. Monthly balances are cumulative; capital purchase occurs once at the start. The minimum spans all three months, while unknown intra-month timing remains an explicit limitation.',
52:'Shared 3.8, AO3/AO4. Payback crosses the actual cumulative inflows, including exact year-3 equality; even accrual supports fractional years. Later cash returns, financing and alternatives still matter.',
53:'Shared 3.8, AO3/AO4. ARR uses original capital cost as explicitly required. Total lifetime accounting profit deducts capital cost once before annual averaging; zero residual and constant forecast inflows are stated.',
54:'AHL: depreciation. Straight-line cost less residual is allocated over life, with requested complete years used for carrying value. Depreciation expense does not duplicate the initial cash payment.',
55:'AHL: units-of-production depreciation. Per-unit rate uses expected total output; annual expense uses actual output. Four-decimal unit rates are retained; uncertainty in lifetime capacity is acknowledged.',
56:'AHL: efficiency ratios. Stock uses average opening/closing inventory; debtor days use sales, creditor days expressly use cost of sales and all use 365 days. Faster collection can damage customer demand.',
57:'AHL: gearing and financial-strategy evaluation. New debt increases both non-current-liability numerator and capital-employed denominator. Control preservation is balanced against servicing risk, without a universal safe gearing threshold.',
58:'AHL: NPV. Each supplied four-decimal factor is used exactly rather than recomputed; time-zero cost is deducted once. Three positive and one negative NPV yield corresponding conditional rules, not guaranteed success.',
59:'AHL: budgets, AO2/AO4. Fixed-budget revenue and cost magnitudes have correct favorable/adverse signs. Corrected the generic favorable-revenue premise so all four cases, including adverse revenue, ask about revenue variance alone.',
60:'AHL: contribution/absorption toolkit. Fixed overhead uses normal output; spare-capacity special orders use incremental contribution. Below full cost can still add contribution; current non-displacement does not remove future customer-reaction risk.',
61:'Shared 4.1, AO2. Customer orientation is not blind compliance with every request: innovation, education, price and material-cost constraints differ. No guarantee that research mechanically produces a successful product.',
62:'Shared 4.1 market-share/growth calculations. Volumes refer to the same market and whole-market totals include own business. Both rising-share and falling-share variants distinguish absolute growth from relative position; no HL leadership evaluation required.',
63:'Shared 4.2, AO2. Life stage/usage, geography/benefits, commuter/leisure and travel/professional learning produce distinct segmentation and targeting chains rather than a generic demographic list.',
64:'Shared 4.2, AO2/AO4. All four position-map geometries support lower perceived price than A, similar high quality, and higher price/quality than B. Perceptions are not technical performance or guaranteed demand.',
65:'Shared 4.2, AO2. Sensory clothing, accessible tours, left-handed tools and controlled-texture meals support specialist differentiation but expose different scale, seasonality, distribution and customer-concentration constraints.',
66:'Shared 4.4, AO3 why/how research. Tasting, focus groups, observation and online surveys provide useful but differently biased evidence. Moderation, missing buyers, control periods and neutral wording are case-specific.',
67:'Shared 4.4, AO2 sampling. Convenience, unrepresentative quotas, random non-response and an incomplete cancellation sampling frame are distinct. Random selection is not assumed to remove frame or response bias.',
68:'Shared 4.5 extension strategies, AO3. New packaging, repair, expansions and colour refreshes must address actual customer problems and incremental demand. A campaign does not remedy zip defects or unused games.',
69:'Shared BCG toolkit. All rows are classified against the stated inclusive share/exclusive growth thresholds. The low-share/low-growth product can have positive cash flow; dog status does not automatically justify withdrawal.',
70:'Shared branding, AO2. Strengthened the second explanation in each case to avoid counting the same loyalty/trust effect twice: acquisition, premium margin, corrective operating cost and cannibalization now have distinct applied consequences.',
71:'Shared 4.5 cost-plus pricing, AO3. Mark-up is on cost; alternate price has its own quantity forecast. Revenue is not profit and cost may change with volume. Removed a floating-point artifact from the displayed working.',
72:'Shared 4.5 penetration pricing, AO3. Trial, retention, capacity, cartridge substitution and competitor matching vary by case. Introductory demand is not treated as proof of sustainable full-price demand.',
73:'Shared 4.5, AO3 social-media strategy. Integrated promotion connects awareness and response, while local reach, sponsorship transparency, actual capacity and substantiated sourcing constrain effectiveness.',
74:'Shared seven-P marketing mix, AO3. People/processes/physical evidence are common SL content. Every case distinguishes visible presentation from actual explanations, advice, follow-up or safe instruction.',
75:'AHL: sales forecasting and regression toolkit. Substitute only into the supplied equation; illustrations are not the complete estimation sample. Each proposed x is outside its stated observed range, and association does not prove causation.',
76:'AHL: PED. Original-value percentages, signed elasticity and revenue change are independently reconstructed. The numerical ceteris-paribus assumption does not carry over as a proven real-world causal fact in the recommendation.',
77:'AHL: dynamic pricing. Capacity/timing benefits are balanced against loyalty, essential access, reselling and driver/customer fairness. The different cases do not imply one uniform policy.',
78:'AHL: international marketing. Adaptation addresses product preferences, shared-device payments, non-stereotyped messages and rural repair/distribution. Appropriate standardization can remain part of a justified recommendation.',
79:'AHL: Gantt toolkit. Independently read bar endpoints against ticks: research precedes two parallel branches, both precede test. Durations assume unconstrained resources; the chart does not itself guarantee staff or funds.',
80:'AHL: importance of market leadership. Member counts, retailer volume, registrations and basic-unit sales are not automatically profit, engagement or mission value. Capacity, cash timing and cannibalization matter.',
81:'Shared 5.1, AO2. Each response links operations to two distinct other functions using actual lead-time, staffing, changeover or server constraints. Owning equipment alone does not create staffed service capacity.',
82:'Shared 5.2, AO3. Job versus batch suitability reflects setup economies, defect concentration and opportunity cost of displaced custom work. No unprovided HL make/buy arithmetic is demanded.',
83:'Shared 5.2, AO3. Modular high-volume systems offer choice but introduce component, colour, assembly and safe-separation constraints. Mass customization is distinguished from full bespoke job work.',
84:'Shared 5.4 location reasons, AO2. Corrected all four records to two applied three-stage explanation chains; no AO3 location recommendation remains. Rent, skills, uptime and wages support different benefits/limitations.',
85:'Shared 5.4, AO3 outsourcing. The specialist vendor’s savings/reach are balanced against clinical escalation, repairable seams, software knowledge and temperature control. Outsourcing does not transfer away brand responsibility.',
86:'Shared 5.4, AO3 reshoring. Total lead times, quality/skills, environmental investment and imported-component bottlenecks differ. Proximity alone does not prove full supply-chain responsiveness.',
87:'Shared 5.5, AO2/AO4. Contribution per unit, break-even output, forecast profit and margin of safety use monthly data consistently. This common contribution arithmetic does not imply the HL absorption/pricing toolkit.',
88:'Shared 5.5, AO2/AO4. Target quantity covers fixed cost plus target profit; target price solves the same equation. Clarified theoretical rounding versus the minimum whole-cent price, especially USD 11.44 versus USD 11.45.',
89:'Shared 5.5 arithmetic with AO3 limitations of break-even as a decision tool. Compare actual cost structures and both profits at forecast sales. Diagram is expressly schematic, and finance/transition/quality uncertainty prevents a mechanical automation verdict.',
90:'Shared 5.2 operations-method choice plus shared circular-model toolkit. Job/batch refurbishment and materials recovery reflect variable returned inputs. No HL cradle-to-cradle or lean theory is required for full credit.',
91:'AHL: lean/JIT and JIT-versus-JIC. Road closure, unstable orders, laundry breakdown and long premium-paper lead times make resilience case dependent. Low inventory is not a universal objective irrespective of stockout consequences.',
92:'AHL: quality management and organizational impacts of TQM/lean. Prevention, circles, benchmarking and certification do not guarantee zero defects. Staff trust, staged validation and cross-department outcomes are applied.',
93:'AHL: production planning and inventory. Reorder level includes lead-time consumption and buffer. Delayed receipt is measured immediately before delivery; physical stock cannot be negative, and unmet demand is reported separately.',
94:'AHL: production metrics. Four variants deliberately examine different metrics: capacity/labour, capital/defects, operating leverage and productivity change. Supplied definitions/time bases prevent denominator ambiguity and hours are not presumed unchanged.',
95:'AHL: make/buy and contribution toolkit. Only avoidable fixed cost enters make, delivered buying cost is explicit and crossover equality is independently substituted in both equations. Quality/reliability remain separate from arithmetic.',
96:'AHL: critical-path toolkit. Forward/backward passes and both complete paths independently reconstructed for all four networks. Total/free float is for the actually requested shorter-branch activity; private event times agree and do not appear in prompt figures.',
97:'AHL: contingency planning impact at AO3. Cold storage, data recovery, weather venue and dual sourcing trade ongoing cost against risk and continuity. An untested backup or insufficient-capacity alternative is not automatically usable.',
98:'AHL: R&D importance, with IP and innovation applied as supporting concepts. Cases distinguish patents, expression/brand rights, validated configurations and incremental relevance. No protection is assumed to monopolize every underlying idea or prove customer demand.',
99:'AHL: benefits/risks/ethics of MIS at AO3. Driver monitoring, loyalty profiling, rural IoT and VR scoring have different accuracy/access/resilience constraints. The model retains accountable human judgment and does not assume technology is unbiased.',
100:'AHL: force-field toolkit. Scores are subjective ordinal workshop judgments, not probabilities. Each actual proposed intervention addresses its case’s restraining force; totals cannot offset a binding safety/feasibility constraint.',
}
assert set(NOTES)==set(range(1,101))

families=[];records=[];changes=[]
for q in sorted(QS,key=lambda q:q['id']):
    fid=FAMILY[q['id']];family_number=int(re.match(r'bm(\d+)',fid)[1]);note=NOTES[family_number]
    assert ('AHL' in note)==(q['level']=='ahl'),(fid,q['level'],note)
    changed=[key for key in sorted(set(OLD[q['id']])|set(q)) if OLD[q['id']].get(key)!=q.get(key)]
    if changed:changes.append({'id':q['id'],'changedFields':changed,'beforeSha256':digest(OLD[q['id']]),'afterSha256':digest(q)})
    case=q['stem'].split('\n\n')[1]
    records.append({'id':q['id'],'status':'passed','family':fid,'level':q['level'],'syllabusCode':q['syllabusCode'],'highestDemandReview':note,'variantCase':case,'partsAndMarkAllocation':'All displayed prompts and private criteria read; exact allocations independently summed; best-fit rubric coverage/IND-only rule checked.','numericReview':{'report':'business-independent-numeric.json','checks':len(MATH[q['id']])} if q['id'] in MATH else {'reason':'No requested numerical output; assumptions and case-specific causal reasoning manually reviewed.'},'figureReview':{'status':'passed','count':len(FIGS[q['id']]),'svgHashes':[r['svgSha256'] for r in FIGS[q['id']]]} if q['id'] in FIGS else None,'difficulty':q['difficulty'],'difficultyReason':'Routine explicit classification and two short applied explanations; 8 marks alone does not make a question medium.' if q['difficulty']=='easy' else 'Conditional synthesis, balanced case evidence and an evaluative recommendation/plan.' if q['difficulty']=='hard' else 'Applied multi-stage explanations and/or linked calculations with interpretation.','corrections':changed,'sha256':digest(q)})
for family_number in range(1,101):
    famrecords=[r for r in records if int(re.match(r'bm(\d+)',r['family'])[1])==family_number]
    assert len(famrecords)==4
    # Keep a per-variant stimulus hash so renamed/numerically varied cases remain
    # separately traceable; this is not used as a proxy for semantic review.
    families.append({'family':famrecords[0]['family'],'status':'passed','review':NOTES[family_number],'ids':[r['id'] for r in famrecords],'variants':[{'id':r['id'],'stemSha256':hashlib.sha256(next(q['stem'] for q in QS if q['id']==r['id']).encode('utf8')).hexdigest(),'manualReview':'Full case and all four variant deltas read, including private indicative reasoning.'} for r in famrecords]})

save('business-independent-family-review.json',{'status':'passed','familyCount':100,'variantCount':400,'families':families})
save('business-independent-corrections.json',{'status':'passed','changedRecordCount':len(changes),'changes':changes,'decisions':['Host-country perspective aligned in MNC prompts and recommendation.','Appraisal and location families lowered to guide-permitted AO2: 2+6 marks, IDs preserved.','Two overlapping motivation explanations changed to one failure plus one response.','Branding second chains made independent of first-chain loyalty/trust consequences.','Budget explanation premise generalized for adverse as well as favorable revenue.','Exact 1.625 ratios rounded half-up to 1.63.','Target-price theoretical versus minimum whole-cent results distinguished.','Floating-point working cleaned; force-field grammar corrected.','Eight routine 8-mark foundational classifications labelled easy.'],'unchangedCounts':{'records':400,'families':100,'sl':260,'ahl':140},'reproduction':'Run business_fixes.py if restoring pre-review author sources; then business_build.py, business_numeric_review.py, business_verify.mjs and business_independent.py.'})

canonical={}
for p in FILES:
    b=p.read_bytes();assert b'\r' not in b and not b.startswith(b'\xef\xbb\xbf');b.decode('utf8');canonical[p.name]=hashlib.sha256(b).hexdigest()
sources={'guide':{'url':'https://xmltwo.ibo.org/publications/EAD/2026_EN/GR3/GR3-BM_EN_24.pdf','edition':'First assessment 2024, updated July 2024; current PDF linked by 2027 examiner instructions','reviewed':'Official primary source read through its examiner-instructions link. Scope table, command-term ceiling and assessment structure checked.'},'examinerInstructions':{'url':'https://ibpublishing.ibo.org/exinst/apps/exinst/index.html?chapter=1&doc=EX_instructions_2027_e&part=10','reviewed':'2027 Paper 1/2 caps and 10-mark guidance; Paper 3 2+6+17 with 4/4/6/3 criteria, resource synthesis, OR-tool/theory guidance and sequencing clarifications.'}}
evidence_names=['business-independent-input.json','business-independent-numeric.json','business-independent-family-review.json','business-independent-corrections.json','business-independent-figures/render-ledger.json','business-author-ledger.json','business-final-review-ledger.json','business-numeric-review-report.json','business-render-schema-report.json']
gate={'status':'passed','questionCount':400,'familyCount':100,'numericQuestionCount':len(MATH),'numericAssertions':NUM['numericalAssertions'],'figureCount':44,'levels':dict(Counter(q['level'] for q in QS)),'difficultyCounts':dict(Counter(q['difficulty'] for q in QS)),'canonicalFiles':canonical,'sources':sources,'evidenceHashes':{name:hashlib.sha256((DOC/name).read_bytes()).hexdigest() for name in evidence_names},'records':records,'limits':'Independent AI subject review, not human examiner moderation, psychometric calibration or a claim of IB endorsement. All 100 families and 400 variants were read; numerical outputs were independently reconstructed from serialized displayed inputs, and every final SVG was rendered and visually inspected.'}
save('business-independent-review.json',gate)
print(json.dumps({k:v for k,v in gate.items() if k not in ('records','sources','evidenceHashes')},indent=2))
