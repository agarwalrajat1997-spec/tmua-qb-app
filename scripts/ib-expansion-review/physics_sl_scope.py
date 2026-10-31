"""Independent whole-record SL scope audit of the 420 previously core records.

The input snapshot records the review population before any promotions. It is
retained so that promoted records do not disappear from the audit population.
"""
from pathlib import Path
import json,re,hashlib
from collections import Counter

ROOT=Path(__file__).resolve().parents[2];DEST=ROOT/'docs/ib-expansion-reviews'
source=DEST/'physics-sl-independent-scope-input.json'
before=json.loads(source.read_text(encoding='utf-8'))
assert len(before)==420
promote={'ib-phy-d-007','ib-phy-d-037'}
fixes=[]

# Preserve all question IDs and wording. Only correct highest-demand metadata.
for p in (ROOT/'content/ib/physics-hl').glob('*.json'):
    qs=json.loads(p.read_text(encoding='utf-8'));changed=False
    for q in qs:
        if q['id'] in promote and q['level']!='ahl':
            q['level']='ahl';q['verification']['notes']+=' Independent SL scope review 2026-10-31: promoted to AHL because determining circular-orbit speed from GM and radius is in the D.1 AHL list, although lower-level force equations can be combined to derive it.';changed=True
            fixes.append({'id':q['id'],'change':'core → ahl','reason':'The highest assessed demand includes the explicitly AHL circular-orbit speed expression.'})
        if q['syllabusCode']=='C.4':
            # The current guide specifies first harmonic rather than these
            # older alternatives. No such legacy occurrences remained at audit.
            def words(v):
                if isinstance(v,str):return re.sub(r'\bfundamental\b','first harmonic',v,flags=re.I)
                if isinstance(v,list):return [words(x) for x in v]
                if isinstance(v,dict):return {k:words(x) if k in ['stem','prompt','text','title','parts','markScheme'] else x for k,x in v.items()}
                return v
            updated=words(q)
            if updated!=q:q.clear();q.update(updated);changed=True;fixes.append({'id':q['id'],'change':'first-harmonic terminology'})
    if changed:p.write_text(json.dumps(qs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

# Update the simple original classification at the source without running its
# whole-bank generator, which would overwrite the new SL additions.
author=ROOT/'scripts/ib-physics-authoring/fields.py'
text=author.read_text(encoding='utf-8')
lines=text.splitlines();hits=0
for i,line in enumerate(lines):
    if "add('D.1','Timing a mapping satellite'" in line:
        if "level='ahl'" not in line:lines[i]=line.replace("],diagram=orbit('r'))", "],level='ahl',diagram=orbit('r'))")
        assert "level='ahl'" in lines[i];hits+=1
assert hits==1
new='\n'.join(lines)+'\n'
if new!=text:author.write_text(new,encoding='utf-8',newline='\n')

qs=[q for p in (ROOT/'content/ib/physics-hl').glob('*.json') for q in json.loads(p.read_text(encoding='utf-8'))];byid={q['id']:q for q in qs}
reasons={
 'A.1':'Shared vector kinematics, constant-acceleration/projectile calculations, graph interpretation and measurement uncertainty. Resistive/terminal descent is qualitative; no resisted-projectile calculation.',
 'A.2':'Shared Newtonian force vectors, circular motion, buoyancy/viscosity, one-dimensional impulse and collisions. Static two-direction force resolution is not a two-dimensional collision; no core record requires two-dimensional collision/explosion calculations.',
 'A.3':'Shared work, kinetic/gravitational/elastic energy, non-conservative transfer, efficiency and power. Spring energy applications do not require AHL phase-time or quantitative SHM-energy formulae.',
 'B.1':'Shared temperature/internal-energy interpretation, heat capacity/latent heat, conduction and black-body radiation with units, model assumptions or uncertainty.',
 'B.2':'Shared greenhouse mechanisms and explicitly defined radiative energy balances, albedo, emissivity and simple planetary models.',
 'B.3':'Shared ideal-gas states and kinetic model, rms molecular speed and monatomic energy. No first-law engine cycle, entropy or adiabatic-process calculation.',
 'B.5':'Shared DC series/parallel circuits, emf/internal resistance, resistivity, sensor dividers and measurement loading. No AC analysis.',
 'C.1':'Shared restoring acceleration a=−ω²x, angular frequency/period and mass–spring or small-angle pendulum scaling. No phase-time solution or quantitative SHM-energy demand.',
 'C.2':'Shared travelling-wave model, snapshots/time traces, frequency/wavelength/speed, boundary behaviour and data uncertainty.',
 'C.3':'Shared reflection/refraction/critical angle, superposition and coherent double-source/double-slit interference. No grating or single-slit intensity/minimum calculation.',
 'C.4':'Shared displacement standing-wave boundary conditions, nth harmonic, phase between standing-wave loops, resonance and qualitative damping. First-harmonic terminology; no pipe end-correction or pressure-node requirement.',
 'C.5':'Shared qualitative sound/EM Doppler and wavefront reasoning, or low-speed spectral-line shift Δλ/λ≈v/c. No quantitative mechanical moving-source/observer equation.',
 'D.1':'Shared Newtonian gravity, field strength/direction and line-restricted superposition, or qualitative circular acceleration. No gravitational potential, escape energy or orbital-speed calculation after the two promotions.',
 'D.2':'Shared Coulomb force, field strength, one-dimensional electric superposition, charge quantization/transfer, conductors and magnetic field directions. No electric-potential or equipotential work calculation.',
 'D.3':'Shared uniform electric/magnetic forces, transverse motion, selector and magnetic radius. Voltage-energy comparisons use shared B.5 V=W/q plus D.3 dynamics, not AHL radial-potential machinery.',
 'E.1':'Shared atomic particle inventory and photon energy from supplied energy-level differences. No Bohr model, nuclear-radius formula or closest-approach/scattering calculation.',
 'E.3':'Shared nuclear decay accounting, radiation properties, background correction and integer-half-life changes. No decay constant or arbitrary-time exponential calculation.',
 'E.4':'Shared fission reaction/energy/reactor component reasoning, with models explicitly supplied. Thermal-decay cases use integer half-lives or ratios of displayed observations; no arbitrary-time decay equation is required.',
 'E.5':'Shared fusion/stellar radiation, parallax, HR interpretation, supplied-fraction lifetime estimates and qualitative stellar evolution. No Cepheid requirement.'
}
rows=[]
for old in before:
    q=byid[old['id']];reason=reasons[q['syllabusCode']]
    decision='retain core'
    if q['id'] in promote:decision='promote to ahl';reason='Explicitly determines v=sqrt(GM/r), which the guide places in D.1 AHL. The following period calculation depends on that result. Whole record promoted while its original ID, values and wording are preserved.'
    if q['id'] in ['ib-phy-c-098','ib-phy-c-100']:reason+=' Specifically reviewed: qualitative acoustic Doppler is expressly shared; only the mechanical observed-frequency equations are AHL.'
    if q['id'] in ['ib-phy-d-069','ib-phy-d-089']:reason+=' Specifically reviewed against B.5 work-per-charge definition and D.3 circular magnetic motion; retained by the shared-equation route.'
    if q['id'] in ['ib-phy-e-079','ib-phy-e-080']:reason+=' Specifically reviewed despite mixed isotope heat: numerical operations are ratios of given data or separate integer half-lives, not arbitrary-time exponentials.'
    rows.append({'id':q['id'],'syllabusCode':q['syllabusCode'],'priorLevel':'core','finalLevel':q['level'],'decision':decision,'scopeReason':reason,'sha256':hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()})
report={'status':'passed with two corrected legacy classifications','population':420,'retainedCore':sum(r['finalLevel']=='core' for r in rows),'promotedAhl':sorted(promote),'allBankQuestions':len(qs),'finalSlAvailable':sum(q['level']=='core' for q in qs),'wholeHlTopicsForbidden':['A.4','A.5','B.4','D.4','E.2'],'sourceAuthority':'Corrected2026 guide as recorded in docs/ib-physics-reviews/syllabus-blueprint.json. Official initial2025 guide independently inspected for unchanged C.1/C.3/C.4/C.5/D.1/D.2/D.3/B.5 boundaries; corrected stellar-pressure and assessment details retained from the current blueprint.','guide':'https://xmltwo.ibo.org/publications/EAD/2026_EN/GR4/GR4-Physics_EN.pdf','secondaryOfficialCopy':'https://www.ibo.org/globalassets/new-structure/university-admission/pdfs/subject-guides/physics-guide.pdf','reviewLimits':'All420 original core records reviewed for highest syllabus demand by prompt/solution families and targeted per-record checks. This is a scope review, not a new independent numerical/diagram re-verification of the420 legacy questions. All100 additions have a separate complete displayed-input numerical review and all32 addition figures have been visually inspected.','records':rows,'fileHashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'content/ib/physics-hl').glob('*.json')}}
assert not [q['id'] for q in qs if q['level']=='core' and q['syllabusCode'] in report['wholeHlTopicsForbidden']]
(DEST/'physics-sl-independent-scope.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['records','fileHashes']},ensure_ascii=False,indent=2))
