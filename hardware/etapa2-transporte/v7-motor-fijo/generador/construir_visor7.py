"""Genera visor/visor-v7.html (un solo archivo: datos 3D incrustados) a partir de visor/plantilla7.html."""
import os, sys, json, base64, math
import numpy as np
from manifold3d import Manifold
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import generar_v7 as v, torre_ref as tr

def enc(m):
    mm = m.to_mesh()
    vt = np.asarray(mm.vert_properties, dtype=np.float32)[:, :3].copy()
    ix = np.asarray(mm.tri_verts, dtype=np.uint32).ravel()
    return base64.b64encode(vt.tobytes()).decode(), base64.b64encode(ix.tobytes()).decode()

piezas = []
def add(n, c, m, mov, col, d):
    a, b = enc(m); piezas.append(dict(n=n, c=c, v=a, t=b, mov=mov, col=col, d=d))

U_C = 153.5                                   # carro con su centro sobre el eje del piñón (corte)
A0 = 333.5
add('Carro', 'CA', v.carro(v.X_CTR0), 1, 'carro', 'Placa para el cartucho con dos zonas que abrazan la cabeza del riel y una ranura de cola de milano en la pared −Y para el brazo. 58 g, PETG.')
add('Brazo', 'BZ', v.brazo(v.X_CTR0), 1, 'carro', 'Placa de pie con una cola de milano que entra por arriba en la ranura del carro y un ojal alargado en Y para la clavija de la barra. 24 g, PETG.')
bars = v.barra_ensamblada(0.0)
desc = ['Tramo más atrasado de la barra: 43 dientes y una lengüeta de cola de milano hacia adelante.', 'Tramo central de la barra: ranura atrás, lengüeta adelante.', 'Tramo central de la barra: ranura atrás, lengüeta adelante.', 'Tramo delantero de la barra, con la clavija que entra en el ojal del brazo.']
g = [26, 25, 25, 32]
for j in range(4): add(f'Barra, tramo {j+1}', f'B{j+1}', bars[j], 1, 'barra', desc[j] + f' {g[j]} g, PLA+.')
add('Motor NEMA17', 'K1', v.nema_ref(), 0, 'motor', 'Ya lo tienes. Fijo: la cara del piloto contra la placa del soporte y el eje apuntando a la barra.')
add('Soporte del motor', 'SP', v.soporte(), 0, 'bloque', 'Base con rampas, placa piloto, dos brazos y una pared guía que mantiene la barra contra el piñón. Se pega a la mesa entre los patines de la torre. 20 g, PETG.')
pin = v.pinon_colocado(0.0).translate((-v.XP, 0, -v.ZC))
a, b = enc(pin); pinion = dict(v=a, t=b)
add('Piñón', 'PI', v.pinon_colocado(0.0), 2, 'pinon', 'Piñón de 16 dientes, módulo 1,5, en el eje del motor (agujero en D). 3 g, PETG al 100 %.')
gr = {0: 42, 1: 29, 2: 29, 3: 29, 4: 30}
for i in range(len(v.SEG)):
    add(f'Riel, tramo {i+1}', f'R{i+1}', v.segmento(i), 0, 'rail', f'Tramo de {v.SEG[i][1]-v.SEG[i][0]:.0f} mm del riel de la v5; se encaja con una lengüeta al siguiente. ' + ('Lleva los postes de la barrera infrarroja. ' if i == 0 else '') + f'PLA+, {gr[i]} g.')

torre = []
for c, gp, m in tr.cargar():
    a, b = enc(m); torre.append(dict(v=a, t=b, cart=1 if gp in ('cartucho', 'vaso') else 0, g=gp))

XC = v.XP
def corte(m):
    r = m.rotate((0, -90, 0))
    cs = r.slice(XC)
    return [[[round(float(y), 2), round(float(-x), 2)] for x, y in p] for p in cs.to_polygons()]
iseg = [i for i, (a_, b_) in enumerate(v.SEG) if a_ <= XC <= b_][0]
bs = v.barra_ensamblada(U_C)
barra_c = sum(bs[1:], bs[0])
cortes = dict(riel=corte(v.segmento(iseg)), carro=corte(v.carro(XC)), motor=corte(v.nema_ref()), soporte=corte(v.soporte()),
              barra=corte(barra_c), pinon=corte(v.pinon_colocado(A0 + U_C / v.RP * 180 / math.pi)))

circ = 2 * math.pi * v.RP; spm = 3200 / circ
num = dict(spm=spm, circ=circ, rp=v.RP, carrera=774 * spm, vaso=38 * spm, rechazo=342 * spm, empuje=0.4 / (v.RP / 1000),
           juego=2 * v.BL * math.tan(v.ALFA) + 2 * v.TD, paso=v.PASO, dientes=v.N_DIENTES, a0=A0)
U = 774.0
planta = dict(torre=[-235, 120], riel=[v.RIEL_X0, v.RIEL_X1], barra0=[round(v.X_T0, 1), round(v.XPEG + 9, 1)], barra1=[round(v.X_T0 + U, 1), round(v.XPEG + 9 + U, 1)],
              barra_y=[-v.Y_BAR[1], -v.Y_BAR[0]], sop=[v.XP - v.XS, v.XP + v.XS, -(v.Y_BAR[1] + 3.4), -(v.Y_MOT - 3.0)],
              mot=[v.XP - 21.15, v.XP + 21.15, -(v.Y_PLACA[0]), -(v.Y_MOT)], carro0=[v.X_CTR0 - v.LEN / 2, v.X_CTR0 + v.LEN / 2], carro1=[v.X_CTR0 - v.LEN / 2 + U, v.X_CTR0 + v.LEN / 2 + U])
datos = dict(planta=planta, piezas=piezas, torre=torre, pinion=pinion, x0=v.X_CTR0, xp=v.XP, xbrazo=v.XSL, largo=v.LEN, desp0=v.DESP0, umax=774, zc=v.ZC, rp=v.RP, num=num, corte=cortes)
html = open(os.path.join(AQUI, '..', 'visor', 'plantilla7.html'), encoding='utf-8').read().replace('/*DATOS*/null', json.dumps(datos, separators=(',', ':')))
open(os.path.join(AQUI, '..', 'visor', 'visor-v7.html'), 'w', encoding='utf-8').write(html)
print(round(len(html) / 1e6, 2), 'MB; corte riel segmento', iseg + 1, {k: len(x) for k, x in cortes.items()})
