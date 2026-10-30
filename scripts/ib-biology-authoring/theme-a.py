"""Rebuild the 144 original Unity and diversity records and author ledger."""
import json,random
from a_common import Bank,ROOT
import a_molecules,a_cells,a_organisms,a_ecosystems
B=Bank()
for module in (a_molecules,a_cells,a_organisms,a_ecosystems):module.build(B)
# Bounded additions after independent review preserve the 16-question topic structure.
def append_part(number,prompt,*answers):
    q=B.qs[number-1];label=chr(97+len(q['parts']))
    q['parts'].append({'label':label,'prompt':prompt,'marks':len(answers)})
    q['markScheme'].append({'part':label,'steps':[{'code':'A1','text':answer} for answer in answers]})
    q['marks']+=len(answers)
append_part(49,'Draw a simplified diagram of B, label two visible structural features, and annotate its main function.',
    'A clear chloroplast outline with a double envelope and internal membrane stacks correctly shown and labelled; both visible features required.',
    'Annotation identifies photosynthesis as the main function. The drawing is based on the supplied schematic, not presented as a specimen measurement.')
B.qs[55]['stem']='The following descriptions are constructed for this question. Sample X is a typical Gram-positive bacterium such as Bacillus: it has a cell wall, plasma membrane, cytoplasm, a loop of DNA in a nucleoid and 70S cytoplasmic ribosomes. Sample Y has a nucleus, mitochondria and 80S cytoplasmic ribosomes.'
append_part(56,'Name two types of filaments in the eukaryotic cytoskeleton.',
    'One correct type: microtubules, microfilaments (actin filaments) or intermediate filaments.',
    'A second distinct correct type from those listed; do not award the same type twice.')
B.qs[56]['parts'][1]['prompt']='Compare two structural features with a typical photosynthetic plant cell.'
append_part(60,'State one advantage of electron microscopy over conventional light microscopy and one advantage of cryogenic electron microscopy over preparation involving dehydration.',
    'Electron microscopy can resolve much smaller structural details than conventional light microscopy.',
    'Rapid freezing preserves specimens in a hydrated state closer to their native organization and reduces some preparation artefacts associated with drying or chemical treatment.')
append_part(60,'Explain why freeze-fracture can be useful when studying cell membranes.',
    'Fracturing frozen material can expose faces within the lipid bilayer, revealing the distribution of embedded membrane proteins.')
B.qs[65]['stem']='A constructed comparison summarizes three viral structures. X, a coronavirus, has a lipid envelope and a single-stranded RNA genome. Y, bacteriophage lambda, is non-enveloped with double-stranded DNA. Z, HIV, also has an RNA genome within a protein capsid and an outer lipid envelope.'
B.qs[65]['parts'][0]['prompt']='State two structural differences between X and Y supported by the descriptions.'
B.qs[65]['parts'][1]['prompt']='State a structural component that both X and Y possess.'
append_part(66,'Explain why detecting RNA alone would not distinguish X from Z.',
    'Both carry RNA; additional evidence such as genome sequence or specific viral proteins is needed to distinguish them.')
B.qs[95]['markScheme'][2]['steps'][0]['text']='Laboratory blanks test contamination from reagents or laboratory processing. Field blanks would be needed to assess contamination introduced during sampling.'
B.qs[126]['stem']='Hybridization and polyploidy have generated species in Persicaria (knotweeds or smartweeds). The following constructed chromosome model illustrates that mechanism; its counts are not measurements of a named Persicaria species. Two plant species each produce gametes containing 10 chromosomes. Their hybrid has one set from each species and is sterile because the sets cannot pair effectively. Chromosome doubling occurs in a cell that forms a new reproductive shoot.'
B.qs[135]['stem']='Canals, levees and drainage have degraded and fragmented wetlands in the Florida Everglades. A constructed regional model illustrates one possible effect on ecosystem variety: six distinct wetland types occur initially, but drainage eliminates all examples of two types, while some areas of the other four remain. The six-type counts are model inputs, not a survey of the real Everglades.'
append_part(136,'Explain why altering water flow can change the biological community even where wetland area remains.',
    'Changing the duration or depth of flooding changes habitat conditions, favouring different organisms and potentially eliminating species adapted to the former water regime.')
append_part(144,'Explain two reasons estimates of the total number of living species on Earth remain uncertain.',
    'Many species remain undiscovered or poorly sampled, especially in inaccessible habitats or among small and cryptic organisms.',
    'Different interpretations of species boundaries can split or combine groups, changing the number recognized from the same underlying diversity.')
B.review[48]['authorReview']+=' Independent review added an annotated drawing from the original schematic, with no claim that it is a micrograph.'
B.review[55]['statements']='A2.2.5-6, A2.2.8'
B.review[59]['statements']='A2.2.3'
B.review[65]['statements']='A2.3.1-2'
B.review[135]['authorReview']+=' Named second ecosystem-loss case checked against South Florida Water Management District; numerical categories explicitly constructed.'
B.review[143]['statements']='A4.2.2, A4.2.5-6'
easy={1,6,10,15,17,19,20,23,35,39,43,49,52,55,65,68,77,81,84,91,98,100,105,108,113,118,123,129,139}
hard={16,30,32,40,48,60,63,70,78,80,83,93,96,103,106,109,111,121,124,127,128,137,141,142,143,144}
for q in B.qs:q['difficulty']='easy' if q['number'] in easy else 'hard' if q['number'] in hard else 'medium'
mcqs=[q for q in B.qs if q['questionType']=='multiple-choice']
targets=list('ABCD')*(len(mcqs)//4)+list('ABCD')[:len(mcqs)%4]
random.Random('biology-theme-a-balanced-answer-key').shuffle(targets)
for q,target in zip(mcqs,targets):
    correct=next(o['text'] for o in q['options'] if o['label']==q['correctOption'])
    distractors=[o['text'] for o in q['options'] if o['label']!=q['correctOption']]
    random.Random('biology-theme-a-distractors-'+q['id']).shuffle(distractors)
    distractors.insert('ABCD'.index(target),correct)
    q['options']=[{'label':label,'text':text} for label,text in zip('ABCD',distractors)]
    q['markScheme'][0]['steps'][0]['text']=q['markScheme'][0]['steps'][0]['text'].replace('Option '+q['correctOption']+'.','Option '+target+'.',1)
    q['correctOption']=target
registry=json.loads((ROOT/'content/ib/biology-image-sources.json').read_text(encoding='utf8'))
image_entry=next(e for e in registry['assets'] if any(u['id']=='ib-bio-a-049' for u in e['uses']))
B.qs[48].update(diagramUrl=image_entry['url'],diagramCaption=image_entry['caption'])
assert not B.qs[48].get('diagramSvg')
for number,url in {
    132:'https://www.doc.govt.nz/globalassets/documents/science-and-technical/mainlanda.pdf',
    133:'https://repository.library.noaa.gov/view/noaa/17045/noaa_17045_DS1.pdf',
    134:'https://www.nma.gov.au/defining-moments/resources/extinction-of-thylacine',
    136:'https://www.sfwmd.gov/our-work/everglades',
}.items():
    B.review[number-1]['sourceUrls']=B.review[number-1]['sourceUrls']+[url]
B.write()
