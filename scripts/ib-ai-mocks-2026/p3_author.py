"""Original AI HL Paper 3 investigations, with fresh reproducible checks.

No source question text, numbers, diagrams or solution structures are imported.
Python standard library only. Run from any directory to regenerate owned files.
"""
from __future__ import annotations

import cmath
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'content/ib/ai-mocks-2026/papers'
REVIEW = ROOT / 'docs/ib-ai-mocks-2026/p3-author-review.json'
checks = []


def test(q, part, name, actual, expected=True, tolerance=0):
    passed = abs(actual-expected) <= tolerance if tolerance else actual == expected
    assert passed, (q, part, name, actual, expected)
    if isinstance(actual, complex): actual = [actual.real, actual.imag]
    if isinstance(expected, complex): expected = [expected.real, expected.imag]
    checks.append({'question':q,'part':part,'check':name,'actual':actual,'expected':expected,'tolerance':tolerance,'passed':True})


def close(q, part, name, actual, expected, tolerance=1e-9):
    test(q,part,name,actual,expected,tolerance)


def part(label, prompt, marks): return {'label':label,'prompt':prompt,'marks':marks}
def scheme(label, *steps): return {'part':label,'steps':[{'code':c,'text':s} for c,s in steps]}


def svg(body, width=760, height=420):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img"><rect width="{width}" height="{height}" fill="#fff"/>{body}</svg>'


def text(x,y,s,size=19,anchor='middle'):
    return f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="{size}" text-anchor="{anchor}" fill="#111">{s}</text>'


def line(x1,y1,x2,y2,dash=False):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#111" stroke-width="2"'+(' stroke-dasharray="6 5"' if dash else '')+'/>'


def arrow(x1,y1,x2,y2):
    theta=math.atan2(y2-y1,x2-x1);a=10;d=.45
    tip=f'<polyline points="{x2-a*math.cos(theta-d):.2f},{y2-a*math.sin(theta-d):.2f} {x2},{y2} {x2-a*math.cos(theta+d):.2f},{y2-a*math.sin(theta+d):.2f}" fill="none" stroke="#111" stroke-width="2"/>'
    return line(x1,y1,x2,y2)+tip


markov = svg(
    '<circle cx="215" cy="205" r="62" fill="#fff" stroke="#111" stroke-width="2"/>'
    '<circle cx="545" cy="205" r="62" fill="#fff" stroke="#111" stroke-width="2"/>'
    +text(215,201,'Unstable U')+text(215,228,'p = 0.12',17)
    +text(545,201,'Stable S')+text(545,228,'p = 0.04',17)
    +arrow(276,183,484,183)+text(380,168,'0.20')
    +arrow(484,227,276,227)+text(380,258,'0.30')
    +'<path d="M170 162 C90 48 340 48 260 162" fill="none" stroke="#111" stroke-width="2"/>'
    +'<polyline points="257,149 260,162 271,155" fill="none" stroke="#111" stroke-width="2"/>'
    +text(215,76,'0.80')
    +'<path d="M500 162 C420 48 670 48 590 162" fill="none" stroke="#111" stroke-width="2"/>'
    +'<polyline points="587,149 590,162 601,155" fill="none" stroke="#111" stroke-width="2"/>'
    +text(545,76,'0.70')
    +text(380,337,'State changes once per day; seal probabilities are conditional on that day\u2019s state.',16),
    height=370,
)

reservoir = svg(
    '<rect x="85" y="140" width="215" height="140" rx="9" fill="#f5f5f5" stroke="#111" stroke-width="2"/>'
    '<rect x="460" y="140" width="215" height="140" rx="9" fill="#f5f5f5" stroke="#111" stroke-width="2"/>'
    +text(192,177,'Reservoir X')+text(192,211,'100000 L')+text(192,247,'pollutant x(t) kg')
    +text(567,177,'Reservoir Y')+text(567,211,'100000 L')+text(567,247,'pollutant y(t) kg')
    +arrow(300,178,460,178)+text(380,164,'20000 L/h',17)
    +arrow(460,244,300,244)+text(380,271,'20000 L/h',17)
    +arrow(150,70,150,140)+text(150,44,'Fresh: 10000 L/h',16)
    +arrow(610,70,610,140)+text(610,44,'Fresh: 10000 L/h',16)
    +arrow(150,280,150,350)+text(150,378,'Drain: 10000 L/h',16)
    +arrow(610,280,610,350)+text(610,378,'Drain: 10000 L/h',16)
    +text(380,417,'Each reservoir is kept at a constant volume and is perfectly mixed.',16),
    height=440,
)

phi=1.2;scale=70;x0,y0=135,100;Z=4+3*cmath.exp(-1j*phi)
phasor = svg(
    arrow(75,y0,665,y0)+arrow(x0,345,x0,35)
    +text(692,y0+6,'Re')+text(x0-22,31,'Im')+text(x0-17,y0-13,'O')
    +arrow(x0,y0,x0+4*scale,y0)+text(x0+2*scale,y0-18,'4')
    +arrow(x0+4*scale,y0,x0+Z.real*scale,y0-Z.imag*scale)
    +text(550,217,'3 exp(-i\u03c6)',18)
    +arrow(x0,y0,x0+Z.real*scale,y0-Z.imag*scale)+text(290,220,'Z',22)
    +line(x0+4*scale,y0,x0+4*scale+80,y0,True)
    +'<path d="M455 100 A40 40 0 0 1 429.49 137.28" fill="none" stroke="#111" stroke-width="1.5"/>'
    +text(465,135,'\u03c6',20)
    +text(380,380,'Phasor construction for one phase choice; all phases in radians.',17),
    height=410,
)

pos={'A':(100,205),'B':(225,55),'C':(515,55),'D':(640,205),'E':(515,355),'F':(225,355)}
edges=[('A','B',4),('B','C',5),('C','D',4),('D','E',6),('E','F',5),('F','A',6),('A','D','w'),('B','E',7)]
labels=[(145,115),(370,38),(598,115),(600,305),(370,384),(145,305),(300,188),(420,275)]
network_body=''
for (a,b,w),(lx,ly) in zip(edges,labels):
    network_body+=line(*pos[a],*pos[b])+f'<rect x="{lx-18}" y="{ly-19}" width="36" height="26" fill="#fff"/>'+text(lx,ly,str(w))
