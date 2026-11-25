# Guía de Impresión 3D (Adaptada a Cama 220 x 215 x 245 mm)

Todas las piezas de esta carpeta han sido verificadas para caber con **mínimo 20 mm de margen libre** dentro de un volumen de impresión de **220 x 215 x 245 mm**.

## 1. Cómo se ensambla la Torreta Modular (`04A`, `04B`, `04C`)
- Para no exceder los 215 mm de tu cama (ya que los dos motores NEMA 17 + reductora opuestos suman 310 mm), la torreta se dividió en **3 bloques macizos con encaje machihembrado**:
  1. **`04A_Torreta_Nucleo_Central_001_x1.stl`** (`90 x 126 x 94 mm`)
  2. **`04B_Cuna_Motor_Izquierda_001B_x1.stl`** (`68 x 95.8 x 54 mm`)
  3. **`04C_Cuna_Motor_Derecha_001C_x1.stl`** (`68 x 95.8 x 54 mm`)
- Cada cuna lateral tiene **2 chavetas rectangulares macho** que encajan en las ranuras del núcleo central (soportando todo el peso vertical del motor) y se fija con **4 tornillos horizontales M4 x 25 mm** desde los bolsillos laterales antes de colocar el motor.

## 2. Cómo se bloquea el Servo SG90 del Último Grado de Libertad (`12A` + `12B` y `13`)
- **`12A_Soporte_Muneca_Pitch_020_Con_Cuna_Servo_x1.stl`**: Ahora incorpora una **jaula/cuna profunda de 16.5 mm** con paredes de `3.2 mm` que abraza las 4 caras rectangulares del servo SG90 de cabeceo (Pitch) y dos pilares donde apoyan sus pestañas con agujeros para tornillos.
- **`12B_Abrazadera_Trasera_Servo_Pitch_021_x1.stl`**: Tapa/abrazadera trasera que encaja en la cola del servo SG90 y se atornilla a través de las pestañas del servo hacia los pilares de `12A`, dejando la carcasa del motor 100% inmovilizada para que toda la fuerza mueva la garra.
- **`13_Soporte_Garra_Pitch_012_Claw_Support_x1.stl`**: También cuenta con un **collarín elevado de 14 mm de profundidad** que abraza el cuerpo del segundo servo SG90 (el que abre y cierra los dedos) y postes para sus 2 tornillos.

## 3. Lista de Archivos, Dimensiones Exactas y Cantidades

