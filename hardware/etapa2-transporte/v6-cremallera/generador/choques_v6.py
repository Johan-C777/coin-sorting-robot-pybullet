"""Choques de la v6: el carro con el motor y el piñón recorre el riel (con cremallera) bajo la torre y el cartucho reales de la etapa 1."""
import os, sys, math, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_v6 as v
import torre_ref as tr
from generar_banda import caja
A0 = 12.0                                              # fase del piñón con el carro en x = 40 (conjugada con la cremallera)
def fase(xc): return A0 - (xc - 40.0) / v.RP * 180 / math.pi
T = tr.cargar()
torre = {f'T{i}{c}': m for i, (c, gp, m) in enumerate(T) if gp not in ('cartucho', 'vaso')}
cartucho = [(c, m) for c, gp, m in T if gp in ('cartucho', 'vaso')]
rechazo = v.cil_z(0.0, 60.0, 0.0, 60.0, 34.0)
rieles = {f'S{i+1}': v.segmento(i) for i in range(len(v.SEG))}
ca0, k0 = v.carro(0.0), v.nema_ref(0.0)
mal = 0
def chk(a, b, A, B, tol=0.5):
    global mal
    vol = (A ^ B).volume()
    if vol > tol:
        print('  CHOQUE', a, b, round(vol, 1)); mal += 1
def conj(xc):
    return {'CA': ca0.translate((xc, 0, 0)), 'K1': k0.translate((xc, 0, 0)), 'PI': v.pinon_colocado(xc, fase(xc))}
# piezas entre sí en una posición
c = conj(v.X_CTR0 + 300)
chk('CA', 'K1', c['CA'], c['K1']); chk('CA', 'PI', c['CA'], c['PI'])
chk('PI', 'K1 (eje)', c['PI'], c['K1'], tol=5.0)
for us in list(range(0, 775, 6)) + [342, 774]:
    xc = v.X_CTR0 + us
    cj = conj(xc)
    for k, m in rieles.items():
        for n, p in cj.items():
            chk(f'{n}@{us}', k, p, m, tol=0.5)
    cart = v.b.cartucho_ref(us)
    for n, p in cj.items():
        chk(f'{n}@{us}', 'cartucho ref', p, cart)
    for k, m in torre.items():
        for n, p in cj.items(): chk(f'{n}@{us}', k, p, m)
    for n, m in cartucho:
        mm = m.translate((v.DESP0 + us, 0, 0))
        for k, p in cj.items(): chk(f'{n}@{us}', k, mm, p)
        for k, f in rieles.items(): chk(f'{n}@{us}', k, mm, f)
for k, m in torre.items():
    for kk, mm in rieles.items(): chk(k, kk, m, mm)
for us in (342,):
    cj = conj(v.X_CTR0 + us)
    for n, p in cj.items(): chk('vaso de rechazo', n, rechazo, p)
for kk, mm in rieles.items(): chk('vaso de rechazo', kk, rechazo, mm)
print('choques:', mal, ' piezas de torre:', len(torre))
