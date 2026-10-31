"""Reproducible, targeted source corrections arising from the independent review."""
from pathlib import Path
import ast, json

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'scripts/ib-expansion-authoring'

def edit(name,changes):
    p=SRC/name;s=p.read_text(encoding='utf8')
    for old,new in changes:
        if old in s:s=s.replace(old,new)
        elif new not in s:raise AssertionError((name,old))
    p.write_text(s,encoding='utf8',newline='\n')

edit('business_build.py',[
 ("exam='paper-2',scope=''):\n    \"\"\"16-mark", "exam='paper-2',scope='',beneficiary=None,decision_maker=None):\n    \"\"\"16-mark"),
 ("for {name} of {decision}.","for {beneficiary or name} of {decision}."),
 ("recommend whether {name} should proceed with {decision}.","recommend whether {decision_maker or name} should proceed with {decision}."),
 ("'difficulty':'hard' if any(x[0]['marks']>=10 for x in items) else 'medium'", "'difficulty':'easy' if family in {'bm01-sectors','bm41-capital-revenue'} else ('hard' if any(x[0]['marks']>=10 for x in items) else 'medium')"),
])
edit('business_unit1.py',[
 ("'building the proposed foreign production facility',[", "'supporting {name}’s proposed foreign production investment',["),
 ("forecast demand are not disclosed.')],exam='paper-1')", "forecast demand are not disclosed.')],exam='paper-1',beneficiary='the host country',decision_maker='the host government')"),
])

# These content items have a maximum teaching demand of AO2 in the current guide.
# Keep the cases and two distinct applied chains, without an AO3 recommendation.
extras={
 'bm35-appraisal':[
  ('Development can therefore target coaching weaknesses that a sales-only review overlooks.','Mistrust may make managers reject useful developmental advice.'),
  ('The combined evidence can identify cross-role coordination skills to develop.','Fearful respondents may withhold the very weaknesses the appraisal is meant to identify.'),
  ('Supervisors can use this evidence to improve explanations and patient access.','A misleading low score may direct training toward the wrong problem.'),
  ('Repeated observations can identify support skills that remote leaders need to develop.','Comparing raw ratings may incorrectly label a leader as weaker because of the project assigned.'),
 ],
 'bm84-location':[
  ('A lower regular rent can reduce the sales needed to cover bakery overhead.','Lost morning sales and recruitment difficulties could reduce operating profit despite cheaper rent.'),
  ('Shorter input lead times and less initial training can reduce production delays.','Interrupted precision work may create defective lenses and missed delivery commitments.'),
  ('Lower ongoing energy costs could reduce the cost of hosting each client.','Connection failure could breach client service commitments and cause lost contracts.'),
  ('Existing specialist skills can help the workshop begin reliable production sooner.','The higher wage bill may offset the savings from nearby timber suppliers.'),
 ]}
for filename,family in [('business_unit2.py','bm35-appraisal'),('business_unit5.py','bm84-location')]:
    p=SRC/filename;s=p.read_text(encoding='utf8');tree=ast.parse(s)
    calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='ef' and len(n.args)>1 and ast.literal_eval(n.args[1])==family]
    if calls:
        n=calls[0];args=[ast.literal_eval(x) for x in n.args]
        rows=[]
        for row,(extra1,extra2) in zip(args[8],extras[family]):
            name,context,pro,con,condition,missing=row
            rows.append((name,context,[pro.split(';',1)[0]+'.',pro.split(';',1)[1]+'.',extra1],[con.split(';',1)[0]+'.',con.split(';',1)[1]+'.',extra2]))
        args[7]='Explain one advantage and one limitation for {name} of '+args[7]+'.'
        args[8]=rows
        replacement='af('+','.join(repr(x) for x in args[:8])+',[\n'+',\n'.join(repr(x) for x in rows)+"],exam='paper-2',scope='Current guide: this content is AO2; two applied explanation chains, no AO3 evaluation demanded.')"
        lines=s.splitlines(keepends=True);s=''.join(lines[:n.lineno-1])+replacement+'\n'+''.join(lines[n.end_lineno:])
        p.write_text(s,encoding='utf8',newline='\n')

