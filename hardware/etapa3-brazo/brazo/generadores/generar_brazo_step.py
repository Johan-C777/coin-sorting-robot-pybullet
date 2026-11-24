import math
import cadquery as cq

# =====================================================================
# 1. PARÁMETROS CINEMÁTICOS Y TOLERANCIAS DE IMPRESIÓN 3D (mm)
#    (Optimizado para cama de impresión de 220 x 215 x 245 mm: ninguna pieza > 200 mm)
# =====================================================================
L1 = 155.0          # Brazo principal (004): O1 -> E1 (Longitud total pieza: 192.0 mm <= 200 mm)
L2 = 130.0          # Antebrazo horizontal (005): E1 -> W1 (Longitud total pieza: 200.0 mm <= 200 mm)
L_PITCH = 28.0      # Distancia entre articulación de muñeca (W1) y eje de cabeceo (Pitch)
L3 = 90.0           # Soporte de pinza (012) + Dedos (013/014): Eje Pitch -> Punta
R_CRANK = 50.0      # Brazo de palanca de 002 (O1 -> A1) y extensión trasera de 005 (E1 -> B1)

# Dimensiones Reales del Acople Cilíndrico de Acero (según foto con pie de rey)
NUT_GAP_L = 12.0                    # Separación de tuerca y contratuerca desde cara azul de reductora
CYL_STEEL_L = 39.3                  # Largo real del cilindro metálico de acople
SHAFT_TOTAL_L = NUT_GAP_L + CYL_STEEL_L  # 51.3 mm totales desde la cara frontal de la reductora
SHAFT_ROT_D = 25.6                  # Diámetro exterior real del cilindro metálico (25.6 mm)
PIN_12_DIST_TIP = 13.5              # Distancia desde la punta del cilindro al centro del hueco Ø12.0 mm
Z_PIN_MOTOR = SHAFT_TOTAL_L - PIN_12_DIST_TIP  # 37.8 mm desde la cara frontal de la reductora

# Tolerancias de Impresión 3D (FDM) para Encajes, Paso Libre y Mamelones
SHAFT_FIT_R = (SHAFT_ROT_D / 2.0) + 0.20    # 13.00 mm (Ø26.00 mm para encaje deslizante del cilindro de 25.6 mm)
SHAFT_CLEAR_R = (SHAFT_ROT_D / 2.0) + 1.20  # 14.00 mm (Ø28.00 mm para paso libre holgado en paredes fijas)
HUB_OUTER_R = 23.0                  # Radio exterior del mamelón reforzado (Ø46.0 mm, pared maciza de 10 mm)

# Pasadores de Ø12.0 mm (Motores J1, J2, J3) - Listos para imprimir en 3D
MOTOR_PIN_NOM_D = 12.0
MOTOR_PIN_PRINT_D = MOTOR_PIN_NOM_D - 0.25  # Ø11.75 mm impreso para entrar sin atascos en el hueco de Ø12.0 mm
MOTOR_PIN_HOLE_R = (MOTOR_PIN_NOM_D / 2.0) + 0.15  # Radio 6.15 mm (Ø12.30 mm en piezas impresas)

# Pasadores de Articulaciones (Ø8.0 mm nominal) y Dedos (Ø4.0 mm nominal) - Listos para imprimir en 3D
PIVOT_PIN_NOM_D = 8.0
PIVOT_PIN_PRINT_D = PIVOT_PIN_NOM_D + 0.20  # Ø8.20 mm impreso para encaje ligeramente a presión en agujero Ø8.30 mm CAD
PIVOT_PIN_R = (PIVOT_PIN_NOM_D / 2.0) + 0.15  # Radio 4.15 mm (Ø8.30 mm en agujeros impresos)

FINGER_PIN_NOM_D = 4.0
FINGER_PIN_PRINT_D = FINGER_PIN_NOM_D - 0.20  # Ø3.80 mm impreso
FINGER_PIN_R = (FINGER_PIN_NOM_D / 2.0) + 0.15  # Radio 2.15 mm (Ø4.30 mm en agujeros impresos)

# Tornillería de Soportes de Motor y Unión Modular de Cunas (M4)
M4_CLEAR_R = 2.15                   # Ø4.30 mm paso libre en abrazadera superior 009 y bridas de cunas
M4_TAP_R = 1.85                     # Ø3.70 mm para roscar directo M4 en plástico (o usar inserto M4)

# Dimensiones Caja Reductora Planetaria Impresa + Motor NEMA 17
NEMA_W = 42.3
NEMA_L = 38.0
GEAR_W = 48.0                       # Ancho exterior de la carcasa impresa turquesa
GEAR_L = 44.0                       # Largo de la carcasa reductora turquesa
GEAR_BOLT = 35.0                    # Entrecentros de tornillos frontales de la reductora

# Vectores geométricos de los paralelogramos
U_REAR_X, U_REAR_Z = -45.0, 35.0    # Vector O1 -> O2 (y E1 -> T_rear en 006)
U_TOP_X, U_TOP_Z = -15.0, 42.0      # Vector E1 -> T_top en 006 (y W1 -> W2 en 020)


# =====================================================================
# 2. FUNCIÓN PARA PERFILES DE ENGRANAJES (TOPOLOGÍA MANIFOLD)
# =====================================================================
def perfil_engranaje(r_raiz, r_punta, num_dientes_total, dientes_activos, angulo_inicio=0.0):
    pts = []
    paso = (2.0 * math.pi) / num_dientes_total
    base = math.radians(angulo_inicio)
    for i in range(num_dientes_total):
        th = base + i * paso
        if i < dientes_activos:
            pts.extend([
                (r_raiz * math.cos(th + paso * 0.12), r_raiz * math.sin(th + paso * 0.12)),
                (r_punta * math.cos(th + paso * 0.28), r_punta * math.sin(th + paso * 0.28)),
                (r_punta * math.cos(th + paso * 0.52), r_punta * math.sin(th + paso * 0.52)),
                (r_raiz * math.cos(th + paso * 0.68), r_raiz * math.sin(th + paso * 0.68)),
                (r_raiz * math.cos(th + paso * 0.90), r_raiz * math.sin(th + paso * 0.90)),
            ])
        else:
            for k in range(1, 4):
                ak = th + paso * (k / 3.0)
                pts.append((r_raiz * math.cos(ak), r_raiz * math.sin(ak)))
    return pts


# =====================================================================
# 3. ACTUADORES: NEMA 17 + PLANETARIA (ACOPLE Ø25.6 x 39.3 + TUERCAS) Y SG90
# =====================================================================
def crear_actuador_planetario(angulo_pin_deg=0.0, z_pin=Z_PIN_MOTOR):
    """
    Modela el motorreductor exactamente como en la foto real:
    - Origen (0,0,0) en la cara frontal de la caja reductora turquesa.
    - Hacia -Z: Carcasa reductora (44 mm) + Placa blanca (8 mm) + Motor NEMA 17 (38 mm) = 90 mm.
    - Hacia +Z: Eje roscado con tuerca y contratuerca (0 a 12 mm) + Cilindro de acero Ø25.6 mm x 39.3 mm (12.0 a 51.3 mm).
    - Agujero transversal de Ø12.0 mm centrado a z_pin (37.8 mm desde la cara frontal, 13.5 mm desde la punta).
    """
    motor = (
        cq.Workplane("XY")
        .workplane(offset=-(GEAR_L + 8.0 + NEMA_L))
        .box(NEMA_W, NEMA_W, NEMA_L, centered=(True, True, False))
        .edges("|Z")
        .chamfer(3.0)
    )
    placa_blanca = (
        cq.Workplane("XY")
        .workplane(offset=-(GEAR_L + 8.0))
        .box(NEMA_W + 2.0, NEMA_W + 2.0, 8.0, centered=(True, True, False))
        .edges("|Z")
        .fillet(2.0)
    )
    caja_azul = (
        cq.Workplane("XY")
        .workplane(offset=-GEAR_L)
        .box(GEAR_W, GEAR_W, GEAR_L, centered=(True, True, False))
        .edges("|Z")
        .fillet(3.0)
    )
    vastago = cq.Workplane("XY").cylinder(NUT_GAP_L, 5.0, centered=(True, True, False))
    tuerca_1 = cq.Workplane("XY").workplane(offset=1.0).polygon(6, 17.5).extrude(5.0)
    tuerca_2 = cq.Workplane("XY").workplane(offset=6.5).polygon(6, 15.0).extrude(5.0)

    cil_acero = (
        cq.Workplane("XY")
        .workplane(offset=NUT_GAP_L)
        .cylinder(CYL_STEEL_L, SHAFT_ROT_D / 2.0, centered=(True, True, False))
        .faces(">Z")
        .edges()
        .chamfer(1.0)
    )
    corte_pin_12 = (
        cq.Workplane("YZ")
        .center(0, z_pin)
        .cylinder(40.0, MOTOR_PIN_NOM_D / 2.0)
        .rotate((0, 0, 0), (0, 0, 1), -angulo_pin_deg)
    )
    acople_completo = vastago.union(tuerca_1).union(tuerca_2).union(cil_acero).cut(corte_pin_12)
    return motor.union(placa_blanca).union(caja_azul).union(acople_completo)