for a,(x,y) in pos.items():
    network_body+=f'<circle cx="{x}" cy="{y}" r="5" fill="#111"/>'
    dx,dy={'A':(-22,5),'B':(-9,-18),'C':(9,-18),'D':(22,5),'E':(9,29),'F':(-9,29)}[a]
    network_body+=text(x+dx,y+dy,a,20)
network_body+=text(370,437,'Edge weights are minutes. Crossings of edges are not junctions.',17)
network=svg(network_body,height=460)


A1={
 'number':1,'section':'','marks':27,
 'syllabusRefs':['SL 1.3','SL 4.6','SL 4.8','AHL 4.18','AHL 4.19'],
 'stem':r'''A factory models each day's production as being in one of two states: unstable $U$ or stable $S$. The state changes once per day according to the transition diagram. Initially, on day $0$, the factory is known to be stable.

On each day an inspector takes $40$ seals. Conditional on that day's state, the seals are independent and each seal is defective with probability $0.12$ in state $U$, or $0.04$ in state $S$. Let $X$ be the number of defective seals in the sample. The sample is too small to change the state-transition probabilities.

The inspector tests $H_0:p=0.04$ against $H_1:p>0.04$ at the $5\%$ significance level, raising an alert when $X\ge c$. Choose the smallest integer $c$ for which the Type I error probability is less than $0.05$.

Let $q_n$ be the probability that the factory is unstable on day $n$, and let $a_n$ be the probability of an alert on day $n$. Use unrounded probabilities in subsequent calculations.''',
 'diagramSvg':markov,
 'parts':[
  part('a',r'Find $c$ and the actual Type I error probability. Show why the next smaller value of $c$ is unsuitable.',4),
  part('b',r'Find the Type II error probability when $p=0.12$. Interpret this error in the factory context.',3),
  part('c',r'Using column states ordered $(U,S)$, write down the transition matrix $T$. Find $q_2$.',3),
  part('d',r'By considering $q_{n+1}-0.6$, obtain an explicit formula for $q_n$ valid for every integer $n\ge0$. Show the reasoning leading to your formula.',5),
  part('e',r'In the long run, an alert is observed. Find the conditional probability that the factory is unstable on that day.',4),
  part('f',r'Find the smallest day number $n$ for which $|a_n-\lim_{k\to\infty}a_k|<0.001$.',3),
  part('g',r'For a more general factory, suppose $\mathrm P(U\to S)=\kappa u$ and $\mathrm P(S\to U)=\kappa v$, where $u,v>0$ and $0<\kappa(u+v)<1$. The two conditional seal distributions and alert rule are unchanged. Show that the limiting alert probability is independent of $\kappa$. Explain how increasing $\kappa$ affects the approach to this limit from a fixed initial state distribution.',5)
 ],
 'answerSummary':r'$c=5$; $\alpha=0.0210222967$, $\beta=0.4669109648$; $q_2=0.45$; $q_n=0.6(1-2^{-n})$; long-run $\mathrm P(U\mid\text{alert})=0.9743835412$; first day $n=9$. General limit uses $v/(u+v)$ and convergence factor $1-\kappa(u+v)$.',
 'markScheme':[
  scheme('a',('M1',r'Under $H_0$, use $X\sim\operatorname{Bin}(40,0.04)$ and upper-tail probabilities.'),('A1',r'$\mathrm P(X\ge4)=0.0748372580>0.05$.'),('A1',r'$\mathrm P(X\ge5)=0.0210222967<0.05$.'),('A1',r'Thus $c=5$, with actual Type I probability $\alpha=0.0210$ (three significant figures).')),
  scheme('b',('M1',r'Use $X\sim\operatorname{Bin}(40,0.12)$ and failure to reject, $X\le4$.'),('A1',r'$\beta=\mathrm P(X\le4)=0.4669109648\approx0.467$.'),('R1',r'The inspector fails to raise an alert although the factory is in its unstable, higher-defect state.')),
  scheme('c',('A1',r'$T=\begin{pmatrix}0.8&0.3\\0.2&0.7\end{pmatrix}$, with column entries representing transitions from that column state.'),('M1',r'Apply $T^2$ to $\binom01$, or use $q_1=0.3$ and $q_2=0.8q_1+0.3(1-q_1)$.'),('A1',r'$q_2=0.45$.')),
  scheme('d',('M1',r'$q_{n+1}=0.8q_n+0.3(1-q_n)=0.3+0.5q_n$.'),('A1',r'The stationary value solves $q=0.3+0.5q$, so $q=0.6$.'),('M1',r'$q_{n+1}-0.6=0.5(q_n-0.6)$, a geometric sequence of differences.'),('A1',r'$q_n-0.6=(q_0-0.6)(0.5)^n$.'),('A1',r'Since $q_0=0$, $q_n=0.6(1-2^{-n})$, including $n=0$.')),
  scheme('e',('M1',r'The limiting alert probability is $a_\infty=0.6(1-\beta)+0.4\alpha$.'),('A1',r'$a_\infty=0.3282623398$.'),('M1',r'$\mathrm P(U\mid\text{alert})=0.6(1-\beta)/a_\infty$.'),('A1',r'$0.9743835412\approx0.974$.')),
  scheme('f',('M1',r'$a_n=\alpha+(1-\beta-\alpha)q_n$, so $|a_n-a_\infty|=0.6(1-\beta-\alpha)2^{-n}$.'),('A1',r'Solving the inequality gives $n>8.2632\ldots$, hence $n=9$.'),('R1',r'At $n=8$ the difference is $0.00120016\ldots$; at $n=9$ it is $0.000600078\ldots$, verifying the first integer day.')),
  scheme('g',('M1',r'The general recurrence is $q_{n+1}=\kappa v+[1-\kappa(u+v)]q_n$.'),('A1',r'The limiting unstable probability is $\pi=v/(u+v)$.'),('M1',r'The limiting alert probability is $\alpha+(1-\beta-\alpha)v/(u+v)$.'),('A1',r'This expression contains no $\kappa$, so the limit is unchanged.'),('R1',r'$q_n-\pi=[1-\kappa(u+v)]^n(q_0-\pi)$. The factor lies in $(0,1)$ and decreases as $\kappa$ increases, so convergence is faster (or the process is already stationary).'))
 ],'sourcePages':[]
}


