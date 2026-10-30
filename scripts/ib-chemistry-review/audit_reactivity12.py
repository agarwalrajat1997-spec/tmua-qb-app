"""Independent review harness. Never imports the question authors' calculations.

Each review model takes values transcribed from, and matched against, the displayed
question. The model calculates a fresh result and compares it with the published
answer. Every question also receives a recorded scientific/scope review and a hash
so that an unreviewed later edit cannot silently retain a passing audit.
"""
from collections import Counter
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import math
import re

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / 'docs/ib-chemistry-reviews'
CONSTANTS = {'R_J_mol_K': 8.31, 'water_c_J_g_K': 4.18,
             'STP_T_K': 273.15, 'STP_p_kPa': 100.0, 'STP_Vm_dm3_mol': 22.7}
SOURCE = 'https://xmltwo.ibo.org/publications/EAD/2026_EN/GR4/GR4-Chemistry_EN.pdf'


def clean(text):
    text = text.replace('−', '-').replace('–', '-').replace('\\,', ' ')
    text = re.sub(r'\\(?:mathrm|text|operatorname|textsf|mathbf)\{([^{}]*)\}', r'\1', text)
    text = re.sub(r'(?P<m>[+-]?(?:\d*\.)?\d+)\s*\\times\s*10\^\{(?P<e>[+-]?\d+)\}',
                  lambda m: str(float(m['m'])*10**int(m['e'])), text)
    text = re.sub(r'([_^])\{([-+]?\d+)\}',r'\1\2',text)
    return re.sub(r'\s+', ' ', text).strip()


def numeric_values(text):
    return [float(x) for x in re.findall(r'(?<![A-Za-z])[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?', clean(text))]


def round_sig(value, sig=3):
    if value == 0: return 0.0
    scale=10**(math.floor(math.log10(abs(value)))-sig+1)
    scaled=abs(value)/scale
    # Treat machine deviations around an exact decimal half as the decimal half.
    nearest_half=round(scaled*2)/2
    if abs(scaled-nearest_half)<1e-10: scaled=nearest_half
    return math.copysign(math.floor(scaled+0.5)*scale,value)


NUMBER = r'[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?'


def take(a, name, pattern, group=1):
    match = re.search(pattern, clean(a.prompt))
    if not match: raise ValueError(a.q['id']+': no displayed input for '+name+' / '+pattern)
    return a.given(name, float(match[group]), match[0])


def quantities(a, unit_start):
    """Dollar-delimited numeric quantities with the requested leading unit."""
    pattern = r'\$('+NUMBER+r')\s+(?:\\mathrm\{)?'+unit_start
    return [(float(m[1]),m[0]) for m in re.finditer(pattern, clean(a.prompt))]


def atom_counts(formula):
    """Element totals for neutral formulas, including condensed/parenthesized forms."""
    tokens = re.findall(r'[A-Z][a-z]?|\d+|[()]', formula)
    if ''.join(tokens) != formula:
        raise ValueError('Unsupported molecular formula: '+formula)
    stack = [Counter()]
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == '(':
            stack.append(Counter()); i += 1
        elif token == ')':
            group = stack.pop(); i += 1
            multiplier = int(tokens[i]) if i < len(tokens) and tokens[i].isdigit() else 1
            if i < len(tokens) and tokens[i].isdigit(): i += 1
            stack[-1].update({k:v*multiplier for k,v in group.items()})
        elif token[0].isupper():
            i += 1
            multiplier = int(tokens[i]) if i < len(tokens) and tokens[i].isdigit() else 1
            if i < len(tokens) and tokens[i].isdigit(): i += 1
            stack[-1][token] += multiplier
        else:
            raise ValueError('Unexpected formula token '+token)
    if len(stack) != 1: raise ValueError('Unbalanced formula parentheses')
    return dict(stack[0])


def balance(left, right):
    """Each side: coefficient, uncharged formula (or e), explicit signed charge."""
    def totals(side):
        total = Counter()
        for coefficient, formula, charge in side:
            coefficient = Fraction(str(coefficient))
            if formula != 'e':
                for element, count in atom_counts(formula).items(): total[element] += coefficient*count
            total['charge'] += coefficient*charge
        return dict(total)
    lhs, rhs = totals(left), totals(right)
    assert lhs == rhs, (lhs, rhs)
    return {k:float(v) for k,v in lhs.items()}


