"""Independent R2 calculations from visible prompts/tables, not authoring inputs."""
import math
import re
from fractions import Fraction
import xml.etree.ElementTree as ET
from audit_reactivity12 import NUMBER as N, clean, take, quantities


def vals(a,unit):
    return [a.given(unit+'_'+str(j),value,evidence) for j,(value,evidence) in enumerate(quantities(a,unit))]


def rows(a,cols):
    pattern=r'\|\s*'+r'\s*\|\s*'.join('('+N+')' for _ in range(cols))+r'\s*\|'
    data=[list(map(float,row)) for row in re.findall(pattern,a.prompt)]
    a.entry['inputs']['displayed_numeric_table']=data
    return data


def formula(counts):
    return ''.join(el+('' if n==1 else '_'+str(n) if n<10 else '_{'+str(n)+'}') for el,n in counts)


def review(a):
    for i in range(1,5):
        a.begin(i,'sl','Complete copper oxidation with excess oxygen; copper:CuO mole ratio is1:1 and supplied rounded molar masses are explicit.')
        m=take(a,'copper_g',r'excess and \$('+N+')'); M,Mo=vals(a,'g')[1:3]
        a.result('CuO mass','copper_g/M(Cu)*M(CuO)',m/M*Mo,'g')
        a.equation('copper oxidation',[(2,'Cu',0),(1,'O2',0)],[(2,'CuO',0)])
    for i in range(5,9):
        a.begin(i,'sl','Limiting extent is minimum of Mg amount and HCl amount/2; excess amount is reported for the correct remaining species.')
        m=take(a,'Mg_g',r'A \$('+N+')'); V=take(a,'acid_cm3',r'with \$('+N+')')
        c=take(a,'acid_concentration',r'concentration \$('+N+')'); M=take(a,'Mg_M',r'Use \$('+N+')')
        mg=m/M; acid=V*c/1000; extent=min(mg,acid/2)
        a.result('Mg initial amount','mass/M',mg,'mol');a.result('HCl initial amount','V*c/1000',acid,'mol')
        a.result('hydrogen amount','min(Mg,HCl/2)',extent,'mol')
        if mg<acid/2:
            a.result('HCl remaining','HCl-2*extent',acid-2*extent,'mol');a.require('Magnesium is limiting')
        else:
            a.result('Mg remaining','Mg-extent',mg-extent,'mol');a.require('Hydrogen chloride is limiting')
        a.equation('magnesium acid reaction',[(1,'Mg',0),(2,'HCl',0)],[(1,'MgCl2',0),(1,'H2',0)])
    for i in range(9,13):
        a.begin(i,'sl','1:1 CO-to-methanol stoichiometry and actual/theoretical percentage yield; incomplete conversion or recovery losses are valid.')
        m,actual,M,Mo=vals(a,'g')[:4]; theory=m/M*Mo
        a.result('theoretical mass','CO_mass/M(CO)*M(methanol)',theory,'g')
        a.result('percentage yield','actual/theoretical*100',actual/theory*100,'%')
        a.equation('methanol synthesis',[(1,'CO',0),(2,'H2',0)],[(1,'CH3OH',0)])
    atom_equations=[([(1,'C2H4',0),(1,'H2O',0)],[(1,'C2H5OH',0)]), ([(1,'C2H5Br',0),(1,'NaOH',0)],[(1,'C2H5OH',0),(1,'NaBr',0)]), ([(1,'C2H5OH',0),(1,'O2',0)],[(1,'CH3COOH',0),(1,'H2O',0)]), ([(1,'CH3COOH',0),(1,'C2H5OH',0)],[(1,'CH3COOC2H5',0),(1,'H2O',0)])]
    for i,(lhs,rhs) in zip(range(13,17),atom_equations):
        a.begin(i,'sl','Target-product molar mass divided by total stoichiometric reactant mass; all stated coefficients are1.')
        m1,m2,target=vals(a,'g')[:3]
        a.result('atom economy','target/(m1+m2)*100',100*target/(m1+m2),'%')
        a.equation('synthetic-route atom balance',lhs,rhs)
    for i in range(17,21):
        a.begin(i,'sl','Supplied complete neutralization equation is used as stoichiometry; no diprotic pH/titration-curve theory is assumed. Mean includes all stated concordant data.')
        V=take(a,'acid_volume',r'titration, \$('+N+')')
        c=take(a,'NaOH_concentration',r'concentration \$('+N+')')
        table=rows(a,2);mean=sum(t[1] for t in table)/len(table);n=c*mean/1000
        a.result('mean titre','sum(titres)/3',mean,'cm^3')
        a.result('NaOH amount','c*mean/1000',n,'mol')
        a.result('H2SO4 concentration','(NaOH_mol/2)/(acid_volume/1000)',n*500/V,'mol dm^-3')
        a.equation('complete sulfuric neutralization',[(1,'H2SO4',0),(2,'NaOH',0)],[(1,'Na2SO4',0),(2,'H2O',0)])
        a.require('dilute')
    for i in range(21,25):
        a.begin(i,'sl','Mass percentages converted independently to mole proportions; small integer ratios justified by rounded percentages, molecular mass fixes multiplier.')
        C=take(a,'carbon_percent',r'gives ('+N+')% carbon');H=take(a,'hydrogen_percent',r', ('+N+')% hydrogen');O=take(a,'oxygen_percent',r'and ('+N+')% oxygen')
        M=take(a,'molar_mass',r'molar mass is \$('+N+')')
        raw=[C/12,H,O/16];small=min(raw);counts=[round(x/small) for x in raw]
        assert max(abs(x/small-count) for x,count in zip(raw,counts))<.02
        emass=sum(x*y for x,y in zip(counts,[12,1,16]));mult=round(M/emass)
        a.entry['inputs']['computed_mole_ratio']=raw
        a.result('empirical formula mass','sum(integer elemental count*atomic mass)',emass,'g mol^-1')
        a.result('molecular multiplier','molar_mass/empirical_mass',M/emass)
        a.require(formula(zip(['C','H','O'],counts)))
        a.require(formula(zip(['C','H','O'],[x*mult for x in counts])))
    for i,metal in zip(range(25,29),['Ca','Mg','Sr','Ba']):
        a.begin(i,'sl','Carbonate produces one mole of CO2 per mole with excess acid; supplied molar volume and molar mass used.')
        m=take(a,'carbonate_g',r'A \$('+N+')');M=take(a,'carbonate_M',r'molar mass \$('+N+')')
        Vm=take(a,'gas_molar_volume',r'molar volume \$('+N+')')
        a.result('carbonate amount','mass/M',m/M,'mol');a.result('CO2 volume','mass/M*Vm',m/M*Vm,'dm^3')
        a.equation('carbonate acid reaction',[(1,metal+'CO3',0),(2,'HCl',0)],[(1,metal+'Cl2',0),(1,'CO2',0),(1,'H2O',0)])
    for i in range(29,33):
        a.begin(i,'sl','Combustion analysis gives nC=nCO2 and nH=2*nH2O; independent rational ratio and molar mass determine empirical and molecular formulas.')
        co2,water,M=vals(a,'g')[:3];C=co2/44;H=2*water/18
        ratio=Fraction(H/C).limit_denominator(20);counts=[ratio.denominator,ratio.numerator];emass=12*counts[0]+counts[1];mult=round(M/emass)
        a.result('carbon amount','CO2_mass/44',C,'mol');a.result('hydrogen-atom amount','2*water_mass/18',H,'mol')
        a.require(formula(zip(['C','H'],counts)));a.require(formula(zip(['C','H'],[x*mult for x in counts])))
        a.entry['inputs']['independent_formula_result']={'empiricalCounts':counts,'empiricalMass':emass,'molecularMultiplier':mult}
    for i in range(33,37):
        a.begin(i,'sl','Positive disappearance rate uses initial minus final concentration over elapsed time.')
        initial,final=vals(a,'mol')[:2];t=take(a,'time_s',r'in \$('+N+')')
        a.result('average disappearance rate','(initial-final)/time',(initial-final)/t,'mol dm^-3 s^-1')
    for i in range(37,41):
        a.begin(i,'sl','Stoichiometric species rates: oxygen formation is half peroxide disappearance for the stated volume basis.')
        rate=take(a,'peroxide_disappearance',r'peroxide is \$('+N+')')
        a.result('oxygen formation rate','peroxide_rate/2',rate/2,'mol dm^-3 s^-1')
        a.equation('peroxide decomposition',[(2,'H2O2',0)],[(2,'H2O',0),(1,'O2',0)])
    for i,reason,fragment in [(41,'Higher temperature increases the energy-distribution fraction above Ea.','fraction'),(42,'Powder increases exposed reactive area at fixed mass.','surface'),(43,'Higher concentration can increase collision frequency at fixed temperature.','frequency'),(44,'Catalyst changes pathway/barrier, not equilibrium thermodynamics.','equilibrium constant')]:
        a.begin(i,'sl',reason);a.require(fragment)
    for i in range(45,49):
        q=a.begin(i,'sl','Single-barrier catalysed profiles are shared; Ea measured from reactant level, ΔH from product minus reactant; lower peak does not change endpoints.')
        root=ET.fromstring(q['diagramSvg']);items=[(e.text,float(e.get('x')),float(e.get('y'))) for e in root.iter() if e.tag.endswith('text') and e.text]
        levels={}
        for label in ['reactants','products','uncatalysed','catalysed']:
            _,_,y=next(e for e in items if e[0]==label)
            value=float(next(t for t,x,yy in items if x==70 and abs(yy-y-16)<.02))
            levels[label]=value
        a.entry['inputs']['visible_SVG_energy_labels']=levels
        a.result('uncatalysed Ea','uncatalysed_peak-reactants',levels['uncatalysed']-levels['reactants'],'kJ mol^-1')
        a.result('catalysed Ea','catalysed_peak-reactants',levels['catalysed']-levels['reactants'],'kJ mol^-1')
        a.result('reaction enthalpy','products-reactants',levels['products']-levels['reactants'],'kJ mol^-1')
        a.require('unchanged')
    for i in range(49,53):
        a.begin(i,'ahl','Experimental rate ratios determine integer order; k dimensions independently checked against overall order. Overall balanced equation alone is insufficient.')
        table=rows(a,2);(c1,r1),(c2,r2)=table[:2]
        order=round(math.log(r2/r1)/math.log(c2/c1));k=r1/c1**order
        assert all(abs(rate-k*c**order)<1e-10 for c,rate in table)
        a.require('order is '+str(order));a.result('rate constant','first_rate/first_concentration**order',k)
        a.require({0:r'mol\,dm^{-3}\,s^{-1}',1:r's^{-1}',2:r'dm^3\,mol^{-1}\,s^{-1}'}[order])
    for i in range(53,57):
        a.begin(i,'ahl','Each controlled concentration change isolates its order; k units follow total order and new rate uses both concentration powers.')
        table=rows(a,3);A,B,r=table[0]
        m=round(math.log(table[1][2]/r)/math.log(table[1][0]/A));n=round(math.log(table[2][2]/r)/math.log(table[2][1]/B));k=r/(A**m*B**n)
        new=take(a,'new_concentration',r'concentrations are ('+N+')')
        a.require('A: order '+str(m));a.require('B: order '+str(n))
        a.result('rate constant','r/(A**m*B**n)',k)
        a.result('new rate','k*new**(m+n)',k*new**(m+n),'mol dm^-3 s^-1')
        a.require(r'dm^3\,mol^{-1}\,s^{-1}' if m+n==2 else r'dm^6\,mol^{-2}\,s^{-1}')
    mechanism={57:(r'A+2B\to P',r'k[\mathrm A][\mathrm B]'),58:(r'A+B\to P',r'kK[\mathrm A][\mathrm B]'),59:(r'A+2B\to P',r'kK[\mathrm A][\mathrm B]^2'),60:(r'2A\to P',r'kK[\mathrm A]^2')}
    for i,(overall,rate) in mechanism.items():
        a.begin(i,'ahl','Abstract particle steps are explicitly elementary. Cancel intermediate I, use slow-step molecularity, and substitute supplied pre-equilibrium relation where needed.')
        a.require('I is formed');a.require(overall);a.require(rate)
    for i in range(61,65):
        a.begin(i,'ahl','Arrhenius two-temperature derivation uses natural logarithm and absolute kelvin; A frequency/orientation interpretation is R2.2.13.')
        (T1,k1),(T2,k2)=rows(a,2);R=take(a,'R',r'Use \$('+N+')')
        Ea=R*math.log(k2/k1)/(1/T1-1/T2)/1000
        a.result('activation energy','R*ln(k2/k1)/(1/T1-1/T2)/1000',Ea,'kJ mol^-1');a.require('orientation')
    for i,reason,fragment in [(65,'Dynamic equilibrium has equal continuing forward/reverse rates.','Equal rates'),(66,'Equilibrium concentrations remain constant, not necessarily equal.','not equal'),(67,'Closure retains reacting species and permits stable composition.','balance'),(68,'Catalyst leaves K and composition unchanged at fixed temperature.','without changing')]:
        a.begin(i,'sl',reason);a.require(fragment)
    expressions={69:r'\frac{[\mathrm{NH_3}]^2}{[\mathrm{N_2}][\mathrm{H_2}]^3}',70:r'\frac{[\mathrm{HI}]^2}{[\mathrm{H_2}][\mathrm{I_2}]}',71:r'\frac{[\mathrm{SO_3}]^2}{[\mathrm{SO_2}]^2[\mathrm{O_2}]}',72:r'\frac{[\mathrm{PCl_3}][\mathrm{Cl_2}]}{[\mathrm{PCl_5}]}' }
    for i,expression in expressions.items():
        a.begin(i,'sl','Homogeneous equilibrium expression is products over reactants with each balanced coefficient as exponent.');a.require(expression)
    for i in range(73,77):
        a.begin(i,'sl','Reversed equation at unchanged temperature has reciprocal K.')
        K=take(a,'forward_K',r'constant is ('+N+')')
        a.result('reverse K','1/forward_K',1/K)
    for i,pressure in [(77,'towards products'),(78,'towards products'),(79,'neither way'),(80,'towards reactants')]:
        a.begin(i,'sl','Compression favours smaller gas amount; temperature favours endothermic direction; catalyst does not alter equilibrium composition.')
        H=take(a,'forward_enthalpy',r'change \$('+N+')')
        a.require(pressure);a.require('constant decreases' if H<0 else 'constant increases');a.require('no change in equilibrium composition')
    for i in range(81,85):
        a.begin(i,'ahl','Q=[HI]^2/([H2][I2]); comparing Q with K determines net initial direction.')
        K=take(a,'K',r'constant is ('+N+')');h2,i2,hi=vals(a,'mol')[:3];Q=hi**2/(h2*i2)
        a.result('reaction quotient','HI**2/(H2*I2)',Q);a.require('forward reaction' if Q<K else 'reverse reaction')
    for i in range(85,89):
        a.begin(i,'ahl','A↔B concentration conservation gives A=c0/(1+K), B=K*c0/(1+K); no quadratic needed.')
        c=take(a,'initial_concentration',r'concentration \$('+N+')');K=take(a,'K',r'=\$ ('+N+')')
        A=c/(1+K);B=c-A
        a.result('A equilibrium','c0/(1+K)',A,'mol dm^-3');a.result('B equilibrium','c0*K/(1+K)',B,'mol dm^-3');a.result('K recheck','B/A',B/A)
    for i in range(89,93):
        a.begin(i,'ahl','Dissociation gives equal products x; small-K estimate sqrt(K*c0), checked fractional depletion well below5%. Numerical concentration convention is explicit.')
        c=take(a,'initial_concentration',r'concentration \$('+N+')');K=take(a,'K',r'constant is \$('+N+')');x=math.sqrt(c*K)
        a.result('each product concentration','sqrt(c0*K)',x,'mol dm^-3');a.result('percentage consumed','x/c0*100',x/c*100,'%')
        assert x/c<.05
        a.equation('sulfuryl chloride dissociation',[(1,'SO2Cl2',0)],[(1,'SO2',0),(1,'Cl2',0)])
    for i in range(93,97):
        a.begin(i,'ahl','K-temperature trend determines enthalpy sign; ΔG°=-RT lnK at300K; actual direction still depends on Q.')
        (T1,K1),(T2,K2)=rows(a,2);R=take(a,'R',r'Use \$('+N+')')
        a.result('standard Gibbs energy','-R*T1*ln(K1)/1000',-R*T1*math.log(K1)/1000,'kJ mol^-1')
        a.require('exothermic' if K2<K1 else 'endothermic');a.require('reaction quotient')
