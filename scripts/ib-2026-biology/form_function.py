"""Fifty separately authored current-course Biology Form and Function tasks."""
from pathlib import Path
import json, math, re, html, hashlib, collections, statistics
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
Q=[]; AUD=[]
SUB={"B1.1":"Carbohydrates and lipids","B1.2":"Proteins","B2.1":"Membranes and membrane transport","B2.2":"Organelles and compartmentalization","B2.3":"Cell specialization","B3.1":"Gas exchange","B3.2":"Transport","B3.3":"Muscle and motility","B4.1":"Adaptation to environment","B4.2":"Ecological niches"}
GUIDE="https://xmltwo.ibo.org/publications/EAD/2026_EN/GR4/GR4-Biology_EN.pdf"
SPECIMEN="https://www.ibo.org/globalassets/new-structure/programmes/dp/pdfs/biology-hl-sl-specimen-papers-1a-2b-2-en.pdf"

def polish(s):
    s=str(s)
    s=re.sub(r"\b([A-Za-z]{3,})(?=[0-9])",r"\1 ",s)
    s=re.sub(r"\b(At|is|are|a|an|the|Hb)(?=[0-9])",r"\1 ",s)
    s=re.sub(r"\b(at|after|before|by|from|to|and|or|of|in|than|through|over|within|versus|for|sodium|glucose|type|RER|Golgi|approximately|about|Load|State|A|B)(?=[0-9])",r"\1 ",s)
    s=re.sub(r"(?<=\d)(?=(?:min|mmHg|mmol|mol|kPa|g|kg|μm|mm|cm|s|L|N|W|ATP|units)\b)", " ",s)
    s=re.sub(r"(?<=\d)(?=(?:stomata|percentage|points|polypeptide|extra|identical|linear|internal|residues|cycles|times|units|cells)\b)"," ",s)
    s=s.replace("typeII","type II").replace("typeI","type I").replace("TypeII","Type II").replace("TypeI","Type I")
    s=s.replace("ATP-linked3:2","ATP-linked 3:2").replace("pH7.","pH 7.").replace("P50=","P50 = ")
    s=re.sub(r",(?=\S)",", ",s)
    s=re.sub(r";(?=\S)","; ",s)
    return s
def esc(s): return html.escape(str(s))
def text(x,y,s,size=17,anchor="middle"):
    return f'<text x="{x:g}" y="{y:g}" font-family="Arial,sans-serif" font-size="{size}" text-anchor="{anchor}" fill="black">{esc(polish(s))}</text>'
def line(x,y,u,v,width=2,dash=False):
    return f'<line x1="{x:g}" y1="{y:g}" x2="{u:g}" y2="{v:g}" stroke="black" stroke-width="{width:g}"'+(' stroke-dasharray="5 4"' if dash else '')+'/>'
def path(d,width=2,fill="none"):
    return f'<path d="{d}" stroke="black" stroke-width="{width}" fill="{fill}"/>'
def rect(x,y,w,h,rx=0,fill="white"):
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx:g}" fill="{fill}" stroke="black" stroke-width="2"/>'
def ellipse(x,y,rx,ry,fill="white"):
    return f'<ellipse cx="{x:g}" cy="{y:g}" rx="{rx:g}" ry="{ry:g}" fill="{fill}" stroke="black" stroke-width="2"/>'
def arrow(x,y,u,v,dash=False):
    a=math.atan2(v-y,u-x);d=9
    return line(x,y,u,v,dash=dash)+line(u,v,u-d*math.cos(a-.5),v-d*math.sin(a-.5))+line(u,v,u-d*math.cos(a+.5),v-d*math.sin(a+.5))
def svg(title,body):
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 480" role="img" aria-label="'+esc(title)+'"><rect width="800" height="480" fill="white"/>'+text(400,28,title,20)+body+'</svg>'
def plot(title,series,xlim,ylim,xlabel,ylabel,xticks=None,yticks=None):
    X=lambda x:110+600*(x-xlim[0])/(xlim[1]-xlim[0])
    Y=lambda y:365-270*(y-ylim[0])/(ylim[1]-ylim[0])
    b=line(110,365,725,365)+line(110,365,110,85)+text(700,444,xlabel,16,"end")
    b+=f'<text x="25" y="235" transform="rotate(-90 25 235)" text-anchor="middle" font-family="Arial,sans-serif" font-size="16">{esc(ylabel)}</text>'
    for x in xticks or [xlim[0],sum(xlim)/2,xlim[1]]:
        b+=line(X(x),365,X(x),371)+text(X(x),393,f"{x:g}",14)
    for y in yticks or [ylim[0],sum(ylim)/2,ylim[1]]:
        b+=line(104,Y(y),110,Y(y))+text(98,Y(y)+5,f"{y:g}",14,"end")
    patterns=["","7 5","2 5","10 4 2 4"]
    for j,(label,points) in enumerate(series):
        ps=" ".join(f"{X(x):.3f},{Y(y):.3f}" for x,y in points)
        b+='<polyline points="'+ps+'" fill="none" stroke="black" stroke-width="'+str(2+j*.4)+'"'+(' stroke-dasharray="'+patterns[j%4]+'"' if patterns[j%4] else '')+'/>'
        for x,y in points:
            b+=ellipse(X(x),Y(y),3,3,"black" if j%2==0 else "white")
        if label:
            legend=line(125+j*185,60,153+j*185,60,dash=bool(patterns[j%4]))
            if patterns[j%4]:legend=legend.replace("5 4",patterns[j%4])
            b+=legend+text(160+j*185,65,label,14,"start")
    return svg(title,b)
def bars(title,labels,values,ylabel,maximum=None):
    maximum=maximum or max(values)*1.2
    b=line(110,365,725,365)+line(110,365,110,85)
    b+=f'<text x="25" y="235" transform="rotate(-90 25 235)" text-anchor="middle" font-family="Arial,sans-serif" font-size="16">{esc(ylabel)}</text>'
    for y in [0,maximum/2,maximum]:
        yy=365-270*y/maximum;b+=line(104,yy,110,yy)+text(98,yy+5,f"{y:g}",14,"end")
    for i,(lab,val) in enumerate(zip(labels,values)):
        x=135+i*565/len(values);w=min(85,400/len(values));h=270*val/maximum
        b+=rect(x,365-h,w,h,fill="#eeeeee")+text(x+w/2,355-h,f"{val:g}",15)
        for k,part in enumerate(lab.split("|")):b+=text(x+w/2,397+20*k,part,14)
    return svg(title,b)
def membrane(title,inside="Cytoplasm",outside="Extracellular fluid",protein=True):
    b=text(400,100,outside,19)+text(400,365,inside,19)
    for x in range(85,725,32):
        if protein and 340<x<460:continue
        b+=ellipse(x,190,11,11)+line(x-4,202,x-4,228)+line(x+4,202,x+4,228)
        b+=ellipse(x,280,11,11)+line(x-4,268,x-4,242)+line(x+4,268,x+4,242)
    if protein:b+=rect(345,165,110,142,22,fill="#eeeeee")+text(400,241,"P",24)
    return svg(title,b)
def cubes():
    b=rect(95,145,145,145)+path("M240 145L285 110L140 110L95 145M240 290L285 255L285 110")+text(185,345,"One cube: side 40 μm")
    for i in range(2):
        for j in range(2):b+=rect(450+i*75,145+j*75,75,75)
    b+=text(530,345,"Eight cubes: each side 20 μm")+text(530,377,"Two layers of four; total volume unchanged.",15)
    return svg("A division model for exchange geometry",b)
def checks(name,actual,expected):
    if isinstance(expected,(int,float)) and not isinstance(expected,bool):
        assert math.isclose(actual,expected,rel_tol=1e-7,abs_tol=1e-12 if expected==0 else abs(expected)*1e-8),(name,actual,expected)
    else:assert actual==expected,(name,actual,expected)
    return {"check":name,"calculated":actual,"expected":expected,"status":"passed"}
def truth(name,condition):
    assert condition,name
    return {"check":name,"status":"passed"}
def M(s):return {"code":"M1","text":s}
def A(s):return {"code":"A1","text":s}
def R(s):return {"code":"R1","text":s}
def P(prompt,*steps):return (prompt,list(steps))
def add(n,title,code,stem,parts,diagram,evidence,scope,caption=None):
    labels="abcdefgh"; ps=[];ms=[]
    for lab,(prompt,steps) in zip(labels,parts):
        ps.append({"label":lab,"prompt":prompt,"marks":len(steps)})
        ms.append({"part":lab,"steps":steps})
    q={"id":f"ib-bio-b-{n}","number":n,"source":{"document":"Independent syllabus-authored practice","question":n},
       "subject":"biology","topicId":"form-function","collectionId":"biology-form-function","syllabusCode":code,"subtopic":SUB[code],
       "level":"sl" if n<=720 else "ahl","difficulty":"hard","calculator":True,"questionType":"data-based","title":title,
       "stem":stem+" All measurements in this question are constructed for this practice task; diagrams are original schematics, not micrographs.",
       "parts":ps,"markScheme":ms,"marks":sum(p["marks"] for p in ps),"diagramSvg":diagram,
       "diagramCaption":caption or "Original schematic or constructed dataset. Use the stated units and assumptions.",
       "answerSummary":" ".join(s["text"] for g in ms for s in g["steps"] if s["code"]=="A1"),
       "status":"published","verification":{"method":"Author biological review and executable per-question numerical/scientific consistency checks; independent review is a separate release gate.",
       "notes":scope+" These are original instructional M/A/R awards, not official IB markscheme notation. Accept scientifically equivalent explanations and valid error-carried-forward calculations."}}
    Q.append(q);AUD.append({"id":q["id"],"status":"passed","scope":scope,"checks":evidence})

# Shared SL/HL questions. B1.1, B4.1 and B4.2 have no AHL additions.
chain=svg("Two six-unit glucose-based chains",text(400,73,"Each hexagon is one glucose residue; each joining line is one glycosidic link.",16)+
    "".join(path("M"+f"{100+100*i} 175l20 -30h35l20 30l-20 30h-35z") for i in range(6))+
    "".join(line(175+100*i,175,200+100*i,175) for i in range(5))+
    text(400,247,"Chain P: the same residue orientation repeats.",16)+
    "".join(path("M"+f"{100+100*i} 330l20 -30h35l20 30l-20 30h-35z")+text(137+100*i,336,"↑" if i%2==0 else "↓",22) for i in range(6))+
    "".join(line(175+100*i,330,200+100*i,330) for i in range(5))+text(400,414,"Chain Q: alternate glucose residues are reversed.",16))
add(701,"Hydrolysis changes particle number without creating glucose carbon","B1.1",
    "P and Q are unbranched glucose-based chains of six residues each. P has alpha-glucose linkages and Q has beta-glucose linkages. An enzyme hydrolyses P but leaves Q unchanged. A sample contains 10.0 μmol of P chains; assume complete hydrolysis to glucose and ignore chain ends when discussing the shapes of long chains.",
    [P("Calculate the amount of glycosidic links hydrolysed, water consumed and glucose formed in the sample.",
       M("Each six-residue open chain contains five glycosidic links; hydrolysis consumes one water per link."),
       A("50.0 μmol links are hydrolysed and 50.0 μmol water consumed; 60.0 μmol glucose forms.")),
     P("Explain enzyme selectivity and relate the long-chain versions of P and Q to storage and structural roles.",
       R("Different glucose/linkage orientation gives a different three-dimensional substrate shape; an enzyme that fits P need not fit Q."),
       R("Alpha-glucose polymers can form compact storage structures, whereas beta-glucose cellulose chains are straight and can associate into strong fibres."),
       R("Do not claim that this enzyme's failure proves Q can never be hydrolysed; another enzyme can be specific to Q.")),
     P("Compare the number of dissolved solute particles before and after hydrolysis, and explain one advantage of storing glucose in large insoluble polymers.",
       M("One chain becomes six separate glucose molecules; solute particle amount changes from 10.0 to 60.0 μmol."),
       A("Particle number is sixfold, an increase of 500%, under the stated dissolved-particle model."),
       R("Large insoluble storage polymers contribute much less to osmotic effects than the same glucose inventory stored as free monomers."))],
    chain,[checks("chain bonds",6-1,5),checks("water μmol",10*5,50),checks("glucose μmol",10*6,60),checks("particle increase percent",(6-1)*100,500)],
    "B1.1 shared: alpha/beta polymers, hydrolysis and storage; no AHL protein-folding detail required.")
add(702,"A kink in a fatty-acid chain changes the melting behaviour of a fat","B1.1",
    "Fats X and Y contain triglycerides with fatty-acid chains of equal carbon length. X contains many cis double bonds; Y contains mainly saturated chains. The plotted values are fractions of each bulk fat that are liquid after equilibration. A purified sample contains 2.00 mmol of a triglyceride with three identical fatty-acid chains.",
    [P("Use the graph to compare the state of the fats at 20 °C and explain the difference using chain structure.",
       A("At 20 °C, X is 80% liquid and Y is 15% liquid: a 65 percentage-point difference."),
       R("Cis double bonds produce kinks, reducing close packing between chains; saturated chains pack more closely."),
       R("Less energy is needed to disrupt interactions between the less closely packed unsaturated chains, so X melts at lower temperatures.")),
     P("State the products and amounts after complete hydrolysis of the purified sample, and explain why a triglyceride is not a polymer.",
       M("One triglyceride hydrolyses with three water molecules to one glycerol and three fatty acids."),
       A("2.00 mmol glycerol and 6.00 mmol fatty acid form; 6.00 mmol water is consumed."),
       R("It is assembled from glycerol and three fatty acids, not a long chain of a repeated identical monomer.")),
     P("Evaluate the claim that a more unsaturated fat always provides more insulation.",
       R("Melting behaviour alone does not determine an adipose layer's thickness or thermal resistance."),
       R("Compare equal thickness/mass and control temperature and other tissue properties; the data establish a melting difference, not a universal insulation ranking."))],
    plot("Equilibrated liquid fraction of two fats",[("X",[(0,20),(10,50),(20,80),(30,100),(40,100)]),("Y",[(0,0),(10,5),(20,15),(30,50),(40,90)])],(0,40),(0,100),"Temperature / °C","Liquid fraction / %"),
    [checks("liquid percentage points",80-15,65),checks("fatty acid mmol",2*3,6),checks("glycerol mmol",2,2)],
    "B1.1 shared lipid saturation/melting and hydrolysis; no membrane-fluidity AHL content assessed.")
add(703,"Terminal carbohydrates provide a recognition signal","B1.1",
    "Fluorescent anti-A binds only the A terminal carbohydrate; anti-B binds only the B terminal carbohydrate. Equal numbers of red blood cells from sample S give signals of 90 and 80 arbitrary units; background is 5 units. Glycosidase G removes the terminal A structure without removing B. After G treatment the signals are 6 and 78. A separate protease removes the protein anchors of these particular surface molecules, releasing both carbohydrate labels.",
    [P("Deduce the ABO carbohydrate pattern of S and calculate the percentage decrease in background-corrected anti-A signal after G.",
       A("S displays both A and B terminal carbohydrates, consistent with AB cells."),
       M("Before G: 90−5=85; after G: 6−5=1; percentage decrease=(85−1)/85×100."),
       A("The background-corrected anti-A signal decreases by 98.8%.")),
     P("Explain how these results connect carbohydrate diversity with recognition, distinguishing the effects of G and protease.",
       R("Different terminal sugar arrangements give specific binding sites, so G selectively removes the anti-A recognition structure."),
       R("Protease cuts the protein component rather than hydrolysing the carbohydrate itself; loss of both labels supports their attachment to these protein anchors."),
       R("The result concerns the tested glycoproteins and does not imply every membrane carbohydrate is attached to a protein rather than a lipid.")),
     P("Design a control that distinguishes enzyme specificity from general damage or unequal cell recovery.",
       R("Use an identical mock-treated sample with inactive G or buffer, equal incubation and equal counted cell numbers."),
       R("Check membrane integrity and anti-B retention; a general loss of cells or membrane would tend to reduce both signals, unlike the observed selective anti-A loss."))],
    bars("Recognition before and after glycosidase G",["anti-A|before","anti-A|after","anti-B|before","anti-B|after"],[90,6,80,78],"Fluorescence / arbitrary units",100),
    [checks("corrected initial A",90-5,85),checks("corrected final A",6-5,1),checks("corrected A loss percent",(85-1)/85*100,98.8235294118)],
    "B1.1 shared ABO glycoprotein recognition; binding specificity and enzyme actions explicitly supplied.")
