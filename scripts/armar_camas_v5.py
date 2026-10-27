# Acomoda piezas STL de v5 en camas de 220x220 y las guarda como .3mf
import sys, numpy as np, trimesh
from shapely.ops import unary_union
from shapely import affinity
from shapely.geometry import box
import os
STL=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","hardware","etapa1-clasificador","v5","stl")+os.sep
BED=box(4,4,216,216); GAP=4
def footprint(m):
    tris=[trimesh.path.polygons.Polygon(t[:,:2]) for t in m.triangles]
    tris=[t for t in tris if t.area>1e-6]
    return unary_union(tris).buffer(0.01)
def pack(parts):
    placed=[]; occ=None
    for name,m,_ in sorted(parts,key=lambda p:-p[2].area):
        best=None
        for r in (0,90,180,270):
            fp=affinity.rotate(m[1],r,origin=(0,0)); mm=m[0].copy()
            mm.apply_transform(trimesh.transformations.rotation_matrix(np.radians(r),[0,0,1]))
            x0,y0,_,_=fp.bounds; fp=affinity.translate(fp,-x0,-y0); mm.apply_translation([-x0,-y0,-mm.bounds[0][2]])
            fb=fp.buffer(GAP/2)
            for y in np.arange(4,216,2):
                for x in np.arange(4,216,2):
                    c=affinity.translate(fp,x,y)
                    if not BED.contains(c): continue
                    if occ is not None and affinity.translate(fb,x,y).intersects(occ): continue
                    if best is None or (y,x)<best[:2]: best=(y,x,r,c,mm,affinity.translate(fb,x,y))
                    break
                if best and best[0]<=y: break
        if best is None: return None,name
        y,x,r,c,mm,cb=best; mm.apply_translation([x,y,0])
        occ=cb if occ is None else occ.union(cb); placed.append((name,mm))
    return placed,None
if __name__=="__main__":
    out=sys.argv[1]; parts=[]; cache={}
    for s in sys.argv[2:]:
        n,k=(s.split("x")+["1"])[:2]
        m=trimesh.load(STL+n+".stl"); m.apply_translation(-m.bounds[0]); fp=footprint(m)
        for i in range(int(k)): parts.append((f"{n}_{i+1}" if int(k)>1 else n,(m,fp),fp))
    placed,fail=pack(parts)
    if fail: print("NO CABE",fail); sys.exit(1)
    sc=trimesh.Scene()
    for n,m in placed: sc.add_geometry(m,node_name=n,geom_name=n)
    sc.export(out); print("OK",out,len(placed))
