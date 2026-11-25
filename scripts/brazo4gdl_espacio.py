"""Dibuja el espacio de trabajo del brazo de 4 GDL (vista lateral) en SVG.

python scripts/brazo4gdl_espacio.py  ->  docs/img/espacio-trabajo-4gdl.svg
"""
import math
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "software"))
from brazo import brazo4gdl as b  # noqa: E402

W, H, S = 760, 600, 1.1          # lienzo y escala (px por mm)
OX, OY = 120, 550                # origen (eje J1 en la mesa)


def px(r, z):
    return OX + r * S, OY - z * S


def main():
    out = []
    a = out.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="sans-serif" font-size="13">')
    a(f'<rect width="{W}" height="{H}" fill="#fff"/>')
    for z in range(0, 470, 50):
        x0, y = px(-80, z); x1, _ = px(560, z)
        a(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="#eee"/><text x="{x0-6}" y="{y+4}" text-anchor="end" fill="#888">{z}</text>')
    for r in range(0, 560, 50):
        x, y0 = px(r, 0)
        a(f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{px(0,460)[1]}" stroke="#eee"/><text x="{x}" y="{y0+16}" text-anchor="middle" fill="#888">{r}</text>')
    paso = 6
    for ph, color in ((0, "#3b82f6"), (-90, "#f59e0b")):
        for r in range(-60, 560, paso):
            for z in range(-60, 460, paso):
                if b.alcanzable(b.Pose(r, 0, z, ph)):
                    x, y = px(r, z)
                    a(f'<rect x="{x-paso*S/2:.1f}" y="{y-paso*S/2:.1f}" width="{paso*S:.1f}" height="{paso*S:.1f}" fill="{color}" opacity="0.28"/>')
    # brazo en una pose de agarre desde arriba
    q = b.inversa(b.Pose(250, 0, 100, -90))
    t2, t3 = math.radians(q.j2), math.radians(q.j3)
    o = (0, b.Z_HOMBRO)
    e = (o[0] + b.L1 * math.cos(t2), o[1] + b.L1 * math.sin(t2))
    w = (e[0] + b.L2 * math.cos(t3), e[1] + b.L2 * math.sin(t3))
    c = (w[0] + b.L_PITCH, w[1])
    t = (c[0], c[1] - b.L3)
    pts = [o, e, w, c, t]
    a('<polyline points="' + " ".join(f"{px(*p)[0]:.1f},{px(*p)[1]:.1f}" for p in pts) + '" fill="none" stroke="#111" stroke-width="5" stroke-linejoin="round"/>')
    for p in pts:
        x, y = px(*p)
        a(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#fff" stroke="#111" stroke-width="2"/>')
    x, y = px(-40, 0); x2, y2 = px(40, b.Z_HOMBRO)
    a(f'<rect x="{x}" y="{y2}" width="{x2-x}" height="{y-y2}" fill="#d4d4d4" stroke="#555"/>')
    a(f'<text x="{px(*o)[0]+8}" y="{px(*o)[1]-8}">O1 hombro</text>')
    a(f'<text x="{px(*e)[0]+8}" y="{px(*e)[1]}">E1 codo</text>')
    a(f'<text x="{px(*w)[0]+10}" y="{px(*w)[1]-10}">W1 muñeca</text>')
    a(f'<text x="{px(*t)[0]+10}" y="{px(*t)[1]+4}">punta (r = 250, z = 100)</text>')
    a(f'<rect x="{W-200}" y="60" width="14" height="14" fill="#3b82f6" opacity="0.5"/><text x="{W-180}" y="72">garra horizontal (0°)</text>')
    a(f'<rect x="{W-200}" y="82" width="14" height="14" fill="#f59e0b" opacity="0.5"/><text x="{W-180}" y="94">garra abajo (−90°)</text>')
    a(f'<text x="{W-200}" y="120" fill="#555">punta: radio y altura, mm</text>')
    a('</svg>')
    dest = RAIZ / "docs" / "img" / "espacio-trabajo-4gdl.svg"
    dest.write_text("\n".join(out), encoding="utf-8")
    print(dest)


if __name__ == "__main__":
    main()
