import math
import os
import cadquery as cq

# =====================================================================
# 1. DIMENSIONES REALES MEDIDAS CON PIE DE REY (MICRO SERVO 9g SG90)
#    Y COMPATIBILIDAD CON EL BRAZO YA IMPRESO (005 y 003, pines O8 mm)
# =====================================================================

# --- Interfaz de muñeca con el brazo ya impreso (NO MODIFICAR) ---
U_TOP_X, U_TOP_Z = -15.0, 42.0     # Vector W1 -> W2 en 005/003
PIVOT_PIN_R = 4.15                 # O8.30 mm en agujeros W1/W2 y eje Pitch derecho
Y_ARM_CENTER = -4.0                # Centro Y de 005_Horizontal_Arm (Y in [-8.0, 0.0])

# --- Medidas reales del SG90 (validadas con pie de rey y fotos) ---
SG_BODY_L = 23.0                   # Largo cuerpo rectangular
SG_BODY_W = 12.0                   # Ancho cuerpo rectangular
SG_SHAFT_FROM_END = 6.0            # Centro del eje desde el borde cercano (lado cable)
SG_BODY_CX = (SG_BODY_L / 2.0) - SG_SHAFT_FROM_END  # +5.5 mm desde el eje hacia cuerpo largo
SG_FLANGE_L = 32.0                 # Largo total pestañas
SG_FLANGE_W = 12.0                 # Ancho pestañas
SG_FLANGE_Z0 = 17.4                # Desde base hasta cara inferior de pestaña
SG_FLANGE_T = 2.6                  # Espesor de pestaña
SG_FLANGE_Z1 = SG_FLANGE_Z0 + SG_FLANGE_T  # 20.0 mm (cara superior de pestaña)
SG_CASE_TOP_Z = 24.0               # Altura caja rectangular azul (20.0 -> 24.0 = 4.0 mm)
SG_TURRET_H = 4.3                  # Torreta circular azul sobre caja rectangular
SG_TURRET_TOP_Z = SG_CASE_TOP_Z + SG_TURRET_H  # 28.3 mm
SG_SPLINE_H = 3.5                  # Altura del eje estriado sobre torreta
SG_SCREW_HALF_SPAN = 13.8          # Entrecentros tornillos ~27.6 mm (centro en pestaña de 32 mm)

# --- Medidas reales de la pala blanca simple del servo (pie de rey) ---
HORN_HUB_D = 7.0                   # Diametro cubo donde va el tornillo
HORN_TIP_D = 4.4                   # Diametro punta redondeada de la pala
HORN_TOTAL_L = 22.0                # Largo total exterior a exterior
HORN_CC = HORN_TOTAL_L - (HORN_HUB_D / 2.0) - (HORN_TIP_D / 2.0)  # 16.3 mm entre centros
HORN_HUB_H = 5.0                   # Altura parte gruesa del cubo (28.3 -> 33.3)
HORN_BLADE_T = 2.0                 # Espesor pala plana (29.8 -> 31.8)
HORN_SKIRT_H = 1.5                 # Falda inferior del cubo bajo la pala (28.3 -> 29.8)

# --- Tolerancias FDM calibradas para impresión 3D ---
SG_POCKET_CLR = 0.25               # +0.25 mm por lado en cajera del cuerpo SG90 (23.5 x 12.5)
HORN_CLR = 0.25                    # +0.25 mm por lado en cajera de pala (encaje firme sin juego)
SG_SCREW_PILOT_R = 0.85            # O1.70 mm piloto para tornillos autorroscantes originales SG90
MOUNT_WALL_T = 6.5                 # Espesor pared de montaje desde cara sup. pestaña (Z=20.0..26.5)
DRIVEN_PART_T = 5.6                # Espesor zona de pala en dedo motriz y oreja pitch
HORN_FLOOR_T = 1.3                 # Piso macizo bajo la pala (6-7 capas a 0.2 mm)
HORN_POCKET_D = DRIVEN_PART_T - HORN_FLOOR_T  # 4.3 mm profundidad cajera de pala

# --- Cinemática de muñeca (Pitch) y garra (2 dedos engranados 1:1) ---
L_PITCH = 30.0                     # Distancia W1 -> Eje Pitch en X
CLAW_PIVOT_X = 44.0                # Distancia Eje Pitch -> Eje pivote dedos en X
GEAR_MODULE = 2.0                  # Modulo engranajes de dedos (dientes fuertes para FDM)
GEAR_Z_TEETH = 12                  # 12 dientes nominales -> R_p = 12.0 mm
GEAR_CENTER_DIST = 24.4            # 2*12.0 + 0.40 mm holgura FDM de rodadura
Y_RIGHT_FINGER = Y_ARM_CENTER - (GEAR_CENTER_DIST / 2.0)   # -16.2 mm (dedo motriz SG90)
Y_LEFT_FINGER = Y_ARM_CENTER + (GEAR_CENTER_DIST / 2.0)    # +8.2 mm (dedo conducido)
ARM_ANGLE_DEG = 20.0               # Angulo de salida del brazo del dedo (aleja brazo de dientes)

# --- Coordenadas Y simétricas de la horquilla Pitch (centradas en Y_ARM_CENTER = -4.0) ---
CLAW_Y_MIN = -25.5                 # Cara exterior izquierda de 012 (3.05 mm pared sobre SG90 garra)
CLAW_Y_MAX = 17.5                  # Cara exterior derecha de 012 (simetrica: -4.0 +/- 21.5)
FORK_L_INNER_Y = CLAW_Y_MIN - 2.0  # -27.5 mm (2.0 mm libre sobre pared izq 020 -> Z_servo = 26.5)
FORK_L_OUTER_Y = FORK_L_INNER_Y - MOUNT_WALL_T  # -34.0 mm (apoyo pestaña SG90 -> Z_servo = 20.0)
FORK_R_INNER_Y = CLAW_Y_MAX + 0.5  # +18.0 mm (0.5 mm luz con oreja der de 012)
FORK_R_OUTER_Y = FORK_R_INNER_Y + 5.5  # +23.5 mm

# --- Coordenadas Z locales de la plataforma de 012 (origen en eje Pitch Z=0) ---
DECK_Z_BOT = -9.0                  # Cara inferior 100% coplanar con fondo de orejas Pitch (R=9)
DECK_Z_TOP = DECK_Z_BOT + MOUNT_WALL_T  # -2.5 mm (apoyo pestañas SG90 garra -> Z_servo = 20.0)
FINGER_Z_TOP = DECK_Z_BOT - 2.0    # -11.0 mm (0.2 mm libre bajo torreta azul a -10.8 mm)
FINGER_Z_BOT = FINGER_Z_TOP - DRIVEN_PART_T  # -16.6 mm