add(704,"A fuel reserve must meet an energy target within a mass budget","B1.1",
    "A model migratory bird needs 510 kJ from its stored organic fuel during a flight. Use 17.0 kJ g−1 for carbohydrate and 37.0 kJ g−1 for lipid; these are supplied usable-energy values. Compare dry fuel masses only. The diagram gives the usable energy carried by several dry reserve masses.",
    [P("Calculate the dry mass needed if all fuel is carbohydrate or all is lipid, and the percentage mass saving from lipid.",
       M("Required mass=510 divided by usable energy per gram."),
       A("Carbohydrate: 30.0 g; lipid: 13.8 g from an unrounded 13.7838 g."),
       A("Mass saving=(30.0−13.7838)/30.0×100=54.1%.")),
     P("Explain two properties that make triglycerides suitable long-term reserves without claiming they are the only useful fuel.",
       R("They yield more usable energy per unit dry mass in the supplied comparison, reducing the carried mass."),
       R("Their hydrophobic insolubility allows storage without acting as many dissolved osmotic particles; adipose also contributes insulation.")),
     P("Evaluate a prediction that the bird therefore loses exactly 13.8 g of total body mass on the flight.",
       R("Dry fuel use is not total body-mass change; water production/loss and other fuel use can change mass."),
       R("Actual energy demand, conversion efficiency and reserve accessibility vary; the arithmetic is conditional on the stated model."))],
    plot("Energy available from dry reserves",[("Carbohydrate",[(0,0),(10,170),(20,340),(30,510)]),("Lipid",[(0,0),(10,370),(20,740),(30,1110)])],(0,30),(0,1200),"Dry reserve mass / g","Usable energy / kJ"),
    [checks("carbohydrate g",510/17,30),checks("lipid g",510/37,13.7837837838),checks("mass saving percent",(1-17/37)*100,54.0540540541)],
    "B1.1 shared triglyceride energy storage/insulation and hydrophobicity; supplied model is not a nutritional recommendation.")
add(705,"More total protein does not guarantee an adequate amino-acid supply","B1.2",
    "In a constructed dietary-protein model, a 10.0 g portion of food P releases 20 mg of essential amino acid E and 80 mg of essential amino acid F; 10.0 g of Q releases 80 mg E and 20 mg F. All other requirements are met. The daily requirement in this model is at least 60 mg of each. Assume complete digestion and additive amounts; no real foods or named amino acids are implied.",
    [P("Determine whether 12.0 g of P alone meets both requirements and compare it with 6.00 g P plus 6.00 g Q.",
       M("Scale each 10 g amino-acid supply by the food mass/10."),
       A("12.0 g P provides 24 mg E and 96 mg F, so E is insufficient."),
       A("6.00 g of each provides 60 mg E and 60 mg F, meeting both requirements with the same total food mass.")),
     P("Explain why an essential amino acid can limit use of the other amino acids for a particular polypeptide.",
       R("Essential amino acids cannot be synthesized in sufficient amounts by the organism and must be supplied by food."),
       R("A polypeptide requires the amino acids in its specified sequence; surplus F cannot simply replace a required E.")),
     P("Outline digestion of a three-amino-acid peptide into free amino acids and evaluate the model's use for real diets.",
       A("Hydrolysis breaks two peptide bonds and consumes two water molecules to give three amino acids."),
       R("Real foods differ in digestibility and contain many amino acids/nutrients; complete digestion and only two limiting requirements are simplifications."))],
    bars("Amino acids released per 10 g food",["P: E","P: F","Q: E","Q: F"],[20,80,80,20],"Amino-acid amount / mg",100),
    [checks("P12 E mg",12/10*20,24),checks("P12 F mg",12/10*80,96),checks("mixture E mg",.6*20+.6*80,60),checks("mixture F mg",.6*80+.6*20,60),checks("tripeptide links",3-1,2)],
    "B1.2 shared essential amino acids, sequence specificity and peptide hydrolysis; no named essential amino acid recall.")
add(706,"Loss and recovery of protein function need not mean chain cleavage","B1.2",
    "One purified protein is measured under four treatments. Untreated activity is 100 units. Activity after heating is 20, and after cooling the heated sample is 30. A separate pH 2 treatment gives 10 units, rising to 80 after neutralization. Peptide-chain length is unchanged in every sample. Assays are performed at the same final substrate concentration and temperature except where the stated treatment is being tested.",
    [P("Compare functional recovery after cooling and after neutralization using percentage-point changes relative to untreated activity.",
       A("Cooling raises activity from 20% to 30%, a 10 percentage-point recovery."),
       A("Neutralization raises activity from 10% to 80%, a 70 percentage-point recovery; it remains 20 percentage points below untreated activity.")),
     P("Explain why denaturation is a better interpretation than complete hydrolysis, while distinguishing loss of function from certain proof of a particular shape.",
       R("Temperature or pH can alter the protein's conformation and hence the shape needed for its function."),
       R("Complete hydrolysis would cleave peptide chains into much smaller units, inconsistent with the unchanged measured chain length."),
       R("Activity is indirect evidence; an independent structural measurement would test the proposed conformation change.")),
     P("Evaluate the claims that denaturation is always irreversible and that all function returns whenever the original conditions are restored.",
       R("The pH-treated sample's substantial recovery shows that the effect can be partly reversible."),
       R("Neither sample fully recovers, so restoring conditions is not a guarantee of complete functional restoration."))],
    bars("Activity after treatment and attempted recovery",["Untreated","Heated","Cooled","pH 2","Neutralized"],[100,20,30,10,80],"Activity / units",120),
    [checks("cool recovery points",30-20,10),checks("neutralization recovery points",80-10,70),checks("remaining loss",100-80,20)],
    "B1.2 shared denaturation and primary chain integrity; detailed R-group interactions are not required.")
add(707,"A selective barrier can admit oxygen while excluding an ion","B2.1",
    "Equal-area artificial phospholipid bilayers separate two stirred solutions. Oxygen moves into the initially oxygen-free receiver. In a second system the transported species is an ion Z+. Bilayers contain no proteins unless a selective Z+ channel is added. The graph shows initial rates; the electrochemical gradient favours inward movement of Z+ when the channel is present.",
    [P("Use the graph to distinguish simple diffusion from protein-facilitated diffusion.",
       A("Oxygen crosses the protein-free bilayer, with rate increasing from 2 to 8 units as the concentration difference increases fourfold."),
       R("Small nonpolar oxygen can pass through the bilayer's hydrophobic region; charged Z+ is strongly restricted without a protein pathway."),
       R("An open Z+ channel provides a selective hydrophilic route down the supplied electrochemical gradient.")),
     P("Predict the effect of removing ATP from the external solutions and explain what would change if the gradient reversed.",
       R("Neither simple diffusion nor an already-open passive channel directly uses ATP, so ATP removal alone need not stop these initial fluxes."),
       R("Reversing the relevant gradient reverses net passive movement; a channel is not an ATP-powered one-way pump.")),
     P("Suggest two controls needed before assigning the rate difference solely to the channel.",
       R("Keep bilayer area, temperature, stirring and concentration/electrical gradients the same."),
       R("Use otherwise identical bilayers and check for membrane leaks; a nonselective damaged membrane could also admit ions."))],
    plot("Initial transport rates across equal bilayer areas",[("O2; no protein",[(1,2),(2,4),(3,6),(4,8)]),("Z+; no protein",[(1,0),(2,0),(3,0),(4,0)]),("Z+; channel",[(1,1),(2,2),(3,3),(4,4)])],(0,4),(0,10),"Concentration difference / relative units","Initial inward rate / relative units"),
    [checks("O2 rate factor",8/2,4),checks("channel rate factor",4/1,4),truth("bare-ion rate zero",all(v==0 for v in [0,0,0,0]))],
    "B2.1 shared bilayer selectivity, simple/facilitated diffusion; electrochemical direction is supplied rather than requiring Nernst calculations.")
add(708,"Aquaporins change the time to osmotic equilibrium","B2.1",
    "Vesicles with or without aquaporins contain the same fixed amount of an impermeant solute. They are transferred to a large external solution of twice their initial internal solute concentration. Only water can cross; pressure effects are negligible and the external concentration remains constant. Volume is expressed relative to the initial volume.",
    [P("Predict the common final relative volume from solute conservation, and compare the observed volumes at 2 minutes.",
       M("Internal concentration doubles when the fixed solute amount occupies half its initial volume."),
       A("Both approach relative volume 0.500."),
       A("At 2 minutes the aquaporin vesicles are 0.55 and the others 0.80, a 0.25 initial-volume-unit difference.")),
     P("Explain the direction of net water movement and the differing rates without saying aquaporins actively pump water.",
       R("Net water moves out by osmosis toward the more concentrated external impermeant-solute solution."),
       R("Aquaporins increase water permeability, so the same equilibrium is approached faster; they do not use ATP to establish a different equilibrium.")),
     P("Evaluate the claim that a faster volume change proves the vesicles contain more solute.",
       R("The initial solute amount and concentration are controlled; permeability alone can account for the rate difference."),
       R("Measure final volumes and membrane integrity as well as initial rates; leakage of solute would violate the model."))],
    plot("Osmotic shrinking of matched vesicles",[("Aquaporins",[(0,1),(1,.65),(2,.55),(4,.505),(8,.5)]),("No aquaporins",[(0,1),(1,.9),(2,.8),(4,.65),(8,.52)])],(0,8),(0,1),"Time / min","Volume / initial volume",xticks=[0,2,4,6,8]),
    [checks("final volume fraction",1/2,.5),checks("two-minute gap",.80-.55,.25),truth("same equilibrium",.5==.5)],
    "B2.1 shared osmosis/aquaporins; no AHL formal water-potential calculation required.")
add(709,"ATP depletion separates uphill accumulation from a passive leak","B2.1",
    "A cell contains 80 mmol dm−3 of an uncharged solute S; the external solution contains 8 mmol dm−3. Temperature, viable cell number and external concentration are held constant. Inward uptake is 6.0 units with ATP available and 0.4 after ATP depletion. The membrane also permits a small outward passive leak. Protein P spans the bilayer.",
    [P("Determine the concentration ratio and explain why sustained inward accumulation requires an energy source.",
       M("Internal/external concentration=80/8."),
       A("The internal concentration is tenfold higher."),
       R("Net inward accumulation moves S against its concentration gradient; an ATP-driven pump can supply energy for this.")),
     P("Explain why the 0.4-unit uptake does not show that all transport stops when ATP is depleted.",
       R("The rate is reduced but not zero; background binding, incomplete ATP depletion or another route may remain."),
       R("Passive outward diffusion can continue down its gradient and does not directly require ATP.")),
     P("Calculate the percentage decrease in measured inward uptake and propose a control testing whether ATP depletion merely killed the cells.",
       M("Percentage decrease=(6.0−0.4)/6.0×100."),
       A("Measured inward uptake decreases by 93.3%."),
       R("Demonstrate viability and recovery after ATP restoration, with an equal-time untreated control; cell death or nonspecific membrane damage would otherwise confound interpretation."))],
    membrane("A candidate transport protein in an asymmetric solute distribution","Cytoplasm: S = 80 mmol dm−3","External solution: S = 8 mmol dm−3"),
    [checks("concentration ratio",80/8,10),checks("uptake decrease percent",(6-.4)/6*100,93.3333333333)],
    "B2.1 shared ATP-driven pumps versus passive movement; S is uncharged so no hidden electrical-gradient assumption.")
add(710,"Keeping digestive enzymes in a compartment protects the cytoplasm","B2.2",
    "Cells are gently homogenized in cold isotonic medium, then fractionated. Of the recovered acid-digestive-enzyme marker, 85% is in an organelle-rich pellet and 15% in supernatant. A soluble cytosolic marker is 10% in pellet and 90% in supernatant. The digestive enzyme works best at pH 5; cytoplasm is near pH 7. Intact vesicles show little activity against a large substrate outside them, but activity rises after detergent opens their membranes.",
    [P("Use both markers to evaluate the fractionation rather than calling the pellet pure.",
       A("The digestive marker is enriched in pellet, whereas the cytosolic marker is mainly in supernatant."),
       R("The pellet still contains 10% of recovered cytosolic marker and some digestive marker is outside it; cross-contamination or organelle breakage is possible."),
       R("Marker percentages describe recovery of each marker, not the percentage of pellet mass made of that organelle.")),
     P("Explain the activity increase after detergent and two benefits of compartmentalization.",
       R("An intact membrane restricts the large substrate's access to the enzyme; detergent removes this separation."),
       R("The compartment can concentrate digestive enzymes/substrates and maintain conditions favourable for digestion."),
       R("Separation of digestion from cytoplasmic reactions limits damage to other cellular components; the pH difference also reduces activity outside the compartment.")),
     P("Explain why cold isotonic conditions improve interpretation.",
       R("Cold slows unwanted enzyme reactions after disruption, while isotonic medium reduces osmotic damage to organelles."),
       R("Compare detergent and untreated samples at the same assay pH; otherwise changing pH could explain the activity difference."))],
    bars("Recovered marker distribution",["Digestive|pellet","Digestive|supernatant","Cytosolic|pellet","Cytosolic|supernatant"],[85,15,10,90],"Recovered marker / %",100),
    [checks("digestive recovery",85+15,100),checks("cytosolic recovery",10+90,100),checks("pellet enrichment ratio",85/10,8.5)],
    "B2.2 shared fractionation and separation of incompatible reactions; no recall of AHL Golgi/mitochondrial ultrastructure.")
add(711,"Subdivision improves exchange geometry without reducing total volume","B2.3",
    "A cube-shaped cell model has side 40 μm. It is divided into eight separate cubes of side 20 μm. Each surface is fully exposed to the same medium. Use surface area=6s² and volume=s³. The cubes are geometry models, not claims that living cells are perfect cubes.",
    [P("Calculate total volume and exposed surface area before and after subdivision.",
       M("Original volume=40³; original area=6×40². For eight smaller cubes multiply each 20 μm result by eight."),
       A("Volume is 64 000 μm³ in both cases; exposed area rises from 9 600 to 19 200 μm²."),
       A("Surface-area:volume ratio increases from 0.150 to 0.300 μm−1.")),
     P("Compare the maximum distance from a cube's centre to its nearest surface and explain the exchange advantage.",
       A("It decreases from 20 to 10 μm."),
       R("More exchange surface per unit volume and shorter internal diffusion distances can improve supply/removal relative to metabolic demand.")),
     P("Evaluate the model for a sheet of cells whose adjacent faces touch.",
       R("Touching faces are not fully exposed to the external medium, so summing all six faces overestimates exchange area."),
       R("Real cells differ in shape, permeability, membrane folding and internal transport; total surface area alone does not determine metabolic rate."))],
    cubes(),[checks("volume preserved",8*20**3,40**3),checks("original area",6*40**2,9600),checks("new area",8*6*20**2,19200),checks("SA V original",6/40,.15),checks("SA V new",6/20,.3)],
    "B2.3 shared cell-size and surface-area:volume scaling.")
