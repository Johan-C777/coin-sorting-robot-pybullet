"""Simulación de tolerancias de impresión: engrane piñón-barra con los flancos engordados (o adelgazados) e mm por lado."""
import math, numpy as np
import generar_v7 as v
from manifold3d import Manifold, CrossSection, JoinType, OpType

def perfil_barra(k0, k1):
    pts = [(v.valle(k0), 0.0), (v.valle(k1), 0.0), (v.valle(k1), v.Z_RAIZ)]
    for k in range(k1 - 1, k0 - 1, -1):
        pts += v.diente(v.valle(k) + v.PASO / 2, v.Z_RAIZ)
    pts.append((v.valle(k0), v.Z_RAIZ))
    return pts

def barra3d(e, k0=156, k1=181):
    cs = CrossSection([perfil_barra(k0, k1)])
    if e:    # el sobrante de extrusión crece en X (plano de la capa); en Z la altura es exacta
        cs = CrossSection.batch_boolean([cs.translate((e, 0)), cs.translate((-e, 0)), cs], OpType.Add) if e > 0 else (CrossSection.batch_boolean([cs.translate((e, 0)), cs.translate((-e, 0))], OpType.Intersect) if e < 0 else cs)
    m = cs.extrude(v.Y_BAR[1] - v.Y_BAR[0])            # (x, z) -> extrusión en z local
    m = m.rotate((90, 0, 0))                          # (x, y, z) -> (x, -z, y): extrusión hacia -Y
    return m.translate((0, v.Y_BAR[1], v.BASE_T))

def pinon3d(e, giro, dz=0.0):
    cs = CrossSection([v.perfil_pinon()])
    if e: cs = cs.offset(e, JoinType.Miter, 2)
    m = cs.extrude(v.Y_PIN[1] - v.Y_PIN[0]).rotate((0, 0, giro)).rotate((90, 0, 0))
    return m.translate((v.XP, v.Y_PIN[1], v.ZC + dz))

def interferencia(e_p, e_b, dz=0.0, paso=0.4):
    """Máximo solape (mm3) sobre un paso de engrane, con el piñón rodando sobre la barra."""
    peor = 0.0
    for s in np.arange(0, v.PASO, paso):
        # la barra avanza s: equivale a trasladarla; el piñón gira A0 + s/RP
        b = barra3d(e_b).translate((s, 0, 0))
        g = 333.5 + s / v.RP * 180 / math.pi
        # la barra está en x ~ valle(100..125): centrarla bajo el piñón
        p = pinon3d(e_p, g, dz)
        peor = max(peor, (p ^ b).volume())
    return peor

def subida_necesaria(e_p, e_b):
    """Cuánto hay que separar el piñón de la barra (mm) para que no haya interferencia en ningún punto."""
    if interferencia(e_p, e_b) < 0.01: return 0.0
    lo, hi = 0.0, 1.0
    for _ in range(7):
        mid = (lo + hi) / 2
        if interferencia(e_p, e_b, mid) < 0.01: hi = mid
        else: lo = mid
    return hi

if __name__ == '__main__':
    print('e mm por lado (piñón y barra, la barra solo en X) -> separación extra necesaria entre ejes (mm)')
    for e in (0.0, 0.03, 0.05, 0.08, 0.10, 0.15):
        print(f'e = {e:+.2f}: {subida_necesaria(e, e):.3f}', flush=True)