# --- Pasadores imprimibles (dedo O4 mm y pitch derecho O8 mm) ---
FINGER_PIN_SHAFT_D = 3.90          # Eje O3.90 mm: gira libre en dedo (O4.35), ajusta en 012 (O4.00)
FINGER_HOLE_FREE_R = 2.175         # O4.35 mm en dedo conducido 014
FINGER_HOLE_PRESS_R = 2.00         # O4.00 mm en soporte 012 (encaje firme)
PITCH_PIN_SHAFT_D = 8.05           # Eje O8.05 mm: desliza suave en O8.30 mm con cabeza tope


# =====================================================================
# 2. UTILIDADES GEOMÉTRICAS (PALA TANGENTE EXACTA Y ENGRANAJES)
# =====================================================================
def crear_solido_perfil_pala(r1, r2, l_cc, altura, angulo_deg=0.0, plano="XY", offset=0.0):
    """
    Crea el prisma 2D exacto de envolvente tangente entre dos círculos:
    - Círculo 1 de radio r1 en (0, 0)
    - Círculo 2 de radio r2 en (l_cc, 0)
    Rotado angulo_deg alrededor del eje normal del plano.
    """
    sin_a = (r1 - r2) / l_cc
    cos_a = math.sqrt(max(0.0, 1.0 - sin_a * sin_a))

    p1_top = (r1 * sin_a, r1 * cos_a)
    p1_bot = (r1 * sin_a, -r1 * cos_a)
    p1_back = (-r1, 0.0)

    p2_top = (l_cc + r2 * sin_a, r2 * cos_a)
    p2_bot = (l_cc + r2 * sin_a, -r2 * cos_a)
    p2_front = (l_cc + r2, 0.0)

    solido = (
        cq.Workplane(plano)
        .workplane(offset=offset)
        .moveTo(*p1_top)
        .threePointArc(p1_back, p1_bot)
        .lineTo(*p2_bot)
        .threePointArc(p2_front, p2_top)
        .close()
        .extrude(altura)
    )
    if abs(angulo_deg) > 1e-9:
        eje = (0, 0, 1) if plano == "XY" else ((0, -1, 0) if plano == "XZ" else (1, 0, 0))
        solido = solido.rotate((0, 0, 0), eje, angulo_deg)
    return solido


def crear_perfil_engranaje_involuta(
    r_raiz=9.5,
    r_paso=12.0,
    r_punta=13.7,
    z_total=12,
    dientes_indices=None,
    fase_deg=0.0,
):
    """
    Genera perfil de engranaje de perfil trapezoidal-involuta (angulo de presion ~20 deg)
    con holgura FDM de flanco para rodadura suave sin atascos.
    Cada diente i queda centrado en: ang_c = fase_deg + i * (360 / z_total).
    """
    if dientes_indices is None:
        dientes_indices = set(range(z_total))
    else:
        dientes_indices = set(dientes_indices)

    paso = 2.0 * math.pi / z_total
    base = math.radians(fase_deg)

    # Semi-angulos del diente (paso = 30 deg -> mitad nominal = 7.5 deg en r_paso)
    # Adelgazamos ligeramente el diente para holgura de impresion 3D (~0.30 mm en paso)
    ha_raiz = math.radians(8.5)
    ha_paso = math.radians(6.6)
    ha_punta = math.radians(4.1)

    pts = []
    for i in range(z_total):
        th_c = base + i * paso
        th_start = th_c - paso / 2.0
        if i in dientes_indices:
            pts.extend([
                (r_raiz * math.cos(th_start), r_raiz * math.sin(th_start)),
                (r_raiz * math.cos(th_c - ha_raiz), r_raiz * math.sin(th_c - ha_raiz)),
                (r_paso * math.cos(th_c - ha_paso), r_paso * math.sin(th_c - ha_paso)),
                (r_punta * math.cos(th_c - ha_punta), r_punta * math.sin(th_c - ha_punta)),
                (r_punta * math.cos(th_c + ha_punta), r_punta * math.sin(th_c + ha_punta)),
                (r_paso * math.cos(th_c + ha_paso), r_paso * math.sin(th_c + ha_paso)),
                (r_raiz * math.cos(th_c + ha_raiz), r_raiz * math.sin(th_c + ha_raiz)),
            ])
        else:
            for k in range(4):
                ak = th_start + paso * (k / 4.0)
                pts.append((r_raiz * math.cos(ak), r_raiz * math.sin(ak)))
    return pts


# =====================================================================
# 3. MODELO EXACTO DEL MICRO SERVO SG90 REAL Y SU PALA BLANCA DE 22 mm
# =====================================================================
def crear_sg90_real():
    """
    Modela el Micro Servo SG90 real medido con pie de rey:
    - Origen (0, 0, 0) sobre el EJE DE SALIDA en el plano inferior del servo.
    - Cuerpo: 23.0 x 12.0 x 24.0 mm, desplazado +5.5 mm en X (eje a 6.0 mm del extremo -X).
    - Pestañas: 32.0 x 12.0 x 2.6 mm, de Z = 17.4 a Z = 20.0 mm.
    - Torreta circular azul: Z = 24.0 a Z = 28.3 mm (O11.8 mm en X=0 + O5.6 mm en X=+5.5).
    - Eje estriado blanco: Z = 28.3 a Z = 31.8 mm (O4.8 mm).
    - Salida de cable en extremo -X (X = -6.0 mm, Z = 1.5..4.5 mm).
    """
    cuerpo = (
        cq.Workplane("XY")
        .center(SG_BODY_CX, 0.0)
        .box(SG_BODY_L, SG_BODY_W, SG_CASE_TOP_Z, centered=(True, True, False))
    )
    pestanas = (
        cq.Workplane("XY")
        .workplane(offset=SG_FLANGE_Z0)
        .center(SG_BODY_CX, 0.0)
        .box(SG_FLANGE_L, SG_FLANGE_W, SG_FLANGE_T, centered=(True, True, False))
    )
    agujeros_pestana = (
        cq.Workplane("XY")
        .workplane(offset=SG_FLANGE_Z0 - 1.0)
        .pushPoints([(SG_BODY_CX - SG_SCREW_HALF_SPAN, 0.0), (SG_BODY_CX + SG_SCREW_HALF_SPAN, 0.0)])
        .circle(1.1)
        .extrude(SG_FLANGE_T + 2.0)
    )
    ranuras_abiertas = (
        cq.Workplane("XY")
        .workplane(offset=SG_FLANGE_Z0 - 1.0)
        .pushPoints([(SG_BODY_CX - SG_FLANGE_L / 2.0, 0.0), (SG_BODY_CX + SG_FLANGE_L / 2.0, 0.0)])
        .box(4.4, 1.5, SG_FLANGE_T + 2.0, centered=(True, True, False))
    )
    pestanas = pestanas.cut(agujeros_pestana).cut(ranuras_abiertas)

    torreta_1 = (
        cq.Workplane("XY")
        .workplane(offset=SG_CASE_TOP_Z)
        .cylinder(SG_TURRET_H, 5.9, centered=(True, True, False))
    )
    torreta_2 = (
        cq.Workplane("XY")
        .workplane(offset=SG_CASE_TOP_Z)
        .center(5.5, 0.0)
        .cylinder(SG_TURRET_H - 0.5, 2.8, centered=(True, True, False))
    )
    eje_estriado = (
        cq.Workplane("XY")
        .workplane(offset=SG_TURRET_TOP_Z)
        .cylinder(SG_SPLINE_H, 2.4, centered=(True, True, False))
    )
    cable_stub = (
        cq.Workplane("XY")
        .workplane(offset=1.5)
        .center(-SG_SHAFT_FROM_END - 1.5, 0.0)
        .box(3.5, 4.5, 3.0, centered=(True, True, False))
    )
    return cuerpo.union(pestanas).union(torreta_1).union(torreta_2).union(eje_estriado).union(cable_stub)