def crear_micro_servo_sg90():
    """Micro-servo SG90/MG90S (usado tanto para cabeceo Pitch como para abrir/cerrar la garra)."""
    cuerpo = cq.Workplane("XY").box(23.0, 12.2, 24.0, centered=(True, True, False))
    pestanas = (
        cq.Workplane("XY")
        .workplane(offset=16.0)
        .box(32.5, 12.2, 2.5, centered=(True, True, False))
        .cut(cq.Workplane("XY").workplane(offset=15.0).pushPoints([(-14.0, 0), (14.0, 0)]).circle(1.2).extrude(5.0))
    )
    buje = cq.Workplane("XY").center(-5.5, 0).cylinder(4.0, 5.5, centered=(True, True, False))
    eje = cq.Workplane("XY").workplane(offset=-6.0).center(-5.5, 0).cylinder(6.0, 2.4, centered=(True, True, False))
    return cuerpo.union(pestanas).union(buje).union(eje)


def crear_pin_pasador(largo=46.0, diametro=MOTOR_PIN_PRINT_D, orientacion="X"):
    """Pasador cilíndrico listo para imprimir en 3D con chaflanes de entrada."""
    radio = diametro / 2.0
    if orientacion == "X":
        pin = cq.Workplane("YZ").cylinder(largo, radio)
    elif orientacion == "Y":
        pin = cq.Workplane("XZ").cylinder(largo, radio)
    else:
        pin = cq.Workplane("XY").cylinder(largo, radio)
    return pin.edges().chamfer(0.5)


def crear_tornillo_m4(largo_vastago=22.0):
    """Tornillo Allen M4 cilíndrico (eje vertical -Z) para abrazaderas superiores 009."""
    cabeza = cq.Workplane("XY").cylinder(4.0, 3.5, centered=(True, True, False)).edges(">Z").chamfer(0.3)
    hex_allen = cq.Workplane("XY").workplane(offset=2.0).polygon(6, 3.2).extrude(3.0)
    vastago = cq.Workplane("XY").workplane(offset=-largo_vastago).cylinder(largo_vastago, 1.8, centered=(True, True, False))
    return cabeza.cut(hex_allen).union(vastago)


def crear_tubo_central(largo=22.0):
    """Eje tubular central pasivo O1 (imprimible en 3D con Ø8.20 mm exterior)."""
    return (
        cq.Workplane("XZ")
        .cylinder(largo, PIVOT_PIN_PRINT_D / 2.0)
        .cut(cq.Workplane("XZ").cylinder(largo + 2.0, 2.0))
        .edges()
        .chamfer(0.4)
    )


# =====================================================================
# 4. PIEZAS ESTRUCTURALES MODULARES OPTIMIZADAS PARA CAMA 220x215x245 mm
# =====================================================================

# --- 010: BASEMENT (128 x 128 x 112 mm -> Cabe perfecto en 220x215x245) ---
def crear_010_basement():
    H_base = 112.0
    brida = cq.Workplane("XY").cylinder(10.0, 62.0, centered=(True, True, False))
    orejas = [(-48.0, -48.0), (48.0, -48.0), (48.0, 48.0), (-48.0, 48.0)]
    for x, y in orejas:
        brida = brida.union(cq.Workplane("XY").center(x, y).cylinder(10.0, 16.0, centered=(True, True, False)))

    cil_ext = cq.Workplane("XY").cylinder(H_base, 56.0, centered=(True, True, False))
    cavidad = cq.Workplane("XY").cylinder(94.0, 48.0, centered=(True, True, False))

    cuna_j1 = (
        cq.Workplane("XY")
        .box(56.0, 56.0, 40.0, centered=(True, True, False))
        .cut(cq.Workplane("XY").box(NEMA_W + 0.6, NEMA_W + 0.6, 42.0, centered=(True, True, False)))
    )

    hueco_rot_j1 = (
        cq.Workplane("XY")
        .workplane(offset=90.0)
        .cylinder(26.0, SHAFT_CLEAR_R, centered=(True, True, False))
    )
    tornillos_j1 = (
        cq.Workplane("XY")
        .workplane(offset=90.0)
        .rect(GEAR_BOLT, GEAR_BOLT, forConstruction=True)
        .vertices()
        .circle(2.1)
        .extrude(26.0)
    )
    anclajes = cq.Workplane("XY").pushPoints(orejas).circle(2.8).extrude(14.0)
    ventana_cables = cq.Workplane("XY").center(0, -52.0).box(34.0, 30.0, 30.0, centered=(True, True, False))

    taladros_holder = (
        cq.Workplane("YZ")
        .workplane(offset=-56.0)
        .pushPoints([(0, 30.0), (0, 62.0)])
        .circle(1.6)
        .extrude(-15.0)
    )

    return (
        brida.union(cil_ext)
        .cut(cavidad)
        .union(cuna_j1)
        .cut(hueco_rot_j1)
        .cut(tornillos_j1)
        .cut(anclajes)
        .cut(ventana_cables)
        .cut(taladros_holder)
    )


# --- 016: DRIVEN GEAR (58.9 x 55.3 x 35.0 mm) ---
def crear_016_driven_gear():
    pts = perfil_engranaje(r_raiz=26.0, r_punta=33.0, num_dientes_total=14, dientes_activos=5, angulo_inicio=110)
    gear = cq.Workplane("XY").polyline(pts).close().extrude(12.0)
    mamelon = cq.Workplane("XY").cylinder(29.0, HUB_OUTER_R, centered=(True, True, False))

    dados = (
        cq.Workplane("XY")
        .workplane(offset=29.0)
        .pushPoints([(-11.0, -14.0), (-11.0, 14.0)])
        .box(8.0, 8.0, 6.0, centered=(True, True, False))
    )
    agujero_256 = cq.Workplane("XY").cylinder(36.0, SHAFT_FIT_R, centered=(True, True, False))
    pasador_12 = cq.Workplane("YZ").center(0, 19.8).cylinder(50.0, MOTOR_PIN_HOLE_R)
    return gear.union(mamelon).union(dados).cut(agujero_256).cut(pasador_12)


# --- 011: ROUND PLATE (112 x 112 x 14 mm) ---
def crear_011_round_plate():
    disco = cq.Workplane("XY").cylinder(8.0, 56.0, centered=(True, True, False)).edges(">Z").fillet(2.5)
    rieles = (
        cq.Workplane("XY")
        .workplane(offset=8.0)
        .pushPoints([(0, -28.0), (0, 28.0)])
        .box(60.0, 5.8, 6.0, centered=(True, True, False))
    )
    cajas_dados = (
        cq.Workplane("XY")
        .pushPoints([(-11.0, -14.0), (-11.0, 14.0)])
        .box(8.4, 8.4, 6.5, centered=(True, True, False))
    )
    agujero_central = cq.Workplane("XY").cylinder(20.0, SHAFT_FIT_R, centered=(True, True, False))
    return disco.union(rieles).cut(cajas_dados).cut(agujero_central)


