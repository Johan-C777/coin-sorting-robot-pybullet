"""Simulación MuJoCo del barredor: moneda plana sobre una pista horizontal con agujeros redondos
pegados a la pared; una cuchilla diagonal la empuja a velocidad constante."""
from __future__ import annotations
import math
import numpy as np
import mujoco
from riel_canto import MONEDAS

PARED_Y = 0.0
ANCHO = 30.0


def piso_con_agujeros(agujeros, x0, x1, esp=4.0, paso=0.1, mu=0.35):
    """Piso (cara superior z=0) con agujeros circulares [(xc, yc, diametro)] hecho de cajas (cada franja en y)."""
    geoms = []
    ys = np.arange(0.0, ANCHO + paso, paso)
    for ya, yb in zip(ys[:-1], ys[1:]):
        ym = (ya + yb) / 2
        cortes = []
        for xc, yc, D in agujeros:
            r = D / 2
            dy = ym - yc
            if abs(dy) < r:
                h = math.sqrt(r * r - dy * dy)
                cortes.append((xc - h, xc + h))
        cortes.sort()
        tramos, x = [], x0
        for a, b in cortes:
            if a > x:
                tramos.append((x, a))
            x = max(x, b)
        if x < x1:
            tramos.append((x, x1))
        for a, b in tramos:
            geoms.append(f'<geom type="box" pos="{(a+b)/2000:.6f} {(ya+yb)/2000:.6f} {-esp/2000:.6f}" '
                         f'size="{(b-a)/2000:.6f} {(yb-ya)/2000:.6f} {esp/2000:.6f}" friction="{mu} 0 0" solref="0.004 1" condim="3"/>')
    return geoms


def escena(agujeros, moneda, x_moneda, y_moneda, mu=0.35, x0=-40.0, x1=420.0, angulo_cuchilla=45.0, x_cuchilla=0.0,
           yaw=0.0, solref="0.004 1"):
    d, e, m = MONEDAS[moneda]
    geoms = piso_con_agujeros(agujeros, x0, x1, mu=mu)
    # pared guía y pared lejana
    geoms.append(f'<geom type="box" pos="{(x0+x1)/2000:.6f} {-1.2/1000:.6f} 0.005" size="{(x1-x0)/2000:.6f} 0.0012 0.005" friction="{mu} 0 0" solref="{solref}"/>')
    geoms.append(f'<geom type="box" pos="{(x0+x1)/2000:.6f} {(ANCHO+1.2)/1000:.6f} 0.005" size="{(x1-x0)/2000:.6f} 0.0012 0.005" friction="{mu} 0 0" solref="{solref}"/>')
    # cuchilla diagonal: mocap
    a = math.radians(angulo_cuchilla)
    L = ANCHO / math.sin(a)                     # largo para cubrir el ancho
    cuchilla = (f'<body name="cuchilla" mocap="true" pos="{x_cuchilla/1000:.6f} {ANCHO/2000:.6f} 0.0045">'
                f'<geom type="box" size="{L/2000:.6f} 0.00125 0.0045" euler="0 0 {-(90-angulo_cuchilla)*0 - angulo_cuchilla:.3f}" friction="{mu} 0 0" solref="{solref}"/></body>')
    cy, sy = math.cos(math.radians(yaw / 2)), math.sin(math.radians(yaw / 2))
    return f"""<mujoco>
  <option timestep="0.0005" gravity="0 0 -9.81" cone="elliptic" impratio="5"/>
  <worldbody>
    {' '.join(geoms)}
    {cuchilla}
    <body name="moneda" pos="{x_moneda/1000:.6f} {y_moneda/1000:.6f} {(e/2+0.05)/1000:.6f}" quat="{cy:.6f} 0 0 {sy:.6f}">
      <freejoint/>
      <geom type="cylinder" size="{d/2000:.6f} {e/2000:.6f}" mass="{m/1000:.6f}" friction="{mu} {mu*2*d/6000:.6f} 0" condim="4" solref="{solref}"/>
    </body>
  </worldbody>
</mujoco>"""


def barrer(agujeros, moneda, v=50.0, mu=0.35, y0=None, x_moneda=60.0, yaw=0.0, angulo=45.0, tmax=30.0, traza=False):
    d = MONEDAS[moneda][0]
    if y0 is None:
        y0 = d / 2 + 0.3
    # la cuchilla parte detrás de la moneda: su punta (en la pared) a x_moneda - d/2 - 2
    pared_x = x_moneda - d / 2 - 3.0
    # centro de la cuchilla: la cuchilla une (pared_x, 0) con (pared_x - ANCHO/tan(a), ANCHO)
    a = math.radians(angulo)
    cx = pared_x - ANCHO / math.tan(a) / 2
    xml = escena(agujeros, moneda, x_moneda, y0, mu=mu, x_cuchilla=cx, yaw=yaw, angulo_cuchilla=angulo)
    mod = mujoco.MjModel.from_xml_string(xml)
    dat = mujoco.MjData(mod)
    cid = mod.body("cuchilla").mocapid[0]
    tr = []
    k = 0
    while dat.time < tmax:
        dat.mocap_pos[cid][0] = cx / 1000 + v / 1000 * dat.time
        mujoco.mj_step(mod, dat)
        k += 1
        p = dat.qpos[:3] * 1000
        if traza and k % 40 == 0:
            tr.append((dat.time, *map(float, p)))
        if p[2] < -8.0:
            return dict(cae=True, x=float(p[0]), y=float(p[1]), t=dat.time, traza=tr)
        if p[0] > agujeros[-1][0] + 60:
            break
    p = dat.qpos[:3] * 1000
    return dict(cae=False, x=float(p[0]), y=float(p[1]), t=dat.time, traza=tr)
