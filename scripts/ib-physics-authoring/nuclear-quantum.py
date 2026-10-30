"""Original Theme E practice, authored from syllabus skills, not question-bank texts.
Deterministic standard-library builder. All diagrams and data are constructed here.
"""
import collections, html, json, math, re, xml.etree.ElementTree as ET
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT, CHECKS = [], []
FAMILIES = collections.Counter()
NAMES = ["Structure of the atom", "Quantum physics", "Radioactive decay", "Fission", "Fusion and stars"]
H, C, E, ME, U, K = 6.63e-34, 3.00e8, 1.60e-19, 9.11e-31, 1.66e-27, 8.99e9
BLUE, RED, GREEN = "#1d4ed8", "#b91c1c", "#047857"
def check(label, value, expected, relative=1e-9):
    assert math.isclose(value, expected, rel_tol=relative, abs_tol=abs(expected)*relative+1e-300), (label,value,expected)
    CHECKS.append(label)
def tex(value, digits=3):
    s=f"{value:.{digits}g}"
    if "e" in s:
        a,b=s.split("e");return a+r"\times10^{"+str(int(b))+"}"
    return s
def qty(value,unit,digits=3):return "$"+tex(value,digits)+r"\,\mathrm{"+unit+"}$"
def table(headings,rows):
    return "\n\n| "+" | ".join(headings)+" |\n| "+" | ".join(["---"]*len(headings))+" |\n"+"\n".join("| "+" | ".join(map(str,row))+" |" for row in rows)
def part(prompt,*steps):return prompt,[{"code":code,"text":body} for code,body in steps]
def text(x,y,s,size=15,color="#172033",anchor="middle"):
    return f'<text x="{x:.2f}" y="{y:.2f}" font-family="Arial, sans-serif" font-size="{size}" fill="{color}" text-anchor="{anchor}">{html.escape(str(s))}</text>'
def line(x1,y1,x2,y2,color="#172033",width=2,dash=False):
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="6 5"' if dash else '')+'/>'
def arrow(x1,y1,x2,y2,color=BLUE):
    a=math.atan2(y2-y1,x2-x1);p=[(x2,y2),(x2-10*math.cos(a-.45),y2-10*math.sin(a-.45)),(x2-10*math.cos(a+.45),y2-10*math.sin(a+.45))]
    return line(x1,y1,x2,y2,color,3)+f'<polygon points="{" ".join(f"{x:.2f},{y:.2f}" for x,y in p)}" fill="{color}"/>'
def svg(body,title,w=660,h=390):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(title,quote=True)}"><rect width="{w}" height="{h}" fill="white"/>{body}</svg>'
def graph(points,xmax,ymax,xlabel,ylabel,title,xmin=0,ymin=0,extra=None,connect=True,legend=None):
    top=105 if legend else 75
    X=lambda x:85+490*(x-xmin)/(xmax-xmin);Y=lambda y:310-(310-top)*(y-ymin)/(ymax-ymin)
    b=text(330,27,title,size=17)
    if legend:
        for i,(label,col) in enumerate(legend):
            x=85+i*(490/len(legend))
            b+=line(x,55,x+25,55,col,2.5)+text(x+33,59,label,size=12,anchor="start")
    for i in range(6):
        x=xmin+(xmax-xmin)*i/5;y=ymin+(ymax-ymin)*i/5
        b+=line(X(x),top,X(x),310,"#e2e8f0",1)+text(X(x),333,f"{x:.3g}",size=12)
        b+=line(85,Y(y),575,Y(y),"#e2e8f0",1)+text(74,Y(y)+4,f"{y:.3g}",size=12,anchor="end")
    b+=line(85,top,85,310)+line(85,310,575,310)+text(330,371,xlabel)+text(85,top-18,ylabel,anchor="start")
    for series,col in [(points,BLUE)]+(extra or []):
        if connect:b+=f'<polyline points="{" ".join(f"{X(x):.2f},{Y(y):.2f}" for x,y in series)}" fill="none" stroke="{col}" stroke-width="{1.5 if legend and len(legend)>2 else 2.5}"/>'
        if len(series)<=25:
            for x,y in series:b+=f'<circle cx="{X(x):.2f}" cy="{Y(y):.2f}" r="3.5" fill="{col}"/>'
    return svg(b,title)
def levels(values,title="Atomic energy levels",transitions=()):
    b=text(330,25,title,size=17)+text(330,52,"Vertical spacing is schematic; energies are labelled.",size=13)
    ys={name:325-i*42 for i,(name,value) in enumerate(values)}
    for name,value in values:
        y=ys[name];b+=line(110,y,450,y,BLUE)+text(90,y+4,name,anchor="end")+text(470,y+4,f"{value:.4g} eV",anchor="start")
    for i,(initial,final) in enumerate(transitions):b+=arrow(180+i*55,ys[initial],180+i*55,ys[final],RED)
    return svg(b,title)
def scattering(theta,title="Photon scattering from a stationary electron"):
    a=math.radians(theta);ox,oy=340,235
    b=text(330,25,title,size=16)+text(330,52,"Schematic; angle measured from the incident direction.",size=13)
    b+=arrow(60,oy,310,oy)+text(155,oy+28,"incident photon",color=BLUE)
    b+=line(ox,oy,600,oy,"#64748b",1,True)+text(570,oy+25,"forward",size=13)
    b+=arrow(ox,oy,ox+175*math.cos(a),oy-175*math.sin(a),RED)
    b+=line(465,80,490,80,RED,3)+text(498,85,"scattered photon",size=14,color=RED,anchor="start")
    b+=f'<circle cx="{ox}" cy="{oy}" r="7" fill="#172033"/><path d="M {ox+55} {oy} A 55 55 0 0 0 {ox+55*math.cos(a):.2f} {oy-55*math.sin(a):.2f}" fill="none" stroke="#172033"/>'
    b+=text(ox+83*math.cos(a/2),oy-83*math.sin(a/2),f"{theta}°",size=14)+text(330,350,"The recoil electron is not drawn.",size=13)
    return svg(b,title)
def reactor(title="Simplified reactor energy transfers"):
    b=text(330,30,title,size=17)
    for x,y,w,h,label in [(30,145,130,65,"Reactor core"),(245,145,150,65,"Heat exchanger"),(480,145,150,65,"Turbine + generator")]:
        b+=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#eef4fb" stroke="#34506b"/>'+text(x+w/2,y+37,label,size=13)
    b+=arrow(160,177,245,177)+arrow(395,177,480,177)+text(200,130,"heat",size=13)+text(435,130,"steam",size=13)
    b+=arrow(555,210,555,305)+text(555,332,"electrical output",size=13)+arrow(320,210,320,305,RED)+text(320,332,"heat rejected",size=13,color=RED)
    b+=text(330,365,"Block diagram; not a construction drawing.",size=12)
    return svg(b,title)
def add(section,family,variant,title,stem,parts=None,options=None,reason=None,level="core",difficulty="medium",data=False,diagram=None,solution=None):
    stem=stem.replace(r"\n\n","\n\n")
    n=len(OUT)+1
    q={"id":f"ib-phy-e-{n:03}","subject":"physics-hl","topicId":"nuclear-quantum","collectionId":"physics-nuclear-quantum","number":n,"title":title,"subtopic":NAMES[section-1],"syllabusCode":f"E.{section}","level":level,"questionType":"multiple-choice" if options else ("data-based" if data else "structured"),"difficulty":difficulty,"calculator":True,"stem":stem,"source":{"document":"Independent syllabus-authored practice","question":n},"verification":{"method":"author reasoning, conservation and deterministic numerical checks","notes":f"Skill family: {family}. Variant {variant+1} of 4. Original constructed context/data and diagrams. Author checked signs, units, assumptions and allocations; not independent exam moderation."},"status":"published"}
    if options:
        assert len(options)==4 and len(set(options))==4,(n,options)
        correct=options[0];shift=n%4;ordered=options[shift:]+options[:shift];letter="ABCD"[ordered.index(correct)]
        q.update(options=[{"label":label,"text":value} for label,value in zip("ABCD",ordered)],correctOption=letter,marks=1,parts=[],markScheme=[{"part":"","steps":[{"code":"A1","text":f"Option {letter}. {reason}"}]}])
    else:
        assert parts;ps=[];schemes=[]
        for i,(prompt,steps) in enumerate(parts):
            label=chr(97+i);marks=sum(int(step["code"][1:]) for step in steps)
            ps.append({"label":label,"prompt":prompt,"marks":marks});schemes.append({"part":label,"steps":steps})
        q.update(parts=ps,markScheme=schemes,marks=sum(p["marks"] for p in ps))
    if diagram:q["diagramSvg"]=diagram
    if solution:q["markSchemeDiagramSvg"]=solution
    OUT.append(q);FAMILIES[family]+=1
def save(final=False):
    assert len({q["stem"] for q in OUT})==len(OUT)
    for q in OUT:
        assert q["number"]==int(q["id"][-3:])
        assert q["marks"]==sum(int(s["code"][1:]) for g in q["markScheme"] for s in g["steps"])
        if q["parts"]:assert q["marks"]==sum(p["marks"] for p in q["parts"])
        for key in ("diagramSvg","markSchemeDiagramSvg"):
            if key in q:
                ET.fromstring(q[key]);assert "viewBox=" in q[key]
                assert not re.search(r"<(?:script|image|style|foreignObject)|\bon\w+\s*=|\b(?:href|src)\s*=|url\s*\(",q[key],re.I)
        for body in [q["stem"]]+[p["prompt"] for p in q["parts"]]+[s["text"] for g in q["markScheme"] for s in g["steps"]]:
            assert not re.search(r"[\x00-\x09\x0b-\x1f]",body),(q["id"],repr(body))
    output=ROOT/"content/ib/physics-hl/nuclear-quantum.json";output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    stats={"questions":len(OUT),"families":len(FAMILIES),"questionDiagrams":sum("diagramSvg" in q for q in OUT),"schemeDiagrams":sum("markSchemeDiagramSvg" in q for q in OUT),"types":dict(collections.Counter(q["questionType"] for q in OUT)),"difficulty":dict(collections.Counter(q["difficulty"] for q in OUT)),"checks":len(CHECKS)}
    print(json.dumps(stats))
    if final:
        assert len(OUT)==100 and len(FAMILIES)>=25 and max(FAMILIES.values())<=4
        assert stats["questionDiagrams"]>=20 and stats["schemeDiagrams"]>=10
        assert stats["types"]=={"multiple-choice":40,"structured":45,"data-based":15}
        assert stats["difficulty"]=={"easy":30,"medium":45,"hard":25}
        review=ROOT/"docs/ib-physics-reviews/nuclear-quantum.txt";review.parent.mkdir(parents=True,exist_ok=True)
        review.write_text("THEME E: AUTHOR REVIEW\n\n"+json.dumps(stats,indent=2)+"\n\nScope: 20 questions per E.1–E.5. E.2 is AHL; nuclear size, closest approach and Bohr work in E.1 are AHL; exponential decay and stability evidence in E.3 are AHL.\nProvenance: original contexts, constructed datasets and self-drawn SVGs. No exam/question-bank texts or graphics were ingested. Corrected syllabus blueprint and standard physical relations set the scope.\nMarking: MCQs award exactly A1 with explicit reasoning; structured parts have distinct method, accuracy and reasoning points. Numerical values are calculated at full precision then rounded; equivalent methods accepted. ECF is stated where appropriate. No blanket unit or precision penalties.\nChecks: deterministic arithmetic assertions, inverse substitution, conservation, decay normalization, units, endpoint/ratio tests, XML parsing and forbidden SVG construct checks. Author-side checks only, not independent exam moderation or official IB approval.\nData: explicitly constructed/modelled, with inference tolerances. Schematic spacing is declared; HR temperatures decrease to the right. Source/solution graphics are separate.\nBoundaries: no weak-interaction explanation, Cepheids, detailed particle taxonomy, Compton derivation or nuclear engineering design. Reactor models are classroom abstractions. Stellar support may be thermal or radiation pressure.\n\nFamily ledger (four variants each):\n"+"\n".join(f"{f}: {c}" for f,c in FAMILIES.items())+"\n\nCheck ledger:\n"+"\n".join(CHECKS)+"\n",encoding="utf-8")

