"""Verify that the manually approved R1/R2 SVG ledger still matches the banks.

This checker never approves a new or edited image. New hashes require a fresh
rendered visual review and a deliberate update to the saved approval ledger.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
REVIEWS = ROOT / 'docs/ib-chemistry-reviews'
ledger = json.loads((REVIEWS / 'reactivity-12-visual-review.json').read_text(encoding='utf8'))
assert ledger['status'] == 'passed'
approved = {}
for image in ledger['images']:
    assert image['status'] == 'passed'
    for use in image['uses']:
        key = (use['id'], use['role'])
        assert key not in approved, ('duplicate approval', key)
        approved[key] = image['sha256']

current = {}
question_count = 0
for bank in ['reactivity-1', 'reactivity-2']:
    questions = json.loads((ROOT / 'content/ib/chemistry' / (bank + '.json')).read_text(encoding='utf8'))
    audit = json.loads((REVIEWS / (bank + '-independent-audit.json')).read_text(encoding='utf8'))
    assert audit['status'] == 'passed'
    record_hashes = {entry['id']: entry['questionSha256'] for entry in audit['entries']}
    assert set(record_hashes) == {q['id'] for q in questions}
    for question in questions:
        question_count += 1
        record_hash = hashlib.sha256(json.dumps(question, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        assert record_hash == record_hashes[question['id']], ('record changed since audit', question['id'])
        if question['syllabusCode'] == 'R1.2':
            assert question['subtopic'] == 'Energy cycles in reactions'
        for field, role in [('diagramSvg', 'question'), ('markSchemeDiagramSvg', 'scheme')]:
            if question.get(field):
                current[(question['id'], role)] = hashlib.sha256(question[field].encode()).hexdigest()

assert current == approved, 'SVG hashes or coverage changed after manual visual approval'
assert len(current) == ledger['svgFieldCount'] == 24
assert len(set(current.values())) == ledger['uniqueSvgCount'] == 17
assert question_count == ledger['fullRecordHashCount'] == 192
print(json.dumps({'status': 'passed', 'questionHashes': question_count,
                  'svgFields': len(current), 'uniqueSvgHashes': len(set(current.values()))}))
