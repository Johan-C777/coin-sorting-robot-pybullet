"""Genera visor/visor-v6.html (un solo archivo: datos 3D incrustados) a partir de visor/plantilla6.html."""
import os, sys, json, base64, math
import numpy as np
from manifold3d import Manifold
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import generar_v6 as v, torre_ref as tr

def enc(m):
    mm = m.to_mesh()
    vt = np.asarray(mm.vert_properties, dtype=np.float32)[:, :3].copy()
    ix = np.asarray(mm.tri_verts, dtype=np.uint32).ravel()
    return base64.b64encode(vt.tobytes()).decode(), base64.b64encode(ix.tobytes()).decode()

piezas = []
def add(n, c, m, mov, col, d):
    a, b = enc(m); piezas.append(dict(n=n, c=c, v=a, t=b, mov=mov, col=col, d=d))

add('Carro', 'CA', v.carro(v.X_CTR0), 1, 'carro', 'Placa para el cartucho con dos zonas que abrazan la cabeza del riel, cuatro topes, dos brazos y una placa que sostienen el motor. 69 g, PETG.')
add('Motor NEMA17', 'K1', v.nema_ref(v.X_CTR0), 1, 'motor', 'Ya lo tienes. Va entre los brazos, con el eje hacia el riel.')
pin = v.pinon_colocado(0.0, 0.0).translate((0, 0, -v.ZC))
a, b = enc(pin); pinion = dict(v=a, t=b)
add('Piñón', 'PI', v.pinon_colocado(v.X_CTR0, 0.0), 2, 'pinon', 'Piñón de 18 dientes, módulo 1,5, en el eje del motor (agujero en D). 4 g, PETG al 100 %.')
nombres = {0: 50, 1: 39, 2: 39, 3: 39, 4: 38}
for i in range(len(v.SEG)):
    add(f'Riel, tramo {i+1}', f'R{i+1}', v.segmento(i), 0, 'rail', f'Tramo de {v.SEG[i][1]-v.SEG[i][0]:.0f} mm del riel con su parte de cremallera; se encaja con una lengüeta al siguiente. ' + ('Lleva los postes de la barrera infrarroja. ' if i == 0 else '') + f'PLA+, {nombres[i]} g.')

torre = []
for c, gp, m in tr.cargar():
    a, b = enc(m); torre.append(dict(v=a, t=b, cart=1 if gp in ('cartucho', 'vaso') else 0, g=gp))

# corte frontal a la altura de x = 40 (el piñón con fase 12°): se rota para que X pase a ser Z y se rebana
XC = 40.0
def corte(m):
    r = m.rotate((0, -90, 0))
    cs = r.slice(XC)
    return [[[round(float(y), 2), round(float(-x), 2)] for x, y in p] for p in cs.to_polygons()]
seg = v.segmento(1)
cortes = dict(riel=corte(seg), carro=corte(v.carro(XC)), motor=corte(v.nema_ref(XC)), pinon=corte(v.pinon_colocado(XC, 12.0)))

circ = 2 * math.pi * v.RP; spm = 3200 / circ
num = dict(spm=spm, circ=circ, rp=v.RP, carrera=v.U_MAX * spm, vaso=38 * spm, rechazo=342 * spm, cero_u=v.IR_X + v.LEN / 2 - v.X_CTR0,
           cero_pasos=(v.IR_X + v.LEN / 2 - v.X_CTR0) * spm, empuje=0.4 / (v.RP / 1000), juego=2 * v.BL * math.tan(v.ALFA),
           paso=v.PASO, dientes=v.N_DIENTES, x0=v.X_V0, x1=v.X_R1, riel=v.RIEL_X1 - v.RIEL_X0, a0=12.0)
datos = dict(piezas=piezas, torre=torre, pinion=pinion, x0=v.X_CTR0, largo=v.LEN, desp0=v.DESP0, umax=v.U_MAX, zc=v.ZC, rp=v.RP, num=num, corte=cortes)
html = open(os.path.join(AQUI, '..', 'visor', 'plantilla6.html'), encoding='utf-8').read().replace('/*DATOS*/null', json.dumps(datos, separators=(',', ':')))
open(os.path.join(AQUI, '..', 'visor', 'visor-v6.html'), 'w', encoding='utf-8').write(html)
print(round(len(html) / 1e6, 2), 'MB')