# E.1 — five distinct families, twenty questions.
for v,(a,z,charge) in enumerate([(40,20,2),(56,26,3),(79,35,-1),(32,16,-2)]):
    neutrons,electrons=a-z,z-charge
    stem=fr"An ion has nucleon number ${a}$, proton number ${z}$ and charge ${abs(charge)}e$ "+("positive" if charge>0 else "negative")+". How many neutrons and electrons does it contain?"
    options=[f"{neutrons} neutrons and {electrons} electrons",f"{a} neutrons and {electrons} electrons",f"{neutrons} neutrons and {z+charge} electrons",f"{z} neutrons and {a-charge} electrons"]
    add(1,"E1-F1 nuclear notation and ionic electron counts",v,f"Particle inventory for ion {v+1}",stem,options=options,reason=fr"Neutron number is $A-Z={neutrons}$. Charge in units of $e$ is proton number minus electron number, so there are ${electrons}$ electrons. The nucleon number does not count electrons.",difficulty="easy")
    check(f"E1 notation {v+1}",electrons+charge,z)
for v,(middle,upper) in enumerate([(2.2,5.6),(1.8,4.9),(2.6,6.8),(3.1,7.7)]):
    gap=upper-middle;wavelengths=[H*C/(energy*E)*1e9 for energy in (gap,upper,middle,upper+middle)]
    add(1,"E1-F2 emission transitions in constructed atomic levels",v,f"A line from artificial atom {v+1}",fr"A model atom has energy levels $0$, ${middle:g}$ and ${upper:g}\,\mathrm{{eV}}$, measured relative to its ground state. An atom makes the transition from the upper level to the middle level. Which wavelength is emitted? Use $h=6.63\times10^{{-34}}\,\mathrm{{J\,s}}$, $c=3.00\times10^8\,\mathrm{{m\,s^{{-1}}}}$ and $1\,\mathrm{{eV}}=1.60\times10^{{-19}}\,\mathrm{{J}}$.",
      options=[qty(w,"nm") for w in wavelengths],reason=fr"The photon carries the positive energy difference ${upper:g}-{middle:g}={gap:g}\,\mathrm{{eV}}$. Hence $\lambda=hc/\Delta E={tex(wavelengths[0])}\,\mathrm{{nm}}$. Using a level energy rather than the difference describes a different transition.",
      diagram=levels([("ground",0),("middle",middle),("upper",upper)],transitions=[("upper","middle")]))
    check(f"E1 transition energy {v+1}",H*C/(wavelengths[0]*1e-9)/E,gap)
for v,(a,root) in enumerate([(27,3),(64,4),(125,5),(216,6)]):
    r=1.2e-15*root;mass=a*U;density=mass/(4*math.pi*r**3/3)
    add(1,"E1-F3 nuclear radius scaling and density",v,f"Nuclear size model for A = {a}",fr"Approximate a nucleus of nucleon number ${a}$ as a uniform sphere. Use $R=r_0A^{{1/3}}$, with $r_0=1.20\times10^{{-15}}\,\mathrm{{m}}$, and a mass of $1.66\times10^{{-27}}\,\mathrm{{kg}}$ per nucleon. Ignore the mass defect for this size model.",parts=[
      part("Calculate the nuclear radius.",("M1",fr"$R=1.20\times10^{{-15}}({a})^{{1/3}}$."),("A1",fr"$R={tex(r)}\,\mathrm{{m}}$.")),
      part("Estimate the nuclear mass density.",("M1",fr"$\rho=A m_u/(\frac43\pi R^3)$, with $m={tex(mass)}\,\mathrm{{kg}}$."),("A1",fr"$\rho={tex(density)}\,\mathrm{{kg\,m^{{-3}}}}$. Accept consistent error carried forward from the radius.")),
      part("Explain why this model predicts approximately the same density for a nucleus with eight times as many nucleons.",("R1","Eight times as many nucleons give twice the radius and eight times the volume."),("R1","Mass and volume increase by the same factor, leaving density unchanged."))],level="ahl")
    check(f"E1 radius cube {v+1}",(r/1.2e-15)**3,a);check(f"E1 density cancellation {v+1}",density,3*U/(4*math.pi*(1.2e-15)**3))
for v,(z,energy,rn) in enumerate([(29,4,4.0),(47,5,5.5),(79,6,7.0),(82,8,7.2)]):
    kinetic=energy*1e6*E;r=K*2*z*E**2/kinetic;contact=K*2*z*E**2/(rn*1e-15)/(1e6*E)
    b=text(330,30,"Head-on alpha-particle approach (schematic)",size=17)+arrow(60,205,230,205)+text(130,175,f"alpha: {energy:g} MeV",color=BLUE)
    b+='<circle cx="490" cy="205" r="23" fill="#fce2df" stroke="#b91c1c"/>'+text(490,250,f"nucleus: +{z}e",color=RED)+line(310,205,490,205,"#64748b",2,True)+'<circle cx="310" cy="205" r="5" fill="#1d4ed8"/><circle cx="490" cy="205" r="3" fill="#b91c1c"/>'+text(400,180,"centre distance r")+text(300,250,"turning position",size=13)+text(330,340,"Target nucleus is treated as fixed; not to scale.",size=13)
    solution=graph([(1+3*i/90,energy/(1+3*i/90)) for i in range(91)],4,energy*1.15,"distance / calculated closest distance","electric potential energy / MeV","Electric potential energy at the turning point",xmin=1,extra=[([(1,energy),(4,energy)],RED)],legend=[("potential energy",BLUE),("incident kinetic energy",RED)])
    add(1,"E1-F4 closest approach and finite nuclear size",v,f"Testing a nuclear size bound {v+1}",fr"An alpha particle of charge $+2e$ approaches a nucleus of charge $+{z}e$ head-on from very far away with kinetic energy ${energy:.2f}\,\mathrm{{MeV}}$. Ignore recoil and electron screening. Use $k=8.99\times10^9\,\mathrm{{N\,m^2\,C^{{-2}}}}$ and $e=1.60\times10^{{-19}}\,\mathrm{{C}}$. The estimated nuclear radius is ${rn:.2f}\,\mathrm{{fm}}$.",parts=[
      part("Calculate the closest distance between the two centres in the point-charge model.",("M1",r"At the turning point, kinetic energy is zero; conserve energy using $E_k=k(2e)(Ze)/r$."),("M1",fr"Convert the incident energy to ${tex(kinetic)}\,\mathrm{{J}}$ and rearrange for $r$."),("A1",fr"$r={tex(r)}\,\mathrm{{m}}={tex(r/1e-15)}\,\mathrm{{fm}}$.")),
      part("Estimate the incident energy that would make the model's closest approach equal to the given nuclear radius.",("M1",fr"$E=k(2e)({z}e)/({rn:g}\times10^{{-15}})$."),("A1",fr"$E={tex(contact)}\,\mathrm{{MeV}}$.")),
      part("Assess the model for the original incident energy and explain why the second result is not a precise prediction of a nuclear collision.",("R1","The original closest distance exceeds the radius, so the projectile turns around outside the nucleus."),("R1","At nuclear dimensions, finite charge distribution and nuclear interactions can invalidate the point-charge Coulomb model; neglected recoil is another limitation."))],level="ahl",difficulty="hard",diagram=svg(b,"Head-on alpha approach"),solution=solution)
    check(f"E1 approach energy recovery {v+1}",K*2*z*E**2/r,kinetic);check(f"E1 radius bound {v+1}",contact/energy,r/(rn*1e-15))
