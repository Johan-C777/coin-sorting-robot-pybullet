import os
import math
import cadquery as cq

# ==============================================================================
# PARÁMETROS GEOMÉTRICOS EXACTOS DE ACOPLAMIENTO CON EL BRAZO ROBÓTICO
# (Idénticos a generar_brazo_step.py para encaje 100% directo sin modificar el robot)
# ==============================================================================
NEMA_W = 42.3                       # Ancho del motor NEMA 17 (entra en la parte angosta de la cuna)
NEMA_L = 38.0                       # Largo estándar del cuerpo NEMA 17
NEMA_BOLT = 31.0                    # Distancia entre centros de tornillos M3 del NEMA 17
NEMA_BOSS_R = 11.25                 # Radio para el resalte circular frontal del NEMA 17 (Ø22 mm + holgura)
NEMA_SHAFT_R = 2.60                 # Radio para eje de 5.0 mm (Ø5.20 mm impreso para encaje firme en D)
NEMA_D_FLAT_X = 2.10                # Posición de la cara plana del eje tipo D de 5 mm (4.5 mm espesor + holgura)

GEAR_W = 48.0                       # Ancho exterior de la caja reductora (entra en el bolsillo ancho de 48.5 mm)
GEAR_BOLT = 35.0                    # Entrecentros de los 4 tornillos frontales M4 (acoplan con 001 y 010)
L_CAJA_TOTAL = 52.0                 # Largo total de la caja en el bolsillo ancho (Z = -52.0 a 0.0 mm)

# Dimensiones exactas del eje de salida hacia los eslabones (002, 004, 016)
SHAFT_TOTAL_L = 51.3                # Longitud total del eje desde la cara frontal Z=0 (12.0 + 39.3 mm)
SHAFT_ROT_D = 25.4                  # Ø25.4 mm impreso (entra suave en el hueco SHAFT_FIT_R de Ø26.0 mm del brazo)
Z_PIN_MOTOR = 37.8                  # Distancia exacta desde la cara frontal (Z=0) al centro del pasador de Ø12 mm
MOTOR_PIN_HOLE_R = 6.15             # Radio 6.15 mm (Ø12.30 mm para el pasador impreso de Ø11.75 mm)

# ==============================================================================
# PARÁMETROS CINEMÁTICOS DEL TREN PLANETARIO DE DOBLE ETAPA (RELACIÓN 16 : 1)
# ==============================================================================
# Módulo m = 1.25 mm (Dientes robustos para impresión FDM con boquilla de 0.4 mm)
# - Sol (Z_S) = 10 dientes   -> Diámetro primitivo = 12.50 mm
# - Planeta (Z_P) = 10 dientes -> Diámetro primitivo = 12.50 mm
# - Corona (Z_R) = 30 dientes  -> Diámetro primitivo = 37.50 mm
# Relación por etapa: i_etapa = 1 + (Z_R / Z_S) = 1 + (30 / 10) = 4.0 : 1
# Relación total (2 etapas en serie): i_total = 4.0 * 4.0 = 16.0 : 1
# ==============================================================================
MODULO = 1.25
Z_SOL = 10
Z_PLANETA = 10
Z_CORONA = 30
R_ORBITA = MODULO * (Z_SOL + Z_PLANETA) / 2.0  # 12.50 mm (radio de órbita de los 3 planetas)

# Radios de tallado para engranajes exteriores (con holgura radial FDM)
R_SOL_RAIZ = (MODULO * Z_SOL / 2.0) - (1.20 * MODULO) - 0.10       # 4.65 mm
R_SOL_PUNTA = (MODULO * Z_SOL / 2.0) + (0.95 * MODULO) - 0.10      # 7.34 mm

R_PLAN_RAIZ = (MODULO * Z_PLANETA / 2.0) - (1.20 * MODULO) - 0.10  # 4.65 mm
R_PLAN_PUNTA = (MODULO * Z_PLANETA / 2.0) + (0.95 * MODULO) - 0.10 # 7.34 mm

