"""Holgura mínima del motor y de los brazos contra la torre de la etapa 1, inflándolos 0,5, 1, 2 y 3 mm."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_v6 as v, torre_ref as tr
from generar_banda import caja
T = tr.cargar()
torre = {f'T{i}{c}': m for i, (c, gp, m) in enumerate(T) if gp not in ('cartucho', 'vaso')}
cart = [(c, m) for c, gp, m in T if gp in ('cartucho', 'vaso')]
L = v.NEMA['lado']; yf = v.Y_PLACA[0]
for g in (0.5, 1.0, 2.0, 3.0):
    mot = caja(-L / 2 - g, L / 2 + g, yf - v.NEMA['largo'] - g, yf + 0.0, v.ZC - L / 2 - g, v.ZC + L / 2 + g)
    brazos = caja(-(v.XB + v.TB) - g, v.XB + v.TB + g, v.Y_BRAZO - g, -18.0, v.ZB - g, v.ZP_TOP + g)
    mal = []
    for us in range(0, 775, 6):
        xc = v.X_CTR0 + us
        for n, m in torre.items():
            for nm, b in (('motor', mot), ('brazos', brazos)):
                if (b.translate((xc, 0, 0)) ^ m).volume() > 0.05: mal.append((nm, n, us))
        for n, m in cart:
            mm = m.translate((v.DESP0 + us, 0, 0))
            for nm, b in (('motor', mot), ('brazos', brazos)):
                if (b.translate((xc, 0, 0)) ^ mm).volume() > 0.05: mal.append((nm, 'cart-' + n, us))
    print(f'holgura {g} mm: {"libre" if not mal else str(len(mal)) + " choques, p. ej. " + str(mal[:3])}')