bohr=[(f"n = {n}",-13.6/n**2) for n in range(1,7)]
for v in range(4):
    if v<2:
        upper=[3,4][v];delta=13.6*(1/4-1/upper**2);wave=H*C/(delta*E)*1e9;angular=upper*H/(2*math.pi)
        stem=fr"The table contains constructed values from the hydrogen model $E_n=-13.6/n^2$ in eV. Consider an emission from $n={upper}$ to $n=2$. Use $h=6.63\times10^{{-34}}\,\mathrm{{J\,s}}$, $c=3.00\times10^8\,\mathrm{{m\,s^{{-1}}}}$ and $1\,\mathrm{{eV}}=1.60\times10^{{-19}}\,\mathrm{{J}}$."+table(["Level n","Energy / eV"],[(n,f"{-13.6/n**2:.4f}") for n in range(1,5)])
        ps=[part("State the energy required to ionize an atom initially in level n = 2.",("A1",r"$3.40\,\mathrm{eV}$ raises the energy from $-3.40\,\mathrm{eV}$ to zero.")),
          part("Calculate the wavelength of the specified emission. Use the formula rather than rounded table entries.",("M1",fr"$\Delta E=13.6(1/2^2-1/{upper}^2)={tex(delta,4)}\,\mathrm{{eV}}$."),("A1",fr"$\lambda=hc/\Delta E={tex(wave)}\,\mathrm{{nm}}$.")),
          part(fr"Use $L=nh/(2\pi)$ to find the angular momentum in level $n={upper}$.",("A1",fr"$L={upper}h/(2\pi)={tex(angular)}\,\mathrm{{J\,s}}$."))]
        check(f"E1 Bohr photon {v+1}",H*C/(wave*1e-9)/E,delta);diagram=levels(bohr[:4],transitions=[(f"n = {upper}","n = 2")]);solution=None
    elif v==2:
        values=[(1/n**2,-13.6/n**2) for n in [1,2,3,4]]
        stem=r"Constructed hydrogen energy measurements are plotted against $1/n^2$. Energy zero corresponds to a free electron. Use $h=6.63\times10^{-34}\,\mathrm{J\,s}$, $c=3.00\times10^8\,\mathrm{m\,s^{-1}}$ and $1\,\mathrm{eV}=1.60\times10^{-19}\,\mathrm{J}$."+table(["1/n²","E / eV"],[(f"{x:.4f}",f"{y:.4f}") for x,y in values])
        wave=H*C/(13.6*(1/4-1/25)*E)*1e9
        ps=[part("Find the gradient and explain its connection to the ground-state ionization energy.",("M1",r"Use separated fit points: $\Delta E/\Delta(1/n^2)\approx-13.6\,\mathrm{eV}$."),("R1",r"The model is $E_n=-13.6/n^2$; the ground state is $13.6\,\mathrm{eV}$ below zero.")),
          part("Predict the wavelength of the n = 5 to n = 2 transition.",("M1",r"$\Delta E=13.6(1/4-1/25)=2.856\,\mathrm{eV}$."),("A1",fr"$\lambda={tex(wave)}\,\mathrm{{nm}}$. Allow 1% for a graph-derived gradient.")),
          part("Explain why negative level energies do not imply negative photon energy.",("R1","Zero is the unbound-electron reference; emitted energy is the positive decrease in atomic energy."))]
        check("E1 Bohr linearization slope",(values[0][1]-values[-1][1])/(values[0][0]-values[-1][0]),-13.6);diagram=graph(sorted(values),1,0,"1 / n²","electron energy / eV","Constructed hydrogen energy data",ymin=-14);solution=None
    else:
        delta=13.6*(1/9-1/36);wave=H*C/(delta*E)*1e9;ionize=13.6/36
        stem=r"A hydrogen atom initially has angular momentum $L=3h/(2\pi)$. It absorbs one photon and reaches n = 6. In a large collection of such atoms, every downward transition between levels 1 to 6 is possible. Use $E_n=-13.6/n^2$ eV, $h=6.63\times10^{-34}\,\mathrm{J\,s}$, $c=3.00\times10^8\,\mathrm{m\,s^{-1}}$ and $1\,\mathrm{eV}=1.60\times10^{-19}\,\mathrm{J}$."
        ps=[part("Identify the initial level and calculate the absorbed photon's wavelength.",("R1",r"$L=nh/(2\pi)$ gives $n=3$."),("M1",r"$\Delta E=E_6-E_3=13.6(1/9-1/36)$."),("A1",fr"$\lambda={tex(wave)}\,\mathrm{{nm}}$.")),
          part("Find the maximum number of distinct emission lines from the collection. Explain why a single atom cannot emit them all in one cascade.",("M1",r"Each pair of levels gives one downward transition: $6(5)/2$."),("A1","There are 15 distinct lines in the model."),("R1","One atom follows one descending sequence with at most five transitions before n = 1.")),
          part("Find the minimum energy needed to ionize an atom from n = 6.",("A1",fr"$0-E_6={tex(ionize)}\,\mathrm{{eV}}$."))]
        check("E1 Bohr absorption inverse",H*C/(wave*1e-9)/E,delta);diagram=levels(bohr,transitions=[("n = 3","n = 6")]);solution=levels(bohr,"One possible five-photon cascade",[(f"n = {n}",f"n = {n-1}") for n in range(6,1,-1)])
    add(1,"E1-F5 Bohr spectrum inference and quantization",v,f"Hydrogen levels investigation {v+1}",stem,parts=ps,level="ahl",difficulty=["easy","easy","medium","hard"][v],data=v<3,diagram=diagram,solution=solution)
save()


# E.2 — photon evidence, Compton shift, matter waves and photoelectric inference.
concepts=[
("Below-threshold illumination",r"A clean metal has threshold frequency $6.0\times10^{14}\,\mathrm{Hz}$. Light of frequency $5.0\times10^{14}\,\mathrm{Hz}$ shines on it. Within the single-photon model, what happens when the intensity is doubled?",["No photoelectrons are emitted.","The maximum kinetic energy doubles.","The stopping voltage doubles.","Electrons begin to emerge after a longer delay."],r"Each photon still has energy $hf<\Phi$. More photons per second do not increase individual photon energy, so no photoelectrons are released in this model."),
("A brighter monochromatic beam",r"Light well above the threshold frequency illuminates a metal. Its frequency is fixed and its intensity is doubled. All emitted electrons are collected and the emission efficiency stays constant. Which change is predicted?",["The saturation current doubles and the stopping voltage is unchanged.","Both saturation current and stopping voltage double.","The saturation current is unchanged and the stopping voltage doubles.","The work function is halved."],r"At fixed frequency, twice the intensity supplies twice as many photons per second, giving twice the electron rate. Maximum electron energy $hf-\Phi$, and therefore stopping voltage, is unchanged."),
("Changing photon energy at fixed photon rate",r"A metal is illuminated above threshold. The incident photon rate and electron-emission efficiency are held fixed while photon frequency rises. Which change follows?",["The stopping voltage rises while the saturation current stays constant.","The stopping voltage stays constant while the current rises.","Both stopping voltage and current must fall.","The work function rises in proportion to frequency."],r"The maximum kinetic energy rises because $K_{\max}=hf-\Phi$. Fixed photon rate and efficiency give the same emitted-electron rate, so the saturation current is constant."),
("Evidence from immediate emission",r"A very weak beam above a metal's threshold produces photoelectrons without a measurable accumulation delay. Increasing intensity changes the number emitted, not their maximum energy. Which statement explains both observations?",["An electron can gain the energy of one photon in one interaction.","An electron must store many wave cycles before escaping.","Intensity sets the energy of each photon at fixed frequency.","The metal's work function falls to zero in weak light."],r"One above-threshold photon can transfer sufficient energy in one interaction. At fixed frequency photon energy is fixed, while intensity controls the number of photons arriving per second.")
]
for v,(title,stem,options,reason) in enumerate(concepts):
    add(2,"E2-F1 photon model of photoelectric observations",v,title,stem,options=options,reason=reason,level="ahl",difficulty="easy")
for v,(theta,wavelength) in enumerate([(45,8),(60,12),(90,20),(120,30)]):
    shift=2.43*(1-math.cos(math.radians(theta)));out=wavelength+shift
    add(2,"E2-F2 Compton wavelength shift and energy transfer",v,f"A photon scattered through {theta} degrees",
      fr"An X-ray photon of wavelength ${wavelength:.2f}\,\mathrm{{pm}}$ scatters through ${theta}^\circ$ from an initially stationary free electron. Use $\Delta\lambda=\lambda_C(1-\cos\theta)$ with $\lambda_C=2.43\,\mathrm{{pm}}$. Which is the scattered photon's wavelength?",
      options=[qty(value,"pm",4) for value in [out,wavelength-shift,shift,wavelength+2*shift]],
      reason=fr"$\Delta\lambda=2.43(1-\cos{theta}^\circ)={tex(shift,4)}\,\mathrm{{pm}}$, so $\lambda'={tex(out,4)}\,\mathrm{{pm}}$. The increased wavelength means lower photon energy; energy is transferred to the recoil electron.",level="ahl",diagram=scattering(theta))
    check(f"E2 Compton inverse angle {v+1}",math.degrees(math.acos(1-(out-wavelength)/2.43)),theta,1e-7)
    assert out>wavelength and shift<=4.86
for v,(voltage,ratio) in enumerate([(36,.80),(64,.75),(100,.60),(144,.50)]):
    speed=math.sqrt(2*E*voltage/ME);wave=H/(ME*speed);newV=voltage/ratio**2
    body=text(330,30,"Electron diffraction rings (schematic)",size=17)
    for radius in [50,100]:
        body+=f'<circle cx="330" cy="200" r="{radius}" fill="none" stroke="{BLUE}" stroke-width="3"/>'
    body+=line(230,200,430,200,"#64748b",1,True)+text(330,325,"Ring diameter D is proportional to wavelength.",size=14)
    add(2,"E2-F3 electron acceleration and diffraction scaling",v,f"Tuning an electron diffraction beam {v+1}",
      fr"Electrons start nearly at rest and are accelerated through ${voltage:.1f}\,\mathrm{{V}}$ before diffracting from a thin target. Use $e=1.60\times10^{{-19}}\,\mathrm{{C}}$, $m_e=9.11\times10^{{-31}}\,\mathrm{{kg}}$, $h=6.63\times10^{{-34}}\,\mathrm{{J\,s}}$ and $c=3.00\times10^8\,\mathrm{{m\,s^{{-1}}}}$. For this fixed apparatus the small-angle ring diameter is proportional to de Broglie wavelength.",
      parts=[
        part("Calculate the electron speed and de Broglie wavelength using the non-relativistic model.",("M1",r"$eV=\frac12m_ev^2$ and $\lambda=h/(m_ev)$."),("A1",fr"$v={tex(speed)}\,\mathrm{{m\,s^{{-1}}}}$."),("A1",fr"$\lambda={tex(wave)}\,\mathrm{{m}}$.")),
        part(fr"The same ring is required to have ${ratio:.2f}$ times its original diameter. Find the new accelerating voltage.",("M1",r"$D\propto\lambda\propto V^{-1/2}$, so $V_{\rm new}=V_{\rm old}/(D_{\rm new}/D_{\rm old})^2$."),("A1",fr"$V_{{\rm new}}={tex(newV)}\,\mathrm{{V}}$.")),
        part("Assess the non-relativistic approximation for the original beam.",("A1",fr"$v/c={tex(speed/C)}$."),("R1","This is much less than one, so relativistic corrections are small for the stated precision."))
      ],level="ahl",diagram=svg(body,"Electron diffraction rings"))
    check(f"E2 kinetic energy recovered {v+1}",(H/wave)**2/(2*ME),E*voltage)
    check(f"E2 diffraction voltage ratio {v+1}",math.sqrt(voltage/newV),ratio)
