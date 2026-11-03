import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_v4 as v, analisis as an
from manifold3d import JoinType
P = {'CA': (v.carro(), (0,0,0), 1), 'TO': (v.tope(), (90,0,0), 4), 'BM': (v.bloque_motor(), (0,0,0), 1), 'BR': (v.bloque_extremo(), (0,0,0), 1),
     'EJ': (v.eje_libre(), (0,0,0), 1), 'PL': (v.polea_libre(), (0,0,0), 1), 'PM': (v.polea_motriz(), (0,0,0), 1), 'IR': (v.puente_ir(), (0,90,0), 1)}
RHO=1.27; H=0.2; PARED=1.2; REL=0.15; TAPA=1.0
tot=0; totv=0
for k,(m,rot,n) in P.items():
    mm,_=an.pose(m,rot)
    z0,z1=mm.bounding_box()[2],mm.bounding_box()[5]
    vol=0.0; z=z0+H/2; nl=int((z1-z0)/H)
    i=0
    while z<z1:
        A=mm.slice(z); a=A.area()
        ai=A.offset(-PARED,JoinType.Round,8).area() if a>0 else 0
        sol = (i<5 or i>=nl-5)
        vol+=H*(a if sol else (a-ai)+REL*ai)
        z+=H;i+=1
    g=vol/1000*RHO
    print(f"{k} x{n}: solido {m.volume()/1000:6.1f} cm3  -> {g:6.1f} g c/u (3 paredes, 15% relleno)")
    tot+=g*n; totv+=m.volume()/1000*RHO*n
print('TOTAL g estimados', round(tot,0), ' | si fuera macizo', round(totv,0))