add(712,"Self-renewal and differentiation are different pieces of evidence","B2.3",
    "Single cells from an adult tissue niche are cultured separately. Each of 20 clones produces both replacement stem-like cells and specialized cells of three lineages normally found in that tissue. Stem-like descendants are recloned twice and continue producing both populations. No cells from unrelated organs or extra-embryonic tissues have been tested. In a model embryo strip, genetically matched cells develop different fates in a supplied concentration gradient.",
    [P("Explain which observations support self-renewal and differentiation.",
       R("Repeated recloning with renewed stem-like descendants supports maintenance of the stem-cell population through divisions."),
       R("Production of specialized descendants of three lineages supports differentiation, rather than merely proliferation of one cell type.")),
     P("Evaluate claims that the cells are multipotent, pluripotent or totipotent.",
       A("The demonstrated range is consistent with multipotency within one tissue."),
       R("Three tissue lineages do not demonstrate the ability to make all body cell types required for pluripotency."),
       R("Totipotency additionally includes the capacity to form all tissues needed for a complete organism, including extra-embryonic tissues; this has not been shown.")),
     P("Explain why matched cells at different positions can differentiate differently, and propose a test of the gradient's role.",
       R("Different signal concentrations can cause different patterns of gene expression in cells with the same genome."),
       R("Move cells or change the gradient while controlling genotype and culture conditions; a predictable fate change would test the signal's influence."),
       R("Trace single-cell descendants to exclude a mixture of already specialized starting cells masquerading as one multipotent clone."))],
    svg("A model positional signal and clonal lineage output",
        "".join(rect(80+i*85,135,80,80,fill=f"#{(230-i*20):02x}{(230-i*20):02x}{(230-i*20):02x}")+text(120+i*85,183,str(6-i)) for i in range(6))+
        text(340,105,"Signal concentration / relative units",17)+text(170,250,"Fate X")+text(425,250,"Fate Y")+
        ellipse(225,345,28,28)+arrow(255,345,365,305)+arrow(255,345,365,385)+text(520,310,"Stem-like descendants retained",17)+text(520,390,"Three specialized lineages produced",17)),
    [checks("clonal founding cells",20,20),truth("tested lineages insufficient for all body types",3<200)],
    "B2.3 shared stem-cell potency, adult niches and signal gradients; no AHL specialized pneumocyte/gamete detail.")
add(713,"A thicker alveolar barrier can outweigh a large exchange surface","B3.1",
    "A simple model has oxygen transfer rate proportional to exchange area×concentration difference/barrier thickness. Tissue H has area 1.00 relative unit, concentration difference 1.00 unit and barrier thickness 1.00 μm, with transfer 240 arbitrary units. Tissue J has area 0.800, difference 0.900 and thickness 3.00 μm. Both are ventilated and perfused. This proportional model is supplied for this question.",
    [P("Predict J's rate relative to H and its numerical transfer rate.",
       M("J/H=(0.800×0.900/3.00)/(1.00×1.00/1.00)."),
       A("The predicted relative rate is 0.240, giving 57.6 transfer units."),
       R("The greater thickness increases diffusion distance, outweighing the retained surface and gradient.")),
     P("Distinguish the roles of ventilation, blood perfusion and diffusion.",
       R("Ventilation replaces air in the lungs and helps maintain the alveolar oxygen concentration."),
       R("Perfusion brings low-oxygen blood and removes oxygenated blood, helping maintain the gradient on the blood side."),
       R("Gas exchange itself is diffusion across the alveolar-capillary barrier; it is not the bulk movement of air or blood.")),
     P("Measured J transfer is 80 units. Evaluate whether the model's mismatch disproves diffusion.",
       R("It shows the simple model or its assumed average inputs are incomplete; it does not show oxygen is not diffusing."),
       R("Effective area, local gradients, blood flow and barrier thickness vary; measure/control these before identifying the cause of the difference."))],
    svg("Two schematic alveolar-capillary barriers",
        text(220,100,"H: 1.00 μm barrier")+text(590,100,"J: 3.00 μm barrier")+
        rect(100,155,240,42,fill="#eeeeee")+rect(470,155,240,126,fill="#eeeeee")+
        text(220,140,"Alveolar air",17)+text(590,140,"Alveolar air",17)+text(220,245,"Capillary blood",17)+text(590,330,"Capillary blood",17)+
        arrow(220,110,220,215)+arrow(590,110,590,300)+text(400,425,"Arrows indicate the oxygen-transfer direction; dimensions are schematic.",15)),
    [checks("relative transfer",.8*.9/3,.24),checks("predicted transfer",240*.24,57.6),checks("observed prediction ratio",80/57.6,1.3888888889)],
    "B3.1 shared exchange surfaces, gradients, ventilation and perfusion; no AHL Hb-affinity mechanisms.")
add(714,"Rapid shallow breathing can move less fresh air to exchange surfaces","B3.1",
    "A model adult has 0.150 L of conducting-airway dead space per breath. Pattern P is 12 breaths min−1 with tidal volume 0.500 L; Q is 30 breaths min−1 with tidal volume 0.200 L. Use minute ventilation=frequency×tidal volume and fresh air reaching exchange regions per minute=frequency×(tidal volume−dead space). Dead-space volume and gas composition are held constant.",
    [P("Calculate total minute ventilation and fresh-air delivery for both patterns.",
       M("Multiply frequency by tidal volume, then separately subtract dead space from each tidal volume before multiplying."),
       A("Both total minute ventilations are 6.00 L min−1."),
       A("Fresh-air delivery is 4.20 L min−1 for P and 1.50 L min−1 for Q.")),
     P("Explain why equal total ventilation does not imply equal oxygen uptake.",
       R("Q spends a larger fraction of each small breath moving air in conducting passages rather than replacing gas at exchange surfaces."),
       R("Oxygen uptake also depends on the maintained oxygen gradient, barrier properties and perfusion; minute ventilation alone is insufficient.")),
     P("Relate inspiration to the diaphragm and rib cage, distinguishing forced expiration from quiet recoil.",
       R("Diaphragm contraction flattens it and external intercostal action raises the ribs, increasing thoracic volume and lowering pressure to draw air in."),
       R("Quiet expiration can follow relaxation and elastic recoil; forceful expiration additionally uses expiratory muscles such as abdominal muscles/internal intercostals."))],
    plot("Two constructed tidal-volume traces",[("P",[(i/10,.25+.25*math.sin(2*math.pi*(i/10)/5)) for i in range(101)]),("Q",[(i/10,.10+.10*math.sin(2*math.pi*(i/10)/2)) for i in range(101)])],(0,10),(0,.6),"Time / s","Volume above end-expiratory level / L",xticks=[0,2,4,6,8,10]),
    [checks("P total",12*.5,6),checks("Q total",30*.2,6),checks("P fresh",12*(.5-.15),4.2),checks("Q fresh",30*(.2-.15),1.5)],
    "B3.1 shared lung-volume measurement and ventilation; dead-space model supplied, not an unsupported syllabus recall demand.")
add(715,"Stomatal counts require a sampling unit and a leaf context","B3.1",
    "One lower-epidermis field of area 0.200 mm² is counted on each of three independently grown sun leaves: 20, 24 and 16 stomata. Three independently grown shade leaves give 10, 12 and 8. Each count is one field per leaf; n=3 independent leaves per group. The schematic shows a typical dicot leaf section, not the counted surfaces. No significance test has been performed.",
    [P("Calculate mean stomatal density for each group and the percentage difference relative to shade leaves.",
       M("Mean counts are 20 and 10; divide each by 0.200 mm²."),
       A("Sun mean=100 stomata mm−2; shade mean=50.0 stomata mm−2."),
       A("The sun-group mean is 100% higher than the shade-group mean.")),
     P("Explain two leaf features supporting gas exchange and the resulting water-loss trade-off.",
       R("Stomata connect internal air spaces with external air, while spongy mesophyll air spaces expose a large moist exchange surface."),
       R("Opening stomata permits carbon dioxide entry but also water-vapour diffusion out, so increased access for gas exchange can increase transpiration.")),
     P("Evaluate the claim that the counts prove sun leaves always transpire twice as fast.",
       R("Stomatal aperture, size, humidity, wind and leaf temperature also affect loss; density alone does not establish the rate."),
       R("Three leaves give limited sampling, and no statistical significance follows automatically from these means."),
       R("Randomize matched genotypes to light treatments and count several fields per leaf while retaining leaf as the independent replicate."))],
    svg("Schematic transverse section of a dicot leaf",
        rect(90,100,620,35,fill="#eeeeee")+rect(90,310,620,30,fill="#eeeeee")+
        "".join(rect(110+i*60,145,45,80,12) for i in range(10))+
        "".join(ellipse(x,y,30,18) for x,y in [(145,270),(245,252),(340,280),(435,250),(540,280),(630,255)])+
        rect(375,310,50,30,fill="white")+arrow(400,360,400,292)+text(400,390,"Lower-surface opening",16)+
        text(400,75,"Upper surface",17)+text(400,438,"Tissue outlines only; not a micrograph and not to scale.",15)),
    [checks("sun density",statistics.mean([20,24,16])/.2,100),checks("shade density",statistics.mean([10,12,8])/.2,50),checks("density percent increase",(100-50)/50*100,100)],
    "B3.1 shared dicot leaf structure, stomatal density and replication; no significance inferred from n=3 or unspecified bars.")
add(716,"Wall structure is stronger evidence of vessel identity than blood colour","B3.2",
    "Two idealized circular vessel sections are drawn to the same geometric scale. Vessel X has lumen radius 4 units and outside radius 6; Y has lumen radius 6 and outside radius 7. X has much more smooth muscle and elastic tissue. Ignore tissue shrinkage for the calculations; the units are arbitrary and are not real vessel dimensions.",
    [P("Calculate wall thicknesses and the ratio of lumen areas Y:X.",
       A("Wall thickness is 2 units for X and 1 unit for Y."),
       M("Area ratio=π6²/(π4²)."),
       A("Y:X lumen area ratio=2.25:1.")),
     P("Deduce the more likely artery and vein, explaining form–function relationships.",
       A("X is more likely an artery; Y is more likely a vein."),
       R("A thicker muscular/elastic wall withstands and smooths higher arterial pressures."),
       R("A vein's lower-pressure return can be assisted by skeletal-muscle compression and valves that restrict backflow.")),
     P("Evaluate identification from oxygen concentration alone.",
       R("Artery means blood travels away from the heart and vein means toward it, not a fixed oxygen content."),
       R("Pulmonary vessels are a counterexample to the systemic oxygen pattern; use structure, direction and context together."))],
    svg("Two same-scale vessel cross-sections",
        ellipse(230,230,120,120,"#eeeeee")+ellipse(230,230,80,80)+text(230,237,"X",25)+
        ellipse(570,230,140,140,"#eeeeee")+ellipse(570,230,120,120)+text(570,237,"Y",25)+
        line(230,230,350,230)+text(290,215,"6",16)+line(570,230,690,230)+text(625,215,"6",16)+
        text(230,405,"Lumen r=4; outside r=6",17)+text(570,405,"Lumen r=6; outside r=7",17)),
    [checks("X wall",6-4,2),checks("Y wall",7-6,1),checks("lumen area ratio",6**2/4**2,2.25)],
    "B3.2 shared artery/vein adaptations and venous return; no AHL cardiac architecture required.")
add(717,"A potometer follows water uptake, not every water loss directly","B3.2",
    "In a sealed potometer the capillary radius is 0.500 mm. A bubble moves 5.00 mm in 10.0 min under drier air and 2.00 mm in 10.0 min after humidity is raised. Leaf area, temperature, light and air movement are controlled. Water uptake volume equals capillary cross-sectional area×bubble displacement; 1 mm³=1 μL.",
    [P("Calculate both uptake rates and their percentage decrease after humidity rises.",
       M("Rate=π(0.500)²×displacement/time."),
       A("Rates are 0.393 μL min−1 and 0.157 μL min−1."),
       A("Uptake decreases by 60.0%.")),
     P("Explain the humidity effect and the mechanism that moves the main transpiration stream through xylem.",
       R("Higher humidity reduces the water-vapour concentration gradient from moist leaf spaces to the air."),
       R("Evaporation from leaves produces tension; cohesion between water molecules transmits the pulling force through xylem."),
       R("Lignified xylem walls resist collapse; mature conducting vessel elements are dead and do not pump the water using ATP.")),
     P("Evaluate treating uptake as an exact direct measure of transpiration.",
       R("Some absorbed water may be retained in growth or changes in tissue water content, so uptake need not equal loss at every moment."),
       R("Check leaks and allow equilibration; repeat with independent shoots and standardize by leaf area."))],
    plot("Bubble displacement under two humidity conditions",[("Drier air",[(0,0),(2,1),(4,2),(6,3),(8,4),(10,5)]),("More humid air",[(0,0),(2,.4),(4,.8),(6,1.2),(8,1.6),(10,2)])],(0,10),(0,6),"Time / min","Bubble displacement / mm"),
    [checks("dry uptake μL min",math.pi*.5**2*5/10,.3926990817),checks("humid uptake",math.pi*.5**2*2/10,.1570796327),checks("percent decrease",(5-2)/5*100,60)],
    "B3.2 shared transpiration cohesion-tension and xylem; no AHL root pressure or formal water potential.")
add(718,"A rolled dune-grass leaf alters the environment of its stomata","B4.1",
    "Matched leaves of dune grass are compared under identical air movement, temperature and external humidity. Intact rolled leaves lose 2.0 g water h−1 per standardized leaf area, while experimentally held-open leaves lose 5.0 g h−1. The schematic shows the stomata on the inward-facing surface of a rolled leaf. The experiment does not measure evolutionary change.",
    [P("Calculate the percentage reduction in water loss associated with the rolled condition.",
       M("Use the held-open rate as the reference: (5.0−2.0)/5.0×100."),
       A("Water loss is 60.0% lower in the rolled condition.")),
     P("Explain how rolling and one other structural feature can be useful in a dry dune habitat.",
       R("Rolling shelters inward-facing stomata from wind and traps more humid air, reducing the water-vapour gradient."),
       R("A thick waxy cuticle reduces water movement through the epidermis; accept a correctly explained alternative such as hairs or reduced exposed leaf area.")),
     P("Evaluate whether the comparison proves the effect is entirely due to humidity inside the roll.",
       R("Holding leaves open could damage tissue or change illumination, temperature and exposed area as well as humidity."),
       R("Use a sham manipulation, check damage and internal humidity, and control actual leaf area before assigning one causal mechanism.")),
     P("Distinguish an inherited adaptation from a short-term response in this study.",
       R("An inherited capacity for leaf rolling can be an adaptation shaped over generations; rolling/unrolling by one leaf is a response, not evidence that the individual evolved."))],
    svg("A rolled-leaf cross-section with an internal stomatal surface",
        path("M280 113.756A240 140 0 1 0 520 113.756L502.5 139.737A205 110 0 1 1 297.5 139.737Z",fill="#eeeeee")+
        "".join(ellipse(x,y,8,5,"white") for x,y in [(605,235),(545,313),(400,345),(255,313),(195,235)])+
        text(400,225,"Sheltered air",19)+text(650,105,"External air",18)+arrow(590,110,455,120)+
        text(400,442,"Small gaps mark stomatal positions on the inward-facing epidermis.",16)),
    [checks("water-loss reduction percent",(5-2)/5*100,60),checks("rolled/open rate ratio",2/5,.4)],
    "B4.1 shared abiotic habitat adaptations and evaluating evidence; diagram is a schematic roll, not a measured grass micrograph.")