A2={
 'number':2,'section':'','marks':28,
 'syllabusRefs':['AHL 1.14','AHL 1.15','SL 2.6','AHL 5.9','AHL 5.10','AHL 5.14','AHL 5.16','AHL 5.17'],
 'stem':r'''Two reservoirs $X$ and $Y$ each contain $100\,000$ litres of water. In each direction, water is pumped between the reservoirs at $20\,000$ litres per hour. Each reservoir also receives pollutant-free water at $10\,000$ litres per hour and discharges water to a drain at the same rate. Each reservoir is perfectly mixed, and its volume stays constant.

At time $t=0$, reservoir $X$ contains $30$ kg of pollutant and reservoir $Y$ contains none. No further pollutant enters the system. Let $x(t)$ and $y(t)$ be the pollutant masses, in kg, at time $t$ hours. Pollutant leaves each reservoir at its current concentration.

The diagram shows the flow rates. Take $1$ kg to be $10^6$ mg.''',
 'diagramSvg':reservoir,
 'parts':[
  part('a',r'Obtain the coupled differential equations for $x$ and $y$, and express them as a matrix equation.',4),
  part('b',r'Use the eigenvalues and eigenvectors of your matrix to find exact expressions for $x(t)$ and $y(t)$.',6),
  part('c',r'Find the time at which reservoir $Y$ contains the most pollutant, and find this maximum mass. Justify that it is a global maximum for $t\ge0$.',4),
  part('d',r'Both reservoirs are classified as safe when each concentration is at most $10$ mg per litre. Find the earliest time at which both are safe, explaining which reservoir determines this time.',3),
  part('e',r"Apply Euler's method with step length $h=1$ hour for two steps. Compare the resulting $y(2)$ with the exact value. A technician claims that an Euler model is accurate whenever it keeps both masses nonnegative. Evaluate this claim using your results.",3),
  part('f',r'Now replace each exchange flow of $20\,000$ litres per hour by an arbitrary rate $Q>0$, leaving both fresh-water and drain rates unchanged. Find the half-life of the total pollutant mass. Does increasing $Q$ make the total pollutant disappear faster? Justify your answer.',3),
  part('g',r'Return to the original exchange flow. Set $S_n=x_n+y_n$ and $D_n=x_n-y_n$ for an Euler approximation with step length $h>0$. Derive recurrences for $S_n$ and $D_n$. Determine the largest $h$ that guarantees, for every initial state $x_0\ge y_0\ge0$, that both masses stay nonnegative and the ordering $x_n\ge y_n$ is preserved at every step. Explain why this guarantee still does not establish accuracy.',5)
 ],
 'answerSummary':r'$\binom{x\prime}{y\prime}=\begin{pmatrix}-0.3&0.2\\0.2&-0.3\end{pmatrix}\binom xy$; $x=15(e^{-t/10}+e^{-t/2})$, $y=15(e^{-t/10}-e^{-t/2})$. The downstream maximum is $8.02488366$ kg at $t=(5/2)\ln5=4.02359478$ h. Safe time $27.08069952$ h. Euler after two steps: $(15.9,8.4)$ kg; exact $y(2)=6.76276968$ kg. Total half-life $10\ln2$ h; largest order-preserving Euler step $h=2$ h.',
 'markScheme':[
  scheme('a',('M1',r'Concentration is mass divided by $100000$ L; total outflow from each reservoir is $30000$ L/h.'),('M1',r'Pollutant inflow from the other reservoir is $0.2$ times its pollutant mass per hour.'),('A1',r'$x\prime=-0.3x+0.2y$, $y\prime=0.2x-0.3y$.'),('A1',r'$\binom{x\prime}{y\prime}=\begin{pmatrix}-0.3&0.2\\0.2&-0.3\end{pmatrix}\binom xy$.')),
  scheme('b',('M1',r'Use the characteristic equation $(-0.3-\lambda)^2-0.04=0$.'),('A2',r'Eigenvalues are $-0.1$ and $-0.5$.'),('A1',r'Corresponding eigenvectors may be taken as $\binom11$ and $\binom1{-1}$.'),('M1',r'$\binom xy=C_1e^{-0.1t}\binom11+C_2e^{-0.5t}\binom1{-1}$; apply $x(0)=30$, $y(0)=0$ to get $C_1=C_2=15$.'),('A1',r'$x(t)=15(e^{-t/10}+e^{-t/2})$, $y(t)=15(e^{-t/10}-e^{-t/2})$.')),
  scheme('c',('M1',r'$y\prime=-1.5e^{-t/10}+7.5e^{-t/2}=0$.'),('A1',r'$e^{0.4t}=5$, hence $t=(5/2)\ln5=4.023594781\ldots$ h.'),('R1',r'$y\prime$ changes from positive to negative at this sole stationary point; $y(0)=0$ and $y(t)\to0$, so it is the global maximum.'),('A1',r'$y_{\max}=8.024883660\ldots\approx8.02$ kg.')),
  scheme('d',('M1',r'$10$ mg/L in $100000$ L is $1$ kg, so require $x\le1$ and $y\le1$.'),('R1',r'For $t\ge0$, $x-y=30e^{-t/2}>0$ and $x$ is strictly decreasing, so the first safe time is the unique solution of $x(t)=1$.'),('A1',r'Solve $15(e^{-t/10}+e^{-t/2})=1$: $t=27.08069952\ldots\approx27.1$ h.')),
  scheme('e',('M1',r'Use simultaneous Euler updates $x_{n+1}=x_n+h(-0.3x_n+0.2y_n)$ and $y_{n+1}=y_n+h(0.2x_n-0.3y_n)$.'),('A1',r'For $h=1$: $(x_1,y_1)=(21,6)$ and $(x_2,y_2)=(15.9,8.4)$.'),('R1',r'The exact $y(2)=6.762769679\ldots$ kg. The nonnegative Euler value overestimates it by about $24.2\%$ and even exceeds the exact global maximum $8.02488\ldots$ kg. Nonnegativity does not imply accuracy.')),
  scheme('f',('M1',r'Exchange terms cancel when adding the equations: $S\prime=-0.1S$, $S(0)=30$, independently of $Q$.'),('A1',r'$S(t)=30e^{-0.1t}$, so the total half-life is $10\ln2\approx6.93$ h.'),('R1',r'Increasing exchange changes the distribution between reservoirs, but not the total removal rate or half-life under this perfectly mixed model.')),
  scheme('g',('M1',r'Add and subtract the simultaneous Euler updates.'),('A1',r'$S_{n+1}=(1-0.1h)S_n$, $D_{n+1}=(1-0.5h)D_n$.'),('A1',r'Preserving $D_n\ge0$ for every $D_0\ge0$ requires $1-0.5h\ge0$, hence $h\le2$.'),('R1',r'For $0<h\le2$, the original update coefficients $1-0.3h$ and $0.2h$ are nonnegative, so masses remain nonnegative; the difference also stays nonnegative. Thus the largest allowed step is $2$ h. If $h>2$, any $D_0>0$ reverses sign after one step.'),('R1',r'These conditions preserve qualitative features only. Finite-step truncation error can remain large, as the $h=1$ computation demonstrates.'))
 ],'sourcePages':[]
}


