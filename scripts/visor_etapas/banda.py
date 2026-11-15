"""Etapa 2 v7 (motor fijo, barra dentada) + electrónica de la base, marco de la banda. Uso: python banda.py <gen7> <torre.json> <salida.json>"""
import sys, json, base64, math
import numpy as np
sys.path.insert(0, sys.argv[1])
from manifold3d import Manifold as M, set_circular_segments
import generar_v7 as v
set_circular_segments(40)

def enc(m):
    mm = m.to_mesh()
    vt = np.round(np.asarray(mm.vert_properties, np.float32)[:, :3], 2).astype(np.float32)
    return base64.b64encode(vt.tobytes()).decode(), base64.b64encode(np.asarray(mm.tri_verts, np.uint32).tobytes()).decode()
out = json.load(open(sys.argv[2]))
def add(id_, n, mat, m, grupo='e2', mov=0, rot=None, sub=0):
    a, b = enc(m); out['piezas'].append(dict(id=id_, n=n, mat=mat, v=a, t=b, g=grupo, mov=mov, rot=rot, sub=sub))
def bx(x0, x1, y0, y1, z0, z1): return M.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))
def cz(x, y, z0, h, r, r2=None): return M.cylinder(h, r, -1 if r2 is None else r2).translate((x, y, z0))
def cy(x, z, y0, h, r): return M.cylinder(h, r).rotate((-90, 0, 0)).translate((x, y0, z))
def cx(y, z, x0, h, r): return M.cylinder(h, r).rotate((0, 90, 0)).translate((x0, y, z))

# ------------------------------------------------------------------ piezas impresas de la banda (u = 0)
add('CA', 'Carro', 'azul', v.carro(v.X_CTR0), mov=1)
add('BZ', 'Brazo del carro', 'azul', v.brazo(v.X_CTR0), mov=1)
for j, b in enumerate(v.barra_ensamblada(0.0)):
    add(f'B{j+1}', f'Barra dentada, tramo {j+1}', 'negro', b, mov=1)
add('SP', 'Soporte del motor', 'azul', v.soporte())
pin = v.pinon_colocado(0.0).translate((-v.XP, 0, -v.ZC))
add('PI', 'Piñón de 16 dientes', 'azul', pin, rot=dict(o=[v.XP, 0, v.ZC], eje=[0, 1, 0]))
for i in range(len(v.SEG)):
    add(f'R{i+1}', f'Riel, tramo {i+1}', 'marmol', v.segmento(i))

# ------------------------------------------------------------------ NEMA17 (etapa 2) con tapas de aluminio
L, yf, XP, ZC = v.NEMA['lado'], v.Y_PLACA[0], v.XP, v.ZC
y0m = yf - v.NEMA['largo']
def ch(m, k=3.0):  # caja con esquinas achaflanadas en X-Z
    return m
cuerpo = bx(XP - L / 2 + 0.6, XP + L / 2 - 0.6, y0m + 8, yf - 8, ZC - L / 2 + 0.6, ZC + L / 2 - 0.6)
tapas = bx(XP - L / 2, XP + L / 2, y0m, y0m + 8, ZC - L / 2, ZC + L / 2) + bx(XP - L / 2, XP + L / 2, yf - 8, yf, ZC - L / 2, ZC + L / 2)
esq = M()
for sx in (-1, 1):
    for sz in (-1, 1):
        esq += bx(XP + sx * L / 2 - 4, XP + sx * L / 2 + 4, y0m - 1, yf + 1, ZC + sz * L / 2 - 4, ZC + sz * L / 2 + 4).rotate((0, 0, 0))