add(719,"Removing a competitor can reveal a broader potential niche","B4.2",
    "Snail S occurs along an intertidal height gradient. Replicated plots receive either competitor removal or a sham disturbance; the graph shows mean density after one season. Sample size is eight independent plots per treatment at each height. No error bars or significance test are supplied. Temperature and immersion time also vary with height.",
    [P("Describe the range change using the plotted densities and distinguish habitat from niche.",
       A("In sham plots S is recorded from 0 to 40 cm, while after removal it occurs from 0 to 80 cm."),
       R("Habitat is where it lives; niche includes its abiotic tolerances, resource use and interactions, not just a location.")),
     P("Explain how competition could restrict the realized niche and what the removal result cannot establish.",
       R("A competitor can reduce access to resources or space, excluding S from heights it could otherwise tolerate."),
       R("Removal supports a biotic restriction on the realized niche, but the experimentally occupied range is not proof of every boundary of the fundamental niche.")),
     P("Calculate the mean-density increase at 60 cm and evaluate the strength of the causal inference.",
       A("At 60 cm density rises from 0 to 12 snails m−2, an absolute increase of 12; a percentage increase from zero is undefined."),
       R("Randomized replicated removal with sham disturbance is stronger than an uncontrolled correlation."),
       R("Removal might also alter shelter or predators; repeat seasons and measure these variables, and do not infer significance from means alone."))],
    plot("Snail density along a constructed intertidal gradient",[("Sham plots",[(0,8),(20,18),(40,10),(60,0),(80,0),(100,0)]),("Competitor removed",[(0,9),(20,20),(40,18),(60,12),(80,5),(100,0)])],(0,100),(0,24),"Height above reference / cm","Mean snail density / m−2"),
    [checks("absolute increase at60",12-0,12),checks("range upper-bound difference",80-40,40),truth("percentage baseline zero undefined",0==0)],
    "B4.2 shared fundamental/realized niches and competition; distribution is not automatically a full tolerance boundary.")
add(720,"Both light and captured prey can contribute to one organism's nutrition","B4.2",
    "One unicellular organism grows in four controlled cultures. Growth rates in divisions day−1 are: light with prey 4.0; light without prey 2.0; darkness with prey 2.0; darkness without prey 0.2. Microscopy of separate labelled cultures shows prey enclosed in food vacuoles, and a carbon tracer shows inorganic carbon incorporation in light without prey. All cultures have the same dissolved inorganic nutrients; stored reserves may support limited short-term dark growth.",
    [P("Deduce the nutritional strategy from both kinds of evidence, rather than growth rate alone.",
       A("It is mixotrophic: it can obtain carbon through photosynthetic fixation and by feeding on prey."),
       R("Light-dependent inorganic-carbon incorporation supports photoautotrophy, while labelled prey inside food vacuoles supports holozoic ingestion.")),
     P("Calculate the growth-rate increase from adding prey in light and explain why the dark no-prey growth does not by itself prove a third nutritional mode.",
       M("Relative increase=(4.0−2.0)/2.0×100."),
       A("Prey doubles the light growth rate, a 100% increase."),
       R("Stored reserves or trace organic contamination could permit short-term growth; test sustained growth over serial transfers before inferring an additional carbon source.")),
     P("Design controls that make the tracer and prey evidence convincing.",
       R("Use washed, labelled prey and remove free label so uptake cannot be explained by dissolved labelled carbon."),
       R("Include killed-cell or no-cell controls and matched light/dark tracer cultures; distinguish internal food vacuoles from prey merely adhering outside."))],
    bars("Constructed growth under crossed light and prey conditions",["Light|prey","Light|no prey","Dark|prey","Dark|no prey"],[4,2,2,.2],"Growth / divisions day−1",5),
    [checks("light prey increase percent",(4-2)/2*100,100),checks("dark prey/no-prey ratio",2/.2,10)],
    "B4.2 shared mixotrophy, photoautotrophy and holozoic feeding; data sources and controls explicitly defined.")

# Additional higher level questions follow.
fold=svg("Two environments for a hydrophobic protein region",
    ellipse(220,240,135,100,fill="#eeeeee")+
    "".join(ellipse(x,y,18,18)+text(x,y+5,s,15) for x,y,s in [(140,190,"P"),(220,155,"−"),(305,205,"P"),(290,290,"+"),(180,325,"P"),(200,225,"H"),(250,255,"H"),(180,270,"H")])+
    text(220,390,"Soluble globular protein",17)+text(220,110,"Water",18)+
    rect(480,155,220,170,fill="#eeeeee")+rect(550,130,85,220,18)+text(592,245,"H-rich",17)+
    text(590,110,"Water",18)+text(590,390,"Membrane-spanning region",17)+text(400,445,"H: hydrophobic; P: polar; +/−: charged R-groups. Schematic positions.",15))
add(721,"The same R-group property can favour a core or a membrane-spanning surface","B1.2",
    "H denotes hydrophobic R-groups, P polar R-groups, and +/− charged R-groups. In soluble protein G, six of eight H residues are buried away from water; in membrane protein T, a central H-rich segment contacts the lipid bilayer. A mutation replaces one buried H residue of G with a charged residue. The mutation changes the sequence but not chain length.",
    [P("Calculate the fraction of G's H residues buried, and explain the different H-rich positions in G and T.",
       A("Six of eight is 0.750, or 75.0%."),
       R("In water-soluble globular proteins, hydrophobic R-groups tend to cluster internally, reducing contact with water."),
       R("A membrane-spanning protein exposes hydrophobic R-groups toward the bilayer's hydrophobic core, while hydrophilic regions can contact water.")),
     P("Explain how the mutation could change tertiary conformation without breaking the peptide backbone.",
       R("Primary sequence fixes the positions and chemical properties of R-groups, so a charged replacement changes local interactions."),
       R("A buried charge can be unfavourable unless accommodated by suitable interactions; folding/stability can change while peptide connectivity and chain length remain."),
       R("The effect is context dependent; a sequence change does not guarantee complete denaturation.")),
     P("Propose a test distinguishing reduced stability from reduced protein production.",
       R("Measure equal purified amounts of wild-type and mutant protein in a matched unfolding/function assay."),
       R("Also quantify cellular protein abundance; lower activity in whole cells alone could reflect less protein rather than changed activity per molecule."))],
    fold,[checks("buried fraction",6/8,.75),checks("buried percent",6/8*100,75)],
    "B1.2.6–10 AHL R-group chemistry, sequence/conformation and environment-dependent hydrophobic positioning.")
add(722,"Regular backbone hydrogen bonding stabilizes secondary structure","B1.2",
    "A model alpha helix contains 12 residues in one uninterrupted segment. For counting only, the supplied rule is that residue i can hydrogen-bond through its backbone C=O to the backbone N–H of residue i+4, when both residues lie in the segment. The diagram shows selected backbone donors and acceptors, not all atoms. A treatment disrupts these hydrogen bonds without cleaving peptide bonds.",
    [P("Determine the possible i values and maximum number of such internal hydrogen bonds in this model.",
       M("The last acceptor index must satisfy i+4≤12, while i starts at 1."),
       A("i=1 through 8, giving eight modeled internal hydrogen bonds.")),
     P("Distinguish the bonds stabilizing the helix from the bonds connecting successive residues, and compare an alpha helix with a beta-pleated sheet.",
       R("The regular hydrogen bonds are between backbone groups; peptide bonds are covalent links joining successive amino acids."),
       R("An alpha helix is coiled; a beta-pleated sheet consists of extended pleated strands linked by regular hydrogen bonding."),
       R("Secondary-structure hydrogen bonds should not be described as a chain of peptide bonds between R-groups.")),
     P("Predict what can change after treatment and what cannot be concluded from an unchanged sequence.",
       R("Helical organization can be lost or rearranged without changing the amino-acid order or number of peptide bonds."),
       R("Unchanged primary structure does not guarantee unchanged secondary/tertiary conformation or function; measure structure and activity separately."))],
    svg("Selected donor–acceptor contacts in a helical backbone model",
        path("M130 145C210 60 330 230 410 145S610 60 690 145M130 270C210 185 330 355 410 270S610 185 690 270",width=3)+
        "".join(text(x,180,"C",19)+text(x+45,180,"O",19)+line(x+14,171,x+30,171)+line(x+14,177,x+30,177)+
                text(x,245,"N",19)+text(x+45,245,"H",19)+line(x+14,238,x+30,238)+line(x+45,189,x+45,225,dash=True) for x in [195,495])+
        text(400,365,"Dashed contacts: O···H hydrogen bonds between backbone groups.",16)+text(400,405,"Two selected turns of one helix are shown; intervening backbone is omitted.",15)),
    [checks("helix hydrogen bonds",12-4,8),checks("chain peptide links",12-1,11)],
    "B1.2.8–9 AHL secondary structure; i→i+4 supplied as model information, not required memorized nomenclature.")
_insulin=svg("Numbered chains and disulfide connections of mature insulin",
    line(100,150,700,150,width=4)+line(100,300,700,300,width=4)+
    text(75,155,"A",22)+text(75,305,"B",22)+
    "".join(text(100+(n-1)*30,132,str(n),15) for n in [1,6,7,11,20,21])+
    "".join(text(100+(n-1)*600/29,331,str(n),15) for n in [1,7,19,30])+
    path("M250 150Q325 60 400 150",width=2)+text(325,83,"S–S",16)+
    line(280,150,100+6*600/29,300)+text(235,232,"S–S",16)+
    line(670,150,100+18*600/29,300)+text(585,232,"S–S",16)+
    text(400,400,"A:21 residues; B:30 residues. Connections: A6–A11, A7–B7, A20–B19.",16))
add(723,"Reducing insulin disulfides is not the same as hydrolysing its chains","B1.2",
    "Mature insulin consists of chain A with 21 residues and chain B with 30. The displayed disulfides are A6–A11, A7–B7 and A20–B19. A reducing treatment breaks only the disulfide connections; a separate complete hydrolysis breaks all peptide bonds. No peptide bond joins A to B in mature insulin.",
    [P("Count intrachain and interchain disulfides and determine the number of polypeptide chains after reduction alone.",
       A("There is one intrachain disulfide and two interchain disulfides."),
       R("Reduction leaves two polypeptide chains; it does not produce 51 free amino acids because peptide bonds have not been hydrolysed.")),
     P("Calculate the number of peptide bonds hydrolysed and water molecules consumed per insulin molecule during complete peptide hydrolysis.",
       M("Each open chain has one fewer peptide bond than residues: (21−1)+(30−1)."),
       A("There are 49 peptide bonds, requiring 49 water molecules to hydrolyse them.")),
     P("Explain the structural roles of cysteine and the two chains, and evaluate using a lost binding response as proof of peptide cleavage.",
       R("Pairs of cysteine R-groups can form covalent disulfide bonds that help stabilize conformation and join chains."),
       R("The association of more than one polypeptide chain is quaternary organization; the disulfides also constrain their folded arrangement."),
       R("Lost receptor binding can result from changed conformation even with intact primary chains; determine chain size or peptide products to establish cleavage."))],
    _insulin,[checks("total residues",21+30,51),checks("peptide links",(21-1)+(30-1),49),checks("disulfide categories",1+2,3)],
    "B1.2.9–12 AHL disulfides/quaternary structure using insulin; mature insulin chain connections accurately indexed.")
add(724,"Protein subunits and non-protein groups answer different structural questions","B1.2",
    "In a simplified separation, native haemoglobin H has protein mass 64 kDa and gives four 16 kDa polypeptide subunits after dissociation. Each subunit carries one haem group, whose mass is ignored here. Collagen C is a fibrous triple-polypeptide assembly of approximately 300 kDa, giving three approximately 100 kDa chains. The chart concerns molecular mass, not protein concentration.",
    [P("Use the masses to calculate subunit numbers and explain why a haem group is not another polypeptide subunit.",
       M("Divide native protein mass by the mass of one polypeptide."),
       A("H has four polypeptide subunits; C has three."),
       R("Haem is a non-polypeptide component, making haemoglobin a conjugated protein; it is not a fifth amino-acid chain.")),
     P("Relate globular and fibrous organization to oxygen transport and tensile support.",
       R("Compact soluble haemoglobin has haem sites that bind oxygen reversibly and can be transported within red cells."),
       R("Long fibrous collagen assemblies give tensile strength and structural support, rather than functioning as soluble oxygen carriers.")),
     P("Evaluate a conclusion that equal masses of H and C contain equal numbers of native protein assemblies.",
       M("At equal mass, molecule number is inversely proportional to molecular mass."),
       A("H:C assembly number ratio is 300/64=4.69:1, not 1:1."),
       R("The approximate masses simplify real molecular variants and associated groups; they do not by themselves measure tissue mechanical strength."))],
    bars("Native assembly and dissociated polypeptide masses",["H native","H chain","C native","C chain"],[64,16,300,100],"Protein molecular mass / kDa",360),
    [checks("H subunits",64/16,4),checks("C subunits",300/100,3),checks("equal mass number ratio",300/64,4.6875)],
    "B1.2.11–12 AHL conjugated/quaternary and fibrous/globular form–function; no clinical inference.")
add(725,"Cold acclimation changes membrane composition without proving a DNA change","B2.1",
    "Genetically matched fish of one species are acclimated for four weeks at 5 °C or 20 °C. Unsaturated fatty-acid tails make up 60% and 30% of their membrane tails, respectively. The graph compares equal-composition model bilayers; larger fluidity-index values mean greater fluidity. All other lipid components are held constant.",
    [P("Calculate the change in unsaturated-tail percentage and explain how it can compensate for low temperature.",
       A("The cold-acclimated membranes have 30 percentage points more unsaturated tails, a 100% relative increase from 30%."),
       R("Cis unsaturated tails pack less tightly and have lower melting transitions, helping membranes remain fluid at lower temperature."),
       R("The change can oppose the stiffening caused by cooling; it does not mean cooling itself increases fluidity.")),
     P("Use the model curves to evaluate the claim that the composition advantage is identical at every temperature.",
       A("At 5 °C indices are 40 versus 15, while at 20 °C they are 70 versus 55: differences of 25 and 15 units."),
       R("The response depends on temperature and other membrane components; a fixed percentage composition does not imply a fixed fluidity difference.")),
     P("Distinguish acclimation from demonstrated evolutionary adaptation and suggest a reciprocal-transfer test.",
       R("A reversible change within genetically matched fish is acclimation/plasticity; this experiment does not show a heritable change in allele frequencies."),
       R("Transfer fish back to the other temperature and remeasure composition/fluidity after controlled intervals; retain independent fish as replicates."))],
    plot("Composition-specific model membrane fluidity",[("60% unsaturated",[(5,40),(10,50),(15,60),(20,70),(25,80)]),("30% unsaturated",[(5,15),(10,28),(15,42),(20,55),(25,68)])],(5,25),(0,100),"Temperature / °C","Fluidity index / relative units",xticks=[5,10,15,20,25]),
    [checks("percentage point change",60-30,30),checks("relative change percent",(60-30)/30*100,100),checks("cold index gap",40-15,25),checks("warm index gap",70-55,15)],
    "B2.1.11 AHL fatty-acid composition and membrane fluidity in a habitat/acclimation context.")
