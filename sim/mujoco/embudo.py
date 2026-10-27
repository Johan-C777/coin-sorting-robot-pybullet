import sys, math, numpy as np, mujoco
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from riel_canto import MONEDAS, _quat

def run(moneda, v0, mu=0.45, pend=22.0, lean=20.0, x_end=60.0, rim=70.0, hole=16.5, alpha=28.0, fx=95.0, fz=-70.0, fy=0.0, tmax=5.0, mu_emb=None):
    d,e,m = MONEDAS[moneda]
    p=math.radians(pend); g=math.radians(lean)
    Rp=np.column_stack([[math.cos(p),0,-math.sin(p)],[0,1,0],[math.sin(p),0,math.cos(p)]])
    ex=np.array([1.0,0,0]); n_=np.array([0,math.cos(g),math.sin(g)]); p_=np.array([0,-math.sin(g),math.cos(g)])
    f=lambda v:f"{v:.6f}"
    def box(center_L, axes_cols, half, fr=mu, rgba=".6 .6 .7 1"):
        c=Rp@center_L; q=_quat(Rp@axes_cols)
        return (f'<geom type="box" pos="{f(c[0]/1000)} {f(c[1]/1000)} {f(c[2]/1000)}" quat="{q[0]:.6f} {q[1]:.6f} {q[2]:.6f} {q[3]:.6f}" '
                f'size="{f(half[0]/1000)} {f(half[1]/1000)} {f(half[2]/1000)}" friction="{fr} 0 0" solref="0.004 1" rgba="{rgba}"/>')
    ax=np.column_stack([ex,n_,p_])
    x0=-40.0; xc=(x0+x_end)/2; hx=(x_end-x0)/2
    geoms=[]
    geoms.append(box(xc*ex+6.0*n_-1.5*p_, ax, (hx,6.0,1.5)))            # repisa
    geoms.append(box(xc*ex+35*p_-2.0*n_, ax, (hx,2.0,35.0)))            # placa
    # embudo (mundo)
    E=Rp@(x_end*ex)
    Fc=E+np.array([fx,fy,fz])
    fr_e = mu if mu_emb is None else mu_emb
    N=28; al=math.radians(alpha)
    rm=(rim+hole)/2; slant=(rim-hole)/math.cos(al)
    for i in range(N):
        th=2*math.pi*i/N
        r_hat=np.array([math.cos(th),math.sin(th),0]); t_hat=np.array([-math.sin(th),math.cos(th),0])
        s_hat=np.array([ -math.cos(al)*r_hat[0], -math.cos(al)*r_hat[1], -math.sin(al)])  # hacia abajo/adentro
        # pendiente: la pared sube hacia afuera -> s_hat apunta hacia adentro y abajo
        nrm=np.cross(t_hat,s_hat)
        if nrm[2]<0:
            s_hat=-s_hat; nrm=np.cross(t_hat,s_hat)
        cen=Fc+r_hat*rm+np.array([0,0,(rm-hole)*math.tan(al)])
        # centro en mundo; construir geom con ejes (t_hat, s_hat, nrm)
        Rm=np.column_stack([t_hat,s_hat,nrm])
        q=_quat(Rm); chord=2*rim*math.tan(math.pi/N)*1.08
        geoms.append(f'<geom type="box" pos="{f(cen[0]/1000)} {f(cen[1]/1000)} {f(cen[2]/1000)}" quat="{q[0]:.6f} {q[1]:.6f} {q[2]:.6f} {q[3]:.6f}" size="{f(chord/2000)} {f(slant/2000)} {f(1.5/1000)}" friction="{fr_e} 0 0" solref="0.004 1" rgba=".7 .6 .5 1"/>')
        if abs(th-math.pi)<math.radians(40): continue   # ventana de entrada (lado de la pista)
        # pared exterior (borde) para que no se salga
        cen2=Fc+r_hat*(rim+3)+np.array([0,0,(rim-hole)*math.tan(al)+45])
        Rm2=np.column_stack([t_hat,np.array([0,0,1.0]),r_hat])
        q2=_quat(Rm2)
        geoms.append(f'<geom type="box" pos="{f(cen2[0]/1000)} {f(cen2[1]/1000)} {f(cen2[2]/1000)}" quat="{q2[0]:.6f} {q2[1]:.6f} {q2[2]:.6f} {q2[3]:.6f}" size="{f(chord/2000)} {f(10/1000)} {f(1.5/1000)}" friction="{fr_e} 0 0" solref="0.004 1" rgba=".7 .6 .5 .3"/>')
    zt=Fc[2]+(rim-hole)*math.tan(al)+90
    geoms.append(f'<geom type="cylinder" pos="{f(Fc[0]/1000)} {f(Fc[1]/1000)} {f((zt+1.5)/1000)}" size="{f((rim+8)/1000)} {f(1.5/1000)}" friction="{fr_e} 0 0" solref="0.004 1" rgba=".7 .6 .5 .2"/>')
    # moneda: parada, apoyada en placa, rodando
    cL=(x0+15)*ex+(e/2+0.1)*n_+(d/2+0.05)*p_
    cw=Rp@cL; qc=_quat(Rp@np.column_stack([p_,ex,n_]))  # eje z de la moneda = n_
    # cilindro de mujoco tiene eje z local -> columnas (ex, p_?, n_) con z=n_
    vel=Rp@(v0*ex); w=-Rp@((v0/(d/2000.0))*n_)  # rad/s con v en mm/s -> usar m/s
    xml=f"""<mujoco><option timestep="0.0004" gravity="0 0 -9.81" cone="elliptic" impratio="5"/><worldbody>
{chr(10).join(geoms)}
<body name="moneda" pos="{f(cw[0]/1000)} {f(cw[1]/1000)} {f(cw[2]/1000)}" quat="{qc[0]:.6f} {qc[1]:.6f} {qc[2]:.6f} {qc[3]:.6f}"><freejoint/>
<geom type="cylinder" size="{f(d/2000)} {f(e/2000)}" mass="{f(m/1000)}" friction="{mu} {f(mu*2*d/6000)} 0" condim="4" solref="0.004 1"/></body></worldbody></mujoco>"""
    mod=mujoco.MjModel.from_xml_string(xml); dat=mujoco.MjData(mod)
    dat.qvel[:3]=vel  # m/s
    dat.qvel[3:6]=Rp.T@Rp@w*0+w  # velocidad angular mundo (freejoint: angular en marco local? en mujoco free joint ang vel en marco local del cuerpo)
    # mujoco: qvel[3:6] es velocidad angular en el marco del cuerpo (local)
    R_body=Rp@np.column_stack([p_,ex,n_])
    dat.qvel[3:6]=R_body.T@w
    mujoco.mj_forward(mod,dat)
    z_exit=Fc[2]-25.0
    t_hole=None; esc=False; rim_max=0
    while dat.time<tmax:
        mujoco.mj_step(mod,dat)
        pos=dat.qpos[:3]*1000
        rad=math.hypot(pos[0]-Fc[0],pos[1]-Fc[1])
        if pos[2]<Fc[2]-3 and (Rp.T@pos)[0]>x_end:
            if rad<hole+6: t_hole=dat.time
            else: esc=True
            break
        if (Rp.T@pos)[0]>x_end+20 and (pos[2]<Fc[2]-60 or rad>rim+30):
            esc=True; break
    x_now=(Rp.T@(dat.qpos[:3]*1000))[0]
    return t_hole, esc, dat.time

if __name__=="__main__":
    import itertools
    res={}
    for v0 in (0.5,0.8,1.2):
        for mu in (0.3,0.45,0.7):
            ts=[]; bad=0; fails=[]
            for mn in MONEDAS:
                t,esc,tt=run(mn,v0,mu=mu)
                if t is None or esc:
                    bad+=1; fails.append((mn,'esc' if esc else 'tmo',round(tt,2)))
                else: ts.append(t)
            print("v0",v0,"mu",mu,"ok",len(ts),"/",len(MONEDAS),"t med %.2f max %.2f"%(np.median(ts) if ts else -1,max(ts) if ts else -1),fails,flush=True)