# --- 001: MAIN BODY (Núcleo Central Modular de 90 x 126 x 94 mm para caber holgado en 220x215 mm) ---
def crear_001_main_body():
    """
    Núcleo central modular de la torreta (90.0 x 126.0 x 94.0 mm):
    - Abarca desde Y = -56.0 mm (plano de montaje de Motor J2 y Cuna Izquierda 001B)
      hasta Y = +70.0 mm (plano de montaje de Motor J3 y Cuna Derecha 001C).
    - Incluye chavetas hembra de encaje (12.4 x 4.0 x 16.0 mm) y 4 roscas horizontales M4
      en cada cara exterior para atornillar rígidamente las cunas macizas 001B y 001C.
    """
    Z_O1 = 48.0
    W_torreta = 68.0
    Z_tope_cuna = Z_O1 + 6.0  # 54.0 mm

    plato_central = (
        cq.Workplane("XY")
        .center(0, 7.0)
        .box(W_torreta, 126.0, 12.0, centered=(True, True, False))
    )

    ranuras_rieles = (
        cq.Workplane("XY")
        .pushPoints([(0, -28.0), (0, 28.0)])
        .box(60.5, 6.2, 6.5, centered=(True, True, False))
    )

    pilar = (
        cq.Workplane("XZ")
        .workplane(offset=-1.0)
        .polyline([(-24.0, 12.0), (20.0, 12.0), (12.0, Z_O1), (-12.0, Z_O1)])
        .close()
        .extrude(7.0, both=True)
        .union(cq.Workplane("XZ").workplane(offset=-1.0).center(0, Z_O1).cylinder(14.0, 14.0))
    )

    # PARED IZQUIERDA (Y in [-56.0, -32.0], centro Y = -44.0)
    pared_izq = (
        cq.Workplane("XY")
        .center(0, -44.0)
        .box(W_torreta, 24.0, Z_O1 + 22.0, centered=(True, True, False))
        .edges("|Y and >Z")
        .chamfer(8.0)
    )
    pasante_28_izq = cq.Workplane("XZ").workplane(offset=44.0).center(0, Z_O1).cylinder(28.0, SHAFT_CLEAR_R)
    tornillos_j2 = (
        cq.Workplane("XZ")
        .workplane(offset=44.0)
        .center(0, Z_O1)
        .rect(GEAR_BOLT, GEAR_BOLT, forConstruction=True)
        .vertices()
        .circle(2.1)
        .extrude(28.0, both=True)
    )
    roscas_union_izq = (
        cq.Workplane("XZ")
        .workplane(offset=56.0)
        .pushPoints([(-29.0, 10.0), (29.0, 10.0), (-29.0, 36.0), (29.0, 36.0)])
        .circle(M4_TAP_R)
        .extrude(22.0, both=True)
    )
    ranuras_guia_izq = (
        cq.Workplane("XY")
        .workplane(offset=14.0)
        .pushPoints([(-29.0, -54.0), (29.0, -54.0)])
        .box(12.4, 4.5, 16.4, centered=(True, True, False))
    )

    # PARED DERECHA (Y in [+44.0, +70.0], centro Y = +57.0)
    pared_der = (
        cq.Workplane("XY")
        .center(0, 57.0)
        .box(W_torreta, 26.0, Z_O1 + 22.0, centered=(True, True, False))
        .edges("|Y and >Z")
        .chamfer(8.0)
    )
    pasante_28_der = cq.Workplane("XZ").workplane(offset=-57.0).center(0, Z_O1).cylinder(30.0, SHAFT_CLEAR_R)
    tornillos_j3 = (
        cq.Workplane("XZ")
        .workplane(offset=-57.0)
        .center(0, Z_O1)
        .rect(GEAR_BOLT, GEAR_BOLT, forConstruction=True)
        .vertices()
        .circle(2.1)
        .extrude(30.0, both=True)
    )
    roscas_union_der = (
        cq.Workplane("XZ")
        .workplane(offset=-70.0)
        .pushPoints([(-29.0, 10.0), (29.0, 10.0), (-29.0, 36.0), (29.0, 36.0)])
        .circle(M4_TAP_R)
        .extrude(22.0, both=True)
    )
    ranuras_guia_der = (
        cq.Workplane("XY")
        .workplane(offset=14.0)
        .pushPoints([(-29.0, 68.0), (29.0, 68.0)])
        .box(12.4, 4.5, 16.4, centered=(True, True, False))
    )

    cuerno_o2 = (
        cq.Workplane("XZ")
        .workplane(offset=-49.0)
        .polyline([(-14.0, 12.0), (U_REAR_X, Z_O1 + U_REAR_Z + 9.0), (U_REAR_X, Z_O1 + U_REAR_Z - 12.0), (-26.0, 12.0)])
        .close()
        .extrude(5.0, both=True)
        .union(cq.Workplane("XZ").workplane(offset=-49.0).center(U_REAR_X, Z_O1 + U_REAR_Z).cylinder(10.0, 11.0))
    )

    alivio_punta_j2 = cq.Workplane("XZ").workplane(offset=6.0).center(0, Z_O1).cylinder(4.0, SHAFT_CLEAR_R)
    pasante_pilar_central = cq.Workplane("XZ").center(0, Z_O1).cylinder(24.0, PIVOT_PIN_R)
    pasante_o2 = cq.Workplane("XZ").workplane(offset=-49.0).center(U_REAR_X, Z_O1 + U_REAR_Z).cylinder(20.0, PIVOT_PIN_R)

    return (
        plato_central.union(pared_izq)
        .union(pared_der)
        .cut(ranuras_rieles)
        .cut(tornillos_j2)
        .cut(pasante_28_izq)
        .cut(roscas_union_izq)
        .cut(ranuras_guia_izq)
        .cut(tornillos_j3)
        .cut(pasante_28_der)
        .cut(roscas_union_der)
        .cut(ranuras_guia_der)
        .union(pilar)
        .union(cuerno_o2)
        .cut(alivio_punta_j2)
        .cut(pasante_pilar_central)
        .cut(pasante_o2)
    )


# --- 001B: CUNA MODULAR MACIZA IZQUIERDA (68 x 95.8 x 54 mm -> Cabe perfecto en 220x215 mm) ---
def crear_001B_cuna_motor_izq():
    """
    Cuna exterior maciza para el Motor J2 (Izquierdo):
    - Se apoya desde Z = 0.0 mm hasta Z = 54.0 mm (sin voladizos).
    - Se acopla a la cara Y = -56.0 mm del núcleo 001 mediante 2 chavetas macho de encaje
      y 4 tornillos horizontales M4 con cajeras internas de acceso, más 4 roscas superiores M4 para 009.
    """
    Z_O1 = 48.0
    W_torreta = 68.0
    Z_piso_gear = Z_O1 - (GEAR_W / 2.0)  # 24.0 mm
    Z_piso_nema = Z_O1 - (NEMA_W / 2.0)  # 26.85 mm
    Z_tope_cuna = Z_O1 + 6.0             # 54.0 mm

    bloque = (
        cq.Workplane("XY")
        .center(0, -102.0)
        .box(W_torreta, 92.0, Z_tope_cuna, centered=(True, True, False))
        .edges("|Z and <Y")
        .chamfer(3.0)
    )
    chavetas = (
        cq.Workplane("XY")
        .workplane(offset=14.2)
        .pushPoints([(-29.0, -54.1), (29.0, -54.1)])
        .box(12.0, 3.8, 15.8, centered=(True, True, False))
    )
    hueco_gear = (
        cq.Workplane("XY")
        .workplane(offset=Z_piso_gear)
        .center(0, -82.0)
        .box(GEAR_W + 0.5, 52.5, 50.0, centered=(True, True, False))
    )
    hueco_nema = (
        cq.Workplane("XY")
        .workplane(offset=Z_piso_nema)
        .center(0, -128.0)
        .box(NEMA_W + 0.5, 44.0, 50.0, centered=(True, True, False))
    )
    roscas_m4_sup = (
        cq.Workplane("XY")
        .workplane(offset=Z_tope_cuna - 22.0)
        .center(0, -80.0)
        .rect(56.0, 18.0, forConstruction=True)
        .vertices()
        .circle(M4_TAP_R)
        .extrude(25.0)
    )
    agujeros_union_m4 = (
        cq.Workplane("XZ")
        .workplane(offset=56.0)
        .pushPoints([(-29.0, 10.0), (29.0, 10.0), (-29.0, 36.0), (29.0, 36.0)])
        .circle(M4_CLEAR_R)
        .extrude(30.0, both=True)
    )
    bolsillos_acceso_m4 = (
        cq.Workplane("XY")
        .workplane(offset=4.0)
        .pushPoints([(-29.0, -78.0), (29.0, -78.0)])
        .box(12.0, 20.0, 13.0, centered=(True, True, False))
        .union(
            cq.Workplane("XY")
            .workplane(offset=30.0)
            .pushPoints([(-29.0, -78.0), (29.0, -78.0)])
            .box(12.0, 20.0, 13.0, centered=(True, True, False))
        )
    )

    return (
        bloque.union(chavetas)
        .cut(hueco_gear)
        .cut(hueco_nema)
        .cut(roscas_m4_sup)
        .cut(agujeros_union_m4)
        .cut(bolsillos_acceso_m4)
    )


