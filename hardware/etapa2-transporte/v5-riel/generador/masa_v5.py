import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_v5 as v, analisis as an
from manifold3d import JoinType
P = {'CA': (v.carro(), 1), 'BM': (v.bloque_motor(), 1), 'BR': (v.bloque_extremo(), 1), 'PM': (v.polea_motriz(), 1), 'PL': (v.polea_libre(), 1), 'EJ': (v.eje_libre(), 1)}
for i in range(len(v.SEG)): P[f'S{i+1}'] = (v.segmento(i), 1)
RHO = 1.27; H = 0.2; PARED = 1.2; REL = 0.15
tot = 0; totv = 0
for k, (m, n) in P.items():
    mm, _ = an.pose(m, (0, 0, 0))
    z0, z1 = mm.bounding_box()[2], mm.bounding_box()[5]
    vol = 0.0; z = z0 + H / 2; nl = int((z1 - z0) / H); i = 0
    while z < z1:
        A = mm.slice(z); a = A.area()
        ai = A.offset(-PARED, JoinType.Round, 8).area() if a > 0 else 0
        sol = (i < 5 or i >= nl - 5)
        vol += H * (a if sol else (a - ai) + REL * ai)
        z += H; i += 1
    gr = vol / 1000 * RHO
    print(f"{k} x{n}: macizo {m.volume()/1000:6.1f} cm3 -> {gr:6.1f} g (3 paredes, 15 % de relleno)")
    tot += gr * n; totv += m.volume() / 1000 * RHO * n
print('TOTAL g estimados', round(tot), '| si fuera macizo', round(totv))
