import json,math,os,re,html
from pathlib import Path
_HERE = Path(__file__).resolve().parent
import sympy as sp
import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm
ROOT=(_HERE.parents[1] / 'content/ib/math-aa-hl')
SOURCES=json.loads(Path(str(_HERE / 'reference-metadata' / 'IB Mathematics AA HL Questionbank - Functions.json')).read_text())
OUT=[]; CHECKS={};x=sp.symbols('x',real=True)
def L(e):return sp.latex(sp.sympify(e))
def ck(n,a,b):
 assert sp.simplify(a-b)==0,(n,a,b)
 CHECKS.setdefault(n,[]).append('symbolic equality')
def nc(n,a,b,tol=1e-8):
 assert abs(float(a)-float(b))<tol,(n,a,b)
 CHECKS.setdefault(n,[]).append('numerical substitution')
def step(code,text):return {'code':code,'text':text}
def P(prompt,*ss):return (prompt,[step(c,t) for c,t in ss])
def add(n,title,sub,stem,parts=None,whole=None,diagram=None,solution=None,note=''):
 source=SOURCES[n-1];ps=[];ms=[]
 if parts:
  for i,(prompt,ss) in enumerate(parts):
   label=chr(97+i);marks=sum(int(z['code'][1:]) if z['code']!='AG' else 0 for z in ss)
   ps.append({'label':label,'prompt':prompt,'marks':marks});ms.append({'part':label,'steps':ss})
 else:ms=[{'part':'','steps':[step(c,t) for c,t in whole]}]
 total=sum(int(z['code'][1:]) if z['code']!='AG' else 0 for g in ms for z in g['steps'])
 obj={'id':f'ib-aa-fn-{n:03}','subject':'math-aa-hl','topicId':'functions','collectionId':'functions','number':n,'title':title,'subtopic':sub,'difficulty':source['difficulty'],'calculator':source['calculator'],'marks':total,'stem':stem,'parts':ps,'markScheme':ms,'source':{'document':'IB Mathematics AA HL Questionbank - Functions.pdf','question':n},'verification':{'method':'reasoned','notes':'Worked through the displayed algebra and checked domains, branches and mark totals. '+note},'status':'published'}
 if diagram:obj['diagramSvg']=diagram
 if solution:obj['markSchemeDiagramSvg']=solution
 if total!=source['marks']:obj['verification']['notes']+=f' Source maximum {source["marks"]}; rebuilt allocation {total}.'
 OUT.append(obj)
def graph(curves,xb=(-5,5),yb=(-5,5),pts=(),vl=(),hl=(),caption=''):
 W,H=620,380;pad=42
 X=lambda t:pad+(t-xb[0])/(xb[1]-xb[0])*(W-2*pad)
 Y=lambda t:H-pad-(t-yb[0])/(yb[1]-yb[0])*(H-2*pad)
 tags=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="{html.escape(caption or "Coordinate graph",quote=True)}">',f'<rect width="{W}" height="{H}" fill="white"/>']
 dx=max(1,math.ceil((xb[1]-xb[0])/12));dy=max(1,math.ceil((yb[1]-yb[0])/10))
 for k in range(math.ceil(xb[0]),math.floor(xb[1])+1,dx):
  tags.append(f'<line x1="{X(k):.2f}" y1="{pad}" x2="{X(k):.2f}" y2="{H-pad}" stroke="#e4e4e4"/>')
  if k:tags.append(f'<text x="{X(k):.2f}" y="{min(H-12,max(18,Y(0)+17)):.2f}" text-anchor="middle" font-size="11" fill="#444">{k}</text>')
 for k in range(math.ceil(yb[0]),math.floor(yb[1])+1,dy):
  tags.append(f'<line x1="{pad}" y1="{Y(k):.2f}" x2="{W-pad}" y2="{Y(k):.2f}" stroke="#e4e4e4"/>')
  if k:tags.append(f'<text x="{min(W-15,max(18,X(0)-8)):.2f}" y="{Y(k)+4:.2f}" text-anchor="end" font-size="11" fill="#444">{k}</text>')
 if xb[0]<=0<=xb[1]:tags.append(f'<line x1="{X(0)}" y1="20" x2="{X(0)}" y2="{H-pad}" stroke="#222"/><text x="{X(0)+8}" y="22" font-size="13">y</text>')
 if yb[0]<=0<=yb[1]:tags.append(f'<line x1="{pad}" y1="{Y(0)}" x2="{W-20}" y2="{Y(0)}" stroke="#222"/><text x="{W-20}" y="{Y(0)-7}" font-size="13">x</text>')
 for a in vl:tags.append(f'<line x1="{X(a)}" x2="{X(a)}" y1="{pad}" y2="{H-pad}" stroke="#999" stroke-dasharray="6 4"/>')
 for a in hl:tags.append(f'<line x1="{pad}" x2="{W-pad}" y1="{Y(a)}" y2="{Y(a)}" stroke="#999" stroke-dasharray="6 4"/>')
 for fun,color in curves:
  commands=[];last=None
  for xx in np.linspace(xb[0],xb[1],700):
   try: yy=float(fun(float(xx)))
   except Exception:last=None;continue
   if not math.isfinite(yy) or not yb[0]<=yy<=yb[1]:last=None;continue
   cmd='M' if last is None or abs(yy-last)>(yb[1]-yb[0])/3 else 'L'
   commands.append(f'{cmd}{X(xx):.2f},{Y(yy):.2f}');last=yy
  tags.append(f'<path d="{" ".join(commands)}" fill="none" stroke="{color}" stroke-width="2.3"/>')
 for xx,yy,label in pts:
  tags.append(f'<circle cx="{X(xx):.2f}" cy="{Y(yy):.2f}" r="3" fill="#7a1f24"/><text x="{X(xx)+7:.2f}" y="{Y(yy)-8:.2f}" font-size="12">{html.escape(label)}</text>')
 tags.append('</svg>');return ''.join(tags)
B='#253c66';R='#7a1f24'
# Each numbered entry follows the corresponding reference skill; values are newly chosen.
add(1,'Reading and transforming a graph','Transformations',r'The diagram shows $y=f(x)$ for $-3\le x\le4$. Let $g(x)=2f(x)+1$ on the same domain.',[
 P(r'Write down $f(3)$.',('A1',r'$f(3)=2$.')),
 P(r'Sketch $y=g(x)$, labelling its vertex and endpoints.',('M1',r'Multiply every ordinate by 2 and add 1.'),('A1',r'The vertex is $(0,-1)$ and endpoints are $(-3,5)$ and $(4,7)$; join with straight segments.')),
 P(r'Find $(g\circ f)(3)$.',('A1',r'$g(f(3))=g(2)=3$.')),
 P(r'Solve $(f\circ g)(x)=0$ for $x>0$.',('A1',r'$f$ vanishes at inputs $-1,1$. Thus $g(x)=\pm1$, giving the single positive solution $x=1$.'))],diagram=graph([(lambda x:abs(x)-1,B)],(-3,4),(-2,4)),solution=graph([(lambda x:2*abs(x)+-1,R)],(-3,4),(-2,8)))
add(2,'Inverse of a rational function','Composite and inverse functions',r'Let $f(x)=\dfrac{5x+3}{2x+k}$, where $k\ne\dfrac65$.',[
 P(r'State the domain of $f$ in terms of $k$.',('A1',r'$x\in\mathbb R\setminus\{-k/2\}$.')),
 P(r'Find $f^{-1}(x)$.',('M1',r'$y(2x+k)=5x+3\Rightarrow x(2y-5)=3-ky$.'),('A1',r'$f^{-1}(x)=\dfrac{3-kx}{2x-5}$, $x\ne5/2$.')),
 P(r'Find $k$ for which $f$ is self-inverse.',('A1',r'$k=-5$, giving $f^{-1}(x)=\dfrac{5x+3}{2x-5}=f(x)$.'))])
ck(2,(5*((5*x+3)/(2*x-5))+3)/(2*((5*x+3)/(2*x-5))-5),x)
add(3,'Composite linear function','Composite and inverse functions',r'$f(x)=3x$, $g(x)=5x-4$ and $h=f\circ g$, with domain $\mathbb R$.',[
 P(r'Find $h(x)$.',('M1',r'$h(x)=3(5x-4)$.'),('A1',r'$h(x)=15x-12$.')),
 P(r'Find $h^{-1}(x)$.',('M1',r'$y=15x-12\Rightarrow15x=y+12$.'),('M1',r'Interchange input and output.'),('A1',r'$h^{-1}(x)=\dfrac{x+12}{15}$.'))])
add(4,'A quadratic from its vertex','Quadratic functions',r'$f(x)=a(x-h)^2+k$. Its vertex is $P(2,5)$ and it passes through $Q(-1,-13)$.',[
 P(r'State $h$ and $k$.',('A2',r'$h=2$ and $k=5$ (one mark each).')),
 P(r'Find $a$.',('M1',r'Substitute $Q$: $-13=a(-1-2)^2+5$.'),('A1',r'$9a=-18$.'),('A1',r'$a=-2$.'))]);ck(4,-2*(-1-2)**2+5,-13)
add(5,'Tangents through the origin','Quadratic functions',r'Find the equations of both tangents to $y=3x^2-2x+12$ which pass through the origin.',whole=[('M1',r'A line through the origin is $y=mx$.'),('A1',r'Intersections satisfy $3x^2-(m+2)x+12=0$.'),('M1',r'Tangency requires discriminant zero: $(m+2)^2-144=0$.'),('A1',r'$m+2=\pm12$, so $m=10,-14$.'),('A1',r'The lines are $y=10x$ and $y=-14x$.')]);ck(5,sp.discriminant(3*x*x-12*x+12,x),0)
add(6,'Function values from a table and graph','Composite and inverse functions',r'The table defines an invertible function $f$ on the listed inputs. The diagram shows $g$.\n\n| $x$ | 0 | 1 | 2 | 3 | 4 |\n|---|---|---|---|---|---|\n| $f(x)$ | 3 | 1 | 4 | 0 | 2 |',[
 P(r'Find (i) $f(2)$; (ii) $g(f(2))$.',('A1',r'$f(2)=4$.'),('M1',r'Read the ordinate of $g$ at input 4.'),('A1',r'$g(4)=1$.')),
 P(r'Find $f^{-1}(g(2))$.',('M1',r'The graph gives $g(2)=3$; locate output 3 in the table.'),('A1',r'$f^{-1}(3)=0$.'))],diagram=graph([(lambda x:5-x,B)],(0,5),(0,5)))
add(7,'Equivalent forms of a quadratic','Quadratic functions',r'The diagram shows a quadratic $f(x)=(x-h)^2+k=(x+p)(x-q)$ with $p,q>0$.',[
 P(r'State $h$ and $k$.',('A2',r'$h=2$, $k=-16$ (one each).')),
 P(r'State $p$ and $q$.',('A2',r'$p=2$, $q=6$ (one each).')),
 P(r'Find the $y$-intercept.',('M1',r'$f(0)=(0+2)(0-6)$.'),('A1',r'$(0,-12)$.'))],diagram=graph([(lambda x:(x-2)**2-16,B)],(-3,7),(-18,12),[(-2,0,'B(-2,0)'),(6,0,'C(6,0)'),(2,-16,'A(2,-16)')]))
add(8,'An inverse and a cubic composition','Composite and inverse functions',r'$f(x)=x^3$ and $g(x)=3x-2$, for $x\in\mathbb R$.',[
 P(r'Find $g^{-1}(x)$.',('M1',r'$y=3x-2\Rightarrow x=(y+2)/3$.'),('A1',r'$g^{-1}(x)=(x+2)/3$.')),
 P(r'Find $(g\circ f)(x)$.',('M1',r'Substitute $x^3$ for the input of $g$.'),('A1',r'$(g\circ f)(x)=3x^3-2$.')),
 P(r'Solve $(g\circ f)(x)=0$, to three significant figures.',('M1',r'$x^3=2/3$.'),('A1',r'$x=\sqrt[3]{2/3}\approx0.874$.'))])
add(9,'Intercepts and symmetry','Quadratic functions',r'$f(x)=x^2-4x-12$, for $x\in\mathbb R$.',[
 P(r'State the $y$-intercept.',('A1',r'$(0,-12)$.')),
 P(r'Solve $f(x)=0$.',('M1',r'Factorise as $(x-6)(x+2)=0$.'),('A2',r'$x=6$ or $x=-2$ (one each).')),
 P(r'Find the axis of symmetry.',('M1',r'Midpoint of the roots: $(-2+6)/2$.'),('A1',r'$x=2$.'))]);ck(9,(x-6)*(x+2),x*x-4*x-12)
add(10,'Evaluating a composition','Composite and inverse functions',r'$f(x)=x^2+5$ and $g(x)=x-4$, for real $x$.',[
 P(r'Find $f(2)$.',('M1',r'$f(2)=2^2+5$.'),('A1',r'$f(2)=9$.')),
 P(r'Find $(g\circ f)(2)$.',('M1',r'$g(f(2))=g(9)=9-4$.'),('A1',r'$5$.')),
 P(r'Find $g^{-1}(x)$.',('M1',r'Rearrange $y=x-4$.'),('A1',r'$g^{-1}(x)=x+4$.'))])
add(11,'A quadratic in factorised form','Quadratic functions',r'$f(x)=(x-5)(x+1)$, for real $x$. Find:',[
 P(r'the $y$-intercept;',('M1',r'$f(0)=(-5)(1)$.'),('A1',r'$(0,-5)$.')),
 P(r'both $x$-intercepts;',('A2',r'$(-1,0)$ and $(5,0)$ (one each).')),
 P(r'the coordinates of the vertex.',('M1',r'$x_v=(-1+5)/2=2$.'),('M1',r'$f(2)=(-3)(3)=-9$.'),('A1',r'The vertex is $(2,-9)$.'))])
add(12,'Composition and inverse composition','Composite and inverse functions',r'$f(x)=5x+2$ and $g(x)=3x$, for real $x$.',[
 P(r'Write down $g(4)$.',('A1',r'$g(4)=12$.')),
 P(r'Find $(f\circ g)(x)$.',('M1',r'$f(3x)=5(3x)+2$.'),('A1',r'$15x+2$.')),
 P(r'Find $(f\circ g)^{-1}(x)$.',('M1',r'Rearrange $y=15x+2$.'),('A1',r'$(f\circ g)^{-1}(x)=(x-2)/15$.'))])
add(13,'A repeated quadratic root','Discriminants',r'The equation $x^2+kx+9=0$ has two equal real roots. Find all possible values of $k$.',whole=[('M1',r'A repeated root requires $b^2-4ac=0$.'),('A1',r'$k^2-36=0$.'),('M1',r'Factorise $(k-6)(k+6)=0$ or take both square roots.'),('A1',r'$k=6$.'),('A1',r'$k=-6$.')])
add(14,'Parallel and perpendicular graphs','Linear functions',r'$f(x)=3x-5$, for real $x$.',[
 P(r'The linear function $g$ has graph perpendicular to $f$ through the origin. Find $g(x)$.',('M1',r'The negative reciprocal of 3 is $-1/3$.'),('A1',r'$g(x)=-x/3$.')),
 P(r'The graph of $h$ is parallel to $f$ and passes through $(2,7)$. Find $h(x)$.',('M1',r'Use gradient 3: $h(x)=3x+c$.'),('A1',r'$7=6+c\Rightarrow c=1$.'),('A1',r'$h(x)=3x+1$.'))])
add(15,'Perpendicular lines with a parameter','Linear functions',r'$L_1$ passes through $A(-3,-2)$ and $B(9,4)$.',[
 P(r'Find its gradient.',('A1',r'$m_1=(4+2)/(9+3)=1/2$.')),
 P(r'$L_2$ is perpendicular to $L_1$, passes through $(-a,3a)$ and has $y$-intercept $3a-8$. Find $a$.',('M1',r'$m_2=-2$; write $y=-2x+(3a-8)$.'),('A1',r'$3a=2a+3a-8\Rightarrow2a=8$.'),('A1',r'$a=4$.'))])
add(16,'Completing the square and sketching','Quadratic functions',r'$f(x)=x^2-6x+5$, for real $x$.',[
 P(r'Find the $y$-intercept and both $x$-intercepts.',('A1',r'$y$-intercept $(0,5)$.'),('M1',r'$x^2-6x+5=(x-1)(x-5)$.'),('A1',r'$x$-intercepts $(1,0)$ and $(5,0)$.')),
 P(r'Write $f(x)=(x-h)^2+k$, stating $h,k$.',('M1',r'$x^2-6x+5=(x-3)^2-9+5$.'),('A1',r'$h=3$, $k=-4$.')),
 P(r'Sketch the graph, labelling the intercepts and vertex.',('A1',r'Upward-opening parabola through the three intercepts.'),('A1',r'Vertex $(3,-4)$, symmetric about $x=3$.'))],solution=graph([(lambda x:x*x-6*x+5,R)],(-1,7),(-5,8)))
