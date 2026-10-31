"""Compact, loss-aware display for independent human-readable family review."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[2]
topics=['introduction-business','human-resources','finance-accounts','marketing','operations-management']
unit=int(sys.argv[1]);lo=int(sys.argv[2]);hi=int(sys.argv[3])
qs=json.loads((ROOT/'content/ib/business-management'/(topics[unit-1]+'.json')).read_text(encoding='utf-8'))
for q in qs:
 if not lo<=q['number']<=hi:continue
 print('\n'+q['id']+' '+q['syllabusCode']+' '+q['level']+' '+q['subtopic'])
 print(q['stem'].replace('All organizations and data in this question are fictional.\n\n',''))
 if q['number']%4==1:print('ASK: '+' / '.join(p['prompt'] for p in q['parts']))
 # Eight-mark sets have no band: show their two applied explanation chains.
 # In evaluative sets show the specific indicative answer once, not again as
 # the preceding four-mark scaffolding. Definitions are displayed once/family.
 for p,g in zip(q['parts'],q['markScheme']):
  if p['label']=='a' and q['number']%4!=1:continue
  if any('rubric' in h for h in q['markScheme']) and 'rubric' not in g and p['marks']==4:continue
  text=' | '.join(s['text'] for s in g['steps'])
  text=text.replace('Alternative recommendations earn full credit when supported by the case and a coherent response to the counterargument.','')
  if 'Evidence limitation:' in text:text=text.split(' Apply best fit:')[0]
  print(p['label']+': '+text)
