"""Bandeja basculante: la moneda llega plana a una bandeja con bisagra a lo largo del riel; al subir la bandeja
hasta quedar como placa (inclinada `lean` grados de la vertical) la moneda resbala hasta el labio y queda de canto.
Marco: x = a lo largo del riel (s), y = hacia el frente, z = arriba. Unidades de entrada en mm."""
from __future__ import annotations
import math
import numpy as np
import mujoco
from riel_canto import MONEDAS, _quat


def rot_x_cols(theta):
    """Ejes del cuerpo de la bandeja inclinada theta grados (x=s, y=-u con u subiendo hacia atrás, z=normal)."""
    a = math.radians(theta)
    s = np.array([1.0, 0, 0]); u = np.array([0, math.cos(a), -math.sin(a)]); n = np.array([0, math.sin(a), math.cos(a)])
    return np.column_stack([s, u, n])


def xml(moneda, pos, quat, L=70.0, W=48.0, lab=12.0, mu=0.25, lean=15.0, pusher=None, solref="0.004 1"):
    d, e, m = MONEDAS[moneda]
    f = lambda v: f"{v:.6f}"
    q0 = _quat(rot_x_cols(0))
    # labio perpendicular a la placa final: ejes (s, p, n) con p = sube por la placa, n = sale de ella
    g = math.radians(lean)
    ex = np.array([1.0, 0, 0]); p_ = np.array([0, -math.sin(g), math.cos(g)]); n_ = np.array([0, math.cos(g), math.sin(g)])
    ql = _quat(np.column_stack([ex, n_, p_]))     # eje y del geom = n, eje z = p (grosor hacia abajo de la placa)
    cl = (L / 2 - 20) * ex + (lab / 2) * n_ - 1.5 * p_
    push = ""
    if pusher is not None:
        x, y, z = pusher["pos"]; sx, sy, sz = pusher["dim"]
        push = (f'<body name="dedo" mocap="true" pos="{f(x/1000)} {f(y/1000)} {f(z/1000)}">'
                f'<geom type="box" size="{f(sx/2000)} {f(sy/2000)} {f(sz/2000)}" friction="{mu} 0 0" solref="{solref}" rgba="1 .3 .3 1"/></body>')
    return f"""<mujoco>
  <option timestep="0.0004" gravity="0 0 -9.81" cone="elliptic" impratio="5"/>
  <worldbody>
    <geom type="box" pos="{f(cl[0]/1000)} {f(cl[1]/1000)} {f(cl[2]/1000)}" quat="{ql[0]:.6f} {ql[1]:.6f} {ql[2]:.6f} {ql[3]:.6f}" size="{f((L/2+40)/1000)} {f(lab/2000)} {f(1.5/1000)}" friction="{mu} 0 0" solref="{solref}" rgba=".6 .6 .7 1"/>
    <body name="bandeja" mocap="true" pos="0 0 0" quat="{q0[0]:.6f} {q0[1]:.6f} {q0[2]:.6f} {q0[3]:.6f}">
      <geom type="box" pos="{f(L/2000)} {f(-W/2000)} {f(-1.5/1000)}" size="{f(L/2000)} {f(W/2000)} {f(1.5/1000)}" friction="{mu} 0 0" solref="{solref}" rgba=".5 .7 .5 1"/>
    </body>
    {push}
    <body name="moneda" pos="{f(pos[0]/1000)} {f(pos[1]/1000)} {f(pos[2]/1000)}" quat="{quat[0]:.6f} {quat[1]:.6f} {quat[2]:.6f} {quat[3]:.6f}">
      <freejoint/>
      <geom type="cylinder" size="{f(d/2000)} {f(e/2000)}" mass="{f(m/1000)}" friction="{mu} {f(mu*2*d/6000)} 0" condim="4" solref="{solref}"/>
    </body>
  </worldbody>
</mujoco>"""


def voltear(moneda, x=35.0, u=25.0, yaw=0.0, altura=10.0, mu=0.25, lean=15.0, t_sube=1.0, t_total=3.0, L=70.0, W=48.0,
            lab=12.0, theta_ini=0.0, traza=False):
    """Suelta la moneda plana en (x, u) de la bandeja (u: distancia al eje de giro, hacia atrás). Devuelve estado final."""
    d, e, m = MONEDAS[moneda]
    c = np.array([x, -u, e / 2 + altura])
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    ez = np.array([0, 0, 1.0]); ex = np.array([cy, sy, 0]); ey = np.cross(ez, ex)
    q = _quat(np.column_stack([ex, ey, ez]))
    mod = mujoco.MjModel.from_xml_string(xml(moneda, c, q, L, W, lab, mu, lean))
    dat = mujoco.MjData(mod)
    bid = mod.body("bandeja").mocapid[0]
    th_fin = 90.0 - lean
    tr = []
    k = 0
    while dat.time < t_total:
        th = th_fin * min(1.0, max(0.0, (dat.time - 0.3) / t_sube)) if dat.time > 0.3 else 0.0
        qq = _quat(rot_x_cols(th))
        dat.mocap_quat[bid] = qq
        mujoco.mj_step(mod, dat)
        k += 1
        if traza and k % 100 == 0:
            tr.append((dat.time, th, *map(float, dat.qpos[:3] * 1000)))
    p = dat.qpos[:3] * 1000
    R = np.zeros(9); mujoco.mju_quat2Mat(R, dat.qpos[3:7]); R = R.reshape(3, 3)
    eje = R[:, 2]
    nf = rot_x_cols(th_fin)[:, 2]
    return dict(x=float(p[0]), y=float(p[1]), z=float(p[2]), alin=float(abs(eje @ nf)), v=float(np.linalg.norm(dat.qvel[:3])),
                traza=tr)