for v,(nm,threshold,power,eta) in enumerate([(400,650,2.0,.12),(450,700,3.0,.18),(500,750,4.0,.24),(550,800,5.0,.30)]):
    photon=H*C/(nm*1e-9);work=H*C/(threshold*1e-9);stopping=(photon-work)/E;current=eta*power*1e-3/photon*E
    f0=C/(threshold*1e-9)/1e14;f=C/(nm*1e-9)/1e14
    sol=graph([(x,H/E*1e14*(x-f0)) for x in [f0,(f0+f)/2,f]],f*1.1,stopping*1.2,"frequency / 10¹⁴ Hz","stopping voltage / V","Energy balance for this metal",xmin=f0*.85)
    add(2,"E2-F4 photoelectric energy and photon-rate budget",v,f"Designing a photoelectric measurement {v+1}",
      fr"A metal has threshold wavelength ${threshold:.0f}\,\mathrm{{nm}}$. A monochromatic beam of wavelength ${nm:.0f}\,\mathrm{{nm}}$ and incident power ${power:.2f}\,\mathrm{{mW}}$ illuminates it. On average ${eta:.2f}$ collected electrons are produced per incident photon. Use $h=6.63\times10^{{-34}}\,\mathrm{{J\,s}}$, $c=3.00\times10^8\,\mathrm{{m\,s^{{-1}}}}$ and $e=1.60\times10^{{-19}}\,\mathrm{{C}}$.",
      parts=[
        part("Calculate the work function in electronvolts and the stopping voltage.",("M1",r"$\Phi=hc/\lambda_0$; $eV_s=hc/\lambda-\Phi$."),("A1",fr"$\Phi={tex(work/E)}\,\mathrm{{eV}}$."),("A1",fr"$V_s={tex(stopping)}\,\mathrm{{V}}$.")),
        part("Calculate the saturation current.",("M1",r"Photon arrival rate $=P/(hc/\lambda)$; multiply by the stated electron yield and electron charge."),("A1",fr"$I={tex(current)}\,\mathrm{{A}}$.")),
        part("The wavelength is shortened while incident power and electron yield remain fixed. Explain the changes in stopping voltage and saturation current.",("R1","The photon energy increases, so maximum electron kinetic energy and stopping voltage increase."),("R1","Fixed power divided by larger photon energy gives fewer photons per second; with fixed yield the saturation current decreases."))
      ],level="ahl",difficulty="hard",solution=sol)
    check(f"E2 photoelectric energy conservation {v+1}",work+E*stopping,photon)
    check(f"E2 photoelectron power fraction {v+1}",current/E*photon,eta*power*1e-3)
for v,f0 in enumerate([4.5,5.0,5.5,6.0]):
    frequencies=[7,8,9,10,11];vs=[.414*(f-f0) for f in frequencies];hfit=.414/1e14*E;phi=.414*f0
    if v<3:
        stem=fr"The following simulated stopping voltages are constructed from a single-metal photoelectric model. Frequency entries are in $10^{{14}}\,\mathrm{{Hz}}$. Take $e=1.60\times10^{{-19}}\,\mathrm{{C}}$."+table(["f / 10¹⁴ Hz","Stopping voltage / V"],[(f,f"{y:.3f}") for f,y in zip(frequencies,vs)])
        ps=[
          part("Use two widely separated points to estimate the gradient in V Hz⁻¹.",("M1",r"Divide the voltage difference by the actual frequency difference in Hz."),("A1",r"Gradient $=4.14\times10^{-15}\,\mathrm{V\,Hz^{-1}}$.")),
          part("Deduce Planck's constant and the threshold frequency.",("M1",r"From $V_s=(h/e)f-\Phi/e$, multiply the gradient by $e$ and find the zero-voltage intercept."),("A1",fr"$h={tex(hfit)}\,\mathrm{{J\,s}}$; $f_0={tex(f0*1e14)}\,\mathrm{{Hz}}$. Accept 1% for graph estimates.")),
          part("Explain whether doubling the beam intensity would change this fitted line.",("R1","It changes the emitted-electron rate, not the maximum kinetic energy at a given frequency; the stopping-voltage line is unchanged."))
        ];solution=None
    else:
        lo=(vs[-1]-.02-(vs[0]+.02))/(4e14)*E;hi=(vs[-1]+.02-(vs[0]-.02))/(4e14)*E
        stem=fr"A photoelectric experiment gives stopping voltages ${vs[0]:.3f}\pm0.020\,\mathrm{{V}}$ at $7.00\times10^{{14}}\,\mathrm{{Hz}}$ and ${vs[-1]:.3f}\pm0.020\,\mathrm{{V}}$ at $1.10\times10^{{15}}\,\mathrm{{Hz}}$. Frequency uncertainties are negligible. Treat endpoint voltage errors as independent allowed bounds. Use $e=1.60\times10^{{-19}}\,\mathrm{{C}}$."
        ps=[
          part("Estimate Planck's constant from the central measurements.",("M1",r"Use $h=e\,\Delta V_s/\Delta f$."),("A1",fr"$h={tex(hfit)}\,\mathrm{{J\,s}}$.")),
          part("Find the minimum and maximum Planck-constant estimates allowed by the endpoint bounds.",("M1","The steepest line joins the lowest allowed first voltage to the highest allowed last voltage; reverse these choices for the shallowest line."),("A1",fr"$h_{{\min}}={tex(lo,4)}\,\mathrm{{J\,s}}$."),("A1",fr"$h_{{\max}}={tex(hi,4)}\,\mathrm{{J\,s}}$.")),
          part(r"A surface change increases the work function by $0.25\,\mathrm{eV}$. Describe the changes to the graph's gradient and vertical position.",("R1",r"The gradient remains $h/e$ because it is independent of work function."),("R1",r"Each stopping voltage decreases by $0.25\,\mathrm{V}$, where photoemission still occurs."))
        ]
        solution=graph([(7,vs[0]),(11,vs[-1])],11,vs[-1]+.25,"frequency / 10¹⁴ Hz","stopping voltage / V","Central fit and bounding endpoint lines",xmin=7,extra=[([(7,vs[0]-.02),(11,vs[-1]+.02)],RED),([(7,vs[0]+.02),(11,vs[-1]-.02)],GREEN)],legend=[("central fit",BLUE),("steepest fit",RED),("shallowest fit",GREEN)])
        check("E2 Planck estimate central within bounds", (lo+hi)/2,hfit)
    add(2,"E2-F5 stopping-voltage graph inference and uncertainty",v,f"Inferring a photon constant {v+1}",stem,parts=ps,level="ahl",difficulty=["easy","easy","medium","hard"][v],data=v<3,
      diagram=graph(list(zip(frequencies,vs)) if v<3 else [(7,vs[0]),(11,vs[-1])],11.5,3.0,"frequency / 10¹⁴ Hz","stopping voltage / V","Constructed stopping-voltage data",xmin=4),solution=solution)
    check(f"E2 photoelectric fitted threshold {v+1}",frequencies[0]-vs[0]/.414,f0)
save()


# E.3 — decay notation, background, exponential statistics and nuclear stability.
decays=[
(210,84,"alpha",206,82,r"An alpha particle $^4_2\alpha$ is emitted.",r"Emission removes two protons and two neutrons: $A$ falls by four and $Z$ by two."),
(32,15,"beta-minus",32,16,r"An electron and an electron antineutrino are emitted in beta-minus decay.",r"One neutron becomes a proton. The nucleon number stays fixed and proton number increases by one; the emitted electron balances charge."),
(22,11,"beta-plus",22,10,r"A positron and an electron neutrino are emitted in beta-plus decay.",r"One proton becomes a neutron. The nucleon number stays fixed and proton number decreases by one; the positron carries the positive charge."),
(99,43,"gamma",99,43,r"An excited nucleus emits a gamma photon and reaches a lower nuclear energy state.",r"A gamma photon carries energy and angular momentum but no nucleon number or electric charge, so neither $A$ nor $Z$ changes.")
]
for v,(a,z,kind,da,dz,description,reason) in enumerate(decays):
    pair=[(da,dz),(da+1,dz),(da,dz+1),(da-2,dz-1)]
    add(3,"E3-F1 nuclear decay bookkeeping",v,f"Following a {kind} decay",fr"A parent nucleus has nucleon number ${a}$ and proton number ${z}$. "+description+" Which pair gives the daughter's nucleon number and proton number?",
      options=[fr"$A={x},\ Z={y}$" for x,y in pair],reason=reason,difficulty="easy")
    if kind=="alpha":check("E3 alpha nucleon conservation",da+4,a);check("E3 alpha charge conservation",dz+2,z)
    elif kind=="beta-minus":check("E3 beta-minus charge conservation",dz-1,z)
    elif kind=="beta-plus":check("E3 beta-plus charge conservation",dz+1,z)
    else:check("E3 gamma nucleon conservation",da,a)
for v,(raw,bg,half,n) in enumerate([(340,20,3,2),(520,40,5,3),(860,60,8,2),(1040,80,10,4)]):
    net=raw-bg;end=bg+net/2**n
    add(3,"E3-F2 half-lives with detector background",v,f"Background in a decay measurement {v+1}",
      fr"A detector initially reads ${raw}\,\mathrm{{s^{{-1}}}}$ near a single-isotope source. Its constant background rate is ${bg}\,\mathrm{{s^{{-1}}}}$. The source half-life is ${half}\,\mathrm{{min}}$ and the efficiency and geometry remain fixed. What mean detector rate is expected after ${half*n}\,\mathrm{{min}}$?",
      options=[qty(value,"s^{-1}") for value in [end,raw/2**n,net/2**n,bg+net/2**(n-1)]],
      reason=fr"Subtract the background first: source rate $={net}\,\mathrm{{s^{{-1}}}}$. After ${n}$ half-lives it is ${tex(net/2**n)}\,\mathrm{{s^{{-1}}}}$. Adding the unchanged background gives ${tex(end)}\,\mathrm{{s^{{-1}}}}$.")
    check(f"E3 background inversion {v+1}",(end-bg)*2**n,net)
for v,(lam,n0,time) in enumerate([(.004,1.2e6,75),(.006,2e6,60),(.008,3e6,50),(.010,4e6,40)]):
    fraction=math.exp(-lam*time);remaining=n0*fraction;activity=lam*remaining;prob=1-fraction;decayed=n0*prob;linear=lam*n0*time
    add(3,"E3-F3 arbitrary-time decay and finite-interval probability",v,f"A finite decay interval {v+1}",
      fr"A model source initially contains ${tex(n0)}$ undecayed nuclei of one isotope with decay constant ${lam:.4f}\,\mathrm{{s^{{-1}}}}$. Each nucleus decays independently. Consider a time interval of ${time:.1f}\,\mathrm{{s}}$. Use the exponential model and report expected populations rather than an exact random outcome.",
      parts=[
        part("Find the expected number of undecayed nuclei and the activity at the end of the interval.",("M1",r"$N=N_0e^{-\lambda t}$ and $A=\lambda N$."),("A1",fr"$N={tex(remaining)}$ nuclei."),("A1",fr"$A={tex(activity)}\,\mathrm{{Bq}}$; accept consistent error carried forward from $N$.")),
        part("Calculate the probability that one initially present nucleus decays during the interval.",("M1",r"Survival probability is $e^{-\lambda t}$, so decay probability is its complement."),("A1",fr"$P=1-e^{{-\lambda t}}={tex(prob)}$.")),
        part("Compare the actual expected number of decays with the estimate initial activity multiplied by time. Explain the discrepancy.",("A1",fr"Exponential expectation $={tex(decayed)}$; $A_0t={tex(linear)}$."),("R1","The initial-activity estimate is larger because it assumes the activity remains fixed while the population is actually declining."))
      ],level="ahl")
    check(f"E3 population conservation {v+1}",remaining+decayed,n0);check(f"E3 probability inversion {v+1}",-math.log(1-prob)/time,lam)
    assert linear>decayed>0