tapas = tapas - esq + sum([cy(XP + sx * (L / 2 - 4), ZC + sz * (L / 2 - 4), y0m, v.NEMA['largo'], 4) for sx in (-1, 1) for sz in (-1, 1)], M()) - bx(XP - L / 2 + 0.6, XP + L / 2 - 0.6, y0m + 8, yf - 8, ZC - L, ZC + L)
cuerpo = cuerpo - esq + sum([cy(XP + sx * (L / 2 - 4), ZC + sz * (L / 2 - 4), y0m + 8, v.NEMA['largo'] - 16, 3.4) for sx in (-1, 1) for sz in (-1, 1)], M())
piloto = cy(XP, ZC, yf, 2, 11) + (cy(XP, ZC, yf, v.NEMA['eje_l'], 2.5) ^ bx(XP - 3, XP + 2, -200, 200, ZC - 3, ZC + 3))
conector = bx(XP - L / 2 - 1, XP - L / 2 + 0.01, y0m + 6, y0m + 22, ZC - 8, ZC + 8)
add('K1', 'Motor NEMA17 (banda)', 'aluminio', tapas + piloto, grupo='elec', sub=0)
add('K1', 'Motor NEMA17 (banda)', 'negro_mate', cuerpo + conector, grupo='elec', sub=1)
out['anclas']['K1'] = [XP - L / 2 - 1, y0m + 14, ZC]

# barrera infrarroja de referencia en el riel (tramo 1)
def led_y(x, z, y0, sgn, mat, n, idn):
    body = cy(x, z, y0 if sgn > 0 else y0 - 5.6, 5.6, 2.5)
    domo = M.sphere(2.5).translate((x, y0 + sgn * 5.6, z)) if True else None
    ring = cy(x, z, y0 - 1 if sgn > 0 else y0, 1, 2.9)
    add(idn, n, mat, body + domo + ring, grupo='elec')
led_y(v.IR_X, v.Z_IR, 41.0, -1, 'led_ir', 'LED IR de referencia (banda)', 'IE3')
led_y(v.IR_X, v.Z_IR, v.Y_IR_N[0], 1, 'negro_led', 'Fototransistor de referencia (banda)', 'IR3')
out['anclas']['IE3'] = [v.IR_X, 44.0, v.Z_IR + 6]
out['anclas']['IR3'] = [v.IR_X, v.Y_IR_N[0] - 2, v.Z_IR + 6]

# ------------------------------------------------------------------ base de la electrónica (detrás de la torre, lado del motor)
TX0, TX1, TY0, TY1 = -300.0, -60.0, -275.0, -135.0
bandeja = bx(TX0, TX1, TY0, TY1, 0, 3) + (bx(TX0, TX1, TY0, TY1, 0, 22) - bx(TX0 + 2, TX1 - 2, TY0 + 2, TY1 - 2, 2, 30))
add('BA', 'Caja de la electrónica', 'transparente', bandeja, grupo='elec')
ZT = 3.0
# placa de expansión del ESP32-S3
EX0, EY0 = -292.0, -262.0
EW, EH = 104.0, 76.0
add('EX', 'Placa de expansión ESP32-S3', 'pcb_negro', bx(EX0, EX0 + EW, EY0, EY0 + EH, ZT + 4, ZT + 5.6) + sum([cz(EX0 + a, EY0 + b, ZT, 4, 1.6) for a in (4, EW - 4) for b in (4, EH - 4)], M()), grupo='elec', sub=0)
hdr = M(); hdr2 = M()
for row, yy in enumerate((EY0 + 8, EY0 + EH - 12)):
    for k in range(3):
        mat_rows = bx(EX0 + 14, EX0 + 14 + 22 * 2.54, yy + k * 2.54 - 1.2, yy + k * 2.54 + 1.2, ZT + 5.6, ZT + 14)
        if k == 0: hdr += mat_rows
        else: hdr2 += mat_rows