add(726,"Cholesterol buffers fluidity in opposite directions at opposite temperatures","B2.1",
    "Model animal-cell membranes have identical phospholipids and proteins but either contain cholesterol or lack it. The fluidity index is defined so that larger values mean more fluid membrane. The curves are constructed equilibrium measurements, not universal numerical values for every membrane.",
    [P("Compare cholesterol's effects at 5 °C and 40 °C using numerical differences.",
       A("At 5 °C, cholesterol raises the index from 5 to 25, an increase of 20 units."),
       A("At 40 °C, cholesterol lowers the index from 80 to 55, a decrease of 25 units.")),
     P("Explain how one molecule can have these contrasting effects, including its location.",
       R("Cholesterol lies among phospholipid tails, with its small polar region near the head-group/water interface."),
       R("At low temperature it interferes with very close tail packing and helps prevent stiffening."),
       R("At high temperature it restrains phospholipid movement, reducing excessive fluidity and stabilizing the bilayer.")),
     P("Evaluate the claim that adding cholesterol always makes membranes more fluid, and give a limitation of this experiment.",
       R("The high-temperature results directly contradict an always-increases claim; its effect is temperature dependent."),
       R("These matched model membranes isolate one variable but lack the full diversity of lipid/protein compositions found in living cells."))],
    plot("Temperature-dependent fluidity modulation",[("No cholesterol",[(5,5),(15,22),(25,48),(40,80)]),("With cholesterol",[(5,25),(15,32),(25,42),(40,55)])],(5,40),(0,100),"Temperature / °C","Fluidity index / relative units",xticks=[5,15,25,40]),
    [checks("cold cholesterol effect",25-5,20),checks("warm cholesterol effect",55-80,-25),truth("effects opposite sign",(25-5)*(55-80)<0)],
    "B2.1.12 AHL temperature-dependent cholesterol modulation; presence in a fluid-mosaic model alone would be shared.")
endo=svg("Membrane sidedness during an endocytic event",
    text(400,80,"Extracellular solution; impermeant label binds domain X",17)+
    path("M75 165H290C315 165 300 245 340 265C380 290 425 265 425 225V165H725",width=4)+
    text(155,210,"Cytoplasm",18)+
    line(365,244,365,284,width=5)+ellipse(365,231,12,12,"black")+text(380,218,"X",16)+
    arrow(480,250,560,250)+ellipse(635,260,65,65)+line(635,247,635,334,width=5)+ellipse(635,235,12,12,"black")+text(658,226,"X",16)+
    text(635,360,"Closed vesicle",17)+text(400,438,"The labelled extracellular domain is carried into the vesicle lumen.",16))
add(727,"An extracellular protein domain becomes an endocytic luminal domain","B2.1",
    "An impermeant fluorescent reagent labels an extracellular domain X of a plasma-membrane protein. After endocytosis and removal of surface label, isolated intact vesicles retain 80 fluorescence units after external protease. Detergent plus protease reduces the signal to 5. Protease cannot cross an intact bilayer. The schematic shows the membrane's sidedness; it does not show a pore opening through the cell.",
    [P("Explain the protease-protection result and calculate the fraction of fluorescence protected above the detergent/protease background.",
       R("After inward budding, the former extracellular domain faces the vesicle lumen, so external protease cannot reach it."),
       M("The protected component is 80−5=75 of the 80 units retained before detergent."),
       A("The protected fraction on that definition is 75/80=93.8%.")),
     P("Distinguish endocytosis from simple diffusion and predict X's orientation after the same vesicle fuses with the plasma membrane.",
       R("Endocytosis encloses material by membrane budding, whereas diffusion moves individual particles through a membrane/pathway down a gradient."),
       R("Fusion returns the luminal domain to the extracellular side; membrane orientation is preserved rather than randomly flipped.")),
     P("Evaluate whether protease protection alone proves endocytosis occurred in the living cell.",
       R("Protection supports enclosure but could also arise in sealed membrane fragments formed during isolation."),
       R("Include a time-resolved uptake assay in intact cells, a non-endocytosed surface-marker control and membrane-integrity controls to test that alternative."))],
    endo,[checks("protected fluorescence component",80-5,75),checks("protected fraction percent",(80-5)/80*100,93.75)],
    "B2.1.13 AHL endocytosis/exocytosis and fluid membrane sidedness; no detailed vesicle-protein catalogue required.")
add(728,"A ligand gate and a voltage gate respond to different triggers","B2.1",
    "A neuronal membrane preparation contains nicotinic acetylcholine receptors and voltage-gated sodium channels. The solution and voltage conditions make sodium entry favourable through either open pathway. Acetylcholine opens a conductance of 8.0 units; a receptor-specific antagonist reduces it to 0.2. A separate depolarizing voltage step opens sodium-channel conductance of 20 units, unchanged by that antagonist. The traces represent independent trials, not one action potential.",
    [P("Deduce which gate responds to each trigger and calculate antagonist inhibition of the acetylcholine response.",
       A("Acetylcholine activates ligand-gated nicotinic receptors; the voltage step activates voltage-gated sodium channels."),
       M("Inhibition=(8.0−0.2)/8.0×100."),
       A("The acetylcholine-evoked conductance is inhibited by 97.5%.")),
     P("Explain why opening a channel is not equivalent to actively pumping sodium.",
       R("Opening changes permeability; sodium then moves down the supplied electrochemical gradient."),
       R("The open channel does not directly hydrolyse ATP to move sodium uphill, even though energy is needed elsewhere to maintain gradients.")),
     P("Evaluate interpreting an unchanged voltage-step response as proof that the antagonist has no other cellular effect.",
       R("It supports selectivity for the tested responses at that dose, but does not test every protein or pathway."),
       R("Use dose-response, vehicle and viability controls; the independent-trial design prevents assuming one trace caused the other."))],
    plot("Independent channel-conductance trials",[("ACh",[(0,0),(1,0),(1.05,8),(3,8),(3.05,0),(5,0)]),("ACh + antagonist",[(0,0),(1,0),(1.05,.2),(3,.2),(3.05,0),(5,0)]),("Voltage step",[(0,0),(1,0),(1.05,20),(3,20),(3.05,0),(5,0)])],(0,5),(0,24),"Time / s","Conductance / relative units"),
    [checks("antagonist inhibition percent",(8-.2)/8*100,97.5),checks("voltage response retention",20/20,1)],
    "B2.1.14 AHL ligand/voltage-gated neuronal channels; nicotinic receptor example correct and electrochemical direction supplied.")
add(729,"An exchange pump transports unequal charges in each cycle","B2.1",
    "The sodium–potassium pump uses one ATP per complete forward cycle. Each cycle exports three Na+ and imports two K+. In a short counting model it completes 800 cycles; ignore passive leaks and changes in compartment volume. The drawing places the ions on their destination sides after transport, not at binding sites inside the pump.",
    [P("Calculate ATP use, Na+ exported, K+ imported and the net positive-charge movement.",
       M("Multiply each stoichiometric amount by 800 cycles."),
       A("800 ATP are used; 2 400 Na+ move out and 1 600 K+ move in."),
       A("There is a net export of 800 positive elementary charges.")),
     P("Explain the pump's contributions to ion gradients and membrane potential, distinguishing it from channels.",
       R("ATP hydrolysis supports sodium export and potassium import against their maintained electrochemical gradients."),
       R("Unequal positive-charge transfer contributes directly to an inside-negative potential; gradients also permit selective passive ion movement that helps generate membrane potential."),
       R("Channels allow downhill movement when open rather than carrying out this ATP-linked 3:2 exchange.")),
     P("Evaluate extrapolating the count to the voltage change of a living neuron.",
       R("Charge count alone does not determine voltage without membrane capacitance and geometry."),
       R("Living cells have leaks, other transporters and changing ion distributions; the no-leak model is a short stoichiometric count, not a full voltage prediction."))],
    membrane("Sodium–potassium exchange: destination sides","Cytoplasm: two K+ delivered per cycle","Extracellular side: three Na+ delivered per cycle") ,
    [checks("ATP",800,800),checks("Na exported",800*3,2400),checks("K imported",800*2,1600),checks("net charge exported",800*(3-2),800)],
    "B2.1.15 AHL sodium–potassium exchange and generation of membrane potential; no Nernst/capacitance calculation required.")
_cotrans=svg("An epithelial cell with apical and basolateral routes",
    rect(170,150,460,175,20)+text(400,105,"Lumen: Na+ = 140; glucose = 1 mmol dm−3",18)+text(400,380,"Basolateral extracellular fluid",18)+
    text(400,235,"Cell: Na+ = 10; glucose = 5 mmol dm−3",18)+rect(245,130,100,45,10,fill="#eeeeee")+text(295,158,"T",20)+
    rect(445,300,100,45,10,fill="#eeeeee")+text(495,329,"Pump",18)+rect(250,300,100,45,10,fill="#eeeeee")+text(300,329,"Carrier",18)+
    text(400,435,"T couples inward Na+ movement with inward glucose transport.",16))
add(730,"Glucose accumulation can depend indirectly on ATP","B2.1",
    "An intestinal epithelial model has an apical sodium-dependent glucose cotransporter T. Luminal sodium is 140 mmol dm−3 and cellular sodium10; luminal glucose is1 and cellular glucose5. The electrochemical gradient favours sodium entry. A basolateral Na+/K+ pump maintains the sodium gradient; a separate basolateral carrier allows glucose exit when its gradient is outward. After pump inhibition, initial glucose uptake declines gradually from60 to10 units over30min rather than stopping instantly.",
    [P("Explain how T can accumulate glucose despite the glucose concentration difference.",
       R("Sodium entry down its electrochemical gradient releases free energy."),
       R("Coupling that entry to glucose entry allows glucose to move against its own concentration gradient."),
       R("The glucose concentration is fivefold greater inside, so simple inward glucose diffusion alone cannot maintain this accumulation.")),
     P("Distinguish direct from indirect ATP dependence and explain the delayed inhibition.",
       R("The pump directly uses ATP; T uses the stored sodium gradient rather than hydrolysing ATP directly."),
       R("An existing gradient can drive transport briefly after the pump stops, then weakens as sodium redistributes."),
       A("The uptake decrease is (60−10)/60×100=83.3% after30min.")),
     P("Evaluate a conclusion that an ATP inhibitor acts specifically on T.",
       R("The inhibitor could reduce the pump's activity or other ATP-dependent cell functions, indirectly reducing T flux."),
       R("Test T with an imposed sodium gradient in a controlled membrane preparation and monitor viability/gradient to separate direct from indirect effects."))],
    _cotrans,[checks("glucose accumulation ratio",5/1,5),checks("Na concentration ratio outside inside",140/10,14),checks("uptake decrease percent",(60-10)/60*100,83.3333333333)],
    "B2.1.16 AHL sodium-dependent glucose cotransport and direct/indirect ATP dependence; epithelial polarity explicit.")
_mito=svg("A continuous inner membrane folded within a mitochondrial envelope",
    rect(80,95,640,245,90)+
    path("M110 220Q110 125 175 125H195V235Q195 250 210 250Q225 250 225 235V125H275V255Q275 270 290 270Q305 270 305 255V125H355V235Q355 250 370 250Q385 250 385 235V125H435V255Q435 270 450 270Q465 270 465 255V125H515V235Q515 250 530 250Q545 250 545 235V125H620Q690 125 690 220Q690 310 620 310H175Q110 310 110 220Z",width=3)+
    text(605,283,"P",22)+arrow(605,265,595,220)+text(585,77,"Q",22)+arrow(585,85,585,110)+
    text(400,405,"P and Q identify fluid regions; the folded boundary is one continuous membrane.",16))
add(731,"Cristae add membrane area while the matrix keeps a different reaction environment","B2.2",
    "Two equal-volume mitochondrial preparations have the same amount of matrix-enzyme marker. Normal inner-membrane area is40 μm² per mitochondrion and model mutant area20 μm². Under matched substrate and oxygen conditions ATP production is100 versus60 units. P and Q mark fluid regions in the schematic. Do not infer that membrane area is the only altered feature of a real mutant.",
    [P("Identify P and Q and link the compartments and cristae to aerobic respiration.",
       A("P is matrix; Q is intermembrane space."),
       R("Matrix compartmentalizes enzymes and substrates of the Krebs cycle."),
       R("Cristae enlarge inner-membrane area for membrane-associated ATP-producing processes; the small intermembrane volume helps maintain distinct local conditions.")),
     P("Calculate area and ATP-production changes and evaluate a strict proportionality claim.",
       A("Area falls by50.0%, whereas ATP production falls by40.0%."),
       M("ATP per stated area is100/40=2.50 versus60/20=3.00 units μm−2."),
       R("The values are not strictly proportional; differences in functional density, conditions or other altered properties may contribute.")),
     P("Explain why an unchanged amount of one matrix marker is useful but insufficient as a complete control.",
       R("It supports comparable recovery of that matrix component, helping distinguish membrane-area loss from loss of all mitochondria."),
       R("It does not establish equal amounts/activity of every enzyme, intact membranes or equal substrate transport; additional integrity and component controls are needed."))],
    _mito,[checks("area reduction percent",(40-20)/40*100,50),checks("ATP reduction percent",(100-60)/100*100,40),checks("normal ATP per area",100/40,2.5),checks("mutant ATP per area",60/20,3)],
    "B2.2.4 AHL mitochondrial ultrastructure; cristae are continuous invaginations, not free sacs or detached matrix compartments.")
_chloro=svg("Envelope, stroma and closed thylakoid compartments",
    ellipse(400,235,305,145)+ellipse(400,235,290,130)+
    "".join(rect(x,y,135,22,11,fill="#eeeeee") for x in [205,455] for y in [175,202,256])+
    rect(205,229,385,22,11,fill="#eeeeee")+text(390,315,"Y",22)+text(240,191,"X",17)+arrow(240,150,240,177)+
    text(400,425,"Each narrow rounded compartment is closed; connecting membrane is schematic.",16))
add(732,"A large thylakoid surface is distinct from the surrounding stroma","B2.2",
    "X marks the fluid enclosed inside one thylakoid; Y is outside thylakoids but inside the chloroplast envelope. Preparation A has total thylakoid-membrane area20 μm² and enclosed thylakoid-fluid volume0.200 μm³. Preparation B has the same area but volume0.400 μm³. Equal photosystem content per unit membrane area and equal stromal enzyme amounts are assumed.",
    [P("Identify X and Y and locate photosystems and Calvin-cycle enzymes.",
       A("X is thylakoid lumen; Y is stroma."),
       R("Photosystems are in thylakoid membranes; Calvin-cycle enzymes and substrates are compartmentalized in the stroma."),
       R("The double envelope separates the chloroplast from cytoplasm but is not a substitute for the internal thylakoid system.")),
     P("Calculate membrane-area:enclosed-volume ratios and explain a possible benefit of small luminal volume.",
       M("Area/volume=20/0.200 or20/0.400."),
       A("A=100 μm−1; B=50.0 μm−1."),
       R("For a given transported amount, smaller fluid volume permits a larger concentration change and helps maintain distinct conditions across the membrane.")),
     P("Evaluate the claim that A must photosynthesize at exactly twice B's rate.",
       R("The ratio is twice as large, but photosystem number is assumed equal because membrane area and density are equal."),
       R("Light, carbon availability, transport and enzyme rates may limit the overall rate; an area:volume ratio alone does not prove a twofold photosynthetic flux."))],
    _chloro,[checks("A area volume",20/.2,100),checks("B area volume",20/.4,50),checks("ratio of ratios",(20/.2)/(20/.4),2)],
    "B2.2.5 AHL chloroplast thylakoid/stroma compartmentation; no requirement for a memorized light-reaction electron-carrier sequence.")