class Audit:
    def __init__(self, bank):
        self.bank = bank
        self.questions = json.loads((ROOT/'content/ib/chemistry'/f'{bank}.json').read_text(encoding='utf8'))
        self.by_id = {q['id']:q for q in self.questions}
        self.entries = []
        self.errors = []

    def question(self, number):
        return self.questions[number-1]

    def begin(self, number, level, notes):
        q = self.question(number)
        prompt = q['stem']+' '+ ' '.join(p['prompt'] for p in q['parts'])
        answer = ' '.join(s['text'] for group in q['markScheme'] for s in group['steps'])
        if q.get('options'):
            answer += ' '+next(o['text'] for o in q['options'] if o['label']==q['correctOption'])
        self.q, self.prompt, self.answer = q, prompt, answer
        self.entry = {'id':q['id'], 'title':q['title'], 'syllabusCode':q['syllabusCode'],
                      'expectedLevel':level, 'scopeResult':'passed' if q['level']==level else 'failed',
                      'questionSha256':hashlib.sha256(json.dumps(q,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),
                      'scientificReview':notes, 'inputs':{}, 'numericChecks':[], 'equationChecks':[]}
        if q['level'] != level: self.errors.append(q['id']+': incorrect course level')
        self.entries.append(self.entry)
        return q

    def given(self, name, value, evidence):
        """Bind an independently transcribed input to an exact displayed fragment."""
        if clean(evidence) not in clean(self.prompt):
            self.errors.append(self.q['id']+': missing input evidence '+evidence)
        self.entry['inputs'][name] = {'value':value, 'displayedEvidence':evidence}
        return value

    def result(self, name, expression, value, unit='', tolerance=1e-9, target=None, sig=3):
        source = target if target is not None else self.answer
        candidates = numeric_values(source)
        rounded = round_sig(value,sig)
        matched = any(abs(rounded-x) <= max(1e-12, abs(rounded)*tolerance) or abs(value-x) <= max(1e-12, abs(value)*tolerance) for x in candidates)
        self.entry['numericChecks'].append({'quantity':name,'independentExpression':expression,
                                          'value':value,'roundedValue':rounded,'unit':unit,'answerMatch':matched})
        if not matched: self.errors.append(self.q['id']+f': {name} result {value:g} not found in answer')
        return value

    def require(self, fragment):
        if clean(fragment).lower() not in clean(self.answer).lower():
            self.errors.append(self.q['id']+': expected answer reasoning absent: '+fragment)

    def equation(self, label, left, right):
        try:
            totals = balance(left, right)
            self.entry['equationChecks'].append({'equation':label,'atomAndChargeTotals':totals,'status':'passed'})
        except (AssertionError, ValueError) as exc:
            self.errors.append(self.q['id']+': '+label+' imbalance '+str(exc))

    def write(self, expected=96):
        expected_ids = set(self.by_id)
        covered_ids = {e['id'] for e in self.entries}
        if len(self.questions) != expected: self.errors.append(f'Expected {expected} questions; got {len(self.questions)}')
        if expected_ids != covered_ids: self.errors.append('Unreviewed: '+', '.join(sorted(expected_ids-covered_ids)))
        if len(covered_ids) != len(self.entries): self.errors.append('Duplicate audit record')
        report = {'status':'failed' if self.errors else 'passed','bank':self.bank,
                  'reviewType':'Independent scientific and numerical audit from published question inputs',
                  'source':SOURCE,'constants':CONSTANTS, 'questions':len(self.questions),
                  'covered':len(covered_ids),'numericChecks':sum(len(e['numericChecks']) for e in self.entries),
                  'equationChecks':sum(len(e['equationChecks']) for e in self.entries),
                  'entries':self.entries,'errors':self.errors}
        DEST.mkdir(exist_ok=True,parents=True)
        (DEST/f'{self.bank}-independent-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(json.dumps({k:v for k,v in report.items() if k not in ['entries','constants']}))
        return not self.errors


if __name__ == '__main__':
    from audit_r1_models import review as review_r1
    from audit_r2_models import review as review_r2
    a, b = Audit('reactivity-1'), Audit('reactivity-2')
    review_r1(a); review_r2(b)
    ok_a, ok_b = a.write(), b.write()
    raise SystemExit(0 if ok_a and ok_b else 1)