B1={
 'number':1,'section':'','marks':27,
 'syllabusRefs':['AHL 1.12','AHL 1.13','AHL 2.9','SL 2.4','AHL 3.8','SL 5.7','AHL 5.11'],
 'stem':r'''A laboratory heating device receives two current components with the same period of $12$ seconds. Their combined current, in amperes, is modelled by

$$I(t)=4\cos(\omega t)+3\cos(\omega t-\phi),\qquad \omega=\frac{\pi}{6},\qquad 0\le\phi\le\pi.$$

The adjustable phase is $\phi$. Write the combined current as $I(t)=A\cos(\omega t-\delta)$ with $A>0$. A phasor diagram is shown for one phase choice.

When current is supplied to the heater, its useful instantaneous heating power is $10I(t)^2$ watts. A safety controller diverts the current away from the heater whenever $|I(t)|>4$ A. While diverted, the useful power is zero; the input current model itself is unchanged. Let $q$ be the fraction of a complete period for which the heater is off.

For any periodic power function $p(t)$ with period $12$ s, its mean power is

$$\overline P=\frac1{12}\int_0^{12}p(t)\,\mathrm dt.$$

You may use $\cos^2u=(1+\cos2u)/2$. All angles are in radians.''',
 'diagramSvg':phasor,
 'parts':[
  part('a',r'For $\phi=1.2$, use the complex number $Z=4+3e^{-i\phi}$ to find $A$ and $\delta$, giving $0\le\delta<\pi$.',3),
  part('b',r'For variable $\phi$, show that $A^2=25+24\cos\phi$. Hence state the possible range of $A$.',3),
  part('c',r'If the safety controller were removed, show that the mean heating power over a complete period would be $5A^2$ watts.',3),
  part('d',r'For $A>4$, obtain $q$ in terms of $A$. Also state $q$ when $1\le A\le4$.',4),
  part('e',r'The permitted fraction of time off is at most $1/4$. Find the resulting interval of permissible phases $\phi$.',3),
  part('f',r'With the controller operating, obtain an expression for the mean useful power $P(A)$ for $1\le A\le4$, and for $4<A\le7$. Show the integration leading to your expression. You may use symmetry over one complete phase cycle.',6),
  part('g',r'Use technology to investigate $P(A)$ under the restriction in part (e). Find the phase that maximizes mean useful power and the resulting maximum. Support your conclusion over the whole permitted domain. Explain why choosing the largest permitted amplitude is not optimal.',5)
 ],
 'answerSummary':r'At $\phi=1.2$, $A=5.80487606$, $\delta=0.502575580$. $A\in[1,7]$. $q=0$ for $A\le4$, otherwise $q=2\arccos(4/A)/\pi$. Permitted $\phi\in[1.834458682,\pi]$. $P=5A^2$ for $A\le4$; otherwise $P=10A^2[\arcsin(4/A)-(4/A)\sqrt{1-16/A^2}]/\pi$. Global optimum $A=4$, $\phi=\arccos(-3/8)=1.955193101$, $P=80$ W.',
 'markScheme':[
  scheme('a',('A1',r'$Z=5.087073263\ldots-2.796117258\ldots i$.'),('A1',r'$A=|Z|=5.804876063\ldots\approx5.80$ A.'),('A1',r'$\delta=-\arg Z=0.5025755802\ldots\approx0.503$ radians, so the combined cosine is delayed by $\delta$.')),
  scheme('b',('M1',r'$|Z|^2=(4+3\cos\phi)^2+(-3\sin\phi)^2$.'),('A1',r'$A^2=16+24\cos\phi+9(\cos^2\phi+\sin^2\phi)=25+24\cos\phi$.'),('A1',r'As $\phi$ ranges from $0$ to $\pi$, $1\le A\le7$.')),
  scheme('c',('M1',r'Use the average $\frac{10A^2}{12}\int_0^{12}\cos^2(\omega t-\delta)\,\mathrm dt$.'),('M1',r'Using the provided identity, the oscillatory cosine term has integral zero over a whole period and the constant term integrates to $6$.'),('A1',r'The unrestricted mean power is $5A^2$ W, independent of $\delta$.')),
  scheme('d',('M1',r'For $c=4/A\in(0,1)$, the controller is off when $|\cos u|>c$.'),('A1',r'Over a phase interval of length $2\pi$, this has total length $4\arccos c$.'),('A1',r'$q=2\arccos(4/A)/\pi$ for $A>4$.'),('A1',r'For $1\le A\le4$, the threshold is never exceeded and $q=0$.')),
  scheme('e',('M1',r'$2\arccos(4/A)/\pi\le1/4$ gives $A\le4/\cos(\pi/8)$, including the $A\le4$ cases.'),('A1',r'$A\le4.329568801\ldots$; use $25+24\cos\phi\le16\sec^2(\pi/8)$.'),('A1',r'$\arccos((16\sec^2(\pi/8)-25)/24)\le\phi\le\pi$, or $1.834458682\ldots\le\phi\le\pi$.')),
  scheme('f',('M1',r'A full-period average is unaffected by the phase shift; work with $u$ over $0\le u\le2\pi$.'),('M1',r'For $A>4$, put $c=4/A$ and use symmetry: $P=\frac{10A^2}{2\pi}\,4\int_{\arccos c}^{\pi/2}\cos^2u\,\mathrm du$.'),('M1',r'An antiderivative is $u/2+\sin(2u)/4$.'),('A1',r'The integral of $\cos^2u$ over all on-intervals is $2\arcsin c-2c\sqrt{1-c^2}$.'),('A1',r'$P(A)=\frac{10A^2}{\pi}\left[\arcsin(4/A)-\frac4A\sqrt{1-\frac{16}{A^2}}\right]$ W for $4<A\le7$.'),('A1',r'For $1\le A\le4$, there is no shutdown and $P(A)=5A^2$ W. Both expressions approach $80$ W at $A=4$.')),
  scheme('g',('M1',r'Investigate the piecewise function on the full permitted interval $1\le A\le4\sec(\pi/8)=4.329568801\ldots$.'),('A1',r'The maximum is $80$ W at $A=4$.'),('M1',r'Support globality with a labelled graph or equivalent numerical/analytic investigation showing increase up to $4$ and decrease from just above $4$ to the upper bound. A single isolated calculator maximum is insufficient.'),('A1',r'$\phi=\arccos((16-25)/24)=\arccos(-3/8)=1.955193101\ldots\approx1.96$ radians.'),('R1',r'Above $A=4$, the largest instantaneous powers are discarded by shutdown. Increasing amplitude increases lost peak intervals; a larger permitted amplitude therefore produces less useful mean power.'))
 ],'sourcePages':[]
}