# Radios de tallado para la corona interior (30 dientes internos)
R_CORONA_INTERIOR_PUNTA = (MODULO * Z_CORONA / 2.0) - (0.90 * MODULO) + 0.15  # 17.78 mm (cresta interna)
R_CORONA_INTERIOR_FONDO = (MODULO * Z_CORONA / 2.0) + (1.20 * MODULO) + 0.20  # 20.45 mm (valle interno)

# Dimensiones de los pines de los planetas
PIN_PLANETA_NOM_D = 5.0
PIN_PLANETA_PRINT_R = (PIN_PLANETA_NOM_D - 0.25) / 2.0  # Ø4.75 mm impreso para giro libre
PIN_PLANETA_HOLE_R = (PIN_PLANETA_NOM_D + 0.25) / 2.0   # Ø5.25 mm en el interior del planeta
PIN_CARRIER_FIT_R = (PIN_PLANETA_NOM_D + 0.05) / 2.0    # Ø5.05 mm encaje firme en los porta-planetas

M3_CLEAR_R = 1.70                   # Ø3.40 mm paso libre para tornillos M3
M3_TAP_R = 1.45                     # Ø2.90 mm para roscar M3 directo
M4_TAP_R = 1.85                     # Ø3.70 mm para roscar M4 en los 4 agujeros frontales de 35x35 mm


def perfil_engranaje_recto(r_raiz, r_punta, num_dientes, angulo_fase_deg=0.0):
    """Genera un polígono cerrado de perfil trapezoidal involuto simplificado para impresión 3D."""
    pts = []
    paso = (2.0 * math.pi) / num_dientes
    base = math.radians(angulo_fase_deg)
    for i in range(num_dientes):
        th = base + i * paso
        pts.extend([
            (r_raiz * math.cos(th + paso * 0.12), r_raiz * math.sin(th + paso * 0.12)),
            (r_punta * math.cos(th + paso * 0.30), r_punta * math.sin(th + paso * 0.30)),
            (r_punta * math.cos(th + paso * 0.52), r_punta * math.sin(th + paso * 0.52)),
            (r_raiz * math.cos(th + paso * 0.70), r_raiz * math.sin(th + paso * 0.70)),
            (r_raiz * math.cos(th + paso * 0.92), r_raiz * math.sin(th + paso * 0.92)),
        ])
    return pts


def crear_hueco_eje_d(altura, r_eje=NEMA_SHAFT_R, x_flat=NEMA_D_FLAT_X):
    """Crea el sólido del eje tipo D del motor NEMA 17 para restarlo del engranaje Sol."""
    cil = cq.Workplane("XY").cylinder(altura, r_eje, centered=(True, True, False))
    corte_plano = (
        cq.Workplane("XY")
        .center(x_flat + 5.0, 0)
        .box(10.0, 12.0, altura + 2.0, centered=(True, True, False))
    )
    return cil.cut(corte_plano)


