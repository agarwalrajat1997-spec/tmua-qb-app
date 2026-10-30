"""Independent chemistry models for R1, using only displayed JSON prompts."""
import math
import re
from audit_reactivity12 import NUMBER as N, clean, take, quantities


def vals(a, unit):
    result=[]
    for j,(value,evidence) in enumerate(quantities(a,unit)):
        result.append(a.given(unit+'_'+str(j),value,evidence))
    return result


def review(a):
    for i in range(1,5):
        a.begin(i,'sl','Heat gained is positive; mcΔT and J-to-kJ conversion, shared calorimetry.')
        m=take(a,'solution_g',r'contains \$('+N+')')
        dt=take(a,'rise_K',r'increases by \$('+N+')')
        c=take(a,'c_J_g_K',r'capacity as \$('+N+')')
        a.result('heat','m*c*ΔT/1000',m*c*dt/1000,'kJ')
    for i in range(5,9):
        a.begin(i,'sl','Equal acid/base moles; total solution mass includes both volumes; reaction heat has opposite sign.')
        vol=take(a,'each_volume_cm3',r'each \$('+N+')')
        c=take(a,'molar_concentration',r'concentration \$('+N+')')
        dt=take(a,'rise_K',r'increase of \$('+N+')')
        rho=take(a,'density',r'density \$('+N+')')
        heatcap=take(a,'specific_heat',r'capacity \$('+N+')')
        q=2*vol*rho*heatcap*dt; n=vol*c/1000
        a.result('solution heat','2*V*rho*c*ΔT',q,'J')
        a.result('water amount','V*concentration/1000',n,'mol')
        a.result('reaction enthalpy','-q/n/1000',-q/n/1000,'kJ mol^-1')
        a.require('reaction loses')
    for i in range(9,13):
        a.begin(i,'sl','Experimental combustion calorimetry is shared; ignored copper heat makes the measured enthalpy less negative.')
        fuel=take(a,'fuel_g',r'trial, \$('+N+')')
        M=take(a,'molar_mass',r'molar mass \$('+N+')')
        water=take(a,'water_g',r'The \$('+N+')')
        dt=take(a,'rise_K',r'warms by \$('+N+')')
        c=take(a,'specific_heat',r'Use \$('+N+')')
        q=water*c*dt; n=fuel/M
        a.result('water heat','water*c*ΔT',q,'J')
        a.result('fuel amount','fuel/M',n,'mol')
        a.result('combustion enthalpy','-q/n/1000',-q/n/1000,'kJ mol^-1')
        a.require('less negative')
    for i in range(13,17):
        a.begin(i,'sl','Backward extrapolation of a specified linear cooling trend; stated limitation of unchanged heat-loss behaviour.')
        initial=take(a,'initial_C',r'both were at ('+N+')')
        m=take(a,'solution_g',r'mass is \$('+N+')')
        n=take(a,'amount_mol',r'; \$('+N+')')
        c=take(a,'specific_heat',r'Use \$('+N+')')
        rows=[(float(x),float(y)) for x,y in re.findall(r'\|\s*('+N+r')\s*\|\s*('+N+r')\s*\|',a.prompt)]
        for j,row in enumerate(rows): a.entry['inputs']['time_temperature_'+str(j)]=list(row)
        slope=(rows[-1][1]-rows[0][1])/(rows[-1][0]-rows[0][0])
        intercept=rows[0][1]-slope*rows[0][0]; dt=intercept-initial
        assert all(abs(y-(intercept+slope*x))<1e-9 for x,y in rows)
        a.result('cooling slope','(Tlast-Tfirst)/(tlast-tfirst)',slope,'K min^-1')
        a.result('zero-time intercept','Tfirst-slope*tfirst',intercept,'C')
        a.result('corrected rise','intercept-initial',dt,'K')
        a.result('corrected enthalpy','-m*c*rise/n/1000',-m*c*dt/n/1000,'kJ mol^-1')
    for i in range(17,21):
        a.begin(i,'sl','Dissolution cools the solution: qsolution<0, dissolution enthalpy>0; entire solution mass is supplied.')
        M=take(a,'molar_mass',r'molar mass \$('+N+')')
        mass=take(a,'solute_g',r'A \$('+N+')')
        solution=take(a,'solution_g',r'form \$('+N+')')
        dt=take(a,'temperature_fall_K',r'falls by \$('+N+')')
        c=take(a,'specific_heat',r'capacity \$('+N+')')
        q=-solution*c*dt; n=mass/M
        a.result('solution heat','-solution*c*fall',q,'J')
        a.result('dissolved amount','mass/M',n,'mol')
        a.result('dissolution enthalpy','-q/n/1000',-q/n/1000,'kJ mol^-1')
        a.require('positive')
    for i in range(21,25):
        a.begin(i,'sl','Maximum absolute errors add for a difference; exact mass/c/n allow percentage uncertainty propagation from ΔT alone.')
        u=take(a,'single_reading_uncertainty',r'uncertainty ±('+N+')')
        dt=take(a,'rise_K',r'difference is \$('+N+')')
        m=take(a,'solution_g',r'treat the \$('+N+')')
        c=take(a,'specific_heat',r'capacity \$('+N+')')
        n=take(a,'amount_mol',r'amount \$('+N+')')
        H=-m*c*dt/n/1000
        a.result('rise uncertainty','2*u',2*u,'K')
        a.result('percentage uncertainty','100*2*u/ΔT',200*u/dt,'%')
        a.result('enthalpy','-m*c*ΔT/n/1000',H,'kJ mol^-1')
        a.result('absolute enthalpy uncertainty','abs(H)*2*u/ΔT',abs(H)*2*u/dt,'kJ mol^-1')
    for i,X in zip(range(25,29),['F','Cl','Br','I']):
        a.begin(i,'sl','Gas-phase bonds broken minus formed; 1 H-H +1 X-X broken and 2 H-X formed.')
        hh=take(a,'D_HH',r'H-H ('+N+')')
        xx=take(a,'D_XX',X+'-'+X+' ('+N+')')
        hx=take(a,'D_HX','H-'+X+' ('+N+')')
        a.result('bond estimate','D(HH)+D(XX)-2*D(HX)',hh+xx-2*hx,'kJ mol^-1')
        a.equation('H2+X2 -> 2HX',[(1,'H2',0),(1,X+'2',0)],[(2,'H'+X,0)])
    inventories=[('CH4',4,0,0,0,0,2,1,2),('C2H6',6,1,0,0,0,3.5,2,3),('C2H4',4,0,1,0,0,3,2,2),('CH3OH',3,0,0,1,1,1.5,1,2)]
    for i,(formula,ch,cc,cc2,co,oh,o2,co2,h2o) in zip(range(29,33),inventories):
        a.begin(i,'sl','Independent molecular bond inventory; O2 coefficient and two O-H bonds per water included; all species gaseous.')
        bond={name:take(a,name,pattern+' ('+N+')') for name,pattern in [('CH','C-H'),('CC','C-C'),('CC2','C=C'),('CO','C-O'),('OH','O-H'),('OO','O=O'),('CO2','carbon dioxide')]}
        broken=ch*bond['CH']+cc*bond['CC']+cc2*bond['CC2']+co*bond['CO']+oh*bond['OH']+o2*bond['OO']
        formed=2*co2*bond['CO2']+2*h2o*bond['OH']
        a.result('broken bonds','independent molecule-specific reactant bond inventory',broken,'kJ mol^-1')
        a.result('formed bonds','2*n(CO2)*D(CO)+2*n(H2O)*D(OH)',formed,'kJ mol^-1')
        a.result('enthalpy','broken-formed',broken-formed,'kJ mol^-1')
        a.equation('complete gas-phase combustion',[(1,formula,0),(o2,'O2',0)],[(co2,'CO2',0),(h2o,'H2O',0)])
    for i in range(33,37):
        a.begin(i,'sl','Hess manipulation with state consistency; reverse/scale equations and their enthalpies together.')
        energies=vals(a,'kJ')
        E,F=energies[:2]
        result={33:E+F,34:E-F,35:2*E-F,36:E+F}[i]
        a.result('target enthalpy',{33:'E+F',34:'E-F',35:'2E-F',36:'E+F'}[i],result,'kJ mol^-1')
        a.require('state function')
    for i in range(37,41):
        a.begin(i,'ahl','Standard formation-data sum is HL; products minus reactants, O2 standard formation zero, liquid water state explicit.')
        carbon=take(a,'CO2_coefficient',r'form ('+N+') mol')
        water=take(a,'H2O_coefficient',r'and ('+N+') mol')
        fuel=take(a,'fuel_formation',r'fuel ('+N+')')
        cf=take(a,'CO2_formation',r'carbon dioxide ('+N+')')
        wf=take(a,'water_formation',r'liquid water ('+N+')')
        mass=take(a,'burnt_g',r'burning \$('+N+')')
        M=take(a,'molar_mass',r'molar mass \$('+N+')')
        H=carbon*cf+water*wf-fuel
        a.result('combustion enthalpy','carbon*CO2_f+water*H2O_f-fuel_f',H,'kJ mol^-1')
        a.result('heat released','-H*mass/M',-H*mass/M,'kJ')
    for i in range(41,45):
        a.begin(i,'ahl','Combustion-data cycle is HL; target hydrogenation sums alkene and H2 combustion minus alkane combustion.')
        E,F,H=vals(a,'kJ')[:3]
        a.result('hydrogenation enthalpy','alkene_c+H2_c-alkane_c',E+H-F,'kJ mol^-1')
        a.require('identical final states')
    for i,cl in zip(range(45,49),[1,1,2,2]):
        a.begin(i,'ahl','Born-Haber calculation HL; lattice formation convention explicit, correct chlorine and electron-affinity stoichiometry.')
        atom=take(a,'metal_atomization',r'Atomization of metal \| ('+N+')')
        ion=take(a,'metal_ionization_total',r'metal atoms \| ('+N+')')
        diss=take(a,'Cl2_bond',r'bond enthalpy \| ('+N+')')
        ea=take(a,'Cl_electron_affinity',r'Cl atoms \| ('+N+')')
        form=take(a,'solid_formation',r'Formation of solid chloride \| ('+N+')')
        lattice=form-atom-ion-cl*diss/2-cl*ea
        a.result('chlorine atomization','Cl_count*D(Cl2)/2',cl*diss/2,'kJ mol^-1')
        a.result('electron affinity term','Cl_count*EA(Cl)',cl*ea,'kJ mol^-1')
        a.result('lattice formation','formation-atomization-ionization-chlorine-EA',lattice,'kJ mol^-1')
        a.result('lattice dissociation','-lattice_formation',-lattice,'kJ mol^-1')
        a.require('releasing energy')
    for i in range(49,53):
        a.begin(i,'sl','Energy per gram is a fuel comparison, shared SL/HL; positive released-energy magnitude.')
        M=take(a,'molar_mass',r'molar mass \$('+N+')')
        H=vals(a,'kJ')[0]
        a.result('specific energy','abs(combustion enthalpy)/M',abs(H)/M,'kJ g^-1')
    for i in range(53,57):
        a.begin(i,'sl','CO2 per MJ uses fuel stoichiometry and energy; life-cycle comparison distinguished from point-of-use emissions.')
        H=vals(a,'kJ')[0]
        carbon=take(a,'CO2_coefficient',r'forms ('+N+') mol')
        M=take(a,'CO2_molar_mass',r'as \$('+N+')')
        a.result('CO2 emission intensity','carbon*M*1000/H',carbon*M*1000/H,'g MJ^-1')
        a.require('life-cycle')
    for i in range(57,61):
        a.begin(i,'sl','Hydrogen fuel cells are explicitly shared; acidic oxidation/reduction half-equations balanced; efficiency multiplies available energy.')
        n=take(a,'H2_amount',r'consumes \$('+N+')')
        H=vals(a,'kJ')[0]
        efficiency=take(a,'efficiency_percent',r'and ('+N+')%')
        released=abs(H)*n
        a.result('chemical energy','abs(H)*n',released,'kJ')
        a.result('electrical energy','released*efficiency/100',released*efficiency/100,'kJ')
        a.equation('H2 oxidation',[(1,'H2',0)],[(2,'H',1),(2,'e',-1)])
        a.equation('O2 reduction',[(1,'O2',0),(4,'H',1),(4,'e',-1)],[(2,'H2O',0)])
    for i in range(61,65):
        a.begin(i,'sl','Methanol fuel-cell equations in acidic medium are shared; six electrons per methanol; CO2 quantity tied to carbon balance.')
        m=take(a,'methanol_g',r'consumes \$('+N+')')
        M=take(a,'molar_mass',r'molar mass \$('+N+')')
        a.result('CO2 amount','methanol mass/M',m/M,'mol')
        a.equation('methanol oxidation',[(1,'CH3OH',0),(1,'H2O',0)],[(1,'CO2',0),(6,'H',1),(6,'e',-1)])
        a.equation('overall methanol fuel cell',[(1,'CH3OH',0),(1.5,'O2',0)],[(1,'CO2',0),(2,'H2O',0)])
    qualitative={65:('Life-cycle biofuel emissions invalidate unconditional carbon-neutral claim.','Life-cycle'),66:('Hydrogen manufacturing requires external energy; energy carrier explanation.','manufacture'),67:('Limited oxygen gives incomplete combustion and potentially CO; shared fuel effects.','Limited oxygen'),68:('A fixed-volume tank demands volumetric, not solely gravimetric, energy comparison.','volume')}
    for i,(notes,required) in qualitative.items():
        a.begin(i,'sl',notes); a.require(required)
    for i in range(69,73):
        a.begin(i,'sl','Volumetric energy follows density*energy_per_mole/molar_mass; choose larger density of energy and multiply tank volume.')
        rows=re.findall(r'\|\s*([^|]+?)\s*\|\s*('+N+r')\s*\|\s*('+N+r')\s*\|\s*('+N+r')\s*\|',a.prompt)
        energies=[]
        for name,rho,M,H in rows:
            rho,M,H=map(float,(rho,M,H)); a.entry['inputs'][name]={'density':rho,'M':M,'energy':H}
            energies.append(rho*H/M); a.result(name+' volumetric energy','density*energy/M',energies[-1],'kJ cm^-3')
        V=take(a,'tank_volume',r'full ('+N+') cubic')
        a.result('larger tank energy','max(volumetric energies)*V',max(energies)*V,'kJ')
        a.require(rows[energies.index(max(energies))][0].strip())
    for i,notes,fragment in [(73,'Vaporization increases accessible configurations.','Gas'),(74,'Dimerization reduces gas particle amount; qualitative entropy prediction.','Two moles'),(75,'Isothermal expansion raises ideal-gas entropy through accessible volume.','microstates'),(76,'Positive total entropy is the spontaneous criterion; kinetic rate remains separate.','positive')]:
        a.begin(i,'ahl',notes); a.require(fragment)
    coeffs={77:[-1,-3,2],78:[-2,1],79:[-1,1,1],80:[-2,-1,2]}
    for i in range(77,81):
        a.begin(i,'ahl','Independent stoichiometric entropy sum; standard elemental entropy is not a zero-formation convention.')
        rows=re.findall(r'\|\s*([^|]+?)\s*\|\s*('+N+r')\s*\|',a.prompt)
        entropy=[float(v) for _,v in rows]
        a.entry['inputs']['standard_entropies']={name.strip():float(v) for name,v in rows}
        a.result('entropy change','sum(stoichiometric signed coefficient*S)',sum(c*s for c,s in zip(coeffs[i],entropy)),'J K^-1 mol^-1')
        a.require('zero convention')
    for i in range(81,85):
        a.begin(i,'ahl','ΔG uses entropy converted J to kJ; sign establishes feasible direction and temperature inequalities preserve the entropy sign.')
        H=take(a,'enthalpy_kJ',r'enthalpy change \$('+N+')')
        S=take(a,'entropy_J_K',r'entropy change \$('+N+')')
        T=take(a,'temperature_K',r'examined at \$('+N+')')
        G=H-T*S/1000
        a.result('Gibbs energy','H-T*S/1000',G,'kJ mol^-1')
        a.require('forward direction' if G<0 else 'reverse direction')
        if H*S>0:
            a.result('boundary temperature','1000*H/S',1000*H/S,'K'); a.require('below' if S<0 else 'above')
        else: a.require('all positive temperatures' if H<0 else 'any positive temperature')
    for i in range(85,89):
        a.begin(i,'ahl','Gibbs standard energy determines dimensionless K; convert kJ to J before division by RT.')
        T=take(a,'temperature_K',r'At \$('+N+')')
        G=take(a,'standard_G_kJ',r'change \$('+N+')')
        R=take(a,'R',r'Use \$('+N+')')
        a.result('equilibrium constant','exp(-G*1000/(R*T))',math.exp(-G*1000/(R*T)))
    for i in range(89,93):
        a.begin(i,'ahl','Actual Gibbs direction uses Q; standard Gibbs fixes K independently. Dimensionless Q and K explicitly given.')
        T=take(a,'temperature_K',r'at \$('+N+')')
        G=take(a,'standard_G_kJ',r'change \$('+N+')')
        Q=take(a,'reaction_quotient',r'quotient ('+N+')')
        R=take(a,'R',r'Use \$('+N+')')
        actual=G+R*T*math.log(Q)/1000
        a.result('actual Gibbs energy','Gstandard+R*T*ln(Q)/1000',actual,'kJ mol^-1')
        a.result('equilibrium constant','exp(-Gstandard*1000/(R*T))',math.exp(-G*1000/(R*T)))
        a.require('forward reaction' if actual<0 else 'reverse reaction')
    for i in range(93,97):
        a.begin(i,'ahl','Reservoir entropy =-H/T at stated constant pressure, total entropy and Gibbs sign agree; energies are for a specified extent, not molar.')
        H=take(a,'system_H_kJ',r'enthalpy change as \$('+N+')')
        S=take(a,'system_S_J_K',r'entropy change as \$('+N+')')
        T=take(a,'reservoir_temperature',r'reaction at \$('+N+')')
        reservoir=-H*1000/T; total=reservoir+S; G=H-T*S/1000
        a.result('reservoir entropy','-H*1000/T',reservoir,'J K^-1')
        a.result('total entropy','reservoir+system entropy',total,'J K^-1')
        a.result('system Gibbs energy','-T*total/1000',G,'kJ')
        a.require('forward direction' if total>0 else 'reverse direction')