add('EX', 'Placa de expansión ESP32-S3', 'amarillo', hdr, grupo='elec', sub=1)
add('EX', 'Placa de expansión ESP32-S3', 'rojo', hdr2, grupo='elec', sub=2)
jack = bx(EX0 - 2, EX0 + 12, EY0 + EH / 2 + 10, EY0 + EH / 2 + 19, ZT + 5.6, ZT + 16)
add('EX', 'Placa de expansión ESP32-S3', 'negro_mate', jack, grupo='elec', sub=3)
# ESP32-S3 DevKitC-1 encima
DX0, DY0 = EX0 + 20, EY0 + EH / 2 - 14
dz = ZT + 14
add('ESP', 'ESP32-S3 DevKitC-1', 'pcb_negro', bx(DX0, DX0 + 63, DY0, DY0 + 25.5, dz, dz + 1.6), grupo='elec', sub=0)
add('ESP', 'ESP32-S3 DevKitC-1', 'acero', bx(DX0 + 40, DX0 + 58, DY0 + 3, DY0 + 22.5, dz + 1.6, dz + 4.8), grupo='elec', sub=1)
add('ESP', 'ESP32-S3 DevKitC-1', 'acero', bx(DX0 - 1.5, DX0 + 6, DY0 + 2.5, DY0 + 11.5, dz + 1.6, dz + 4.8) + bx(DX0 - 1.5, DX0 + 6, DY0 + 14, DY0 + 23, dz + 1.6, dz + 4.8), grupo='elec', sub=2)
add('ESP', 'ESP32-S3 DevKitC-1', 'oro', sum([bx(DX0 + 5 + 2.54 * i, DX0 + 5.6 + 2.54 * i, DY0 + yy, DY0 + yy + 0.6, dz - 6, dz) for i in range(22) for yy in (1.2, 23.7)], M()), grupo='elec', sub=3)
add('ESP', 'ESP32-S3 DevKitC-1', 'led_rgb', cz(DX0 + 33, DY0 + 6, dz + 1.6, 1.0, 1.2), grupo='elec', sub=4)
out['anclas']['ESP'] = [DX0 + 30, DY0 + 12, dz + 5]
out['anclas']['EX'] = [EX0 + 8, EY0 + 6, ZT + 6]
# protoboard 400 puntos con el A4988
PX0, PY0 = -180.0, -265.0
add('PB', 'Protoboard', 'blanco_proto', bx(PX0, PX0 + 82.5, PY0, PY0 + 55, ZT, ZT + 8.5), grupo='elec', sub=0)
add('PB', 'Protoboard', 'rojo', bx(PX0 + 4, PX0 + 78, PY0 + 2.2, PY0 + 2.8, ZT + 8.5, ZT + 8.6) + bx(PX0 + 4, PX0 + 78, PY0 + 52.2, PY0 + 52.8, ZT + 8.5, ZT + 8.6), grupo='elec', sub=1)
add('PB', 'Protoboard', 'azul_linea', bx(PX0 + 4, PX0 + 78, PY0 + 9.2, PY0 + 9.8, ZT + 8.5, ZT + 8.6) + bx(PX0 + 4, PX0 + 78, PY0 + 45.2, PY0 + 45.8, ZT + 8.5, ZT + 8.6), grupo='elec', sub=2)
out['anclas']['PB'] = [PX0 + 70, PY0 + 50, ZT + 9]
AX, AY = PX0 + 14, PY0 + 20
z9 = ZT + 8.5
add('A4', 'Driver A4988', 'pcb_rojo', bx(AX, AX + 20.3, AY, AY + 15.2, z9 + 3, z9 + 4.6), grupo='elec', sub=0)
add('A4', 'Driver A4988', 'aluminio', bx(AX + 6, AX + 15, AY + 3, AY + 12, z9 + 4.6, z9 + 5.6) + sum([bx(AX + 6 + 1.6 * k, AX + 6.8 + 1.6 * k, AY + 3, AY + 12, z9 + 5.6, z9 + 11) for k in range(6)], M()), grupo='elec', sub=1)
add('A4', 'Driver A4988', 'negro_mate', bx(AX + 0.8, AX + 19.5, AY + 0.3, AY + 2.7, z9, z9 + 3) + bx(AX + 0.8, AX + 19.5, AY + 12.5, AY + 14.9, z9, z9 + 3), grupo='elec', sub=2)
out['anclas']['A4'] = [AX + 10, AY + 7, z9 + 11]
add('CP', 'Condensador 100 µF', 'negro_cap', cz(AX + 32, AY + 8, z9, 12, 4), grupo='elec', sub=0)
add('CP', 'Condensador 100 µF', 'aluminio', cz(AX + 32, AY + 8, z9 + 12, 0.4, 3.6), grupo='elec', sub=1)
out['anclas']['CP'] = [AX + 32, AY + 8, z9 + 13]
# resistencias de las barreras IR
for k in range(3):
    rx = PX0 + 56 + k * 6
    add('RS', 'Resistencias 330 Ω y 10 kΩ', 'resistencia', cx(PY0 + 30, z9 + 4, rx - 0.1, 6.2, 1.2).rotate((0, 0, 0)).translate((0, 0, 0)) if False else M.cylinder(6.2, 1.2).rotate((90, 0, 0)).translate((rx, PY0 + 33, z9 + 3)), grupo='elec')