add(17,'Inverting a translated cubic','Composite and inverse functions',r'$f(x)=(x+3)^3$ for real $x$.',[
 P(r'Find $f^{-1}(x)$.',('M1',r'$y=(x+3)^3\Rightarrow\sqrt[3]y=x+3$.'),('M1',r'Solve for the input and exchange variables.'),('A1',r'$f^{-1}(x)=\sqrt[3]x-3$.')),
 P(r'$g$ satisfies $(f\circ g)(x)=64x^6$. Find $g(x)$.',('M1',r'$(g(x)+3)^3=64x^6$.'),('A1',r'$g(x)+3=4x^2$, taking the unique real cube root.'),('A1',r'$g(x)=4x^2-3$.'))]);ck(17,(4*x*x)**3,64*x**6)
add(18,'Finding rational-function parameters','Rational functions',r'$f(x)=b+\dfrac6{x+a}$, where $a,b$ are integers. The vertical asymptote is $x=3$ and $f(1)=0$.',[
 P(r'State $a$.',('A1',r'$a=-3$.')),
 P(r'Find $b$.',('M1',r'Substitute $x=1$: $0=b+6/(1-3)$.'),('A1',r'$0=b-3$.'),('A1',r'$b=3$.')),
 P(r'State the horizontal asymptote.',('A1',r'$y=3$.'))])
add(19,'Intersecting perpendicular lines','Linear functions',r'$L_1$ has equation $3x+2y=12$. The line $L_2$ is perpendicular to $L_1$ and passes through $P(2,0)$.',[
 P(r'Find the gradient of $L_1$.',('M1',r'$y=-3x/2+6$.'),('A1',r'$m_1=-3/2$.')),
 P(r'State the gradient of $L_2$.',('A1',r'$m_2=2/3$.')),
 P(r'Find an equation of $L_2$ with integer coefficients.',('M1',r'$y=\frac23(x-2)$.'),('A1',r'$2x-3y-4=0$.')),
 P(r'Find $Q=L_1\cap L_2$.',('M1',r'Substitute $y=2x/3-4/3$ in $3x+2y=12$.'),('A1',r'$13x=44\Rightarrow x=44/13$.'),('A1',r'$Q=(44/13,12/13)$.'))]);ck(19,3*sp.Rational(44,13)+2*sp.Rational(12,13),12)
add(20,'Transformations of general functions','Transformations',r'$g(x)=4f(x-3)-2$. The graph of $g$ is obtained from $f$ by a vertical stretch of factor $k$, a horizontal translation of $a$ units and a vertical translation of $b$ units, in that order.',[
 P(r'State $k,a,b$, taking right and up as positive.',('A3',r'$k=4$, $a=3$, $b=-2$ (one each).')),
 P(r'$h(x)=-3g(x)$. The point $P(2,5)$ on $g$ maps to $Q$ on $h$. Find $Q$.',('M1',r'The abscissa stays 2.'),('M1',r'Multiply the ordinate by $-3$: $-3(5)=-15$.'),('A1',r'$Q=(2,-15)$.'))])
add(21,'An inverse square-root value','Composite and inverse functions',r'$f(x)=\sqrt{x+5}$, with $x\ge-5$.',[
 P(r'Find $f^{-1}(4)$.',('M1',r'$4=\sqrt{x+5}$.'),('M1',r'$16=x+5$.'),('A1',r'$f^{-1}(4)=11$.')),
 P(r'$g$ is invertible and $g(20)=6$. Find $(f\circ g^{-1})(6)$.',('M1',r'$g^{-1}(6)=20$.'),('M1',r'$f(20)=\sqrt{20+5}$.'),('A1',r'$5$.'))])
add(22,'Domains and ranges of inverses','Composite and inverse functions',r'$f(x)=\sqrt{x-4}$, $x\ge4$, and $g(x)=x^2+3$, $x\in\mathbb R$.',[
 P(r'Find $f^{-1}(x)$.',('M1',r'$y=\sqrt{x-4}\Rightarrow x=y^2+4$.'),('A1',r'$f^{-1}(x)=x^2+4$, $x\ge0$.')),
 P(r'Find $(g\circ f)(40)$.',('M1',r'$f(40)=6$, so $g(f(40))=6^2+3$.'),('A1',r'$39$.')),
 P(r'State the ranges of (i) $f^{-1}$; (ii) $g$.',('A2',r'(i) $[4,\infty)$; (ii) $[3,\infty)$ (one each).'))])
add(23,'Solving a cubic composition','Composite and inverse functions',r'$f(x)=x^3+8$ and $g(x)=x-3$, for real $x$.',[
 P(r'Find $f(2)$.',('M1',r'$2^3+8$.'),('A1',r'$16$.')),
 P(r'Find $f^{-1}(x)$.',('M1',r'$y=x^3+8\Rightarrow x=\sqrt[3]{y-8}$.'),('A1',r'$f^{-1}(x)=\sqrt[3]{x-8}$.')),
 P(r'Solve $(f\circ g)(x)=0$.',('M1',r'$(x-3)^3+8=0$.'),('A1',r'$x-3=-2$.'),('A1',r'$x=1$.'))])
add(24,'An exponential graph and transformation','Exponential and logarithmic functions',r'$f(x)=\tfrac12e^{x+1}-3$ for $-2\le x\le2$. Give numerical coordinates to three significant figures.',[
 P(r'Sketch $y=f(x)$.',('A1',r'An increasing convex exponential curve.'),('A1',r'Endpoints $(-2,-2.82)$ and $(2,7.04)$.'),('A1',r'Correct position relative to the $x$-axis and intercepts stated in (b).')),
 P(r'Find both axis intercepts.',('A1',r'$x$-intercept $(\ln6-1,0)\approx(0.792,0)$.'),('A1',r'$y$-intercept $(0,e/2-3)\approx(0,-1.64)$.')),
 P(r'Reflect $f$ in the $x$-axis, then translate 2 units right and 1 unit up. Find the new function $g$.',('M1',r'$g(x)=-f(x-2)+1$.'),('A1',r'$g(x)=-\tfrac12e^{x-1}+4$, $0\le x\le4$.'))],solution=graph([(lambda x:.5*math.exp(x+1)-3,R)],(-2,2),(-4,8)))
add(25,'An inverse from a graph','Composite and inverse functions',r'The graph shows an invertible function $f$ for $-2\le x\le4$.',[
 P(r'Read (i) $f(1)$; (ii) $f^{-1}(3)$.',('A2',r'(i) $1$; (ii) $3$ (one each).')),
 P(r'Find the domain of $f^{-1}$.',('M1',r'The inverse domain is the range of $f$.'),('A1',r'$[-3,4]$.')),
 P(r'Sketch the graph of $f^{-1}$.',('M1',r'Reflect in $y=x$.'),('A1',r'Join $(-3,-2)$, $(0,0)$ and $(4,4)$ with straight segments.'))],diagram=graph([(lambda x:1.5*x if x<0 else x,B)],(-2,4),(-3,4)),solution=graph([(lambda x:2*x/3 if x<0 else x,R)],(-3,4),(-2,4)))
add(26,'Recovering a quadratic from a graph','Quadratic functions',r'The graph shows $f(x)=3x^2+bx+c$.',[
 P(r'State $c$.',('A1',r'$c=-9$.')),
 P(r'Find $b$ and write $f(x)$.',('M1',r'The root $x=3$ gives $0=27+3b-9$.'),('A1',r'$b=-6$.'),('A1',r'$f(x)=3x^2-6x-9$.')),
 P(r'Find the vertex.',('M1',r'$x_v=-b/(2a)=1$, and $f(1)=-12$.'),('A1',r'The vertex is $(1,-12)$.'))],diagram=graph([(lambda x:3*x*x-6*x-9,B)],(-2,4),(-14,14),[(0,-9,'(0,-9)'),(3,0,'(3,0)')]))
add(27,'Tracking a point under transformations','Transformations',r'$f(x)=x^3$ and $g(x)=4(x-3)^3$.',[
 P(r'Describe two transformations mapping $f$ to $g$.',('A2',r'Vertical stretch by factor 4 and translation 3 units right (one each; either order).')),
 P(r'Translate $g$ 2 units right and 3 units down to obtain $h$. Find the image on $h$ of $P(1,1)$ on $f$.',('M1',r'Under the stretch, $P\mapsto(1,4)$.'),('A1',r'Under the first translation, $(1,4)\mapsto(4,4)$.'),('M1',r'Apply the further translation $(x,y)\mapsto(x+2,y-3)$.'),('A1',r'$Q=(6,1)$.'))])
add(28,'Symmetry determines a coefficient','Quadratic functions',r'$f(x)=ax^2-32x+c$. A horizontal line $L$ meets the graph at $x=1$ and $x=7$.',[
 P(r'(i) Find the axis of symmetry. (ii) Hence show that $a=4$.',('M1',r'The axis bisects 1 and 7.'),('A1',r'$x=4$.'),('M1',r'$-(-32)/(2a)=4$.'),('A1',r'$a=4$.')),
 P(r'$L$ has equation $y=9$. Find $c$.',('M1',r'Substitute $(1,9)$ into $f$.'),('A1',r'$9=4-32+c$.'),('A1',r'$c=37$.'))]);ck(28,4*7**2-32*7+37,9)
add(29,'Completing a square inside a composition','Composite and inverse functions',r'Consider the expression $3x^2-18x+29$.',[
 P(r'Express it in the form $a(x+b)^2+c$.',('M1',r'$3(x^2-6x)+29=3[(x-3)^2-9]+29$.'),('A1',r'$3(x-3)^2+2$.')),
 P(r'Given $f(x)=x-3$ and $(g\circ f)(x)=3x^2-18x+29$, find $g(x)$.',('M1',r'Let $u=x-3$.'),('A1',r'$g(u)=3u^2+2$.'),('A1',r'$g(x)=3x^2+2$.'))])
add(30,'Parameters of a hyperbola','Rational functions',r'The diagram shows $f(x)=a+\dfrac b{x-c}$, where $a,b,c$ are integers. Its asymptotes are drawn as dashed lines. Find $a,b,c$.',whole=[('A1',r'The horizontal asymptote gives $a=2$.'),('A1',r'The vertical asymptote gives $c=1$.'),('M1',r'Using $(0,-2)$: $-2=2+b/(0-1)$.'),('A1',r'$b=4$.')],diagram=graph([(lambda x:2+4/(x-1),B)],(-5,7),(-7,9),[(0,-2,'(0,-2)')],vl=[1],hl=[2]),note='Reference print omits its graph and final instruction. Reconstructed a labelled graph for the stated three-parameter rational-function skill, retaining the 4-mark scale.')
add(31,'Exponential pressure model','Exponential and logarithmic functions',r'A model for air pressure is $P(h)=100(1.15)^{-h}$ kPa, where $h$ is altitude in kilometres.',[
 P(r'State the pressure at sea level.',('A1',r'$P(0)=100$ kPa.')),
 P(r'Find the pressure at a summit 2600 m above sea level.',('M1',r'Use $h=2.6$: $100(1.15)^{-2.6}$.'),('A1',fr'$P(2.6)\approx{100*1.15**(-2.6):#.3g}$ kPa.')),
 P(r'Find the altitude at which the pressure is 12 kPa.',('M1',r'$12/100=1.15^{-h}$.'),('M1',r'$h=-\ln(0.12)/\ln(1.15)$.'),('A1',fr'$h\approx{-math.log(.12)/math.log(1.15):#.3g}$ km.'))])
add(32,'Asymptotes determine coefficients','Rational functions',r'$f(x)=\dfrac{ax+b}{2x+c}$. Its asymptotes are $x=-3$ and $y=2$. The graph contains $(1,-\tfrac14)$. Find $a,b,c$.',whole=[('A1',r'$2(-3)+c=0\Rightarrow c=6$.'),('M1',r'The horizontal asymptote is the ratio $a/2$.'),('A1',r'$a=4$.'),('M1',r'$-1/4=(4+b)/(2+6)$.'),('A1',r'$4+b=-2$.'),('A1',r'$b=-6$, so $(a,b,c)=(4,-6,6)$.')])
add(33,'A population approaching a limit','Exponential and logarithmic functions',r'A population is modelled by $P(t)=6400\times2^{-t}+80$ for $t\ge0$, where $t$ is in days.',[
 P(r'State the initial population.',('A1',r'$P(0)=6480$.')),
 P(r'Find the population after 4 days.',('M1',r'$P(4)=6400/16+80$.'),('A1',r'$480$.')),
 P(r'Find when the population reaches 105.',('M1',r'$6400\times2^{-t}=25\Rightarrow2^t=256$.'),('A1',r'$t=8$ days.')),
 P(r'State the limiting population.',('A1',r'$80$.'))]);ck(33,sp.Rational(6400,2**8)+80,105)
b34=math.log(1.8,2)
add(34,'Fitting a power model','Exponential and logarithmic functions',r'Monthly visits to a new online archive are modelled by $H=aN^b$, where $N$ is the month number. In month 1 there were 200 visits; in month 2 there were 360.',[
 P(r'(i) State $a$. (ii) Find $b$ to five significant figures.',('A1',r'$a=200$.'),('M1',r'$360=200(2^b)\Rightarrow2^b=1.8$.'),('M1',r'$b=\ln1.8/\ln2$.'),('A1',fr'$b\approx{b34:#.5g}$.')),
 P(r'Estimate visits in month 8, to the nearest integer.',('A1',r'$H(8)=200(1.8)^3=1166.4\approx1166$.'))])
add(35,'Roots from symmetry and separation','Quadratic functions',r'$f(x)=x^2+bx+c$ has its minimum at $x=\tfrac72$. Its two $x$-intercepts are 9 units apart.',[
 P(r'Find the intercepts.',('M1',r'They lie $9/2$ on either side of $7/2$.'),('A1',r'$(-1,0)$ and $(8,0)$.')),
 P(r'Find $b$ and $c$.',('M1',r'$f(x)=(x+1)(x-8)$.'),('A1',r'$f(x)=x^2-7x-8$.'),('A2',r'$b=-7$, $c=-8$ (one each).'))])
add(36,'A limit of a composition','Composite and inverse functions',r'$f(x)=e^x-3$ and $g(x)=4x+k$.',[
 P(r'Find $(g\circ f)(x)$.',('M1',r'$g(f(x))=4(e^x-3)+k$.'),('A1',r'$4e^x-12+k$.')),
 P(r'Given $\lim_{x\to-\infty}(g\circ f)(x)=-5$, find $k$.',('M1',r'$e^x\to0$ as $x\to-\infty$.'),('A1',r'$-12+k=-5$.'),('A1',r'$k=7$.'))])
add(37,'Composing and reflecting a graph','Transformations',r'The diagram shows an invertible function $f$ for $-1\le x\le2$.',[
 P(r'Write down (i) $f(1)$; (ii) $f^{-1}(-3)$.',('A2',r'(i) $f(1)=1$; (ii) $f^{-1}(-3)=-1$ (one each).')),
 P(r'Find $(f\circ f)(1)$.',('M1',r'$f(f(1))=f(1)$.'),('A1',r'$1$.')),
 P(r'Sketch $y=f(-x)$ and state its domain.',('M1',r'Reflect in the $y$-axis.'),('A1',r'The graph passes through $(1,-3),(0,-2),(-1,1),(-2,6)$, with domain $[-2,1]$.'))],diagram=graph([(lambda x:(x+1)**2-3,B)],(-1,2),(-4,7)),solution=graph([(lambda x:(1-x)**2-3,R)],(-2,1),(-4,7)))
add(38,'Exponential wildlife growth','Exponential and logarithmic functions',r'A reserve initially contains 60 rabbits. After one month there are 75. The model is $P(t)=60b^t$, where $t$ is in months.',[
 P(r'Find $b$.',('M1',r'$75=60b$.'),('A1',r'$b=1.25$.')),
 P(r'Estimate the population after 6 months.',('M1',r'$P(6)=60(1.25)^6=228.8818\ldots$.'),('A1',r'Approximately 229 rabbits.')),
 P(r'Find the time at which the model reaches 2400 rabbits.',('M1',r'$1.25^t=40\Rightarrow t=\ln40/\ln1.25$.'),('A1',fr'$t\approx{math.log(40)/math.log(1.25):#.3g}$ months.'))])
add(39,'A quadratic from labelled intercepts','Quadratic functions',r'The graph shows $f(x)=ax^2+bx+48$.',[
 P(r'Find $a$ and $b$.',('M1',r'The roots give $f(x)=a(x+4)(x-6)$.'),('A1',r'$-24a=48\Rightarrow a=-2$.'),('M1',r'Expand $-2(x^2-2x-24)$.'),('A1',r'$b=4$.')),
 P(r'Find the vertex.',('M1',r'$x_v=(-4+6)/2=1$, $f(1)=50$.'),('A1',r'$(1,50)$.'))],diagram=graph([(lambda x:-2*x*x+4*x+48,B)],(-5,7),(-15,60),[(-4,0,'(-4,0)'),(6,0,'(6,0)'),(0,48,'(0,48)')]),note='The reference print omits the graph and its task parts. Reconstructed a 6-mark coefficient/vertex problem from the stated quadratic form.')
add(40,'Constructing a downward parabola','Quadratic functions',r'A quadratic has axis of symmetry $x=2$ and one $x$-intercept $P(-2,0)$. Its equation is $y=-x^2+bx+c$.',[
 P(r'Draw the axis of symmetry.',('A1',r'A vertical line $x=2$.')),
 P(r'Find and label both $x$-intercepts.',('M1',r'Reflect $x=-2$ about $x=2$: $x_Q=6$.'),('A1',r'$P(-2,0)$ and $Q(6,0)$.')),
 P(r'Find $b,c$ and the vertex, then sketch the graph.',('M1',r'$y=-(x+2)(x-6)=-x^2+4x+12$.'),('A1',r'$b=4$, $c=12$.'),('A1',r'Vertex $(2,16)$.'),('A1',r'Downward parabola through $(-2,0),(0,12),(6,0)$ with that vertex.'))],solution=graph([(lambda x:-x*x+4*x+12,R)],(-3,7),(-5,18)))