# ==============================================================================
# 1. BRIDA TRASERA DE ADAPTACIÓN AL MOTOR NEMA 17 (Z = -52.0 a -41.0 mm)
# ==============================================================================
def crear_01_brida_motor_nema17():
    """
    Placa trasera que se atornilla al motor NEMA 17 (patrón 31x31 mm M3)
    y centra/cierra la caja reductora por detrás (patrón exterior 39x39 mm M3).
    """
    cuerpo = (
        cq.Workplane("XY")
        .workplane(offset=-52.0)
        .box(GEAR_W, GEAR_W, 8.0, centered=(True, True, False))
        .edges("|Z")
        .fillet(3.0)
    )
    # Espiga cilíndrica de centrado que entra en la carcasa central (Z = -44.0 a -41.0 mm)
    espiga = (
        cq.Workplane("XY")
        .workplane(offset=-44.0)
        .cylinder(3.0, 20.8, centered=(True, True, False))
    )
    # Cajera posterior para el resalte circular de Ø22 mm del NEMA 17
    rebaje_boss_nema = (
        cq.Workplane("XY")
        .workplane(offset=-52.5)
        .cylinder(3.0, NEMA_BOSS_R, centered=(True, True, False))
    )
    # Hueco central holgado para el collarín reforzado del Engranaje Sol 1 (Ø16.6 mm)
    hueco_central = (
        cq.Workplane("XY")
        .workplane(offset=-53.0)
        .cylinder(15.0, 8.3, centered=(True, True, False))
    )
    # 4 Agujeros pasantes M3 para atornillar al frente del motor NEMA 17 (31.0 x 31.0 mm)
    tornillos_nema = (
        cq.Workplane("XY")
        .workplane(offset=-53.0)
        .rect(NEMA_BOLT, NEMA_BOLT, forConstruction=True)
        .vertices()
        .circle(M3_CLEAR_R)
        .extrude(15.0)
    )
    # Cajeras avellanadas internas para que las cabezas M3 del motor queden ocultas dentro de la brida
    cajeras_cabeza_nema = (
        cq.Workplane("XY")
        .workplane(offset=-47.5)
        .rect(NEMA_BOLT, NEMA_BOLT, forConstruction=True)
        .vertices()
        .circle(3.2)
        .extrude(8.0)
    )
    # 4 Agujeros en las esquinas exteriores (39.0 x 39.0 mm) para cerrar la carcasa reductora con tornillos M3
    tornillos_carcasa = (
        cq.Workplane("XY")
        .workplane(offset=-53.0)
        .rect(39.0, 39.0, forConstruction=True)
        .vertices()
        .circle(M3_CLEAR_R)
        .extrude(15.0)
    )
    # Ventana lateral para apretar el prisionero M3 del Engranaje Sol
    ventana_prisionero = (
        cq.Workplane("XZ")
        .workplane(offset=0.0)
        .center(0, -47.5)
        .cylinder(30.0, 2.5)
    )

    return (
        cuerpo.union(espiga)
        .cut(rebaje_boss_nema)
        .cut(hueco_central)
        .cut(tornillos_nema)
        .cut(cajeras_cabeza_nema)
        .cut(tornillos_carcasa)
        .cut(ventana_prisionero)
    )


# ==============================================================================
# 2. CARCASA CENTRAL CON CORONA DENTADA INTERNA (Z = -44.0 a -10.0 mm)
# ==============================================================================
def crear_02_carcasa_corona_central():
    """
    Cuerpo central cuadrado de 48x48 mm con corona dentada interna de 30 dientes
    que sirve a ambas etapas planetarias, y rebajes de centrado trasero y delantero.
    """
    exterior = (
        cq.Workplane("XY")
        .workplane(offset=-44.0)
        .box(GEAR_W, GEAR_W, 34.0, centered=(True, True, False))
        .edges("|Z")
        .fillet(3.0)
    )
    # Vaciado de la corona dentada interna (Z = -41.5 a -15.5 mm)
    pts_corona = perfil_engranaje_recto(
        r_raiz=R_CORONA_INTERIOR_PUNTA,
        r_punta=R_CORONA_INTERIOR_FONDO,
        num_dientes=Z_CORONA,
    )
    corona_hueco = (
        cq.Workplane("XY")
        .workplane(offset=-41.5)
        .polyline(pts_corona)
        .close()
        .extrude(26.0)
    )
    # Cámara lisa superior para el Porta-Planetas de salida (Z = -16.2 a -10.0 mm, r = 17.6 mm)
    camara_salida = (
        cq.Workplane("XY")
        .workplane(offset=-16.2)
        .cylinder(6.5, 17.6, centered=(True, True, False))
    )
    # Rebaje posterior de centrado para la espiga de la brida 01 (Z = -44.0 a -41.0 mm, Ø42.0 mm)
    rebaje_trasero = (
        cq.Workplane("XY")
        .workplane(offset=-44.5)
        .cylinder(3.6, 21.0, centered=(True, True, False))
    )
    # Rebaje frontal de centrado para el anillo guía de la tapa 03 (Z = -12.0 a -10.0 mm, Ø42.0 mm)
    rebaje_frontal = (
        cq.Workplane("XY")
        .workplane(offset=-12.0)
        .cylinder(2.5, 21.0, centered=(True, True, False))
    )
    # 4 Perforaciones en las esquinas (39.0 x 39.0 mm) para los tornillos largos M3 que unen toda la caja
    tornillos_carcasa = (
        cq.Workplane("XY")
        .workplane(offset=-45.0)
        .rect(39.0, 39.0, forConstruction=True)
        .vertices()
        .circle(M3_CLEAR_R)
        .extrude(36.0)
    )

    return (
        exterior.cut(corona_hueco)
        .cut(camara_salida)
        .cut(rebaje_trasero)
        .cut(rebaje_frontal)
        .cut(tornillos_carcasa)
    )


