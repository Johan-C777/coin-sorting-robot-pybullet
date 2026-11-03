import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_v4 as v, analisis as an
from capas import islas
P = {'CA': v.carro(), 'TO': v.tope(), 'BM': v.bloque_motor(), 'BR': v.bloque_extremo(), 'EJ': v.eje_libre(),
     'PL': v.polea_libre(), 'PM': v.polea_motriz(), 'IR': v.puente_ir()}
for k, m in P.items():
    r = an.mejor(m)
    print(k, [(round(a,1), round(h,1), n, round(p,1)) for a,h,n,rot,p,box in r[:3]])
    a,h,n,rot,p,box = r[0]
    pm,_ = an.pose(m, rot)
    il = islas(pm, tol=0.21)
    print('   pose', n, 'islas', len(il), 'area', round(sum(x[1] for x in il),1), il[:3])
