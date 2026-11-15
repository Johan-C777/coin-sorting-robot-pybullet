"""Holguras de la v7: uniones de la barra, brazo contra carro, y soporte del motor contra los patines y la torre (inflando 0,5 / 1 / 2 / 3 mm)."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_v7 as v, torre_ref as tr
from generar_banda import caja
from manifold3d import Manifold, CrossSection
bs = v.barra_ensamblada(0.0)
for j in range(3):
    ov = (bs[j] ^ bs[j + 1]).volume()
    print(f'unión {j+1}-{j+2}: solape {ov:.3f} mm3')
# juego de la lengüeta: engordar un tramo 0,1 / 0,2 mm y ver si choca
for j in range(3):
    t = v.tramo_barra(j)
    for d in (0.1, 0.2):
        eng = Manifold.compose([t])  # copia
        # engordar con una dilatación aproximada: unión de desplazamientos
        acum = t
        for dx, dz in ((d, 0), (-d, 0), (0, d), (0, -d)):
            acum = acum + t.translate((dx, 0, dz))
        print(f'  tramo {j+1} engordado {d} mm contra el {j+2}: solape {(acum.translate((0,0,0)) ^ v.tramo_barra(j+1)).volume():.2f}')
# brazo contra carro
ca, bz = v.carro(v.X_CTR0), v.brazo(v.X_CTR0)
print('brazo-carro solape', round((ca ^ bz).volume(), 3))
acum = bz
for dx, dy in ((0.1, 0), (-0.1, 0), (0, 0.1), (0, -0.1)): acum = acum + bz.translate((dx, dy, 0))
print('brazo engordado 0,1 mm contra el carro:', round((acum ^ ca).volume(), 2))
# soporte y motor contra la torre
T = tr.cargar()
torre = {f'T{i}{c}': m for i, (c, gp, m) in enumerate(T) if gp not in ('cartucho', 'vaso')}
sop, mot = v.soporte(), v.nema_ref()
bbm = mot.bounding_box()
for g in (0.5, 1.0, 2.0, 3.0, 5.0):
    mal = []
    for nom, pieza in (('soporte', sop), ('motor', mot)):
        bb = pieza.bounding_box()
        inf = caja(bb[0] - g, bb[3] + g, bb[1] - g, bb[4] + g, 0, bb[5] + g) ^ Manifold.cube((1, 1, 1))  # caja contenedora
        inf = caja(bb[0] - g, bb[3] + g, bb[1] - g, bb[4] + g, 0, bb[5] + g)
        for n, m in torre.items():
            if (inf ^ m).volume() > 0.05: mal.append((nom, n))
    print(f'caja del soporte/motor inflada {g} mm contra la torre:', 'libre' if not mal else mal[:4])
