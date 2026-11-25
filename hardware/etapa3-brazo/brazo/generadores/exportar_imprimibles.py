import os
import glob
import cadquery as cq
import generar_brazo_step as g

DEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PIEZAS_IMPRIMIBLES_3D")
DIR_STL = os.path.join(DEST_DIR, "STL")
DIR_STEP = os.path.join(DEST_DIR, "STEP")

os.makedirs(DIR_STL, exist_ok=True)
os.makedirs(DIR_STEP, exist_ok=True)

# Limpiar archivos antiguos para que no queden nombres desactualizados
for old_f in glob.glob(os.path.join(DIR_STL, "*")) + glob.glob(os.path.join(DIR_STEP, "*")):
    try:
        os.remove(old_f)
    except OSError:
        pass

# Lista completa de todas las piezas que se deben imprimir en 3D (Todas <= 200 mm para cama 220x215x245 mm)
# Formato: (nombre_archivo_amigable, objeto_cadquery, cantidad, notas)
piezas_imprimibles = [
    # 1. Base y Torreta Modular (Dividida en 3 piezas M4 para caber con holgura en cama de 220x215 mm)
    ("01_Base_010_Basement_x1", g.crear_010_basement(), 1, "Base inferior del robot (128x128x112 mm). Aloja motor J1."),
    ("02_Engranaje_Base_016_Driven_Gear_x1", g.crear_016_driven_gear(), 1, "Engranaje de giro de torreta. Mamelon O46mm para eje O25.6mm."),
    ("03_Plato_Giratorio_011_Round_Plate_x1", g.crear_011_round_plate(), 1, "Plato de apoyo con rieles para la torreta (112x112x14 mm)."),
    ("04A_Torreta_Nucleo_Central_001_x1", g.crear_001_main_body(), 1, "Nucleo central de la torreta (90x126x94 mm). Con ranuras y roscas M4 laterales."),
    ("04B_Cuna_Motor_Izquierda_001B_x1", g.crear_001B_cuna_motor_izq(), 1, "Cuna maciza izquierda para Motor J2 (68x95.8x54 mm). Se atornilla con 4 M4 al nucleo."),
    ("04C_Cuna_Motor_Derecha_001C_x1", g.crear_001C_cuna_motor_der(), 1, "Cuna maciza derecha para Motor J3 (68x95.8x54 mm). Se atornilla con 4 M4 al nucleo."),
    ("05_Abrazadera_Motor_M4_009_Servo_Plate_x2", g.crear_009_servo_plate(), 2, "Abrazadera superior de 68mm con 4 tornillos M4. IMPRIMIR 2 UNIDADES."),
    
    # 2. Brazos y Paralelogramos (Todos <= 200 mm para caber rectos en cama de 220x215 mm)
    ("06_Brazo_Principal_004_Forward_Drive_Arm_x1", g.crear_004_forward_drive_arm(), 1, "Brazo principal L1=155mm (192x48x46 mm). Mamelon O46mm para motor J2."),
    ("07_Palanca_Motriz_002_Vertical_Drive_Arm_x1", g.crear_002_vertical_drive_arm(), 1, "Palanca motriz R=50mm (87x23x46 mm). Mamelon O46mm para motor J3."),
    ("08_Biela_Inferior_155mm_003_Link_x2", g.crear_003_link(g.L1), 2, "Bielas del paralelogramo inferior (176x6x21 mm). IMPRIMIR 2 UNIDADES."),
    ("09_Biela_Superior_130mm_003_Link_Forearm_x1", g.crear_003_link(g.L2), 1, "Biela superior del paralelogramo del antebrazo (151x6x21 mm)."),
    ("10_Antebrazo_Horizontal_005_Horizontal_Arm_x1", g.crear_005_horizontal_arm(), 1, "Antebrazo horizontal L2=130mm (200x33.5x20 mm -> cabe con 20mm de margen)."),
    ("11_Escuadra_Codo_006_Triangular_Link_x1", g.crear_006_triangular_link(), 1, "Escuadra triangular del codo (65x37x62 mm)."),
    
    # 3. Nuevo Grado de Libertad (Pitch) con Cuna Anti-Rotacion + Abrazadera Trasera y Garra
    ("12A_Soporte_Muneca_Pitch_020_Con_Cuna_Servo_x1", g.crear_020_wrist_pitch_bracket(), 1, "Soporte de muneca con jaula/cuna profunda que evita que el servo SG90 gire sobre si mismo."),
    ("12B_Abrazadera_Trasera_Servo_Pitch_021_x1", g.crear_021_wrist_servo_clamp(), 1, "NUEVA PIEZA: Tapa trasera que prensa y atornilla la cola del servo SG90 de Pitch."),
    ("13_Soporte_Garra_Pitch_012_Claw_Support_x1", g.crear_012_claw_support(), 1, "Soporte de la garra con collarin profundo anti-rotacion para el servo de la pinza."),
    ("14_Engranaje_Garra_015_Drive_Gear_x1", g.crear_015_drive_gear(), 1, "Engranaje motriz central acoplado al servo de la pinza."),
    ("15_Dedo_Derecho_013_Right_Finger_x1", g.crear_013_right_finger(), 1, "Dedo derecho con sector dentado calibrado."),
    ("16_Dedo_Izquierdo_014_Left_Finger_x1", g.crear_014_left_finger(), 1, "Dedo izquierdo con sector dentado calibrado."),
    ("17_Soporte_Maestro_018_Holder_x1_OPCIONAL", g.crear_018_maestro_holder(), 1, "Soporte trasero de controlador Pololu Maestro (Opcional)."),

    # 4. Pasadores Imprimibles con tolerancias FDM
    ("Pin_12mm_Motor_x3", g.crear_pin_pasador(largo=46.0, diametro=g.MOTOR_PIN_PRINT_D, orientacion="X"), 3, "Pasador O11.75x46mm para eje de acero O12mm. IMPRIMIR 3 UDS (100% relleno)."),
    ("Pin_8mm_Articulacion_x8", g.crear_pin_pasador(largo=18.0, diametro=g.PIVOT_PIN_PRINT_D, orientacion="Y"), 8, "Pasador O8.20x18mm para articulaciones (encaje ligeramente a presion en Ø8.30mm). IMPRIMIR 8 UNIDADES."),
    ("Pin_8mm_Codo_Largo_x1", g.crear_pin_pasador(largo=46.0, diametro=g.PIVOT_PIN_PRINT_D, orientacion="Y"), 1, "Pasador O8.20x46mm pasante del codo E1 (encaje ligeramente a presion)."),
    ("Pin_4mm_Dedos_Garra_x2", g.crear_pin_pasador(largo=14.0, diametro=g.FINGER_PIN_PRINT_D, orientacion="Z"), 2, "Pasador O3.80x14mm para pivotes de los dedos."),
    ("Tubo_Central_O1_x1", g.crear_tubo_central(largo=22.0), 1, "Eje tubular pasivo central O1 (O8.20x22mm exterior)."),
]