# ==============================================================================
# 3. TAPA FRONTAL DE LA CAJA REDUCTORA (Z = -10.0 a 0.0 mm)
# ==============================================================================
def crear_03_tapa_frontal_salida():
    """
    Tapa frontal que se apoya exactamente en Z = 0.0 mm contra las paredes del brazo robótico (001 y 010).
    Incluye anillo centrador externo (sin interferir con el porta-planetas) y roscas M4 a 35x35 mm.
    """
    cuerpo = (
        cq.Workplane("XY")
        .workplane(offset=-10.0)
        .box(GEAR_W, GEAR_W, 10.0, centered=(True, True, False))
        .edges("|Z")
        .fillet(3.0)
    )
    # Anillo centrador posterior que encaja en el rebaje frontal de la carcasa (r_in=17.6, r_out=20.8)
    anillo_espiga = (
        cq.Workplane("XY")
        .workplane(offset=-12.0)
        .cylinder(2.0, 20.8, centered=(True, True, False))
        .cut(cq.Workplane("XY").workplane(offset=-12.5).cylinder(3.0, 17.6, centered=(True, True, False)))
    )
    # Agujero central de cojinete para el eje de salida de Ø25.4 mm (Ø26.0 mm con holgura de giro)
    hueco_eje_salida = (
        cq.Workplane("XY")
        .workplane(offset=-13.0)
        .cylinder(15.0, (SHAFT_ROT_D / 2.0) + 0.30, centered=(True, True, False))
    )
    # 4 Roscas M4 en patrón de 35.0 x 35.0 mm (GEAR_BOLT) para atornillar la caja al brazo robótico (001 y 010)
    roscas_montaje_robot = (
        cq.Workplane("XY")
        .workplane(offset=-9.5)
        .rect(GEAR_BOLT, GEAR_BOLT, forConstruction=True)
        .vertices()
        .circle(M4_TAP_R)
        .extrude(10.5)
    )
    # 4 Roscas M3 en las esquinas exteriores (39.0 x 39.0 mm) para cerrar el sándwich de la caja reductora
    roscas_cierre_caja = (
        cq.Workplane("XY")
        .workplane(offset=-10.5)
        .rect(39.0, 39.0, forConstruction=True)
        .vertices()
        .circle(M3_TAP_R)
        .extrude(9.5)
    )

    return (
        cuerpo.union(anillo_espiga)
        .cut(hueco_eje_salida)
        .cut(roscas_montaje_robot)
        .cut(roscas_cierre_caja)
    )


