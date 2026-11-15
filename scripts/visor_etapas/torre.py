"""Etapa 1 (torre v5 + ajustes vigentes) + su electrónica, exportada al marco de la banda (X igual, Y = z, Z = y).
Uso: python torre.py <repo/scripts> <salida.json>"""
import sys, json, math, base64
import numpy as np
sys.path.insert(0, sys.argv[1])
from manifold3d import Manifold, set_circular_segments
import trimesh
import generar_v5 as g
import generar_ajustes_tolva as aj
set_circular_segments(48)

def enc(m, perm=True):
    mm = m.to_mesh()
    v = np.asarray(mm.vert_properties, np.float32)[:, :3]
    t = np.asarray(mm.tri_verts, np.uint32)
    if perm: v, t = v[:, [0, 2, 1]].copy(), t[:, [0, 2, 1]].copy()
    return base64.b64encode(np.round(v, 2).astype(np.float32).tobytes()).decode(), base64.b64encode(t.tobytes()).decode()

def P(p):  # punto del mundo de la torre -> marco de la banda
    p = np.asarray(p, float); return [round(float(p[0]), 2), round(float(p[2]), 2), round(float(p[1]), 2)]

out = dict(piezas=[], anclas={})
def add(id_, nombre, mat, m, grupo='e1', mov=0, rot=None, perm=True):
    a, b = enc(m, perm); out['piezas'].append(dict(id=id_, n=nombre, mat=mat, v=a, t=b, g=grupo, mov=mov, rot=rot))

pz = g.ensamble()
cil, caja = g.cil, g.caja
NOM = {'L01': 'Pista L01', 'B01': 'Porta-emisor IR B01', 'H01': 'Base de la tolva H01', 'H03': 'Rascador H03',
       'K01': 'Soporte K01', 'K02': 'Soporte K02', 'F01': 'Embudo F01', 'F02': 'Campana F02', 'G01': 'Cuna del servo G01',
       'T01': 'Caballete T01', 'S01': 'Patín S01', 'S02': 'Patín S02', 'R01': 'Larguero R01', 'R02': 'Larguero R02',
       'C01': 'Cartucho C01', 'C02': 'Rampa de rechazo C02', 'V01': 'Vaso'}
MAT = {'L01': 'negro', 'B01': 'negro', 'H01': 'negro', 'H03': 'negro', 'K01': 'negro', 'K02': 'negro', 'F01': 'negro', 'F02': 'negro',
       'G01': 'marmol', 'T01': 'azul', 'S01': 'azul', 'S02': 'azul', 'R01': 'azul', 'R02': 'azul', 'C02': 'negro'}
VASOS = ['azul', 'negro', 'azul', 'azul', 'marmol', 'azul', 'azul', 'negro', 'azul']   # como en la foto del cartucho
for cod, ms in pz.items():
    if cod in ('H02', 'G02'):
        continue
    for i, m in enumerate(ms):
        if cod == 'C01':
            add(f'C01-{i}', 'Cartucho C01', 'negro' if i == 1 else 'marmol', m, 'e1', 1)
        elif cod == 'C02':
            add('C02', NOM[cod], 'negro', m, 'e1', 1)
        elif cod == 'V01':
            x = (i - 4) * g.CUP_PASO; y0 = g.Y_BELT + g.SLED_E - 3
            if VASOS[i] == 'azul':      # vaso bicolor: fondo plateado y cuerpo azul
                base = m ^ caja(x - 30, x + 30, y0 - 1, y0 + 15, -30, 30)
                add(f'V{i+1}a', f'Vaso {i+1}', 'marmol', base, 'e1', 1)
                add(f'V{i+1}', f'Vaso {i+1}', 'azul', m - caja(x - 30, x + 30, y0 - 1, y0 + 15, -30, 30), 'e1', 1)
            else:
                add(f'V{i+1}', f'Vaso {i+1}', VASOS[i], m, 'e1', 1)
        elif cod == 'L01':
            continue
        else:
            add(f'{cod}-{i}', NOM[cod], MAT[cod], m)

# disco vigente H02e (5 bolsillos Ø40) en su marco local: gira alrededor de ND por DISCO_O
d = aj.disco_c(5, 40.0, 45.5)
Minv = np.column_stack([g.UD, g.WD, g.ND])
loc = d.translate(tuple(-g.DISCO_O)).transform(np.column_stack([Minv.T, np.zeros(3)]))
add('H02', 'Disco de 5 bolsillos H02e', 'verde', loc, 'e1', 0, rot=dict(o=P(g.DISCO_O), u=P(g.UD), w=P(g.WD), n=P(g.ND)), perm=False)
# los vectores se pasan con la misma permutación (P sin traslación funciona igual para direcciones)
add('H04', 'Tope trasero H04', 'negro', aj.tope())