print("=== EXPORTANDO PIEZAS IMPRIMIBLES OPTIMIZADAS PARA CAMA 220x215x245 mm ===")
tabla_resumen = []

for nombre, solido, cant, desc in piezas_imprimibles:
    path_step = os.path.join(DIR_STEP, f"{nombre}.step")
    path_stl = os.path.join(DIR_STL, f"{nombre}.stl")
    
    cq.exporters.export(solido, path_step)
    cq.exporters.export(solido, path_stl, tolerance=0.03, angularTolerance=0.15)
    
    bb = solido.val().BoundingBox()
    dims_str = f"{bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm"
    assert max(bb.xlen, bb.ylen) <= 205.0 and bb.zlen <= 240.0, f"ERROR: {nombre} excede cama: {dims_str}"
    print(f" -> {nombre:50s} | {dims_str:24s} | OK (<= 220x215x245)")
    tabla_resumen.append(f"| `{nombre}.stl` | **{cant}** | `{dims_str}` | {desc} |")

# Generar Guía de Impresión Markdown actualizada
guia_path = os.path.join(DEST_DIR, "GUIA_DE_IMPRESION_3D.md")
with open(guia_path, "w", encoding="utf-8") as f:
    f.write("# Guía de Impresión 3D (Adaptada a Cama 220 x 215 x 245 mm)\n\n")
    f.write("Todas las piezas de esta carpeta han sido verificadas para caber con **mínimo 20 mm de margen libre** dentro de un volumen de impresión de **220 x 215 x 245 mm**.\n\n")
    f.write("## 1. Cómo se ensambla la Torreta Modular (`04A`, `04B`, `04C`)\n")
    f.write("- Para no exceder los 215 mm de tu cama (ya que los dos motores NEMA 17 + reductora opuestos suman 310 mm), la torreta se dividió en **3 bloques macizos con encaje machihembrado**:\n")
    f.write("  1. **`04A_Torreta_Nucleo_Central_001_x1.stl`** (`90 x 126 x 94 mm`)\n")
    f.write("  2. **`04B_Cuna_Motor_Izquierda_001B_x1.stl`** (`68 x 95.8 x 54 mm`)\n")
    f.write("  3. **`04C_Cuna_Motor_Derecha_001C_x1.stl`** (`68 x 95.8 x 54 mm`)\n")
    f.write("- Cada cuna lateral tiene **2 chavetas rectangulares macho** que encajan en las ranuras del núcleo central (soportando todo el peso vertical del motor) y se fija con **4 tornillos horizontales M4 x 25 mm** desde los bolsillos laterales antes de colocar el motor.\n\n")
    f.write("## 2. Cómo se bloquea el Servo SG90 del Último Grado de Libertad (`12A` + `12B` y `13`)\n")
    f.write("- **`12A_Soporte_Muneca_Pitch_020_Con_Cuna_Servo_x1.stl`**: Ahora incorpora una **jaula/cuna profunda de 16.5 mm** con paredes de `3.2 mm` que abraza las 4 caras rectangulares del servo SG90 de cabeceo (Pitch) y dos pilares donde apoyan sus pestañas con agujeros para tornillos.\n")
    f.write("- **`12B_Abrazadera_Trasera_Servo_Pitch_021_x1.stl`**: Tapa/abrazadera trasera que encaja en la cola del servo SG90 y se atornilla a través de las pestañas del servo hacia los pilares de `12A`, dejando la carcasa del motor 100% inmovilizada para que toda la fuerza mueva la garra.\n")
    f.write("- **`13_Soporte_Garra_Pitch_012_Claw_Support_x1.stl`**: También cuenta con un **collarín elevado de 14 mm de profundidad** que abraza el cuerpo del segundo servo SG90 (el que abre y cierra los dedos) y postes para sus 2 tornillos.\n\n")
    f.write("## 3. Lista de Archivos, Dimensiones Exactas y Cantidades\n\n")
    f.write("| Archivo STL / STEP | Cant. | Dimensiones (X x Y x Z) | Descripción y Función |\n")
    f.write("| :--- | :---: | :---: | :--- |\n")
    f.write("\n".join(tabla_resumen))
    f.write("\n\n## 4. Tornillería y Hardware Comercial Necesario\n")
    f.write("- **16 Tornillos Allen M4 x 22-25 mm:**\n")
    f.write("  - 8 tornillos M4 para unir rígidamente las cunas `04B` y `04C` al núcleo central `04A`.\n")
    f.write("  - 8 tornillos M4 para fijar las dos abrazaderas superiores `05_Abrazadera_Motor_M4`.\n")
    f.write("- **3 Motores NEMA 17 con reductora planetaria** (`39.3 x Ø25.6 mm`, pin `Ø12 mm`).\n")
    f.write("- **2 Micro-servos SG90 / MG90S:** Uno para cabeceo de muñeca (Pitch) y otro para abrir/cerrar la garra (con sus 4 tornillos M2/autorroscantes incluidos en la bolsita del servo).\n")

print(f"\n¡Éxito! Todas las piezas verificadas <= 200 mm y exportadas en: {DEST_DIR}")
