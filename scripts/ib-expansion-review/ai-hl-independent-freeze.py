"""Bind the AI HL independent disposition to final UTF-8/LF content and audits."""
from pathlib import Path
import json,hashlib,collections
ROOT=Path(__file__).resolve().parents[2]
DOCS=ROOT/'docs/ib-expansion-reviews'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
review_path=DOCS/'ai-hl-independent-review.json'
review=json.loads(review_path.read_text(encoding='utf8'))
author=json.loads((DOCS/'ai-hl-author-freeze.json').read_text(encoding='utf8'))
numeric=json.loads((DOCS/'ai-hl-numeric-audit.json').read_text(encoding='utf8'))
structural=json.loads((DOCS/'ai-hl-author-audit.json').read_text(encoding='utf8'))
assert review['status']=='passed' and review['questionCount']==500 and len(review['records'])==500
assert not review['failures'] and all(r['status']=='passed' for r in review['records'])
assert len({r['id'] for r in review['records']})==500
assert numeric['status']=='passed' and numeric['records']==500 and structural['errors']==[]
assert review['scalarComparisons']==sum(r['scalarComparisons'] for r in review['records'])==1912
assert review['figures']['uniqueDiagrams']==43 and review['figures']['diagramUses']==52
assert len(review['corrections'])==review['correctionCount']==55
assert all(r['reasons'] for r in review['corrections'])
expected={Path(x['path']).name:x['sha256'] for x in author['files']}
assert review['canonicalFiles']==numeric['bankHashes']==expected
for name,sha in expected.items():
 p=ROOT/'content/ib/math-ai-hl'/name
 raw=p.read_bytes();assert raw.decode('utf8') and b'\r' not in raw and not raw.startswith(b'\xef\xbb\xbf')
 assert digest(p)==sha
for sheet in review['figures']['sheets']:
 assert digest(ROOT/sheet['path'])==sheet['sha256']
notes=collections.defaultdict(list)
for r in review['corrections']:
 for reason in r['reasons']:notes[reason].append(r['id'])
lines=['# AI HL independent review','',
 'Passed: all 500 records, 125 problem families and four variants per family. The review applies to the first-assessment-2021 course through November 2028. No unresolved findings remain in the reviewed files.','',
 'The reviewer did not author the original bank. Essential corrections were applied under the integrating agent’s authorization, regenerated from source, and rechecked against the serialized questions. The report preserves exact before/after field changes and per-record hashes.','',
 '## Evidence','',
 f"- {review['scalarComparisons']} independent scalar comparisons, with reconstructed values and family-specific mathematical/semantic decisions for every ID.",
 f"- {review['displayPrecisionChecks']} explicit display/domain/bound checks, including exact decimal tie cases, formal composition domains and excluded strict convergence boundaries.",
 '- Cash-flow sums, discrete probability enumeration, independent least-squares fitting, all-pairs shortest paths, exhaustive tours, symbolic differentiation, quadrature, matrix exponentials and simultaneous old-state Euler iteration were reconstructed from learner-visible data. Original author modules were not imported. The author ledger was used only for comparison after reconstruction.',
 '- All 43 unique serialized SVGs (52 uses) were independently rasterized; four contact sheets were visually inspected. Public data, private solution points, graph edges/weights, coordinate scales and mathematical directions were checked.',
 f"- Refreshed author audits also pass: {numeric['checks']} numerical ledger fields and {structural['formulaeValidated']} KaTeX formula occurrences. These support, but do not replace, the independent replay.",
 f"- Difficulty after review: {review['difficulty']['easy']} easy, {review['difficulty']['medium']} medium, {review['difficulty']['hard']} hard. Total: {review['totalMarks']} marks. All questions require a calculator.",
 '- Part totals, distinct marking criteria, command terms, model assumptions, statistical conditions, domains, branches, finite-interval roots, units, precision and answer leakage were reviewed.','',
 '## Corrections','']
for reason,ids in notes.items():lines.append('- '+reason+' IDs: '+', '.join(ids)+'.')
lines+=['', 'The 55 changed records include difficulty-only changes, contextual clarification and mathematical corrections; the remaining 445 records passed without a content change. Figures were unchanged by the review.','',
 '## Scope and limits','',
 review['scopeExclusions'], '',review['limits'],'',
 '## Final content hashes','', '| File | SHA-256 |','|---|---|']
for name,sha in sorted(expected.items()):lines.append(f'| {name} | {sha} |')
lines+=['', 'The machine-readable release contract is `ai-hl-independent-review.json`: `status=passed`, `questionCount=500`, 500 per-ID `records`, and `canonicalFiles` keyed by basename.','']
md=DOCS/'ai-hl-independent-review.md';md.write_text('\n'.join(lines),encoding='utf8',newline='\n')
paths=[review_path,md,DOCS/'ai-hl-author-freeze.json',DOCS/'ai-hl-author-audit.json',DOCS/'ai-hl-numeric-audit.json',DOCS/'ai-hl-author-ledger.json',DOCS/'ai-hl-author-signoff.md']
paths+=sorted((ROOT/'scripts/ib-expansion-review').glob('ai-hl*'))
for p in paths:assert b'\r' not in p.read_bytes(),str(p)
manifest=dict(status='passed',questionCount=500,reviewDate='2026-10-31',canonicalFiles=expected,independentScalarComparisons=1912,displayPrecisionChecks=review['displayPrecisionChecks'],changedRecords=55,unresolvedFindings=[],evidenceFiles={str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in paths},independence='Independent of original author; no author modules imported by independent replay. Authorized corrections are disclosed in exact before/after records.',limits=review['limits'])
out=DOCS/'ai-hl-independent-freeze.json';out.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf8',newline='\n')
print(json.dumps(dict(status='passed',questionCount=500,canonicalFiles=expected,independentReportSha256=digest(review_path),independentFreezeSha256=digest(out)),indent=2))