add(41,'A discrete pair of functions','Composite and inverse functions',r'The table defines $f$ and $g$ on $\{1,2,3,4,5\}$.\n\n| $x$ | 1 | 2 | 3 | 4 | 5 |\n|---|---|---|---|---|---|\n| $f(x)$ | 2 | 4 | 1 | 5 | 3 |\n| $g(x)$ | 5 | 3 | 4 | 1 | 2 |',[
 P(r'State $f(2)$.',('A1',r'$f(2)=4$.')),
 P(r'Find $(g\circ f)(2)$.',('M1',r'$g(f(2))=g(4)$.'),('A1',r'$1$.')),
 P(r'Find $g^{-1}(4)$.',('M1',r'Find the input whose $g$-output is 4.'),('A1',r'$g^{-1}(4)=3$.'))])
add(42,'Two distinct real roots','Discriminants',r'$x^2-kx+4=0$ has two distinct real roots. Find all possible real $k$.',whole=[('M1',r'Require discriminant strictly positive.'),('A1',r'$k^2-16>0$.'),('M1',r'Factorise $(k-4)(k+4)>0$.'),('A1',r'$k<-4$.'),('A1',r'Or $k>4$. Endpoints are excluded.')])
add(43,'A graph involving modulus','Modulus functions',r'Let $f(x)=(x-1)^2-3|x-1|-2$ for $-4\le x\le6$.',[
 P(r'Sketch $y=f(x)$, labelling its turning points.',('A1',r'The graph is symmetric about $x=1$ with central local maximum $(1,-2)$.'),('A1',r'Local minima occur at $x=1\pm3/2$, with ordinate $-17/4$.'),('A1',r'Correct upward outer arms, through the endpoints $(-4,8)$ and $(6,8)$.')),
 P(r'Solve $f(x)=0$ to three significant figures.',('M1',r'Put $u=|x-1|\ge0$: $u^2-3u-2=0$, so $u=(3+\sqrt{17})/2$.'),('A1',r'$x=1\pm(3+\sqrt{17})/2\approx-2.56,\ 4.56$.'))],solution=graph([(lambda x:(x-1)**2-3*abs(x-1)-2,R)],(-4,6),(-5,9)))
rectsvg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 220" role="img" aria-label="Two adjacent rectangular plots, each width x and height y"><rect x="60" y="40" width="400" height="130" fill="none" stroke="#253c66" stroke-width="2"/><line x1="260" y1="40" x2="260" y2="170" stroke="#253c66" stroke-width="2"/><text x="155" y="195" font-size="18">x</text><text x="355" y="195" font-size="18">x</text><text x="35" y="110" font-size="18">y</text></svg>'
add(44,'Fencing adjacent plots','Quadratic models',r'Two adjacent rectangular plots each have width $x$ metres and height $y$ metres. The shared boundary is fenced. Exactly 96 m of fencing is available.',[
 P(r'Write the fencing equation.',('A1',r'$4x+3y=96$.')),
 P(r'Express the total area $A$ in terms of $x$.',('M1',r'$y=(96-4x)/3$ and $A=2xy$.'),('A1',r'$A(x)=64x-\frac83x^2$, $0<x<24$.')),
 P(r'Find the maximum area of one plot.',('M1',r'The total-area parabola has vertex $x=-64/[2(-8/3)]=12$.'),('A1',r'Then $y=16$ and total area $384$ m$^2$.'),('A1',r'One plot has maximum area $192$ m$^2$.'))],diagram=rectsvg)
add(45,'Inverse composition evaluated implicitly','Composite and inverse functions',r'$f(x)=\dfrac{x-3}{4}$ and $g(x)=20x+5$.',[
 P(r'Show that $(g\circ f)(x)=5x-10$.',('M1',r'$20((x-3)/4)+5=5(x-3)+5$.'),('A1',r'This simplifies to $5x-10$.')),
 P(r'Given $(g\circ f)^{-1}(a)=8$, find $a$.',('M1',r'Apply $g\circ f$ to both sides.'),('M1',r'$a=(g\circ f)(8)=5(8)-10$.'),('A1',r'$a=30$.'))])
add(46,'Two remainders determine coefficients','Polynomials',r'$f(x)=x^4+3x^3+ax^2+bx+4$. Division by $x-1$ leaves remainder 8; division by $x+2$ leaves remainder $-30$. Find $a,b$.',whole=[('M1',r'Use the remainder theorem at 1 and $-2$.'),('A1',r'$a+b=0$.'),('A1',r'$4a-2b=-26$.'),('M1',r'Solve with $b=-a$: $6a=-26$.'),('A1',r'$a=-13/3$, $b=13/3$.')]);ck(46,(-2)**4+3*(-2)**3-sp.Rational(13,3)*4+sp.Rational(13,3)*(-2)+4,-30)
add(47,'Using a vertex axis and one root','Quadratic functions',r'A quadratic has $y$-intercept $(0,40)$, one $x$-intercept $(2,0)$, and axis of symmetry $x=6$. Write it as $f(x)=ax^2+bx+c$.',[
 P(r'State $c$.',('A1',r'$c=40$.')),
 P(r'Find $a,b$.',('M1',r'Symmetry gives the second root 10, so $f(x)=a(x-2)(x-10)$.'),('A1',r'$20a=40\Rightarrow a=2$.'),('M1',r'Expand $2(x^2-12x+20)$.'),('A1',r'$b=-24$.')),
 P(r'State the second $x$-intercept.',('A1',r'$(10,0)$.'))])
add(48,'A parameter with one excluded value','Discriminants',r'$x^2+(k-4)x-4k=0$ has two distinct real roots. Find the possible values of $k$.',whole=[('M1',r'Require $(k-4)^2-4(1)(-4k)>0$.'),('A1',r'$k^2+8k+16>0$.'),('M1',r'$(k+4)^2>0$.'),('A1',r'Equality occurs only at $k=-4$.'),('A1',r'All real $k\ne-4$.')])
add(49,'Asymptote, intercept and limit','Rational functions',r'$f(x)=\dfrac3{x-a}+b$. Its vertical asymptote is $x=2$, and the graph passes through $(0,\tfrac72)$.',[
 P(r'State $a$.',('A1',r'$a=2$.')),
 P(r'Find $b$.',('M1',r'$7/2=3/(0-2)+b$.'),('A1',r'$7/2=-3/2+b$.'),('A1',r'$b=5$.')),
 P(r'Find $\lim_{x\to\infty}f(x)$.',('M1',r'$3/(x-2)\to0$.'),('A1',r'The limit is $5$.'))])
add(50,'Inverse perimeter-area model','Composite and inverse functions',r'The area of a square is $A(P)=P^2/16$, where $P$ is its perimeter and $0\le P\le24$.',[
 P(r'Find $A(24)$.',('A1',r'$A(24)=36$.')),
 P(r'Sketch the inverse function, stating its domain.',('M1',r'From $y=P^2/16$ take the non-negative square root.'),('A1',r'$A^{-1}(x)=4\sqrt x$, $0\le x\le36$.'),('A1',r'A rising concave-down curve from $(0,0)$ to $(36,24)$; it reflects the original in $y=x$.')),
 P(r'Interpret $A^{-1}(9)=12$.',('A1',r'A square of area 9 square units has perimeter 12 units.'))],solution=graph([(lambda x:4*math.sqrt(max(0,x)),R)],(0,36),(0,26)))
add(51,'Recovering an outer function','Composite and inverse functions',r'Consider $2x^2+16x+35$.',[
 P(r'Complete the square.',('M1',r'$2(x^2+8x)+35=2[(x+4)^2-16]+35$.'),('A1',r'$2(x+4)^2+3$.')),
 P(r'$f(x)=x+4$ and $(g\circ f)(x)=2x^2+16x+35$. Find $g(x)$.',('M1',r'Let $u=x+4$.'),('A1',r'$g(u)=2u^2+3$.'),('A1',r'$g(x)=2x^2+3$.'))])
add(52,'Cube-root function and inverse','Composite and inverse functions',r'$f(x)=\sqrt[3]{3x+2}$ for $-22\le x\le42$.',[
 P(r'State the range of $f$.',('M1',r'$f(-22)=-4$, $f(42)=\sqrt[3]{128}$; $f$ is strictly increasing.'),('A1',r'$[-4,\sqrt[3]{128}]$.')),
 P(r'Find $f^{-1}(x)$.',('M1',r'$y^3=3x+2$.'),('A1',r'$f^{-1}(x)=(x^3-2)/3$.')),
 P(r'State the domain and range of $f^{-1}$.',('A2',r'Domain $[-4,\sqrt[3]{128}]$; range $[-22,42]$ (one each).'))])
add(53,'Remainder of a product','Polynomials',r'When $(2x^2+3x-1)(ax+1)$ is divided by $x-2$, the remainder is $-39$. Find $a$.',whole=[('M1',r'The remainder equals the product evaluated at 2.'),('A1',r'$(8+6-1)(2a+1)=-39$.'),('M1',r'$13(2a+1)=-39\Rightarrow2a+1=-3$.'),('A1',r'$a=-2$.')])
b54=1.1;t54=math.log(1e6/400000)/math.log(b54)
add(54,'A growing membership model','Exponential and logarithmic functions',r'An online learning community had 400000 members on 1 January 2020 and 440000 on 1 January 2021. Model membership by $N(t)=400000b^t$, where $t$ is years after 1 January 2020.',[
 P(r'Find the exact value of $b$.',('M1',r'$440000=400000b$.'),('A1',r'$b=11/10$.')),
 P(r'Estimate membership on 1 January 2026.',('M1',r'$N(6)=400000(1.1)^6=708624.4$.'),('A1',r'Approximately $708624$ members.')),
 P(r'During which calendar year does the model reach one million?',('M1',r'$t=\ln(2.5)/\ln(1.1)\approx9.61$.'),('A1',r'During 2029.'))])
add(55,'Factor and remainder conditions','Polynomials',r'$x-5$ is a factor of $f(x)=x^3-3x^2+ax+b$. Division by $x+1$ leaves remainder 12. Find $a,b$.',whole=[('M1',r'Use $f(5)=0$.'),('A1',r'$5a+b=-50$.'),('M1',r'Use $f(-1)=12$.'),('A1',r'$-a+b=16$.'),('M1',r'Subtract: $6a=-66$.'),('A1',r'$a=-11$, $b=5$.')]);ck(55,5**3-3*5**2-11*5+5,0)
add(56,'A rational function and its inverse value','Rational functions',r'$f(x)=\dfrac{a-4x}{x-3}$, $x\ne3$, and $a\ne12$. It is known that $f(1)=f^{-1}(1)$.',[
 P(r'State both asymptotes.',('A2',r'$x=3$ and $y=-4$ (one each).')),
 P(r'Find $a$.',('M1',r'$f(1)=(4-a)/2$ and $f^{-1}(x)=(a+3x)/(x+4)$.'),('A1',r'$(4-a)/2=(a+3)/5\Rightarrow20-5a=2a+6$.'),('A1',r'$a=2$.')),
 P(r'Sketch $f$, labelling asymptotes and intercepts.',('A1',r'Intercepts $(1/2,0)$ and $(0,-2/3)$.'),('A1',r'Hyperbola $y=-4-10/(x-3)$ with asymptotes $x=3,y=-4$, correct branch orientations.'))],solution=graph([(lambda x:-4-10/(x-3),R)],(-5,9),(-12,8),vl=[3],hl=[-4]))
b57=(4000/1000)**(1/3)
add(57,'A memory-retention model','Exponential and logarithmic functions',r'The number of vocabulary items recalled is $N(t)=ab^{-t}+500$, where $t$ is years and $a,b>0$. Initially 4500 items are recalled; after 3 years, 1500 are recalled.',[
 P(r'Find $a$.',('M1',r'$4500=a+500$.'),('A1',r'$a=4000$.')),
 P(r'Find $b$.',('M1',r'$1500=4000b^{-3}+500$.'),('A1',r'$b^3=4$.'),('A1',r'$b=\sqrt[3]4\approx1.59$.')),
 P(r'State the lower limiting number recalled.',('A1',r'$500$.'))])
add(58,'Sketching a linear rational function','Rational functions',r'$f(x)=\dfrac{4x-8}{x+2}$, $x\ne-2$.',[
 P(r'Find both axis intercepts.',('M1',r'For the $x$-intercept set $4x-8=0$.'),('A1',r'$(2,0)$.'),('A1',r'$f(0)=-4$, so $(0,-4)$.')),
 P(r'Find both asymptotes.',('M1',r'Compare leading coefficients and set the denominator to zero.'),('A2',r'Horizontal $y=4$ and vertical $x=-2$ (one each).')),
 P(r'Sketch the graph.',('A1',r'Hyperbola through the two intercepts, approaching the stated asymptotes.'),('A1',r'Use $f(x)=4-16/(x+2)$: left branch above 4, right branch below 4.'))],solution=graph([(lambda x:4-16/(x+2),R)],(-9,8),(-12,15),vl=[-2],hl=[4]))
add(59,'An even rational function and its range','Rational functions',r'$f(x)=\dfrac{3x^2-54}{x^2-9}$, $x\ne\pm3$.',[
 P(r'Prove that $f$ is even.',('M1',r'$f(-x)=[3(-x)^2-54]/[(-x)^2-9]$.'),('A1',r'$f(-x)=f(x)$ on the symmetric domain.')),
 P(r'Sketch $f$ and state its range.',('A1',r'Vertical asymptotes $x=\pm3$, horizontal asymptote $y=3$.'),('A1',r'Intercepts $(\pm3\sqrt2,0)$ and $(0,6)$.'),('A1',r'Central branch has minimum $(0,6)$; outer branches lie below 3.'),('M1',r'Write $f=3-27/(x^2-9)$ and consider $x^2<9$ or $x^2>9$.'),('A1',r'Range $(-\infty,3)\cup[6,\infty)$.'))],solution=graph([(lambda x:(3*x*x-54)/(x*x-9),R)],(-8,8),(-10,14),vl=[-3,3],hl=[3]))
add(60,'Composing depth and pressure','Composite models',r'Water pressure is modelled by $P(D)=D/10+1$ atmospheres at depth $D$ metres. A submersible follows $D(t)=15+4t$, with $t$ in minutes.',[
 P(r'Find and interpret $(P\circ D)(t)$.',('M1',r'$P(D(t))=(15+4t)/10+1$.'),('A1',r'$(P\circ D)(t)=2.5+0.4t$.'),('R1',r'This is the pressure in atmospheres at time $t$ minutes.')),
 P(r'Find and interpret $(P\circ D)(12)$.',('M1',r'$2.5+0.4(12)=7.3$.'),('A1',r'After 12 minutes the pressure is 7.3 atmospheres.'))])
add(61,'A quartic obtained by composition','Composite and inverse functions',r'$f(x)=\tfrac12x^2-1$ and $g(x)=x^2-4$.',[
 P(r'Show that $(f\circ g)(x)=\tfrac12x^4-4x^2+7$.',('M1',r'$\tfrac12(x^2-4)^2-1=\tfrac12(x^4-8x^2+16)-1$.'),('A1',r'This simplifies to $\tfrac12x^4-4x^2+7$.')),
 P(r'Sketch this composition for $0\le x\le3$.',('A1',r'Endpoint $(0,7)$, falling to $(2,-1)$.'),('A1',r'Minimum $(2,-1)$ and then a rising branch.'),('A1',r'Endpoint $(3,23/2)$.')),
 P(r'Find all $k$ for which $(f\circ g)(x)=k$ has exactly two distinct solutions in $[0,3]$.',('M1',r'Two intersections occur above the minimum and no higher than the lower endpoint value.'),('A1',r'$k>-1$ and $k\le7$.'),('A1',r'$-1<k\le7$.'))],solution=graph([(lambda x:.5*x**4-4*x*x+7,R)],(0,3),(-2,12)))
add(62,'A downward quadratic from equal values','Quadratic functions',r'$f(x)=-4x^2+bx+c$ and $f(-2)=f(6)=h$.',[
 P(r'Find the axis of symmetry and hence show $b=16$.',('M1',r'The midpoint of $-2$ and 6 is 2.'),('A1',r'The axis is $x=2$.'),('M1',r'$-b/(2(-4))=2$.'),('A1',r'$b=16$.')),
 P(r'Given $h=-12$, find $c$.',('M1',r'$-12=-4(-2)^2+16(-2)+c$.'),('A1',r'$-12=-48+c$.'),('A1',r'$c=36$.'))])
add(63,'Profit as a composite model','Composite models',r'A workshop produces $N(t)=4t-8$ items after operating $t\ge2$ hours per day. Profit in dollars is $P(N)=50N-600$.',[
 P(r'Find profit or loss for a 5-hour day.',('M1',r'$N(5)=12$ and $P(12)=600-600$.'),('A1',r'Zero profit: the workshop breaks even.')),
 P(r'Express profit in terms of $t$.',('M1',r'$P(N(t))=50(4t-8)-600$.'),('A1',r'$P(t)=200t-1000$.')),
 P(r'Find the minimum whole number of operating hours needed for positive profit.',('M1',r'$200t-1000>0\Rightarrow t>5$.'),('A1',r'At least 6 whole hours.'))])