out['anclas']['RS'] = [PX0 + 62, PY0 + 30, z9 + 5]
# ULN2003
UX, UY = -170.0, -200.0
add('UL', 'Driver ULN2003', 'pcb_verde', bx(UX, UX + 35, UY, UY + 32, ZT + 3, ZT + 4.6) + sum([cz(UX + a, UY + b, ZT, 3, 1.4) for a in (2.5, 32.5) for b in (2.5, 29.5)], M()), grupo='elec', sub=0)
add('UL', 'Driver ULN2003', 'negro_mate', bx(UX + 6, UX + 25, UY + 10, UY + 17, ZT + 4.6, ZT + 8), grupo='elec', sub=1)
add('UL', 'Driver ULN2003', 'blanco', bx(UX + 26, UX + 33, UY + 4, UY + 18, ZT + 4.6, ZT + 11), grupo='elec', sub=2)
add('UL', 'Driver ULN2003', 'led_rojo', sum([cz(UX + 8 + 4 * k, UY + 25, ZT + 4.6, 2.0, 1.5) for k in range(4)], M()), grupo='elec', sub=3)
out['anclas']['UL'] = [UX + 12, UY + 18, ZT + 8]
# fuente de 12 V (adaptador) sobre la mesa
add('FU', 'Fuente 12 V 2 A', 'negro_mate', bx(-370, -320, -250, -215, 0, 30), grupo='elec', sub=0)
add('FU', 'Fuente 12 V 2 A', 'aluminio', bx(-372, -370, -240, -225, 10, 20), grupo='elec', sub=1)
out['anclas']['FU'] = [-345, -232, 31]
out['anclas']['BA'] = [TX1 - 10, TY1 - 4, 22]

# ------------------------------------------------------------------ cables (polilíneas; el visor las convierte en tubos)
A = out['anclas']
R_ = lambda p, dx=0, dy=0, dz=0: [p[0] + dx, p[1] + dy, p[2] + dz]
salida = [-205.0, -137.0, 24.0]          # boca de la caja hacia la torre
leg = [-200.0, -103.0]                   # pata -Y del caballete 1, por donde suben los cables a la tolva y la pista
cables = []
def cab(colores, pts, de, a):
    cables.append(dict(c=colores, p=[[round(float(t), 1) for t in q] for q in pts], de=de, a=a))