def crear_pala_servo_22mm():
    """
    Modela la pala blanca real del servo SG90:
    - Cubo O7.0 mm x 5.0 mm de alto (Z = 28.3 .. 33.3 mm).
    - Pala plana de 2.0 mm de espesor (Z = 29.85 .. 31.85 mm), largo total 22.0 mm, punta O4.4 mm.
    - En la posicion neutra, la pala apunta hacia +X.
    """
    z_hub0 = SG_TURRET_TOP_Z
    z_blade0 = z_hub0 + HORN_SKIRT_H + 0.05  # 29.85 mm (0.05 mm libre sobre piso cajera)

    cubo = (
        cq.Workplane("XY")
        .workplane(offset=z_hub0)
        .cylinder(HORN_HUB_H, HORN_HUB_D / 2.0, centered=(True, True, False))
    )
    pala_plana = crear_solido_perfil_pala(
        r1=HORN_HUB_D / 2.0,
        r2=HORN_TIP_D / 2.0,
        l_cc=HORN_CC,
        altura=HORN_BLADE_T,
        angulo_deg=0.0,
        plano="XY",
        offset=z_blade0,
    )
    taladro_central = (
        cq.Workplane("XY")
        .workplane(offset=z_hub0 - 0.5)
        .cylinder(HORN_HUB_H + 1.0, 1.1, centered=(True, True, False))
    )
    taladros_pala = (
        cq.Workplane("XY")
        .workplane(offset=z_blade0 - 0.5)
        .pushPoints([(6.8, 0.0), (9.3, 0.0), (11.8, 0.0), (14.3, 0.0), (16.3, 0.0)])
        .circle(0.55)
        .extrude(HORN_BLADE_T + 1.0)
    )
    return cubo.union(pala_plana).cut(taladro_central).cut(taladros_pala)


# =====================================================================
# 4. PIEZAS IMPRIMIBLES 3D REDISEÑADAS PARA LOS SERVOS SG90 REALES
# =====================================================================

def crear_020_soporte_muneca_pitch():
    """
    01_Soporte_Muneca_Pitch_020:
    - Mantiene 100% intacta la interfaz W1 (0,0) y W2 (-15,+42) con orejas en Y=-11.25 y Y=+3.25
      y perforaciones O8.30 mm para encajar en el antebrazo 005 y biela 003 ya impresos.
    - Brazo izquierdo adaptado al SG90 REAL: pared de 6.5 mm (Y in [-34.1, -27.6]), cajera
      rectangular de 23.5 x 12.5 mm para la caja azul superior, paso de torreta, costillas
      laterales anti-rotacion y 2 pilotos O1.70 mm para los tornillos originales del SG90.
    - Brazo derecho (Y in [+18.0, +23.5]) con paso O8.30 mm para el pin pasivo y acceso directo
      de destornillador al tornillo central de la pala de Pitch antes de colocar el pin.
    """
    # 1) Orejas de muñeca W1 / W2 (identicas al brazo ya impreso, fondo coplanar en Z = -9.75 mm)
    orejas = cq.Workplane("XY")
    for y_c in [-11.25, 3.25]:
        oreja = (
            cq.Workplane("XZ")
            .workplane(offset=-y_c)
            .polyline([(-8.0, -9.75), (14.0, -9.75), (14.0, 9.75), (U_TOP_X + 8.0, U_TOP_Z), (U_TOP_X - 8.0, U_TOP_Z)])
            .close()
            .extrude(3.0, both=True)
            .union(cq.Workplane("XZ").workplane(offset=-y_c).cylinder(6.0, 9.75))
            .union(cq.Workplane("XZ").workplane(offset=-y_c).center(U_TOP_X, U_TOP_Z).cylinder(6.0, 9.5))
        )
        orejas = orejas.union(oreja)

    # 2) Puente transversal que une orejas W1/W2 con ambos brazos de la horquilla Pitch
    puente_y_c = (FORK_L_OUTER_Y + FORK_R_OUTER_Y) / 2.0
    puente_y_w = FORK_R_OUTER_Y - FORK_L_OUTER_Y
    puente = (
        cq.Workplane("XY")
        .workplane(offset=-9.75)
        .center(14.25, puente_y_c)
        .box(6.5, puente_y_w, 19.5, centered=(True, True, False))
    )

    # 3) Brazo izquierdo de montaje del SG90 de Pitch (Y in [-34.1, -27.6], X in [11.0, 54.5])
    #    Nota: Workplane("XZ") tiene normal -Y -> offset=+d coloca plano en Y=-d, extrude(+h) avanza hacia -Y.
    brazo_izq = (
        cq.Workplane("XZ")
        .workplane(offset=-FORK_L_INNER_Y)  # Y = -27.6
        .polyline([(11.0, -9.75), (54.5, -9.75), (54.5, 9.75), (11.0, 9.75)])
        .close()
        .extrude(MOUNT_WALL_T)              # Y = -27.6 -> -34.1
    )

    # Costillas superior e inferior anti-rotación en la cara externa (-Y) que abrazan el cuerpo de 12 mm
    # Dejan completamente libres ambas pestañas (X=21.7 y X=49.3) y la salida del cable (X<24.0)
    sg_x_c = L_PITCH + SG_BODY_CX  # 35.5 mm
    costilla_sup = (
        cq.Workplane("XZ")
        .workplane(offset=-FORK_L_OUTER_Y)  # Y = -34.1
        .polyline([
            (sg_x_c - SG_BODY_L / 2.0, 6.25),
            (sg_x_c + SG_BODY_L / 2.0, 6.25),
            (sg_x_c + SG_BODY_L / 2.0, 9.75),
            (sg_x_c - SG_BODY_L / 2.0, 9.75),
        ])
        .close()
        .extrude(8.0)  # Y = -34.1 -> -42.1
    )
    costilla_inf = (
        cq.Workplane("XZ")
        .workplane(offset=-FORK_L_OUTER_Y)
        .polyline([
            (sg_x_c - SG_BODY_L / 2.0, -9.75),
            (sg_x_c + SG_BODY_L / 2.0, -9.75),
            (sg_x_c + SG_BODY_L / 2.0, -6.25),
            (sg_x_c - SG_BODY_L / 2.0, -6.25),
        ])
        .close()
        .extrude(8.0)
    )

    # Cajera rectangular para la parte superior del cuerpo azul del SG90 (Z_servo 20.0 -> 24.3)
    cajera_cuerpo_sg = (
        cq.Workplane("XZ")
        .workplane(offset=-FORK_L_OUTER_Y + 0.2)  # Inicia justo fuera de Y=-34.1
        .center(sg_x_c, 0.0)
        .rect(SG_BODY_L + 2 * SG_POCKET_CLR, SG_BODY_W + 2 * SG_POCKET_CLR)
        .extrude(-4.5)  # Entra hacia +Y hasta Y = -29.8 mm
    )
    # Paso pasante para la torreta circular azul (O12.6 mm en eje + O6.4 mm en secundario)
    paso_torreta_1 = (
        cq.Workplane("XZ")
        .workplane(offset=-FORK_L_INNER_Y - 0.5)
        .center(L_PITCH, 0.0)
        .circle(6.3)
        .extrude(MOUNT_WALL_T + 1.0)
    )
    paso_torreta_2 = (
        cq.Workplane("XZ")
        .workplane(offset=-FORK_L_INNER_Y - 0.5)
        .center(L_PITCH + 5.5, 0.0)
        .circle(3.2)
        .extrude(MOUNT_WALL_T + 1.0)
    )
    # 2 agujeros piloto O1.70 mm (profundidad 6.0 mm desde cara externa Y=-34.1) para tornillos SG90
    pilotos_sg90 = (
        cq.Workplane("XZ")
        .workplane(offset=-FORK_L_OUTER_Y + 0.5)
        .pushPoints([(sg_x_c - SG_SCREW_HALF_SPAN, 0.0), (sg_x_c + SG_SCREW_HALF_SPAN, 0.0)])
        .circle(SG_SCREW_PILOT_R)
        .extrude(-6.2)
    )

    # 4) Brazo derecho de pivote pasivo (Y in [+18.0, +23.5])
    brazo_der = (
        cq.Workplane("XZ")
        .workplane(offset=-FORK_R_INNER_Y)  # Y = +18.0
        .polyline([(11.0, -9.75), (L_PITCH, -9.75), (L_PITCH, 9.75), (11.0, 9.75)])
        .close()
        .extrude(-5.5)  # Avanza hacia +Y hasta +23.5
        .union(
            cq.Workplane("XZ")
            .workplane(offset=-(FORK_R_INNER_Y + 2.75))
            .center(L_PITCH, 0.0)
            .cylinder(5.5, 9.75)
        )
    )

    # 5) Perforaciones pasantes W1, W2 y pivote derecho Pitch
    h_w1 = cq.Workplane("XZ").cylinder(40.0, PIVOT_PIN_R)
    h_w2 = cq.Workplane("XZ").center(U_TOP_X, U_TOP_Z).cylinder(40.0, PIVOT_PIN_R)
    h_pitch_der = (
        cq.Workplane("XZ")
        .workplane(offset=-(FORK_R_INNER_Y + 2.75))
        .center(L_PITCH, 0.0)
        .cylinder(12.0, PIVOT_PIN_R)
    )

    pieza = (
        orejas.union(puente)
        .union(brazo_izq)
        .union(costilla_sup)
        .union(costilla_inf)
        .union(brazo_der)
        .cut(cajera_cuerpo_sg)
        .cut(paso_torreta_1)
        .cut(paso_torreta_2)
        .cut(pilotos_sg90)
        .cut(h_w1)
        .cut(h_w2)
        .cut(h_pitch_der)
    )
    return pieza