for v,(a,binding,fragment_binding,endpoint,electron_energy) in enumerate([(12,7.6,7.2,.8,.3),(16,8.0,7.6,1.2,.5),(20,8.3,7.8,1.6,.7),(24,8.5,8.1,2.0,1.0)]):
    z=a//2;free=z*1.00728+(a-z)*1.00866;mass=round(free-a*binding/931.5,6);defect=free-mass;be=defect*931.5;per=be/a;qbreak=a*fragment_binding-be;neutrino=endpoint-electron_energy
    points=[(endpoint*i/20,100*(i/20)*(1-i/20)**2/(4/27)) for i in range(21)]
    stem=fr"In a simplified nuclear mass dataset, a nucleus has $A={a}$, $Z={z}$ and nuclear mass ${mass:.6f}\,\mathrm{{u}}$. Use proton mass $1.00728\,\mathrm{{u}}$, neutron mass $1.00866\,\mathrm{{u}}$ and $1\,\mathrm{{u}}c^2=931.5\,\mathrm{{MeV}}$. These are nuclear masses; electron masses are excluded. A proposed breakup conserves the total proton and neutron numbers and gives fragments with mean binding energy ${fragment_binding:.2f}\,\mathrm{{MeV}}$ per nucleon. Separately, the schematic beta spectrum shown has endpoint ${endpoint:.2f}\,\mathrm{{MeV}}$."
    add(3,"E3-F4 binding-energy stability and continuous beta evidence",v,f"Interpreting nuclear energy evidence {v+1}",stem,parts=[
      part("Calculate the mass defect and binding energy per nucleon of the original nucleus.",("M1",fr"$\Delta m=Z m_p+(A-Z)m_n-m_{{\rm nucleus}}={tex(defect,5)}\,\mathrm{{u}}$."),("M1",r"Multiply by $931.5\,\mathrm{MeV\,u^{-1}}$ to obtain total binding energy, then divide by $A$."),("A1",fr"$B/A={tex(per,4)}\,\mathrm{{MeV}}$.")),
      part("Determine whether the proposed breakup releases energy.",("M1",fr"Reaction energy is final total binding minus initial binding: $Q={a}({fragment_binding:g})-{tex(be,6)}$ MeV."),("A1",fr"$Q={tex(qbreak)}\,\mathrm{{MeV}}$; it requires an input of ${tex(-qbreak)}\,\mathrm{{MeV}}$."),("R1","The more tightly bound original configuration has lower total rest energy than the separated fragments.")),
      part(fr"In the beta process, an electron emerges with ${electron_energy:.2f}\,\mathrm{{MeV}}$. Neglect nuclear recoil and neutrino rest energy. Find the energy carried by the neutrino or antineutrino and explain why the electron spectrum is continuous.",("A1",fr"The other emitted particle carries approximately ${endpoint:g}-{electron_energy:g}={neutrino:g}\,\mathrm{{MeV}}$."),("R1","The released energy can be shared in different proportions between electron and neutrino/antineutrino; the electron need not take a fixed amount."))
      ],level="ahl",difficulty="hard",diagram=graph(points,endpoint,110,"electron kinetic energy / MeV","relative counts / arbitrary units","Illustrative continuous beta spectrum"),
      solution=graph([(0,endpoint),(electron_energy,neutrino),(endpoint,0)],endpoint,endpoint,"electron kinetic energy / MeV","neutrino energy / MeV","Allowed energy sharing when recoil is neglected"))
    check(f"E3 mass defect round-trip {v+1}",mass+be/931.5,free);check(f"E3 breakup rest-energy sign {v+1}",qbreak+be,a*fragment_binding);check(f"E3 beta energy balance {v+1}",electron_energy+neutrino,endpoint)
for v in range(4):
    if v<2:
        half,bg,initial=[(4,20,800),(6,30,960)][v];times=[0,half,2*half,3*half];rates=[bg+initial/2**i for i in range(4)]
        stem=fr"The table gives simulated mean detector count rates from one source plus a constant background of ${bg}\,\mathrm{{s^{{-1}}}}$. Geometry and detector efficiency are fixed."+table(["time / min","detector rate / s⁻¹"],[(t,f"{r:g}") for t,r in zip(times,rates)])
        ps=[part("Determine the source half-life after allowing for background.",("M1",fr"The initial net rate is ${initial}\,\mathrm{{s^{{-1}}}}$; compare net rates rather than raw detector readings."),("A1",fr"Successive net rates halve every ${half}\,\mathrm{{min}}$, so this is the half-life.")),
          part(fr"Predict the mean detector rate at ${4*half}\,\mathrm{{min}}$.",("M1",r"Reduce the initial source contribution through four half-lives and restore background."),("A1",fr"$R={bg}+{initial}/16={tex(bg+initial/16)}\,\mathrm{{s^{{-1}}}}$.")),
          part("Explain why a real short count would not be expected to equal the model mean exactly.",("R1","Individual decays and detections are random, so finite counts fluctuate statistically around the mean."))]
        diagram=graph(list(zip(times,rates)),3*half,rates[0]*1.1,"time / min","mean detector rate / s⁻¹","Constructed source-plus-background rates");solution=None;level="core"
        check(f"E3 data half-life recovery {v+1}",(rates[0]-bg)/(rates[1]-bg),2)
    elif v==2:
        lam=.0032;rate0=400;eff=.25;times=[0,100,200,300,400];logs=[math.log(rate0)-lam*t for t in times];half=math.log(2)/lam;n0=rate0/(eff*lam)
        stem=r"Background has already been subtracted from a source's detected count rate $r$. The table gives constructed values of $\ln[r/(1\,\mathrm{s^{-1}})]$. The detector records a constant fraction $0.250$ of decays."+table(["time / s","ln[r / (1 s⁻¹)]"],[(t,f"{y:.4f}") for t,y in zip(times,logs)])
        ps=[part("Find the decay constant and half-life.",("M1",r"From $\ln r=\ln r_0-\lambda t$, the negative gradient is $\lambda$."),("A1",fr"$\lambda={tex(lam)}\,\mathrm{{s^{{-1}}}}$ and $t_{{1/2}}=\ln2/\lambda={tex(half)}\,\mathrm{{s}}$. Accept 1% from displayed data.")),
          part("Estimate the initial number of undecayed nuclei.",("M1",r"Exponentiate the intercept to find $r_0\approx400\,\mathrm{s^{-1}}$; $r_0=\epsilon\lambda N_0$."),("A1",fr"$N_0={tex(n0)}$ nuclei; allow consistent ECF from the fitted decay constant.")),
          part("Explain why taking logarithms before subtracting background would spoil this linear model.",("R1",r"The raw rate is $r_0e^{-\lambda t}+b$. The logarithm of this sum is not a straight line in time; it flattens towards the background level."))
        ];diagram=graph(list(zip(times,logs)),400,6.2,"time / s","ln[r / (1 s⁻¹)]","Linearised simulated decay data",ymin=4.5);solution=None;level="ahl"
        check("E3 log gradient recovery",-(logs[-1]-logs[0])/400,lam);check("E3 efficiency population recovery",eff*lam*n0,rate0)
    else:
        half=12;initial=600;eff0=.25;eff1=.20;raw=108;bg=12;ratio=((raw-bg)/eff1)/(initial/eff0);age=-half*math.log(ratio)/math.log(2)
        stem=r"A source has half-life $12.0\,\mathrm{h}$. At preparation its background-corrected detected rate was $600\,\mathrm{s^{-1}}$ with detection efficiency $0.250$. At a later measurement the efficiency is $0.200$, the raw detector rate is $108\,\mathrm{s^{-1}}$ and the background is $12.0\,\mathrm{s^{-1}}$. The source contains one isotope and has not lost material."
        ps=[part("Find the original and later source activities.",("M1",r"Correct the later rate for background and use $A=r/\epsilon$ at each measurement."),("A1",r"$A_0=2400\,\mathrm{Bq}$ and $A=480\,\mathrm{Bq}$.")),
          part("Calculate the source's age at the later measurement.",("M1",r"$A/A_0=0.200=e^{-\lambda t}$ with $\lambda=\ln2/12.0\,\mathrm{h^{-1}}$."),("A1",fr"$t={tex(age)}\,\mathrm{{h}}$; accept consistent ECF from the activity ratio.")),
          part("A student divides the later net detector rate by the original net detector rate without correcting efficiencies. Explain the direction of the age error.",("R1","The lower later efficiency makes this detected-rate ratio smaller than the true activity ratio."),("R1","A smaller surviving fraction would imply too many half-lives, so the calculated age would be too large."))
        ];diagram=graph([(x,2**(-x/half)) for x in range(0,49,4)],48,1.1,"elapsed time / h","fraction of initial activity","Single-isotope activity model");solution=graph([(0,1),(age,ratio),(48,.0625)],48,1.1,"elapsed time / h","fraction of initial activity","Corrected activity ratio and inferred age",connect=False);level="ahl"
        check("E3 age reverse decay",2**(-age/half),ratio)
    add(3,"E3-F5 decay-graph inference and detector calibration",v,f"Reading a decay record {v+1}",stem,parts=ps,level=level,difficulty=["easy","easy","medium","hard"][v],data=v<3,diagram=diagram,solution=solution)
save()