# ==============================================================================
# 4. ENGRANAJE SOL ETAPA 1 CON ADAPTADOR REFORZADO PARA EJE NEMA 17
# ==============================================================================
def crear_04_engranaje_sol_etapa1_nema17():
    """
    Engranaje central (Sol 1, 10 dientes) con collarín trasero macizo de Ø15 mm
    para multiplicar el área de contacto con el eje de 5 mm del motor NEMA 17.
    El hueco en 'D' atraviesa toda la pieza para admitir ejes de 20 a 24 mm sin topar.
    """
    # Collarín reforzado trasero (Z = -50.5 a -40.5 mm, largo 10.0 mm, Ø15.0 mm)
    collarin = (
        cq.Workplane("XY")
        .workplane(offset=-50.5)
        .cylinder(10.0, 7.5, centered=(True, True, False))
        .edges("<Z")
        .chamfer(0.8)
    )
    # Cuerpo dentado del Sol 1 (Z = -40.5 a -31.0 mm, largo 9.5 mm)
    pts_sol = perfil_engranaje_recto(R_SOL_RAIZ, R_SOL_PUNTA, Z_SOL)
    sol_dentado = (
        cq.Workplane("XY")
        .workplane(offset=-40.5)
        .polyline(pts_sol)
        .close()
        .extrude(9.5)
    )
    # Hueco pasante en 'D' (Z = -51.0 a -30.5 mm)
    hueco_d = (
        crear_hueco_eje_d(altura=21.0, r_eje=NEMA_SHAFT_R, x_flat=NEMA_D_FLAT_X)
        .translate((0, 0, -51.0))
    )
    # Orificio transversal para tornillo prisionero M3 contra la cara plana del eje D
    agujero_prisionero = (
        cq.Workplane("YZ")
        .workplane(offset=0.0)
        .center(0, -46.0)
        .circle(M3_TAP_R)
        .extrude(12.0)
    )

    return collarin.union(sol_dentado).cut(hueco_d).cut(agujero_prisionero)


# ==============================================================================
# 5. ENGRANAJES PLANETA (x6 UNIDADES IGUALES: 3 PARA ETAPA 1 + 3 PARA ETAPA 2)
# ==============================================================================
def crear_05_engranaje_planeta():
    """
    Engranaje planeta de 10 dientes (espesor 9.0 mm) con perforación central de Ø5.25 mm.
    """
    pts_planeta = perfil_engranaje_recto(R_PLAN_RAIZ, R_PLAN_PUNTA, Z_PLANETA, angulo_fase_deg=18.0)
    cuerpo = (
        cq.Workplane("XY")
        .polyline(pts_planeta)
        .close()
        .extrude(9.0)
    )
    agujero_pin = cq.Workplane("XY").cylinder(12.0, PIN_PLANETA_HOLE_R, centered=(True, True, False))
    return cuerpo.cut(agujero_pin)


# ==============================================================================
# 6. PORTA-PLANETAS ETAPA 1 INTEGRADO CON ENGRANAJE SOL ETAPA 2
# ==============================================================================
def crear_06_porta_planetas_etapa1_sol2():
    """
    Recibe el movimiento de los 3 planetas de la Etapa 1 (Z = -31.0 a -26.0 mm)
    y transmite la rotación al Sol de la Etapa 2 (10 dientes, Z = -26.0 a -16.5 mm).
    """
    plato = (
        cq.Workplane("XY")
        .workplane(offset=-31.0)
        .cylinder(5.0, 17.0, centered=(True, True, False))
        .edges()
        .chamfer(0.4)
    )
    pts_sol2 = perfil_engranaje_recto(R_SOL_RAIZ, R_SOL_PUNTA, Z_SOL)
    sol_etapa2 = (
        cq.Workplane("XY")
        .workplane(offset=-26.0)
        .polyline(pts_sol2)
        .close()
        .extrude(9.5)
    )
    pts_pines = [
        (R_ORBITA * math.cos(math.radians(ang)), R_ORBITA * math.sin(math.radians(ang)))
        for ang in [0, 120, 240]
    ]
    agujeros_pines = (
        cq.Workplane("XY")
        .workplane(offset=-31.5)
        .pushPoints(pts_pines)
        .circle(PIN_CARRIER_FIT_R)
        .extrude(6.0)
    )
    # Agujero central pasante de Ø6.0 mm (da paso libre si el eje del NEMA 17 supera los 21 mm)
    hueco_centro = (
        cq.Workplane("XY")
        .workplane(offset=-31.5)
        .cylinder(16.0, 3.0, centered=(True, True, False))
    )

    return plato.union(sol_etapa2).cut(agujeros_pines).cut(hueco_centro)