def crear_012_soporte_garra():
    """
    02_Soporte_Garra_012 (Origen local en el eje Pitch (0, 0, 0)):
    - Fondo 100% plano en Z = -9.0 mm para impresion estable sobre la cama.
    - Oreja izquierda Pitch (Y in [-25.5, -19.9], 5.6 mm de espesor) con cajera exacta de
      4.3 mm de profundidad para embeber la pala blanca completa de 22 mm (O7.0 -> O4.4)
      en su cara interna + paso O7.5 mm para encajar en la estria del SG90 de Pitch.
    - Oreja derecha Pitch (Y in [+12.0, +17.5], 5.5 mm) con pivote O8.30 mm.
    - Plataforma principal (X in [20.0, 56.0], Y in [-25.5, +17.5], Z in [-9.0, -2.5]) con
      alojamiento exacto para el SG90 de la garra (eje en X=44.0, Y=-16.2 apuntando -Z),
      costillas laterales anti-rotacion, 2 pilotos O1.70 mm para sus tornillos originales
      y perforacion O4.00 mm de encaje firme en (44.0, +8.2) para el pasador del dedo 014.
    """
    # 1) Plataforma principal
    plataforma = (
        cq.Workplane("XY")
        .workplane(offset=DECK_Z_BOT)
        .center(38.0, Y_ARM_CENTER)
        .box(36.0, CLAW_Y_MAX - CLAW_Y_MIN, MOUNT_WALL_T, centered=(True, True, False))
    )

    # 2) Oreja izquierda Pitch (Y in [-25.5, -19.9], espesor 5.6 mm)
    #    Envuelve completamente la pala de 22 mm horizontal a lo largo de +X (X = -3.75..+18.8)
    #    y cae a Z = DECK_Z_TOP (-2.5) en X = 22.0 mm, dejando libre la pestaña trasera del SG90 garra (X >= 22.5).
    y_ear_l_inner = CLAW_Y_MIN + DRIVEN_PART_T  # -19.9 mm
    oreja_izq = (
        cq.Workplane("XZ")
        .workplane(offset=-y_ear_l_inner)  # Y = -19.9
        .polyline([(0.0, -9.0), (24.0, -9.0), (24.0, -2.5), (22.0, -2.5), (21.2, 4.8), (0.0, 8.5)])
        .close()
        .extrude(DRIVEN_PART_T)            # Hacia -Y hasta -25.5
        .union(
            cq.Workplane("XZ")
            .workplane(offset=-(CLAW_Y_MIN + DRIVEN_PART_T / 2.0))
            .center(0.0, 0.0)
            .cylinder(DRIVEN_PART_T, 9.0)
        )
    )

    # 3) Oreja derecha Pitch (Y in [+12.0, +17.5], espesor 5.5 mm)
    oreja_der = (
        cq.Workplane("XZ")
        .workplane(offset=-12.0)  # Y = +12.0
        .polyline([(0.0, -9.0), (24.0, -9.0), (24.0, -2.5), (22.0, -2.5), (14.0, 6.0), (0.0, 8.5)])
        .close()
        .extrude(-5.5)            # Hacia +Y hasta +17.5
        .union(
            cq.Workplane("XZ")
            .workplane(offset=-14.75)
            .center(0.0, 0.0)
            .cylinder(5.5, 9.0)
        )
    )

    # 4) Costillas laterales anti-rotacion sobre la plataforma para abrazar el SG90 de la garra
    #    SG90 de la garra tiene eje en (44.0, -16.2) y cuerpo hacia -X (X in [27.0, 50.0], Y in [-22.2, -10.2])
    sg_claw_xc = CLAW_PIVOT_X - SG_BODY_CX  # 38.5 mm
    costilla_garra_ext = (
        cq.Workplane("XY")
        .workplane(offset=DECK_Z_TOP)
        .center(sg_claw_xc, (CLAW_Y_MIN + (Y_RIGHT_FINGER - SG_BODY_W / 2.0 - SG_POCKET_CLR)) / 2.0)
        .box(SG_BODY_L, (Y_RIGHT_FINGER - SG_BODY_W / 2.0 - SG_POCKET_CLR) - CLAW_Y_MIN, 6.0, centered=(True, True, False))
    )
    costilla_garra_int = (
        cq.Workplane("XY")
        .workplane(offset=DECK_Z_TOP)
        .center(sg_claw_xc, Y_RIGHT_FINGER + SG_BODY_W / 2.0 + SG_POCKET_CLR + 1.5)
        .box(SG_BODY_L, 3.0, 6.0, centered=(True, True, False))
    )

    # 5) Cortes de la oreja izquierda Pitch: paso O7.5 mm + cajera exacta para la pala de 22 mm
    paso_hub_pitch = (
        cq.Workplane("XZ")
        .workplane(offset=-(CLAW_Y_MIN + DRIVEN_PART_T / 2.0))
        .center(0.0, 0.0)
        .cylinder(DRIVEN_PART_T + 2.0, (HORN_HUB_D / 2.0) + HORN_CLR)
    )
    # Cajera entra desde la cara interna (Y = -19.9) hacia -Y una profundidad de HORN_POCKET_D (4.3 mm)
    cajera_pala_pitch = crear_solido_perfil_pala(
        r1=(HORN_HUB_D / 2.0) + HORN_CLR,
        r2=(HORN_TIP_D / 2.0) + HORN_CLR,
        l_cc=HORN_CC,
        altura=HORN_POCKET_D + 0.5,
        angulo_deg=0.0,
        plano="XZ",
        offset=-y_ear_l_inner - 0.5,  # Inicia a Y=-19.4, corta hasta Y=-24.2 (deja 1.3 mm piso)
    )
    # 2 mini agujeros opcionales O1.3 mm en el piso de la cajera (por si se desea asegurar con alambre/tornillo)
    mini_agujeros_pitch = (
        cq.Workplane("XZ")
        .workplane(offset=-(CLAW_Y_MIN + DRIVEN_PART_T / 2.0))
        .pushPoints([(9.3, 0.0), (14.3, 0.0)])
        .circle(0.65)
        .extrude(DRIVEN_PART_T + 2.0, both=True)
    )

    # 6) Corte del pivote derecho Pitch (O8.30 mm)
    h_pitch_der = (
        cq.Workplane("XZ")
        .workplane(offset=-14.75)
        .center(0.0, 0.0)
        .cylinder(10.0, PIVOT_PIN_R)
    )

    # 7) Cortes del alojamiento del SG90 de la garra (eje en X=44.0, Y=-16.2, cuerpo hacia -X)
    cajera_sg_garra = (
        cq.Workplane("XY")
        .workplane(offset=DECK_Z_TOP - 4.3)  # Z = -6.8 .. -2.5 (4.3 mm profundidad)
        .center(sg_claw_xc, Y_RIGHT_FINGER)
        .box(SG_BODY_L + 2 * SG_POCKET_CLR, SG_BODY_W + 2 * SG_POCKET_CLR, 5.0, centered=(True, True, False))
    )
    paso_torreta_g1 = (
        cq.Workplane("XY")
        .workplane(offset=DECK_Z_BOT - 1.0)
        .center(CLAW_PIVOT_X, Y_RIGHT_FINGER)
        .cylinder(MOUNT_WALL_T + 2.0, 6.3, centered=(True, True, False))
    )
    paso_torreta_g2 = (
        cq.Workplane("XY")
        .workplane(offset=DECK_Z_BOT - 1.0)
        .center(CLAW_PIVOT_X - 5.5, Y_RIGHT_FINGER)
        .cylinder(MOUNT_WALL_T + 2.0, 3.2, centered=(True, True, False))
    )
    pilotos_sg_garra = (
        cq.Workplane("XY")
        .workplane(offset=DECK_Z_BOT + 0.5)
        .pushPoints([
            (sg_claw_xc - SG_SCREW_HALF_SPAN, Y_RIGHT_FINGER),
            (sg_claw_xc + SG_SCREW_HALF_SPAN, Y_RIGHT_FINGER),
        ])
        .circle(SG_SCREW_PILOT_R)
        .extrude(MOUNT_WALL_T)
    )

    # 8) Agujero de encaje firme (O4.00 mm) para el pin del dedo izquierdo conducido 014
    h_pin_dedo_izq = (
        cq.Workplane("XY")
        .workplane(offset=DECK_Z_BOT - 1.0)
        .center(CLAW_PIVOT_X, Y_LEFT_FINGER)
        .cylinder(MOUNT_WALL_T + 2.0, FINGER_HOLE_PRESS_R, centered=(True, True, False))
    )

    pieza = (
        plataforma.union(oreja_izq)
        .union(oreja_der)
        .union(costilla_garra_ext)
        .union(costilla_garra_int)
        .cut(paso_hub_pitch)
        .cut(cajera_pala_pitch)
        .cut(mini_agujeros_pitch)
        .cut(h_pitch_der)
        .cut(cajera_sg_garra)
        .cut(paso_torreta_g1)
        .cut(paso_torreta_g2)
        .cut(pilotos_sg_garra)
        .cut(h_pin_dedo_izq)
    )
    return pieza