# Two variants contain one motivational failure, rather than two independent ones.
# Their second chain now explains a concrete response instead of double-counting it.
edit('business_unit2.py',[
 ("['Relevant comparisons need not be objectively identical.','Cru’s staff judge rewards against colleagues with easier territories.','A clear explanation and review of territory difficulty may matter more than a uniform bonus increase.']", "['Review bonuses or targets to reflect territory difficulty.','Cru can compare the extra effort required in experienced staff’s harder territories before setting rewards.','A transparent adjustment can improve perceived input–outcome fairness and restore effort.']"),
 ("['Reward preferences differ among employees.','A benefit valued by travelling managers may not suit reception staff’s budgets.','Offering a meaningful choice could raise valence without changing the target.']", "['Offer a choice of rewards within the same affordable budget.','Fru’s reception staff could select a locally usable benefit rather than a distant stay they cannot travel to.','A reward employees value raises valence while leaving the achievable target and reliable payment unchanged.']"),
])
# Set only these two variants' wording, leaving expectancy/instrumentality and
# achievement/affiliation as two distinct explanations in the other variants.
edit('business_build.py',[("items=[define('a',term,meaning),explain('b',prompt.replace('{name}',name),chain1+chain2)]", "current_prompt=prompt.replace('{name}',name)\n        if family=='bm38-hl-motivation-diagnosis' and name in {'Cru Sales','Fru Rooms'}:\n            current_prompt='Using relevant HL motivation theory, explain why the stated reward may fail to motivate employees, and explain one appropriate response by the business.'\n        items=[define('a',term,meaning),explain('b',current_prompt,chain1+chain2)]")])

edit('business_unit3.py',[
 ("Explain why a favorable revenue variance does not automatically mean the manager performed better overall.","Explain why the revenue variance alone is insufficient to judge the manager’s overall performance."),
 ("f'{new:.2f}:1.'", "f'{Decimal(str(new)).quantize(Decimal(\"0.01\"),rounding=ROUND_HALF_UP)}:1.'"),
 ("Current={cur:.2f}:1; acid test={quick:.2f}:1.","Current={Decimal(str(cur)).quantize(Decimal(\"0.01\"),rounding=ROUND_HALF_UP)}:1; acid test={Decimal(str(quick)).quantize(Decimal(\"0.01\"),rounding=ROUND_HALF_UP)}:1."),
])
p=SRC/'business_unit3.py';s=p.read_text(encoding='utf8')
if 'from decimal import Decimal, ROUND_HALF_UP' not in s:s='from decimal import Decimal, ROUND_HALF_UP\n'+s
p.write_text(s,encoding='utf8',newline='\n')

edit('business_unit4.py',[
 ("f'{p}×{forecast}.'", "f'{p:.2f}×{forecast}.'"),
 ("['Brand value may be damaged by negative reviews.','The lifetime repair claim creates an expectation beyond a normal bottle sale.','Aze may need to restore parts access and communicate accurately to protect its differentiation.']", "['Negative reviews may deter new customers as well as existing buyers.','People researching Aze’s lifetime repair promise may find reports of unavailable lids.','Lower acquisition of first-time buyers can reduce sales even before current customers need replacement bottles.']"),
 ("['Brand awareness alone may not secure value.','Customers can recognize the name while distrusting its claims.','Bze must align the message with actual sourcing to preserve a premium based on local origin.']", "['The premium price may become harder to sustain.','Imported ingredients remove the local-origin benefit that supported Bze’s differentiation.','If buyers demand a lower price while other costs remain unchanged, profit per snack falls.']"),
 ("['A strong existing brand may amplify disappointment.','Loyal users have learned to expect same-day work.','Cze needs realistic communication and operational correction to avoid damaging repeat business.']", "['Restoring the service promise may raise operating costs.','Cze may need extra trained repairers or overtime to reduce the four-day backlog to same-day delivery.','Those corrective costs can reduce profit even if the business retains its customers.']"),
 ("['Brand loyalty may decline if perceived quality changes.','Existing buyers may believe standards have fallen across all products.','Clear range identities and consistent minimum quality can help protect Dze’s reputation.']", "['The cheaper range may cannibalize premium sales.','The shared logo and unclear range distinction can encourage existing buyers to trade down.','Unless the additional volume compensates, switching purchases can reduce total contribution from the original premium range.']"),
])
edit('business_unit5.py',[
 ("Calculate the selling price needed to achieve the target profit at {q:,} units.","Calculate the theoretical selling price needed for the target profit at {q:,} units, to two decimals. Also state the minimum price in whole cents that would meet or exceed the target."),
 ("f'USD {price:.2f} per unit.'", "f'Theoretical price USD {price:.2f} per unit; minimum whole-cent price USD {math.ceil(round(price*100,10))/100:.2f} per unit. The accuracy mark requires both, including upward cent rounding where needed.'"),
 ("f'The proposed {proposal} directly addresses", "f'The intervention ({proposal}) directly addresses"),
])
print('Targeted business authoring-source corrections applied.')