# --- 001C: CUNA MODULAR MACIZA DERECHA (68 x 95.8 x 54 mm -> Cabe perfecto en 220x215 mm) ---
def crear_001C_cuna_motor_der():
    """
    Cuna exterior maciza para el Motor J3 (Derecho):
    - Se apoya desde Z = 0.0 mm hasta Z = 54.0 mm (sin voladizos).
    - Se acopla a la cara Y = +70.0 mm del núcleo 001 mediante 2 chavetas macho de encaje
      y 4 tornillos horizontales M4 con cajeras internas de acceso, más 4 roscas superiores M4 para 009.
    """
    Z_O1 = 48.0
    W_torreta = 68.0
    Z_piso_gear = Z_O1 - (GEAR_W / 2.0)
    Z_piso_nema = Z_O1 - (NEMA_W / 2.0)
    Z_tope_cuna = Z_O1 + 6.0

    bloque = (
        cq.Workplane("XY")
        .center(0, 116.0)
        .box(W_torreta, 92.0, Z_tope_cuna, centered=(True, True, False))
        .edges("|Z and >Y")
        .chamfer(3.0)
    )
    chavetas = (
        cq.Workplane("XY")
        .workplane(offset=14.2)
        .pushPoints([(-29.0, 68.1), (29.0, 68.1)])
        .box(12.0, 3.8, 15.8, centered=(True, True, False))
    )
    hueco_gear = (
        cq.Workplane("XY")
        .workplane(offset=Z_piso_gear)
        .center(0, 96.0)
        .box(GEAR_W + 0.5, 52.5, 50.0, centered=(True, True, False))
    )
    hueco_nema = (
        cq.Workplane("XY")
        .workplane(offset=Z_piso_nema)
        .center(0, 142.0)
        .box(NEMA_W + 0.5, 44.0, 50.0, centered=(True, True, False))
    )
    roscas_m4_sup = (
        cq.Workplane("XY")
        .workplane(offset=Z_tope_cuna - 22.0)
        .center(0, 94.0)
        .rect(56.0, 18.0, forConstruction=True)
        .vertices()
        .circle(M4_TAP_R)
        .extrude(25.0)
    )
    agujeros_union_m4 = (
        cq.Workplane("XZ")
        .workplane(offset=-70.0)
        .pushPoints([(-29.0, 10.0), (29.0, 10.0), (-29.0, 36.0), (29.0, 36.0)])
        .circle(M4_CLEAR_R)
        .extrude(30.0, both=True)
    )
    bolsillos_acceso_m4 = (
        cq.Workplane("XY")
        .workplane(offset=4.0)
        .pushPoints([(-29.0, 92.0), (29.0, 92.0)])
        .box(12.0, 20.0, 13.0, centered=(True, True, False))
        .union(
            cq.Workplane("XY")
            .workplane(offset=30.0)
            .pushPoints([(-29.0, 92.0), (29.0, 92.0)])
            .box(12.0, 20.0, 13.0, centered=(True, True, False))
        )
    )

    return (
        bloque.union(chavetas)
        .cut(hueco_gear)
        .cut(hueco_nema)
        .cut(roscas_m4_sup)
        .cut(agujeros_union_m4)
        .cut(bolsillos_acceso_m4)
    )


# --- 009: SERVO PLATE (Abrazadera Superior Reforzada de 68 mm con 4 Tornillos M4) ---
def crear_009_servo_plate():
    W_clamp = 68.0
    L_clamp = 32.0
    H_clamp = 26.0
    arco = (
        cq.Workplane("XY")
        .box(W_clamp, L_clamp, H_clamp, centered=(True, True, False))
        .edges("|Y and >Z")
        .fillet(5.0)
        .cut(cq.Workplane("XY").box(GEAR_W + 0.5, L_clamp + 4.0, 18.5, centered=(True, True, False)))
    )
    agujeros_m4 = (
        cq.Workplane("XY")
        .rect(56.0, 18.0, forConstruction=True)
        .vertices()
        .circle(M4_CLEAR_R)
        .extrude(H_clamp + 2.0)
    )
    cajeras_cabeza = (
        cq.Workplane("XY")
        .workplane(offset=H_clamp - 4.5)
        .rect(56.0, 18.0, forConstruction=True)
        .vertices()
        .circle(4.2)
        .extrude(6.0)
    )
    return arco.cut(agujeros_m4).cut(cajeras_cabeza)


# --- 002: VERTICAL DRIVE ARM (87.0 x 23.0 x 46.0 mm) ---
def crear_002_vertical_drive_arm():
    barra = (
        cq.Workplane("XZ")
        .workplane(offset=-5.5)
        .center(-R_CRANK / 2.0, 0)
        .slot2D(R_CRANK + 28.0, 28.0, 0)
        .extrude(5.5, both=True)
    )
    mamelon_o1 = cq.Workplane("XZ").cylinder(23.0, HUB_OUTER_R)
    hueco_256 = cq.Workplane("XZ").cylinder(28.0, SHAFT_FIT_R)
    hueco_a1 = cq.Workplane("XZ").center(-R_CRANK, 0).cylinder(28.0, PIVOT_PIN_R)
    agujero_pin_12 = cq.Workplane("YZ").cylinder(52.0, MOTOR_PIN_HOLE_R)

    return barra.union(mamelon_o1).cut(hueco_256).cut(hueco_a1).cut(agujero_pin_12)


# --- 003: LINK (176 mm para L1=155 mm; 151 mm para L2=130 mm) ---
def crear_003_link(L_biela=L1):
    barra = cq.Workplane("XZ").center(L_biela / 2.0, 0).box(L_biela, 13.0, 6.0)
    o1 = cq.Workplane("XZ").cylinder(6.0, 10.5)
    o2 = cq.Workplane("XZ").center(L_biela, 0).cylinder(6.0, 10.5)
    rebaje = cq.Workplane("XZ").center(L_biela / 2.0, 0).box(L_biela - 28.0, 6.0, 3.0)
    h1 = cq.Workplane("XZ").cylinder(12.0, PIVOT_PIN_R)
    h2 = cq.Workplane("XZ").center(L_biela, 0).cylinder(12.0, PIVOT_PIN_R)
    return barra.union(o1).union(o2).cut(rebaje).cut(h1).cut(h2)


# --- 004: FORWARD DRIVE ARM (192.0 x 48.0 x 46.0 mm -> Cabe holgado en 220x215 mm) ---
def crear_004_forward_drive_arm():
    m_izq = (
        cq.Workplane("XZ")
        .workplane(offset=18.20)
        .center(L1 / 2.0, 0)
        .slot2D(L1 + 28.0, 28.0, 0)
        .extrude(6.5, both=True)
        .union(cq.Workplane("XZ").workplane(offset=18.20).cylinder(23.0, HUB_OUTER_R))
    )
    m_der = (
        cq.Workplane("XZ")
        .workplane(offset=-13.25)
        .center(L1 / 2.0, 0)
        .slot2D(L1 + 28.0, 28.0, 0)
        .extrude(5.0, both=True)
    )
    puentes = (
        cq.Workplane("XY")
        .center(L1 / 2.0 + 10.0, -2.5)
        .box(L1 - 76.0, 25.0, 28.0)
        .cut(cq.Workplane("XY").center(L1 / 2.0 - 14.0, -2.5).box(18.0, 30.0, 32.0))
        .cut(cq.Workplane("XY").center(L1 / 2.0 + 34.0, -2.5).box(18.0, 30.0, 32.0))
    )
    eje_256_izq = cq.Workplane("XZ").workplane(offset=18.20).cylinder(25.0, SHAFT_FIT_R)
    pin_transversal_j2 = (
        cq.Workplane("YZ")
        .center(-18.20, 0)
        .cylinder(52.0, MOTOR_PIN_HOLE_R)
    )
    eje_pasivo_der = cq.Workplane("XZ").workplane(offset=-13.25).cylinder(14.0, PIVOT_PIN_R)
    eje_codo_e1 = cq.Workplane("XZ").center(L1, 0).cylinder(60.0, PIVOT_PIN_R)

    return (
        m_izq.union(m_der)
        .union(puentes)
        .cut(eje_256_izq)
        .cut(pin_transversal_j2)
        .cut(eje_pasivo_der)
        .cut(eje_codo_e1)
    )