# E.4 — reactor roles, balanced reactions, energy yield, neutron economy and decay heat.
roles=[
("Moderator","A reactor component reduces the speed of neutrons mainly through collisions. What is its intended function?",["To increase the chance that suitable slower neutrons induce fission in the fuel.","To absorb every neutron so no further fission can occur.","To convert thermal energy directly into electrical energy.","To make the nuclei's proton numbers decrease."],"The moderator slows neutrons by collisions; in the stated thermal-reactor context, slower neutrons have a greater probability of causing fission in the selected fuel."),
("Control rods","A thermal reactor has rods that can be inserted further into its core. What physical process allows the rods to reduce the rate of the chain reaction?",["Neutron absorption reduces the number available to cause subsequent fissions.","Neutrons gain kinetic energy from the rods until they stop fissioning.","The rods raise the binding energy of every fuel nucleus.","The rods immediately remove all radioactive decay products."],"Control rods absorb neutrons. Fewer neutrons remain to initiate the next generation of fissions, reducing the multiplication factor."),
("Coolant","In a simplified reactor, a fluid circulates through the core and then through a heat exchanger. What is its primary role in this circuit?",["To carry thermal energy from the core to the heat exchanger.","To guarantee that every neutron is slowed to exactly the same speed.","To change gamma photons into electrons before they leave the fuel.","To increase the half-lives of fission products."],"The circulating coolant transports internal energy from the hot core to the heat exchanger, where energy can be passed to another fluid."),
("Shielding","A thick shield surrounds a reactor assembly. Which statement best describes its purpose?",["It reduces the radiation reaching surrounding areas through absorption and scattering.","It replaces control rods by setting the neutron multiplication factor exactly to one.","It makes all fission products stable.","It removes the need to transport heat out of the core."],"Shielding attenuates radiation by absorption and scattering. This role is distinct from controlling the chain reaction, cooling the core, or eliminating radioactivity.")
]
for v,(name,stem,options,reason) in enumerate(roles):
    add(4,"E4-F1 distinct reactor component functions",v,f"The role of {name.lower()}",stem,options=options,reason=reason,difficulty="easy",diagram=reactor() if v==2 else None)
for v,(a1,z1,s1,a2,z2,s2) in enumerate([(141,56,"Ba",92,36,"Kr"),(140,54,"Xe",94,38,"Sr"),(100,40,"Zr",132,52,"Te"),(102,42,"Mo",131,50,"Sn")]):
    neutrons=236-a1-a2
    stem=fr"Consider the possible induced-fission channel $^{{235}}_{{92}}\mathrm{{U}}+^1_0\mathrm{{n}}\rightarrow ^{{{a1}}}_{{{z1}}}\mathrm{{{s1}}}+^{{{a2}}}_{{{z2}}}\mathrm{{{s2}}}+k\,^1_0\mathrm{{n}}$. No other particles carrying nucleon number are emitted. What is $k$?"
    options=[str(neutrons),str(neutrons+1),str(neutrons-1),str(neutrons+2)]
    add(4,"E4-F2 fission nucleon and charge conservation",v,f"Balancing a fission channel {v+1}",stem,options=options,
      reason=fr"The initial nucleon number is $235+1=236$. The fragments contain ${a1}+{a2}={a1+a2}$ nucleons, leaving $k={neutrons}$ neutrons. Proton number is also conserved because ${z1}+{z2}=92$.")
    check(f"E4 fission nucleons {v+1}",a1+a2+neutrons,236);check(f"E4 fission charge {v+1}",z1+z2,92)
for v,(defect,pthermal,efficiency) in enumerate([(.18,150,.30),(.19,200,.32),(.20,250,.34),(.21,300,.36)]):
    initial=236.0526;final=initial-defect;qmev=defect*931.5;qjoule=qmev*1e6*E;rate=pthermal*1e6/qjoule;electric=pthermal*efficiency;massday=rate*235*U*86400
    add(4,"E4-F3 fission energy yield and fuel consumption",v,f"Energy accounting for a reactor model {v+1}",
      fr"The summed masses before one fission are ${initial:.6f}\,\mathrm{{u}}$ and after it are ${final:.6f}\,\mathrm{{u}}$. The sums include all emitted neutrons and equal numbers of atomic electrons on both sides, so electron masses cancel. The average thermal power is ${pthermal:.0f}\,\mathrm{{MW}}$ and electrical efficiency is ${efficiency:.2f}$. Assume all reaction energy becomes heat, each fission consumes one fuel nucleus of mass $235\,\mathrm{{u}}$, and no other fuel losses occur. Use $1\,\mathrm{{u}}c^2=931.5\,\mathrm{{MeV}}$, $1\,\mathrm{{MeV}}=1.60\times10^{{-13}}\,\mathrm{{J}}$ and $1\,\mathrm{{u}}=1.66\times10^{{-27}}\,\mathrm{{kg}}$.",
      parts=[
        part("Calculate the energy released per fission in MeV and joules.",("M1",fr"$\Delta m={initial:.6f}-{final:.6f}={defect:.3f}\,\mathrm{{u}}$ and $Q=\Delta mc^2$."),("A1",fr"$Q={tex(qmev,4)}\,\mathrm{{MeV}}={tex(qjoule,4)}\,\mathrm{{J}}$.")),
        part("Determine the fission rate and electrical output power.",("M1",r"Fission rate is thermal power divided by energy per fission; electrical power is efficiency times thermal power."),("A1",fr"Rate $={tex(rate)}\,\mathrm{{s^{{-1}}}}$; electrical output $={tex(electric)}\,\mathrm{{MW}}$.")),
        part("Estimate the mass of fuel that undergoes fission in one day.",("M1",r"Multiply fissions per second by $86400\,\mathrm{s}$ and by $235(1.66\times10^{-27})\,\mathrm{kg}$ per nucleus."),("A1",fr"Fuel mass $={tex(massday)}\,\mathrm{{kg}}$. Accept consistent ECF from the reaction rate."))
      ],diagram=reactor(f"Energy transfer at {pthermal:g} MW thermal power"))
    check(f"E4 power recovered {v+1}",rate*qjoule,pthermal*1e6);check(f"E4 daily fuel count {v+1}",massday/(235*U),rate*86400)
for v,(nu,loss,p) in enumerate([(2.4,.10,.50),(2.5,.12,.48),(2.6,.15,.46),(2.8,.18,.44)]):
    mult=nu*(1-loss)*p;growth=mult**20;required=1/(nu*(1-loss));absorb=1-1/mult
    add(4,"E4-F4 neutron generations and controlled multiplication",v,f"Following a model neutron population {v+1}",
      fr"In a simplified thermal-reactor model each fission emits on average ${nu:.2f}$ neutrons. A fraction ${loss:.2f}$ is lost before it can interact with fuel. Each remaining neutron has probability ${p:.3f}$ of inducing the next fission. Ignore the time taken by a generation and all feedback. This is an average population model, not an engineering design.",
      parts=[
        part("Calculate the expected multiplication factor k, defined as next-generation fissions divided by current-generation fissions. Classify the trend.",("M1",r"$k=\nu(1-\ell)p$."),("A1",fr"$k={tex(mult,5)}$."),("R1",r"Because $k>1$, the expected number of fissions increases from generation to generation.")),
        part("Find the ratio of the twentieth-generation fission count to the initial count.",("M1",r"Apply the same factor twenty times: $N_{20}/N_0=k^{20}$."),("A1",fr"Ratio $={tex(growth)}$; allow consistent ECF from $k$.")),
        part("Keeping neutron production and losses fixed, find the inducing probability required for a steady expected count. Explain the relevant role of control rods.",("M1",r"Set $k=1$, giving $p_{\rm steady}=1/[\nu(1-\ell)]$."),("A1",fr"$p_{{\rm steady}}={tex(required,4)}$."),("R1","Neutron absorption in control rods reduces the number available for further fissions; a moderator's principal role is slowing, not absorbing, neutrons."))
      ],difficulty="hard",solution=graph([(n,mult**n) for n in range(21)],20,growth*1.1,"generation number","fission count / initial count","Expected growth in the stated simplified model"))
    check(f"E4 steady multiplication {v+1}",nu*(1-loss)*required,1);check(f"E4 geometric generation recovery {v+1}",growth**(1/20),mult)
for v in range(4):
    if v<2:
        half,p0,threshold=[(2,640,40),(5,960,60)][v];times=[0,half,2*half,3*half];heat=[p0/2**i for i in range(4)]
        stem=fr"A constructed dataset models heat from one dominant radioactive fission product after a reactor is shut down. Heat power is proportional to its activity; no new nuclei of this product are formed."+table(["time / years","heat power / W"],list(zip(times,heat)))
        stem+=fr"\n\nA particular thermal calculation asks when this component's heat output first reaches ${threshold}\,\mathrm{{W}}$."
        ps=[
          part("Infer the half-life from the dataset.",("R1","Successive powers halve, indicating that the activity halves over each equal time interval."),("A1",fr"Half-life $={half}\,\mathrm{{years}}$.")),
          part("Find the elapsed time to the specified heat output.",("M1",fr"${threshold}/{p0}=1/16$ corresponds to four half-lives."),("A1",fr"Time $={4*half}\,\mathrm{{years}}$.")),
          part("Explain why meeting this heat-output condition alone does not establish that the material has negligible radiological hazard.",("R1","Heat power alone does not specify radiation type, activity, exposure pathways or containment; radioactive material may remain after its heat output has fallen."))
        ];diagram=graph(list(zip(times,heat)),3*half,p0*1.1,"time after shutdown / years","heat power / W","Constructed single-product decay heat");solution=None
        check(f"E4 cooling threshold {v+1}",p0/2**4,threshold)
    elif v==2:
        times=[0,3,6,9,12];heat=[600*2**(-t/3)+80*2**(-t/30) for t in times]
        stem=r"A simulated waste sample contains a short-lived and a longer-lived heat-producing component. The total heat powers below are rounded model values. No new radioactive nuclei are produced."+table(["time / years","total heat power / W"],[(t,f"{p:.2f}") for t,p in zip(times,heat)])
        ratio1=heat[1]/heat[0];ratio2=heat[-1]/heat[-2]
        ps=[
          part("Calculate the fractional heat remaining over the first and last three-year intervals.",("M1","Divide the later power by the earlier power for each interval."),("A1",fr"First interval: ${tex(ratio1)}$; last interval: ${tex(ratio2)}$.")),
          part("Explain why one fixed half-life cannot describe all of these total-power values.",("R1","A single exponential would give the same surviving fraction over equal time intervals, but the measured fractions differ."),("R1","The short-lived contribution becomes less important, leaving a larger relative contribution from the slower-decaying component.")),
          part("Predict the qualitative long-time behaviour, without extrapolating a numerical value.",("R1","After the short-lived component becomes negligible, the total increasingly follows the longer-lived component's slower decline."))
        ];diagram=graph(list(zip(times,heat)),12,750,"time after shutdown / years","total heat power / W","Two-component constructed decay heat");solution=None
        assert ratio2>ratio1
        check("E4 mixture initial heat",heat[0],680)
    else:
        a_short,a_long=8e14,3e14;e_short,e_long=.80,2.4;ps=a_short*e_short*1.6e-13;pl=a_long*e_long*1.6e-13
        total=ps+pl;later=ps/16+pl/2
        stem=r"A waste model contains two independent products. Initially S has activity $8.0\times10^{14}\,\mathrm{Bq}$ and deposits on average $0.80\,\mathrm{MeV}$ as heat per decay; L has activity $3.0\times10^{14}\,\mathrm{Bq}$ and deposits $2.4\,\mathrm{MeV}$ per decay. Their half-lives are $2.0\,\mathrm{years}$ and $8.0\,\mathrm{years}$ respectively. Neither feeds the other. The quoted deposited energies already exclude escaping energy. Use $1\,\mathrm{MeV}=1.60\times10^{-13}\,\mathrm{J}$."
        pscheme=[
          part("Find each product's initial heat power and the total.",("M1",r"Power is activity times deposited energy per decay."),("A1",fr"$P_S={tex(ps)}\,\mathrm{{W}}$, $P_L={tex(pl)}\,\mathrm{{W}}$; total $={tex(total)}\,\mathrm{{W}}$.")),
          part("Calculate the total heat power eight years later and its fraction of the initial power.",("M1","S undergoes four half-lives and L undergoes one; apply the factors separately before adding."),("A1",fr"$P={tex(ps/16)}+{tex(pl/2)}={tex(later)}\,\mathrm{{W}}$."),("A1",fr"Remaining fraction $={tex(later/total)}$; allow consistent ECF.")),
          part("Evaluate the claim that the component with greater activity must produce more heat and that the total power must halve every eight years.",("R1","Heat depends on energy deposited per decay as well as activity; L initially produces more heat despite its lower activity."),("R1","The total combines different decay rates, so it has no single fixed half-life during the mixed stage."))
        ];ps=pscheme
        diagram=None;solution=graph([(0,total),(8,later),(16,(8e14*.80*1.6e-13)/256+(3e14*2.4*1.6e-13)/4)],16,total*1.1,"time / years","total deposited heat power / W","Calculated powers for the two-product mixture",connect=False)
        check("E4 two-product later heat",later,64.0)
        check("E4 two-product surviving heat fraction",later/total,5/17)
        ps=pscheme
    add(4,"E4-F5 fission-product decay-heat interpretation",v,f"Cooling after shutdown {v+1}",stem,parts=ps,difficulty=["easy","easy","medium","hard"][v],data=v<3,diagram=diagram,solution=solution)
