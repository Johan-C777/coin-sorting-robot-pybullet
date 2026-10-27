"""Alimentación por bandeja basculante + rodadura por gravedad + medición por tiempo de vuelo (dos barreras).
Marco: x = a lo largo de la pista, y = hacia el frente, z = arriba con la bandeja plana. La inclinación de la pista
(`pend`) se simula inclinando la gravedad hacia +x. La placa fija sigue a la bandeja (inclinada `lean` de la vertical)."""
from __future__ import annotations
import math
import numpy as np
import mujoco
from riel_canto import MONEDAS, _quat
from bandeja import rot_x_cols

H_BARRERA = 10.0


def xml(moneda, pos, quat, dr, L=60.0, W=48.0, lab=12.0, mu=0.4, lean=20.0, pend=20.0, S=700.0, solref="0.004 1", mu_placa=None, mu_flap=None, pared=True):
    d, e, m = MONEDAS[moneda]
    f = lambda v: f"{v:.6f}"
    g = math.radians(lean)
    ex = np.array([1.0, 0, 0]); p_ = np.array([0, -math.sin(g), math.cos(g)]); n_ = np.array([0, math.cos(g), math.sin(g)])
    ql = _quat(np.column_stack([ex, n_, p_]))
    cl = ((L - 40 + S) / 2) * ex + (lab / 2) * n_ - 1.5 * p_
    cp = ((L + S) / 2) * ex + 35 * p_ - 2.0 * n_
    qp = _quat(np.column_stack([ex, n_, p_]))
    q0 = _quat(rot_x_cols(0))
    mp = mu if mu_placa is None else mu_placa
    mf = mp if mu_flap is None else mu_flap
    muro = ""
    if pared:
        cw = (L + 1.5) * ex + 17.5 * p_ - 25.0 * n_
        qw = _quat(np.column_stack([ex, n_, p_]))
        muro = (f'<geom type="box" pos="{f(cw[0]/1000)} {f(cw[1]/1000)} {f(cw[2]/1000)}" quat="{qw[0]:.6f} {qw[1]:.6f} {qw[2]:.6f} {qw[3]:.6f}" '
                f'size="{f(1.5/1000)} {f(25/1000)} {f(22.5/1000)}" friction="{mp} 0 0" solref="{solref}" rgba=".5 .5 .5 1"/>')
    p = math.radians(pend)
    grav = f"{9.81*math.sin(p):.5f} 0 {-9.81*math.cos(p):.5f}"
    return f"""<mujoco>
  <option timestep="0.0004" gravity="{grav}" cone="elliptic" impratio="5"/>
  <worldbody>
    <geom type="box" pos="{f(cl[0]/1000)} {f(cl[1]/1000)} {f(cl[2]/1000)}" quat="{ql[0]:.6f} {ql[1]:.6f} {ql[2]:.6f} {ql[3]:.6f}" size="{f((S-L+40)/2000)} {f(lab/2000)} {f(1.5/1000)}" friction="{mu} 0 0" solref="{solref}" rgba=".6 .6 .7 1"/>
    <geom type="box" pos="{f(cp[0]/1000)} {f(cp[1]/1000)} {f(cp[2]/1000)}" quat="{qp[0]:.6f} {qp[1]:.6f} {qp[2]:.6f} {qp[3]:.6f}" size="{f((S-L)/2000)} {f(2/1000)} {f(35/1000)}" friction="{mp} 0 0" solref="{solref}" rgba=".5 .8 .8 1"/>
    {muro}
    <body name="bandeja" mocap="true" pos="0 0 0" quat="{q0[0]:.6f} {q0[1]:.6f} {q0[2]:.6f} {q0[3]:.6f}">
      <geom type="box" pos="{f(L/2000)} {f(-W/2000)} {f(-1.5/1000)}" size="{f(L/2000)} {f(W/2000)} {f(1.5/1000)}" friction="{mf} 0 0" solref="{solref}" rgba=".5 .7 .5 1"/>
    </body>
    <body name="moneda" pos="{f(pos[0]/1000)} {f(pos[1]/1000)} {f(pos[2]/1000)}" quat="{quat[0]:.6f} {quat[1]:.6f} {quat[2]:.6f} {quat[3]:.6f}">
      <freejoint/>
      <geom type="cylinder" size="{f(dr/2000)} {f(e/2000)}" mass="{f(m/1000)}" friction="{mu} {f(mu*2*dr/6000)} 0" condim="4" solref="{solref}"/>
    </body>
  </worldbody>
</mujoco>"""