# --- 005: HORIZONTAL ARM (200.0 x 33.5 x 20.0 mm -> Cabe con 20 mm de margen en cama de 220x215 mm) ---
def crear_005_horizontal_arm():
    L_tot = R_CRANK + L2
    x_mid = (L2 - R_CRANK) / 2.0
    barra = (
        cq.Workplane("XZ")
        .workplane(offset=4.0)
        .center(x_mid, 0)
        .slot2D(L_tot + 20.0, 20.0, 0)
        .extrude(4.0, both=True)
    )
    boss_b1 = cq.Workplane("XZ").workplane(offset=-12.75).center(-R_CRANK, 0).cylinder(25.5, 10.0)
    slot1 = cq.Workplane("XZ").center(-R_CRANK / 2.0, 0).slot2D(24.0, 7.0, 0).extrude(25.0, both=True)
    slot2 = cq.Workplane("XZ").center(L2 / 2.0, 0).slot2D(75.0, 7.0, 0).extrude(25.0, both=True)

    h_b1 = cq.Workplane("XZ").center(-R_CRANK, 0).cylinder(55.0, PIVOT_PIN_R)
    h_e1 = cq.Workplane("XZ").cylinder(25.0, PIVOT_PIN_R)
    h_w1 = cq.Workplane("XZ").center(L2, 0).cylinder(25.0, PIVOT_PIN_R)

    return barra.union(boss_b1).cut(slot1).cut(slot2).cut(h_b1).cut(h_e1).cut(h_w1)


# --- 006: TRIANGULAR LINK (65.0 x 37.0 x 62.0 mm) ---
def crear_006_triangular_link():
    placa = (
        cq.Workplane("XZ")
        .workplane(offset=-4.125)
        .polyline([(0, 0), (U_REAR_X, U_REAR_Z), (U_TOP_X, U_TOP_Z)])
        .close()
        .extrude(3.875, both=True)
    )
    o_e1 = cq.Workplane("XZ").workplane(offset=-4.125).cylinder(7.75, 10.0)
    o_top = cq.Workplane("XZ").workplane(offset=-4.125).center(U_TOP_X, U_TOP_Z).cylinder(7.75, 10.0)
    o_rear = cq.Workplane("XZ").workplane(offset=-18.75).center(U_REAR_X, U_REAR_Z).cylinder(37.0, 10.0)

    h_e1 = cq.Workplane("XZ").cylinder(30.0, PIVOT_PIN_R)
    h_rear = cq.Workplane("XZ").center(U_REAR_X, U_REAR_Z).cylinder(80.0, PIVOT_PIN_R)
    h_top = cq.Workplane("XZ").center(U_TOP_X, U_TOP_Z).cylinder(30.0, PIVOT_PIN_R)

    return placa.union(o_e1).union(o_top).union(o_rear).cut(h_e1).cut(h_rear).cut(h_top)


# --- 020: WRIST PITCH BRACKET (Con Cuna Anti-Rotación y Pilares para el Servo SG90 de Cabeceo) ---
def crear_020_wrist_pitch_bracket():
    """
    Soporte de muñeca estabilizado por el paralelogramo (W1 y W2) con CUNA COMPLETA ANTI-ROTACIÓN para el servo SG90:
    - Además de la ventana rectangular que abraza el cuerpo del SG90, incorpora una jaula/cuna exterior
      de paredes de 3.2 mm y dos pilares de atornillado en Y = -20.0 a -36.5 mm con perforaciones para los 2 tornillos
      de las pestañas del servo SG90. Así la carcasa del servo queda 100% bloqueada contra el giro y solo mueve la garra.
    """
    orejas = cq.Workplane("XY")
    for y_c in [-11.25, 3.25]:
        oreja = (
            cq.Workplane("XZ")
            .workplane(offset=-y_c)
            .polyline([(-8.0, -8.0), (14.0, -8.0), (14.0, 8.0), (U_TOP_X + 8.0, U_TOP_Z), (U_TOP_X - 8.0, U_TOP_Z)])
            .close()
            .extrude(3.0, both=True)
            .union(cq.Workplane("XZ").workplane(offset=-y_c).cylinder(6.0, 9.5))
            .union(cq.Workplane("XZ").workplane(offset=-y_c).center(U_TOP_X, U_TOP_Z).cylinder(6.0, 9.5))
        )
        orejas = orejas.union(oreja)

    puente = (
        cq.Workplane("XY")
        .workplane(offset=-8.0)
        .center(13.5, -4.0)
        .box(6.0, 40.0, 16.0, centered=(True, True, False))
    )
    # Brazo izquierdo hacia el eje Pitch (X = 10.5 a 53.5, Y in [-24.0, -20.0])
    pared_servo_izq = (
        cq.Workplane("XZ")
        .workplane(offset=22.0)
        .polyline([(10.5, -9.2), (L_PITCH + 25.5, -9.2), (L_PITCH + 25.5, 9.2), (10.5, 9.2)])
        .close()
        .extrude(2.0, both=True)
    )
    # Cuna / Jaula exterior anti-rotación que envuelve el cuerpo del SG90 y soporta sus pestañas hasta Y = -36.5 mm
    cuna_antirotacion_sg90 = (
        cq.Workplane("XZ")
        .workplane(offset=20.0)
        .center(L_PITCH + 5.5, 0.0)
        .rect(40.0, 18.4)
        .extrude(16.5)  # Extiende desde Y = -20.0 hasta Y = -36.5 mm (justo donde asientan las pestañas del SG90)
    )
    # Vaciado interior exacto para el cuerpo rectangular del SG90 (23.6 x 12.6 mm) + ranura inferior para cable
    hueco_cuerpo_sg90 = (
        cq.Workplane("XZ")
        .workplane(offset=18.0)
        .center(L_PITCH + 5.5, 0.0)
        .box(23.6, 12.6, 50.0)
    )
    # Agujeros para los 2 tornillos de fijación de las pestañas del SG90 (en X = L_PITCH + 5.5 ± 14.0 mm)
    tornillos_fijacion_sg90 = (
        cq.Workplane("XZ")
        .workplane(offset=20.0)
        .pushPoints([(L_PITCH + 5.5 - 14.0, 0.0), (L_PITCH + 5.5 + 14.0, 0.0)])
        .circle(1.2)
        .extrude(20.0)
    )

    # Brazo derecho de soporte pasivo: Y in [+12.0, +16.0] (centro Y = +14.0, espesor 4.0 mm)
    pared_pivote_der = (
        cq.Workplane("XZ")
        .workplane(offset=-14.0)
        .polyline([(10.5, -8.0), (L_PITCH, -8.0), (L_PITCH, 8.0), (10.5, 8.0)])
        .close()
        .extrude(2.0, both=True)
        .union(cq.Workplane("XZ").workplane(offset=-14.0).center(L_PITCH, 0).cylinder(4.0, 8.5))
    )

    h_w1 = cq.Workplane("XZ").cylinder(40.0, PIVOT_PIN_R)
    h_w2 = cq.Workplane("XZ").center(U_TOP_X, U_TOP_Z).cylinder(40.0, PIVOT_PIN_R)
    h_pitch_der = cq.Workplane("XZ").workplane(offset=-14.0).center(L_PITCH, 0).cylinder(10.0, PIVOT_PIN_R)

    return (
        orejas.union(puente)
        .union(pared_servo_izq.union(cuna_antirotacion_sg90).cut(hueco_cuerpo_sg90).cut(tornillos_fijacion_sg90))
        .union(pared_pivote_der)
        .cut(h_w1)
        .cut(h_w2)
        .cut(h_pitch_der)
    )


# --- 021: TAPA / ABRAZADERA TRASERA DEL SERVO PITCH (Sujeta el servo SG90 por detrás para bloqueo total) ---
def crear_021_wrist_servo_clamp():
    """
    Pequeña abrazadera / tapa trasera (40.0 x 18.4 x 12.0 mm) que abraza la cola del servo SG90 de cabeceo (Pitch)
    desde Y = -39.0 hasta Y = -51.0 mm y se atornilla sobre las pestañas del servo hacia los pilares de 020.
    Así el servo queda prensado tipo sándwich y jamás puede girar ni salirse hacia afuera.
    """
    bloque = (
        cq.Workplane("XZ")
        .workplane(offset=39.0)
        .center(0, 0)
        .rect(40.0, 18.4)
        .extrude(12.0)  # Y in [-51.0, -39.0]
        .edges("|Y")
        .chamfer(2.0)
    )
    # Alojamiento interno para la parte trasera del cuerpo del SG90 (de Y = -39.0 a Y = -45.0) con tope trasero de 6 mm
    cajera_cola_sg90 = (
        cq.Workplane("XZ")
        .workplane(offset=38.5)
        .center(0, 0)
        .rect(23.6, 12.6)
        .extrude(6.5)
    )
    # Ventana central para salida de cables y ventilación
    ventana_cables = (
        cq.Workplane("XZ")
        .workplane(offset=38.0)
        .center(0, 0)
        .rect(14.0, 9.0)
        .extrude(15.0)
    )
    # Perforaciones pasantes para los 2 tornillos M2/autorroscantes del servo (X = ±14.0 mm)
    agujeros_tornillos = (
        cq.Workplane("XZ")
        .workplane(offset=38.0)
        .pushPoints([(-14.0, 0.0), (14.0, 0.0)])
        .circle(1.5)
        .extrude(15.0)
    )
    return bloque.cut(cajera_cola_sg90).cut(ventana_cables).cut(agujeros_tornillos)


