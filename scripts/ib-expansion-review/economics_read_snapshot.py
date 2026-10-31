"""Lossless text projection for independent family and variant review (no author imports)."""
from pathlib import Path
import json,sys,difflib
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[2]
qs={q['id']:q for p in (ROOT/'content/ib/economics').glob('*.json') for q in json.loads(p.read_text(encoding='utf8'))}
ledger=json.loads((ROOT/'docs/ib-expansion-reviews/economics-ledger.json').read_text(encoding='utf8'))
families={}
for row in ledger:families.setdefault(row['family'],[]).append(qs[row['id']])
def fields(q):
    result={'stem':q['stem']}
    for p,g in zip(q['parts'],q['markScheme']):
        result[p['label']+' prompt']=f"[{p['marks']}] "+p['prompt']
        result[p['label']+' answer']=' | '.join(s['code']+': '+s['text'] for s in g['steps'])
        if 'rubric' in g:result[p['label']+' rubric']=json.dumps(g['rubric'],ensure_ascii=False,separators=(',',':'))
    return result
topic=sys.argv[1] if len(sys.argv)>1 else 'introduction'
start=int(sys.argv[2]) if len(sys.argv)>2 else 0
end=int(sys.argv[3]) if len(sys.argv)>3 else 999
keys=[k for k,a in families.items() if a[0]['topicId']==topic]
for family in keys[start:end]:
    records=families[family];base=records[0];basefields=fields(base)
    print('\nFAMILY',family,base['syllabusCode'],base['level'],base['examStyle'],[q['id'] for q in records])
    for key,value in basefields.items():
        # Repeated band language is separately verified at every record. Retain focus.
        if key.endswith(' rubric'):
            rr=json.loads(value);print(key,rr['maxMarks'],[x['descriptor'].split('Focus: ')[-1] for x in rr['bands']][-1])
        else: print(key+':',value)
    for q in records[1:]:
        print('VARIANT',q['id']);variant=fields(q)
        for key,value in variant.items():
            if value==basefields.get(key):continue
            if key.endswith(' rubric'):
                rr=json.loads(value);print(key,rr['maxMarks'],rr['bands'][-1]['descriptor'].split('Focus: ')[-1]);continue
            if key=='stem':print('stem:',value);continue
            a=basefields.get(key,'').split(' | ');b=value.split(' | ')
            changed=[s for s in b if s not in a];print(key+':',' | '.join(changed) if changed else value)