add(733,"A pulse-chase follows a secreted protein through several compartments","B2.2",
    "A short pulse labels newly synthesized protein P, then unlabelled amino acids are supplied. At2,10 and30min, recovered label percentages are RER70/20/5, Golgi10/60/10, extracellular medium0/20/80 and other fractions20/0/5. Each time totals100%. A separately labelled cytosolic protein Q stays mainly outside the secretory compartments. The plotted percentages describe recovered P label, not organelle volume.",
    [P("Deduce the likely route of P and explain where ribosomes synthesize P compared with Q.",
       A("P's sequence is RER→Golgi→secretory vesicles→extracellular medium."),
       R("Membrane-bound ribosomes on rough ER synthesize proteins entering this intracellular transport/secretion route."),
       R("Free ribosomes synthesize Q for retention in the cytosolic compartment; their different location does not require a different genetic code.")),
     P("Calculate the extracellular percentage-point increase between2 and30min, and explain the Golgi peak without claiming Golgi makes the peptide backbone.",
       A("Extracellular label increases by80 percentage points."),
       R("Label first accumulates in Golgi and then leaves as processed protein moves onward in vesicles."),
       R("Ribosomes synthesize the polypeptide; Golgi processes and sorts it for secretion, rather than translating its amino-acid sequence.")),
     P("Evaluate whether the time course proves every labelled molecule followed exactly that route.",
       R("Population fractions are compatible with the route but do not track every molecule individually; fraction contamination and label recycling can affect results."),
       R("Use a protein-specific assay, short chase, fraction-purity markers and controlled transport inhibition to strengthen the inference."))],
    plot("Recovered pulse label of protein P",[("RER",[(2,70),(10,20),(30,5)]),("Golgi",[(2,10),(10,60),(30,10)]),("Medium",[(2,0),(10,20),(30,80)])],(0,30),(0,100),"Chase time / min","Recovered P label / %",xticks=[0,2,10,20,30]),
    [checks("2min recovery",70+10+0+20,100),checks("10min recovery",20+60+20+0,100),checks("30min recovery",5+10+80+5,100),checks("medium increase points",80-0,80)],
    "B2.2.7–8 AHL free/bound ribosomes, RER and Golgi processing/secretion; tracer caveats explicit.")
_nuc=svg("A nuclear envelope with an open pore and separated cytoplasm",
    ellipse(345,235,200,140)+ellipse(345,235,185,125)+
    '<rect x="516" y="214" width="45" height="48" fill="white"/>'+line(516,214,561,214)+line(516,262,561,262)+
    path("M235 215l20 -12l20 18l20 -15l20 16",width=3)+text(270,265,"Labelled RNA",17)+
    text(345,140,"Nucleoplasm",18)+text(660,140,"Cytoplasm",18)+
    "".join(ellipse(x,y,9,6,"black") for x,y in [(620,210),(690,260),(640,320)])+
    text(665,365,"Ribosomes",17)+text(400,440,"The gap represents a nuclear pore, not an unsealed random tear.",16))
add(734,"Nuclear pores allow regulated exchange across a double envelope","B2.2",
    "A labelled RNA is initially detected in the nucleus. In controls, nuclear/cytoplasmic recovered label changes from8/2 units at2min to2/8 at10min. An export-blocking treatment gives9/1 at10min, with unchanged total recovered label. Ribosomes translating this RNA are in the cytoplasm. The treatment is tested only over this short period.",
    [P("Calculate the cytoplasmic fraction at10min in control and treated cells, and relate the change to nuclear pores.",
       M("Divide cytoplasmic label by total recovered label10."),
       A("Control fraction=80%; treated fraction=10%, a70 percentage-point difference."),
       R("Pores provide a route across the double nuclear envelope; blocked export can retain RNA in the nucleus.")),
     P("Explain the functional advantage of separating transcription from cytoplasmic translation.",
       R("New RNA can undergo post-transcriptional processing before it meets translating ribosomes."),
       R("The nuclear boundary permits different regulated activities and conditions; a pore allows exchange without removing compartmental separation.")),
     P("Explain why the envelope disassembles during nuclear division, and evaluate the short-term export evidence.",
       R("Envelope breakdown allows chromosome attachment/segregation through the division machinery; membrane components can reassemble around daughter nuclei."),
       R("Equal total label controls recovery but not every alternative: the treatment might alter RNA degradation or processing, so measure these and cell viability before assigning a specific pore defect."))],
    _nuc,[checks("control cytoplasmic percent",8/(2+8)*100,80),checks("treated cytoplasmic percent",1/(9+1)*100,10),checks("difference points",80-10,70)],
    "B2.2.6 AHL nuclear-envelope pores and division; shared processing advantage linked to required AHL envelope behavior.")
_clathrin=svg("A coated pit viewed from the cytoplasmic side",
    text(400,78,"Extracellular space: receptor-bound cargo",17)+
    path("M95 155H280C305 155 300 260 355 280C410 300 475 260 475 210V155H715",width=4)+
    "".join(ellipse(x,y,9,9,"black") for x,y in [(335,225),(375,250),(425,225)])+
    "".join(path(f"M{x-10} {y-8}l10 -9l10 9l-10 12z",width=1.6) for x,y in [(295,220),(310,260),(345,295),(390,309),(435,295),(475,260),(490,220)])+
    text(400,370,"Polygonal coat: cytoplasmic clathrin",17)+arrow(400,345,390,315)+
    text(400,435,"Cargo remains on the extracellular/luminal side of the bending membrane.",15))
add(735,"A coat-defective cell can still bind cargo at its surface","B2.2",
    "Control cells bind100 units of receptor-specific cargo at the surface and internalize70 units during a short pulse. Clathrin-reduced cells bind98 units but internalize15. Counts are normalized per viable cell and a wash removes unbound cargo. The schematic places the coat on the cytoplasmic side of the membrane.",
    [P("Calculate internalized cargo as a percentage of bound cargo for each condition.",
       M("Use internalized/bound×100, not both values divided by control binding."),
       A("Control=70.0%; clathrin-reduced=15/98×100=15.3%.")),
     P("Explain how the coat contributes and which step is most directly affected by these results.",
       R("Clathrin participates in membrane bending/formation of coated vesicles, helping concentrate selected membrane cargo."),
       R("Near-normal binding with much lower internalization supports an uptake/vesicle-formation defect rather than simple absence of surface binding sites."),
       R("The coat is cytoplasmic; cargo enclosed from outside lies in the vesicle lumen, not embedded in the clathrin coat.")),
     P("Evaluate whether these data prove all cellular endocytosis requires clathrin.",
       R("Only this cargo, cell type and intervention were tested; alternative uptake mechanisms are not excluded."),
       R("Restore clathrin expression and test rescue while monitoring general membrane integrity and other cargos to support specificity."))],
    _clathrin,[checks("control internalization percent",70/100*100,70),checks("reduced internalization percent",15/98*100,15.306122449),checks("binding retention",98/100,.98)],
    "B2.2.9 AHL clathrin and vesicle formation; correct cytoplasmic coat orientation and cargo protection.")
_villi=svg("A continuous apical membrane with microvilli",
    text(400,85,"Extracellular lumen",19)+
    path("M90 310H175V175Q175 150 195 150Q215 150 215 175V310H275V175Q275 150 295 150Q315 150 315 175V310H375V175Q375 150 395 150Q415 150 415 175V310H475V175Q475 150 495 150Q515 150 515 175V310H710",width=4)+
    text(400,370,"Continuous cell cytoplasm",19)+line(550,155,550,310)+line(543,155,557,155)+line(543,310,557,310)+text(575,240,"1.00 μm",16,"start")+
    text(400,435,"Four representative projections shown; the calculation models40 identical cylinders.",15))
add(736,"Microvilli add membrane without adding a separate layer of cells","B2.3",
    "An epithelial apical patch has flat area100 μm². It develops40 cylindrical microvilli of radius0.100 μm and length1.00 μm. Each top replaces an equal circular area of the original flat patch, so the net additional area is the curved side area2πrL per microvillus. Ignore membrane thickness and end curvature.",
    [P("Calculate additional and total apical membrane area and the percentage area increase.",
       M("Additional area=40×2π×0.100×1.00."),
       A("Additional area=25.1 μm²; total area=125 μm² from unrounded125.133 μm²."),
       A("The area increases by25.1%.")),
     P("Explain why microvilli can increase uptake and distinguish their organization from separate cells or cilia.",
       R("More membrane area can contain more transport proteins/enzymes and provide more contact with the luminal material."),
       R("Microvilli are projections of one cell's continuous membrane and cytoplasm; they are not40 extra cells."),
       R("Their principal role here is increasing exchange/absorption surface, not beating to propel fluid as motile cilia do.")),
     P("Evaluate predicting an exactly25.1% increase in whole-tissue uptake.",
       R("That follows only if uptake per area and all other limiting factors stay constant."),
       R("Transporter density, substrate supply, basolateral export or blood flow may limit flux; measure uptake as well as membrane area."))],
    _villi,[checks("extra area",40*2*math.pi*.1*1,25.1327412287),checks("total area",100+40*2*math.pi*.1,125.1327412287),checks("percent area increase",40*2*math.pi*.1,25.1327412287)],
    "B2.3.7 AHL specialized surface enlargement by microvilli; side-area model supplied and tip/base accounting explicit.")
_pneumo=svg("Alveolar cell specialization at an air–tissue interface",
    text(400,80,"Alveolar air space",20)+line(100,230,310,230,width=5)+line(370,230,700,230,width=5)+
    path("M310 230V200Q340 165 370 200V230",width=3,fill="#eeeeee")+
    "".join(ellipse(x,y,5,5,"black") for x,y in [(325,206),(341,192),(356,207)])+arrow(340,175,340,130)+
    text(190,208,"Cell X",18)+text(420,193,"Cell Y",18)+arrow(405,190,370,206)+
    rect(100,285,600,40,10,fill="#eeeeee")+text(400,313,"Capillary blood",18)+
    text(400,395,"X is very thin and spread; Y contains secretory vesicles.",17))
add(737,"A cell type can cover most of an alveolus without being most of its cells","B2.3",
    "In a model alveolar lining, thin spread cells X make up40% of cells but cover95% of surface area. Cuboidal cells Y make up60% but cover5%; Y contains surfactant-secreting vesicles. After selectively suppressing Y secretion, the volume increase at a fixed inflation pressure falls from0.600 to0.200 L. The treatment does not change haemoglobin concentration.",
    [P("Identify X and Y and compare their average area per cell relative to one another.",
       A("X is typeI pneumocytes; Y is typeII pneumocytes."),
       M("Area per X cell relative to Y=(95/40)/(5/60)."),
       A("The model average area per X cell is28.5 times that per Y cell.")),
     P("Explain the different form–function adaptations and the inflation result.",
       R("Very thin typeI cells minimize the gas-diffusion distance over most of the alveolar surface."),
       R("TypeII secretory vesicles deliver surfactant, lowering surface tension and helping prevent alveolar collapse."),
       R("Less surfactant makes inflation harder; at the same pressure, volume increase falls by66.7%.")),
     P("Evaluate interpreting this result as a direct measurement of haemoglobin's oxygen affinity.",
       R("The measurement concerns mechanical inflation of the air–tissue interface, not a haemoglobin dissociation curve."),
       R("Gas transfer may be affected indirectly through altered alveolar expansion, but Hb affinity requires a separate controlled saturation-versus-oxygen measurement."))],
    _pneumo,[checks("mean cell area ratio",(95/40)/(5/60),28.5),checks("inflation reduction percent",(.6-.2)/.6*100,66.6666666667),checks("cell percentage sum",40+60,100),checks("area percentage sum",95+5,100)],
    "B2.3.8 AHL typeI/typeII pneumocyte specialization; surfactant role distinct from Hb affinity and gas diffusion itself.")
_musclecells=svg("Two schematic striated muscle organizations",
    rect(90,120,620,85,35,fill="#eeeeee")+
    "".join(line(x,125,x,200,width=1) for x in range(120,700,25))+
    "".join(ellipse(x,138,12,7,"black") for x in [145,285,460,630])+
    text(400,95,"Preparation X: one long multinucleate fibre",17)+
    path("M140 325L270 325L340 270L410 325L570 325L650 280M270 325L340 380L410 325",width=33)+
    '<path d="M140 325L270 325L340 270L410 325L570 325L650 280M270 325L340 380L410 325" stroke="#dddddd" stroke-width="29" fill="none"/>'+
    "".join(line(x,312,x,338,width=1) for x in [155,175,220,240,455,475,515,540,560])+
    "".join(ellipse(x,y,12,8,"black") for x,y in [(200,325),(340,285),(490,325),(350,372)])+
    line(255,306,255,343,width=4)+line(435,306,435,343,width=4)+
    text(400,435,"Preparation Y: branched cells with central nuclei and joining discs",17))
add(738,"Striations do not make cardiac and skeletal cells identical","B2.3",
    "X and Y are schematic striated muscle tissues. X contains very long unbranched multinucleate fibres. Y contains shorter branched cells with central nuclei and specialized joining discs. In an equal-mass sample, mitochondrial volume fraction is8% for X and30% for Y. These values are constructed and do not describe every fibre subtype.",
    [P("Identify X and Y and use two structural comparisons.",
       A("X is skeletal muscle; Y is cardiac muscle."),
       R("Skeletal fibres are typically long, unbranched and multinucleate, whereas cardiac cells are shorter/branched with central nuclei."),
       R("Cardiac joining discs connect neighbouring cells and support coordinated contraction; X is not simply a chain of separate one-nucleus cells.")),
     P("Calculate the mitochondrial volume-fraction ratio and relate it to sustained cardiac work without using it to predict ATP flux exactly.",
       M("Y:X fraction ratio=30/8."),
       A("Y has3.75 times the mitochondrial volume fraction."),
       R("A large mitochondrial investment supports repeated aerobic ATP supply; actual ATP rate also depends on substrate, oxygen and mitochondrial activity.")),
     P("Evaluate whether multinucleation alone identifies every cell as skeletal muscle.",
       R("Other cell types can be multinucleate, and a section can miss nuclei; use the combination of striations, fibre shape, branching and junctions."),
       R("Sampling different skeletal-fibre types or exercise histories may alter mitochondrial fractions, so independent matched samples are needed."))],
    _musclecells,[checks("mitochondrial fraction ratio",30/8,3.75),checks("fraction difference points",30-8,22)],
    "B2.3.9 AHL cardiac/skeletal specialization; intercalated-disc organization and central/peripheral nuclear differences scientifically grounded.")