# --- 012: CLAW SUPPORT (Con Cavidad Empotrada Anti-Rotación para el Servo SG90 de la Pinza) ---
def crear_012_claw_support():
    """
    Soporte de la garra con articulación de cabeceo (Pitch) y collarín elevado de 14 mm de profundidad
    que abraza las 4 caras del servo SG90 de la pinza + 2 postes reforzados para sus tornillos.
    """
    placa = (
        cq.Workplane("XY")
        .workplane(offset=-10.0)
        .center(29.0, -4.0)
        .box(34.0, 29.0, 6.0, centered=(True, True, False))
        .edges("|Z")
        .chamfer(3.0)
    )
    # Collarín superior anti-rotación que sube hasta Z = +6.0 mm (altura de las pestañas del SG90)
    collarin_servo_garra = (
        cq.Workplane("XY")
        .workplane(offset=-4.0)
        .center(27.5, -4.0)
        .box(34.0, 18.0, 10.0, centered=(True, True, False))
        .edges("|Z")
        .chamfer(2.0)
    )
    orejas_pitch = cq.Workplane("XY")
    for y_c in [-16.5, 8.5]:
        oreja_p = (
            cq.Workplane("XZ")
            .workplane(offset=-y_c)
            .polyline([(0.0, -7.5), (14.0, -10.0), (14.0, -4.0), (0.0, 7.5)])
            .close()
            .extrude(2.0, both=True)
            .union(cq.Workplane("XZ").workplane(offset=-y_c).cylinder(4.0, 7.5))
        )
        orejas_pitch = orejas_pitch.union(oreja_p)

    hueco_sg90 = (
        cq.Workplane("XY")
        .workplane(offset=-12.0)
        .center(27.5, -4.0)
        .box(23.6, 12.6, 20.0, centered=(True, True, False))
    )
    tornillos_sg90 = (
        cq.Workplane("XY")
        .workplane(offset=-12.0)
        .pushPoints([(27.5 - 14.0, -4.0), (27.5 + 14.0, -4.0)])
        .circle(1.2)
        .extrude(20.0)
    )
    pivotes_dedos = (
        cq.Workplane("XY")
        .workplane(offset=-12.0)
        .pushPoints([(42.0, -13.0), (42.0, 5.0)])
        .circle(FINGER_PIN_R)
        .extrude(12.0)
    )
    h_servo_izq = cq.Workplane("XZ").workplane(offset=16.5).cylinder(8.0, 2.55)
    h_pin_der = cq.Workplane("XZ").workplane(offset=-8.5).cylinder(8.0, PIVOT_PIN_R)

    return (
        placa.union(collarin_servo_garra)
        .union(orejas_pitch)
        .cut(hueco_sg90)
        .cut(tornillos_sg90)
        .cut(pivotes_dedos)
        .cut(h_servo_izq)
        .cut(h_pin_der)
    )


# --- 013, 014, 015: DEDOS Y ENGRANAJES DE LA PINZA ---
def crear_013_right_finger():
    pts = perfil_engranaje(r_raiz=7.0, r_punta=10.2, num_dientes_total=12, dientes_activos=5, angulo_inicio=30)
    gear = cq.Workplane("XY").polyline(pts).close().extrude(5.0)
    brazo = cq.Workplane("XY").center(20.0, -2.0).box(36.0, 6.0, 5.0, centered=(True, True, False))
    mordaza = (
        cq.Workplane("XY")
        .polyline([(36.0, -5.0), (48.0, -1.0), (48.0, 8.0), (36.0, 4.0)])
        .close()
        .extrude(12.0)
    )
    return gear.union(brazo).union(mordaza).cut(cq.Workplane("XY").cylinder(15.0, FINGER_PIN_R))


def crear_014_left_finger():
    pts = perfil_engranaje(r_raiz=7.0, r_punta=10.2, num_dientes_total=12, dientes_activos=5, angulo_inicio=-73)
    gear = cq.Workplane("XY").polyline(pts).close().extrude(5.0)
    brazo = cq.Workplane("XY").center(20.0, 2.0).box(36.0, 6.0, 5.0, centered=(True, True, False))
    mordaza = (
        cq.Workplane("XY")
        .polyline([(36.0, 5.0), (48.0, 1.0), (48.0, -8.0), (36.0, -4.0)])
        .close()
        .extrude(12.0)
    )
    return gear.union(brazo).union(mordaza).cut(cq.Workplane("XY").cylinder(15.0, FINGER_PIN_R))


def crear_015_drive_gear():
    pts = perfil_engranaje(r_raiz=10.0, r_punta=13.0, num_dientes_total=16, dientes_activos=16, angulo_inicio=15)
    gear = cq.Workplane("XY").polyline(pts).close().extrude(5.0)
    hueco = cq.Workplane("XY").cylinder(12.0, 2.5)
    corte_c = cq.Workplane("XY").center(4.0, 0).box(8.0, 3.5, 12.0)
    return gear.cut(hueco).cut(corte_c)


# --- 018: MAESTRO HOLDER ---
def crear_018_maestro_holder():
    caja = cq.Workplane("XY").box(20.0, 32.0, 48.0, centered=(True, True, False))
    vaciado = cq.Workplane("XY").center(-3.0, 0).box(18.0, 26.0, 50.0, centered=(True, True, False))
    agujeros = (
        cq.Workplane("YZ")
        .workplane(offset=10.0)
        .pushPoints([(0, 8.0), (0, 40.0)])
        .circle(1.6)
        .extrude(-15.0)
    )
    return caja.cut(vaciado).cut(agujeros)


