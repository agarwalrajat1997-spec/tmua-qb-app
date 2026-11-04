"""Original Psychology 2027 bank authoring helpers. Review is a separate step."""
from pathlib import Path
import json, hashlib, math, html, textwrap

ROOT = Path(__file__).resolve().parents[2]
TASK = ROOT.parents[1]
DOCS = ROOT / 'docs/ib-psychology-reviews'
CONTENT = ROOT / 'content/ib/psychology'
CONTRACT = json.loads((DOCS / 'content-contract.json').read_text(encoding='utf-8'))
TOPICS = {x['token']: x for x in CONTRACT['topics']}
CONTEXTS = CONTRACT['contexts']
CONCEPTS = CONTRACT['concepts']

def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')

def question_hash(q):
    return hashlib.sha256(json.dumps(q, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def rubric(section):
    """Original best-fit descriptors; these are not copied IB markbands."""
    maximum = CONTRACT['sections'][section]['marks']
    if maximum == 3:
        bands = [(0, 0, 'No relevant limitation is established.'), (1, 1, 'Identifies a limitation relevant to this display.'), (2, 2, 'Describes the limitation accurately using a feature of this source.'), (3, 3, 'Explains how that source feature restricts a specific inference.')]
    elif maximum == 4:
        focus = 'the psychological idea and the explanatory example' if section == 'p1-a' else 'the method and its practical application' if section == 'p2-a-knowledge' else 'the named concept and the practical decisions'
        bands = [(0, 0, 'No relevant psychological understanding is demonstrated.'), (1, 2, f'Offers some relevant understanding of {focus}, with gaps or weak links.'), (3, 4, f'Gives an accurate, developed account of {focus}, making the explanatory connections clear.')]
    elif maximum == 6:
        focus = {'p1-b': 'Explains the relevant psychological mechanism and uses specific scenario details to show how it applies.', 'p2-a-comparison': 'Develops both similarities and differences between the methods and explains their practical consequences.', 'p2-a-design': 'Presents a coherent, feasible procedure with justified methodological decisions and relevant ethical protections.', 'p3-data': 'Develops an accurate analysis using the supplied findings and states a proportionate conclusion supported by those findings.', 'p3-qualitative': 'Explains the research consideration in detail and explicitly connects the discussion to the qualitative source.'}[section]
        bands = [(0, 0, 'No relevant response to the task.'), (1, 2, 'Relevant ideas are present, but explanations or source links are minimal or substantially inaccurate.'), (3, 4, 'The main reasoning is sound but is unevenly developed or incompletely connected to the task.'), (5, 6, focus)]
    else:
        top = {'p1-c': 'Integrates accurate psychological knowledge, the specified concept or concepts, and the context; weighs competing explanations and reaches a justified conclusion.', 'p2-b': 'Develops a balanced evaluation of this study through at least two named concepts, using methodological details and a supported overall judgement.', 'p3-synthesis': 'Synthesizes at least three supplied sources and relevant HL knowledge; weighs different interpretations and reaches a qualified, evidence-based judgement about the stated claim.'}[section]
        bands = [(0, 0, 'No relevant response to the question.'), (1, 3, 'Gives isolated relevant ideas, with major gaps and little sustained reasoning.'), (4, 6, 'Develops a basic relevant account, but remains mainly descriptive and offers weak support for its judgement.'), (7, 9, 'Addresses the main issue with some analysis and relevant evidence, though important links or alternatives remain underdeveloped.'), (10, 12, 'Develops a coherent argument with relevant psychological knowledge and evidence; evaluates alternatives and supports its conclusion, with some unevenness.'), (13, 15, top)]
    return {'maxMarks': maximum, 'bands': [{'min': lo, 'max': hi, 'descriptor': text} for lo, hi, text in bands]}

def question(token, number, title, code, section, stem, steps, *, difficulty='hard', context='general', concepts=None, summary='', diagram=None, caption=None):
    topic = TOPICS[token]
    spec = CONTRACT['sections'][section]
    subtopic = next(x for x in topic['subtopics'] if x['code'] == code)
    assert difficulty in ('medium', 'hard')
    assert context in (['general'] if section == 'p1-a' else CONTEXTS)
    concepts = concepts or ['measurement']
    assert len(concepts) == len(set(concepts)) and all(c in CONCEPTS for c in concepts)
    assert isinstance(steps, list) and len(steps) >= (4 if spec['marks'] == 15 else 2)
    assert all(isinstance(s, str) and len(s.strip()) >= 35 for s in steps)
    q = {'id': f'ib-psy-{token}-{number:03}', 'subject': 'psychology', 'firstAssessment': 2027, 'number': number, 'title': title, 'topicId': topic['topicId'], 'collectionId': topic['collectionId'], 'syllabusCode': code, 'subtopic': subtopic['title'], 'level': topic['level'], 'difficulty': difficulty, 'calculator': False, 'examStyle': spec['examStyle'], 'examSection': section, 'questionType': spec['questionType'], 'context': context, 'concepts': concepts, 'marks': spec['marks'], 'stem': stem, 'parts': [], 'markScheme': [{'part': '', 'steps': [{'code': 'IND', 'text': s} for s in steps], 'rubric': rubric(section)}], 'source': {'document': 'Independent syllabus-authored practice', 'question': number}, 'verification': {'method': 'Author conceptual and methodological checks; independent review is recorded separately.', 'notes': 'Checked question demand, supplied evidence, scope and non-additive best-fit marking. Specific derivations and source checks are retained in the author ledger.'}, 'status': 'published', 'answerSummary': summary or steps[-1]}
    if diagram:
        assert diagram.startswith('<svg') and 'viewBox=' in diagram and '</svg>' in diagram
        q['diagramSvg'] = diagram
        q['diagramCaption'] = caption or 'Original schematic for this practice question; not necessarily to scale.'
        manifest_path = ROOT / 'content/ib/psychology-diagram-manifest.json'
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            assert manifest['origin'] == 'https://media.thrivingscholars.com'
            digest = hashlib.sha256(diagram.encode()).hexdigest()
            asset = manifest['assets'].get(digest)
            if asset:
                assert asset['key'] == f'ib/psychology/2026-11-04/{digest}.svg'
                assert asset['contentType'] == 'image/svg+xml' and asset['bytes'] == len(diagram.encode())
                q['diagramUrl'] = manifest['origin'] + '/' + asset['key']
    return q

def write_collection(token, questions):
    topic = TOPICS[token]
    assert len(questions) == topic['questions']
    assert [q['number'] for q in questions] == list(range(1, len(questions) + 1))
    assert len({q['stem'] for q in questions}) == len(questions)
    path = CONTENT / (topic['topicId'] + '.json')
    dump(path, questions)
    return {'file': path.relative_to(ROOT).as_posix(), 'sha256': file_hash(path), 'questions': len(questions)}

def assertion(name, actual, expected, tolerance=1e-9, reason=''):
    assert math.isfinite(float(actual)) and math.isfinite(float(expected)) and math.isfinite(float(tolerance)) and tolerance >= 0
    assert abs(actual - expected) <= tolerance, (name, actual, expected)
    return {'name': name, 'actual': actual, 'expected': expected, 'tolerance': tolerance, 'reason': reason}

def evidence(q, reasoning, *, sources=None, checks=None, figure=None, alternatives=None):
    assert len(reasoning) > 80
    r = {'questionId': q['id'], 'questionSha256': question_hash(q), 'status': 'author-checks-passed; independent review required', 'reasoning': reasoning, 'sources': sources or [], 'numericChecks': checks or [], 'alternativeInterpretations': alternatives or [], 'openFindings': []}
    if q.get('diagramSvg'):
        assert figure and len(str(figure)) > 60
        r['figureEvidence'] = {'svgSha256': hashlib.sha256(q['diagramSvg'].encode()).hexdigest(), 'scientificChecks': figure}
    return r

def svg(contents, width=720, height=400, description='Original psychology practice stimulus'):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(description, quote=True)}"><rect width="{width}" height="{height}" fill="#fffdf7"/>{contents}</svg>'

def text(x, y, value, size=18, anchor='start', fill='#251d1d'):
    return f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" text-anchor="{anchor}" fill="{fill}">{html.escape(str(value))}</text>'

def line(x1, y1, x2, y2, color='#412b2b', width=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"{d}/>'

def rect(x, y, w, h, fill='#f5db7e', stroke='#663238'):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'

def bars(labels, values, maximum, *, title='Simulated practice data', ylabel='Mean score', errors=None, baseline=0, decimals=0):
    assert len(labels) == len(values) and maximum > baseline
    assert all(baseline <= v <= maximum for v in values)
    x0, x1, y0, y1 = 80, 570, 325, 115
    scale = (y0-y1)/(maximum-baseline)
    body = ''.join(text(300,25+i*25,s,22,'middle') for i,s in enumerate(textwrap.wrap(title,46)))
    body += text(80,91,ylabel,20)
    for k in range(6):
        v = baseline + (maximum-baseline)*k/5
        y = y0-(v-baseline)*scale
        body += line(x0,y,x1,y,'#ddd2c4',1) + text(68,y+6,f'{v:g}',20,'end')
    body += line(x0,y0,x1,y0) + line(x0,y0,x0,y1)
    slot=(x1-x0)/len(labels)
    for i,(label,v) in enumerate(zip(labels,values)):
        x=x0+(i+.5)*slot; yy=y0-(v-baseline)*scale; w=min(slot*.55,105)
        body+=rect(round(x-w/2,2),round(yy,2),round(w,2),round(y0-yy,2))
        if errors:
            e=errors[i]; assert e>=0 and baseline<=v-e and v+e<=maximum
            top=y0-(v+e-baseline)*scale; bot=y0-(v-e-baseline)*scale
            body+=line(x,top,x,bot)+line(x-8,top,x+8,top)+line(x-8,bot,x+8,bot)
        body+=text(x,370,label,21,'middle')
    body+=text(300,412,'Constructed data; not a published study.',18,'middle')
    return svg(body,600,430,'Bar chart of explicitly simulated psychology data')
