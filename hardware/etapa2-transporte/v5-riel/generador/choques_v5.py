import os, sys, json, base64, itertools
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manifold3d import Manifold, Mesh
import generar_v5 as v
from generar_banda import caja
import torre_ref as tr
T = tr.cargar()
fijas = dict(v.piezas()); fijas.pop('CA')
carro0 = v.carro(v.X_CTR0)
torre = {f'T{i}{c}': m for i, (c, gp, m) in enumerate(T) if gp not in ('cartucho', 'vaso')}
cartucho = [(c, m) for c, gp, m in T if gp in ('cartucho', 'vaso')]
rechazo = v.cil_z(0.0, 60.0, 0.0, 60.0, 34.0)
mal = 0
def chk(a, b, A, B, tol=0.5):
    global mal
    vol = (A ^ B).volume()
    if vol > tol:
        print('  CHOQUE', a, b, round(vol, 1)); mal += 1
nombres = [k for k in fijas]
for a, b in itertools.combinations(nombres, 2):
    if {a, b} <= {'PM', 'K1'}: continue
    chk(a, b, fijas[a], fijas[b])
for us in (0, 100, 250, 342, 500, 650, 774):
    c = carro0.translate((us, 0, 0)); cart = v.cartucho_ref(us)
    for k, m in {**fijas}.items(): chk(f'CA@{us}', k, c, m)
    chk(f'CA@{us}', 'cartucho', c, cart)
    for k, m in fijas.items(): chk(f'cartucho@{us}', k, cart, m)
    for k, m in torre.items(): chk(f'CA@{us}', k, c, m)
for k, m in torre.items():
    for kk, mm in fijas.items(): chk(k, kk, m, mm)
# hilo: dos cabos arriba (z 43,5) y uno abajo (z 4,5) como cajas de 1 mm
hilos = {'arriba': caja(v.XM, v.X_P, v.Y_HILO_C - 0.5, v.Y_HILO_C + 0.5, v.Z_HILO - 0.5, v.Z_HILO + 0.5), 'abajo': caja(v.XM, v.X_P, v.Y_HILO_C - 2, v.Y_HILO_C + 2, v.ZC - v.R_EFF - 1.2, v.ZC - v.R_EFF + 1.2)}
for h, hm in hilos.items():
    for k, m in {**fijas, **torre}.items():
        if k in ('PM', 'PL', 'EJ'): continue
        chk('hilo ' + h, k, hm, m, tol=0.05)
    pass
for us in range(0, 775, 6):
    c = carro0.translate((us, 0, 0))
    for n, m in cartucho:
        mm = m.translate((v.DESP0 + us, 0, 0))
        for k, f in {**fijas, 'CA': c}.items(): chk(f'{n}@{us}', k, mm, f)
chk('vaso de rechazo', 'CA', rechazo, carro0.translate((342, 0, 0)))
for k, f in fijas.items(): chk('vaso de rechazo', k, rechazo, f)
print('choques:', mal, ' torre piezas:', len(torre))