| Archivo STL / STEP | Cant. | Dimensiones (X x Y x Z) | Descripción y Función |
| :--- | :---: | :---: | :--- |
| `01_Base_010_Basement_x1.stl` | **1** | `128.0 x 128.0 x 112.1 mm` | Base inferior del robot (128x128x112 mm). Aloja motor J1. |
| `02_Engranaje_Base_016_Driven_Gear_x1.stl` | **1** | `58.9 x 55.3 x 35.0 mm` | Engranaje de giro de torreta. Mamelon O46mm para eje O25.6mm. |
| `03_Plato_Giratorio_011_Round_Plate_x1.stl` | **1** | `112.1 x 112.1 x 14.0 mm` | Plato de apoyo con rieles para la torreta (112x112x14 mm). |
| `04A_Torreta_Nucleo_Central_001_x1.stl` | **1** | `90.0 x 126.0 x 94.0 mm` | Nucleo central de la torreta (90x126x94 mm). Con ranuras y roscas M4 laterales. |
| `04B_Cuna_Motor_Izquierda_001B_x1.stl` | **1** | `70.0 x 95.8 x 54.0 mm` | Cuna maciza izquierda para Motor J2 (68x95.8x54 mm). Se atornilla con 4 M4 al nucleo. |
| `04C_Cuna_Motor_Derecha_001C_x1.stl` | **1** | `70.0 x 95.8 x 54.0 mm` | Cuna maciza derecha para Motor J3 (68x95.8x54 mm). Se atornilla con 4 M4 al nucleo. |
| `05_Abrazadera_Motor_M4_009_Servo_Plate_x2.stl` | **2** | `68.0 x 32.0 x 26.0 mm` | Abrazadera superior de 68mm con 4 tornillos M4. IMPRIMIR 2 UNIDADES. |
| `06_Brazo_Principal_004_Forward_Drive_Arm_x1.stl` | **1** | `192.0 x 48.0 x 46.1 mm` | Brazo principal L1=155mm (192x48x46 mm). Mamelon O46mm para motor J2. |
| `07_Palanca_Motriz_002_Vertical_Drive_Arm_x1.stl` | **1** | `87.0 x 23.1 x 46.1 mm` | Palanca motriz R=50mm (87x23x46 mm). Mamelon O46mm para motor J3. |
| `08_Biela_Inferior_155mm_003_Link_x2.stl` | **2** | `176.0 x 6.0 x 21.0 mm` | Bielas del paralelogramo inferior (176x6x21 mm). IMPRIMIR 2 UNIDADES. |
| `09_Biela_Superior_130mm_003_Link_Forearm_x1.stl` | **1** | `151.0 x 6.0 x 21.0 mm` | Biela superior del paralelogramo del antebrazo (151x6x21 mm). |
| `10_Antebrazo_Horizontal_005_Horizontal_Arm_x1.stl` | **1** | `200.0 x 33.5 x 20.0 mm` | Antebrazo horizontal L2=130mm (200x33.5x20 mm -> cabe con 20mm de margen). |
| `11_Escuadra_Codo_006_Triangular_Link_x1.stl` | **1** | `65.0 x 37.0 x 62.0 mm` | Escuadra triangular del codo (65x37x62 mm). |
| `12A_Soporte_Muneca_Pitch_020_Con_Cuna_Servo_x1.stl` | **1** | `78.0 x 52.5 x 61.0 mm` | Soporte de muneca con jaula/cuna profunda que evita que el servo SG90 gire sobre si mismo. |
| `12B_Abrazadera_Trasera_Servo_Pitch_021_x1.stl` | **1** | `40.0 x 12.0 x 18.4 mm` | NUEVA PIEZA: Tapa trasera que prensa y atornilla la cola del servo SG90 de Pitch. |
| `13_Soporte_Garra_Pitch_012_Claw_Support_x1.stl` | **1** | `53.5 x 29.0 x 17.5 mm` | Soporte de la garra con collarin profundo anti-rotacion para el servo de la pinza. |
| `14_Engranaje_Garra_015_Drive_Gear_x1.stl` | **1** | `26.0 x 26.0 x 5.0 mm` | Engranaje motriz central acoplado al servo de la pinza. |
| `15_Dedo_Derecho_013_Right_Finger_x1.stl` | **1** | `57.9 x 17.1 x 12.0 mm` | Dedo derecho con sector dentado calibrado. |
| `16_Dedo_Izquierdo_014_Left_Finger_x1.stl` | **1** | `55.0 x 18.3 x 12.0 mm` | Dedo izquierdo con sector dentado calibrado. |
| `17_Soporte_Maestro_018_Holder_x1_OPCIONAL.stl` | **1** | `20.0 x 32.0 x 48.0 mm` | Soporte trasero de controlador Pololu Maestro (Opcional). |
| `Pin_12mm_Motor_x3.stl` | **3** | `46.0 x 11.8 x 11.8 mm` | Pasador O11.75x46mm para eje de acero O12mm. IMPRIMIR 3 UDS (100% relleno). |
| `Pin_8mm_Articulacion_x8.stl` | **8** | `8.2 x 18.0 x 8.2 mm` | Pasador O8.20x18mm para articulaciones (encaje ligeramente a presion en Ø8.30mm). IMPRIMIR 8 UNIDADES. |
| `Pin_8mm_Codo_Largo_x1.stl` | **1** | `8.2 x 46.0 x 8.2 mm` | Pasador O8.20x46mm pasante del codo E1 (encaje ligeramente a presion). |
| `Pin_4mm_Dedos_Garra_x2.stl` | **2** | `3.8 x 3.8 x 14.0 mm` | Pasador O3.80x14mm para pivotes de los dedos. |
| `Tubo_Central_O1_x1.stl` | **1** | `8.2 x 22.0 x 8.2 mm` | Eje tubular pasivo central O1 (O8.20x22mm exterior). |

## 4. Tornillería y Hardware Comercial Necesario
- **16 Tornillos Allen M4 x 22-25 mm:**
  - 8 tornillos M4 para unir rígidamente las cunas `04B` y `04C` al núcleo central `04A`.
  - 8 tornillos M4 para fijar las dos abrazaderas superiores `05_Abrazadera_Motor_M4`.
- **3 Motores NEMA 17 con reductora planetaria** (`39.3 x Ø25.6 mm`, pin `Ø12 mm`).
- **2 Micro-servos SG90 / MG90S:** Uno para cabeceo de muñeca (Pitch) y otro para abrir/cerrar la garra (con sus 4 tornillos M2/autorroscantes incluidos en la bolsita del servo).