# compuerta G02 + paleta plana G03 pegada encima; gira sobre el eje del servo (X) en (Y_G, Z_BIS)
gate = g.compuerta() + caja(-g.PAL, g.PAL, g.Y_G + g.PAL_E / 2 - 0.01, g.Y_G + g.PAL_E / 2 + 2.5, g.Z_BIS + 1, g.PAL)
piv = np.array([0.0, g.Y_G, g.Z_BIS])
add('G02', 'Compuerta G02 + paleta G03', 'marmol', gate.translate(tuple(-piv)), 'e1', 0, rot=dict(o=P(piv), eje=[1, 0, 0]))

# adaptador A01 del TCS3200 (STL en posición de impresión -> pista)
R = np.array([g.SV, -g.NV, g.TV])
pl = g.pista().transform(np.column_stack([R, np.zeros(3)])); bb = pl.bounding_box()
c = np.array([(bb[0] + bb[3]) / 2, (bb[1] + bb[4]) / 2, bb[2]])
def de_l01(m):  # marco de impresión de L01 -> mundo
    return m.translate(tuple(c)).transform(np.column_stack([R.T, np.zeros(3)]))
tm = trimesh.load(sys.argv[3]) if len(sys.argv) > 3 else None
from manifold3d import Mesh
a01 = Manifold(Mesh(vert_properties=np.asarray(tm.vertices, np.float32), tri_verts=np.asarray(tm.faces, np.uint32)))
# el STL del adaptador está en el marco de L01 recentrado igual que la cama: comprobar el desfase con el centro del bloque
corte = de_l01(Manifold.cube((22.02, 5.52, 34.0)).translate((55.49, -8.01, 6.0)))
add('L01', 'Pista L01', 'negro', pz['L01'][0] - corte)
add('A01', 'Adaptador del sensor de color A01', 'verde', de_l01(a01))

# ------------------------------------------------------------------ electrónica de la etapa 1
def piezaE(id_, nombre, partes):
    for k, (mat, m) in enumerate(partes):
        a, b = enc(m); out['piezas'].append(dict(id=id_, n=nombre, mat=mat, v=a, t=b, g='elec', mov=0, rot=None, sub=k))

# 28BYJ-48 detrás de H01 (marco del disco)
MD = lambda m: g.marco_disco(m)
z0 = -g.BASE_E
cuerpo = Manifold.cylinder(g.MOTOR_L, g.MOTOR_D / 2).translate((0, -g.MOTOR_OFF, z0 - g.MOTOR_L))
orejas = (Manifold.cylinder(0.8, 3.5).translate((-g.OREJAS / 2, -g.MOTOR_OFF, z0 - 0.8)) + Manifold.cylinder(0.8, 3.5).translate((g.OREJAS / 2, -g.MOTOR_OFF, z0 - 0.8))
          + caja(-g.OREJAS / 2, g.OREJAS / 2, -g.MOTOR_OFF - 3.5, -g.MOTOR_OFF + 3.5, z0 - 0.8, z0))
tapa = caja(-8.5, 8.5, -g.MOTOR_OFF - g.MOTOR_D / 2 - 3, -g.MOTOR_OFF - 6, z0 - g.MOTOR_L + 0.5, z0 - 1.5)
piezaE('M1', 'Motor 28BYJ-48 (tolva)', [('acero', MD(cuerpo + orejas)), ('plastico_azul', MD(tapa))])
mot_c = g.a_mundo_disco(0, -g.MOTOR_OFF - g.MOTOR_D / 2 - 3, z0 - g.MOTOR_L / 2)
out['anclas']['M1'] = P(g.a_mundo_disco(0, -g.MOTOR_OFF, z0 - g.MOTOR_L - 2))
out['anclas']['M1c'] = P(mot_c)

# SG90 en la cuna G01 (eje hacia -X sobre la bisagra)
yc = g.Y_G - g.SERVO_OFF
x0 = g.G01_X0 + 0.3
sg = caja(x0, x0 + 22.7, yc - 11.35, yc + 11.35, g.Z_BIS - 6.1, g.Z_BIS + 6.1)
sg += caja(x0 + 4.5, x0 + 7.0, yc - 16.0, yc + 16.0, g.Z_BIS - 6.1, g.Z_BIS + 6.1)          # pestañas
sg += cil((x0, g.Y_G, g.Z_BIS), (-1, 0, 0), 4.0, 5.9 / 2)
cuerno = cil((x0 - 4.0, g.Y_G, g.Z_BIS), (-1, 0, 0), 1.6, 3.5) + caja(x0 - 5.6, x0 - 4.0, g.Y_G - 2.2, g.Y_G + 2.2, g.Z_BIS, g.Z_BIS + 14)
piezaE('SV', 'Servo SG90 (compuerta)', [('plastico_azul_t', sg), ('blanco', cuerno)])
out['anclas']['SV'] = P((x0 + 22.7, yc, g.Z_BIS))