save()


# E.5 — light-nucleus fusion, stellar distances, HR positions, lifetimes and parallax data.
def parallax_picture():
    b=text(330,28,"Annual parallax geometry",size=18)+text(330,55,"The angle p uses half the annual baseline; not to scale.",size=13)
    b+=line(160,300,500,300,"#64748b",2)+line(330,82,330,300,"#64748b",1,True)+line(330,82,160,300,BLUE)+line(330,82,500,300,BLUE)
    for x,y,color in [(160,300,BLUE),(500,300,BLUE),(330,300,"#d99a17"),(330,82,RED)]:
        b+=f'<circle cx="{x}" cy="{y}" r="7" fill="{color}"/>'
    b+=text(160,330,"Earth: epoch 1",size=13)+text(500,330,"Earth: epoch 2",size=13)+text(330,330,"Sun",size=13)
    b+=text(355,83,"star",size=13,anchor="start")+text(310,145,"p",color=RED)+text(350,145,"p",color=RED)
    b+=text(245,280,"1 AU",size=13)+text(415,280,"1 AU",size=13)+text(330,365,"Distance is inferred from the small annual angular shift.",size=13)
    return svg(b,"Annual parallax with the half-angle p")
def hr_diagram(stars):
    X=lambda t:85+490*(math.log10(20000)-math.log10(t))
    Y=lambda l:315-235*(math.log10(l)+3)/8
    b=text(330,25,"Hertzsprung–Russell diagram",size=18)
    for t in [20000,10000,5000,2000]:
        b+=line(X(t),80,X(t),315,"#e2e8f0",1)+text(X(t),338,str(t),size=12)
    for l in [.001,.1,1,100,10000,100000]:
        b+=line(85,Y(l),575,Y(l),"#e2e8f0",1)+text(74,Y(l)+4,f"{l:g}",size=12,anchor="end")
    b+=line(85,80,85,315)+line(85,315,575,315)+text(330,370,"surface temperature / K (decreases to the right)")+text(85,61,"luminosity / solar luminosity",anchor="start",size=14)
    sequence=[(20000,10000),(12000,300),(6000,1),(3500,.05),(2500,.005)]
    b+=f'<polyline points="{" ".join(f"{X(t):.2f},{Y(l):.2f}" for t,l in sequence)}" fill="none" stroke="#8899aa" stroke-width="2" stroke-dasharray="5 5"/>'
    for name,t,l in stars:
        b+=f'<circle cx="{X(t):.2f}" cy="{Y(l):.2f}" r="5" fill="{RED}"/>'+text(X(t)+9,Y(l)-9,name,size=13,color=RED,anchor="start")
    b+=text(170,295,"dashed: illustrative main sequence",size=11)
    return svg(b,"HR diagram with decreasing temperature to the right")
channels=[
(r"$^2_1\mathrm{H}+^3_1\mathrm{H}\rightarrow{}^4_2\mathrm{He}+{}^1_0\mathrm{n}$",2.01355+3.01550,4.00151+1.00866,r"$m(^2\mathrm{H})=2.01355\,\mathrm{u}$, $m(^3\mathrm{H})=3.01550\,\mathrm{u}$, $m(^4\mathrm{He})=4.00151\,\mathrm{u}$ and $m_n=1.00866\,\mathrm{u}$"),
(r"$^2_1\mathrm{H}+^2_1\mathrm{H}\rightarrow{}^3_2\mathrm{He}+{}^1_0\mathrm{n}$",2*2.01355,3.01493+1.00866,r"$m(^2\mathrm{H})=2.01355\,\mathrm{u}$, $m(^3\mathrm{He})=3.01493\,\mathrm{u}$ and $m_n=1.00866\,\mathrm{u}$"),
(r"$^2_1\mathrm{H}+^2_1\mathrm{H}\rightarrow{}^3_1\mathrm{H}+{}^1_1\mathrm{H}$",2*2.01355,3.01550+1.00728,r"$m(^2\mathrm{H})=2.01355\,\mathrm{u}$, $m(^3\mathrm{H})=3.01550\,\mathrm{u}$ and $m_p=1.00728\,\mathrm{u}$"),
(r"$^1_1\mathrm{H}+^2_1\mathrm{H}\rightarrow{}^3_2\mathrm{He}+\gamma$",1.00728+2.01355,3.01493,r"$m_p=1.00728\,\mathrm{u}$, $m(^2\mathrm{H})=2.01355\,\mathrm{u}$ and $m(^3\mathrm{He})=3.01493\,\mathrm{u}$")
]
for v,(reaction,mi,mf,givens) in enumerate(channels):
    defect=mi-mf;energy=defect*931.5
    add(5,"E5-F1 fusion mass defect and released energy",v,f"Energy in light-nucleus fusion {v+1}","Consider the fusion channel "+reaction+". Nuclear masses are "+givens+r". Use $1\,\mathrm{u}c^2=931.5\,\mathrm{MeV}$. Which is the energy released per reaction? Neglect initial kinetic energy.",
      options=[qty(x,"MeV",3) for x in [energy,-energy,defect,2*energy]],
      reason=fr"The total rest mass decreases by ${tex(defect,5)}\,\mathrm{{u}}$, so $Q=\Delta mc^2={tex(energy)}\,\mathrm{{MeV}}$ is released. The reaction energy is the difference of total masses, not the mass defect written with the wrong unit.",difficulty="easy")
    check(f"E5 fusion mass-energy recovery {v+1}",mf+energy/931.5,mi)
for v,(parallax,fluxratio) in enumerate([(.025,1),(.040,2),(.050,3),(.080,4)]):
    reference=.100;ratio=fluxratio*(reference/parallax)**2
    add(5,"E5-F2 parallax distance and inverse-square luminosity",v,f"Comparing two stars by parallax {v+1}",
      fr"Star X has annual parallax ${parallax:.3f}$ arcseconds and star Y has parallax $0.100$ arcseconds. X's measured energy flux is ${fluxratio:.1f}$ times Y's. Neglect absorption. Use $d/\mathrm{{pc}}=1/(p/\mathrm{{arcsec}})$ and $b=L/(4\pi d^2)$. What is $L_X/L_Y$?",
      options=[fr"${tex(x,4)}$" for x in [ratio,fluxratio,fluxratio*(parallax/reference)**2,fluxratio*reference/parallax]],
      reason=fr"The distance ratio is $d_X/d_Y=p_Y/p_X={tex(reference/parallax,4)}$. Therefore $L_X/L_Y=(b_X/b_Y)(d_X/d_Y)^2={tex(ratio,4)}$; equal observed brightness need not mean equal luminosity.",diagram=parallax_picture())
    check(f"E5 luminosity inverse-square recovery {v+1}",ratio/(reference/parallax)**2,fluxratio)
for v,(temperature,hot,luminosity) in enumerate([(4000,12000,64),(4500,15000,81),(5000,10000,100),(3500,14000,49)]):
    radius=math.sqrt(luminosity)*(6000/temperature)**2;hotradius=math.sqrt(luminosity)*(6000/hot)**2
    add(5,"E5-F3 HR positions and stellar radius inference",v,f"Two equally luminous stars {v+1}",
      fr"Stars X and Y each have luminosity ${luminosity}L_\odot$. X has surface temperature ${temperature}\,\mathrm{{K}}$ and Y has ${hot}\,\mathrm{{K}}$. Model their surfaces as blackbodies and take the Sun's temperature as $6000\,\mathrm{{K}}$. Use $L=4\pi R^2\sigma T^4$. The diagram includes an illustrative main sequence for comparison.",
      parts=[
        part("Find each stellar radius in units of the solar radius.",("M1",r"Divide by the solar relation to obtain $R/R_\odot=\sqrt{L/L_\odot}(T_\odot/T)^2$."),("A1",fr"X: $R_X={tex(radius)}R_\odot$."),("A1",fr"Y: $R_Y={tex(hotradius)}R_\odot$.")),
        part("Explain how stars with the same luminosity can occupy these different HR positions.",("R1","The cooler star emits less energy per unit surface area, so a larger surface area compensates."),("R1","Temperature distinguishes their horizontal positions, while equal luminosity places them at the same vertical position.")),
        part("Compare X with main-sequence stars of similar surface temperature and identify its broad region on the diagram.",("R1","X is much more luminous and larger than main-sequence stars of similar temperature, placing it in the giant region above the main sequence."))
      ],diagram=hr_diagram([("X",temperature,luminosity),("Y",hot,luminosity),("Sun",6000,1)]))
    check(f"E5 radius luminosity round-trip {v+1}",radius**2*(temperature/6000)**4,luminosity)
    check(f"E5 equal luminosity radius ratio {v+1}",radius/hotradius,(hot/temperature)**2)