pin_esp = lambda k: [DX0 + 6 + 2.54 * k, DY0 + 1.5, dz + 2]
# 28BYJ-48 -> ULN2003 (cable propio del motor)
m1 = A['M1c']
cab(['azul', 'rosa', 'amarillo', 'naranja', 'rojo'], [R_(A['UL'], 18, -12, 0), [UX + 30, -150, 26], salida, [leg[0] - 8, leg[1] - 4, 30], [leg[0] - 8, leg[1] - 4, 150], [m1[0] - 10, -60, 200], R_(m1, 0, -8, 0)], 'UL', 'M1')
# ULN2003 IN1-4 <- ESP32 (GPIO 4-7)
cab(['naranja', 'amarillo', 'verde', 'azul'], [pin_esp(3), R_(pin_esp(3), 0, 0, 14), [UX - 6, UY + 12, 20], [UX + 2, UY + 12, ZT + 6]], 'ESP', 'UL')
# SG90 -> ESP32 GPIO 15 (y 5 V)
sv = A['SV']
cab(['naranja', 'rojo', 'marron'], [pin_esp(12), R_(pin_esp(12), 0, 0, 16), salida, [leg[0] + 30, leg[1] - 4, 30], [-84, -103, 30], [-84, -103, 150], [10, -80, 152], R_(sv, 10, -5, 0)], 'ESP', 'SV')
# TCS3200 -> GPIO 14,16,17,18,21
tc = A['TC']
cab(['blanco', 'gris', 'violeta', 'azul', 'verde', 'rojo', 'negro'], [pin_esp(10), R_(pin_esp(10), 0, 0, 18), salida, [leg[0] + 14, leg[1] - 4, 30], [-84 - 6, -103, 30], [-90, -103, 170], [tc[0] - 10, -60, 230], R_(tc, 0, -18, 6), tc], 'ESP', 'TC')
# barreras IR de la pista -> GPIO 1 y 2 (receptores) y 5 V (emisores)
for k in (1, 2):
    e, r = A[f'IE{k}'], A[f'IR{k}']
    cab(['rojo', 'negro'], [R_(A['PB'], -10 * k, 0, 0), R_(A['PB'], -10 * k, 0, 16), salida, [leg[0] + 2 + 4 * k, leg[1] - 4, 30], [leg[0] + 2 + 4 * k, leg[1] - 4, 180], [e[0] - 8, -50, 215], R_(e, 0, -10, 0), e], 'PB', f'IE{k}')
    cab(['amarillo', 'negro'], [pin_esp(k - 1), R_(pin_esp(k - 1), 0, 0, 12 + 3 * k), salida, [leg[0] + 4 * k, leg[1] - 6, 30], [leg[0] + 4 * k, leg[1] - 6, 185], [r[0] - 6, -40, 240], [r[0], 45, 252], R_(r, 0, 10, 4), r], 'ESP', f'IR{k}')
# NEMA17 -> A4988 (cable JST de 4 hilos)
k1 = A['K1']
cab(['negro', 'verde', 'rojo', 'azul'], [k1, R_(k1, -12, 0, 0), [XP - 40, -118, 6], [AX + 24, -150, 8], [AX + 22, AY + 15, z9 + 4]], 'A4', 'K1')
# A4988 STEP/DIR/EN <- GPIO 10, 11, 12
cab(['verde', 'amarillo', 'blanco'], [pin_esp(8), R_(pin_esp(8), 0, 0, 12), [AX - 4, AY + 2, 20], [AX + 3, AY + 1, z9 + 3]], 'ESP', 'A4')
# barrera de referencia de la banda -> GPIO 13
ie3, ir3 = A['IE3'], A['IR3']
cab(['amarillo', 'negro'], [pin_esp(11), R_(pin_esp(11), 0, 0, 13), [TX0 + 30, TY1 + 4, 26], [v.IR_X, -110, 6], [v.IR_X, ir3[1] - 6, 10], ir3], 'ESP', 'IR3')
cab(['rojo', 'negro'], [R_(A['PB'], -40, 0, 0), R_(A['PB'], -40, 0, 14), [TX0 + 50, TY1 + 4, 24], [v.IR_X - 14, -110, 4], [v.IR_X - 14, 60, 4], [v.IR_X, 50, v.Z_IR], ie3], 'PB', 'IE3')
# fuente -> jack de la placa; 12 V de la placa -> VMOT del A4988
cab(['negro'], [A['FU'], [-345, -232, 40], [-320, -190, 30], [EX0 - 2, EY0 + EH / 2 + 14.5, ZT + 11]], 'FU', 'EX')
cab(['rojo', 'negro'], [[EX0 + 4, EY0 + EH - 6, ZT + 8], [EX0 + 40, EY0 + EH + 10, 22], [AX + 34, AY + 14, 22], [AX + 32, AY + 11, z9 + 2]], 'EX', 'CP')
out['cables'] = cables
out['banda'] = dict(desp0=v.DESP0, umax=774, xp=v.XP, zc=v.ZC, rp=v.RP, a0=333.5, x0=v.X_CTR0, xbarra=[v.X_T0, v.XPEG + 9])
json.dump(out, open(sys.argv[3], 'w'), separators=(',', ':'))
print('piezas', len(out['piezas']), 'cables', len(cables), 'MB', round(sum(len(p['v']) + len(p['t']) for p in out['piezas']) / 1e6, 2))