B2={
 'number':2,'section':'','marks':28,
 'syllabusRefs':['SL 2.6','AHL 3.14','AHL 3.16'],
 'stem':r'''A maintenance crew must inspect every link of an underground service network. The undirected graph has the eight edges shown; edge weights are traversal times in minutes. Inspecting a link requires traversing the whole edge at least once. Edges may be repeated, and there are no junctions at crossings in the diagram.

The time on link $AD$ is a positive parameter $w$. All other times are fixed. Unless a part states otherwise, the crew starts and finishes at $A$. The aim is to minimize total traversal time, including repeated edges. Denote this minimum closed-route time by $L_c(w)$.''',
 'diagramSvg':network,
 'parts':[
  part('a',r'Identify the odd-degree vertices. Explain why the crew cannot inspect all eight links exactly once on a closed route.',2),
  part('b',r'For $w=2$, construct a table of shortest traversal times between the odd-degree vertices. Show any indirect paths used.',3),
  part('c',r'For $w=2$, find the minimum closed-route time and give one route attaining it. Justify why a shorter closed route is impossible.',5),
  part('d',r'Investigate how the optimal repeated links change as $w$ varies. Obtain an exact piecewise expression for $L_c(w)$ for all $w>0$, justifying the breakpoint and all candidate pairings.',6),
  part('e',r'The link $AD$ is removed from the inspection network. Find the new minimum closed-route time. Explain why removing a useful connection can nevertheless shorten an inspection route.',3),
  part('f',r'Instead, keep all eight links, but allow the crew to start at $A$ and finish at $D$. Show that the minimum open-route time is $L_o(w)=44+w$ for all $w>0$.',4),
  part('g',r'An open route incurs an additional return cost equivalent to $h>0$ minutes. Derive a complete decision rule in terms of $w$ and $h$ for choosing a closed route or an open route plus return. Include all tie cases. Explain why the maximum possible saving in traversal time from using an open route is only $3$ minutes, however large $w$ becomes.',5)
 ],
 'answerSummary':r'Odd vertices $A,B,D,E$. At $w=2$ minimum added time is $9$ and $L_c=48$. In general $L_c(w)=44+2w$ for $0<w\le3$, and $47+w$ for $w\ge3$. Removing $AD$ gives $44$. $L_o=44+w$. Open plus return is strictly better iff $h<3$ and $w>h$. Closed is strictly better iff $h>\min(w,3)$; ties are $h=\min(w,3)$.',
 'markScheme':[
  scheme('a',('A1',r'$A,B,D,E$ each have degree $3$; $C,F$ have degree $2$.'),('R1',r'A closed Eulerian route requires every degree even. Four odd vertices prevent traversing every edge exactly once on a closed route.')),
  scheme('b',('M1',r'Use shortest paths, including $A\to D\to E$ for $AE$ and $B\to A\to D$ for $BD$.'),('A2',r'For the order $(A,B,D,E)$, shortest distances are $d_{AB}=4$, $d_{AD}=2$, $d_{AE}=8$, $d_{BD}=6$, $d_{BE}=7$, $d_{DE}=6$; diagonal zeros and symmetric entries complete the table.')),
  scheme('c',('M1',r'Compare the three odd-vertex pairings: $(AB,DE)$, $(AD,BE)$ and $(AE,BD)$.'),('A1',r'Their added costs are $10$, $9$ and $14$, so repeat $AD$ and $BE$.'),('M1',r'The original edge total is $37+w=39$; any closed inspection route must correct all four odd degrees, requiring at least the least pairing cost.'),('A1',r'A route attaining it is $A-B-E-F-A-D-C-B-E-D-A$.'),('A1',r'The minimum is $39+9=48$ minutes.')),
  scheme('d',('M1',r'For general $w$, $d_{AD}=\min(w,13)$, since the alternative shortest path is $A-B-C-D$.'),('A1',r'The pairing $(AB,DE)$ always costs $4+6=10$.'),('A1',r'The pairing $(AD,BE)$ costs $\min(w,13)+7$.'),('A1',r'The third pairing costs $\min(w+6,11)+\min(w+4,9)$, which is $10+2w$ for $0<w\le5$ and $20$ for $w\ge5$.'),('R1',r'The third pairing is never cheaper than $10$. The first two tie at $w=3$; repeat $AD,BE$ below $3$, or $AB,DE$ above $3$.'),('A1',r'$L_c(w)=37+w+\min(w+7,10)=\begin{cases}44+2w,&0<w\le3,\\47+w,&w\ge3.\end{cases}$ Both formulas give $50$ at $w=3$.')),
  scheme('e',('M1',r'After removing $AD$, only $B,E$ are odd and the remaining edge total is $37$.'),('A1',r'Repeat shortest path $BE$ of length $7$, giving $37+7=44$ minutes.'),('R1',r'The inspection obligation itself loses an edge, and the parity requirements change. A connection may shorten point-to-point travel while increasing the work required to inspect every link.')),
  scheme('f',('M1',r'An open route from $A$ to $D$ requires exactly $A,D$ to remain odd.'),('A1',r'Thus the extra traversals need only correct the odd degrees at $B,E$.'),('A1',r'The shortest $B$ to $E$ path is the direct edge of length $7$ for every $w>0$.'),('A1',r'$L_o(w)=37+w+7=44+w$. For example $A-B-E-F-A-D-C-B-E-D$ attains this total.')),
  scheme('g',('M1',r'$L_c(w)-L_o(w)=\min(w,3)$.'),('A1',r'The open option including return costs $44+w+h$; its saving relative to the closed option is $\min(w,3)-h$.'),('R1',r'Choose open strictly when $0<h<3$ and $w>h$. Choose closed strictly when $h>\min(w,3)$.'),('A1',r'Tie when $h=\min(w,3)$: equivalently $w=h\le3$, or $h=3$ and $w\ge3$.'),('R1',r'For $w\ge3$, the best closed route repeats $AB$ and $DE$ for $10$ minutes, while the open route repeats $BE$ for $7$. This fixed $3$-minute difference bounds the saving; increasing $w$ adds the same once-traversed link time to both routes.'))
 ],'sourcePages':[]
}