# barreras IR de la pista: emisor (en B01, detrás de la placa) y fototransistor (poste delantero)
def led(p0, eje, mat_cuerpo):
    a = np.asarray(eje, float)
    body = cil(p0, a, 5.6, 2.5) + cil(np.asarray(p0) + 5.6 * a, a, 1.0, 2.5, 0.5)
    ring = cil(np.asarray(p0) - 1.0 * a, a, 1.0, 2.9)
    return [(mat_cuerpo, body + ring)]
ir = []
for k, sb in enumerate((g.B1, g.B1 + g.SEP)):
    pe = g.a_mundo_pista(sb, g.H_BAR, -11.0)
    pr = g.a_mundo_pista(sb, g.H_BAR, g.LAB + 9.0)
    piezaE(f'IE{k+1}', f'LED IR emisor {k+1}', led(pe, g.NV, 'led_ir'))
    piezaE(f'IR{k+1}', f'Fototransistor {k+1}', led(pr, -g.NV, 'negro_led'))
    out['anclas'][f'IE{k+1}'] = P(g.a_mundo_pista(sb, g.H_BAR, -13.0))
    out['anclas'][f'IR{k+1}'] = P(g.a_mundo_pista(sb, g.H_BAR, g.LAB + 15.0))

# TCS3200 en el adaptador A01 (marco de impresión de L01: X a lo largo, Y = -n, Z = t)
CX, h = 66.5, 28.5 / 2
from manifold3d import Manifold as Mf
def bx(x0, x1, y0, y1, z0, z1): return Mf.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))
zb = 6.0 + 1.6
pcb = bx(CX - h, CX + h, -6.1 + 0.1, -4.5, zb, zb + 28.5)
chip = bx(CX - 2.5, CX + 2.5, -4.5, -3.7, zb + 12, zb + 17)
leds = sum([Mf.cylinder(1.2, 1.6).rotate((-90, 0, 0)).translate((CX + sx * 7.5, -4.5, zb + 14.25 + sz * 7.5)) for sx in (-1, 1) for sz in (-1, 1)], Mf())
pines = sum([bx(CX - 8.9 + 2.54 * i - 0.32, CX - 8.9 + 2.54 * i + 0.32, -6.0, -5.4, zb + 28.5, zb + 34.5) for i in range(8)], Mf())
cab = bx(CX - 10.2, CX + 10.2, -7.0, -4.6, zb + 28.5, zb + 31.0)
piezaE('TC', 'Sensor de color TCS3200', [('pcb_azul', de_l01(pcb)), ('negro_led', de_l01(chip + cab)), ('blanco_led', de_l01(leds)), ('oro', de_l01(pines))])
out['anclas']['TC'] = P(de_l01(bx(CX - 1, CX + 1, -6, -5, zb + 33, zb + 34)).bounding_box()[:3])

# puntos útiles de la torre (para las etiquetas y el recorrido de los cables)
out['anclas']['disco'] = P(g.DISCO_O)
out['anclas']['embudo'] = P((0, g.FUN_Y_RIM, 0))
out['anclas']['pista_fin'] = P(g.a_mundo_pista(g.S_END, 0, 0))
out['anclas']['pista_ini'] = P(g.a_mundo_pista(0, 0, 0))
out['cotas'] = dict(Y_BELT=g.Y_BELT, CUP_PASO=g.CUP_PASO, X_RECHAZO=-1.5 * g.CART_L - g.CUP_PASO / 2, Z_RECHAZO=g.Z_RECHAZO, G_ABRE=g.G_ABRE,
                    X_CAB=list(g.X_CAB), Z_PATA=g.Z_PATA, Y_VIGA1=g.Y_VIGA1, CUP_H=g.CUP_H)
json.dump(out, open(sys.argv[2], 'w'), separators=(',', ':'))
print('piezas', len(out['piezas']), 'MB', round(sum(len(p['v']) + len(p['t']) for p in out['piezas']) / 1e6, 2))
print('A01 bbox', [round(x, 1) for x in de_l01(a01).bounding_box()], 'L01 bbox', [round(x, 1) for x in g.pista().bounding_box()])
print("choque A01-L01 cortada", round((de_l01(a01) ^ (pz["L01"][0] - corte)).volume(), 1))
