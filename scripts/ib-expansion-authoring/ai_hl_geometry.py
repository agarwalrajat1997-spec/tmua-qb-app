from ai_hl_common import *
import itertools
def mst(edges,vertices):
 parent={x:x for x in vertices}
 def find(x):
  while parent[x]!=x:x=parent[x]
  return x
 result=[]
 for a,b,w in sorted(edges,key=lambda e:(e[2],e[0],e[1])):
  if find(a)!=find(b):parent[find(a)]=find(b);result.append((a,b,w))
 return result
def distances(edges,vertices):
 d={(a,b):(0 if a==b else math.inf) for a in vertices for b in vertices}
 for a,b,w in edges:d[a,b]=d[b,a]=w
 for k in vertices:
  for a in vertices:
   for b in vertices:d[a,b]=min(d[a,b],d[a,k]+d[k,b])
 return d
def build():
 for v in range(4):
  r=4+.5*v;theta=1.2+.1*v
  add('gt',1,v,'An irrigated circular sector','Radians and sector geometry','3.7',f'A sprinkler covers a sector of radius {r:g} m and angle {theta:g} radians.',[
   P('Find the arc length and sector area.',M('Use $s=r\\theta$.'),A(f'Arc length {sf(r*theta)} m.'),M('Use $A=r^2\\theta/2$.'),A(f'Area {sf(r*r*theta/2)} square metres.')),
   P('Find the perimeter of the sector and the area not irrigated in a full circle of this radius.',A(f'Perimeter {sf(2*r+r*theta)} m.'),M('Subtract the sector area from $\\pi r^2$.'),A(f'Uncovered area {sf(math.pi*r*r-r*r*theta/2)} square metres.'))],{'arc':r*theta,'sectorArea':r*r*theta/2,'perimeter':2*r+r*theta,'uncoveredArea':math.pi*r*r-r*r*theta/2})
  c=.2+.1*v;a=math.asin(c);sol=[a,math.pi-a,a+2*math.pi,3*math.pi-a]
  add('gt',2,v,'All positions of a rotating marker','Unit-circle trigonometric solutions','3.8',f'A rotating marker satisfies $\\sin\\theta={c:g}$ for $0\\leq\\theta\\leq4\\pi$.',[
   P('Find all solutions in radians.',M('Find the principal inverse-sine angle.'),A(f'Principal angle {sf(a)}.'),M('Include the supplementary angle and both corresponding angles one revolution later.'),A(f'Solutions $[{", ".join(sf(x) for x in sol)}]$.')),
   P('For these solutions, state the possible cosine values and justify the signs.',M('Use $\\cos^2\\theta=1-\\sin^2\\theta$.'),A(f'$\\cos\\theta=\\pm{sf(math.sqrt(1-c*c))}$.'),R('Cosine is positive in quadrant I and negative in quadrant II of each revolution.'))],{'solutions':sol,'cosMagnitude':math.sqrt(1-c*c)})
  a=8+v;b=12+v;C=65+v*5;side=math.sqrt(a*a+b*b-2*a*b*math.cos(math.radians(C)));area=.5*a*b*math.sin(math.radians(C))
  add('gt',3,v,'Surveying a triangular reserve','Triangle modelling','3.3',f'Two boundaries from a survey point have lengths {a} km and {b} km with included angle {C} degrees.',[
   P('Find the third boundary length and the reserve area.',M('Apply the cosine rule with the included angle.'),A(f'Third side {sf(side)} km.'),M('Use half the product of the two sides and sine of their included angle.'),A(f'Area {sf(area)} square kilometres.')),
   P('The included angle has uncertainty $\\pm1$ degree. Find an interval of possible third-side lengths.',M('Evaluate the cosine-rule expression at both angular endpoints.'),A(f'Interval $[{sf(math.sqrt(a*a+b*b-2*a*b*math.cos(math.radians(C-1))))},{sf(math.sqrt(a*a+b*b-2*a*b*math.cos(math.radians(C+1))))}]$ km.'),R('On this angular interval the side length increases with the included angle.'))],{'thirdSide':side,'area':area,'lowerSide':math.sqrt(a*a+b*b-2*a*b*math.cos(math.radians(C-1))),'upperSide':math.sqrt(a*a+b*b-2*a*b*math.cos(math.radians(C+1)))})
  s=1+v;T=np.array([[0,-1],[1,0]]);t=np.array([s,2]);p=np.array([2,1]);q=T@p+t;diag=plot(points=[(2,1,'P'),(4,1,'Q'),(2,3,'R')],xmin=0,xmax=6,ymin=0,ymax=5,equal=True)
  add('gt',4,v,'Mapping a triangular motif','Affine matrix transformations','3.9',f'The diagram shows triangle PQR. The mapping is $x\\mapsto {mat(T.tolist())}x+{vec(t.tolist())}$.',[
   P('Describe the two operations represented by this mapping.',R('A rotation of 90 degrees anticlockwise about the origin.'),R(f'Followed by translation by $({s},2)$.')),
   P('Find the image coordinates of all three vertices.',M('Multiply each original position vector by the matrix, then add the translation.'),A(f'$P^\\prime=({s-1},4)$.'),A(f'$Q^\\prime=({s-1},6)$ and $R^\\prime=({s-3},4)$.')),
   P('Find the original and transformed areas, explaining the relationship.',A('Original area 2 square units.'),R('Rotation and translation preserve area.'),A('Transformed area 2 square units.'))],{'imagePx':int(q[0]),'imagePy':int(q[1]),'area':2},diagram=diag)
  k=2+v;S=np.array([[k,0],[0,1]]);R0=np.array([[0,-1],[1,0]]);p=np.array([2,3]);rs=R0@S@p;sr=S@R0@p
  add('gt',5,v,'Order in a map transformation','Composition of transformation matrices','3.9',f'A horizontal stretch has matrix $S={mat(S.tolist())}$ and an anticlockwise quarter-turn has matrix $R={mat(R0.tolist())}$. Let $P=(2,3)$.',[
   P('Find the combined matrix for S followed by R.',M('Matrices act right to left, so the combined matrix is $RS$.'),A(f'$RS={mat((R0@S).tolist())}$.')),
   P('Find the images of P under S then R, and under R then S.',M('Evaluate the two ordered matrix products on the point vector.'),A(f'S then R gives $({rs[0]},{rs[1]})$.'),A(f'R then S gives $({sr[0]},{sr[1]})$.')),
   P('Explain whether these transformations commute.',R('They do not commute because the two products give different images of P.'),R('The stretch acts along a fixed horizontal direction, which the rotation changes.'))],{'RSx':int(rs[0]),'RSy':int(rs[1]),'SRx':int(sr[0]),'SRy':int(sr[1])})
  a=2+v;T=[[a,1],[0,2]];area=5
  add('gt',6,v,'Area under a digital map','Determinant and area scale','3.9',f'A region of area 5 square units is transformed by $A={mat(T)}$. The image is then translated by $(4,-2)$.',[
   P('Calculate the area of the final image.',M('The absolute determinant is the area multiplier.'),A(f'$|\\det A|={2*a}$.'),A(f'Final area {10*a} square units.')),
   P('Explain the role of the translation in this calculation.',R('Translation moves every point by the same displacement.'),R('It does not alter lengths or area.')),
   P('Find the original point whose transformed and translated position is $(12,6)$.',M('Subtract the translation to obtain $(8,8)$.'),A('$y=4$.'),A(f'$x=4/{a}={sf(4/a)}$.'))],{'imageArea':10*a,'originalX':4/a,'originalY':4})
  r=.4+.02*v;copies=3;areaRatio=copies*r*r;total=100/(1-areaRatio)
  add('gt',7,v,'A recursive habitat design','Fractal transformations investigation','3.9',f'A habitat diagram starts with a region of area 100. At each stage each new region produces three similar regions with length scale factor {r:g}. Assume all regions created across the generations are mutually nonoverlapping. Only newly created regions generate the next stage.',[
   P('Find the area multiplier from one generation to the next.',M('Each similar copy has area multiplier $r^2$.'),A(f'Three copies give ratio {sf(areaRatio)}.')),
   P('Find the new area at generation 4, taking the original region as generation 0.',M(f'$A_n=100({areaRatio:g})^n$.'),A(f'$A_4={sf(100*areaRatio**4)}$.')),
   P('Find the total area of all generations in the idealized design.',M('Recognize a geometric series with ratio below one.'),M('$S_\\infty=100/(1-3r^2)$.'),A(f'Total area {sf(total)}.')),
   P('Find the range of positive length scale factors giving a finite total, and state whether there is a largest allowable value.',M('Convergence requires $3r^2<1$ for positive scale factors.'),A(f'$0<r<1/\\sqrt3$, with upper bound approximately {sf(1/math.sqrt(3))}.'),R('There is no largest allowable value: the upper bound is excluded because at equality each generation adds the same positive area and the total diverges.')),
   P('Give two physical limitations of the infinite design.',R('Finite manufacturing precision prevents arbitrarily small copies.'),R('The copies may overlap or encounter finite boundary space, invalidating addition of their areas.'))],{'generationRatio':areaRatio,'generation4':100*areaRatio**4,'totalArea':total,'criticalLengthScale':1/math.sqrt(3)},scope='3.9 fractal transformation linked with 1.11 infinite geometric series')
  a=np.array([2+v,-1,3]);b=np.array([-1,4+v,5]);d=b-a;mag=np.linalg.norm(d)
  add('gt',8,v,'Drone displacement','Three-dimensional vectors','3.10',f'A drone moves from $A={tuple(float(z) for z in a)}$ to $B={tuple(float(z) for z in b)}$, with coordinates in metres.',[
   P('Find the displacement and distance travelled on a straight flight.',M('Subtract the initial position vector from the final vector.'),A(f'$\\overrightarrow{{AB}}={vec(d.tolist())}$.'),M('Use the Euclidean norm.'),A(f'Distance {sf(mag)} m.')),
   P('Find a unit vector in the direction of flight.',M('Divide the displacement by its magnitude.'),A(f'Unit vector ${vec([sf(z) for z in d/mag])}$.')),
   P('Explain why the magnitude of the displacement need not equal distance on a curved flight.',R('The displacement depends only on endpoints; a curved route can have a greater path length.'))],{'distance':mag,'unitVector':(d/mag).tolist()})
  a=np.array([1,2+v,3]);d=np.array([2,-1,4]);p=a+3*d
  add('gt',9,v,'A tunnel centre line','Vector and parametric line forms','3.11',f'A tunnel follows $r={vec(a.tolist())}+\\lambda{vec(d.tolist())}$, with coordinates in metres.',[
   P('Write parametric equations and find the point for $\\lambda=3$.',A('$x=1+2\\lambda$.'),A(f'$y={2+v}-\\lambda$, $z=3+4\\lambda$.'),A(f'Point ${tuple(float(z) for z in p)}$.')),
   P(f'Determine whether $Q={tuple(float(z) for z in p+np.array([0,1,0]))}$ lies on the line.',M('The x-coordinate forces $\\lambda=3$.'),R(f'The corresponding y-coordinate must be {p[1]}, which differs from Q.'),A('Q does not lie on the line.')),
   P('Explain why $\\lambda$ need not represent elapsed time.',R('A line parameter has no time interpretation unless a speed and time origin are specified.'))],{'pointAt3':p.tolist()})
  t=3+v;Apos=np.array([0.,2.]);va=np.array([2.,1.]);vb=np.array([-1.,2.]);Bpos=Apos+t*(va-vb)
  add('gt',10,v,'Meeting of two service boats','Vector constant-velocity motion','3.12',f'Boat A has position $r_A(t)={vec(Apos.tolist())}+t{vec(va.tolist())}$ and boat B has $r_B(t)={vec(Bpos.tolist())}+t{vec(vb.tolist())}$, with distances in km and time in hours, $t\\geq0$.',[
   P('Find when and where the boats meet.',M('Equate the two position vectors at the same time.'),M('Solve the component equations and check they give the same time.'),A(f'$t={t}$ hours.'),A(f'Meeting point ${tuple(float(z) for z in Apos+t*va)}$ km.')),
   P('Find each boat\'s speed.',M('Take the magnitude of each velocity vector.'),A(f'Both speeds are $\\sqrt5={sf(math.sqrt(5))}$ km per hour.')),
   P('Explain why intersection of two route lines alone does not establish a collision.',R('The boats must reach the intersection at the same nonnegative time.'),R('A shared location at different parameter times is not a collision.'))],{'meetingTime':t,'meetingPoint':(Apos+t*va).tolist(),'speed':math.sqrt(5)})
  b=np.array([12.+v,8.]);u=np.array([-2.,-1.]);t=-float(b@u)/float(u@u);closest=b+t*u;dist=np.linalg.norm(closest)
  add('gt',11,v,'Closest approach of aircraft','Relative motion investigation','3.12',f'The position of aircraft B relative to A is $d(t)={vec(b.tolist())}+t{vec(u.tolist())}$ km, for $0\\leq t\\leq10$ minutes.',[
   P('Write the squared separation as a quadratic in $t$.',M('Take $d(t)\\cdot d(t)$.'),A(f'$D^2(t)=5t^2+({2*float(b@u):g})t+{float(b@b):g}$.')),
   P('Find the time and value of the minimum separation on the stated interval.',M('Minimize the quadratic or use its vertex.'),A(f'$t={sf(t)}$ minutes, inside the interval.'),M('Evaluate the separation, not just its square.'),A(f'Minimum separation {sf(dist)} km.')),
   P('A safety rule requires separation of at least 2 km. Assess this flight plan.',R(f'The minimum {sf(dist)} km is {"below" if dist<2 else "above"} 2 km.'),A('The plan '+('breaches' if dist<2 else 'satisfies')+' the modelled separation rule.')),
   P('State three modelling assumptions that should be checked before using this conclusion, and explain why uncertainty matters for a near-threshold decision.',R('Both velocity vectors must remain constant over the interval.'),R('Position and timing measurements must be sufficiently accurate.'),R('If altitude is omitted, the two-dimensional rule must be the appropriate safety criterion.'),R('Uncertainty in these inputs can alter a near-threshold conclusion.'))],{'closestTime':t,'minimumDistance':dist,'minimumSquaredDistance':dist*dist})
  a=np.array([2+v,1,3]);b=np.array([1,4,-1]);dot=int(a@b);angle=math.degrees(math.acos(dot/(np.linalg.norm(a)*np.linalg.norm(b))))
  add('gt',12,v,'Angles between support members','Scalar product','3.13',f'Two support directions are $a={vec(a.tolist())}$ and $b={vec(b.tolist())}$.',[
   P('Calculate $a\\cdot b$ and the angle between the directed vectors.',A(f'$a\\cdot b={dot}$.'),M('Use $\\cos\\theta=(a\\cdot b)/(|a||b|)$.'),A(f'$\\theta={sf(angle)}$ degrees.')),
   P('Find the acute angle between the corresponding undirected lines.',M('Use the smaller of $\\theta$ and $180^\\circ-\\theta$.'),A(f'Acute line angle {sf(min(angle,180-angle))} degrees.')),
   P('Find the scalar projection of $a$ in the direction of $b$.',M('Divide the dot product by $|b|$.'),A(f'Scalar projection {sf(dot/np.linalg.norm(b))}.'))],{'dotProduct':dot,'vectorAngleDegrees':angle,'acuteLineAngle':min(angle,180-angle),'scalarProjection':dot/np.linalg.norm(b)})
  a=np.array([2+v,1,0]);b=np.array([0,2,3]);cross=np.cross(a,b);area=np.linalg.norm(cross)
  add('gt',13,v,'A triangular solar panel','Vector product and area','3.13',f'Two adjacent edges from a panel vertex are $a={vec(a.tolist())}$ and $b={vec(b.tolist())}$ metres.',[
   P('Find $a\\times b$ and a unit normal to the panel.',M('Calculate the three signed components of the vector product.'),A(f'$a\\times b={vec(cross.tolist())}$.'),M('Divide by its magnitude.'),A(f'A unit normal is ${vec([sf(z) for z in cross/area])}$; the negative is also acceptable.')),
   P('Find the triangular panel area.',M('A triangle has half the parallelogram area $|a\\times b|$.'),A(f'Area {sf(area/2)} square metres.')),
   P('Verify that your normal is perpendicular to both edges.',M('Evaluate its dot products with both edge vectors.'),A('Both dot products are zero.'))],{'crossProduct':cross.tolist(),'triangleArea':area/2})
  p=np.array([3+v,4,5]);a=p-2*np.array([1,2,1]);b=p-3*np.array([2,-1,1]);u=[1,2,1];w=[2,-1,1]
  add('gt',14,v,'Intersecting pipeline routes','Intersection of vector lines','3.11',f'Two pipeline centre lines are $r={vec(a.tolist())}+\\lambda{vec(u)}$ and $r={vec(b.tolist())}+\\mu{vec(w)}$.',[
   P('Find their intersection, checking all three coordinates.',M('Equate the x and y component equations.'),A('$\\lambda=2$, $\\mu=3$.'),M('Substitute both parameter values into the z-components.'),A(f'Both give $z=5$, so the intersection is ${tuple(float(z) for z in p)}$.')),
   P('Explain whether an intersection of infinite lines guarantees the physical segments meet.',R('No; the intersection parameters must lie in the ranges defining the physical segments.'),R('The segment parameter intervals must therefore be checked.'))],{'lambda':2,'mu':3,'intersection':p.tolist()})
  edges=[('A','B',3+v),('B','C',4+v),('C','D',5+v),('D','E',6+v),('E','A',7+v),('A','C',8+v)];degrees={'A':3,'B':2,'C':3,'D':2,'E':2}
  add('gt',15,v,'Inspection route feasibility','Graph degrees and Euler trails','3.16','The diagram represents an undirected connected inspection network. Edge labels are distances in km.',[
   P('State the degree of every vertex and identify the odd vertices.',A('Degrees A=3, B=2, C=3, D=2, E=2.'),A('The odd vertices are A and C.')),
   P('Determine whether an Euler circuit or an Euler trail exists.',R('A connected graph has an Euler circuit only when every degree is even.'),A('There is no Euler circuit.'),R('Exactly two vertices are odd, so an Euler trail exists starting at one of A,C and ending at the other.')),
   P('Give one Euler trail and calculate its length.',A('One trail is A-B-C-D-E-A-C.'),M('Sum all six edge lengths exactly once.'),A(f'Length {sum(e[2] for e in edges)} km.'))],{'degrees':degrees,'trailLength':sum(e[2] for e in edges)},diagram=network(edges))
  A0=np.array([[0,1,1,0],[1,0,1,1],[1,1,0,1],[0,1,1,0]]);k=3+v;n=int(np.linalg.matrix_power(A0,k)[0,3]);two=int((A0@A0)[0,3])
  add('gt',16,v,'Counting transfers in a network','Adjacency matrix walks','3.15',f'An undirected transit graph has adjacency matrix $A={mat(A0.tolist())}$ in vertex order A,B,C,D.',[
   P('Find the number of length-2 walks from A to D and list them.',M('Read the A,D entry of $A^2$.'),A(f'{two} walks: A-B-D and A-C-D.')),
   P(f'Find the number of length-{k} walks from A to D.',M(f'Compute $A^{k}$ using matrix multiplication.'),A(f'The A,D entry is {n}.')),
   P('Explain why these walks need not be paths.',R('Walks can repeat vertices or edges.'),R('A path does not repeat a vertex.')),
   P('State whether a length-1 walk from A to D exists.',A('No; the A,D entry of the original adjacency matrix is zero.'))],{'length2Walks':two,'lengthK':k,'walkCount':n})
  edges=[('A','B',1),('A','C',1),('B','C',1),('B','D',1),('C','D',1)];T=np.array([[0,1/3,1/3,0],[1/2,0,1/3,1/2],[1/2,1/3,0,1/2],[0,1/3,1/3,0]]);k=2+v;p=float(np.linalg.matrix_power(T,k)[3,0])
  add('gt',17,v,'Random moves through a graph','Graph transition matrix','3.15',f'A walker starts at A and at each step chooses uniformly from the adjacent vertices shown. The graph is undirected; all drawn edge labels are 1. Use vertex order A,B,C,D.',[
   P('Construct a column transition matrix.',M('For each source vertex, divide one equally among its neighbours.'),A(f'$T={mat([["0","1/3","1/3","0"],["1/2","0","1/3","1/2"],["1/2","1/3","0","1/2"],["0","1/3","1/3","0"]])}$.'),R('Every column sums to one.')),
   P(f'Find the probability of being at D after {k} steps.',M(f'Use the D,A entry of $T^{k}$.'),A(f'Probability {sf(p)}.')),
   P('Explain why counting walks and dividing by one common power of a degree does not work for this graph.',R('The vertex degrees are not all equal.'),R('Different walks can therefore have different probabilities.'))],{'steps':k,'probabilityAtD':p},diagram=network(edges,{'A':(80,190),'B':(280,70),'C':(280,300),'D':(510,190)}))
  edges=[('A','B',2+v),('B','C',4+v),('C','D',3+v),('D','E',5+v),('E','A',9+v),('B','E',7+v),('A','C',8+v)];tree=mst(edges,'ABCDE');weight=sum(x[2] for x in tree)
  add('gt',18,v,'Connecting field stations','Kruskal network investigation','3.16','The network shows possible cable links between five field stations. Weights are costs in thousands of currency units.',[
   P('Apply Kruskal\'s algorithm, giving the chosen edges in order.',M('Sort all edges by nondecreasing weight.'),A('Choose AB then CD.'),R('Choose BC to join the two current components without a cycle.'),A('Choose DE to include the fifth vertex.')),
   P('Find the minimum connection cost and explain why four links suffice.',M('Add the selected tree-edge weights.'),A(f'Minimum cost {weight} thousand currency units.'),R('A spanning tree on five vertices has four edges.')),
   P('A new link AC is discounted to cost 1. Find the revised minimum cost.',M('Restart the algorithm using AC as the cheapest link.'),A(f'Revised MST uses AC, AB, CD, DE; cost {1+(2+v)+(3+v)+(5+v)}.')),
   P('State two limitations of using the minimum spanning tree as the final communication design.',R('Removing any tree edge disconnects the network, so it has no route redundancy.'),R('Weights may omit reliability, terrain, capacity or future expansion costs.'),R('The cheapest construction design need not meet the operational requirements.'))],{'mstCost':weight,'discountedCost':1+(2+v)+(3+v)+(5+v)},diagram=network(edges))
  edges=[('A','B',4+v),('A','C',7+v),('A','E',9+v),('B','C',2+v),('B','E',6+v),('C','D',3+v),('D','E',5+v)];tree=mst(edges,'ABCDE');weight=sum(x[2] for x in tree)
  add('gt',19,v,'A fibre network from a depot','Prim network investigation','3.16','Five buildings are to be linked using the network shown. Costs are in thousands. Apply Prim\'s algorithm starting at A.',[
   P('Give the sequence of selected edges and vertices.',M('At each step select the cheapest edge joining the current tree to a new vertex.'),A('First AB, adding B.'),A('Then BC, adding C.'),A('Then CD, adding D; finally DE, adding E.')),
   P('Find the total cost and explain why the unused edge BE is not added.',A(f'Total {weight} thousand.'),R('At the relevant step DE is cheaper than BE.'),R('Adding BE after all vertices are connected would create a cycle.')),
   P('The depot changes from A to E. Explain whether the minimum total cost must change.',R('The minimum spanning-tree problem does not depend on a designated root.'),R('The chosen order may change, but the optimal total cost remains the same.')),
   P('Distinguish this objective from finding shortest routes from the depot to every building.',R('A minimum spanning tree minimizes the sum of selected construction edges.'),R('A shortest-route tree optimizes route distances from a source and can use a different set of edges.'),R('A link with low total construction cost can force a longer depot journey.'))],{'mstCost':weight},diagram=network(edges))
  edges=[('A','B',3+v),('B','C',4+v),('C','D',5+v),('D','E',6+v),('E','A',7+v),('A','C',12+3*v)];d=distances(edges,'ABCDE');total=sum(e[2] for e in edges);extra=d['A','C']
  add('gt',20,v,'A closed road inspection','Chinese postman with two odd vertices','3.16','An inspector starts and finishes at A and must traverse every undirected road in the diagram at least once. Weights are road lengths in km.',[
   P('Identify the odd vertices and explain why extra traversal is necessary.',A('A and C are the odd vertices.'),R('A closed Euler route requires all degrees even.'),R('At least one connecting route between A and C must be duplicated.')),
   P('Find the shortest connecting route between the odd vertices.',M('Compare AC with A-B-C and A-E-D-C.'),A(f'Shortest is A-B-C, length {extra:g} km.')),
   P('Calculate the shortest closed inspection length.',M('Add all original edge lengths once.'),A(f'Original total {total} km.'),M('Add the shortest odd-pair connection length.'),A(f'Closed inspection length {total+extra:g} km.')),
   P('Explain why duplicating the cheapest individual road in the network is not a valid general method.',R('The duplicated roads must change the parity of the odd vertices.'),R('A cheap edge unrelated to that pairing can leave odd degrees unchanged or create other odd vertices.'),R('The chosen duplication must connect the odd pair at minimum total path length.'))],{'edgeTotal':total,'extraDistance':extra,'closedDistance':total+extra},diagram=network(edges))
  # K4 with four odd vertices: use weighted table to avoid crossing-edge label ambiguity.
  edges=[('A','B',4+v),('A','C',7+v),('A','D',9+v),('B','C',3+v),('B','D',8+v),('C','D',5+v)];d=distances(edges,'ABCD');pairs=[(('A','B'),('C','D')),(('A','C'),('B','D')),(('A','D'),('B','C'))];costs=[sum(d[a,b] for a,b in pair) for pair in pairs];total=sum(e[2] for e in edges)
  add('gt',21,v,'Four odd road junctions','Postman pairing investigation','3.16',f'A complete undirected road graph has edges '+', '.join(f'{a}{b}={w}' for a,b,w in edges)+'. All lengths are in km. A closed route must cover every road.',[
   P('State the odd vertices and explain how many pairings need to be compared.',A('All four vertices have degree 3 and are odd.'),R('There are three pairings of four odd vertices.')),
   P('Use shortest-path distances to calculate the cost of each pairing.',M('First replace any direct edge by a shorter available route when appropriate.'),A(f'AB with CD costs {costs[0]:g}.'),A(f'AC with BD costs {costs[1]:g}.'),A(f'AD with BC costs {costs[2]:g}.')),
   P('Find the shortest closed inspection length and justify the pairing.',M(f'The sum of all road lengths is {total}.'),R('Choose the odd-vertex pairing with the least added distance.'),A(f'Minimum length {total+min(costs):g} km.')),
   P('Explain why shortest-path distances, rather than necessarily the direct edges, must be used for pairing.',R('Duplicating an indirect route can be cheaper than duplicating a direct road.'),R('The intermediate vertices gain even degree, so only the route endpoints change parity.'),R('This preserves the required parity correction at minimum added cost.'))],{'pairingCosts':costs,'edgeTotal':total,'minimumClosedLength':total+min(costs)})
  edges=[('A','B',4+v),('A','C',8+v),('A','D',7+v),('B','C',5+v),('B','D',9+v),('C','D',3+v)];d={(a,b):w for a,b,w in edges};d.update({(b,a):w for a,b,w in edges});route=['A','B','C','D','A'];cost=sum(d[a,b] for a,b in zip(route,route[1:]));best=min(sum(d[a,b] for a,b in zip(('A',)+p+('A',),(('A',)+p+('A',))[1:])) for p in itertools.permutations('BCD'))
  add('gt',22,v,'A courier visit cycle','Nearest-neighbour TSP investigation','3.16',f'A courier must visit A,B,C,D once each and return to A. The symmetric direct distances are '+', '.join(f'{a}{b}={w}' for a,b,w in edges)+'.',[
   P('Apply nearest neighbour starting at A and give the tour length.',M('From A choose nearest unvisited B.'),A('From B choose C, then D, and return to A.'),M('Sum AB+BC+CD+DA.'),A(f'Tour length {cost}.')),
   P('Explain why this is an upper bound for the optimal tour.',R('The constructed route is a feasible Hamiltonian cycle.'),R('The optimum cannot be longer than a known feasible route.')),
   P('Check all distinct tours (up to reversal) to find the exact optimum.',M('Compare A-B-C-D-A, A-B-D-C-A, A-C-B-D-A.'),A(f'Lengths {cost}, {d["A","B"]+d["B","D"]+d["D","C"]+d["C","A"]}, {d["A","C"]+d["C","B"]+d["B","D"]+d["D","A"]}.'),A(f'Exact optimum {best}.')),
   P('Give two practical limitations of this routing model.',R('Travel times may depend on direction or traffic.'),R('The route ignores service windows, capacity and time spent at stops.'),R('These constraints can make a distance-optimal tour impractical.'))],{'nearestNeighbourCost':cost,'exactOptimum':best})
  edges=[('A','B',6+v),('A','C',9+v),('A','D',7+v),('B','C',4+v),('B','D',8+v),('C','D',5+v)];tree=mst([e for e in edges if 'A' not in e[:2]],'BCD');bound=sum(e[2] for e in tree)+sorted(w for a,b,w in edges if a=='A')[:2][0]+sorted(w for a,b,w in edges if a=='A')[:2][1]
  add('gt',23,v,'A lower bound for a delivery tour','Deleted-vertex TSP investigation','3.16',f'A complete undirected graph has distances '+', '.join(f'{a}{b}={w}' for a,b,w in edges)+'. A travelling salesman must return to the start.',[
   P('Delete vertex A and find the minimum spanning tree on the remaining vertices.',M('Compare the three edges among B,C,D.'),A('Choose BC and CD.'),A(f'Remaining MST weight {sum(e[2] for e in tree)}.')),
   P('Use the deleted-vertex method to obtain a lower bound.',M('Add the two cheapest distinct edges incident to A.'),A(f'These are AB={6+v} and AD={7+v}.'),A(f'Lower bound {bound}.')),
   P('The tour A-B-C-D-A is available. Find its length and deduce the exact optimum.',M('Add its four edge weights.'),A(f'Tour length {6+v+4+v+5+v+7+v}.'),R('This equals the lower bound.'),A(f'Therefore the exact optimum is {bound}.')),
   P('Explain why deleting A from any Hamiltonian cycle supports this lower-bound method.',R('The remaining tour edges form a spanning path, whose weight is at least the remaining MST weight.'),R('The two removed edges incident to A cost at least the two cheapest such edges.'))],{'deletedVertexLowerBound':bound,'optimalTour':bound})
  edges=[('A','B',4+v),('B','C',3+v),('C','D',5+v),('D','E',4+v),('E','A',6+v),('B','E',2+v)];d=distances(edges,'ABCDE');tour=['A','B','E','D','C','A'];cost=sum(d[a,b] for a,b in zip(tour,tour[1:]));best=min(sum(d[a,b] for a,b in zip(('A',)+p+('A',),(('A',)+p+('A',))[1:])) for p in itertools.permutations('BCDE'))
  add('gt',24,v,'Visits on an incomplete road map','Metric completion routing investigation','3.16','The diagram is a road network. A courier must visit all five sites and return to A; passing through a previously visited site is allowed. Edge lengths are in km.',[
   P('Find the shortest road distances AC, AD and CE.',M('Compare available road paths, allowing intermediate sites.'),A(f'AC={d["A","C"]:g}, AD={d["A","D"]:g}.'),A(f'CE={d["C","E"]:g}.')),
   P('Explain how to construct the complete distance table for a travelling-salesman method.',R('Use the shortest road distance for each unordered pair of sites.'),R('An edge in the completed graph can represent several roads in the original graph.')),
   P('Find the length of the completed-graph tour A-B-E-D-C-A and translate its last connection back into roads.',M('Add its five shortest connection distances.'),A(f'Tour length {cost:g} km.'),A('The final C-to-A connection uses C-B-A.')),
   P('State an upper bound from this tour and explain a limitation of using nearest neighbour alone.',A(f'The optimal tour is at most {cost:g} km.'),R('A nearest-neighbour route can make locally cheap choices that force an expensive return.'),R('A lower bound or comparison with alternative tours is needed to assess its quality.'),R('Repeated physical road traversal can occur even when each site appears once in the completed-graph tour.'))],{'AC':d['A','C'],'AD':d['A','D'],'CE':d['C','E'],'tourCost':cost,'exactOptimumForAudit':best},diagram=network(edges))
  a=2+v;b=8+v;mid=(a+b)/2;new=(mid,6);diag=plot(points=[(a,2,'A'),(b,2,'B'),(mid,6,'C')],xmin=0,xmax=12,ymin=0,ymax=9,equal=True)
  add('gt',25,v,'Emergency station catchments','Voronoi modelling investigation','3.6','The diagram shows three emergency stations A,B,C on a square-kilometre coordinate grid. Each point is assigned to its nearest station by straight-line distance.',[
   P('Find the equation of the perpendicular bisector of AB.',M('The boundary is the perpendicular bisector of AB.'),A(f'$x={mid:g}$.')),
   P('Find the point equidistant from all three stations, and hence state the portion of the AB bisector forming a Voronoi edge.',M(f'It lies on $x={mid:g}$.'),M(f'Equate squared distances to A and C: $9+(y-2)^2=(y-6)^2$.'),A(f'Vertex $({mid:g},23/8)$ or $({mid:g},2.875)$.'),R(f'The A-B Voronoi edge is $x={mid:g}$ with $y\\leq23/8$; above the vertex C is nearer.')),
   P('Calculate its distance from each station and explain its service significance.',M('Use the distance to any station.'),A(f'Distance {sf(math.sqrt(9+.875**2))} km.'),R('It is a location with the same travel-distance estimate to all three stations.')),
   P('Assess the use of Euclidean Voronoi cells for emergency response, giving two refinements.',R('Straight-line distance ignores roads, barriers and congestion.'),R('Use travel time or a road-network metric where available.'),R('Station capacity or specialist equipment may require weighted service rules.'),R('The nearest station by distance is not always the fastest suitable responder.'))],{'boundaryX':mid,'voronoiVertexY':23/8,'vertexDistance':math.sqrt(9+.875**2)},diagram=diag)
