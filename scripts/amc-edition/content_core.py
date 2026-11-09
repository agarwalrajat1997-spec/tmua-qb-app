"""Original November collection. Exact answers are checked before assigning option letters."""
import math,itertools,random,json,hashlib,re,html,statistics,collections
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
from itertools import combinations, permutations, product
ALG='Algebra & functions'; GEO='Geometry & measurement'; CNT='Counting & combinatorics'; NT='Number theory'; AR='Arithmetic & proportional reasoning'; PRO='Probability & statistics'; SEQ='Sequences & patterns'; LOG='Logic & problem solving'; TRIG='Trigonometry'
def fmt(v):
 if isinstance(v,F):return str(v.numerator) if v.denominator==1 else str(v)
 return str(v)
def join(x):return ', '.join(map(fmt,x))
def pg(x):return '<p>'+html.escape(str(x))+'</p>'
def svg(inner,title,w=300,h=156):
 return '<svg xmlns="http://www.w3.org/2000/svg" width="'+str(w)+'" height="'+str(h)+'" viewBox="0 0 '+str(w)+' '+str(h)+'" style="display:block;max-width:100%;height:auto;margin:12px 0" role="img" aria-label="'+html.escape(title,quote=True)+'"><title>'+html.escape(title)+'</title><rect width="100%" height="100%" fill="white"/>'+inner+'</svg>'
def square_art(cells,labels=False):
 step=22;ox=12;oy=10
 return svg(''.join(f'<rect x="{ox+step*x}" y="{oy+step*y}" width="{step}" height="{step}" stroke="#273645" fill="#f5cf7b"/>' for x,y in sorted(cells)),'Unit squares forming the figure',2*ox+(max(x for x,y in cells)+1)*step,2*oy+(max(y for x,y in cells)+1)*step)
def network(layers,edges,ids):
 w=320;h=154
 ps={n:(16+i*(w-32)/(len(layers)-1),16+(j+1)*(h-32)/(len(layer)+1)) for i,layer in enumerate(layers) for j,n in enumerate(layer)}
 ins=''.join(f'<line x1="{ps[a][0]}" y1="{ps[a][1]}" x2="{ps[b][0]}" y2="{ps[b][1]}" stroke="#556775" stroke-width="1.5"/>' for a,b in edges)
 for n,(x,y) in ps.items():ins+=f'<circle cx="{x}" cy="{y}" r="9" fill="#fff7e8" stroke="#5d2c39"/><text x="{x}" y="{y+3.5}" text-anchor="middle" font-size="9" font-family="sans-serif">{n}</text>'
 return svg(ins,'Directed route diagram; each edge leads from left to right',w,h)
def item(lv,fam,k,topic,sub,diff,stem,answer,check,solution,distr=(),art='',mock=False):
 assert answer==check,(lv,fam,k,answer,check)
 ident=f'{lv}-{fam}-{k}';rng=random.Random(ident)
 correct=fmt(answer);opts=[correct];v=F(answer)
 additions=list(distr)+[v+1,v-1,v*2,v/2,v+2,v-2,v+3,v+4,v+5]
 isprob='probability' in stem.lower() and 0<=v<=1
 if isprob:
  specials=[1-v,v/2,(1+v)/2,F(1,2),F(1,3),F(2,3),F(1,4),F(3,4)]
  additions=[a for a in additions if 0<=F(a)<=1]+specials
 for a in additions:
  t=fmt(a)
  if t not in opts and F(a)>=0:opts.append(t)
  if len(opts)==5:break
 assert len(opts)==5
 rng.shuffle(opts)
 return dict(id=ident,level=lv,family=fam,topic=topic,subtopic=sub,difficulty=diff,stem=stem,diagram=art,choices=opts,key='ABCDE'[opts.index(correct)],answer=correct,solution=solution,section='mock' if mock else 'bank')
def poly(k,rng,size):
 cells={(0,0)};dirs=[(1,0),(-1,0),(0,1),(0,-1)]
 while len(cells)<size:
  x,y=rng.choice(sorted(cells));a,b=rng.choice(dirs);cells.add((x+a,y+b))
 x0=min(x for x,y in cells);y0=min(y for x,y in cells)
 return {(x-x0,y-y0) for x,y in cells}
def top_sum(n):return n*(n+1)//2