def _cruces(f, ts):
    out = []
    for i in range(1, len(f)):
        if (f[i - 1] < 0) != (f[i] < 0):
            u = f[i - 1] / (f[i - 1] - f[i]); out.append(ts[i - 1] + u * (ts[i] - ts[i - 1]))
    return out


def estimar(ts, fa, fb, L):
    ca = _cruces(np.array(fa), np.array(ts)); cb = _cruces(np.array(fb), np.array(ts))
    if len(ca) != 2 or len(cb) != 2:
        return None
    t1a, t1b = ca; t2a, t2b = cb
    T = t2a - t1a; tau1 = t1b - t1a; tau2 = t2b - t2a
    M = np.array([[T, 0.5 * T * T, 0.0], [tau1, 0.5 * tau1 ** 2, -1.0], [T + tau2, 0.5 * (T + tau2) ** 2, -1.0]])
    v, a, c = np.linalg.solve(M, np.array([L, 0.0, L]))
    return H_BARRERA + c * c / (4 * H_BARRERA), v


def correr(moneda, mu=0.4, lean=20.0, pend=20.0, x0=30.0, u=22.0, yaw=0.0, altura=8.0, dex=0.0, t_sube=1.0,
           x_b=320.0, sep=24.0, mu_placa=None, tmax=5.0, L=60.0, mu_flap=None, pared=True, x_end=None):
    d, e, m = MONEDAS[moneda]; dr = d + dex
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    ez = np.array([0, 0, 1.0]); ex = np.array([cy, sy, 0]); ey = np.cross(ez, ex)
    q = _quat(np.column_stack([ex, ey, ez]))
    c = np.array([x0, -u, e / 2 + altura])
    mod = mujoco.MjModel.from_xml_string(xml(moneda, c, q, dr, L=L, mu=mu, lean=lean, pend=pend, mu_placa=mu_placa, mu_flap=mu_flap, pared=pared))
    dat = mujoco.MjData(mod)
    bid = mod.body("bandeja").mocapid[0]
    th_fin = 90.0 - lean
    g = math.radians(lean)
    p_ = np.array([0, -math.sin(g), math.cos(g)])
    ts, fa, fb = [], [], []
    estado = "ok"; t_end = None; v_end = None
    while dat.time < tmax:
        th = th_fin * min(1.0, max(0.0, (dat.time - 0.3) / t_sube)) if dat.time > 0.3 else 0.0
        dat.mocap_quat[bid] = _quat(rot_x_cols(th))
        mujoco.mj_step(mod, dat)
        pos = dat.qpos[:3] * 1000
        xc, pc = pos[0], pos @ p_
        ts.append(dat.time)
        fa.append((x_b - xc) ** 2 + (H_BARRERA - pc) ** 2 - (dr / 2) ** 2)
        fb.append((x_b + sep - xc) ** 2 + (H_BARRERA - pc) ** 2 - (dr / 2) ** 2)
        if pc < -10:
            estado = "cae"; break
        if x_end is not None and xc >= x_end:
            t_end = dat.time; v_end = float(dat.qvel[0] * 1000); break
        if x_end is None and xc > x_b + sep + dr:
            break
    else:
        estado = "no_llega"
    r = estimar(ts, fa, fb, sep) if estado == "ok" else None
    cb = _cruces(np.array(fb), np.array(ts)) if estado == "ok" else []
    t_b2 = cb[-1] if len(cb) == 2 else None
    return dict(estado=estado, dest=None if r is None else r[0], v=None if r is None else r[1], x=float(dat.qpos[0] * 1000), t=float(dat.time), t_end=t_end, v_end=v_end, t_b2=t_b2)