def sat(p,p50,n=2.7):return 100*p**n/(p**n+p50**n) if p else 0
_xs=list(range(0,101,5))
add(739,"Foetal haemoglobin can load oxygen at a lower partial pressure","B3.1",
    f"Equal haemoglobin amounts are compared at the same temperature, pH and carbon dioxide. Curve F has P50=20 mmHg and curve A P50=27 mmHg; P50 is the oxygen partial pressure at50% saturation. At30 mmHg the constructed saturations are {sat(30,20):.2f}% for F and {sat(30,27):.2f}% for A. Maternal and foetal blood remain in separate vessels at the placenta.",
    [P("Identify the curve more consistent with foetal haemoglobin and quantify its saturation advantage at30 mmHg.",
       A("F is more consistent with foetal haemoglobin because its lower P50 indicates higher oxygen affinity."),
       M(f"Difference={sat(30,20):.2f}−{sat(30,27):.2f} percentage points."),
       A(f"Using the stated rounded values, F is {round(sat(30,20),2)-round(sat(30,27),2):.2f} percentage points more saturated, approximately17.9 points.")),
     P("Explain how this difference aids transfer without claiming that the blood mixes or that Hb crosses the placenta.",
       R("Foetal Hb binds oxygen effectively at the lower oxygen partial pressures available across the placental exchange surface."),
       R("Binding removes oxygen from the dissolved pool in foetal blood and helps maintain the dissolved-oxygen/partial-pressure gradient for further diffusion across the placental barrier; the two blood supplies remain separate.")),
     P("Evaluate the claim that greater affinity is always better for an adult delivering oxygen to tissues.",
       R("High affinity favours loading but can reduce unloading at a given tissue oxygen partial pressure."),
       R("Effective delivery depends on the saturation difference between loading and unloading sites, Hb amount and circulation, not affinity alone."))],
    plot("Matched foetal-like and adult-like oxygen curves",[("F: P50=20",[(p,sat(p,20)) for p in _xs]),("A: P50=27",[(p,sat(p,27)) for p in _xs])],(0,100),(0,100),"Oxygen partial pressure / mmHg","Haemoglobin saturation / %"),
    [checks("F saturation at30",sat(30,20),74.9276209928),checks("A saturation at30",sat(30,27),57.0642592737),checks("P50 defines half saturation",sat(20,20),50)],
    "B3.1.11–13 AHL foetal/adult affinity and oxygen curves; pH/CO2/temperature controlled and blood separation explicit.")
add(740,"A Bohr shift can increase oxygen unloading where carbon dioxide is high","B3.1",
    f"The same amount of adult haemoglobin is measured under low-CO2/pH7.4 conditions with P50=27 mmHg and high-CO2/pH7.2 conditions with P50=33 mmHg. At40 mmHg, saturations are {sat(40,27):.2f}% and {sat(40,33):.2f}%. Temperature is held constant. Both carbon dioxide and pH differ between the two curves.",
    [P("Identify the direction of the shift and calculate the saturation difference at40 mmHg.",
       A("Higher CO2/lower pH shifts the dissociation curve to the right, indicating lower oxygen affinity."),
       M(f"Difference={sat(40,27):.2f}−{sat(40,33):.2f}."),
       A(f"Saturation is approximately{sat(40,27)-sat(40,33):.2f} percentage points lower in high CO2.")),
     P("Explain the benefit in actively respiring tissues, distinguishing CO2 binding from O2 binding.",
       R("Respiring tissues release CO2; reduced affinity promotes oxygen dissociation where oxygen demand is high."),
       R("CO2 can bind allosterically at sites distinct from the oxygen-binding haem sites; it does not simply occupy all the same sites as oxygen.")),
     P("Evaluate whether the comparison separates a direct CO2 effect from a pH effect.",
       R("It does not: CO2 and pH change together, so their individual contributions are confounded."),
       R("Compare CO2 levels at controlled buffered pH and pH levels at controlled CO2, with equal Hb and temperature, to separate effects."))],
    plot("A constructed Bohr shift at matched haemoglobin concentration",[("Low CO2; pH7.4",[(p,sat(p,27)) for p in _xs]),("High CO2; pH7.2",[(p,sat(p,33)) for p in _xs])],(0,100),(0,100),"Oxygen partial pressure / mmHg","Haemoglobin saturation / %"),
    [checks("low CO2 saturation40",sat(40,27),74.2922662596),checks("high CO2 saturation40",sat(40,33),62.7008416782),truth("right shift lowers saturation",sat(40,33)<sat(40,27))],
    "B3.1.11–13 AHL Bohr shift and allosteric CO2 binding; coupled pH/CO2 design explicitly evaluated.")
add(741,"A sigmoid curve carries information about cooperative binding","B3.1",
    f"Constructed oxygen-binding curves C and N have the same P50=27 mmHg and the same maximum capacity. C is cooperative haemoglobin-like binding and N is an independent-site comparison. At10 mmHg their saturations are {sat(10,27):.2f}% and {sat(10,27,1):.2f}%; at40 mmHg they are {sat(40,27):.2f}% and {sat(40,27,1):.2f}%. No binding equation is required.",
    [P("Compare C and N at the two pressures, and explain why identical P50 values do not imply identical curve shapes.",
       A(f"At10 mmHg C is less saturated ({sat(10,27):.2f}% versus{sat(10,27,1):.2f}%), but at40 it is more saturated ({sat(40,27):.2f}% versus{sat(40,27,1):.2f}%)."),
       R("P50 specifies one point, not the full response at other pressures.")),
     P("Explain the S-shaped form of C in terms of subunit interactions.",
       R("Binding of an initial oxygen molecule alters haemoglobin conformation."),
       R("This increases the tendency of remaining haem groups to bind oxygen, producing a steep central part of the curve."),
       R("At high oxygen pressure most sites are occupied, so the curve levels off; the plateau is not evidence of unlimited extra binding sites.")),
     P("Calculate C's percentage-point saturation decrease from40 to10 mmHg and explain why it is not itself a volume of oxygen.",
       M(f"Subtract {sat(10,27):.2f}% from{sat(40,27):.2f}%."),
       A(f"From the supplied rounded values, the decrease is{round(sat(40,27),2)-round(sat(10,27),2):.2f} percentage points, approximately67.9."),
       R("Converting a fractional saturation change to oxygen volume requires the amount of haemoglobin and its oxygen capacity."))],
    plot("Same P50, different binding behaviour",[("C: cooperative",[(p,sat(p,27)) for p in _xs]),("N: independent",[(p,sat(p,27,1)) for p in _xs])],(0,100),(0,100),"Oxygen partial pressure / mmHg","Binding-site saturation / %"),
    [checks("C atP50",sat(27,27),50),checks("N atP50",sat(27,27,1),50),truth("low C belowN",sat(10,27)<sat(10,27,1)),truth("high C aboveN",sat(40,27)>sat(40,27,1))],
    "B3.1.11/13 AHL cooperative haem binding and saturation curves; independent-site comparator supplied, not a required Hill-equation derivation.")
add(742,"Oxygen content depends on both affinity and haemoglobin amount","B3.1",
    f"Blood models X and Y are compared at the same temperature and CO2. X contains100 g Hb L−1 with P50=27 mmHg; Y contains120 g Hb L−1 with P50=35 mmHg. Each gram of fully saturated Hb binds1.34 mL oxygen. At40 mmHg, fractional saturations are {sat(40,27)/100:.4f} and {sat(40,35)/100:.4f}. Ignore dissolved oxygen for the calculation. These are models, not clinical diagnostic data.",
    [P("Distinguish which model has higher affinity and which has higher maximum oxygen capacity per litre.",
       A("X has higher affinity because its P50 is lower; Y has more Hb and hence higher full-saturation capacity."),
       M("Full capacities=Hb concentration×1.34."),
       A("X capacity=134 mL L−1; Y capacity=160.8 mL L−1.")),
     P("Calculate oxygen bound per litre at40 mmHg using the supplied rounded fractional saturations.",
       M("Bound content=full capacity×fractional saturation."),
       A(f"X≈{134*round(sat(40,27)/100,4):.2f} and Y≈{160.8*round(sat(40,35)/100,4):.2f} mL L−1; accept small differences from unrounded curves."),
       R("More Hb in Y partly compensates for lower affinity, but does not guarantee higher content at every oxygen pressure.")),
     P("Evaluate identifying foetal blood from a single measured oxygen content.",
       R("Content confounds Hb amount, saturation and oxygen conditions; a high content alone is not a measurement of high affinity."),
       R("Compare controlled dissociation curves/P50 and Hb concentration, rather than assigning developmental identity from one content value."))],
    plot("Affinity curves separated from haemoglobin concentration",[("X:100 g/L; P50=27",[(p,sat(p,27)) for p in _xs]),("Y:120 g/L; P50=35",[(p,sat(p,35)) for p in _xs])],(0,100),(0,100),"Oxygen partial pressure / mmHg","Haemoglobin saturation / %"),
    [checks("X capacity",100*1.34,134),checks("Y capacity",120*1.34,160.8),checks("X content40",134*round(sat(40,27)/100,4),99.5486),checks("Y content40",160.8*round(sat(40,35)/100,4),94.74336)],
    "B3.1.11–13 AHL affinity/capacity distinctions with Hb developmental-identity confounding; oxygen-capacity constant supplied.")
_fluid=svg("A simplified local tissue-fluid budget",
    rect(100,110,600,65,20,fill="#eeeeee")+arrow(125,142,675,142)+text(400,95,"Blood capillary",18)+
    arrow(250,175,250,260)+text(215,230,"20",18)+arrow(545,260,545,175)+text(580,230,"17",18)+
    text(400,290,"Tissue fluid",20)+rect(225,340,430,50,20)+arrow(250,365,620,365)+
    arrow(400,305,400,340)+text(440,325,"3",18)+path("M480 345l20 20l-20 20M545 345l20 20l-20 20")+
    text(400,432,"Arrows: fluid routes; numbers: mL min−1 in the supplied steady model.",16))
add(743,"Lymphatic drainage closes a tissue-fluid budget","B3.2",
    "A simplified steady local model has20 mL min−1 leaving blood capillaries for tissue fluid,17 returning directly to blood and3 entering lymph vessels. These rates are supplied aggregate exchanges, not a claim that every real capillary has this exact pattern. A partial lymph blockage lowers drainage to1 mL min−1 while other rates initially stay unchanged. Plasma proteins are largely retained in blood in the unblocked model.",
    [P("Verify the initial balance and calculate the initial accumulation rate and one-hour accumulation after blockage, if rates remained fixed.",
       M("Steady balance:20−17−3=0. After blockage:20−17−1."),
       A("Initial accumulation is2 mL min−1; conditional one-hour accumulation is120 mL.")),
     P("Explain capillary exchange, protein retention and the lymphatic return route.",
       R("Capillary walls are thin and allow exchange of water and small solutes between blood and tissue fluid."),
       R("Retained plasma proteins favour water retention/return toward blood by osmotic effects; pressure also affects outward movement."),
       R("Excess tissue fluid enters thin-walled lymph vessels with gaps and valves, then returns to blood circulation rather than being permanently lost.")),
     P("Evaluate extrapolating the initial model for many hours and predict the effect of increased protein leakage.",
       R("Accumulated fluid changes tissue pressure and exchange rates, so a fixed2 mL min−1 long-term prediction is unlikely to remain accurate."),
       R("Loss of plasma proteins into tissue reduces the osmotic difference favouring water retention in blood and can promote tissue-fluid accumulation; consider the altered pressures too."))],
    _fluid,[checks("initial balance",20-17-3,0),checks("blocked accumulation",20-17-1,2),checks("conditional hourly accumulation",(20-17-1)*60,120)],
    "B3.2.11–13 AHL tissue-fluid formation, protein effects and lymphatic return; simplified steady budget explicitly distinguished from a universal Starling claim.")
_heartdata=[(0,5,10,80),(.1,15,12,78),(.2,100,10,85),(.3,120,8,120),(.4,70,8,95),(.5,5,10,85),(.6,5,10,80)]
add(744,"Valve positions follow pressure differences rather than a timetable alone","B3.2",
    "The graph gives left-atrial, left-ventricular and aortic pressures during one constructed cardiac cycle. At0.10 s they are12,15 and78 mmHg; at0.20 s10,100 and85; at0.40 s8,70 and95; at0.50 s10,5 and85. End-diastolic ventricular volume is120 mL and end-systolic volume50 mL. Heart rate is75 min−1. Use cardiac output=stroke volume×heart rate.",
    [P("Deduce mitral and aortic valve states at0.20 and0.50 s from the pressure differences.",
       R("At0.20 s ventricular pressure exceeds atrial and aortic pressures, closing the mitral valve and opening the aortic valve."),
       R("At0.50 s atrial pressure exceeds ventricular while aortic pressure exceeds ventricular, opening the mitral valve and closing the aortic valve.")),
     P("Explain why both valves can be closed at0.10 and0.40 s and identify the event initiating the heartbeat.",
       R("At both times ventricle pressure exceeds atrium but remains below aorta; neither pressure gradient opens its corresponding forward valve."),
       R("The sinoatrial node initiates the heartbeat; valves respond passively to pressure differences rather than actively pumping blood.")),
     P("Calculate stroke volume and cardiac output, and distinguish them from ejection pressure.",
       M("Stroke volume=120−50=70 mL; output=70×75."),
       A("Cardiac output=5 250 mL min−1=5.25 L min−1."),
       R("Pressure is force per area, whereas stroke volume and output measure volume per beat and per time; pressure alone does not determine either."))],
    plot("Constructed pressures on the left side of the heart",[("Left ventricle",[(t,v) for t,v,a,o in _heartdata]),("Left atrium",[(t,a) for t,v,a,o in _heartdata]),("Aorta",[(t,o) for t,v,a,o in _heartdata])],(0,.6),(0,140),"Time in cycle / s","Pressure / mmHg",xticks=[0,.1,.2,.3,.4,.5,.6]),
    [checks("stroke volume",120-50,70),checks("cardiac output L min",(120-50)*75/1000,5.25),truth("both closed0.1",12<15<78),truth("both closed0.4",8<70<95)],
    "B3.2.15–16 AHL cardiac architecture/cycle/pressure; equality points are not used for unique valve-state decisions.")
_circulation=svg("Two simplified circulation circuits",
    rect(90,120,150,55,12)+text(165,154,"Pump P",18)+rect(90,290,150,55,12)+text(165,324,"Body",18)+rect(290,205,130,55,12)+text(355,239,"Gills",18)+
    arrow(240,147,355,205)+arrow(355,260,240,315)+arrow(90,315,90,175)+
    rect(510,105,175,50,12)+text(597,137,"Lungs",18)+rect(510,340,175,50,12)+text(597,372,"Body",18)+
    rect(455,220,120,55,12)+text(515,253,"Pump Q",18)+rect(650,220,120,55,12)+text(710,253,"Pump R",18)+
    arrow(515,220,550,155)+arrow(650,155,710,220)+arrow(710,275,650,340)+arrow(550,340,515,275)+
    text(250,425,"Circuit1",18)+text(615,425,"Circuit2",18))
add(745,"Two heart passages can restore pressure between two capillary beds","B3.2",
    "Circuit1 represents a bony fish: one pump sends blood through gills, then body, then back to the pump. Circuit2 represents a mammal: pump Q sends blood to lungs and pump R sends it to body. Q and R are the two sides of one heart, not two separate organs. Vessel directions are shown. Constructed pressures after a gas-exchange bed are12 mmHg in circuit1 and25 mmHg in circuit2's pulmonary route; mammalian systemic arterial pressure is120 mmHg.",
    [P("Identify single and double circulation, and identify Q and R as right or left heart.",
       A("Circuit1 is single circulation; circuit2 is double circulation."),
       A("Q is right heart to lungs; R is left heart to body.")),
     P("Trace one mammalian red cell from vena cava to aorta, naming the chambers and pulmonary vessels in order.",
       R("Vena cava→right atrium→right ventricle→pulmonary artery→lung capillaries."),
       R("Then pulmonary vein→left atrium→left ventricle→aorta; valves and septum maintain directed, separated flow.")),
     P("Explain the pressure advantage and calculate the stated systemic:pulmonary pressure ratio without treating it as an oxygen-concentration ratio.",
       R("A second passage through the heart can raise pressure again after pulmonary capillaries, supplying high-pressure systemic flow while keeping pulmonary pressure lower."),
       M("Use120/25."),
       A("The supplied pressure ratio is4.80:1."),
       R("Pressure is not oxygen concentration, and these values do not imply that fish blood lacks oxygen or that the two mammalian sides normally mix."))],
    _circulation,[checks("systemic pulmonary pressure ratio",120/25,4.8),checks("pump passages single",1,1),checks("pump passages double",2,2)],
    "B3.2.14–15 AHL single/double circulation and directed mammalian heart flow; simple circuit diagrams are explicitly allowed.")
