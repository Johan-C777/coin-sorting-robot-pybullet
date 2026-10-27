"""Adaptador TCS3200 (4 LED) para L01 v5, version "corte": se quita el bloque del TCS34725 y esto lo sustituye.
Marco de L01: X a lo largo, Y frente (-), Z arriba. Uso: python -I generar_adaptador_tcs3200.py [salida] [L01.stl]
"""
import sys, os
import numpy as np, trimesh
from manifold3d import Manifold

CX = 66.5                              # centro del bloque de L01
BX0, BX1 = 55.5, 77.5                  # bloque: x
BY0, BY1 = -8.0, -2.5                  # bloque: y
LEDGE_Y = -3.5                         # frente de la repisa fuera del bloque
Z_CORTE = 6.0                          # corte a ras del piso de la pista
PLACA, HOLG = 28.5, 0.6                # placa TCS3200, holgura por lado
LIP, T = 1.2, 1.6                      # solapa sobre el borde, grosor de rieles
PCB_T = 1.8                            # grosor placa + holgura
SHELF = 1.6
LUG_H, LUG_T = 4.0, 1.6

def box(x0,x1,y0,y1,z0,z1):
    return Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))

def adaptador():
    h = PLACA/2 + HOLG                 # medio bolsillo
    z0 = Z_CORTE
    zb = z0 + SHELF                    # asiento de la placa
    zt = zb + PLACA                    # borde superior de la placa
    yb0 = BY0                          # cara trasera = cara frontal de L01
    yb1 = yb0 + 1.9                    # placa trasera
    yf = yb1 + PCB_T                   # cara frontal de la placa
    y_lip1 = yf + LIP
    xa, xb = CX-h, CX+h
    m = box(xa-T, xb+T, yb0, yb1, z0, zt)                           # placa trasera
    m += box(xa-T, xb+T, yb0, y_lip1, z0, zb)                       # asiento
    for x0,x1,l0,l1 in ((xa-T,xa,xa,xa+LIP),(xb,xb+T,xb-LIP,xb)):   # rieles laterales + solapas
        m += box(x0, x1, yb0, y_lip1, z0, zt)
        m += box(l0, l1, yf, y_lip1, zb, zt)
    m += box(xa, xb, yf, y_lip1, zb, zb+LIP)                        # solapa inferior
    # patillas que abrazan el muñon del bloque (centran en X y apoyan por delante)
    for x0,x1 in ((BX0-0.2-LUG_T, BX0-0.2),(BX1+0.2, BX1+0.2+LUG_T)):
        m += box(x0, x1, BY0, LEDGE_Y-0.2, z0-LUG_H, z0)
    m += box(BX0-0.2-LUG_T, BX1+0.2+LUG_T, BY0-LUG_T, BY0, z0-LUG_H, z0+SHELF)  # faldon frontal
    return m, dict(zb=zb, zt=zt, yf=yf, centro_z=zb+PLACA/2)

def a_trimesh(man):
    mm = man.to_mesh()
    return trimesh.Trimesh(np.asarray(mm.vert_properties)[:,:3], np.asarray(mm.tri_verts))

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv)>1 else "."
    os.makedirs(out, exist_ok=True)
    man, info = adaptador(); ad = a_trimesh(man)
    ad.export(f"{out}/A01_adaptador_tcs3200.stl")
    print("A01", ad.is_watertight, ad.bounds.round(1).tolist(), info)
    if len(sys.argv)>2:
        l = trimesh.load(sys.argv[2])
        corte = box(BX0-0.01,BX1+0.01,BY0-0.01,BY1+0.01,Z_CORTE,40.0)       # L01 sin el bloque
        from trimesh.boolean import difference, intersection
        cutter = a_trimesh(corte)
        l2 = difference([l, cutter], engine="manifold")
        inter = intersection([ad, l2], engine="manifold")
        print("choque con L01 cortada (mm3):", round(inter.volume,3) if len(inter.vertices) else 0)