# =====================================================================
# 5. EXPORTACIÓN DE PIEZAS IMPRIMIBLES EN 3D Y ENSAMBLE COMPLETO
# =====================================================================
if __name__ == "__main__":
    THETA1_DEG = 60.0
    PITCH_GARRA_DEG = -15.0
    th1 = math.radians(THETA1_DEG)

    actuador_recto_j1 = crear_actuador_planetario(angulo_pin_deg=0.0, z_pin=Z_PIN_MOTOR)
    actuador_j2 = crear_actuador_planetario(angulo_pin_deg=THETA1_DEG, z_pin=Z_PIN_MOTOR)
    actuador_j3 = crear_actuador_planetario(angulo_pin_deg=0.0, z_pin=Z_PIN_MOTOR)
    servo_sg90 = crear_micro_servo_sg90()
    tubo_central = crear_tubo_central(22.0)
    tornillo_m4 = crear_tornillo_m4(22.0)
    tornillo_m4_union = crear_tornillo_m4(25.0)

    # Pasadores de Ø12.0 mm nominal (Ø11.75 mm impresos en 3D)
    pin_12_motor_x = crear_pin_pasador(largo=46.0, diametro=MOTOR_PIN_PRINT_D, orientacion="X")

    # Pasadores de articulación de Ø8.0 mm nominal (Ø8.20 mm impresos en 3D, encaje ligeramente a presión)
    pin_a1 = crear_pin_pasador(largo=18.0, diametro=PIVOT_PIN_PRINT_D, orientacion="Y")
    pin_b1 = crear_pin_pasador(largo=18.0, diametro=PIVOT_PIN_PRINT_D, orientacion="Y")
    pin_o2 = crear_pin_pasador(largo=18.0, diametro=PIVOT_PIN_PRINT_D, orientacion="Y")
    pin_e1_codo = crear_pin_pasador(largo=46.0, diametro=PIVOT_PIN_PRINT_D, orientacion="Y")
    pin_t_rear = crear_pin_pasador(largo=16.0, diametro=PIVOT_PIN_PRINT_D, orientacion="Y")
    pin_t_top = crear_pin_pasador(largo=16.0, diametro=PIVOT_PIN_PRINT_D, orientacion="Y")
    pin_w1_muneca = crear_pin_pasador(largo=20.0, diametro=PIVOT_PIN_PRINT_D, orientacion="Y")
    pin_w2_muneca = crear_pin_pasador(largo=20.0, diametro=PIVOT_PIN_PRINT_D, orientacion="Y")
    pin_pitch_der = crear_pin_pasador(largo=9.0, diametro=PIVOT_PIN_PRINT_D, orientacion="Y")

    # Pasadores de dedos Ø4.0 mm nominal (Ø3.80 mm impresos en 3D)
    pin_dedo_der = crear_pin_pasador(largo=14.0, diametro=FINGER_PIN_PRINT_D, orientacion="Z")
    pin_dedo_izq = crear_pin_pasador(largo=14.0, diametro=FINGER_PIN_PRINT_D, orientacion="Z")

    biela_L1 = crear_003_link(L1)
    biela_L2 = crear_003_link(L2)

    piezas = {
        "EBA_01.00.001": crear_001_main_body(),
        "EBA_01.00.001B_cuna_motor_izq": crear_001B_cuna_motor_izq(),
        "EBA_01.00.001C_cuna_motor_der": crear_001C_cuna_motor_der(),
        "EBA_01.00.002_vertical_drive_arm": crear_002_vertical_drive_arm(),
        "EBA_01.00.003_link": biela_L1,
        "EBA_01.00.003_link_forearm": biela_L2,
        "EBA_01.00.004_forward_drive_arm": crear_004_forward_drive_arm(),
        "EBA_01.00.005_horizontal_arm": crear_005_horizontal_arm(),
        "EBA_01.00.006_triangular_link": crear_006_triangular_link(),
        "EBA_01.00.009_servo_plate": crear_009_servo_plate(),
        "EBA_01.00.010_basement": crear_010_basement(),
        "EBA_01.00.011_round_plate": crear_011_round_plate(),
        "EBA_01.00.012_R01_claw_support": crear_012_claw_support(),
        "EBA_01.00.013_R01_right_finger": crear_013_right_finger(),
        "EBA_01.00.014_R01_left_finger": crear_014_left_finger(),
        "EBA_01.00.015_drive_gear": crear_015_drive_gear(),
        "EBA_01.00.016_R01_driven_gear": crear_016_driven_gear(),
        "EBA_01.00.018_maestro_holder": crear_018_maestro_holder(),
        "EBA_01.00.020_wrist_pitch_bracket": crear_020_wrist_pitch_bracket(),
        "EBA_01.00.021_wrist_servo_clamp": crear_021_wrist_servo_clamp(),
        "Pin_Imprimible_12mm_Motor": pin_12_motor_x,
        "Pin_Imprimible_8mm_Articulacion": pin_a1,
        "Pin_Imprimible_8mm_Codo_Largo": pin_e1_codo,
        "Pin_Imprimible_4mm_Dedos": pin_dedo_der,
        "Tubo_Central_O1_Imprimible": tubo_central,
        "00_NEMA17_Planetaria_25mm": actuador_recto_j1,
        "00_MicroServo_SG90": servo_sg90,
    }

    for nombre, solido in piezas.items():
        cq.exporters.export(solido, f"{nombre}.step")

    # Coordenadas globales cinemáticas
    Z_TORRETA = 149.0
    X_O1, Z_O1 = 0.0, Z_TORRETA + 48.0  # (0.0, 197.0 mm)

    X_E1 = X_O1 + L1 * math.cos(th1)
    Z_E1 = Z_O1 + L1 * math.sin(th1)

    X_A1, Z_A1 = X_O1 - R_CRANK, Z_O1
    X_B1, Z_B1 = X_E1 - R_CRANK, Z_E1

    X_O2, Z_O2 = X_O1 + U_REAR_X, Z_O1 + U_REAR_Z
    X_TREAR, Z_TREAR = X_E1 + U_REAR_X, Z_E1 + U_REAR_Z
    X_TTOP, Z_TTOP = X_E1 + U_TOP_X, Z_E1 + U_TOP_Z

    X_W1, Z_W1 = X_E1 + L2, Z_E1
    X_W2, Z_W2 = X_W1 + U_TOP_X, Z_W1 + U_TOP_Z
    X_PITCH, Z_PITCH = X_W1 + L_PITCH, Z_W1

    ensamble = cq.Assembly(name="EEZYbotARM_40cm_NEMA_Planetaria_Final")
    c_azul = cq.Color(0.08, 0.48, 0.88)
    c_gear = cq.Color(0.12, 0.72, 0.85)
    c_acero = cq.Color(0.75, 0.78, 0.82)
    c_servo = cq.Color(0.15, 0.25, 0.65)
    c_tornillo = cq.Color(0.25, 0.27, 0.30)

    # 1. Base fija + Actuador J1 + Engranaje 016 + Pasador Ø12 J1 + Plato 011 + Soporte 018
    ensamble.add(piezas["EBA_01.00.010_basement"], name="010_Basement", color=c_azul)
    ensamble.add(actuador_recto_j1, name="Motor_Planetaria_J1_Base", color=c_gear, loc=cq.Location(cq.Vector(0, 0, 94.0)))
    ensamble.add(piezas["EBA_01.00.016_R01_driven_gear"], name="016_Driven_Gear", color=c_azul, loc=cq.Location(cq.Vector(0, 0, 112.0)))
    ensamble.add(pin_12_motor_x, name="Pin_12mm_J1_Base", color=c_acero, loc=cq.Location(cq.Vector(0, 0, 131.8)))
    ensamble.add(piezas["EBA_01.00.011_round_plate"], name="011_Round_Plate", color=c_azul, loc=cq.Location(cq.Vector(0, 0, 141.0)))
    ensamble.add(
        piezas["EBA_01.00.018_maestro_holder"],
        name="018_Maestro_Holder",
        color=c_azul,
        loc=cq.Location(cq.Vector(-66.0, 0, 22.0)),
    )

    # 2. Torreta Modular (001 Núcleo + 001B Cuna Izq + 001C Cuna Der) + Abrazaderas 009 + 16 Tornillos M4 + Motores J2 y J3
    ensamble.add(piezas["EBA_01.00.001"], name="001_Main_Body_Nucleo_Central", color=c_azul, loc=cq.Location(cq.Vector(0, 0, Z_TORRETA)))
    ensamble.add(piezas["EBA_01.00.001B_cuna_motor_izq"], name="001B_Cuna_Maciza_Izq", color=c_azul, loc=cq.Location(cq.Vector(0, 0, Z_TORRETA)))
    ensamble.add(piezas["EBA_01.00.001C_cuna_motor_der"], name="001C_Cuna_Maciza_Der", color=c_azul, loc=cq.Location(cq.Vector(0, 0, Z_TORRETA)))
    ensamble.add(tubo_central, name="Tubo_Central_O1", color=c_acero, loc=cq.Location(cq.Vector(X_O1, 7.25, Z_O1)))

    # 8 Tornillos horizontales M4 que unen las cunas 001B y 001C al núcleo 001
    idx_u = 1
    for dx in [-29.0, 29.0]:
        for dz in [10.0, 36.0]:
            ensamble.add(
                tornillo_m4_union,
                name=f"Tornillo_M4_Union_Cuna_Izq_{idx_u}",
                color=c_tornillo,
                loc=cq.Location(cq.Vector(dx, -68.0, Z_TORRETA + dz), cq.Vector(1, 0, 0), 90),
            )
            ensamble.add(
                tornillo_m4_union,
                name=f"Tornillo_M4_Union_Cuna_Der_{idx_u}",
                color=c_tornillo,
                loc=cq.Location(cq.Vector(dx, 82.0, Z_TORRETA + dz), cq.Vector(1, 0, 0), -90),
            )
            idx_u += 1

    ensamble.add(
        actuador_j2,
        name="Motor_Planetaria_J2_Izq",
        color=c_gear,
        loc=cq.Location(cq.Vector(X_O1, -56.0, Z_O1), cq.Vector(1, 0, 0), -90),
    )
    Z_CLAMP_BASE = Z_TORRETA + 54.0
    ensamble.add(
        piezas["EBA_01.00.009_servo_plate"],
        name="009_Clamp_Motor_Izq",
        color=c_azul,
        loc=cq.Location(cq.Vector(X_O1, -80.0, Z_CLAMP_BASE)),
    )
    idx_t = 1
    for dx in [-28.0, 28.0]:
        for dy in [-9.0, 9.0]:
            ensamble.add(
                tornillo_m4,
                name=f"Tornillo_M4_Cuna_Izq_{idx_t}",
                color=c_tornillo,
                loc=cq.Location(cq.Vector(X_O1 + dx, -80.0 + dy, Z_CLAMP_BASE + 21.5)),
            )
            idx_t += 1

    ensamble.add(
        actuador_j3,
        name="Motor_Planetaria_J3_Der",
        color=c_gear,
        loc=cq.Location(cq.Vector(X_O1, 70.0, Z_O1), cq.Vector(1, 0, 0), 90),
    )
    ensamble.add(
        piezas["EBA_01.00.009_servo_plate"],
        name="009_Clamp_Motor_Der",
        color=c_azul,
        loc=cq.Location(cq.Vector(X_O1, 94.0, Z_CLAMP_BASE)),
    )
    idx_t = 1
    for dx in [-28.0, 28.0]:
        for dy in [-9.0, 9.0]:
            ensamble.add(
                tornillo_m4,
                name=f"Tornillo_M4_Cuna_Der_{idx_t}",
                color=c_tornillo,
                loc=cq.Location(cq.Vector(X_O1 + dx, 94.0 + dy, Z_CLAMP_BASE + 21.5)),
            )
            idx_t += 1

    # 3. Brazo Principal 004 + Pasador Ø12.0 mm J2
    ensamble.add(
        piezas["EBA_01.00.004_forward_drive_arm"],
        name="004_Forward_Drive_Arm",
        color=c_azul,
        loc=cq.Location(cq.Vector(X_O1, 0, Z_O1), cq.Vector(0, 1, 0), -THETA1_DEG),
    )
    ensamble.add(
        pin_12_motor_x,
        name="Pin_12mm_J2_Hombro",
        color=c_acero,
        loc=cq.Location(cq.Vector(X_O1, -18.20, Z_O1), cq.Vector(0, 1, 0), -THETA1_DEG),
    )

    # 4. Palanca 002 + Pasador Ø12.0 mm J3 + Pin A1
    ensamble.add(
        piezas["EBA_01.00.002_vertical_drive_arm"],
        name="002_Vertical_Drive_Arm",
        color=c_azul,
        loc=cq.Location(cq.Vector(X_O1, 32.20, Z_O1)),
    )
    ensamble.add(
        pin_12_motor_x,
        name="Pin_12mm_J3_Palanca",
        color=c_acero,
        loc=cq.Location(cq.Vector(X_O1, 32.20, Z_O1)),
    )
    ensamble.add(
        pin_a1,
        name="Pin_8mm_A1_Biela",
        color=c_acero,
        loc=cq.Location(cq.Vector(X_A1, 34.0, Z_A1)),
    )

    # 5. Articulación fija O2 de la torre
    ensamble.add(
        pin_o2,
        name="Pin_8mm_O2_Torre",
        color=c_acero,
        loc=cq.Location(cq.Vector(X_O2, 45.0, Z_O2)),
    )

    # 6. Bielas y Paralelogramos (003 #1, 003 #2, 005, 006, 003 #3) + Pines
    ensamble.add(
        biela_L1,
        name="003_Link_1_Motriz",
        color=c_azul,
        loc=cq.Location(cq.Vector(X_A1, 29.0, Z_A1), cq.Vector(0, 1, 0), -THETA1_DEG),
    )
    ensamble.add(
        pin_b1,
        name="Pin_8mm_B1_Antebrazo",
        color=c_acero,
        loc=cq.Location(cq.Vector(X_B1, 23.0, Z_B1)),
    )
    ensamble.add(
        biela_L1,
        name="003_Link_2_Paralelogramo_Base",
        color=c_azul,
        loc=cq.Location(cq.Vector(X_O2, 40.5, Z_O2), cq.Vector(0, 1, 0), -THETA1_DEG),
    )
    ensamble.add(
        piezas["EBA_01.00.005_horizontal_arm"],
        name="005_Horizontal_Arm",
        color=c_azul,
        loc=cq.Location(cq.Vector(X_E1, 0, Z_E1)),
    )
    ensamble.add(
        piezas["EBA_01.00.006_triangular_link"],
        name="006_Triangular_Link",
        color=c_azul,
        loc=cq.Location(cq.Vector(X_E1, 0, Z_E1)),
    )
    ensamble.add(
        pin_e1_codo,
        name="Pin_8mm_E1_Codo",
        color=c_acero,
        loc=cq.Location(cq.Vector(X_E1, -4.0, Z_E1)),
    )
    ensamble.add(
        pin_t_rear,
        name="Pin_8mm_T_Rear",
        color=c_acero,
        loc=cq.Location(cq.Vector(X_TREAR, 35.5, Z_TREAR)),
    )
    ensamble.add(
        biela_L2,
        name="003_Link_3_Paralelogramo_Superior",
        color=c_azul,
        loc=cq.Location(cq.Vector(X_TTOP, -3.00, Z_TTOP)),
    )
    ensamble.add(
        pin_t_top,
        name="Pin_8mm_T_Top",
        color=c_acero,
        loc=cq.Location(cq.Vector(X_TTOP, 1.0, Z_TTOP)),
    )

    # 7. Nuevo Grado de Libertad: Soporte de Muñeca Pitch (020) + Cuna Anti-Rotación + Tapa Trasera (021) + Servo SG90
    ensamble.add(
        piezas["EBA_01.00.020_wrist_pitch_bracket"],
        name="020_Wrist_Pitch_Bracket",
        color=c_azul,
        loc=cq.Location(cq.Vector(X_W1, 0, Z_W1)),
    )
    ensamble.add(
        piezas["EBA_01.00.021_wrist_servo_clamp"],
        name="021_Wrist_Servo_Clamp_Antirotacion",
        color=c_azul,
        loc=cq.Location(cq.Vector(X_PITCH + 5.5, 0, Z_PITCH)),
    )
    ensamble.add(
        pin_w1_muneca,
        name="Pin_8mm_W1_Muneca",
        color=c_acero,
        loc=cq.Location(cq.Vector(X_W1, -4.0, Z_W1)),
    )
    ensamble.add(
        pin_w2_muneca,
        name="Pin_8mm_W2_Muneca",
        color=c_acero,
        loc=cq.Location(cq.Vector(X_W2, -4.0, Z_W2)),
    )
    ensamble.add(
        servo_sg90,
        name="MicroServo_SG90_Pitch_Muneca",
        color=c_servo,
        loc=cq.Location(cq.Vector(X_PITCH + 5.5, -20.5, Z_PITCH), cq.Vector(1, 0, 0), 90),
    )
    ensamble.add(
        pin_pitch_der,
        name="Pin_8mm_Eje_Pitch_Garra",
        color=c_acero,
        loc=cq.Location(cq.Vector(X_PITCH, 11.25, Z_PITCH)),
    )

    # 8. Subensamble de Garra Articulada (rota libremente arriba/abajo alrededor de X_PITCH, Z_PITCH)
    sub_garra = cq.Assembly(name="Subensamble_Garra_Pitch")
    sub_garra.add(
        piezas["EBA_01.00.012_R01_claw_support"],
        name="012_Claw_Support",
        color=c_azul,
        loc=cq.Location(cq.Vector(0, 0, 0)),
    )
    sub_garra.add(
        servo_sg90,
        name="MicroServo_SG90_Garra",
        color=c_servo,
        loc=cq.Location(cq.Vector(27.5, -4.0, -10.0)),
    )
    sub_garra.add(
        piezas["EBA_01.00.015_drive_gear"],
        name="015_Drive_Gear",
        color=c_azul,
        loc=cq.Location(cq.Vector(22.0, -4.0, -15.25)),
    )
    sub_garra.add(
        piezas["EBA_01.00.013_R01_right_finger"],
        name="013_Right_Finger",
        color=c_azul,
        loc=cq.Location(cq.Vector(42.0, -13.0, -15.25)),
    )
    sub_garra.add(
        pin_dedo_der,
        name="Pin_4mm_Dedo_Derecho",
        color=c_acero,
        loc=cq.Location(cq.Vector(42.0, -13.0, -15.25)),
    )
    sub_garra.add(
        piezas["EBA_01.00.014_R01_left_finger"],
        name="014_Left_Finger",
        color=c_azul,
        loc=cq.Location(cq.Vector(42.0, 5.0, -15.25)),
    )
    sub_garra.add(
        pin_dedo_izq,
        name="Pin_4mm_Dedo_Izquierdo",
        color=c_acero,
        loc=cq.Location(cq.Vector(42.0, 5.0, -15.25)),
    )

    ensamble.add(
        sub_garra,
        name="Garra_Articulada_Pitch",
        loc=cq.Location(cq.Vector(X_PITCH, 0, Z_PITCH), cq.Vector(0, 1, 0), PITCH_GARRA_DEG),
    )

    ensamble.save("Ensamble_EBA_40cm_NEMA_Planetaria_Final.step")
    print("¡Diseño actualizado con cuna anti-rotación y tapa trasera para el servo del último grado de libertad!")