add(64,'Transforming a piecewise function','Transformations',r'$$f(x)=\begin{cases}3x-1,&x\ge2,\\-x^2+2x+5,&x<2.\end{cases}$$',[
 P(r'Determine whether $f$ is continuous at $x=2$.',('M1',r'The left limit is $-4+4+5=5$ and $f(2)=6-1=5$.'),('R1',r'The limits and function value agree, so $f$ is continuous at 2.')),
 P(r'Translate $f$ 1 unit left, reflect in the $x$-axis, then stretch vertically by factor 2. Find $g(x)$.',('M1',r'$g(x)=-2f(x+1)$.'),('A1',r'The boundary becomes $x=1$.'),('A1',r'For $x\ge1$, $g(x)=-2[3(x+1)-1]=-6x-4$.'),('A1',r'For $x<1$, $g(x)=-2[-(x+1)^2+2(x+1)+5]=2x^2-12$.'))])
add(65,'Inverse circumference-area model','Composite and inverse functions',r'A circle has circumference $C(A)=2\sqrt{\pi A}$ in terms of area $A$, with $0\le A\le36$.',[
 P(r'Find $C(36)$ to three significant figures.',('A1',r'$C(36)=12\sqrt\pi\approx21.3$.')),
 P(r'Sketch the inverse function and state its domain.',('M1',r'$y=2\sqrt{\pi A}\Rightarrow A=y^2/(4\pi)$.'),('A1',r'$C^{-1}(x)=x^2/(4\pi)$, $0\le x\le12\sqrt\pi$.'),('A1',r'Rising convex curve from $(0,0)$ to $(12\sqrt\pi,36)$, the reflection in $y=x$.')),
 P(r'Interpret $C^{-1}(6\pi)=9\pi$.',('A1',r'A circle with circumference $6\pi$ units has area $9\pi$ square units.'))],solution=graph([(lambda x:x*x/(4*math.pi),R)],(0,12*math.sqrt(math.pi)),(0,36)))
add(66,'Comparing two exponential models','Exponential and logarithmic functions',r'A conservation programme began on 1 January 1980 with 12 birds. A model $P(t)=12e^{kt}$ uses $t$ years after that date. There were 60 birds on 1 January 2000.',[
 P(r'Use this model to estimate the population on 1 January 2030.',('M1',r'$60=12e^{20k}\Rightarrow e^{20k}=5$.'),('A1',r'$k=\ln5/20$.'),('M1',r'$P(50)=12e^{50\ln5/20}=12\cdot5^{5/2}$.'),('A1',r'$P(50)\approx671$ birds.')),
 P(r'The actual 2030 population is 720. A second model uses a constant annual percentage increase $r$ from 12 to 720 over 50 years. Find $r$.',('M1',r'$720=12(1+r/100)^{50}$.'),('A1',r'$r=100(60^{1/50}-1)$.'),('A1',fr'$r\approx{100*(60**.02-1):#.3g}\%$.'))])
add(67,'Two intersections with a hyperbola','Discriminants',r'The line $y=x-p$ meets $f(x)=p-\dfrac{25}{x}$, $x\ne0$, at two distinct points. Find the possible values of real $p$.',whole=[('M1',r'Set $x-p=p-25/x$.'),('A1',r'$x^2-2px+25=0$.'),('M1',r'Two intersections require $(-2p)^2-100>0$.'),('A1',r'$p^2>25$.'),('A1',r'$p<-5$ or $p>5$.'),('R1',r'Neither intersection can have $x=0$ because the product of the roots is 25, so both satisfy the original domain.')])
add(68,'Squared roots and Vieta relations','Polynomials',r'The roots of $x^2-kx+(k-2)=0$ are $\alpha,\beta$. Without solving for the roots, find real $k$ if $\alpha^2+\beta^2=28$.',whole=[('A1',r'$\alpha+\beta=k$, $\alpha\beta=k-2$.'),('M1',r'$\alpha^2+\beta^2=(\alpha+\beta)^2-2\alpha\beta$.'),('A1',r'$k^2-2(k-2)=28\Rightarrow k^2-2k-24=0$.'),('M1',r'$(k-6)(k+4)=0$.'),('A1',r'$k=6$ or $k=-4$.')])
add(69,'A parameter from root identities','Polynomials',r'The roots of $x^2-kx+(k-4)=0$ are $\alpha,\beta$, with $\alpha^2+\beta^2=12$. Find real $k$ without first solving the quadratic for its roots.',whole=[('A1',r'$\alpha+\beta=k$.'),('A1',r'$\alpha\beta=k-4$.'),('M1',r'Use $(\alpha+\beta)^2-2\alpha\beta=12$.'),('A1',r'$k^2-2k-4=0$.'),('M1',r'$k=(2\pm\sqrt{4+16})/2$.'),('A1',r'$k=1\pm\sqrt5$.')])
track='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 560 260" role="img" aria-label="Stadium-shaped track inside a rectangular field"><rect x="20" y="20" width="520" height="220" fill="none" stroke="#aaa"/><path d="M160,65 L400,65 A65,65 0 0 1 400,195 L160,195 A65,65 0 0 1 160,65" fill="none" stroke="#253c66" stroke-width="2"/><line x1="160" y1="130" x2="160" y2="65" stroke="#7a1f24"/><text x="168" y="102" font-size="17">x</text><text x="263" y="55" font-size="16">90 m</text><text x="250" y="255" font-size="15">field: 150 m × 60 m</text></svg>'
add(70,'Perimeter and an inverse track model','Composite models',r'A stadium-shaped path consists of two straight sections of length 90 m joined by two semicircles of radius $x$ m. It must fit inside a rectangular field 150 m long and 60 m wide, with the straight sections parallel to the longer side.',[
 P(r'Write the perimeter $P(x)$.',('A1',r'$P(x)=180+2\pi x$.')),
 P(r'State the physical domain of $P$ and its range.',('M1',r'The width gives $2x\le60$ and the length gives $90+2x\le150$.'),('A1',r'$0<x\le30$; $180<P\le180+60\pi$.')),
 P(r'Find $P^{-1}(p)$.',('M1',r'Solve $p=180+2\pi x$ for $x$.'),('A1',r'$P^{-1}(p)=(p-180)/(2\pi)$.')),
 P(r'Would a 360 m perimeter fit? Justify.',('M1',r'The required radius is $180/(2\pi)=90/\pi\approx28.6$ m.'),('A1',r'Yes, since this is less than 30 m (both dimensions fit).'))],diagram=track,note='Reference print loses its task parts after the track introduction. Reconstructed the perimeter/domain/inverse modelling sequence at the same 7-mark scale.')
window='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" role="img" aria-label="Window with a rectangular base and a semicircular top"><path d="M90,260 L90,150 A110,110 0 0 1 310,150 L310,260 Z" fill="none" stroke="#253c66" stroke-width="2"/><line x1="90" y1="150" x2="310" y2="150" stroke="#aaa" stroke-dasharray="5 4"/><text x="180" y="281" font-size="18">2x</text><text x="320" y="210" font-size="16">1.2 m</text><line x1="200" y1="150" x2="310" y2="150" stroke="#7a1f24"/><text x="248" y="140" font-size="18">x</text></svg>'
add(71,'A semicircular window model','Composite models',r'A window has a rectangular base of fixed height 1.2 m and width $2x$, topped by a semicircle of radius $x$. The available wall space is 2.4 m wide and 2.6 m high.',[
 P(r'Write its perimeter $P(x)$.',('A1',r'$P(x)=2.4+(2+\pi)x$.')),
 P(r'State the physical domain and range of $P$.',('M1',r'$2x\le2.4$ and $1.2+x\le2.6$, hence $0<x\le1.2$.'),('A1',r'$2.4<P\le4.8+1.2\pi\approx8.57$ m.')),
 P(r'Find the inverse formula.',('M1',r'Solve $p=2.4+(2+\pi)x$.'),('A1',r'$P^{-1}(p)=(p-2.4)/(2+\pi)$.')),
 P(r'Frames are sold only in lengths 7 m, 8 m or 9 m. The full chosen length must be used without cutting. Which gives the largest window that fits?',('M1',r'Area $2.4x+\pi x^2/2$ and perimeter both increase with positive $x$.'),('A1',r'Choose 8 m: it is the largest available perimeter not exceeding $8.57$ m; 9 m does not fit.'))],diagram=window)
add(72,'Quadratic structure and a point transformation','Quadratic functions',r'$f(x)=a(x+2)(x+6)$ has $y$-intercept $(0,-24)$.',[
 P(r'Find both $x$-intercepts and $a$.',('A2',r'$(-2,0)$ and $(-6,0)$ (one each).'),('M1',r'Use $f(0)=-24$.'),('A1',r'$12a=-24$.'),('M1',r'Divide by 12.'),('A1',r'$a=-2$.')),
 P(r'Find the axis of symmetry.',('M1',r'Average the roots: $(-2-6)/2$.'),('A1',r'$x=-4$.')),
 P(r'Find the vertex.',('M1',r'Evaluate $f(-4)$.'),('A1',r'$-2(-2)(2)=8$.'),('A1',r'$(-4,8)$.')),
 P(r'Reflect in the $y$-axis, then translate 3 units up. Find the image of $P(-5,6)$.',('M1',r'Reflection changes the sign of the abscissa.'),('A1',r'$(-5,6)\mapsto(5,6)$.'),('M1',r'Add 3 to the ordinate.'),('A1',r'$Q=(5,9)$.'))])
add(73,'Quadratic forms and a reflected graph','Quadratic functions',r'$f(x)=2x^2+12x+16$.',[
 P(r'Find all axis intercepts.',('M1',r'$f(0)=16$.'),('A1',r'$y$-intercept $(0,16)$.'),('M1',r'$f(x)=2(x+2)(x+4)$.'),('A1',r'$x$-intercepts $(-2,0),(-4,0)$.')),
 P(r'Write $f(x)=a(x-h)^2+k$, finding $a,h,k$.',('M1',r'Factor out 2 from the quadratic and linear terms.'),('A1',r'$2(x^2+6x)+16$.'),('M1',r'Complete the square: $x^2+6x=(x+3)^2-9$.'),('A1',r'$f(x)=2(x+3)^2-2$.'),('A1',r'$a=2,h=-3,k=-2$.')),
 P(r'State the vertex and symmetry axis.',('A2',r'Vertex $(-3,-2)$; axis $x=-3$ (one each).')),
 P(r'Reflect in the $x$-axis, then translate 5 units up. Find $g(x)$ in expanded form.',('M1',r'Reflection gives $-f(x)$.'),('A1',r'$-2x^2-12x-16$.'),('M1',r'Add 5.'),('A1',r'$g(x)=-2x^2-12x-11$.'))])
add(74,'A quadratic with a double root','Quadratic functions',r'$f(x)=3x^2+12x+p$. The equation $f(x)=0$ has two equal real roots.',[
 P(r'State the discriminant and hence find $p$.',('A1',r'The discriminant is zero.'),('M1',r'$12^2-4(3)p=0$.'),('A1',r'$p=12$.')),
 P(r'Find the axis of symmetry and vertex.',('M1',r'$x_v=-12/(2\cdot3)$.'),('A1',r'Axis $x=-2$.'),('M1',r'$f(-2)=12-24+12=0$.'),('A1',r'Vertex $(-2,0)$.')),
 P(r'State the solution of $f(x)=0$.',('A1',r'$x=-2$.')),
 P(r'Write $f(x)=a(x-h)^2+k$.',('M1',r'$3x^2+12x+12=3(x^2+4x+4)$.'),('A1',r'$f(x)=3(x+2)^2$.'),('A3',r'$a=3,h=-2,k=0$ (one each).')),
 P(r'Reflect in the $x$-axis. Find the new vertex.',('M1',r'$(x,y)\mapsto(x,-y)$.'),('A1',r'The vertex remains $(-2,0)$.'))])
add(75,'Exponential inverse sketch','Exponential and logarithmic functions',r'$f(x)=4e^{x/3}$ for real $x$.',[
 P(r'State the horizontal asymptote of $f$.',('A1',r'$y=0$.')),
 P(r'State the $y$-intercept.',('A1',r'$(0,4)$.')),
 P(r'Sketch the inverse, labelling its intercept and asymptote.',('M1',r'Reflect the exponential graph in $y=x$; equivalently $f^{-1}(x)=3\ln(x/4)$.'),('A1',r'Increasing concave-down log curve with intercept $(4,0)$ and asymptote $x=0$.')),
 P(r'State the domain of $f^{-1}$.',('A1',r'$(0,\infty)$.'))],solution=graph([(lambda x:3*math.log(x/4),R)],(.05,10),(-7,4),vl=[0]))
add(76,'A tangent line and an unknown coefficient','Discriminants',r'The line $y=2x+1$ touches $g(x)=3x^2+kx+4$ at exactly one point. Find the possible values of $k$.',whole=[('M1',r'Equate the expressions for $y$.'),('A1',r'$3x^2+(k-2)x+3=0$.'),('M1',r'Tangency gives $(k-2)^2-36=0$.'),('A1',r'$k-2=\pm6$.'),('A1',r'$k=8$ or $k=-4$.')])
add(77,'Distinct intersections depending on a parameter','Discriminants',r'$f(x)=x^2+kx$ and $g(x)=3x+3k$. Find all $k\in\mathbb R$ for which their graphs meet at two distinct points.',whole=[('M1',r'Equate $f(x)$ and $g(x)$.'),('A1',r'$x^2+(k-3)x-3k=0$.'),('M1',r'Require $(k-3)^2+12k>0$.'),('A1',r'$(k+3)^2>0$.'),('A1',r'$k\ne-3$.'),('R1',r'At $k=-3$ the equation is $(x-3)^2=0$, giving one point; every other real $k$ gives two.')])
add(78,'Quadratic transformation in expanded form','Quadratic functions',r'$f(x)=3x^2-12x+9$.',[
 P(r'State $f(0)$.',('A1',r'$9$.')),
 P(r'Solve $f(x)=0$.',('M1',r'$3(x^2-4x+3)=0$.'),('A1',r'$3(x-1)(x-3)=0$.'),('A1',r'$x=1$ or $x=3$.')),
 P(r'Write $f(x)=a(x-h)^2+k$.',('M1',r'Factor the first two terms: $f(x)=3(x^2-4x)+9$.'),('M1',r'Use $x^2-4x=(x-2)^2-4$, then combine constants: $-12+9=-3$.'),('A3',r'$f(x)=3(x-2)^2-3$, so $a=3,h=2,k=-3$ (one each).')),
 P(r'State the vertex and axis.',('A2',r'Vertex $(2,-3)$; axis $x=2$ (one each).')),
 P(r'Reflect in the $x$-axis, then move 2 units right and 4 up. Find $g(x)$ in expanded form.',('M1',r'$g(x)=-f(x-2)+4$.'),('A1',r'$g(x)=-3(x-4)^2+7$.'),('M1',r'Expand the square.'),('A1',r'$g(x)=-3x^2+24x-41$.'))])
add(79,'Inverse with a restricted domain','Composite and inverse functions',r'$f(x)=\dfrac{8+2x}{8-2x}$ for $-4\le x<4$. Find $f^{-1}$ and state its domain and range.',whole=[('M1',r'$y(8-2x)=8+2x$.'),('A1',r'$8y-8=2x(y+1)$.'),('A1',r'$f^{-1}(x)=\dfrac{4(x-1)}{x+1}$.'),('M1',r'$f(-4)=0$ and $f(x)\to\infty$ as $x\to4^-$; $f$ is increasing.'),('A1',r'Inverse domain $[0,\infty)$.'),('A1',r'Inverse range $[-4,4)$.')]);ck(79,4*(((8+2*x)/(8-2*x))-1)/(((8+2*x)/(8-2*x))+1),x)
add(80,'Squaring the ordinates of a graph','Transformations',r'The graph shows a smooth even function $f$. It decreases for $x>0$, has maximum $(0,3)$, roots $x=\pm3$, and horizontal asymptote $y=-3$. Sketch $y=[f(x)]^2-2$, labelling all local extrema and horizontal asymptotes.',whole=[('M1',r'Apply $y\mapsto y^2-2$ to the ordinates.'),('A1',r'Local maximum $(0,7)$.'),('A1',r'Local minima $(-3,-2)$ and $(3,-2)$.'),('A1',r'Horizontal asymptote $y=7$.'),('A1',r'Even graph, falling from the central maximum to each minimum, then increasing towards 7 from below on each outer side.')],diagram=graph([(lambda x:3*(9-x*x)/(9+x*x),B)],(-10,10),(-4,4),[(0,3,'(0,3)'),(-3,0,'(-3,0)'),(3,0,'(3,0)')],hl=[-3]),solution=graph([(lambda x:(3*(9-x*x)/(9+x*x))**2-2,R)],(-10,10),(-3,8),hl=[7]))

