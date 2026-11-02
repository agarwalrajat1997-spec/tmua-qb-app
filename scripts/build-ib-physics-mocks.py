"""Reproducible compilation of original questions, not copied examination papers."""
import collections
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
questions = sum((json.loads(p.read_text()) for p in sorted((ROOT / 'content/ib/physics-hl').glob('*.json'))), [])
used = set()

def rank(q, salt):
    return hashlib.sha256((salt + q['id']).encode()).hexdigest()

def candidates(course, kind):
    return [q for q in questions if q['status'] == 'published' and q['questionType'] == kind
            and q['id'] not in used and (course == 'hl' or q['level'] == 'core')]

def mcqs(course, n):
    pool = candidates(course, 'multiple-choice')
    selected = []
    codes = sorted({q['syllabusCode'] for q in pool})
    # Every applicable syllabus subtopic appears in every Paper 1A.
    for i, code in enumerate(codes):
        target = ['easy', 'medium', 'hard'][(i+n) % 3]
        q = min((q for q in pool if q['syllabusCode'] == code),
                key=lambda q: (q['difficulty'] != target, rank(q, f'{course}{n}')))
        selected.append(q)
        pool.remove(q)
    count = 25 if course == 'sl' else 40
    while len(selected) < count:
        counts = collections.Counter(q['syllabusCode'] for q in selected)
        remaining_mocks = 3-n+(3 if course == 'sl' else 0)
        available = collections.Counter(q['syllabusCode'] for q in pool)
        spare = [q for q in pool if available[q['syllabusCode']] > remaining_mocks]
        assert spare, (course, n, 'insufficient MCQ reserve')
        q = min(spare, key=lambda q: (counts[q['syllabusCode']],
                course == 'hl' and q['level'] != 'ahl', rank(q, f'extra{course}{n}')))
        selected.append(q)
        pool.remove(q)
    selected.sort(key=lambda q: (q['syllabusCode'], {'easy':0,'medium':1,'hard':2}[q['difficulty']]))
    used.update(q['id'] for q in selected)
    return [q['id'] for q in selected]

def written(course, n, kind, target):
    pool = candidates(course, kind)
    # Exact mark total, all five themes for Paper 2, experiment-rich Paper 1B.
    # A bounded dynamic program selects a diverse, diagram-rich combination.
    pool.sort(key=lambda q: rank(q, f'{course}{n}{kind}'))
    states = {(0, 0, 0, 0): (0, [])}
    for q in pool:
        bit = 1 << (ord(q['syllabusCode'][0])-65)
        ahl = int(q['level'] == 'ahl')
        merit = 3 * bool(q.get('diagramSvg') or q.get('diagramUrl')) + {'easy':0,'medium':3,'hard':2}[q['difficulty']]
        if kind == 'data-based':
            merit += 4 * any(w in (q['stem'] + str(q['parts'])).lower() for w in ['uncertainty','gradient','experiment','measurement','error'])
        for (marks, mask, a, count), (value, selected) in list(states.items()):
            key = (marks+q['marks'], mask | bit, min(3, a+ahl), count+1)
            if key[0] > target or len(selected) >= (4 if kind == 'data-based' else (9 if course == 'sl' else 12)):
                continue
            score = value + merit - 1
            if key not in states or score > states[key][0]:
                states[key] = (score, selected+[q])
    eligible = [(key, value) for key,value in states.items() if key[0] == target
                and (kind != 'structured' or key[1] == 31)
                and (course != 'hl' or kind != 'structured' or key[2] == 3)]
    assert eligible, (course, n, kind)
    key, (_, selected) = max(eligible, key=lambda kv: (kv[0][1].bit_count(), kv[1][0]))
    selected.sort(key=lambda q: (q['syllabusCode'], q['id']))
    used.update(q['id'] for q in selected)
    return [q['id'] for q in selected]

mocks = []
for course in ['sl', 'hl']:
    for n in range(1, 4):
        mocks.append({
            'id': f'physics-{course}-mock-{n:02}', 'subject': 'physics-hl', 'course': course,
            'title': f'Physics {course.upper()} · Mock {n:02}', 'status': 'published', 'version': 1,
            'paper1A': mcqs(course, n), 'paper1B': written(course, n, 'data-based', 20),
            'paper2': written(course, n, 'structured', 55 if course == 'sl' else 90),
        })
out = ROOT / 'content/ib/physics-mocks.json'
out.write_text(json.dumps(mocks, indent=2)+'\n')
lookup = {q['id']:q for q in questions}
for m in mocks:
    print(m['id'], {p: {'questions':len(m[p]), 'marks':sum(lookup[i]['marks'] for i in m[p])} for p in ['paper1A','paper1B','paper2']})
print(len(used), 'distinct original questions')
