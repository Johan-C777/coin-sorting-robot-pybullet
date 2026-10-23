import sys, math, re, numpy as np, mujoco
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import rodar
from rodar import *
from riel_canto import MONEDAS, _quat

def correr_gate(moneda, xg, G, mu=0.45, lean=20.0, pend=22.0, x0=30.0, u=22.0, S=700.0, L=60.0, tmax=4.0, saltos=(40,80,120,160)):
    d,e,m = MONEDAS[moneda]; dr=d
    ez=np.array([0,0,1.0]); ex=np.array([1.0,0,0]); ey=np.cross(ez,ex)
    q=_quat(np.column_stack([ex,ey,ez]))
    c=np.array([x0,-u,e/2+8.0])
    xm = rodar.xml(moneda,c,q,dr,L=L,mu=mu,lean=lean,pend=pend,pared=False)
    g=math.radians(lean)
    ex_=np.array([1.0,0,0]); p_=np.array([0,-math.sin(g),math.cos(g)]); n_=np.array([0,math.cos(g),math.sin(g)])
    ql=_quat(np.column_stack([ex_,n_,p_]))
    lab=12.0; f=lambda v:f"{v:.6f}"
    lines=xm.split("\n")
    # first geom after <worldbody> is the ledge
    i=[k for k,l in enumerate(lines) if '<worldbody>' in l][0]+1
    def geom(xa,xb):
        cx=(xa+xb)/2; cl=cx*ex_+(lab/2)*n_-1.5*p_
        return (f'<geom type="box" pos="{f(cl[0]/1000)} {f(cl[1]/1000)} {f(cl[2]/1000)}" quat="{ql[0]:.6f} {ql[1]:.6f} {ql[2]:.6f} {ql[3]:.6f}" '
                f'size="{f((xb-xa)/2000)} {f(lab/2000)} {f(1.5/1000)}" friction="{mu} 0 0" solref="0.004 1" rgba=".6 .6 .7 1"/>')
    lines[i]=geom(L-40,xg)+"\n"+geom(xg+G,S)
    mod=mujoco.MjModel.from_xml_string("\n".join(lines)); dat=mujoco.MjData(mod)
    bid=mod.body("bandeja").mocapid[0]
    th_fin=90.0-lean; pr=math.radians(pend)
    res={}; fell=False; ref=None
    while dat.time<tmax:
        th=th_fin*min(1.0,max(0.0,(dat.time-0.3)/1.0)) if dat.time>0.3 else 0.0
        dat.mocap_quat[bid]=_quat(rot_x_cols(th))
        mujoco.mj_step(mod,dat)
        pos=dat.qpos[:3]*1000
        xc=pos[0]; pc=pos@p_
        # coordenadas reales (la pista cae hacia +x con pendiente pend)
        Zv=-xc*math.sin(pr)+pos[2]*math.cos(pr); Xh=xc*math.cos(pr)+pos[2]*math.sin(pr)
        if not fell and xc>xg-2 and pc>0:
            if ref is None and xc>=xg: ref=(Xh,Zv,xc,float(dat.qvel[0]*1000),dat.time)
        if ref is not None:
            for s in saltos:
                if s not in res and ref[1]-Zv>=s: res[s]=(Xh-ref[0], pos[1]-(-u))
        if ref is not None and len(res)==len(saltos): break
    return ref,res

if __name__=="__main__":
    moneda=sys.argv[1]; xg=float(sys.argv[2]); G=float(sys.argv[3]); mu=float(sys.argv[4]); pend=float(sys.argv[5])
    ref,res=correr_gate(moneda,xg,G,mu=mu,pend=pend)
    print(moneda,xg,G,mu,pend,"v_gap",None if ref is None else round(ref[3]),"t",None if ref is None else round(ref[4],2),{k:(round(v[0]),round(v[1])) for k,v in res.items()})