def normalize_primes(value):
 if isinstance(value,str):return re.sub(r'([A-Za-z])((?:\\prime)+)',lambda m:m[1]+'^{'+m[2]+'}',value)
 if isinstance(value,list):return [normalize_primes(v) for v in value]
 if isinstance(value,dict):return {k:normalize_primes(v) for k,v in value.items()}
 return value

def emit():
 for i,q in enumerate(OUT):
  OUT[i]=q=normalize_primes(q)
  n=q['number']
  if n in CHECKS and q['verification']['method']=='reasoned':q['verification']={'method':'symbolic/numerical','notes':'; '.join(CHECKS[n])+'. '+q['verification']['notes']}
  if n in (6,41):q['stem']=q['stem'].replace('\\n','\n')
  assert q['marks']==sum(p['marks'] for p in q['parts']) if q['parts'] else True
 tmp=ROOT/'functions.json.atomic'
 with open(tmp,'w') as f:json.dump(OUT,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
 os.replace(tmp,ROOT/'functions.json')
 print('Saved',len(OUT),'Functions questions')
emit()
k81=math.log2(14)/30;t81=math.log2(70)/k81
add(81,'Cooling model parameters','Exponential and logarithmic functions',r'A drink cools according to $T(t)=A2^{-kt}+B$, $k>0$, where $t$ is minutes. Initially $T=90^\circ\mathrm C$, and $T(1/k)=55^\circ\mathrm C$.',[
 P(r'Find $A$ and $B$.',('M1',r'$A+B=90$ and $A/2+B=55$; subtract to obtain $A/2=35$.'),('A1',r'$A=70$, $B=20$.')),
 P(r'After 30 minutes the temperature is $25^\circ\mathrm C$. Find $k$.',('M1',r'$5=70\cdot2^{-30k}\Rightarrow k=\log_2(14)/30$.'),('A1',fr'$k\approx{k81:#.3g}$ min$^{{-1}}$.')),
 P(r'Find when the temperature reaches $21^\circ\mathrm C$.',('M1',r'$1=70\cdot2^{-kt}\Rightarrow t=\log_2(70)/k$.'),('A1',fr'$t\approx{t81:#.3g}$ minutes.'))]);nc(81,70*2**(-k81*t81)+20,21)
r82=[(5-2*math.sqrt(10))/3,(5+2*math.sqrt(10))/3]
add(82,'A rational function and inverse intersections','Rational functions',r'$f(x)=\dfrac{4x+5}{3x-6}$, $x\ne2$.',[
 P(r'Find both axis intercepts.',('M1',r'Set the numerator to zero for the $x$-intercept.'),('A1',r'$(-5/4,0)$.'),('A1',r'The $y$-intercept is $(0,-5/6)$.')),
 P(r'Find both asymptotes.',('M1',r'Use the leading-coefficient ratio and denominator zero.'),('A2',r'$y=4/3$ and $x=2$ (one each).')),
 P(r'Sketch $f$.',('A1',r'Correct intercepts and asymptotes on the sketch.'),('A1',r'Use $f=4/3+13/[3(x-2)]$: left branch below $4/3$, right branch above.')),
 P(r'Find $f^{-1}(x)$.',('M1',r'$y(3x-6)=4x+5$.'),('A1',r'$x(3y-4)=6y+5$.'),('A1',r'$f^{-1}(x)=(6x+5)/(3x-4)$, $x\ne4/3$.')),
 P(r'Find the intersections of $f$ and $f^{-1}$ to two decimal places.',('M1',r'Equating the rational expressions gives $3x^2-10x-5=0$.'),('A1',r'$x=(5\pm2\sqrt{10})/3$ and $y=x$.'),('A1',fr'Points $({r82[0]:.2f},{r82[0]:.2f})$ and $({r82[1]:.2f},{r82[1]:.2f})$.')),
 P(r'Find the perpendicular bisector of the segment joining them.',('M1',r'The midpoint is $(5/3,5/3)$.'),('A1',r'The joining line has gradient 1, so the bisector has gradient $-1$.'),('A1',r'$y=-x+10/3$.'))],solution=graph([(lambda x:(4*x+5)/(3*x-6),R)],(-5,7),(-6,7),vl=[2],hl=[4/3]))
ck(82,sp.factor((4*x+5)*(3*x-4)-(6*x+5)*(3*x-6)),-2*(3*x*x-10*x-5))
h83=lambda z:math.sinh(z)-(z**4+4)/(2*z)
r83=brentq(h83,4,5)
add(83,'An odd function and a numerical inequality','Function sketching',r'Let $f(x)=\dfrac{e^x-e^{-x}}2$ and $g(x)=\dfrac{x^4+4}{2x}$, where $g$ is defined for $x\ne0$.',[
 P(r'Show that $f$ is odd.',('M1',r'$f(-x)=(e^{-x}-e^x)/2$.'),('A1',r'This equals $-f(x)$, so $f$ is odd.')),
 P(r'Use the graph of $f-g$ to solve $f(x)>g(x)$. Give boundary values to three significant figures.',('M1',r'Graph $H(x)=\sinh x-(x^4+4)/(2x)$ with $x\ne0$.'),('A1',fr'Its two zeros are $x\approx\pm{r83:#.3g}$.'),('A1',r'$H>0$ between the negative zero and 0, and above the positive zero.'),('A1',fr'$x\in(-{r83:#.3g},0)\cup({r83:#.3g},\infty)$.'))]);nc(83,h83(r83),0)
add(84,'Existence of exponential-equation solutions','Exponential and logarithmic functions',r'Find the range of $p$ for which $e^{2x}+2\ln p=6e^x$ has at least one real solution.',whole=[('R1',r'The logarithm requires $p>0$.'),('M1',r'Put $u=e^x>0$, giving $u^2-6u+2\ln p=0$.'),('A1',r'Real roots require $36-8\ln p\ge0$, so $\ln p\le9/2$.'),('R1',r'The root $u=3+\sqrt{9-2\ln p}$ is positive whenever this condition holds, so it yields a real $x$.'),('A1',r'$0<p\le e^{9/2}$.')])
add(85,'A tangent to a rational curve','Rational functions',r'$f(x)=\dfrac{1-ax}{4x-1}$. Its horizontal asymptote is $y=-1.5$.',[
 P(r'State the vertical asymptote.',('A1',r'$x=1/4$.')),
 P(r'Find $a$.',('M1',r'$-a/4=-1.5$.'),('A1',r'$a=6$.')),
 P(r'The line $y=x-c$, $c>0$, meets $f$ at exactly one point. Find the possible values of $c$.',('M1',r'Equating gives $4x^2+(5-4c)x+c-1=0$.'),('M1',r'Set the discriminant to zero: $(5-4c)^2-16(c-1)=0$.'),('A1',r'$16c^2-56c+41=0$.'),('A1',r'$c=(7\pm2\sqrt2)/4\approx1.04,\ 2.46$; both are positive and the tangent points are not $x=1/4$.'))])
add(86,'Intersections and a perpendicular bisector','Rational functions',r'$f(x)=\dfrac{12}{x+2}$, $x\ne-2$, and $g(x)=x-2$.',[
 P(r'Find any axis intercepts of $f$ and its vertical asymptote.',('R1',r'The numerator never vanishes, so there is no $x$-intercept.'),('M1',r'$f(0)=12/2$.'),('A1',r'The $y$-intercept is $(0,6)$.'),('M1',r'The denominator is zero at $x=-2$.'),('A1',r'Vertical asymptote $x=-2$.')),
 P(r'Find the intersection points $A,B$ of $f$ and $g$.',('M1',r'$12/(x+2)=x-2$.'),('A1',r'$x^2-4=12$.'),('M1',r'$x^2=16$ gives both signs.'),('A1',r'$x=-4,4$.'),('A1',r'$A=(-4,-6)$, $B=(4,2)$.')),
 P(r'Find their perpendicular bisector $L$.',('M1',r'The midpoint is $(0,-2)$.'),('A1',r'$AB$ has gradient 1, so $L$ has gradient $-1$.'),('A1',r'$L:y=-x-2$.')),
 P(r'Find the $x$-intercept of $L$.',('M1',r'$0=-x-2$.'),('A1',r'$(-2,0)$.'))])
add(87,'Quadratic sketch and scale factor','Quadratic functions',r'$f(x)=3(x-2)^2-27$.',[
 P(r'Expand $f(x)$.',('M1',r'$3(x^2-4x+4)-27$.'),('A1',r'$f(x)=3x^2-12x-15$.')),
 P(r'Find the vertex and all axis intercepts.',('A2',r'Vertex $(2,-27)$: one mark per coordinate.'),('M1',r'$f(0)=12-27$.'),('A1',r'$y$-intercept $(0,-15)$.'),('M1',r'$3(x-2)^2=27\Rightarrow x-2=\pm3$.'),('A2',r'$x$-intercepts $(-1,0)$ and $(5,0)$ (one each).')),
 P(r'Sketch the graph.',('A1',r'Upward-opening parabola.'),('A1',r'Correct vertex and symmetry about $x=2$.'),('A1',r'Correct axis intercepts labelled.')),
 P(r'The graph of $g(x)=9x^2$ is compressed vertically by factor $a$, moved $h$ units right and $k$ units up to give $f$. Find $a,h,k$.',('A3',r'$a=1/3$, $h=2$, $k=-27$ (one each).'))],solution=graph([(lambda x:3*(x-2)**2-27,R)],(-2,6),(-30,24)))
add(88,'A sequence of trigonometric transformations','Transformations',r'$f(x)=3\cos(x-\pi/3)+4$ and $g(x)=6\cos(x+\pi/3)+1$.',[
 P(r'Describe, in order, three transformations taking $f$ to $g$.',('A1',r'Translate $2\pi/3$ units left, obtaining $3\cos(x+\pi/3)+4$.'),('A1',r'Stretch vertically by factor 2, obtaining $6\cos(x+\pi/3)+8$.'),('A1',r'Translate 7 units down. Accept another explicitly correct sequence.')),
 P(r'$h(x)=g(x)+k$. Find the minimum $k$ such that $h(x)\ge0$ for all real $x$.',('M1',r'The minimum of $g$ is $1-6=-5$.'),('A1',r'$k_{\min}=5$.'))])
r89=brentq(lambda z:2*z*z*math.asin(z)-.8,0,1)
add(89,'Inverse trigonometric graph','Function sketching',r'$f(x)=2x^2\arcsin x$ for $-1\le x\le1$, using radians.',[
 P(r'Sketch $y=f(x)$.',('A1',r'The graph is odd and passes through $(0,0)$.'),('A1',r'Endpoints $(-1,-\pi)$ and $(1,\pi)$.'),('A1',r'Increasing throughout, with a horizontal tangent at the origin.')),
 P(r'State the range.',('M1',r'Use monotonicity and the endpoint values.'),('A1',r'$[-\pi,\pi]$.')),
 P(r'Solve $2x^2\arcsin x>0.8$, to three significant figures.',('M1',r'Solve $2x^2\arcsin x=0.8$ numerically on $[0,1]$.'),('A1',fr'The boundary is $x\approx{r89:#.3g}$.'),('A1',fr'${r89:#.3g}<x\le1$.'))],solution=graph([(lambda x:2*x*x*math.asin(x),R)],(-1,1),(-3.5,3.5)));nc(89,2*r89*r89*math.asin(r89),.8)
add(90,'Phase and vertical translations','Transformations',r'$f(x)=4\cos x+6$ and $g(x)=4\cos(x+\pi/3)+A$, where $A<6$.',[
 P(r'Describe two transformations mapping $f$ to $g$.',('A1',r'Translate $\pi/3$ units to the left.'),('M1',r'The vertical shift is $A-6$.'),('A1',r'Translate $6-A$ units down; these two translations can occur in either order.')),
 P(r'The $y$-intercept of $g$ is $(0,5)$. Find its range.',('M1',r'$5=4\cos(\pi/3)+A=2+A$.'),('A1',r'$A=3$.'),('M1',r'Apply $-1\le\cos\theta\le1$.'),('A1',r'Range $[-1,7]$.'))])
t91=math.log(.4)/math.log(.91)
add(91,'Continuous exponential decay','Exponential and logarithmic functions',r'A population follows $P(t)=P_0e^{kt}$, with $t$ in years. It is estimated that $P(1)/P_0=0.91$.',[
 P(r'Find $k$ and interpret the model.',('M1',r'$e^k=0.91$.'),('A1',r'$k=\ln0.91\approx-0.0943$ per year.'),('R1',r'The negative value represents decay; the model multiplies population by 0.91 each year, a 9% annual reduction.')),
 P(r'Find the least whole number of years for which $P(t)/P_0<0.40$.',('M1',r'$0.91^t<0.40$.'),('A1',r'$t\ln0.91<\ln0.40$.'),('M1',r'Divide by the negative $\ln0.91$, reversing the inequality.'),('A1',fr'$t>{t91:#.3g}$.'),('A1',fr'The least whole number is ${math.floor(t91)+1}$ years.'))])
t92=3*math.log(.1)/math.log(.4)
add(92,'An exponential clearance model','Exponential and logarithmic functions',r'For a mathematical model, an injected quantity is $D(t)=300e^{-kt}$ mg, $k>0$, with $t$ in hours. After 3 hours, 60% of the initial quantity has disappeared. A threshold is reached when 10% remains. The injection is at 08:00. Estimate the clock time the threshold is reached, to the nearest hour.',whole=[('M1',r'After 3 hours the remaining fraction is 0.40, so $e^{-3k}=0.40$.'),('A1',r'$k=-\ln0.40/3$.'),('M1',r'The threshold satisfies $e^{-kt}=0.10$.'),('A1',fr'$t=3\ln(0.10)/\ln(0.40)\approx{t92:#.3g}$ hours.'),('A1',r'This is approximately 15:32, giving 16:00 to the nearest hour.')])
add(93,'A rational function with an oblique asymptote','Rational functions',r'$f(x)=\dfrac{3x^2-12x+18}{x-2}$, $x\ne2$.',[
 P(r'State its vertical asymptote.',('A1',r'$x=2$.')),
 P(r'Find and classify its stationary points.',('M1',r'Write $f=3x-6+6/(x-2)$ and differentiate.'),('A1',r'$f\prime(x)=3-6/(x-2)^2$.'),('M1',r'Set the derivative to zero: $(x-2)^2=2$.'),('A1',r'$x=2\pm\sqrt2$.'),('A1',r'Coordinates $(2-\sqrt2,-6\sqrt2)$ and $(2+\sqrt2,6\sqrt2)$.'),('R1',r'$f\prime$ changes $+\to-$ at the first, a maximum, and $-\to+$ at the second, a minimum.')),
 P(r'Find the oblique asymptote.',('M1',r'Divide the numerator by $x-2$.'),('A1',r'$f(x)=3x-6+6/(x-2)$.'),('M1',r'The remainder term tends to zero as $|x|\to\infty$.'),('A1',r'The oblique asymptote is $y=3x-6$.')),
 P(r'Sketch $f$, labelling the asymptotes, intercepts and stationary points.',('A1',r'$y$-intercept $(0,-9)$.'),('R1',r'No $x$-intercepts: $3[(x-2)^2+2]>0$.'),('A1',r'Both asymptotes correctly labelled.'),('A1',r'Both stationary points correctly placed.'),('A1',r'Left branch is below the oblique asymptote, tends to $-\infty$ at $2^-$.'),('A1',r'Right branch is above the oblique asymptote, tends to $+\infty$ at $2^+$.'))],solution=graph([(lambda x:3*x-6+6/(x-2),R),(lambda x:3*x-6,'#888')],(-4,8),(-24,24),vl=[2]),note='The source header says 17 marks but its visible parts sum to 16. The rebuilt sketch allocation is 6, so the complete scheme consistently totals 17.')
ck(93,(3*x*x-12*x+18)/(x-2),3*x-6+6/(x-2))
add(94,'Coefficients from prescribed factors','Polynomials',r'$p(x)=3x^4+a_3x^3+a_2x^2+a_1x-36$ is divisible by $x+2$, $x-1$ and $x-3$. Find $a_1,a_2,a_3$.',whole=[('M1',r'Write $p(x)=3(x+2)(x-1)(x-3)(x-r)$.'),('A1',r'The constant is $3(2)(-1)(-3)(-r)=-18r=-36$, hence $r=2$.'),('M1',r'Expand $3(x+2)(x-1)(x-2)(x-3)$.'),('A2',r'$p(x)=3x^4-12x^3-3x^2+48x-36$, so $a_1=48,a_2=-3,a_3=-12$.')]);ck(94,3*(x+2)*(x-1)*(x-2)*(x-3),3*x**4-12*x**3-3*x*x+48*x-36)
add(95,'Largest coefficient from a remainder','Polynomials',r'When $p(x)=x^2-4x+c$ is divided by $x-r$, the remainder is 7. Find the largest possible real $c$.',whole=[('M1',r'The remainder theorem gives $r^2-4r+c=7$.'),('A1',r'$c=7-r^2+4r$.'),('M1',r'Complete the square: $c=11-(r-2)^2$.'),('R1',r'The square is non-negative, with equality at $r=2$.'),('A1',r'$c_{\max}=11$.')])
add(96,'Change of logarithm base','Exponential and logarithmic functions',r'All logarithms must have valid real bases and arguments.',[
 P(r'State the domain and range of $y=\log_a x$, for $a>0$, $a\ne1$.',('A2',r'Domain $(0,\infty)$; range $\mathbb R$ (one each).')),
 P(r'For $x>0$, $x\ne1$, solve $\log_{x^2}y=4\log_y(x^2)$ for $y$ in terms of $x$.',('M1',r'Let $u=\log_{x^2}y$.'),('A1',r'Change of base gives $\log_y(x^2)=1/u$.'),('M1',r'$u=4/u\Rightarrow u^2=4$.'),('A1',r'$u=2$ or $u=-2$.'),('A1',r'$y=(x^2)^2=x^4$ or $y=(x^2)^{-2}=x^{-4}$.'),('R1',r'For the stated $x$, both outputs are positive and unequal to 1, so all logarithms are defined.'))])
add(97,'Rational sketch with two poles','Rational functions',r'$f(x)=x^2-6x+5$ and $g(x)=\dfrac{x-3}{f(x)}$.',[
 P(r'Find $g(2)$.',('M1',r'$g(2)=(2-3)/(4-12+5)$.'),('A1',r'$g(2)=1/3$.')),
 P(r'Find the vertical asymptotes.',('M1',r'$f(x)=(x-1)(x-5)$ with no cancellation.'),('A1',r'$x=1$ and $x=5$.')),
 P(r'Find the axis intercepts.',('A2',r'$(3,0)$ and $(0,-3/5)$ (one each).')),
 P(r'State the horizontal asymptote.',('A1',r'$y=0$.')),
 P(r'Sketch $g$, labelling these features.',('A1',r'Left branch below the axis, from $0^-$ to $-\infty$ at $1^-$.'),('A1',r'Middle branch decreases from $+\infty$ to $-\infty$, crossing at $(3,0)$.'),('A1',r'Right branch decreases from $+\infty$ at $5^+$ towards $0^+$; asymptotes/intercepts labelled.'))],solution=graph([(lambda x:(x-3)/((x-1)*(x-5)),R)],(-3,9),(-4,4),vl=[1,5],hl=[0]))
add(98,'Area enclosed by two modulus graphs','Modulus functions',r'Consider $y=-|x|$ and $y=3|x|-a$, with $a>0$.',[
 P(r'Sketch the two graphs on the same axes.',('A1',r'Downward V with vertex $(0,0)$ and slopes $\pm1$.'),('A1',r'Upward V with vertex $(0,-a)$ and slopes $\pm3$.')),
 P(r'The enclosed region has area 36 square units. Find $a$.',('M1',r'At intersections $4|x|=a$, so the horizontal diagonal is $a/2$; the vertical diagonal is $a$.'),('A1',r'Area $=\tfrac12(a/2)a=a^2/4=36$.'),('A1',r'$a=12$, since $a>0$.'))])
add(99,'Geometrically spaced polynomial roots','Polynomials',r'A monic polynomial has the form $p(x)=x^5-22x^4+\cdots-32768$. Its five real roots form a geometric sequence with first term $u>0$ and common ratio $r<-1$.',[
 P(r'Obtain two expressions for $u$ in terms of $r$.',('M1',r'By Vieta, $u(1+r+r^2+r^3+r^4)=22$.'),('A1',r'$u=22/(1+r+r^2+r^3+r^4)$.'),('A1',r'The product is $u^5r^{10}=32768=8^5$, hence $u=8/r^2$.')),
 P(r'Hence find $u$ and $r$.',('M1',r'Equate the expressions and solve $4r^4+4r^3-7r^2+4r+4=0$ in $r<-1$.'),('A1',r'$r=-2$ and $u=2$. For uniqueness, divide by $r^2$ and set $s=r+1/r<-2$: $4s^2+4s-15=0$ forces $s=-5/2$, then $r=-2$.'))]);ck(99,sum(sp.Integer(2)*(-2)**j for j in range(5)),22);ck(99,sp.prod(sp.Integer(2)*(-2)**j for j in range(5)),32768)
add(100,'A second squared-ordinate sketch','Transformations',r'The diagram shows a smooth even function $f$, decreasing for $x>0$, with maximum $(0,2)$, roots $x=\pm2$ and horizontal asymptote $y=-2$. Sketch $y=[f(x)]^2-3$, labelling every local extremum and horizontal asymptote.',whole=[('M1',r'Apply $y\mapsto y^2-3$.'),('A1',r'The central local maximum is $(0,1)$.'),('A1',r'The local minima are $(-2,-3)$ and $(2,-3)$.'),('A1',r'The horizontal asymptote is $y=1$.'),('A1',r'An even curve decreases from the central maximum to each minimum, then rises towards 1 from below on the outer branches.')],diagram=graph([(lambda x:2*(4-x*x)/(4+x*x),B)],(-8,8),(-3,3),[(0,2,'(0,2)'),(-2,0,'(-2,0)'),(2,0,'(2,0)')],hl=[-2]),solution=graph([(lambda x:(2*(4-x*x)/(4+x*x))**2-3,R)],(-8,8),(-4,2),hl=[1]))
emit()
add(101,'Polynomial roots in arithmetic progression','Polynomials',r'Consider $2x^3-15x^2+37x-30=0$.',[
 P(r'State the sum and product of its roots.',('A1',r'Sum $15/2$ and product $15$; both required.')),
 P(r'The roots are consecutive terms $a-d,a,a+d$ of an arithmetic sequence. Find them.',('M1',r'$3a=15/2$.'),('A1',r'$a=5/2$.'),('M1',r'The product gives $a(a^2-d^2)=15$.'),('A1',r'$(5/2)(25/4-d^2)=15\Rightarrow d^2=1/4$.'),('M1',r'Take $d=1/2$; the negative value reverses the ordering only.'),('A1',r'The roots are $2,5/2,3$.'))]);ck(101,2*(x-2)*(x-sp.Rational(5,2))*(x-3),2*x**3-15*x*x+37*x-30)
p102=x**5+3*x**4-x**3+2*x*x+36*x+40
add(102,'A repeated factor and complex roots','Polynomials',r'$p(z)=z^5+3z^4-z^3+2z^2+36z+40$, where $z\in\mathbb C$.',[
 P(r'State the sum and product of the roots.',('A2',r'Sum $-3$; product $-40$ (one each).')),
 P(r'Show that $z+2$ is a factor.',('M1',r'$p(-2)=-32+48+8+8-72+40=0$.'),('R1',r'The factor theorem gives the factor $z+2$.')),
 P(r'Given $p(z)=(z+2)^3(z^2+cz+d)$, find $c,d$.',('M1',r'Compare coefficients after expanding $(z+2)^3=z^3+6z^2+12z+8$.'),('A1',r'The $z^4$ coefficient gives $c+6=3$.'),('A1',r'$c=-3$.'),('M1',r'The constant term gives $8d=40$.'),('A1',r'$d=5$; multiplication verifies every coefficient.')),
 P(r'Hence find all roots, including multiplicities.',('A1',r'$z=-2$ is a triple root.'),('M1',r'$z^2-3z+5=0\Rightarrow z=(3\pm\sqrt{-11})/2$.'),('A1',r'The other roots are $(3\pm i\sqrt{11})/2$.'))]);ck(102,(x+2)**3*(x*x-3*x+5),p102)
add(103,'Complex roots and real coefficients','Polynomials',r'Two roots of $z^4-14z^3+cz^2+dz+377=0$ are $a+2i$ and $2+bi$, where $a,b,c,d$ are integers and $b>0$.',[
 P(r'State the other two roots.',('A2',r'$a-2i$ and $2-bi$ by the conjugate-root theorem (one each).')),
 P(r'Find $a,b$.',('M1',r'The sum of the four roots is $2a+4=14$.'),('A1',r'$a=5$.'),('M1',r'The product is $(a^2+4)(4+b^2)=377$.'),('A1',r'$29(4+b^2)=377\Rightarrow b^2=9$.'),('M1',r'Take the positive square root because $b>0$.'),('A1',r'$b=3$.'))]);ck(103,(25+4)*(4+9),377)
add(104,'Minimum coefficient from a remainder','Polynomials',r'When $p(x)=x^2-6x-c$ is divided by $x-r$, the remainder is $-7$. Find the smallest possible real $c$.',whole=[('M1',r'Apply the remainder theorem: $r^2-6r-c=-7$.'),('A1',r'$c=r^2-6r+7$.'),('M1',r'$c=(r-3)^2-2$.'),('R1',r'The square is at least zero, with equality when $r=3$.'),('A1',r'$c_{\min}=-2$.')])
add(105,'Maxima form an arithmetic sequence','Function sketching',r'$f(x)=e^{2\sin(\pi x/3)}$ for $x>0$. The $k$th maximum has abscissa $x_k$, in increasing order.',[
 P(r'Given $x_{k+1}=x_k+d$, find $d$.',('M1',r'The exponential increases with its exponent, so maxima occur when $\sin(\pi x/3)=1$.'),('A1',r'$\pi x/3=\pi/2+2j\pi$.'),('A1',r'$x_k=3/2+6(k-1)$ for $k\ge1$.'),('A1',r'$d=6$.')),
 P(r'Find $n$ such that $\sum_{k=1}^n x_k=1170$.',('M1',r'Use the arithmetic-series formula: $S_n=n[3+6(n-1)]/2$.'),('A1',r'$3n^2-\tfrac32n=1170\Rightarrow2n^2-n-780=0$.'),('M1',r'$(n-20)(2n+39)=0$.'),('A1',r'$n=20$; the other solution is negative.'))]);ck(105,sum(sp.Rational(3,2)+6*j for j in range(20)),1170)
add(106,'Five transformations of a cosine graph','Transformations',r'$g(x)=-3x-\pi/2$ and $h(x)=4\cos x+2$.',[
 P(r'Find $(h\circ g)(x)$.',('A1',r'$(h\circ g)(x)=4\cos(-3x-\pi/2)+2$.')),
 P(r'Find its range.',('M1',r'$-1\le\cos\theta\le1$.'),('A1',r'Range $[-2,6]$.')),
 P(r'Given $(h\circ g)(\pi/2)=6$, find the next greater input giving 6.',('M1',r'The period is $2\pi/3$.'),('A1',r'$x=\pi/2+2\pi/3=7\pi/6$.')),
 P(r'Describe an ordered sequence of five transformations from $y=\cos x$ to this graph.',('A1',r'Reflect in the $y$-axis, giving $\cos(-x)$.'),('A1',r'Compress horizontally by factor $1/3$, giving $\cos(-3x)$.'),('A1',r'Translate $\pi/6$ units left, giving $\cos[-3(x+\pi/6)]$.'),('A1',r'Stretch vertically by factor 4.'),('A1',r'Translate 2 units up.'))])
add(107,'A cubic recovered from its graph','Polynomials',r'The graph shows $f(x)=ax^3+bx^2+cx+d$. Find $a,b,c,d$.',whole=[('M1',r'The roots imply $f(x)=a(x+2)(x-1)(x-3)$.'),('A1',r'All three factors correctly identified.'),('M1',r'The $y$-intercept gives $12=a(2)(-1)(-3)=6a$.'),('A1',r'$a=2$.'),('M1',r'Expand: $(x+2)(x-1)(x-3)=x^3-2x^2-5x+6$.'),('A1',r'$b=-4$.'),('A1',r'$c=-10$, $d=12$; both required.')],diagram=graph([(lambda x:2*(x+2)*(x-1)*(x-3),B)],(-3,4),(-18,22),[(-2,0,'(-2,0)'),(1,0,'(1,0)'),(3,0,'(3,0)'),(0,12,'(0,12)')]),note='Reference print omits the cubic graph and the final task parts. Reconstructed a labelled roots/intercept graph to determine the stated four coefficients on its 7-mark scale.')
ck(107,2*(x+2)*(x-1)*(x-3),2*x**3-4*x*x-10*x+12)
add(108,'Quadratic parameters and a universal intersection proof','Quadratic functions',r'A quadratic $f$ has vertex $(2,8)$ and an $x$-intercept at $x=-2$.',[
 P(r'Find $f$ in vertex form.',('M1',r'$f(x)=a(x-2)^2+8$.'),('A1',r'$0=16a+8\Rightarrow a=-1/2$.'),('A1',r'$f(x)=-\tfrac12(x-2)^2+8$.')),
 P(r'Let $g(x)=mx^2-2nx+2n^2/m$, with $m>0$. Given $g(-1)=g(3)=6$, find $m,n$ and the range of $g$.',('M1',r'Equal values at $-1,3$ give axis $x=1$.'),('A1',r'The axis is $x=n/m$, hence $n=m$.'),('M1',r'$g(-1)=m+2m+2m=5m=6$.'),('A1',r'$m=6/5$.'),('A1',r'$n=6/5$.'),('M1',r'$g(x)=m(x-n/m)^2+n^2/m$ has minimum $n^2/m=6/5$.'),('A1',r'Range $[6/5,\infty)$.')),
 P(r'Without the conditions in (b), let $h(x)=nx+2$. Prove $g$ and $h$ meet twice for every $m>0$ and real $n$.',('M1',r'Equate the functions.'),('A1',r'$mx^2-3nx+2n^2/m-2=0$.'),('M1',r'The discriminant is $(-3n)^2-4m(2n^2/m-2)$.'),('A1',r'$\Delta=n^2+8m$.'),('R1',r'$n^2\ge0$ and $8m>0$, so $\Delta>0$.'),('R1',r'The leading coefficient is nonzero and the discriminant positive, proving two distinct real intersections.'))])
add(109,'Restricting a logarithmic function for inversion','Exponential and logarithmic functions',r'$f(x)=-\tfrac12\ln(x^2-9)$.',[
 P(r'Find its largest real domain.',('M1',r'The argument must be positive: $x^2-9>0$.'),('A1',r'$D=(-\infty,-3)\cup(3,\infty)$.')),
 P(r'Sketch the graph, showing asymptotes and intercepts.',('A1',r'Vertical asymptotes $x=\pm3$; the graph tends to $+\infty$ on the allowed side of each.'),('A1',r'$x$-intercepts $(\pm\sqrt{10},0)$; there is no $y$-intercept.'),('A1',r'Even branches tend to $-\infty$ as $|x|\to\infty$.')),
 P(r'Explain why $f$ is even.',('R1',r'$f(-x)=-\tfrac12\ln((-x)^2-9)=f(x)$, and its domain is symmetric.')),
 P(r'Explain why $f$ has no inverse function on $D$.',('R1',r'It is not one-to-one: each $x>3$ and $-x$ have the same output.')),
 P(r'Let $g$ be the restriction to $(3,\infty)$. Find $g^{-1}$ and its domain.',('M1',r'$y=-\tfrac12\ln(x^2-9)\Rightarrow e^{-2y}=x^2-9$.'),('A1',r'$x=\sqrt{9+e^{-2y}}$, choosing the positive root because $x>3$.'),('A1',r'$g^{-1}(x)=\sqrt{9+e^{-2x}}$.'),('A1',r'The inverse domain is $\mathbb R$.'))],solution=graph([(lambda x:-.5*math.log(x*x-9) if abs(x)>3 else math.nan,R)],(-8,8),(-3,4),vl=[-3,3]))
add(110,'A quadratic determined by its axis','Quadratic functions',r'$f(x)=p(x-2)(x-q)$ has axis of symmetry $x=3$ and $y$-intercept $(0,-8)$.',[
 P(r'Find $q$.',('M1',r'The symmetry axis is the midpoint of the roots.'),('A1',r'$(2+q)/2=3$.'),('A1',r'$q=4$.')),
 P(r'Find $p$.',('M1',r'$f(0)=p(-2)(-4)=-8$.'),('A1',r'$8p=-8$.'),('A1',r'$p=-1$.')),
 P(r'The line $y=kx+5$ is tangent to $f$. Find all possible $k$.',('M1',r'Equate $-x^2+6x-8=kx+5$.'),('A1',r'$x^2+(k-6)x+13=0$.'),('M1',r'Tangency requires a repeated root.'),('A1',r'$(k-6)^2-52=0$.'),('A1',r'$(k-6)^2=52$.'),('M1',r'Take both square roots.'),('A2',r'$k=6+2\sqrt{13}$ or $k=6-2\sqrt{13}$ (one each).'))])
f111=x**4-x**3-7*x*x+x+6
crit111=sorted(float(sp.re(z)) for z in sp.nroots(sp.diff(f111,x)))
a111,b111=crit111[:2];ya111=float(f111.subs(x,a111));yb111=float(f111.subs(x,b111))
f111num=sp.lambdify(x,f111,'numpy');grid111=np.linspace(a111,b111,600);vals111=f111num(grid111)
add(111,'Quartic inequality and an inverse restriction','Polynomials',r'$f(x)=x^4-x^3-7x^2+x+6$.',[
 P(r'Solve $f(x)<0$.',('M1',r'Factorise or use a graph: $f=(x+2)(x+1)(x-1)(x-3)$.'),('A1',r'The simple roots are $-2,-1,1,3$ and the leading coefficient is positive.'),('A1',r'$x\in(-2,-1)\cup(1,3)$.')),
 P(r'Find the local maximum, to three significant figures.',('M1',r'Solve $f\prime(x)=4x^3-3x^2-14x+1=0$.'),('A1',fr'The middle stationary input is ${b111:#.3g}$, with second derivative negative.'),('A1',fr'The maximum is $({b111:#.3g},{yb111:#.3g})$.')),
 P(r'Restrict $f$ to $[a,b]$, with $a<0<b$, so it has an inverse. Find the smallest possible $a$ and largest possible $b$. Sketch this restriction and its inverse with endpoint coordinates. Solve $f^{-1}(x)=-1$.',('A2',fr'$a\approx{a111:#.3g}$ and $b\approx{b111:#.3g}$, the left local minimum and the local maximum (one each).'),('M1',r'Use the increasing branch and reflect it in $y=x$.'),('A1',fr'Branch endpoints $({a111:#.3g},{ya111:#.3g})$, $({b111:#.3g},{yb111:#.3g})$; inverse endpoints have coordinates swapped.'),('M1',r'$f^{-1}(x)=-1\Rightarrow x=f(-1)$.'),('A1',r'$x=0$.'))],solution=graph([(lambda z:float(f111num(z)) if a111<=z<=b111 else math.nan,B),(lambda z:float(np.interp(z,vals111,grid111)) if ya111<=z<=yb111 else math.nan,R)],(-3,7),(-3,7)))
ck(111,f111,(x+2)*(x+1)*(x-1)*(x-3))
add(112,'A logarithmic sequence becomes a quadratic','Quadratic models',r'An arithmetic sequence has $u_5=-\ln3$ and $u_7=3\ln3$. Let $S_n$ be the sum of its first $n$ terms.',[
 P(r'Find the common difference and $u_1$, and show $S_n=(n^2-10n)\ln3$.',('R1',r'$2d=u_7-u_5=4\ln3$, hence $d=2\ln3$.'),('M1',r'$u_5=u_1+4d$.'),('A1',r'$u_1=-9\ln3$.'),('M1',r'$S_n=\frac n2[2(-9\ln3)+(n-1)2\ln3]$.'),('A1',r'This simplifies to $(n^2-10n)\ln3$.')),
 P(r'Let $f(x)=(x^2-10x)\ln3$. State its axis, sketch its graph and find the minimum value of $S_n$ for positive integers $n$.',('A1',r'The symmetry axis is $x=5$.'),('A1',r'Upward-opening parabola with intercepts $(0,0),(10,0)$.'),('A1',r'Vertex $(5,-25\ln3)$.'),('M1',r'The vertex input is the allowed integer $n=5$.'),('A1',r'The minimum is $-25\ln3$.')),
 P(r'Let $g(x)=(8-4x)\ln3$. Solve $f(x)=g(x)$ and $f(x)<g(x)$, then state the positive integers $n$ with $S_n<g(n)$.',('M1',r'Cancel $\ln3>0$: $x^2-10x=8-4x$.'),('A1',r'$x^2-6x-8=0\Rightarrow x=3\pm\sqrt{17}$.'),('M1',r'The monic quadratic is negative strictly between its roots.'),('A1',r'$3-\sqrt{17}<x<3+\sqrt{17}$.'),('A1',r'$n\in\{1,2,3,4,5,6,7\}$.'))])
f113=lambda z:2*z if z<=1 else 4-2*z if z<=3 else 2*z-8
add(113,'Odd extension, square and reciprocal','Transformations',r'The diagram shows $f$ on $0\le x\le4$; its segments are straight. The odd function $h$ is defined on $[-4,4]$ with $h(x)=3f(x)$ for $x\ge0$.',[
 P(r'Sketch $h$.',('A1',r'On the positive half, join $(0,0),(1,6),(3,-6),(4,0)$ by straight segments.'),('A1',r'Use origin symmetry: also join $(-4,0),(-3,6),(-1,-6),(0,0)$.')),
 P(r'Sketch $y=[f(x)]^2$ on $[0,4]$.',('A1',r'Zeros are at $x=0,2,4$; the graph is non-negative.'),('A1',r'Local maxima at $(1,4)$ and $(3,4)$.'),('A1',r'Join with quadratic arcs: $4x^2$, $(4-2x)^2$, $(2x-8)^2$ on the three original segments.')),
 P(r'Sketch $y=1/f(x)$ on its domain.',('A1',r'Vertical asymptotes at $x=0,2,4$; these inputs are excluded.'),('A1',r'Positive branch on $(0,2)$, with minimum $(1,1/2)$ and $+\infty$ at both ends.'),('A1',r'Negative branch on $(2,4)$, with maximum $(3,-1/2)$ and $-\infty$ at both ends.'))],diagram=graph([(f113,B)],(0,4),(-3,3),[(0,0,'(0,0)'),(1,2,'(1,2)'),(3,-2,'(3,-2)'),(4,0,'(4,0)')]))
add(114,'Logarithmic apparent magnitude','Exponential and logarithmic functions',r'Apparent magnitude is modelled by $M=-2.5\log_{10}(F/F_0)$, where $F,F_0>0$.',[
 P(r'Express $F$ in terms of $M$.',('M1',r'$\log_{10}(F/F_0)=-M/2.5$.'),('A1',r'$F=F_0\,10^{-0.4M}$.')),
 P(r'Two stars have magnitudes 2 and 7, with fluxes $F_2,F_7$. Find $F_2/F_7$.',('A1',r'$F_2/F_7=10^{-0.4(2-7)}=100$.')),
 P(r'Derive $M_2-M_1$ in terms of $F_1,F_2$.',('M1',r'Subtract the two logarithmic expressions and combine logarithms.'),('A1',r'$M_2-M_1=-2.5\log_{10}(F_2/F_1)$.')),
 P(r'Two objects have magnitudes $-24.5$ and $-11.0$. Write their flux ratio (brighter over dimmer) as $10^{a/b}$, where $a,b$ are coprime positive integers.',('M1',r'The exponent is $-0.4[-24.5-(-11.0)]=5.4=27/5$.'),('A1',r'$a=27$, $b=5$.'))])
add(115,'Horizontal-line intersections','Rational functions',r'$f(x)=\dfrac{7-10x}{cx-18}$, where $c\ne0$. The vertical asymptote is $x=3$.',[
 P(r'Find $c$ and the horizontal asymptote.',('M1',r'$3c-18=0$.'),('A1',r'$c=6$.'),('M1',r'The leading-coefficient ratio is $-10/6$.'),('A1',r'Horizontal asymptote $y=-5/3$.')),
 P(r'Find the real $h$ for which $y=h$ meets the curve exactly once.',('M1',r'$h(6x-18)=7-10x\Rightarrow(6h+10)x=18h+7$.'),('A1',r'For $h\ne-5/3$, the unique solution is $x=(18h+7)/(6h+10)$, never 3.'),('R1',r'At $h=-5/3$ the equation reduces to $0=-23$, impossible. Thus all $h\in\mathbb R\setminus\{-5/3\}$.'))])
add(116,'Largest domain allowing an inverse','Composite and inverse functions',r'$f(x)=\sin(2x+c)$ is defined for $0\le x\le a$.',[
 P(r'Find the largest $a$ for which an inverse exists when $c=\pi/2$.',('M1',r'Starting at phase $\pi/2$, sine decreases until phase $3\pi/2$; beyond this it repeats outputs.'),('A1',r'$2a+\pi/2=3\pi/2\Rightarrow a=\pi/2$.')),
 P(r'Find the largest $a$ when $c=\pi$.',('A1',r'$2a+\pi=3\pi/2\Rightarrow a=\pi/4$.')),
 P(r'Find the largest $a$ for $\pi/2<c<\pi$.',('R1',r'The initial decreasing branch ends at the first minimum, phase $3\pi/2$.'),('A1',r'$a=3\pi/4-c/2$.'))])
f117=x**4-2*x**3-13*x*x+14*x+24
lo117=(1-math.sqrt(29))/2;hi117=(1+math.sqrt(29))/2
add(117,'A quartic with a quadratic factor','Polynomials',r'$f(x)=x^4-2x^3+ax^2+bx+24$. The polynomial $x^2-x-2$ is a factor.',[
 P(r'Find $a,b$.',('M1',r'The factor has roots $-1,2$, so $f(-1)=f(2)=0$.'),('A1',r'$a-b=-27$ and $4a+2b=-24$.'),('M1',r'Solve the simultaneous equations.'),('A1',r'$a=-13$, $b=14$.')),
 P(r'Factorise $f$ completely.',('M1',r'Divide by $x^2-x-2$.'),('A1',r'The quotient is $x^2-x-12$.'),('M1',r'Factor both quadratics.'),('A1',r'$f(x)=(x+3)(x+1)(x-2)(x-4)$.')),
 P(r'Sketch $f$, labelling intercepts and stationary points.',('A1',r'Roots $-3,-1,2,4$ and $y$-intercept 24; both outer arms rise.'),('A1',fr'Local minima $({lo117:#.3g},-25)$ and $({hi117:#.3g},-25)$.'),('A1',r'Local maximum $(1/2,441/16)\approx(0.500,27.6)$.')),
 P(r'Find all $c$ for which $f(x)=c$ has four distinct real roots.',('M1',r'The horizontal line must lie above both equal minima and below the local maximum.'),('A1',r'$-25<c<441/16$.'))],solution=graph([(lambda z:z**4-2*z**3-13*z*z+14*z+24,R)],(-4,5),(-30,35)))
ck(117,f117,(x+3)*(x+1)*(x-2)*(x-4));ck(117,f117.subs(x,sp.Rational(1,2)),sp.Rational(441,16))
add(118,'A rational-modulus equation','Modulus functions',r'Consider $y=-\dfrac6{x-3}$ and $y=-x-3$.',[
 P(r'Sketch both on the same axes, labelling intercepts and asymptotes.',('A1',r'The rational curve has asymptotes $x=3,y=0$, $y$-intercept $(0,2)$ and no $x$-intercept.'),('A1',r'The line passes through $(-3,0)$ and $(0,-3)$.'),('A1',r'Correct hyperbola branches: positive left of 3, negative right of 3, and the decreasing line.')),
 P(r'Find the exact solutions of $x+3=6/|x-3|$.',('M1',r'The right side is positive, so $x>-3$ and $x\ne3$. Split at 3.'),('M1',r'For $x>3$, $(x+3)(x-3)=6\Rightarrow x^2=15$.'),('A1',r'Only $x=\sqrt{15}$ satisfies this case.'),('M1',r'For $-3<x<3$, $(x+3)(3-x)=6\Rightarrow x^2=3$.'),('A1',r'$x=\pm\sqrt3$ are both valid. The full set is $\{-\sqrt3,\sqrt3,\sqrt{15}\}$.'))],solution=graph([(lambda z:-6/(z-3),R),(lambda z:-z-3,B)],(-6,7),(-8,8),vl=[3],hl=[0]))
f119=x**5/2-sp.Rational(3,2)*x**4-sp.Rational(17,2)*x**3+sp.Rational(27,2)*x*x+26*x-30
add(119,'Roots after an input transformation','Polynomials',r'$p(x)=\tfrac12x^5-\tfrac32x^4-\tfrac{17}2x^3+\tfrac{27}2x^2+26x-30$. Define $q(x)=p(2x-1)$.',[
 P(r'Find the sum and product of the roots of $p(x)=0$.',('M1',r'Use Vieta for a degree-five polynomial.'),('A1',r'Sum $=-(-3/2)/(1/2)=3$.'),('A1',r'Product $=-(-30)/(1/2)=60$.')),
 P(r'Find the sum and product of the roots of $q(x)=0$.',('M1',r'If $r_i$ is a root of $p$, the corresponding root of $q$ is $(r_i+1)/2$.'),('A1',r'Sum $=(3+5)/2=4$.'),('M1',r'The leading coefficient of $q$ is $(1/2)2^5=16$.'),('M1',r'The constant is $q(0)=p(-1)=-36$.'),('A1',r'Product $=-(-36)/16=9/4$.'))]);ck(119,f119,sp.Rational(1,2)*(x+3)*(x+2)*(x-1)*(x-2)*(x-5));ck(119,f119.subs(x,-1),-36)
add(120,'Inverse and two modulus inequalities','Rational functions',r'$f(x)=1+\dfrac{4x}{x+2}$, $x\ne-2$.',[
 P(r'Sketch $f$, labelling intercepts and asymptotes.',('A1',r'$f=(5x+2)/(x+2)=5-8/(x+2)$.'),('A1',r'Intercepts $(-2/5,0)$ and $(0,1)$.'),('A1',r'Asymptotes $x=-2$, $y=5$.'),('A1',r'Left branch above 5; right branch below 5, increasing on both domain intervals.')),
 P(r'Find $f^{-1}(x)$.',('M1',r'$y(x+2)=5x+2$.'),('A1',r'$x(y-5)=2-2y$.'),('M1',r'Solve for the input and exchange variables.'),('A1',r'$f^{-1}(x)=(2-2x)/(x-5)$, $x\ne5$.')),
 P(r'Solve $f(x)=f^{-1}(x)$.',('M1',r'Equate the fractions and cross-multiply on $x\ne-2,5$.'),('A1',r'$7(x^2-3x-2)=0$.'),('A1',r'$x=(3\pm\sqrt{17})/2$, both valid.')),
 P(r'Solve $|f(x)|<2$.',('M1',r'Solve the bounds $f(x)=-2$ and $f(x)=2$.'),('A1',r'They occur at $x=-6/7$ and $x=2/3$.'),('R1',r'The left branch $x<-2$ has $f>5$; the right branch is strictly increasing.'),('A1',r'$-6/7<x<2/3$.')),
 P(r'Solve $f(|x|)<2$.',('M1',r'As $|x|+2>0$, $(5|x|+2)/(|x|+2)<2\Rightarrow3|x|<2$.'),('A1',r'$-2/3<x<2/3$.'))],solution=graph([(lambda z:5-8/(z+2),R)],(-8,6),(-8,12),vl=[-2],hl=[5]))
ck(120,(5*x+2)*(x-5)-(2-2*x)*(x+2),7*x*x-21*x-14)
add(121,'Two negative roots','Discriminants',r'$p(x)=3kx^2+12kx+2k+5$, with real $k$.',[
 P(r'For $k\ne0$, express the product of the roots in terms of $k$.',('A1',r'$(2k+5)/(3k)$.')),
 P(r'Find the values of $k$ for which there are two distinct negative real roots.',('M1',r'The sum is $-12k/(3k)=-4<0$ for $k\ne0$.'),('M1',r'The product must be positive: $(2k+5)/k>0$.'),('A1',r'This gives $k<-5/2$ or $k>0$.'),('M1',r'The discriminant must be positive: $60k(2k-1)>0$, hence $k<0$ or $k>1/2$.'),('A1',r'Combining conditions: $k<-5/2$ or $k>1/2$.'))])
emit()
svg122='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 360" role="img" aria-label="Increasing curve with horizontal asymptotes y equals 5 and y equals minus 3"><rect width="620" height="360" fill="white"/><line x1="40" y1="210" x2="585" y2="210" stroke="#222"/><line x1="280" y1="20" x2="280" y2="330" stroke="#222"/><line x1="40" y1="50" x2="580" y2="50" stroke="#888" stroke-dasharray="6 4"/><line x1="40" y1="305" x2="580" y2="305" stroke="#888" stroke-dasharray="6 4"/><path d="M40 302 C160 302 230 290 280 260 C310 240 320 225 335 210 C380 90 430 52 580 51" fill="none" stroke="#253c66" stroke-width="3"/><text x="585" y="202" font-size="15">x</text><text x="290" y="23" font-size="15">y</text><text x="42" y="43" font-size="15">y = 5</text><text x="42" y="325" font-size="15">y = −3</text><text x="335" y="231" font-size="15">a</text><text x="248" y="266" font-size="15">−b</text><text x="260" y="230" font-size="13">0</text></svg>'
add(122,'Counting intersections after two modulus transformations','Modulus functions',r'The diagram shows a continuous strictly increasing function $f$ on $\mathbb R$, with horizontal asymptotes $y=-3$ as $x\to-\infty$ and $y=5$ as $x\to\infty$. Its intercepts are $(a,0)$ and $(0,-b)$, where $a>0$ and $0<b<3$. Let $g(x)=|f(|x|)|$.',[
 P(r'Sketch $g$, labelling its intercepts and horizontal asymptote.',('A1',r'Retain the part of $f$ with $x\ge0$ and reflect it in the $y$-axis.'),('A1',r'Reflect negative ordinates upwards: $g$ has roots $x=\pm a$, a central local maximum $(0,b)$ and minima $(\pm a,0)$.'),('A1',r'The two outer branches rise towards horizontal asymptote $y=5$; the result is even.')),
 P(r'Find all real $r$ such that $[g(x)]^2=r$ has exactly two distinct real solutions.',('M1',r'For $r\ge0$, count intersections of $g$ with the line $y=\sqrt r$.'),('R1',r'At height 0 there are two; for $0<\sqrt r<b$ there are four; at $b$ there are three; for $b<\sqrt r<5$ there are two. Heights at least 5 or below 0 give none.'),('A1',r'$r\in\{0\}\cup(b^2,25)$.'))],diagram=svg122)
f123=8*x*x-10*x+3
add(123,'Domain of a logarithmic composition','Exponential and logarithmic functions',r'Let $f(x)=8x^2-10x+3$, $g(x)=\ln x$ and $h=g\circ f$.',[
 P(r'Factorise $f$ completely.',('M1',r'Seek two linear factors with product of leading coefficients 8 and constant terms 3.'),('A1',r'$f(x)=(4x-3)(2x-1)$.')),
 P(r'Find the domain of $h$.',('M1',r'The logarithm requires $f(x)>0$.'),('A1',r'The zeros are $1/2,3/4$, and the quadratic opens upwards.'),('A1',r'$D_h=(-\infty,1/2)\cup(3/4,\infty)$.')),
 P(r'Define $h_a(x)=\ln(f(x)+a)$. Find the threshold $a_0$ for which $h_a$ has domain $\mathbb R$ exactly when $a>a_0$.',('M1',r'Complete the square: $f(x)=8(x-5/8)^2-1/8$.'),('A1',r'The minimum of $f$ is $-1/8$.'),('R1',r'The argument must be strictly positive, including at the vertex, so $a>1/8$ and $a_0=1/8$.')),
 P(r'For $b>a_0$, find $b$ such that the vertex of $h_b$ lies on the $x$-axis. Give $b$ to four significant figures.',('M1',r'The vertex ordinate is $\ln(b-1/8)$.'),('A1',r'$\ln(b-1/8)=0\Rightarrow b-1/8=1$.'),('A1',r'$b=9/8=1.125$.'))]);ck(123,f123,(4*x-3)*(2*x-1));ck(123,f123,8*(x-sp.Rational(5,8))**2-sp.Rational(1,8))
add(124,'Counting and identifying cubic polynomials','Polynomials',r'The polynomial $P(x)=ax^3+bx^2+cx+d$ has coefficients from the set $\{3,9,12,36\}$.',[
 P(r'Find the number of possible polynomials (i) when values may be repeated; (ii) when all four coefficients must differ.',('M1',r'With repetition there are four independent choices for each of four positions.'),('A1',r'$4^4=256$.'),('M1',r'Without repetition there are $4\times3\times2\times1$ assignments.'),('A1',r'$4!=24$.')),
 P(r'Now suppose all coefficients differ, $x+3$ is a factor, and the other two roots are purely imaginary. (i) Use the sum of roots to find the two possible ordered pairs $(a,b)$. (ii) Given $P(0)=36$, show that the coefficient assignment is unique.',('M1',r'Real coefficients give roots $-3,it,-it$ with $t>0$, so the sum is $-3$.'),('R1',r'By Vieta, $-b/a=-3$, hence $b=3a$.'),('A2',r'The possibilities are $(a,b)=(3,9)$ or $(12,36)$ (one each).'),('R1',r'$P(0)=d=36$ excludes $b=36$, because all coefficients differ.'),('A1',r'Therefore $a=3,b=9,c=12,d=36$ is the only assignment.'),('R1',r'It is admissible: $P(x)=3(x+3)(x^2+4)$, whose other roots are purely imaginary.')),
 P(r'For this polynomial, (i) express $P$ as a product of a linear and a quadratic factor; (ii) find all three roots.',('M1',r'Group terms: $3x^2(x+3)+12(x+3)$.'),('M1',r'Factor out the common factor $x+3$ from the two grouped terms.'),('A1',r'$P(x)=3(x+3)(x^2+4)$.'),('M1',r'Set each factor to zero.'),('A1',r'$x=-3$.'),('A1',r'$x=2i$.'),('A1',r'$x=-2i$.'))]);ck(124,3*(x+3)*(x*x+4),3*x**3+9*x*x+12*x+36)
add(125,'A rational graph, inverse and trigonometric composition','Rational functions',r'$f(x)=\dfrac8{x^2+4x-12}$, for $x\in\mathbb R\setminus\{-6,2\}$. Let $g$ be its restriction to $x>2$, and let $h(x)=\arccos(x/8)$.',[
 P(r'Sketch $f$, labelling all intercepts, asymptotes and local extrema.',('A1',r'Vertical asymptotes $x=-6$ and $x=2$.'),('A1',r'Horizontal asymptote $y=0$.'),('A1',r'The $y$-intercept is $(0,-2/3)$; there are no $x$-intercepts.'),('M1',r'$f\prime(x)=-16(x+2)/(x^2+4x-12)^2$, so the stationary input is $-2$.'),('A1',r'There is a local maximum at $(-2,-1/2)$.'),('A1',r'The outer branches are positive and approach 0; the middle branch is negative and tends to $-\infty$ at its ends.')),
 P(r'Show that $g^{-1}(x)=-2+\sqrt{(16x+8)/x}$.',('M1',r'Set $y=8/(x^2+4x-12)$, with $x>2$.'),('A1',r'$x^2+4x-12=8/y$.'),('M1',r'Complete the square.'),('A1',r'$(x+2)^2=16+8/y$.'),('R1',r'Use the positive square root since $x+2>4>0$.'),('A1',r'$x=-2+\sqrt{16+8/y}$, so $g^{-1}(x)=-2+\sqrt{(16x+8)/x}$.')),
 P(r'State the domain of $g^{-1}$.',('A1',r'$(0,\infty)$, the range of $g$.')),
 P(r'Given $(h\circ g)(a)=\pi/3$, find $a$ in the form $p+q\sqrt2$, where $p,q\in\mathbb Z$.',('M1',r'Take cosine: $g(a)/8=\cos(\pi/3)$.'),('A1',r'$g(a)=4$.'),('M1',r'Substitute $g(a)=8/(a^2+4a-12)$.'),('A1',r'$a^2+4a-14=0$.'),('M1',r'Complete the square: $(a+2)^2=18$.'),('A1',r'$a=-2\pm3\sqrt2$.'),('R1',r'Only $a=-2+3\sqrt2$ lies in the domain $a>2$.'))],solution=graph([(lambda z:8/(z*z+4*z-12),R)],(-10,6),(-3,3),[(0,-2/3,'(0,-2/3)'),(-2,-.5,'(-2,-1/2)')],vl=[-6,2],hl=[0]))
ck(125,8/(((-2+3*sp.sqrt(2))**2+4*(-2+3*sp.sqrt(2))-12)),4)
add(126,'Roots in arithmetic or geometric progression','Polynomials',r'The monic cubic $x^3+bx^2+cx+d$ has roots $r_1,r_2,r_3$, which may be complex.',[
 P(r'Expand $(x-r_1)(x-r_2)(x-r_3)$ to show that $b=-(r_1+r_2+r_3)$, $c=r_1r_2+r_1r_3+r_2r_3$, and $d=-r_1r_2r_3$.',('M1',r'The first two factors give $x^2-(r_1+r_2)x+r_1r_2$.'),('A1',r'Multiplying by $x-r_3$ gives $x^3-(r_1+r_2+r_3)x^2+(r_1r_2+r_1r_3+r_2r_3)x-r_1r_2r_3$.'),('A1',r'Comparing coefficients yields all three stated identities.')),
 P(r'For $b=-12,c=64$, suppose the roots form an arithmetic progression. Show that one root is 4, and hence find $d$.',('M1',r'Write the roots as $u-v,u,u+v$. Their sum is $3u=12$.'),('A1',r'$u=4$, so one root is 4.'),('M1',r'The pairwise products sum to $3u^2-v^2=64$.'),('A1',r'$v^2=48-64=-16$, giving product $u(u^2-v^2)=4(16+16)=128$.'),('A1',r'$d=-128$.')),
 P(r'In another case with $b=-12,c=64$, the roots form a geometric progression. Find $d$.',('M1',r'Write the roots as $u/r,u,ur$, with $r\ne0$; $u\ne0$ since their sum is 12.'),('A1',r'$u(r+1+1/r)=12$.'),('M1',r'The pairwise products give $u^2(r+1+1/r)=64$.'),('A1',r'Divide the two equations to obtain $u=64/12=16/3$.'),('M1',r'The product of the three roots is $u^3$.'),('A1',r'$d=-(16/3)^3=-4096/27$.'))]);ck(126,(4-4*sp.I)*4*(4+4*sp.I),128)
f127=x**4-sp.Rational(1,2)*x**3-3*x*x+x+sp.Rational(3,2)
crit127=sorted(float(sp.re(z)) for z in sp.nroots(sp.diff(f127,x)));vals127=[float(f127.subs(x,z)) for z in crit127]
a127,b127=crit127[1:];ya127,yb127=vals127[1:]
grid127=np.linspace(a127,b127,700);fn127=sp.lambdify(x,f127,'numpy');fvals127=fn127(grid127)
low127=(1+math.asin(13/16))/3;up127=(1+math.pi/2)/3
add(127,'A quartic inverse composed with a sine function','Composite and inverse functions',r'Let $f(x)=x^4-0.5x^3-3x^2+x+1.5$, for $x\in\mathbb R$.',[
 P(r'Solve $f(x)>0$.',('M1',r'Find the zeros from $f(x)=(x+3/2)(x-1)(x^2-x-1)$.'),('A1',r'They are $-3/2,(1-\sqrt5)/2,1,(1+\sqrt5)/2$ in increasing order.'),('A1',r'$x\in(-\infty,-3/2)\cup((1-\sqrt5)/2,1)\cup((1+\sqrt5)/2,\infty)$.')),
 P(r'Find (i) the coordinates of all local extrema; (ii) the $x$-coordinates of the inflexion points.',('M1',r'Solve $f\prime(x)=4x^3-1.5x^2-6x+1=0$.'),('A2',fr'Local minima approximately $({crit127[0]:#.3g},{vals127[0]:#.3g})$ and $({crit127[2]:#.3g},{vals127[2]:#.3g})$; local maximum approximately $({crit127[1]:#.3g},{vals127[1]:#.3g})$. Award one for both minima, one for the maximum.'),('M1',r'$f\prime\prime(x)=12x^2-3x-6=0$; it changes sign at both roots.'),('A1',r'$x=(1\pm\sqrt{33})/8\approx-0.593,0.843$.')),
 P(r'Restrict $f$ to an interval $[a,b]$ with $a,b>0$, containing $x=0.5$, so that the restriction has an inverse. Find the smallest possible $a$ and largest possible $b$, to three significant figures. Sketch the restriction and its inverse, labelling endpoints. Solve $f^{-1}(x)=0.5$.',('A2',fr'$a\approx{a127:#.3g}$ and $b\approx{b127:#.3g}$, the endpoints of the maximal decreasing branch containing $0.5$ (one each).'),('M1',r'Reflect the restricted graph in $y=x$.'),('A1',fr'The branch endpoints are approximately $({a127:#.3g},{ya127:#.3g})$, $({b127:#.3g},{yb127:#.3g})$; swap coordinates for the inverse endpoints.'),('M1',r'$f^{-1}(x)=0.5\Rightarrow x=f(0.5)$.'),('A1',r'$x=5/4=1.25$.')),
 P(r'Let $g(x)=\frac45\sin(3x-1)+\frac35$, on $\frac{1-\pi/2}{3}\le x\le\frac{1+\pi/2}{3}$. (i) Find $g^{-1}$ and its domain. (ii) Solve $(f^{-1}\circ g)(x)<0.5$ using the restriction in (c).',('M1',r'Rearrange $y=\frac45\sin(3x-1)+\frac35$ to $\sin(3x-1)=(5y-3)/4$.'),('A1',r'The phase interval is $[-\pi/2,\pi/2]$, so $3x-1=\arcsin((5y-3)/4)$.'),('A1',r'$g^{-1}(x)=[1+\arcsin((5x-3)/4)]/3$.'),('A1',r'The inverse domain is $[-1/5,7/5]$.'),('R1',r'The restricted $f$ and its inverse are decreasing, so $f^{-1}(g(x))<0.5$ is equivalent to $g(x)>f(0.5)=5/4$. The whole range of $g$ lies in the domain of this inverse.'),('M1',r'$\frac45\sin(3x-1)+\frac35>\frac54$.'),('A1',r'$\sin(3x-1)>13/16$.'),('A1',fr'$\frac{{1+\arcsin(13/16)}}3<x\le\frac{{1+\pi/2}}3$, approximately ${low127:#.3g}<x\le{up127:#.3g}$.'))],solution=graph([(lambda z:float(fn127(z)) if a127<=z<=b127 else math.nan,B),(lambda z:float(np.interp(z,fvals127[::-1],grid127[::-1])) if yb127<=z<=ya127 else math.nan,R)],(-1,2),(-1,2)),note='Clarified the inverse restriction must contain 0.5, avoiding the reference ambiguity about positive left endpoints on a separate monotonic branch.')
ck(127,f127,(x+sp.Rational(3,2))*(x-1)*(x*x-x-1));ck(127,f127.subs(x,sp.Rational(1,2)),sp.Rational(5,4))
for z in crit127:nc(127,sp.diff(f127,x).subs(x,z),0)
add(128,'A monotone cubic with an inverse','Composite and inverse functions',r'Let $g(x)=ax^3+bx^2+cx+d$ for $x\in\mathbb R$, where $a\ne0$ and all coefficients are real.',[
 P(r'Write down $g\prime(x)$. Hence show that if $g$ has no inverse function, then $b^2-3ac>0$.',('A1',r'$g\prime(x)=3ax^2+2bx+c$.'),('R1',r'If $b^2-3ac\le0$, this derivative quadratic has discriminant $4(b^2-3ac)\le0$. It has the constant sign of $a$, apart from at most one zero.'),('R1',r'Then $g$ is strictly monotonic on $\mathbb R$ and has an inverse. The contrapositive proves that no inverse implies $b^2-3ac>0$.')),
 P(r'Now let $f(x)=x^3/3+3x^2+9x+7$. (i) Show that $f^{-1}$ exists. (ii) Find $p,q$ such that $f(x)=p(x+3)^3+q$. (iii) Find $f^{-1}(x)$.',('M1',r'Differentiate: $f\prime(x)=x^2+6x+9$.'),('A1',r'$f\prime(x)=(x+3)^2$.'),('R1',r'The derivative is positive except at the isolated input $-3$, so $f$ is strictly increasing and has an inverse.'),('A1',r'$f(x)=\tfrac13(x+3)^3-2$, hence $p=1/3,q=-2$.'),('M1',r'$y=\tfrac13(x+3)^3-2\Rightarrow (x+3)^3=3y+6$.'),('A1',r'$x=\sqrt[3]{3y+6}-3$.'),('A1',r'$f^{-1}(x)=\sqrt[3]{3x+6}-3$ for all real $x$.')),
 P(r'Describe three ordered transformations taking $y=x^3$ to $y=f(x)$.',('A1',r'Translate 3 units left.'),('A1',r'Scale vertically by factor $1/3$.'),('A1',r'Translate 2 units down.')),
 P(r'Sketch $f$ and its inverse on the same axes, labelling their axis intercepts.',('A1',r'$f$ has intercepts $(0,7)$ and $(\sqrt[3]6-3,0)$.'),('A1',r'The inverse has intercepts $(0,\sqrt[3]6-3)$ and $(7,0)$.'),('A1',r'The graphs are reflections in $y=x$.'),('A1',r'Correct increasing cubic with stationary inflexion $(-3,-2)$ and increasing cube-root graph with vertical tangent at $(-2,-3)$.'))],solution=graph([(lambda z:(z+3)**3/3-2,B),(lambda z:np.cbrt(3*z+6)-3,R)],(-6,9),(-6,9)))
ck(128,(x+3)**3/3-2,x**3/3+3*x*x+9*x+7)
prob129=2*norm.sf(2);num129=2*norm.sf(2.5);cond129=num129/prob129
add(129,'Random quadratic roots and conditional probability','Discriminants',r'Let $f(x)=x^2+2bx+4$, with real $b$.',[
 P(r'Find the values of $b$ for which $f$ has two distinct real roots.',('M1',r'The discriminant must be positive: $4b^2-16>0$.'),('A1',r'$b<-2$ or $b>2$.')),
 P(r'Let $g(x)=x^2+2Ax+4$, where $A\sim N(0,1)$. Show that the probability of two distinct real roots is 0.04550, to four significant figures.',('M1',r'Real distinct roots occur precisely when $|A|>2$.'),('A1',r'$P(|A|>2)=2[1-\Phi(2)]$ by symmetry.'),('A1',fr'$P\approx{prob129:.8f}\approx0.04550$ to four significant figures.')),
 P(r'Given that $g$ has two distinct real roots, label them so that $|r_1|<2<|r_2|$. Find $P(|r_1|<1\mid g\text{ has two distinct real roots})$.',('M1',r'The roots are $-A\pm\sqrt{A^2-4}$.'),('A1',r'With $s=|A|>2$, the smaller absolute value is $s-\sqrt{s^2-4}$. The root product is 4, so their absolute values straddle 2.'),('M1',r'The required condition is $s-\sqrt{s^2-4}<1$.'),('R1',r'This is $\sqrt{s^2-4}>s-1$; both sides are non-negative, so squaring preserves the inequality.'),('M1',r'$s^2-4>(s-1)^2=s^2-2s+1$.'),('A1',r'$s>5/2$, or $|A|>2.5$.'),('M1',r'The conditional probability is $P(|A|>2.5)/P(|A|>2)$.'),('A1',fr'This is $2[1-\Phi(2.5)]/[2(1-\Phi(2))]\approx{num129:.8f}/{prob129:.8f}$.'),('A1',fr'The probability is approximately ${cond129:#.3g}$.'))]);nc(129,cond129,float(sp.erfc(sp.Rational(5,2)/sp.sqrt(2))/sp.erfc(sp.sqrt(2))),1e-12)
assert len(OUT)==129
assert {q['number'] for q in OUT}==set(range(1,130))
emit()
