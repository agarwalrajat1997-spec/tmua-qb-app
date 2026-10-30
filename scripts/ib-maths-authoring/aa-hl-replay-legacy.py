"""Re-execute legacy mathematical assertions without permitting their output writers."""
import ast,sys,json,re,time,contextlib,io
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'work/aa-sl-deps'));sys.path.insert(0,str(ROOT/'work/aa-hl-dependencies'))
class Review(ast.NodeTransformer):
 def visit_FunctionDef(self,node):
  if node.name in ('save','emit'):node.body=[ast.Return(value=ast.Constant(None))];return node
  return self.generic_visit(node)
 def visit_Assert(self,node):
  node.test=ast.Call(func=ast.Name(id='_record_assertion',ctx=ast.Load()),args=[node.test,ast.Constant(node.lineno)],keywords=[])
  return node
summaries=[]
for name in sys.argv[1:] or ['number-algebra','functions','geometry-trigonometry','statistics-probability','calculus-1','calculus-2']:
 path=ROOT/'scripts/ib-authoring'/f'{name}.py';count=[0];lines=[]
 def record(test,line):
  if not bool(test):raise AssertionError(f'{name}:{line}: mathematical assertion failed')
  count[0]+=1;lines.append(line);return test
 tree=Review().visit(ast.parse(path.read_text(encoding='utf8')));ast.fix_missing_locations(tree)
 gl=dict(__file__=str(path),__name__='__legacy_review__',_record_assertion=record)
 start=time.perf_counter()
 with contextlib.redirect_stdout(io.StringIO()):exec(compile(tree,str(path),'exec'),gl)
 checks=gl.get('CHECKS',{});q=gl.get('Q',gl.get('OUT',[]));q=gl.get('OUT',[]) if callable(q) else q;q=list(q.values()) if isinstance(q,dict) else q
 ids=sorted(checks) if isinstance(checks,dict) else sorted({int(v) for line in checks for v in re.findall(r'Q(\d+)',str(line))})
 info=dict(collection=name,questionsReconstructed=len(q),executedAssertions=count[0],assertionSourceLines=sorted(set(lines)),assertionsBySourceLine={str(j):lines.count(j) for j in sorted(set(lines))},explicitPerQuestionCheckNumbers=ids,seconds=round(time.perf_counter()-start,2),scope='Original builder assertions, including mathematical and mark-total assertions, re-executed in memory; output writers disabled. This confirms retained checks, not a new independent proof of every displayed step.')
 summaries.append(info)
 out=ROOT/'docs/ib-maths-reviews';out.mkdir(exist_ok=True)
 (out/f'aa-hl-{name}-legacy-replay.json').write_text(json.dumps(info,indent=2)+'\n')
 print(json.dumps(info),flush=True)
