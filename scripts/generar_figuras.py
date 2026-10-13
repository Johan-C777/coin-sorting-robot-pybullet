"""Genera las figuras del README y de docs/ a partir del código del proyecto.

    python scripts/generar_figuras.py

Nada de imágenes sueltas: si cambia un parámetro en software/brazo/config.py,
se vuelve a correr esto y las figuras quedan al día.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Wedge

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "software"))

from brazo.config import (D1, HOME, L1, L2, L3, LIMITES, R_ARCO, YAW_ENTRADA,
                          YAW_RACK, Z_AGARRE, Z_SEGURA)          # noqa: E402
from brazo.kinematics import ik, pose_puesto, puntos             # noqa: E402
from brazo.statics import factores_seguridad, pares              # noqa: E402
from brazo.trajectory import perfil                              # noqa: E402
from brazo import monedas as mon                                 # noqa: E402
from brazo import obstaculos as obs                              # noqa: E402

SALIDA = RAIZ / "docs" / "img"
PAPEL = "#F1F4EF"
TINTA = "#1E2928"
NARANJA = "#E06E17"
AZUL = "#2F5878"
GRIS = "#9AA6A1"
VERDE = "#2C7A54"
COLOR_NIVEL = {1: "#2C7A54", 2: "#B8860B", 3: "#C2571A", 4: "#A3262A"}

plt.rcParams.update({
    "figure.facecolor": PAPEL, "axes.facecolor": PAPEL,
    "savefig.facecolor": PAPEL, "text.color": TINTA,
    "axes.labelcolor": TINTA, "xtick.color": TINTA, "ytick.color": TINTA,
    "axes.edgecolor": "#C9D3CC", "font.size": 10, "figure.dpi": 140,
})


def espacio_trabajo():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6))

    # --- corte lateral: nube de puntos alcanzables
    xs, zs = [], []
    for q2 in range(int(LIMITES[1][0]), int(LIMITES[1][1]) + 1, 2):
        for q3 in range(int(LIMITES[2][0]), int(LIMITES[2][1]) + 1, 2):
            q4 = -90 - q2 - q3
            if not LIMITES[3][0] <= q4 <= LIMITES[3][1]:
                continue
            p = puntos([0, q2, q3, q4, 0])["tcp"]
            if p[1] >= 0:
                xs.append(p[0])
                zs.append(p[1])
    ax1.scatter(xs, zs, s=4, c=AZUL, alpha=0.25, linewidths=0,
                label="alcanzable con la pinza vertical")
    p = puntos(ik(*pose_puesto(24.0, Z_AGARRE)))
    cadena = [(0, 0), p["hombro"], p["codo"], p["muneca"], p["tcp"]]
    ax1.plot([c[0] for c in cadena], [c[1] for c in cadena], "-o", color=NARANJA,
             lw=3, ms=5, label="pose de agarre")
    ax1.add_patch(Rectangle((R_ARCO - 2.6, 0.6), 5.2, 8, fill=False, ec=TINTA, lw=1.2))
    for z, txt in ((Z_AGARRE, "agarre 6,8 cm"), (Z_SEGURA, "traslado 17 cm")):
        ax1.axhline(z, color=GRIS, ls="--", lw=1)
        ax1.text(33, z + 0.6, txt, ha="right", fontsize=8, color=GRIS)
    ax1.axhline(0, color=TINTA, lw=1.6)
    ax1.set_xlim(-4, 36); ax1.set_ylim(-3, 40); ax1.set_aspect("equal")
    ax1.set_xlabel("radio desde el eje de la base (cm)")
    ax1.set_ylabel("altura sobre la mesa (cm)")
    ax1.set_title("Corte en el plano del brazo", loc="left")
    ax1.legend(loc="upper right", fontsize=8, frameon=False)

    # --- vista superior: sector alcanzable y puestos
    ax2.add_patch(Wedge((0, 0), 30.76, 0, 180, width=30.76 - 7.14,
                        facecolor=AZUL, alpha=0.18, edgecolor=AZUL))
    ax2.add_patch(Wedge((0, 0), 27.65, 0, 180, width=0.15, facecolor=GRIS))
    for yaws, pre in ((YAW_ENTRADA, "E"), (YAW_RACK, "R")):
        for i, yaw in enumerate(yaws):
            x, y, _ = pose_puesto(yaw, Z_AGARRE)
            ax2.add_patch(Circle((-y, x), 2.6, fill=False, ec=NARANJA, lw=1.6))
            ax2.text(-y, x, f"{pre}{i + 1}", ha="center", va="center", fontsize=8)
    ax2.plot([0], [0], "o", color=TINTA, ms=7)
    ax2.annotate("X", (0, 13), fontsize=9, color=GRIS)
    ax2.annotate("Y", (-13, 0.6), fontsize=9, color=GRIS)
    ax2.set_xlim(-34, 34); ax2.set_ylim(-4, 34); ax2.set_aspect("equal")
    ax2.set_title("Vista superior, giro de base ±90°", loc="left")
    ax2.set_xlabel("cm")
    fig.tight_layout()
    fig.savefig(SALIDA / "espacio-trabajo.png")
    plt.close(fig)


def perfil_quintico():
    T, delta = 2.2933, 172.0
    ts = [T * k / 200 for k in range(201)]
    pos, vel, acc = zip(*(perfil(delta, T, t) for t in ts))
    fig, axes = plt.subplots(3, 1, figsize=(7, 5.2), sharex=True)
    for ax, datos, etiqueta, color in zip(
            axes, (pos, vel, acc),
            ("posición (grados)", "velocidad (°/s)", "aceleración (°/s²)"),
            (NARANJA, AZUL, "#2C7A54")):
        ax.plot(ts, datos, color=color, lw=2.2)
        ax.axhline(0, color=GRIS, lw=0.8)
        ax.set_ylabel(etiqueta, fontsize=9)
        pico = max(datos, key=abs)
        ax.annotate(f"pico {pico:.1f}", (ts[datos.index(pico)], pico),
                    textcoords="offset points", xytext=(6, -2), fontsize=8, color=color)
    axes[0].set_title("Perfil quíntico del giro más largo: 172° en 2,29 s", loc="left")
    axes[-1].set_xlabel("tiempo (s)")
    fig.tight_layout()
    fig.savefig(SALIDA / "perfil-quintico.png")
    plt.close(fig)


def pares_y_seguridad():
    poses = {
        "Reposo": HOME,
        "Agarre": ik(*pose_puesto(24.0, Z_AGARRE)),
        "Traslado": ik(*pose_puesto(24.0, Z_SEGURA)),
        "Extendido": [0.0, 0.0, 0.0, 0.0, 0.0],
    }
    juntas = ["J2", "J3", "J4"]
    nombres = {"J2": "hombro", "J3": "codo", "J4": "muñeca"}
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.0))

    ancho = 0.25
    for k, j in enumerate(juntas):
        valores = [pares(q).como_dict()[j] for q in poses.values()]
        ax1.bar([i + k * ancho for i in range(len(poses))], valores, ancho,
                label=f"{j} ({nombres[j]})",
                color=[NARANJA, AZUL, "#2C7A54"][k])
    ax1.set_xticks([i + ancho for i in range(len(poses))])
    ax1.set_xticklabels(poses.keys())
    ax1.set_ylabel("par requerido (kg·cm)")
    ax1.set_title("Par estático con el vaso más pesado (416 g)", loc="left")
    ax1.legend(fontsize=8, frameon=False)

    fs_op = factores_seguridad(poses["Agarre"])
    fs_ext = factores_seguridad(poses["Extendido"])
    etiquetas = ["J1", "J2", "J3", "J4", "pinza"]
    ax2.bar([i - 0.2 for i in range(len(etiquetas))],
            [min(fs_op[e], 6) for e in etiquetas], 0.4, label="en operación", color=AZUL)
    ax2.bar([i + 0.2 for i in range(len(etiquetas))],
            [min(fs_ext[e], 6) for e in etiquetas], 0.4, label="extendido", color=NARANJA)
    ax2.axhline(1.5, color="#B23E0C", ls="--", lw=1.2)
    ax2.text(len(etiquetas) - 0.6, 1.6, "mínimo 1,5", fontsize=8, color="#B23E0C")
    ax2.set_xticks(range(len(etiquetas)))
    ax2.set_xticklabels(etiquetas)
    ax2.set_ylabel("factor de seguridad (recorte en 6)")
    ax2.set_title("Margen de los servos elegidos", loc="left")
    ax2.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(SALIDA / "pares.png")
    plt.close(fig)


def pose_acotada():
    q = ik(*pose_puesto(24.0, Z_AGARRE))
    p = puntos(q)
    fig, ax = plt.subplots(figsize=(7.4, 5.0))
    ax.axhline(0, color=TINTA, lw=1.8)
    ax.add_patch(Rectangle((-4.2, 0), 8.4, D1 - 1.6, facecolor="#DCE4DD", ec=GRIS))
    cadena = [p["hombro"], p["codo"], p["muneca"], p["tcp"]]
    ax.plot([c[0] for c in cadena], [c[1] for c in cadena], "-", color=NARANJA, lw=8,
            solid_capstyle="round", alpha=0.9)
    ax.plot([c[0] for c in cadena], [c[1] for c in cadena], "--o", color=TINTA, lw=1,
            ms=7, mfc=PAPEL)
    ax.add_patch(Rectangle((R_ARCO - 2.6, 0.6), 5.2, 8, facecolor="#2F587822",
                           ec=AZUL, lw=1.2))
    etiquetas = [(p["hombro"], p["codo"], "L₁ = 16"), (p["codo"], p["muneca"], "L₂ = 15"),
                 (p["muneca"], p["tcp"], "L₃ = 8")]
    for a, b, txt in etiquetas:
        ax.text((a[0] + b[0]) / 2 - 1.6, (a[1] + b[1]) / 2 + 1.2, txt, fontsize=9,
                color=TINTA, fontweight="bold")
    ax.annotate("", (0, 0), (0, D1), arrowprops=dict(arrowstyle="<->", color=AZUL))
    ax.text(-3.4, D1 / 2, "d₁ = 11", fontsize=9, color=AZUL, rotation=90, va="center")
    ax.annotate("", (0, -2.4), (p["tcp"][0], -2.4), arrowprops=dict(arrowstyle="<->", color=AZUL))
    ax.text(p["tcp"][0] / 2, -3.6, f"r = {p['tcp'][0]:.2f} cm", fontsize=9, color=AZUL, ha="center")
    ax.plot(*p["tcp"], marker="x", color=NARANJA, ms=10, mew=2)
    ax.text(p["tcp"][0] + 1.4, p["tcp"][1] + 1.2, "TCP", fontsize=9, color=NARANJA)
    ax.text(1, 32, f"θ₂ = {q[1]:.2f}°   θ₃ = {q[2]:.2f}°   θ₄ = {q[3]:.2f}°",
            fontsize=10, color=TINTA)
    ax.set_xlim(-9, 34); ax.set_ylim(-6, 35); ax.set_aspect("equal")
    ax.set_xlabel("cm"); ax.set_ylabel("cm")
    ax.set_title("Pose de agarre en el puesto R1", loc="left")
    fig.tight_layout()
    fig.savefig(SALIDA / "pose-agarre.png")
    plt.close(fig)


def selector_monedas():
    """Diámetros de las dos familias y luces de las ocho ranuras del riel."""
    fig, ax = plt.subplots(figsize=(11, 4.0))
    filas = {mon.NUEVA: 1.0, mon.ANTIGUA: 0.0}
    for e in mon.SELECTOR:
        ax.axvline(e.luz_mm, color=GRIS, lw=1, ls="--", zorder=1)
        ax.text(e.luz_mm, 1.62, f"E{e.numero}\n{e.luz_mm:.2f}".replace(".", ","),
                ha="center", va="bottom", fontsize=8, color=TINTA)
    for m in mon.CATALOGO:
        fuera = m.clave in mon.FUERA_DE_ALCANCE
        y = filas[m.familia] - (0.0 if not fuera else 0.0)
        color = GRIS if fuera else (AZUL if m.familia == mon.NUEVA else NARANJA)
        ax.scatter([m.diametro_mm], [y], s=(m.diametro_mm * 1.05) ** 2,
                   facecolors="none" if fuera else color, edgecolors=color,
                   linewidths=1.5, linestyle=":" if fuera else "-", zorder=3 if not fuera else 4)
        texto = f"${m.denominacion:,}".replace(",", ".")
        if fuera:
            ax.text(m.diametro_mm - 0.35, y - 0.68, "$1.000 de 1996: no admitida\n(0,17 mm de la $50)",
                    ha="right", va="top", fontsize=8, color=GRIS)
        else:
            ax.text(m.diametro_mm, y - 0.36, texto, ha="center", va="top", fontsize=8.5, color=TINTA)
    e4 = mon.SELECTOR[3]
    ax.annotate("ranura crítica E4:\n0,30 mm a cada lado", xy=(e4.luz_mm, -0.8),
                xytext=(25.25, -0.8), fontsize=8.5, color="#A3262A", va="center",
                arrowprops=dict(arrowstyle="->", color="#A3262A", lw=1))
    ax.text(15.9, 1.0, "Familia nueva\n(2012)", ha="right", va="center", color=AZUL, fontsize=9)
    ax.text(15.9, 0.0, "Familia anterior\n(1989-1996)", ha="right", va="center", color=NARANJA,
            fontsize=9)
    ax.set_xlim(13.2, 28.2)
    ax.set_ylim(-1.15, 2.05)
    ax.set_yticks([])
    ax.set_xlabel("diámetro (mm); cada línea punteada es la luz de una ranura")
    ax.set_title("Riel selector: ocho estaciones para monedas antiguas y nuevas", loc="left")
    for lado in ("left", "right", "top"):
        ax.spines[lado].set_visible(False)
    fig.tight_layout()
    fig.savefig(SALIDA / "selector-monedas.png")
    plt.close(fig)


def ruta_obstaculos():
    """Vista superior de la celda de A a B y altura del TCP a lo largo del arco."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 5.0),
                                   gridspec_kw={"width_ratios": [1.0, 1.05]})
    yaws = [obs.YAW_A + i * 0.5 for i in range(int((obs.YAW_B[-1] - obs.YAW_A) / 0.5) + 1)]
    plan = [obs.plan_en(y) for y in yaws]

    # --- vista superior: X adelante, Y a la izquierda (se dibuja Y hacia arriba)
    ax1.add_patch(Circle((0, 0), 3.0, color=TINTA, zorder=4))
    ax1.text(0, -4.8, "base", ha="center", fontsize=8.5)
    arco = [(obs.R_ARCO * math.cos(math.radians(y)), obs.R_ARCO * math.sin(math.radians(y)))
            for y in yaws]
    ax1.plot(*zip(*arco), color=TINTA, lw=1.6, ls="--", zorder=3)
    ax1.text(25.5, 3.0, "arco de tránsito\nρ = 23 cm", fontsize=8, color=TINTA)
    pos_texto = {"O1": (31.0, -16.5), "O2": (34.0, -5.0), "O3": (2.5, 9.5), "O4": (31.5, 18.0)}
    for o in obs.OBSTACULOS:
        a = math.radians(o.yaw)
        px, py = o.r_pivote * math.cos(a), o.r_pivote * math.sin(a)
        c = COLOR_NIVEL[o.nivel]
        ax1.add_patch(Circle((px, py), o.radio + o.r_esfera, facecolor=c, alpha=0.15,
                             edgecolor=c, lw=1.4, zorder=2))
        ax1.add_patch(Circle((px, py), 0.6, color=c, zorder=3))
        tx, ty = pos_texto[o.codigo]
        ax1.text(tx, ty, f"N{o.nivel} · {o.codigo}\n{o.nombre}", ha="center", va="center",
                 fontsize=8.5, color=c, fontweight="bold")
    ya = math.radians(obs.YAW_A)
    xa, ya_ = obs.R_ARCO * math.cos(ya), obs.R_ARCO * math.sin(ya)
    ax1.add_patch(Rectangle((xa - 2.6, ya_ - 2.6), 5.2, 5.2, color=NARANJA, zorder=5))
    ax1.text(xa - 4.0, ya_, "A\nfin de\nla banda", ha="right", va="center", fontsize=8.5,
             fontweight="bold", color=NARANJA)
    for i, y in enumerate(obs.YAW_B):
        b = math.radians(y)
        ax1.add_patch(Circle((obs.R_ARCO * math.cos(b), obs.R_ARCO * math.sin(b)), 2.6,
                             facecolor=AZUL, edgecolor="white", lw=1, zorder=5))
        ax1.text(obs.R_ARCO * math.cos(b) * 0.78, obs.R_ARCO * math.sin(b) * 0.78, f"R{i + 1}",
                 ha="center", va="center", fontsize=8, color=AZUL)
    ax1.text(-4.5, 27.5, "B\nrack", ha="center", va="center", fontsize=8.5,
             fontweight="bold", color=AZUL)
    ax1.set_aspect("equal")
    ax1.set_xlim(-9, 41)
    ax1.set_ylim(-27, 31)
    ax1.set_xlabel("X (cm)")
    ax1.set_ylabel("Y (cm)")
    ax1.set_title("Celda vista desde arriba", loc="left")

    # --- altura del TCP a lo largo del arco y maniobra que manda en cada tramo
    ax2.plot(yaws, [p[0] for p in plan], color=TINTA, lw=2.2, label="altura del TCP")
    ax2.axhline(obs.Z_TRANSITO, color=GRIS, lw=1, ls="--", label="tránsito nominal, 20 cm")
    for o in obs.OBSTACULOS:
        c = COLOR_NIVEL[o.nivel]
        ax2.plot([o.yaw - 7, o.yaw + 7], [o.y_esfera - o.r_esfera] * 2, color=c, lw=3.5)
        ax2.text(o.yaw, o.y_esfera - o.r_esfera + 0.55, f"N{o.nivel} {o.codigo}",
                 ha="center", fontsize=8.5, color=c, fontweight="bold")
    nombres = {"bajo": "bajar", "rodeo": "recogerse", "espera": "esperar ventana",
               "directo": "directo"}
    inicio = 0
    for k in range(1, len(plan) + 1):
        if k == len(plan) or plan[k][2:] != plan[inicio][2:]:
            modo, quien = plan[inicio][2], plan[inicio][3]
            c = COLOR_NIVEL[int(quien[1])] if quien else GRIS
            ax2.add_patch(Rectangle((yaws[inicio], 6.0), yaws[k - 1] - yaws[inicio] + 0.5, 1.1,
                                    color=c, alpha=0.85))
            if yaws[k - 1] - yaws[inicio] > 10:
                ax2.text((yaws[inicio] + yaws[k - 1]) / 2, 7.55, f"{nombres[modo]} ({quien})",
                         ha="center", fontsize=8, color=c)
            inicio = k
    ax2.axvline(obs.YAW_A, color=NARANJA, lw=1.2)
    ax2.axvspan(obs.YAW_B[0] - 2.6, obs.YAW_B[-1] + 2.6, color=AZUL, alpha=0.07)
    ax2.text(obs.YAW_A + 1.2, 25.0, "A", color=NARANJA, fontweight="bold")
    ax2.text(obs.YAW_B[0] + 1, 25.0, "B: R1 a R5", color=AZUL, fontweight="bold")
    ax2.set_xlabel("yaw de la base (°)")
    ax2.set_ylabel("altura (cm)")
    ax2.set_ylim(5.5, 26.5)
    ax2.legend(loc="upper left", bbox_to_anchor=(0.06, 0.93), fontsize=8, frameon=False)
    ax2.set_title("Altura que pide el planificador de A a B", loc="left")
    ax2.text(obs.YAW_A, 9.3, "franja inferior: maniobra que manda en cada tramo;\n"
             "barras de color: borde inferior de las esferas", fontsize=7.5, color=GRIS)
    fig.tight_layout()
    fig.savefig(SALIDA / "ruta-obstaculos.png")
    plt.close(fig)


def main() -> int:
    SALIDA.mkdir(parents=True, exist_ok=True)
    pose_acotada()
    espacio_trabajo()
    perfil_quintico()
    pares_y_seguridad()
    selector_monedas()
    ruta_obstaculos()
    print(f"Figuras guardadas en {SALIDA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