# ==============================================================================
# 7. PORTA-PLANETAS DE SALIDA (ETAPA 2) CON EJE DE Ø25.4 mm Y HUECO DE Ø12 mm
# ==============================================================================
def crear_07_porta_planetas_salida_eje():
    """
    Pieza final de salida de alta resistencia:
    - Plato porta-planetas interno (Z = -16.0 a -10.5 mm, Ø34.0 mm) con los 3 agujeros para Etapa 2.
    - Eje cilíndrico macizo de Ø25.4 mm que sale desde Z = -10.5 mm hasta Z = +51.3 mm (idéntico al robot).
    - Perforación transversal de Ø12.30 mm centrada exactamente en Z = +37.8 mm (Z_PIN_MOTOR).
    """
    plato_interno = (
        cq.Workplane("XY")
        .workplane(offset=-16.0)
        .cylinder(5.5, 17.0, centered=(True, True, False))
        .edges("<Z")
        .chamfer(0.4)
    )
    eje_salida = (
        cq.Workplane("XY")
        .workplane(offset=-10.5)
        .cylinder(10.5 + SHAFT_TOTAL_L, SHAFT_ROT_D / 2.0, centered=(True, True, False))
        .faces(">Z")
        .edges()
        .chamfer(1.0)
    )
    pts_pines = [
        (R_ORBITA * math.cos(math.radians(ang)), R_ORBITA * math.sin(math.radians(ang)))
        for ang in [60, 180, 300]
    ]
    agujeros_pines = (
        cq.Workplane("XY")
        .workplane(offset=-16.5)
        .pushPoints(pts_pines)
        .circle(PIN_CARRIER_FIT_R)
        .extrude(6.0)
    )
    corte_pin_12 = (
        cq.Workplane("YZ")
        .center(0, Z_PIN_MOTOR)
        .cylinder(40.0, MOTOR_PIN_HOLE_R)
    )

    return plato_interno.union(eje_salida).cut(agujeros_pines).cut(corte_pin_12)


# ==============================================================================
# 8. PINES DE PLANETAS Y ARANDELA DE EMPUJE IMPRIMIBLES
# ==============================================================================
def crear_08_pin_planeta():
    """Pin cilíndrico de Ø4.75 x 14.0 mm para los engranajes planeta (imprimir 6 unidades)."""
    return (
        cq.Workplane("XY")
        .cylinder(14.0, PIN_PLANETA_PRINT_R, centered=(True, True, False))
        .edges()
        .chamfer(0.4)
    )


def crear_09_arandela_empuje():
    """Arandela axial de 0.5 mm (Ø33.6 ext x Ø26.2 int) entre Porta-Planetas de salida y Tapa Frontal."""
    ext = cq.Workplane("XY").cylinder(0.5, 16.8, centered=(True, True, False))
    hueco = cq.Workplane("XY").cylinder(2.0, 13.1, centered=(True, True, False))
    return ext.cut(hueco)


# ==============================================================================
# MODELOS DE REFERENCIA PARA EL ENSAMBLE VISUAL (NO SON IMPRIMIBLES)
# ==============================================================================
def crear_ref_motor_nema17():
    """Modelo visual de referencia del motor NEMA 17 con eje tipo D de 22 mm."""
    cuerpo = (
        cq.Workplane("XY")
        .workplane(offset=-(L_CAJA_TOTAL + NEMA_L))
        .box(NEMA_W, NEMA_W, NEMA_L, centered=(True, True, False))
        .edges("|Z")
        .chamfer(3.0)
    )
    boss = (
        cq.Workplane("XY")
        .workplane(offset=-L_CAJA_TOTAL)
        .cylinder(2.0, 11.0, centered=(True, True, False))
    )
    eje = (
        crear_hueco_eje_d(altura=22.0, r_eje=2.5, x_flat=2.0)
        .translate((0, 0, -L_CAJA_TOTAL))
    )
    return cuerpo.union(boss).union(eje)


def crear_ref_pasador_12mm():
    """Pasador de Ø11.75 x 46.0 mm que atraviesa el eje de salida en Z = +37.8 mm."""
    return cq.Workplane("YZ").center(0, Z_PIN_MOTOR).cylinder(46.0, 11.75 / 2.0).edges().chamfer(0.5)


