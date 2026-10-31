from economics_author import *

def build():
    topic='introduction'
    for f in range(14):
      for v in range(3 if f<12 else 2):
        town=CASES[(f*3+v)%len(CASES)]
        h=30+6*v; k=20+5*v
        base=f'All places, agents and data in this question are constructed for practice. In {town}, '
        code='1.1' if f<9 else '1.2'; diagram=None; nums=[]
        if f==0:
            stem=base+f'a local clinic has {h} staff-hours available on a Saturday. One screening uses 2 staff-hours and one home visit uses 3. All staff-hours are fully usable for either service.'
            title='Scarce clinic time and opportunity cost'
            ps=[point('a','Define scarcity.',2,('A1','Resources are limited relative to the wants they could satisfy.'),('A1','Consequently choices between competing uses are necessary; a shortage at one price alone is not the definition.')),
                point('b','Calculate the maximum number of screenings if no home visits are offered.',2,('M1',f'Maximum screenings = {h}/2.'),('A1',f'{h//2} screenings.')),
                point('c','Explain the opportunity cost of allocating 6 staff-hours to home visits instead of screenings.',4,('A1','Six hours permit two home visits.'),('A1','The same hours could provide three screenings.'),('R1','The opportunity cost is the next best alternative forgone: three screenings.'),('R1','The monetary wage bill need not change; the forgone service is still a cost.'))]
            nums=[{'expression':f'{h}/2','expected':h/2}]
        elif f==1:
            stem=base+'a workshop uses a leased building, a forest parcel, trained carpenters and a founder who coordinates production and bears commercial risk.';title='Classifying productive resources'
            ps=[point('a','Identify the factor of production represented by the forest parcel and explain why.',2,('A1','Land.'),('R1','It is a natural resource rather than a produced input.')),
                point('b','Distinguish the building from the carpenters as factors of production.',2,('A1','The produced building is capital used to make other output.'),('A1','The carpenters supply labour: human effort and skills.')),
                point('c','Explain the founder\'s entrepreneurial role and one associated opportunity cost.',4,('A1','The founder organizes the factors of production.'),('R1','The founder makes decisions under uncertainty and bears risk.'),('A1','For example, the founder forgoes a salaried management job.'),('R1','That next best alternative income is an opportunity cost even if it is not an accounting payment.'))]
        elif f==2:
            stem=base+f'a repair centre can produce the following combinations using all its current resources.\n\n'+table(['Combination','Bicycles repaired','Radios repaired'],[['A',0,60+12*v],['B',10,54+12*v],['C',20,42+12*v],['D',30,24+12*v]])+'No technical change occurs.';title='Increasing opportunity cost on a frontier';diagram='ppc-repairs'
            ps=[point('a','Calculate the opportunity cost in radios of moving from B to C.',2,('M1',f'Radios forgone = {54+12*v} − {42+12*v}.'),('A1','12 radios.')),
                point('b','Calculate the opportunity cost per bicycle from C to D.',2,('M1',f'({42+12*v} − {24+12*v})/(30 − 20).'),('A1','1.80 radios per bicycle.')),
                point('c','Explain why these data are consistent with a bowed-out PPC.',4,('A1','The sacrifice for ten extra bicycles rises from 6 to 12 to 18 radios.'),('R1','Thus marginal opportunity cost rises as bicycle repairs expand.'),('A1','Some tools and skills suit radio repair better than bicycle repair.'),('R1','Reallocation increasingly uses less suitable resources; this generates the bowed-out frontier.'))]
            nums=[{'expression':'(42-24)/(30-20)','expected':1.8}]
        elif f==3:
            stem=base+f'a cooperative has {h} interchangeable machine-hours. One basket requires 3 hours and one stool requires 6 hours. The input requirements remain constant.';title='Constant cost and a linear PPC';diagram='ppc-linear'
            ps=[point('a','Calculate both intercepts of the PPC.',2,('A1',f'{h//3} baskets when no stools are made.'),('A1',f'{h//6} stools when no baskets are made.')),
                point('b','State the opportunity cost of one additional stool.',2,('A1','Two baskets.'),('R1','A stool uses the six hours that could make two baskets.')),
                point('c','Explain why this PPC is a straight line rather than bowed out.',4,('A1','Resources are equally adaptable to the two products in the stated model.'),('R1','The resource requirement ratio is constant at 6:3.'),('A1','Every stool displaces the same two baskets.'),('R1','A constant marginal opportunity cost gives a constant slope; specialize resources differently and this assumption may fail.'))]
            nums=[{'expression':f'{h}/3','expected':h/3},{'expression':f'{h}/6','expected':h/6}]
        elif f==4:
            stem=base+'a power outage leaves some productive machines idle. Engineers later restore power without adding machines or improving skills.';title='Recovery within an unchanged PPC';diagram='ppc-recovery'
            ps=[point('a','State where the economy lies relative to its PPC during the outage.',2,('A1','Inside the frontier.'),('R1','Some available resources are unemployed or used inefficiently.')),
                point('b','Distinguish actual growth from growth of production possibilities.',2,('A1','Actual growth raises realized output, for example by using idle machines.'),('A1','Growth of possibilities raises productive capacity and shifts the PPC outward.')),
                point('c','Using a PPC diagram, explain the immediate effect of restoring power.',4,('A1','Correctly labelled output axes and an unchanged frontier.'),('A1','A movement from an interior point toward the frontier.'),('R1','More existing resources become usable, so actual production increases.'),('R1','There is no stipulated increase in resource quantity, quality or technology to justify an outward frontier shift.'))]
        elif f==5:
            stem=base+'a training programme improves only the productivity of workers making heat pumps. Output of food with all resources devoted to food is unchanged.';title='A sector-specific capacity improvement';diagram='ppc-sector'
            ps=[point('a','Identify one change in the quality of a factor of production.',2,('A1','Worker skill/human capital improves.'),('R1','The same labour input can produce more heat pumps.')),
                point('b','State how each intercept of a food/heat-pump PPC changes.',2,('A1','The heat-pump intercept increases.'),('A1','The food intercept is unchanged in the stated case.')),
                point('c','Explain why growth in production possibilities does not guarantee higher current output.',4,('A1','The frontier records potential, not necessarily realized, output.'),('R1','Demand may be weak so firms do not use the new capability.'),('A1','Complementary inputs or finance may also be missing.'),('R1','An interior allocation may persist despite the outward rotation of the frontier.'))]
        elif f==6:
            stem=base+'households buy meals from firms and supply labour to them. The households save some income with banks; banks lend to firms for new ovens.';title='Real flows, money flows and interdependence'
            ps=[point('a','Distinguish one real flow from its corresponding money flow.',2,('A1','Labour services move from households to firms.'),('A1','Wages move from firms to households in the opposite direction.')),
                point('b','Identify the leakage and injection mentioned.',2,('A1','Saving is a leakage from the domestic income flow.'),('A1','Investment expenditure on ovens is an injection.')),
                point('c','Explain the interdependence of firms, households and banks in this case.',4,('A1','Household consumption provides firms with sales revenue.'),('R1','Firms pay factor incomes that fund household consumption and saving.'),('A1','Banks intermediate saving into business borrowing.'),('R1','Investment generates demand for capital goods and may increase future productive capacity; saving is not automatically identical to current domestic investment.'))]
        elif f==7:
            s=14+v;t=18+2*v;m=20+v;i=16+v;g=22+2*v;x=14+v
            stem=base+'the following annual flows are recorded, in million crowns.\n\n'+table(['Flow','Value'],[['Saving',s],['Taxes',t],['Imports',m],['Investment',i],['Government spending',g],['Exports',x]])+'Treat the model as a simple circular flow at the stated income.';title='Leakages and injections at an income level'
            ps=[point('a','Calculate total leakages.',2,('M1',f'S + T + M = {s}+{t}+{m}.'),('A1',f'{s+t+m} million crowns.')),
                point('b','Calculate total injections.',2,('M1',f'I + G + X = {i}+{g}+{x}.'),('A1',f'{i+g+x} million crowns.')),
                point('c','Explain the direction of pressure on the income flow if these planned flows persist.',4,('A1',f'Injections and leakages both equal {s+t+m} million crowns.'),('R1','There is no net planned injection at this income.'),('A1','The circular-flow condition is I + G + X = S + T + M.'),('R1','This is an equilibrium of the flow model, not proof of full employment, equity or sustainability.'))]
            nums=[{'expression':f'{s}+{t}+{m}','expected':s+t+m},{'expression':f'{i}+{g}+{x}','expected':i+g+x}]
        elif f==8:
            stem=base+'a council must choose whether scarce river water goes to farms or a public recreation lake. Water is allocated by prices in one proposal and by a public quota in another.';title='The three economic questions and allocation'
            ps=[point('a','Identify two basic economic questions illustrated by the allocation.',2,('A1','What/how much to produce: farm output versus recreation services.'),('A1','For whom to produce: which users receive the water and benefits.')),
                point('b','Distinguish a market allocation from a government allocation here.',2,('A1','The market proposal uses prices and willingness/ability to pay.'),('A1','The quota proposal uses an administrative decision or rule.')),
                point('c','Explain why either system still faces opportunity cost.',4,('A1','River water is limited and has competing uses.'),('R1','Allocating more water to the lake leaves less for farms.'),('A1','The forgone farm output is a possible next best alternative.'),('R1','Changing the allocation institution does not remove the underlying scarcity.'))]
        elif f==9:
            stem=base+'two claims appear in a transport debate: “A lower fare will increase bus journeys, other things equal” and “Bus access should be equal for every resident.”';title='Positive and normative economic statements'
            ps=[point('a','Classify the first claim and explain your classification.',2,('A1','Positive.'),('R1','It makes a potentially testable causal prediction; it need not be true to be positive.')),
                point('b','Classify the second claim and explain your classification.',2,('A1','Normative.'),('R1','The word “should” expresses a value judgement about a desirable distribution.')),
                point('c','Explain why evidence alone may not resolve the whole debate.',4,('A1','Observed fare and journey data can help test the positive prediction.'),('R1','Confounders such as service frequency must be controlled.'),('A1','Different residents may place different values on equality, budget cost and efficiency.'),('R1','Evidence clarifies consequences but cannot by itself select society\'s ethical priorities.'))]
        elif f==10:
            stem=base+'a shop cuts its price just as a festival doubles visitors to the town. Sales rise and the owner attributes the whole increase to the price cut.';title='Ceteris paribus and confounding variables'
            ps=[point('a','Explain the ceteris paribus assumption.',2,('A1','Other relevant influences are held constant.'),('R1','It isolates a particular relationship, such as price and quantity demanded.')),
                point('b','Identify the confounding influence in this case.',2,('A1','The festival increases the number of potential customers.'),('R1','It can raise sales independently of the price cut.')),
                point('c','Explain how the owner could improve the empirical test.',4,('A1','Compare similar periods or shops with similar festival exposure.'),('R1','Vary the price while holding important demand conditions as constant as feasible.'),('A1','Collect observations before and after rather than relying on one coincidence.'),('R1','Acknowledge remaining differences and uncertainty; correlation alone does not identify the whole price effect.'))]
        elif f==11:
            stem=base+'a model predicts that a longer queue increases waiting time, assuming unchanged staffing and service times. A second clerk starts work on the day the queue lengthens, and observed waiting time falls.';title='Models, evidence and refutation'
            ps=[point('a','State the model\'s conditional hypothesis.',2,('A1','With staffing and service times unchanged, a longer queue increases waiting time.'),('R1','The prediction depends on its stated assumptions.')),
                point('b','Explain why this observation is not a clean refutation.',2,('A1','Staffing changed.'),('R1','The observation does not hold the model\'s conditioning variables constant.')),
                point('c','Explain two useful roles of a simplified economic model.',4,('A1','It isolates a causal mechanism from many simultaneous influences.'),('R1','This makes a conditional prediction that can be tested.'),('A1','It provides a framework for interpreting evidence and comparing policies.'),('R1','Its omissions and assumptions must be assessed before applying the prediction to a particular setting.'))]
        elif f==12:
            stem=base+'a scholarship gives every applicant the same payment. A second plan gives larger payments to students with lower household incomes.';title='Equality, equity and normative choices'
            ps=[point('a','Explain the meaning of equality in the first plan.',2,('A1','Each applicant receives an identical monetary payment.'),('R1','This is equality of the specified outcome, not necessarily equality of opportunity.')),
                point('b','Explain why the second plan could be considered more equitable.',2,('A1','It directs more assistance toward greater financial need.'),('R1','Fairness can justify unequal payments to reduce unequal opportunities.')),
                point('c','Explain why economists may disagree about which plan is fairer.',4,('A1','Equity involves a normative judgement.'),('R1','One view values identical treatment, another values compensating disadvantage.'),('A1','Evidence about access and incentives can inform their judgements.'),('R1','The evidence does not eliminate differences in ethical weighting of those outcomes.'))]
        else:
            stem=base+'a study of economic ideas contrasts Smith\'s price coordination, Keynes\'s concern with deficient aggregate spending, and modern attempts to reuse materials in a circular economy.';title='Economic thought in changing contexts'
            ps=[point('a','Explain how the price mechanism can coordinate choices in a market system.',2,('A1','Relative prices communicate scarcity and consumer demand.'),('R1','They create incentives for producers and consumers to adjust their decisions.')),
                point('b','Explain the reason for Keynesian interest in aggregate demand.',2,('A1','Total planned spending may be insufficient for full employment.'),('R1','An economy can then remain below capacity even when productive resources exist.')),
                point('c','Explain how a circular-economy perspective extends the analysis of scarcity.',4,('A1','Material resources and environmental absorption capacity are finite.'),('R1','Repair, reuse and recycling can reduce virgin resource extraction and waste.'),('A1','Production and consumption are interdependent with ecosystems.'),('R1','The framework broadens analysis beyond current market output to resource use over time; it does not claim to eliminate opportunity cost.'))]
        add(topic,f'intro-{f+1:02}',v,code,title+' — '+town,'What is economics?' if code=='1.1' else 'Economic methodology and thought','sl','paper-2','structured',stem,ps,diagram,nums,difficulty='easy' if f in [0,1,6,9,12] else 'medium')
