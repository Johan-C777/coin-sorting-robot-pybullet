"""Choques de la v7: el carro, el brazo, la barra dentada y el cartucho recorren u = 0 a 774 contra el riel, el soporte fijo del motor, el piñón, el motor y la torre de la etapa 1."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_v7 as v
import torre_ref as tr
A0 = 333.5
def fase(u): return A0 + u / v.RP * 180 / math.pi
T = tr.cargar()
torre = {f'T{i}{c}': m for i, (c, gp, m) in enumerate(T) if gp not in ('cartucho', 'vaso')}
cartucho = [(c, m) for c, gp, m in T if gp in ('cartucho', 'vaso')]
rechazo = v.cil_z(0.0, 60.0, 0.0, 60.0, 34.0)
rieles = {f'R{i+1}': v.segmento(i) for i in range(len(v.SEG))}
ca0, bz0 = v.carro(v.X_CTR0), v.brazo(v.X_CTR0)
sop, k1 = v.soporte(), v.nema_ref()
tramos = [v.tramo_barra(j) for j in range(4)]
mal = 0
def chk(a, b, A, B, tol=0.5):
    global mal
    vol = (A ^ B).volume()
    if vol > tol:
        print('  CHOQUE', a, b, round(vol, 1)); mal += 1
paso = int(sys.argv[1]) if len(sys.argv) > 1 else 6
for us in list(range(0, 775, paso)) + [342, 774]:
    mov = {'CA': ca0.translate((us, 0, 0)), 'BZ': bz0.translate((us, 0, 0))}
    for j, t in enumerate(tramos): mov[f'B{j+1}'] = t.translate((us, 0, v.BASE_T))
    fij = {'SOP': sop, 'K1': k1, 'PI': v.pinon_colocado(fase(us))}
    fij.update(rieles); fij.update(torre); fij['rechazo'] = rechazo
    for n, p in mov.items():
        bb = p.bounding_box()
        for k, f in fij.items():
            fb = f.bounding_box()
            if fb[3] < bb[0] or fb[0] > bb[3] or fb[4] < bb[1] or fb[1] > bb[4] or fb[5] < bb[2] or fb[2] > bb[5]: continue
            if (n.startswith('B') and n != 'BZ') and k == 'PI': chk(f'{n}@{us}', k, p, f, tol=0.6); continue
            chk(f'{n}@{us}', k, p, f)
    for n, m in cartucho:
        mm = m.translate((v.DESP0 + us, 0, 0))
        for k in ('SOP', 'K1', 'PI'): chk(f'{n}@{us}', k, mm, fij[k])
        for k, p in mov.items(): chk(f'{n}@{us}', k, mm, p)
    # los móviles entre sí
    for a, b_ in (('CA', 'BZ'),):
        chk(a, b_, mov[a], mov[b_], tol=0.5)
    for k in ('B1', 'B2', 'B3', 'B4'):
        chk('CA', k, mov['CA'], mov[k]); chk('BZ', k, mov['BZ'], mov[k], tol=3.0)
print('choques:', mal)