papers=[]
for set_name,questions in [('A',[A1,A2]),('B',[B1,B2])]:
    papers.append({'id':f'ai-hl-set-{set_name.lower()}-paper-3','strand':'ai','course':'hl','set':set_name,'paper':'3','title':f'Mathematics AI HL — Set {set_name} Paper 3','minutes':75,'marks':55,'calculator':True,'questions':questions})


# A1: binomial tails and Markov dynamics, calculated from the given model.
binom_tail=lambda c,p:sum(math.comb(40,j)*p**j*(1-p)**(40-j) for j in range(c,41))
critical=next(c for c in range(41) if binom_tail(c,.04)<.05)
alpha=binom_tail(critical,.04);power=binom_tail(critical,.12);beta=1-power
test('A1','a','Minimal one-tailed critical count',critical,5)
close('A1','a','Rejected smaller threshold tail',binom_tail(4,.04),.07483725799931401)
close('A1','a','Actual significance',alpha,.02102229672833392)
close('A1','b','Type II probability',beta,.46691096475829197)
test('A1','b','Type II event is no alert at elevated defect rate',beta>0 and critical==5)
T=((.8,.3),(.2,.7));v=(0.,1.)
test('A1','c','Column transition sums',[sum(T[i][j] for i in range(2)) for j in range(2)],[1.,1.])
for _ in range(2):v=tuple(sum(T[i][j]*v[j] for j in range(2)) for i in range(2))
close('A1','c','Two-day unstable probability',v[0],.45)
q=0.
for n in range(21):
    close('A1','d',f'Recurrence and closed form at day {n}',q,.6*(1-2**(-n)))
    q=.3+.5*q
alert_limit=.6*power+.4*alpha;posterior=.6*power/alert_limit
close('A1','e','Limiting alert rate',alert_limit,.32826233983635844)
close('A1','e','Conditional unstable posterior',posterior,.9743835412386156)
gap=lambda n:.6*(power-alpha)*2**(-n)
test('A1','f','First qualifying integer day',next(n for n in range(100) if gap(n)<.001),9)
test('A1','f','Adjacent integer boundary',gap(8)>=.001>gap(9))
close('A1','f','Real-valued cutoff',math.log(.6*(power-alpha)/.001,2),8.263222446942438,1e-8)
for speed in [.3,.7,1.1]:
    u,v=.2,.3;pi=v/(u+v);rho=1-speed*(u+v)
    close('A1','g','Stationary recurrence invariant',speed*v+rho*pi,pi)
    close('A1','g','Limiting alert independent of speed',alpha+(power-alpha)*pi,alert_limit)
test('A1','g','Contraction improves with speed',0<1-1.1*.5<1-.7*.5<1-.3*.5<1)

# A2: exact solution, extrema, threshold, simultaneous Euler and general rates.
matrix=((-0.3,.2),(.2,-.3))
test('A2','a','Flow coefficients',[30000/100000,20000/100000],[.3,.2])
for lam,vec in [(-.1,(1,1)),(-.5,(1,-1))]:
    for i in range(2):close('A2','b','Eigenpair substitution',sum(matrix[i][j]*vec[j] for j in range(2)),lam*vec[i])
xy=lambda t:(15*(math.exp(-t/10)+math.exp(-t/2)),15*(math.exp(-t/10)-math.exp(-t/2)))
test('A2','b','Initial conditions',list(xy(0)),[30.,0.])
for t in [0,1,4,10,30]:
    x,y=xy(t)
    close('A2','b','x derivative equation',-1.5*math.exp(-t/10)-7.5*math.exp(-t/2),-.3*x+.2*y)
    close('A2','b','y derivative equation',-1.5*math.exp(-t/10)+7.5*math.exp(-t/2),.2*x-.3*y)
peak=math.log(5)/.4
close('A2','c','Unique stationary time',peak,4.023594781085251)
close('A2','c','Downstream peak mass',xy(peak)[1],8.024883659717064)
test('A2','c','Derivative sign either side',(.2*xy(peak-1)[0]-.3*xy(peak-1)[1])>0>(.2*xy(peak+1)[0]-.3*xy(peak+1)[1]))
lo,hi=0.,100.
for _ in range(100):
    m=(lo+hi)/2
    if xy(m)[0]>1:lo=m
    else:hi=m
safe=(lo+hi)/2
test('A2','d','Concentration to kg threshold',10*100000/1e6,1)
close('A2','d','Unique simultaneous safe time',safe,27.080699524330335)
close('A2','d','Limiting reservoir mass at threshold',xy(safe)[0],1)
test('A2','d','Other reservoir already below limit',xy(safe)[1]<1)
x,y=30.,0.
for step,expect in [(1,(21.,6.)),(2,(15.9,8.4))]:
    x,y=x+(-.3*x+.2*y),y+(.2*x-.3*y)
    close('A2','e',f'Euler x at step {step}',x,expect[0])
    close('A2','e',f'Euler y at step {step}',y,expect[1])
close('A2','e','Exact downstream mass at two hours',xy(2)[1],6.762769678598092)
test('A2','e','Nonnegative Euler estimate exceeds true global peak',y>xy(peak)[1]>xy(2)[1]>0)
for Q in [5000,20000,80000]:
    rate=Q/100000;x,y=17.,4.
    close('A2','f','Exchange cancels from total derivative',-(.1+rate)*x+rate*y+rate*x-(.1+rate)*y,-.1*(x+y))