def crear_ref_tornillo_m3(largo=45.0):
    """Tornillo M3 largo de cierre para las 4 esquinas de la caja reductora."""
    cabeza = cq.Workplane("XY").cylinder(3.0, 2.75, centered=(True, True, False))
    vastago = cq.Workplane("XY").cylinder(largo, 1.5, centered=(True, True, False))
    return cabeza.union(vastago)


# ==============================================================================
# EXPORTACIÓN DE IMPRIMIBLES (CARPETA PROPIA) Y ENSAMBLES COMPLETOS
# ==============================================================================
if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    imprimibles_dir = os.path.join(base_dir, "Imprimibles")
    os.makedirs(imprimibles_dir, exist_ok=True)

    p01_brida = crear_01_brida_motor_nema17()
    p02_corona = crear_02_carcasa_corona_central()
    p03_tapa = crear_03_tapa_frontal_salida()
    p04_sol1 = crear_04_engranaje_sol_etapa1_nema17()
    p05_planeta = crear_05_engranaje_planeta()
    p06_carrier1_sol2 = crear_06_porta_planetas_etapa1_sol2()
    p07_salida = crear_07_porta_planetas_salida_eje()
    p08_pin = crear_08_pin_planeta()
    p09_arandela = crear_09_arandela_empuje()

    piezas_imprimibles = {
        "01_Brida_Motor_NEMA17": p01_brida,
        "02_Carcasa_Corona_30T": p02_corona,
        "03_Tapa_Frontal_Montaje_Robot": p03_tapa,
        "04_Engranaje_Sol_Etapa1_EjeD_5mm": p04_sol1,
        "05_Engranaje_Planeta_10T_x6": p05_planeta,
        "06_PortaPlanetas_Etapa1_con_Sol2": p06_carrier1_sol2,
        "07_PortaPlanetas_Salida_Eje_25mm": p07_salida,
        "08_Pin_Planeta_5mm_x6": p08_pin,
        "09_Arandela_Empuje": p09_arandela,
    }

    for nombre, solido in piezas_imprimibles.items():
        ruta_step = os.path.join(imprimibles_dir, f"{nombre}.step")
        ruta_stl = os.path.join(imprimibles_dir, f"{nombre}.stl")
        cq.exporters.export(solido, ruta_step)
        cq.exporters.export(solido, ruta_stl)
        print(f"Exportado en Imprimibles/: {nombre} (.step y .stl)")

    # --------------------------------------------------------------------------
    # ENSAMBLE 1: SOLO CAJA REDUCTORA PLANETARIA 16:1 COMPLETA
    # --------------------------------------------------------------------------
    ensamble_caja = cq.Assembly(name="Caja_Reductora_Planetaria_16a1")

    c_carcasa = cq.Color(0.12, 0.72, 0.85)
    c_brida = cq.Color(0.92, 0.94, 0.96)
    c_sol = cq.Color(0.95, 0.65, 0.15)
    c_planeta = cq.Color(0.20, 0.80, 0.45)
    c_salida = cq.Color(0.75, 0.78, 0.82)
    c_arandela = cq.Color(0.95, 0.85, 0.25)
    c_motor = cq.Color(0.18, 0.20, 0.22)
    c_tornillo = cq.Color(0.30, 0.32, 0.35)

    ensamble_caja.add(p01_brida, name="01_Brida_Motor_NEMA17", color=c_brida)
    ensamble_caja.add(p02_corona, name="02_Carcasa_Corona_30T", color=c_carcasa)
    ensamble_caja.add(p03_tapa, name="03_Tapa_Frontal_Montaje", color=c_carcasa)
    ensamble_caja.add(p04_sol1, name="04_Sol_Etapa1_Entrada", color=c_sol)
    ensamble_caja.add(p06_carrier1_sol2, name="06_PortaPlanetas1_Sol2", color=c_sol)
    ensamble_caja.add(p07_salida, name="07_PortaPlanetas2_Eje_Salida", color=c_salida)
    ensamble_caja.add(
        p09_arandela,
        name="09_Arandela_Empuje",
        color=c_arandela,
        loc=cq.Location(cq.Vector(0, 0, -10.5)),
    )

    # 3 Planetas + 3 Pines de Etapa 1 (Planetas Z = -40.5 a -31.5; Pines Z = -40.3 a -26.3)
    for idx, ang in enumerate([0, 120, 240], start=1):
        px = R_ORBITA * math.cos(math.radians(ang))
        py = R_ORBITA * math.sin(math.radians(ang))
        ensamble_caja.add(
            p05_planeta,
            name=f"05_Planeta_Etapa1_{idx}",
            color=c_planeta,
            loc=cq.Location(cq.Vector(px, py, -40.5)),
        )
        ensamble_caja.add(
            p08_pin,
            name=f"08_Pin_Etapa1_{idx}",
            color=c_salida,
            loc=cq.Location(cq.Vector(px, py, -40.3)),
        )

    # 3 Planetas + 3 Pines de Etapa 2 (Planetas Z = -25.5 a -16.5; Pines Z = -25.2 a -11.2)
    for idx, ang in enumerate([60, 180, 300], start=1):
        px = R_ORBITA * math.cos(math.radians(ang))
        py = R_ORBITA * math.sin(math.radians(ang))
        ensamble_caja.add(
            p05_planeta,
            name=f"05_Planeta_Etapa2_{idx}",
            color=c_planeta,
            loc=cq.Location(cq.Vector(px, py, -25.5)),
        )
        ensamble_caja.add(
            p08_pin,
            name=f"08_Pin_Etapa2_{idx}",
            color=c_salida,
            loc=cq.Location(cq.Vector(px, py, -25.2)),
        )

    ruta_ensamble_caja = os.path.join(base_dir, "00_Ensamble_Caja_Reductora_16a1.step")
    ensamble_caja.save(ruta_ensamble_caja)
    print(f"Ensamble caja guardado en: {ruta_ensamble_caja}")

    # --------------------------------------------------------------------------
    # ENSAMBLE 2: CAJA REDUCTORA + MOTOR NEMA 17 + TORNILLERÍA + PASADOR Ø12 mm
    # --------------------------------------------------------------------------
    ensamble_completo = cq.Assembly(name="Actuador_Completo_NEMA17_Caja_16a1")
    ensamble_completo.add(ensamble_caja, name="Caja_Reductora_16a1")
    ensamble_completo.add(crear_ref_motor_nema17(), name="Motor_NEMA17_Ref", color=c_motor)
    ensamble_completo.add(crear_ref_pasador_12mm(), name="Pasador_Salida_12mm_Ref", color=c_salida)

    tornillo_m3_cierre = crear_ref_tornillo_m3(46.0)
    for idx, (cx, cy) in enumerate([(-19.5, -19.5), (19.5, -19.5), (19.5, 19.5), (-19.5, 19.5)], start=1):
        ensamble_completo.add(
            tornillo_m3_cierre,
            name=f"Tornillo_M3_Cierre_{idx}",
            color=c_tornillo,
            loc=cq.Location(cq.Vector(cx, cy, -52.0)),
        )

    tornillo_m3_nema = crear_ref_tornillo_m3(10.0)
    for idx, (nx, ny) in enumerate([(-15.5, -15.5), (15.5, -15.5), (15.5, 15.5), (-15.5, 15.5)], start=1):
        ensamble_completo.add(
            tornillo_m3_nema,
            name=f"Tornillo_M3_NEMA_{idx}",
            color=c_tornillo,
            loc=cq.Location(cq.Vector(nx, ny, -47.5), cq.Vector(1, 0, 0), 180),
        )

    ruta_ensamble_completo = os.path.join(base_dir, "00_Ensamble_Caja_con_Motor_NEMA17.step")
    ensamble_completo.save(ruta_ensamble_completo)
    print(f"Ensamble con motor guardado en: {ruta_ensamble_completo}")
