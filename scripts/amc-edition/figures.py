from content_core import *
def attach(level,n):
 line=lambda x,y,X,Y:f'<line x1="{x}" y1="{y}" x2="{X}" y2="{Y}" stroke="#633648" stroke-width="2"/>'
 txt=lambda x,y,t:f'<text x="{x}" y="{y}" fill="#25333b" font-family="sans-serif" font-size="12">{t}</text>'
 rect=lambda x,y,w,h,col:f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{col}" stroke="#694351"/>'
 poly=lambda pts:f'<polygon points="{" ".join(str(x)+","+str(y) for x,y in pts)}" stroke="#633648" fill="#fff0cf" stroke-width="2"/>'
 circ=lambda x,y,r:f'<circle cx="{x}" cy="{y}" r="{r}" stroke="#74444d" fill="none" stroke-width="1.5"/>'
 if (level,n)==(8,5):return svg(rect(18,15,160,112,'#e5b759')+rect(34,31,128,80,'white')+txt(82,77,'Photo')+txt(198,43,'Border: 1 cm')+txt(198,67,'Photo: 5 × 8 cm'),'Photo 8 wide and 5 high with a one-centimetre border',310,145)
 if (level,n)==(8,18):return svg(''.join(rect(12+x*30,12+y*30,30,30,'#eac265' if (x,y)==(1,1) else 'white') for x,y in product(range(3),repeat=2)),'A three by three grid with the centre cell shaded',115,115)
 if (level,n)==(10,10):return svg(poly([(24,113),(204,113),(24,17)])+circ(60,77,36)+txt(93,133,'15')+txt(5,70,'8'),'Right triangle with legs 8 and 15 and its incircle',230,150)
 if (level,n)==(10,16):return svg(poly([(20,115),(220,115),(160,35),(80,35)])+line(50,75,190,75)+txt(112,27,'4')+txt(110,133,'10'),'Trapezoid with horizontal bases and the segment joining leg midpoints',245,150)
 if (level,n)==(10,19):return svg(poly([(24,101),(68,13),(156,57),(112,145)])+line(24,101,156,57)+txt(4,117,'(0,0)')+txt(161,62,'(6,2)'),'Square with labelled opposite vertices; other diagonal not shown',220,160)
 if (level,n)==(12,13):
  # Triangle in units: radii 2,3,4; centres (0,0),(5,0),(1.2,sqrt(34.56)).
  X,Y=122,124;sc=11
  return svg(circ(X,Y,22)+circ(X+55,Y,33)+circ(X+13.2,Y-11*math.sqrt(34.56),44)+line(X,Y,X+55,Y)+line(X,Y,X+13.2,Y-11*math.sqrt(34.56))+line(X+55,Y,X+13.2,Y-11*math.sqrt(34.56))+txt(74,144,'r = 2')+txt(190,144,'r = 3')+txt(184,55,'r = 4'),'Externally tangent circles of radii 2, 3 and 4 with centres joined',255,164)
 if (level,n)==(12,18):return svg(line(10,108,218,108)+line(40,28,105,108)+line(105,108,180,48)+txt(20,21,'(1,4)')+txt(166,39,'(8,3)')+txt(86,128,'(t,0)')+txt(192,124,'x'),'Two paths to a movable point on the x-axis; not to scale',235,143)
 if (level,n)==(12,20):return svg(rect(28,15,112,112,'white')+poly([(28,127),(84,127),(112,99),(56,43),(28,71)])+line(28,15,140,127)+txt(15,143,'0')+txt(141,141,'1')+txt(10,22,'1'),'The feasible region in the unit square; axes run right and up',180,155)
 return ''