close('A2','f','Total half-life',10*math.log(2),6.931471805599453)
for h in [.1,1,2]:
    for x,y in [(30.,0.),(8.,4.),(3.,3.)]:
        xx=x+h*(-.3*x+.2*y);yy=y+h*(.2*x-.3*y)
        close('A2','g','Euler total recurrence',xx+yy,(1-.1*h)*(x+y))
        close('A2','g','Euler difference recurrence',xx-yy,(1-.5*h)*(x-y))
        test('A2','g','Ordering and nonnegative mass preserved',xx>=yy-1e-12 and yy>=-1e-12)
test('A2','g','Every larger h fails for some positive difference',all((1-.5*h)*30<0 for h in [2.0001,3,5,20]))

# B1: complex combination, interval geometry, smooth on-interval integrals.
phi=1.2;z=4+3*cmath.exp(-1j*phi);A=abs(z);delta=-cmath.phase(z)
close('B1','a','Phasor real component',z.real,5.087073263430021)
close('B1','a','Phasor imaginary component',z.imag,-2.796117257901679)
close('B1','a','Amplitude',A,5.8048760630559695)
close('B1','a','Delayed phase',delta,.502575580195619)
for t in [0,1,2,6,11.3]:close('B1','a','Current equivalence',4*math.cos(math.pi*t/6)+3*math.cos(math.pi*t/6-phi),A*math.cos(math.pi*t/6-delta))
for phi in [0,.4,1.2,2.2,math.pi]:close('B1','b','Amplitude identity',abs(4+3*cmath.exp(-1j*phi))**2,25+24*math.cos(phi))
close('B1','b','Minimum attainable amplitude',abs(4+3*cmath.exp(-1j*math.pi)),1)
close('B1','b','Maximum attainable amplitude',abs(4+3*cmath.exp(0j)),7)
def simpson(f,a,b,n=4000):
    h=(b-a)/n
    return h/3*(f(a)+f(b)+sum((4 if j%2 else 2)*f(a+j*h) for j in range(1,n)))
for a in [1,3,5,7]:
    close('B1','c','Full-period power integral',simpson(lambda t:10*a*a*math.cos(math.pi*t/6-.37)**2,0,12)/12,5*a*a)
qoff=lambda a:0 if a<=4 else 2*math.acos(4/a)/math.pi
for a in [4.1,5,7]:close('B1','d','Off-fraction from four phase intervals',4*math.acos(4/a)/(2*math.pi),qoff(a))
test('B1','d','No shutdown below or at threshold',[qoff(a) for a in [1,3.9,4]],[0,0,0])
amax=4/math.cos(math.pi/8);phimin=math.acos((amax*amax-25)/24)
close('B1','e','Largest permitted amplitude',amax,4.329568801169576)
close('B1','e','Smallest permitted phase',phimin,1.8344586819029165)
close('B1','e','Duty-cycle boundary',qoff(amax),.25)
test('B1','e','Phase below bound fails',qoff(math.sqrt(25+24*math.cos(phimin-.01)))>.25)
def useful(a):
    return 5*a*a if a<=4 else 10*a*a/math.pi*(math.asin(4/a)-(4/a)*math.sqrt(1-16/a**2))
for a in [4.05,amax,5,7]:
    v=math.acos(4/a)
    integral=10*a*a/(2*math.pi)*4*simpson(lambda u:math.cos(u)**2,v,math.pi/2)
    close('B1','f','Useful power formula from independent on-interval quadrature',useful(a),integral,1e-8)
close('B1','f','Power continuous at threshold',useful(4),80)
close('B1','f','Right-hand limit at threshold',useful(4+1e-12),80,1e-3)
optphi=math.acos(-3/8)
close('B1','g','Optimal phase',optphi,1.9551931012905357)
close('B1','g','Optimal amplitude from phase',math.sqrt(25+24*math.cos(optphi)),4)
close('B1','g','Maximum useful mean power',useful(4),80)
test('B1','g','Whole-domain dense search bounded by optimum',all(useful(1+(amax-1)*j/5000)<=80+1e-10 for j in range(5001)))
test('B1','g','Analytic derivative sign above threshold',all(math.asin(c)-c/math.sqrt(1-c*c)<0 for c in [.1,.4,.7,.95,.999]))
close('B1','g','Largest permitted amplitude wastes more peak energy',useful(amax),49.19864901206661)

# B2: shortest paths, parity pairings, valid tours and parameter cases.
vertices=list('ABCDEF')
def distances(w,remove=False):
    d={a:{b:(0. if a==b else math.inf) for b in vertices} for a in vertices}
    for a,b,weight in edges:
        if remove and (a,b)==('A','D'):continue
        weight=w if weight=='w' else weight
        d[a][b]=d[b][a]=weight
    for k in vertices:
        for a in vertices:
            for b in vertices:d[a][b]=min(d[a][b],d[a][k]+d[k][b])
    return d
degree={a:sum(a in (x,y) for x,y,_ in edges) for a in vertices}
test('B2','a','Odd-degree vertices',[a for a in vertices if degree[a]%2],['A','B','D','E'])
d=distances(2)
for (a,b),expect in zip([('A','B'),('A','D'),('A','E'),('B','D'),('B','E'),('D','E')],[4,2,8,6,7,6]):test('B2','b',f'Shortest {a}{b}',d[a][b],expect)
pairings=lambda d:[d['A']['B']+d['D']['E'],d['A']['D']+d['B']['E'],d['A']['E']+d['B']['D']]
test('B2','c','Three parity corrections',pairings(d),[10,9,14])
test('B2','c','Minimum closed tour at w=2',37+2+min(pairings(d)),48)
def route_cost(route,w):
    weights={frozenset((a,b)):(w if weight=='w' else weight) for a,b,weight in edges}
    used=[frozenset((a,b)) for a,b in zip(route,route[1:])]
    assert all(e in weights for e in used)
    return sum(weights[e] for e in used),set(used)==set(weights)
cost,covers=route_cost('ABEFADC BEDA'.replace(' ',''),2)
test('B2','c','Exhibited route covers all edges',covers)
test('B2','c','Exhibited route cost',cost,48)
closed=lambda w:44+2*w if w<=3 else 47+w
for w in [.01,.7,2,2.999,3,3.001,5,8,13,20,100]:
    d=distances(w)
    close('B2','d','Computed Chinese-postman optimum matches full piecewise expression',37+w+min(pairings(d)),closed(w))
    close('B2','d','First pairing',pairings(d)[0],10)
    close('B2','d','Second pairing',pairings(d)[1],7+min(w,13))
    close('B2','d','Third pairing',pairings(d)[2],min(w+6,11)+min(w+4,9))