for v,(massratio,lumratio) in enumerate([(1.0,1.0),(1.5,5.0),(2.0,10.0),(3.0,30.0)]):
    mass=massratio*2e30;lum=lumratio*3.8e26;fuel=.10*.70*mass;available=.007*fuel*C**2;lifetime=available/lum/3.156e7
    b=text(330,30,"Simplified stellar fuel model",size=18)
    b+='<circle cx="330" cy="210" r="115" fill="#fff1cc" stroke="#ad7c16" stroke-width="2"/><circle cx="330" cy="210" r="48" fill="#f8b398" stroke="#ad3b27" stroke-width="2"/>'
    b+=text(330,203,"fusion core",size=13)+text(330,223,"0.10 M",size=13)+text(330,365,"Core size is schematic; the label is a mass fraction.",size=13)
    sb=text(330,25,f"Model evolution: {massratio:g} solar {'mass' if massratio==1 else 'masses'}",size=17)
    stages=[("Core hydrogen is exhausted","Core contracts and warms; shell fusion develops."),("Envelope expands","The surface becomes cooler: giant stage."),("Outer layers are ejected","A compact core remains in this stated scenario."),("White dwarf cools","No sustained fusion; luminosity declines.")]
    for i,(heading,detail) in enumerate(stages):
        y=55+i*80;sb+=f'<rect x="55" y="{y}" width="550" height="60" rx="6" fill="#f7f3ec" stroke="#8a7963"/>'+text(330,y+23,heading,size=15)+text(330,y+44,detail,size=12)
        if i<3:sb+=arrow(330,y+60,330,y+79)
    add(5,"E5-F4 fusion fuel budgets and stellar evolution",v,f"A model stellar lifetime {v+1}",
      fr"A main-sequence star has mass ${massratio:.1f}M_\odot$ and constant model luminosity ${lumratio:.1f}L_\odot$. Only $0.10$ of its mass participates in core hydrogen burning; $0.70$ of that participating mass is hydrogen. Fusion converts $0.0070$ of the consumed hydrogen mass into released energy. Take $M_\odot=2.00\times10^{{30}}\,\mathrm{{kg}}$, $L_\odot=3.80\times10^{{26}}\,\mathrm{{W}}$, $c=3.00\times10^8\,\mathrm{{m\,s^{{-1}}}}$ and one year as $3.156\times10^7\,\mathrm{{s}}$. Assume all the released energy contributes to the luminosity.",
      parts=[
        part("Estimate the available fusion energy and the duration of core hydrogen burning.",("M1",r"Available energy $E=(0.10)(0.70)(0.0070)Mc^2$."),("A1",fr"$E={tex(available)}\,\mathrm{{J}}$."),("M1",r"Use $t=E/L$ and convert seconds to years."),("A1",fr"$t\approx{tex(lifetime)}\,\mathrm{{years}}$. Accept rounding with the supplied year conversion.")),
        part("A comparison star has twice the mass and ten times the luminosity, with the same usable fractions. Compare its model lifetime.",("M1",r"Usable fuel energy scales with mass, so $t'/t=2/10$."),("R1","Its lifetime is 0.20 times as long: a greater fuel supply is outweighed by a much greater rate of energy release.")),
        part("Explain why a sufficiently hot stellar core can sustain fusion and how a star is supported during a stable stage.",("R1","High temperature supplies large particle kinetic energies, increasing the chance of close nuclear encounters despite electric repulsion."),("R1","An outward pressure gradient, from thermal gas and/or radiation pressure, balances inward gravitational force.")),
        part("In the stated low-mass evolutionary scenario, core hydrogen is exhausted and outer layers are eventually ejected without core collapse. Name the remnant and describe its subsequent energy source.",("A1","The remnant is a white dwarf."),("R1","It cools by radiating stored internal energy; it has no sustained core fusion."))
      ],difficulty="hard",diagram=svg(b,"Core mass fraction in a stellar model"),solution=svg(sb,"A low-mass stellar evolution path"))
    check(f"E5 stellar fuel mass recovery {v+1}",available/(.007*C**2),fuel)
    check(f"E5 stellar time back-substitution {v+1}",lifetime*3.156e7*lum,available)
for v in range(4):
    if v<2:
        p=[.025,.040][v];distance=1/p;months=[0,3,6,9,12];shifts=[p,0,-p,0,p]
        stem="The table contains simulated angular positions of a nearby star relative to distant background sources after removing any steady proper motion. The observing geometry gives the full annual parallax amplitude along this measured direction."+table(["month","angular displacement / arcsec"],[(t,f"{x:.3f}") for t,x in zip(months,shifts)])+r"\n\nUse $d/\mathrm{pc}=1/(p/\mathrm{arcsec})$."
        ps=[part("Find the annual parallax p from the peak-to-peak change.",("M1","The annual parallax is half the peak-to-peak angular displacement."),("A1",fr"$p={p:.3f}$ arcseconds.")),
          part("Calculate the distance and describe the expected position after another full year.",("A1",fr"$d={tex(distance)}\,\mathrm{{pc}}$."),("R1","The annual parallax pattern repeats; after two years the position returns to the same point in this proper-motion-corrected model."))]
        diagram=graph(list(zip(months,shifts)),12,p*1.4,"time / months","angular displacement / arcsec","Constructed annual parallax record",ymin=-p*1.4);solution=None
        check(f"E5 parallax reciprocal {v+1}",distance*p,1)
    elif v==2:
        p=.050;distance=1/p;flux=3e-10;peak=500e-9;temp=2.90e-3/peak;lum=4*math.pi*(distance*3.09e16)**2*flux;radius=math.sqrt(lum/(4*math.pi*5.67e-8*temp**4))
        stem=r"A simulated stellar dataset gives annual parallax $0.0500$ arcseconds, received energy flux $3.00\times10^{-10}\,\mathrm{W\,m^{-2}}$, and a blackbody spectral peak at $500\,\mathrm{nm}$. Neglect absorption and use $d/\mathrm{pc}=1/(p/\mathrm{arcsec})$, $1\,\mathrm{pc}=3.09\times10^{16}\,\mathrm{m}$, $\lambda_{\max}T=2.90\times10^{-3}\,\mathrm{m\,K}$ and $\sigma=5.67\times10^{-8}\,\mathrm{W\,m^{-2}\,K^{-4}}$."
        ps=[part("Find the distance and surface temperature.",("A1",fr"$d={tex(distance)}\,\mathrm{{pc}}={tex(distance*3.09e16)}\,\mathrm{{m}}$."),("M1",r"Apply Wien's relation with the wavelength in metres."),("A1",fr"$T={tex(temp)}\,\mathrm{{K}}$.")),
          part("Estimate the luminosity and stellar radius.",("M1",r"$L=4\pi d^2b$, then $R=\sqrt{L/(4\pi\sigma T^4)}$."),("A1",fr"$L={tex(lum)}\,\mathrm{{W}}$."),("A1",fr"$R={tex(radius)}\,\mathrm{{m}}$. Accept consistent ECF from distance or temperature.")),
          part("Explain the effect of unrecognized absorption on the radius estimate if parallax and temperature remain correct.",("R1","Absorption reduces the received flux, so inferred luminosity is too small; at fixed temperature the inferred radius is also too small."))
        ];diagram=parallax_picture();solution=hr_diagram([("inferred star",temp,lum/3.8e26),("Sun",6000,1)])
        check("E5 radius flux round-trip",5.67e-8*temp**4*(radius/(distance*3.09e16))**2,flux)
    else:
        mu,p=.12,.04;times=[0,.25,.5,.75,1];positions=[mu*t+p*math.sin(2*math.pi*t) for t in times];distance=1/p;flux=2e-10;lum=4*math.pi*(distance*3.09e16)**2*flux
        stem=r"A star's measured displacement is modelled by $x(t)=\mu t+p\sin(2\pi t)$, where $t$ is time in years, $\mu$ is steady proper motion in arcseconds per year and $p$ is annual parallax in arcseconds. The annual phase is known. The constructed measurements below are rounded to the shown precision."+table(["t / years","x / arcsec"],[(f"{t:.2f}",f"{x:.3f}") for t,x in zip(times,positions)])+r"\n\nIts received flux is $2.00\times10^{-10}\,\mathrm{W\,m^{-2}}$. Use $d/\mathrm{pc}=1/(p/\mathrm{arcsec})$ and $1\,\mathrm{pc}=3.09\times10^{16}\,\mathrm{m}$. Neglect absorption."
        ps=[part("Determine proper motion and annual parallax from the measurements.",("M1","At zero and one year the sinusoidal term is zero; the endpoint difference gives the steady drift."),("A1",r"$\mu=0.120\,\mathrm{arcsec\,year^{-1}}$."),("M1",r"At $t=0.25$ subtract $\mu t=0.030$ arcsec from $x=0.070$ arcsec."),("A1",r"$p=0.0400$ arcsec.")),
          part("Find the distance and luminosity.",("M1",r"Use the corrected parallax to find distance, then $L=4\pi d^2b$."),("A1",fr"$d={distance:g}\,\mathrm{{pc}}$ and $L={tex(lum)}\,\mathrm{{W}}$. Accept ECF from the inferred parallax.")),
          part("A student uses half the difference between the positions at 0.25 and 0.75 years as p, without removing proper motion. Quantify the distance error.",("M1",r"This gives $p_{\rm wrong}=(0.070-0.050)/2=0.0100$ arcsec, hence $d_{\rm wrong}=100\,\mathrm{pc}$."),("R1","The distance is four times the correct value because the steady drift partly cancels the annual displacement difference."))
        ];diagram=graph(list(zip(times,positions)),1,.14,"time / years","observed displacement / arcsec","Annual motion with a steady drift");solution=graph([(t,p*math.sin(2*math.pi*t)) for t in [i/20 for i in range(21)]],1,.05,"time / years","displacement after drift removal / arcsec","Recovered annual parallax motion",ymin=-.05)
        check("E5 proper-motion recovery",positions[-1]-positions[0],mu);check("E5 annual amplitude recovery",positions[1]-mu*.25,p)
    add(5,"E5-F5 stellar observation inversion and parallax calibration",v,f"Interpreting a stellar observation {v+1}",stem,parts=ps,difficulty=["easy","easy","medium","hard"][v],data=v<3,diagram=diagram,solution=solution)
save(final=True)
