"""Análisis tipo rebanador: por cada capa, lo que no apoya en la capa anterior (con 45 grados de tolerancia)."""
import os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generar_banda as g, analisis as an
from manifold3d import CrossSection, JoinType
def islas(m, h=0.2, tol=None, minw=0.5):
    tol = h if tol is None else tol
    z0,z1 = m.bounding_box()[2], m.bounding_box()[5]
    prev=None; out=[]
    z=z0+h/2
    while z<z1:
        A=m.slice(z)
        if prev is not None and not A.is_empty():
            sup=prev.offset(tol,JoinType.Round,12) if not prev.is_empty() else CrossSection()
            U=A-sup
            U=U.offset(-minw/2,JoinType.Round,8).offset(minw/2,JoinType.Round,8)   # ignora lo más fino que minw
            for p in U.decompose():
                a=p.area()
                if a>0.2:
                    b=p.bounds(); out.append((round(z-z0,2),round(a,2),[round(x,1) for x in b]))
        prev=A; z+=h
    return out
if __name__=='__main__':
    for pid,rot in (('BT19',(0,0,0)),):
        for p,m,ex in g.piezas():
            if p==pid:
                mm,_=an.pose(m,rot); r=islas(mm)
                print(pid,'capas con isla',len(r),'area',round(sum(x[1] for x in r),1))
                for x in r[:20]: print(' ',x)
                break