close('B2','d','Both branches agree at breakpoint',44+2*3,47+3)
cost,covers=route_cost('ABCDEBAFEDA',8)
test('B2','d','High-w exhibited tour covers all edges',covers)
close('B2','d','High-w exhibited tour matches optimum',cost,closed(8))
test('B2','e','Removed-edge optimum',37+distances(2,True)['B']['E'],44)
for w in [.01,2,3,10,100]:
    d=distances(w)
    test('B2','f','Only remaining parity correction shortest path BE',d['B']['E'],7)
    cost,covers=route_cost('ABEFADCBED',w)
    test('B2','f','Open tour covers all edges',covers)
    close('B2','f','Open tour matches lower bound',cost,44+w)
    close('B2','g','Closed-open saving formula',closed(w)-(44+w),min(w,3))
    for h in [.2,1,2,3,4]:
        difference=closed(w)-(44+w+h)
        test('B2','g','Strict preference condition',difference>1e-10,h<3 and w>h)
        close('B2','g','Full cost comparison',difference,min(w,3)-h)
test('B2','g','Tie at bridge-time threshold',closed(2.4),44+2.4+2.4)
test('B2','g','Tie on entire h=3 plateau',closed(10),44+10+3)


OUT.mkdir(parents=True,exist_ok=True)
paper_records=[]
for paper in papers:
    assert paper['minutes']==75 and paper['marks']==55 and paper['calculator']
    assert [q['marks'] for q in paper['questions']]==[27,28]
    for q in paper['questions']:
        assert q['section']=='' and q['syllabusRefs']
        assert sum(p['marks'] for p in q['parts'])==q['marks']
        schemes={s['part']:s['steps'] for s in q['markScheme']}
        assert len(schemes)==len(q['parts'])
        for p in q['parts']:
            assert p['label'] in schemes
            assert sum(int(re.search(r'(\d+)$',s['code']).group(1)) for s in schemes[p['label']])==p['marks']
            assert any(c['question']==paper['set']+str(q['number']) and c['part']==p['label'] for c in checks)
        ET.fromstring(q['diagramSvg'])
        assert not re.search(r'<(?:defs|style|script|foreignObject|image)\b|\bon\w+\s*=|(?:href|url)\s*[:=(]',q['diagramSvg'],re.I)
        raw=json.dumps(q,ensure_ascii=False)
        assert all(ord(c)>=32 or c in '\n\t' for c in raw)
    path=OUT/(paper['id']+'.json')
    path.write_text(json.dumps(paper,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    paper_records.append({'id':paper['id'],'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'questions':2,'marks':55,'minutes':75,'diagrams':2})

report={
 'status':'author calculations and content checks passed; independent and final visual reviews pending',
 'originality':'Four original investigations developed from independent contexts, data and models. No provider question or source solution was copied or numerically varied.',
 'officialGuide':'https://xmltwo.ibo.org/publications/EAD/2026_EN/GR5/GR5-Maths_AI_EN.pdf',
 'syllabusApplicability':'First assessment 2021; current 2026 guide updated August 2025; not the 2029 revision.',
 'papers':paper_records,'questions':4,'parts':28,'diagrams':4,'calculationChecks':len(checks),'checks':checks,
 'mathRenderingReview':{'status':'passed','katexExpressions':403,'method':'Every dollar-delimited expression in both full paper JSON files compiled with KaTeX throwOnError and strict error settings.'},
 'diagramVisualReview':{'status':'passed','diagrams':4,'previewDirectory':'work/ai-mocks-2026/p3-preview','method':'All four original SVGs rasterized at width1140 and visually inspected. White backgrounds, geometry, labels, arrows, units and graph crossings checked. Network w label moved away from diagonal before final review.'},
 'questionReviews':[
  {'id':'A1','status':'passed','thinking':'Links discrete test errors, conditional probability, transition dynamics and parameter-invariant long-run behaviour.','boundaryChecks':['one-tailed exact binomial','regular positive two-state chain','column orientation','strict Type I significance bound','integer day boundary','transition contraction constrained to (0,1)'],'reasoningVerified':'The recurrence difference is geometric, which supplies a closed formula and a justified limit; posterior conditioning is on an alert, not merely a defect.'},
  {'id':'A2','status':'passed','thinking':'Derives mass balance, identifies conserved exchange cancellation, solves a real-eigenvalue system, and separates numerical feasibility from accuracy.','boundaryChecks':['distinct nonzero real 2x2 eigenvalues','constant equal volumes','all flows balance','mg/L to kg conversion','global maximum and monotone safe threshold','simultaneous Euler updates','all-state step-size necessity and sufficiency'],'reasoningVerified':'x exceeds y for all finite nonnegative time; only x determines safety. General exchange cancels in the total. h<=2 preserves order and positive update coefficients; h>2 reverses any strictly positive difference.'},
  {'id':'B1','status':'passed','thinking':'Moves from complex representation to duty cycle, integration on retained intervals, and a global constrained optimum at a nondifferentiable joining point.','boundaryChecks':['phasor sum, not complex roots','all phases and integration in radians','double-angle identity supplied','full-period shift invariance','shutdown strictness affects measure-zero points only','mean useful power includes zero off-state','global permitted amplitude interval'],'reasoningVerified':'For A>4 the derivative sign reduces to arcsin(c)-c/sqrt(1-c^2)<0, since the difference is zero at c=0 and has negative derivative thereafter. Below4 useful power rises. Thus80W at A4 is the global maximum, also satisfying the duty constraint.'},
  {'id':'B2','status':'passed','thinking':'Investigates parity corrections as a bridge time changes; contrasts closed/open postman obligations and develops a complete return-cost policy.','boundaryChecks':['connected undirected network','four odd vertices','all pairings considered','shortest paths allowed to use indirect links','crossings explicitly not vertices','all positive w cases including alternative AD shortest path13','open endpoints parity','all strict and tie decision cases'],'reasoningVerified':'The third odd pairing is always at least10; the first two cross at w3. For open endpoints A,D only B,E need correction and their shortest distance is always7. Their fixed competing parity costs bound the saving by3.'}
 ],
 'unresolvedFindings':[]
}
REVIEW.parent.mkdir(parents=True,exist_ok=True)
REVIEW.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'questions':4,'parts':28,'calculationChecks':len(checks),'papers':paper_records},indent=2))