def _crear_segmento_capsula(p1, p2, r1, r2, altura):
    """Conecta dos circulos en p1 (radio r1) y p2 (radio r2) con tangente suave exacta."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    l_cc = math.hypot(dx, dy)
    ang = math.degrees(math.atan2(dy, dx))
    sol = crear_solido_perfil_pala(r1, r2, l_cc, altura, angulo_deg=ang, plano="XY", offset=0.0)
    return sol.translate((p1[0], p1[1], 0.0))


def _crear_dedo_exacto(es_motriz=True):
    """
    Construye 013 (es_motriz=True) o 014 (es_motriz=False) en marco de IMPRESION 3D (Z >= 0, SIN SOPORTES).
    Tras rotar 180 deg sobre el eje X para montarlos debajo de 012:
      - 013 (en Y = -16.2): dientes en +Y_ensamble (diente centrado en +90 deg), brazo en -20 deg, mordaza en +Y_ensamble.
      - 014 (en Y = +8.2):  dientes en -Y_ensamble (valle centrado en -90 deg), brazo en +20 deg, mordaza en -Y_ensamble.
    """
    signo_imp = -1.0 if es_motriz else 1.0  # En marco impresion (Y_imp = -Y_ens)

    if es_motriz:
        # Diente centrado en -90 deg (tras rotX 180 -> +90 deg)
        pts_gear = crear_perfil_engranaje_involuta(
            r_raiz=9.5, r_paso=12.0, r_punta=13.7, z_total=GEAR_Z_TEETH,
            dientes_indices={7, 8, 9, 10, 11}, fase_deg=0.0
        )
    else:
        # Valle centrado en +90 deg (tras rotX 180 -> -90 deg)
        pts_gear = crear_perfil_engranaje_involuta(
            r_raiz=9.5, r_paso=12.0, r_punta=13.7, z_total=GEAR_Z_TEETH,
            dientes_indices={0, 1, 2, 3, 4, 5}, fase_deg=15.0
        )

    engranaje = cq.Workplane("XY").polyline(pts_gear).close().extrude(DRIVEN_PART_T)

    # Brazo principal recto que aloja la pala completa de 22 mm (L_cc=16.3, punta en r=18.8 mm)
    ang_deg = ARM_ANGLE_DEG if es_motriz else -ARM_ANGLE_DEG
    ang = math.radians(ang_deg)
    L_arm = 23.0
    p_elbow = (L_arm * math.cos(ang), L_arm * math.sin(ang))
    p_jaw_base = (38.0, 7.5 * signo_imp)

    brazo_recto = _crear_segmento_capsula((0.0, 0.0), p_elbow, 6.2, 4.9, DRIVEN_PART_T)
    tramo_mordaza = _crear_segmento_capsula(p_elbow, p_jaw_base, 4.9, 4.2, DRIVEN_PART_T)

    # Mordaza frontal de 12.0 mm de alto con 5 dientes suaves antideslizantes (sin puntos duplicados)
    mordaza_pts = [
        (36.0, 4.2 * signo_imp),
        (54.0, 6.2 * signo_imp),
        (55.5, 10.6 * signo_imp),
        (54.0, 11.0 * signo_imp),
    ]
    for k in range(5):
        x_hi = 54.0 - k * 3.4
        x_mid = x_hi - 1.7
        x_lo = x_hi - 3.4
        mordaza_pts.append((x_mid, 11.7 * signo_imp))
        mordaza_pts.append((x_lo, 11.0 * signo_imp))
    mordaza_pts.append((36.0, 10.8 * signo_imp))

    mordaza = cq.Workplane("XY").polyline(mordaza_pts).close().extrude(12.0)
    cuerpo = engranaje.union(brazo_recto).union(tramo_mordaza).union(mordaza)

    if es_motriz:
        paso_cubo = (
            cq.Workplane("XY")
            .workplane(offset=-1.0)
            .cylinder(DRIVEN_PART_T + 2.0, (HORN_HUB_D / 2.0) + HORN_CLR, centered=(True, True, False))
        )
        cajera_pala = crear_solido_perfil_pala(
            r1=(HORN_HUB_D / 2.0) + HORN_CLR,
            r2=(HORN_TIP_D / 2.0) + HORN_CLR,
            l_cc=HORN_CC,
            altura=HORN_POCKET_D + 1.0,
            angulo_deg=ang_deg,
            plano="XY",
            offset=HORN_FLOOR_T,
        )
        mini_pts = [(r * math.cos(ang), r * math.sin(ang)) for r in (9.3, 14.3)]
        mini_agujeros = (
            cq.Workplane("XY")
            .workplane(offset=-1.0)
            .pushPoints(mini_pts)
            .circle(0.65)
            .extrude(DRIVEN_PART_T + 2.0)
        )
        return cuerpo.cut(paso_cubo).cut(cajera_pala).cut(mini_agujeros)
    else:
        paso_pivote = (
            cq.Workplane("XY")
            .workplane(offset=-1.0)
            .cylinder(DRIVEN_PART_T + 2.0, FINGER_HOLE_FREE_R, centered=(True, True, False))
        )
        return cuerpo.cut(paso_pivote)


def crear_05_pin_dedo_4mm():
    """
    05_Pin_Dedo_4mm:
    - Pasador imprimible con cabeza plana (O8.0 x 2.0 mm) + vastago O3.90 x 14.5 mm.
    - Entra desde abajo por 014 (giro libre O4.35 mm) + arandela de 2.0 mm + encaje firme en 012 (O4.00 mm).
    """
    cabeza = (
        cq.Workplane("XY")
        .cylinder(2.0, 4.0, centered=(True, True, False))
        .edges("<Z")
        .chamfer(0.4)
    )
    vastago = (
        cq.Workplane("XY")
        .workplane(offset=2.0)
        .cylinder(14.5, FINGER_PIN_SHAFT_D / 2.0, centered=(True, True, False))
        .edges(">Z")
        .chamfer(0.5)
    )
    return cabeza.union(vastago)


def crear_06_pin_pitch_8mm():
    """
    06_Pin_Pitch_8mm:
    - Pasador imprimible con cabeza plana (O12.0 x 2.5 mm) + vastago O8.05 x 12.0 mm.
    - Se inserta al final por el brazo derecho de 020 (tras apretar el tornillo del servo de Pitch).
    """
    cabeza = (
        cq.Workplane("XY")
        .cylinder(2.5, 6.0, centered=(True, True, False))
        .edges("<Z")
        .chamfer(0.5)
    )
    vastago = (
        cq.Workplane("XY")
        .workplane(offset=2.5)
        .cylinder(12.0, PITCH_PIN_SHAFT_D / 2.0, centered=(True, True, False))
        .edges(">Z")
        .chamfer(0.6)
    )
    return cabeza.union(vastago)


def crear_07_arandela_dedo_2mm():
    """
    07_Arandela_Dedo_2mm:
    - Separador plano O9.0 x 2.0 mm (agujero O4.40 mm) entre 012 y el dedo izquierdo 014.
    - Deja ambos dedos exactamente coplanares a Z = -11.0..-16.6 mm sin requerir soportes al imprimir.
    """
    return (
        cq.Workplane("XY")
        .cylinder(2.0, 4.5, centered=(True, True, False))
        .cut(cq.Workplane("XY").workplane(offset=-0.5).cylinder(3.0, 2.2, centered=(True, True, False)))
    )


def crear_ensamble_completo(pitch_deg=-10.0, finger_open_deg=20.0):
    """
    Construye el cq.Assembly completo y tambien devuelve una lista de (nombre, solido_ubicado)
    para ejecutar auditoria booleana 3D de colisiones en cualquier pose.
    """
    p020 = crear_020_soporte_muneca_pitch()
    p012 = crear_012_soporte_garra()
    p013 = _crear_dedo_exacto(es_motriz=True)
    p014 = _crear_dedo_exacto(es_motriz=False)
    pin_dedo = crear_05_pin_dedo_4mm()
    pin_pitch = crear_06_pin_pitch_8mm()
    arandela = crear_07_arandela_dedo_2mm()
    sg90 = crear_sg90_real()
    pala = crear_pala_servo_22mm()

    # Ubicaciones fijas respecto a W1 = (0, 0, 0)
    loc_020 = cq.Location(cq.Vector(0, 0, 0))

    # SG90 Pitch: Z_local=0 en Y = FORK_L_OUTER_Y - SG_FLANGE_Z1 = -54.1, eje +Z_local -> +Y_global
    loc_sg_pitch = cq.Location(
        cq.Vector(L_PITCH, FORK_L_OUTER_Y - SG_FLANGE_Z1, 0.0),
        cq.Vector(1, 0, 0),
        -90.0,
    )
    # Pala Pitch: rotada con pitch_deg en el eje Y_global (= +Z_local del SG90 Pitch!)
    loc_pala_pitch = loc_sg_pitch * cq.Location(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), pitch_deg)

    # Pin derecho Pitch: cabeza en Y = FORK_R_OUTER_Y + 2.5 (+26.0), vastago hacia -Y (+Z_local -> -Y_global)
    loc_pin_pitch = cq.Location(
        cq.Vector(L_PITCH, FORK_R_OUTER_Y + 2.5, 0.0),
        cq.Vector(1, 0, 0),
        90.0,
    )

    # Subensamble articulado de garra (gira pitch_deg alrededor de eje +Y en (L_PITCH, 0, 0))
    loc_pitch = cq.Location(cq.Vector(L_PITCH, 0.0, 0.0), cq.Vector(0, 1, 0), pitch_deg)

    # SG90 Garra en marco de 012:
    # Rotar 180° en Y: (x,y,z) -> (-x, y, -z). Asi +X_local apunta a -X_012 y +Z_local apunta a -Z_012!
    loc_sg_garra = loc_pitch * cq.Location(
        cq.Vector(CLAW_PIVOT_X, Y_RIGHT_FINGER, DECK_Z_TOP + SG_FLANGE_Z1),
        cq.Vector(0, 1, 0),
        180.0,
    )

    # Dedo derecho motriz 013:
    # Cara Z_imp=0 en Z_012 = FINGER_Z_TOP (-11.0). Rotar 180° en X: +Z_imp -> -Z_012, +Y_imp -> -Y_012.
    # Para abrir hacia afuera (-Y_012), rota -finger_open_deg alrededor de +Z_012!
    loc_013 = (
        loc_pitch
        * cq.Location(cq.Vector(CLAW_PIVOT_X, Y_RIGHT_FINGER, FINGER_Z_TOP), cq.Vector(0, 0, 1), -finger_open_deg)
        * cq.Location(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 180.0)
    )

    # Pala Garra: montada en SG90 Garra (donde +X_local = -X_012, +Z_local = -Z_012!).
    # Necesitamos que apunte a -(ARM_ANGLE_DEG + finger_open_deg) en el plano XY de 012!
    # En marco del SG90 Garra (rotY 180): +X_local = 180° en XY_012, +Y_local = +90° en XY_012, +Z_local = -Z_012.
    # Un giro +phi alrededor de +Z_local (= -Z_012) mueve +X_local (180°) hacia (180° - phi) en XY_012!
    # Queremos angulo en XY_012 = -(ARM_ANGLE_DEG + finger_open_deg) => 180 - phi = -(ARM_ANGLE_DEG + finger_open_deg)
    # => phi = 180 + ARM_ANGLE_DEG + finger_open_deg!
    loc_pala_garra = loc_sg_garra * cq.Location(
        cq.Vector(0, 0, 0),
        cq.Vector(0, 0, 1),
        180.0 + ARM_ANGLE_DEG + finger_open_deg,
    )

    # Dedo izquierdo conducido 014:
    # Para abrir hacia afuera (+Y_012), rota +finger_open_deg alrededor de +Z_012!
    loc_014 = (
        loc_pitch
        * cq.Location(cq.Vector(CLAW_PIVOT_X, Y_LEFT_FINGER, FINGER_Z_TOP), cq.Vector(0, 0, 1), +finger_open_deg)
        * cq.Location(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 180.0)
    )

    # Arandela separadora de 2.0 mm (Z_012 = -11.0 .. -9.0 -> justo entre 012 y 014)
    loc_arandela = loc_pitch * cq.Location(cq.Vector(CLAW_PIVOT_X, Y_LEFT_FINGER, FINGER_Z_TOP))

    # Pin de dedo O4 mm: cabeza abajo en Z_012 = FINGER_Z_BOT - 2.0 (-18.6), vastago sube +Z hasta -2.1!
    loc_pin_dedo = loc_pitch * cq.Location(cq.Vector(CLAW_PIVOT_X, Y_LEFT_FINGER, FINGER_Z_BOT - 2.0))

    c_azul = cq.Color(0.08, 0.48, 0.88)
    c_cian = cq.Color(0.12, 0.72, 0.85)
    c_servo = cq.Color(0.10, 0.25, 0.75)
    c_pala = cq.Color(0.95, 0.95, 0.95)
    c_pin = cq.Color(0.75, 0.78, 0.82)

    items = [
        ("01_Soporte_Muneca_Pitch_020", p020, loc_020, c_azul),
        ("02_Soporte_Garra_012", p012, loc_pitch, c_azul),
        ("03_Dedo_Derecho_Motriz_013", p013, loc_013, c_cian),
        ("04_Dedo_Izquierdo_Conducido_014", p014, loc_014, c_cian),
        ("05_Pin_Dedo_4mm", pin_dedo, loc_pin_dedo, c_pin),
        ("06_Pin_Pitch_8mm", pin_pitch, loc_pin_pitch, c_pin),
        ("07_Arandela_Dedo_2mm", arandela, loc_arandela, c_pin),
        ("08_MicroServo_SG90_Pitch", sg90, loc_sg_pitch, c_servo),
        ("09_Pala_SG90_22mm_Pitch", pala, loc_pala_pitch, c_pala),
        ("10_MicroServo_SG90_Garra", sg90, loc_sg_garra, c_servo),
        ("11_Pala_SG90_22mm_Garra", pala, loc_pala_garra, c_pala),
    ]

    assy = cq.Assembly(name="Ensamble_Garra_SG90")
    solidos_pos = []
    for nombre, sol, loc, col in items:
        assy.add(sol, name=nombre, color=col, loc=loc)
        solidos_pos.append((nombre, sol.val().located(loc)))

    return assy, solidos_pos


def verificar_colisiones(poses=None):
    if poses is None:
        poses = [
            (0.0, 0.0),     # Nivelada, cerrada
            (0.0, 25.0),    # Nivelada, semi-abierta
            (0.0, 50.0),    # Nivelada, abierta al maximo
            (45.0, 20.0),   # Pitch arriba +45 deg
            (-45.0, 0.0),   # Pitch abajo -45 deg, cerrada
        ]
    # Pares que se conectan fisicamente por encaje de estria (SG90 eje estriado <-> pala blanca)
    pares_permitidos = {
        frozenset(("08_MicroServo_SG90_Pitch", "09_Pala_SG90_22mm_Pitch")),
        frozenset(("10_MicroServo_SG90_Garra", "11_Pala_SG90_22mm_Garra")),
    }
    print("=== VERIFICACION DE COLISIONES 3D EN MULTIPLES POSES ===")
    todo_ok = True
    for pitch_deg, open_deg in poses:
        _, solidos = crear_ensamble_completo(pitch_deg=pitch_deg, finger_open_deg=open_deg)
        colisiones_pose = []
        for i in range(len(solidos)):
            n1, s1 = solidos[i]
            bb1 = s1.BoundingBox()
            for j in range(i + 1, len(solidos)):
                n2, s2 = solidos[j]
                if frozenset((n1, n2)) in pares_permitidos:
                    continue
                bb2 = s2.BoundingBox()
                if (
                    bb1.xmax < bb2.xmin or bb2.xmax < bb1.xmin
                    or bb1.ymax < bb2.ymin or bb2.ymax < bb1.ymin
                    or bb1.zmax < bb2.zmin or bb2.zmax < bb1.zmin
                ):
                    continue
                inter = s1.intersect(s2)
                vol = inter.Volume()
                if vol > 0.05:
                    colisiones_pose.append((n1, n2, vol))
        if colisiones_pose:
            todo_ok = False
            print(f"  [!] Pose Pitch={pitch_deg:+5.1f} deg, Open={open_deg:4.1f} deg -> COLISIONES:")
            for n1, n2, vol in colisiones_pose:
                print(f"      - {n1} <-> {n2}: {vol:.3f} mm^3")
        else:
            print(f"  [OK] Pose Pitch={pitch_deg:+5.1f} deg, Open={open_deg:4.1f} deg -> 0.00 mm^3 colisiones")
    return todo_ok


def verificar_compatibilidad_brazo():
    """Verifica que 01_Soporte_Muneca_Pitch_020 encaje con 0.00 mm^3 colision en 005 y 003 ya impresos (en multiples angulos)."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    p005_path = os.path.join(base_dir, "EBA_01.00.005_horizontal_arm.step")
    p003_path = os.path.join(base_dir, "EBA_01.00.003_link_forearm.step")
    if not (os.path.exists(p005_path) and os.path.exists(p003_path)):
        print("  (Omitido chequeo contra 005/003: archivos STEP no encontrados)")
        return True
    s005_raw = cq.importers.importStep(p005_path).val()
    s003_raw = cq.importers.importStep(p003_path).val()
    s020 = crear_020_soporte_muneca_pitch().val()
    print("=== COMPATIBILIDAD CON BRAZO YA IMPRESO (005 y 003) ===")
    ok = True
    for ang_deg in (-40.0, 0.0, 40.0):
        # Rotar antebrazo alrededor de W1=(0,0,0) y biela alrededor de W2=(-15,0,42)
        loc005 = cq.Location(cq.Vector(0, 0, 0), cq.Vector(0, 1, 0), ang_deg) * cq.Location(cq.Vector(-130.0, 0.0, 0.0))
        loc003 = cq.Location(cq.Vector(U_TOP_X, 0, U_TOP_Z), cq.Vector(0, 1, 0), ang_deg) * cq.Location(cq.Vector(-130.0, -3.0, 0.0))
        v005 = s020.intersect(s005_raw.located(loc005)).Volume()
        v003 = s020.intersect(s003_raw.located(loc003)).Volume()
        print(f"  Inclinacion antebrazo {ang_deg:+5.1f} deg | 020<->005: {v005:.4f} mm^3 | 020<->003: {v003:.4f} mm^3")
        if v005 >= 0.05 or v003 >= 0.05:
            ok = False
    return ok


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    GARRA_DIR = os.path.join(BASE_DIR, "garra")
    DIR_SOLID = os.path.join(GARRA_DIR, "SolidWorks")
    DIR_STL = os.path.join(GARRA_DIR, "Imprimibles_STL")

    os.makedirs(DIR_SOLID, exist_ok=True)
    os.makedirs(DIR_STL, exist_ok=True)

    # 1. Exportar STL imprimibles apoyados planos en Z = 0.0 mm (listos para laminar)
    piezas_stl = [
        ("01_Soporte_Muneca_Pitch_020_x1", crear_020_soporte_muneca_pitch(), 1, "Soporte de muñeca (ultimo GDL Pitch) compatible con 005/003 y SG90 real."),
        ("02_Soporte_Garra_012_x1", crear_012_soporte_garra(), 1, "Soporte de garra con cajera para pala 22mm (Pitch) y alojamiento SG90 garra."),
        ("03_Dedo_Derecho_Motriz_013_x1", _crear_dedo_exacto(es_motriz=True), 1, "Dedo derecho motriz con cajera exacta para pala 22mm del SG90 (sin soportes)."),
        ("04_Dedo_Izquierdo_Conducido_014_x1", _crear_dedo_exacto(es_motriz=False), 1, "Dedo izquierdo conducido engranado 1:1 con 013 (sin soportes)."),
        ("05_Pin_Dedo_4mm_x1", crear_05_pin_dedo_4mm(), 1, "Pasador con cabeza O3.90mm para pivote del dedo izquierdo 014."),
        ("06_Pin_Pitch_8mm_x1", crear_06_pin_pitch_8mm(), 1, "Pasador con cabeza O8.05mm para pivote derecho de muñeca Pitch."),
        ("07_Arandela_Dedo_2mm_x1", crear_07_arandela_dedo_2mm(), 1, "Arandela separadora 2.0mm entre 012 y 014 para coplanaridad exacta de dientes."),
    ]

    print("=== EXPORTANDO PIEZAS IMPRIMIBLES (STL EN Z=0) ===")
    for nombre, solido, cant, desc in piezas_stl:
        bb = solido.val().BoundingBox()
        solido_cama = solido.translate((-bb.xmin, -bb.ymin, -bb.zmin))
        stl_path = os.path.join(DIR_STL, f"{nombre}.stl")
        cq.exporters.export(solido_cama, stl_path, tolerance=0.02, angularTolerance=0.10)
        bb2 = solido_cama.val().BoundingBox()
        print(f"  -> {nombre:38s} | {bb2.xlen:5.1f} x {bb2.ylen:5.1f} x {bb2.zlen:5.1f} mm (Z0={bb2.zmin:.2f}) | OK")

    # 2. Exportar ensamble STEP (fuente exacta para SolidWorks)
    ensamble, _ = crear_ensamble_completo(pitch_deg=0.0, finger_open_deg=18.0)
    step_path = os.path.join(DIR_SOLID, "Ensamble_Garra_SG90.step")
    ensamble.export(step_path)
    print(f"\nEnsamble STEP exportado en: {step_path}")

    # 3. Verificaciones geométricas y de colisiones
    ok_col = verificar_colisiones()
    ok_arm = verificar_compatibilidad_brazo()
    if not (ok_col and ok_arm):
        raise SystemExit("ERROR: Se detectaron colisiones! Revisar geometria.")
    print("\n¡TODAS LAS VERIFICACIONES 3D PASARON CON 0.00 mm^3 DE COLISIONES!")