_phloem=svg("A sieve-tube element beside a companion cell",
    rect(190,95,190,280,15)+line(195,145,375,145,width=5)+line(195,325,375,325,width=5)+
    "".join(ellipse(x,145,4,4,"white")+ellipse(x,325,4,4,"white") for x in range(215,365,25))+
    rect(430,95,170,280,15)+ellipse(520,170,30,25,fill="#eeeeee")+
    "".join(ellipse(x,y,13,7,fill="#eeeeee") for x,y in [(465,240),(550,255),(475,295),(555,320)])+
    "".join(line(380,y,430,y,width=3) for y in [200,220,240])+
    text(285,417,"Sieve-tube element",17)+text(515,417,"Companion cell",17)+text(400,70,"Connecting channels are plasmodesmata.",16))
add(746,"Root pressure and phloem loading use living cells in different ways","B3.2",
    "At night in humid air, a rooted plant develops positive xylem pressure40 kPa. A reversible root ATP-production inhibitor lowers it to10 kPa; after washing out the inhibitor it recovers to35 kPa. Transpiration remains very low throughout. A separate diagram shows a phloem sieve-tube element and companion cell. These are not the same conduits as xylem vessels.",
    [P("Calculate the initial pressure reduction and explain a mechanism for positive root pressure at low transpiration.",
       M("Reduction=(40−10)/40×100."),
       A("Pressure decreases by75.0%."),
       R("Active mineral-ion transport into root xylem increases solute accumulation, drawing water inward by osmosis and generating positive pressure when transpiration pull is small.")),
     P("Explain three phloem form–function features, distinguishing sieve elements from companion cells.",
       R("Sieve plates with pores and reduced cytoplasm/organelles ease sap flow between sieve-tube elements."),
       R("Mature sieve elements lack a nucleus, while living companion cells have many mitochondria to support their metabolic/transport roles."),
       R("Plasmodesmata connect companion cells with sieve elements, supporting loading/unloading and maintenance.")),
     P("Evaluate the inhibitor evidence and the claim that all upward xylem flow is ATP-pumped by dead vessels.",
       R("Partial recovery supports a reversible energy-dependent root process, but broad ATP inhibition can affect several living-cell functions; monitor viability and ion transport."),
       R("Mature xylem conduits are dead; most daytime transpiration flow is pulled by cohesion-tension, while living root cells can create root pressure under these conditions."))],
    _phloem,[checks("pressure decrease percent",(40-10)/40*100,75),checks("pressure recovery fraction",35/40,.875)],
    "B3.2.17–18 AHL root pressure/phloem adaptations; no formal D2.3 water-potential calculation, and dead xylem is not an ATP pump.")
def sarco(x,y,L,label):
    left=x;right=x+L*130;mid=(left+right)/2
    b=line(left,y-55,left,y+55,width=4)+line(right,y-55,right,y+55,width=4)+line(mid-.8*130,y,mid+.8*130,y,width=9)
    for yy in [y-28,y+28]:
        b+=line(left,yy,left+130,yy,width=3)+line(right-130,yy,right,yy,width=3)
    b+=text(mid,y+88,label,17)
    return b
add(747,"Shorter sarcomeres do not require shorter actin or myosin filaments","B3.3",
    "The same model sarcomere changes from length3.00 μm to2.20 μm. Thick filaments are1.60 μm long and each thin filament extends1.00 μm inward from its Z line in both states. All filaments are centred/aligned as drawn. Use the central region lacking thin filament length=L−2.00 μm for these two states.",
    [P("Calculate shortening percentage and the central thin-filament-free lengths.",
       M("Shortening=(3.00−2.20)/3.00×100; central length=L−2.00."),
       A("Sarcomere shortening is26.7%; central lengths decrease from1.00 to0.200 μm.")),
     P("Use the geometry to explain sliding-filament contraction rather than filament shortening.",
       R("Thin filaments slide farther between the thick filaments, increasing overlap and bringing Z lines closer."),
       R("Thick and thin filament lengths stay1.60 and1.00 μm; it is their relative position and sarcomere length that change.")),
     P("Explain why relaxation/stretching involves titin and antagonistic muscles rather than active pushing by a contracted muscle.",
       R("Titin provides elastic recoil after stretch and helps prevent sarcomere overstretching."),
       R("Muscles generate pulling force when they contract; an antagonist can pull a bone/body part in the opposite direction and stretch the first muscle."),
       R("Reduced activation permits relaxation but does not make the same muscle actively push its attachments apart."))],
    svg("Two accurately scaled model sarcomere lengths",sarco(190,160,3,"State1:3.00 μm")+sarco(242,350,2.2,"State2:2.20 μm")+
        line(80,65,145,65,width=3)+text(112,50,"0.500 μm",15)+text(690,170,"Thick",16)+text(690,195,"Thin above/below",14)),
    [checks("shortening percent",(3-2.2)/3*100,26.6666666667),checks("central gap initial",3-2,1),checks("central gap final",2.2-2,.2),checks("total I-region initial",3-1.6,1.4),checks("total I-region final",2.2-1.6,.6)],
    "B3.3.2–3 entirely AHL sliding filaments, titin and antagonists; filament lengths and scale are consistent.")
_motor=svg("Three separately recruited motor units",
    "".join(ellipse(150,125+j*110,28,23)+text(150,131+j*110,f"N{j+1}",16)+line(178,125+j*110,310,125+j*110)+
        "".join(arrow(310,125+j*110,465,95+j*110+k*30)+rect(470,82+j*110+k*30,190,24,10,fill="#eeeeee") for k in range(j+2)) for j in range(3))+
    text(400,462,"Each neuron branches to its own muscle fibres; no fibre is shared between units.",15))
add(748,"Recruiting whole motor units gives a stepped force record","B3.3",
    "In a simplified preparation, increasing stimulus level recruits motor units in a fixed order. At levels0,1,2,3 and4 the total force is0,12,32,62 and62 N. Each newly recruited unit adds a constant force, and already recruited units retain their force; firing frequency and muscle length are fixed. The schematic shows three motor neurons and their separate fibre groups, but fibre drawing count is not a force calibration.",
    [P("Deduce the force contribution of each unit and explain the final plateau.",
       M("Subtract successive total forces:12−0,32−12,62−32."),
       A("Unit forces are12,20 and30 N; level4 adds no further force."),
       R("Under the stated model, all available units have been recruited by level3, so further stimulus amplitude cannot recruit another unit.")),
     P("Explain the structural meaning of a motor unit and why whole-muscle force can be graded.",
       R("A motor unit is one motor neuron and the skeletal muscle fibres it innervates, connected through neuromuscular junctions."),
       R("Recruiting additional units increases the number of active fibres; an all-or-none response of an individual unit does not make the whole muscle's force all-or-none.")),
     P("Evaluate whether exactly42 N can be selected by stimulus level in this fixed-order model.",
       A("No tested/modelled recruitment state gives42 N: the successive states are0,12,32 and62 N."),
       R("Although12+30=42 arithmetically, fixed recruitment order does not permit unit3 without unit2."),
       R("Real muscle can also alter firing frequency, length and activation pattern; the restricted model does not prove42 N is impossible in every physiological situation."))],
    _motor,[checks("unit1 force",12-0,12),checks("unit2 force",32-12,20),checks("unit3 force",62-32,30),checks("total force",12+20+30,62),truth("42 absent fixed states",42 not in [0,12,32,62])],
    "B3.3.4 AHL motor units/recruitment; force increments supplied, not inferred from illustrative fibre counts.")
_lever=svg("A simplified hip-lever model with perpendicular forces",
    path("M160 205l-25 45h50z",fill="#eeeeee")+line(160,205,680,205,width=7)+
    arrow(212,300,212,140)+text(265,140,"Muscle force",18)+arrow(680,160,680,325)+text(680,355,"Load60 N",18)+
    line(160,100,212,100)+line(160,93,160,107)+line(212,93,212,107)+text(186,83,"4.0 cm",15)+
    line(160,390,680,390)+line(160,382,160,398)+line(680,382,680,398)+text(420,420,"40.0 cm",17)+
    text(115,290,"Hip pivot",17)+text(400,462,"Lever lengths are scaled; this is a mechanical model, not an anatomical bone drawing.",15))
add(749,"A small muscle moment arm requires a large force at a joint","B3.3",
    "A simplified static hip lever has a60.0 N load acting40.0 cm from the pivot and muscle force acting4.00 cm from it. Both forces are perpendicular to the lever and act in opposite rotational directions. Ignore limb weight. Use moment=force×perpendicular distance and equate opposing moments. The biological joint is the ball-and-socket connection of the femur with the pelvis.",
    [P("Calculate load moment and the muscle force needed for equilibrium.",
       M("Load moment=60.0×0.400 N m; muscle force×0.0400 equals that moment."),
       A("Load moment=24.0 N m and muscle force=600 N.")),
     P("Explain the distinct roles of tendons, ligaments, cartilage and synovial fluid in the actual hip.",
       R("Tendons transmit pulling force from muscle to bone; ligaments connect bones and help limit excessive joint displacement."),
       R("Articular cartilage and synovial fluid reduce friction and support smooth movement between the femoral head and pelvic socket.")),
     P("A goniometer records maximum flexion120° before a restriction and85° after. Calculate the change and evaluate the lever's anatomical limits.",
       A("The recorded range is reduced by35°, or29.2% relative to120°."),
       R("A ball-and-socket hip moves in several planes; one flexion angle does not measure all its range of motion."),
       R("Real moment arms vary with joint angle and several muscles/limb weight contribute; the600 N result belongs to the stated static model, not a full anatomical prediction."))],
    _lever,[checks("load moment Nm",60*.4,24),checks("muscle force N",60*.4/.04,600),checks("angle decrease",120-85,35),checks("angle percentage reduction",(120-85)/120*100,29.1666666667)],
    "B3.3.5–7 entirely AHL skeleton leverage, human hip and range-of-motion measurement; force arms perpendicular and units supplied.")
add(750,"Streamlining can reduce the power needed for a migration speed","B3.3",
    "Equal-volume models of a marine mammal's streamlined body and a less-streamlined comparison are towed at the same speeds. At2.00 m s−1 their drag forces are40.0 and65.0 N. Use mechanical power against drag=drag force×speed. This mechanical model excludes muscle efficiency, buoyancy changes and metabolic maintenance. Real marine mammals propel themselves using muscular body/tail movements and use flippers for control.",
    [P("Calculate towing powers at2.00 m s−1 and the percentage power reduction associated with the streamlined shape.",
       M("Power=force×speed."),
       A("Powers are80.0 W and130 W."),
       A("Reduction=(130−80)/130×100=38.5%.")),
     P("Relate two marine-mammal features to swimming and explain why muscle action must be coordinated rather than a muscle pushing back on its own.",
       R("Streamlining reduces resistance; modified limbs/flippers assist steering/stability, and muscular tail/body movements produce propulsion."),
       R("Muscles pull on contraction; coordinated opposing muscle groups can reverse movement while elastic structures assist return, rather than one muscle actively pushing its attachments apart.")),
     P("Evaluate extrapolating the power difference to a38.5% reduction in total migration energy.",
       R("Only drag power at a fixed speed is compared; total energy also includes duration, metabolic maintenance and conversion efficiency."),
       R("Real animals change speed, depth, behaviour and propulsive efficiency; measure whole-animal energy use and travel conditions before making that quantitative claim."))],
    plot("Constructed tow-test resistance curves",[("Streamlined",[(v,10*v*v) for v in [0,.5,1,1.5,2,2.5,3]]),("Comparison",[(v,16.25*v*v) for v in [0,.5,1,1.5,2,2.5,3]])],(0,3),(0,160),"Tow speed / m s−1","Drag force / N"),
    [checks("streamlined power W",40*2,80),checks("comparison power W",65*2,130),checks("power saving percent",(130-80)/130*100,38.4615384615)],
    "B3.3.3/9–10 entirely AHL muscular movement and marine-mammal swimming adaptations; towing mechanics formula explicitly supplied.")

def finish():
    assert len(Q)==50 and len({q["id"] for q in Q})==50 and len({q["title"] for q in Q})==50
    assert [q["number"] for q in Q]==list(range(701,751))
    assert collections.Counter(q["level"] for q in Q)=={"sl":20,"ahl":30}
    for q in Q:
        for key in ["title","stem","diagramCaption","answerSummary"]:q[key]=polish(q[key])
        for key in ["method","notes"]:q["verification"][key]=polish(q["verification"][key])
        for p in q["parts"]:p["prompt"]=polish(p["prompt"])
        for g in q["markScheme"]:
            for step in g["steps"]:step["text"]=polish(step["text"])
        assert 6<=q["marks"]<=14
        assert q["marks"]==sum(p["marks"] for p in q["parts"])
        assert q["syllabusCode"] in SUB and q["subtopic"]==SUB[q["syllabusCode"]]
        assert q["number"]==q["source"]["question"]==int(q["id"][-3:])
        for p,g in zip(q["parts"],q["markScheme"],strict=True):
            assert p["label"]==g["part"] and p["marks"]==len(g["steps"])
        ET.fromstring(q["diagramSvg"])
        assert len(q["diagramSvg"])<=300000 and "viewBox=" in q["diagramSvg"]
        assert not re.search(r"<(?:script|foreignObject|iframe|object|embed|image|style|animate|set)\b|\bon\w+\s*=|(?:href|src)\s*=|url\s*\(|<!DOCTYPE|<!ENTITY",q["diagramSvg"],re.I)
        assert "constructed" in q["stem"] and "not micrographs" in q["stem"]
    out=ROOT/"content/ib/biology-2026-expansion/form-function.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(Q,ensure_ascii=False,indent=2)+"\n",encoding="utf8",newline="\n")
    report={"batch":"Form and function","firstAssessment":2025,"questions":50,
       "status":"Author scientific/computational self-review passed; separate independent review required before release.",
       "sha256":hashlib.sha256(out.read_bytes()).hexdigest(),"sourceGuide":GUIDE,"sourceSpecimen":SPECIMEN,
       "guideAccess":"Corrected March2024 guide reached via ordinary Biology-guide link on official2027 examiner instructions; current statement boundaries cross-checked with repository blueprint.",
       "counts":{"sl":20,"ahl":30,"hard":50,"diagrams":50,"minimumMarks":min(q["marks"] for q in Q),"maximumMarks":max(q["marks"] for q in Q),"marks":sum(q["marks"] for q in Q),"scientificNumericAssertions":sum(len(a["checks"]) for a in AUD)},
       "originality":"Fifty distinct original problem structures, constructed data and precise vector schematics; no official question wording or actual micrographs reproduced.",
       "scopePolicy":"SL means shared2025 content. Every AHL question requires at least one additional statement-level concept; difficult arithmetic alone never determines level.",
       "records":AUD,"limitations":["AI author scientific/computational checks are not moderation by human IB examiners.","Difficulty is editorial and not calibrated with student performance.","Separate schema, rendering, scientific independent review and release hashes remain required."]}
    rp=ROOT/"docs/ib-2026-biology/form-function-author-review.json"
    rp.parent.mkdir(parents=True,exist_ok=True)
    rp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8",newline="\n")
    print(json.dumps(report["counts"]))

if __name__=="__main__":finish()
