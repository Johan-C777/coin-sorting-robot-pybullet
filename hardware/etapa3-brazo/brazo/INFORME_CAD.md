# Informe Exhaustivo de Auditoría CAD, Rediseño de Motores y Nuevo Grado de Libertad (Pitch)

Se realizó una auditoría geométrica, cinemática y de manufactura aditiva (impresión 3D FDM) sobre todos los modelos `.step` y el script generador [`generar_brazo_step.py`](generadores/generar_brazo_step.py), incorporando además las **medidas reales tomadas con pie de rey** ([`referencia_motor.png`](referencia_motor.png)), el **refuerzo estructural macizo de las cunas de motor con tornillería superior M4**, y el **nuevo grado de libertad de cabeceo (Pitch) para la garra**.

---

## 1. Nuevas Especificaciones Implementadas (Según Foto con Pie de Rey y Requerimientos 3D)

### 1.1. Acople Cilíndrico Real de Acero (`39.3 mm x Ø25.6 mm`) y Pasador Transversal (`Ø12.0 mm`)
- **Separación de tuerca y contratuerca:** Se modeló el tramo de `12.0 mm` entre la cara frontal de la reductora planetaria turquesa y el inicio del cilindro metálico.
- **Cilindro de acero inoxidable:** Ajustado de `Ø25.0 x 35.0 mm` a las medidas reales del pie de rey: **`Ø25.6 mm` de diámetro exterior** (`SHAFT_ROT_D = 25.6 mm`) y **`39.3 mm` de longitud** (`CYL_STEEL_L = 39.3 mm`), dando una longitud total de **`51.3 mm`** desde la cara frontal de la reductora.
- **Agujero transversal para pasador del motor:** Ajustado de `Ø8.0 mm` al valor real medido de **`Ø12.0 mm`** (`MOTOR_PIN_NOM_D = 12.0 mm`), centrado a **`13.5 mm` desde la punta** (`37.8 mm` desde la cara frontal de la reductora).
- **Mamelones reforzados en piezas impresas (`002`, `004`, `016`):**
  - Diámetro interior con tolerancia de impresión 3D: **`Ø26.00 mm`** (`SHAFT_FIT_R = 13.00 mm`, holgura radial de `+0.20 mm`).
  - Diámetro exterior del mamelón ampliado a **`Ø46.0 mm`** (`HUB_OUTER_R = 23.0 mm`) para garantizar una pared maciza de `10.0 mm` alrededor del cilindro de `Ø25.6 mm` y soportar el pasador transversal de `Ø12.0 mm` sin fracturas.
  - Paso libre en paredes fijas (`001_main_body` y `010_basement`): ampliado a **`Ø28.0 mm`** (`SHAFT_CLEAR_R = 14.0 mm`) para que el cilindro metálico y las tuercas giren sin rozar jamás la estructura.

### 1.2. Cunas de Motor Macizas de Cuerpo Completo (`001_main_body`) + Tornillos Superiores `M4` (`009_servo_plate`)
- **Eliminación total de voladizos:** Las cunas laterales de los motores `J2` y `J3` en [`crear_001_main_body`](generadores/generar_brazo_step.py#L272-L426) ahora bajan **completamente macizas hasta el piso de la torreta (`Z = 0.0 mm`)** y tienen el mismo ancho total que el cuerpo central (**`68.0 mm`**). Esto permite imprimir `EBA_01.00.001.step` plano sobre la cama de la impresora 3D sin soportes colgantes y elimina la flexión bajo el peso de los motores NEMA 17 con reductora.
- **Fijación superior con 8 tornillos Allen `M4`:** Las abrazaderas superiores [`crear_009_servo_plate`](generadores/generar_brazo_step.py#L430-L456) se ensancharon a **`68.0 mm`** y cuentan con **4 perforaciones pasantes `M4` (`Ø4.30 mm`) con cajera para cabeza Allen** en cada lado (8 tornillos `M4` en total), alineadas con **4 perforaciones de `Ø3.70 mm` (`22 mm` de profundidad)** en cada cuna maciza para roscar directamente en el plástico o colocar insertos térmicos `M4`.

### 1.3. Nuevo Grado de Libertad (Cabeceo / Pitch de la Garra Arriba y Abajo)
- **Nueva pieza imprimible [`EBA_01.00.020_wrist_pitch_bracket.step`](stl/12A_Soporte_Muneca_Pitch_020_Con_Cuna_Servo_x1.stl) ([`crear_020_wrist_pitch_bracket`](generadores/generar_brazo_step.py#L573-L637)):**
  - Recibe los dos pasadores de `Ø8.0 mm` de la muñeca (`W1` del antebrazo `005` y `W2` de la biela superior `003`), conservando intacto el mecanismo de doble paralelogramo.
  - Se extiende hacia adelante formando una horquilla abierta de `32.0 mm` de luz libre (`Y in [-20.0, +12.0]`) hasta el nuevo eje de cabeceo `X_PITCH = X_W1 + 28.0 mm`.
  - Su brazo izquierdo (`Y in [-24.0, -20.0]`) aloja un **micro-servo `SG90` / `MG90S` de cabeceo (`MicroServo_SG90_Pitch_Muneca`)**, mientras que su brazo derecho (`Y in [+12.0, +16.0]`) soporta el pasador pasivo coaxial de `Ø8.0 mm` (`Pin_8mm_Eje_Pitch_Garra`).
- **Soporte de garra rediseñado [`EBA_01.00.012_R01_claw_support.step`](stl/13_Soporte_Garra_Pitch_012_Claw_Support_x1.stl) ([`crear_012_claw_support`](generadores/generar_brazo_step.py#L641-L699)):**
  - Incorpora dos orejas traseras redondeadas (`R = 7.5 mm`) alineadas con el eje `Pitch`: la oreja izquierda (`Y = -16.5 mm`) se acopla directamente al eje del servo `SG90` de cabeceo y la oreja derecha (`Y = +8.5 mm`) pivota sobre el pasador pasivo derecho, permitiendo inclinar toda la garra hacia arriba y hacia abajo (`±45°`).

---

## 2. Errores Originales Corregidos y Verificación de Colisiones (`0.0 mm³`)

| # | Problema / Requerimiento | Solución Implementada en [`generar_brazo_step.py`](generadores/generar_brazo_step.py) | Estado |
| :--- | :--- | :--- | :--- |
| **1** | **Eje de motor desactualizado (`Ø25 x 35 mm`, pin `Ø8 mm`)** | Actualizado a medidas reales del pie de rey: `12.0 mm` de tuerca/contratuerca + cilindro de **`Ø25.6 x 39.3 mm`** (`51.3 mm` totales) y pasador transversal de **`Ø12.0 mm`** a `13.5 mm` de la punta. | **Corregido** |
| **2** | **Soportes de motores colgando en voladizo** | Cunas laterales de `001_main_body` convertidas en bloques macizos desde `Z = 0.0 mm` con ancho completo de `68.0 mm` y 8 tornillos superiores `M4` en las abrazaderas `009`. | **Corregido** |
| **3** | **Falta de movimiento vertical (Pitch) en la garra** | Se creó `020_wrist_pitch_bracket` con servo `SG90` dedicado para inclinar todo el subensamble de la garra (`012`, `013`, `014`, `015`) hacia arriba y abajo. | **Corregido** |
| **4** | **13 colisiones severas en el ensamble original** | Reubicados axialmente todos los eslabones sobre `O1`, `E1`, `W1` y `X_PITCH`. Verificado mediante intersección booleana 3D entre los **48 sólidos** del ensamble con **0 colisiones (`0.00 mm³`)**. | **Corregido** |
| **5** | **Tolerancias de pasadores para impresión 3D** | Todos los pasadores y agujeros tienen holgura calibrada para impresión FDM (`Ø11.75 mm` para huecos de `Ø12.0 mm`, `Ø7.75 mm` para articulaciones de `Ø8.30 mm`, y `Ø3.80 mm` para dedos de `Ø4.30 mm`). | **Corregido** |

---

## 3. Lista de Archivos `.step` Listos para Imprimir en 3D

Todas las piezas se regeneraron desde `generadores/` y se verificaron; los STL de impresión están en `stl/` y el ensamble completo en `step/`:

### Piezas Estructurales del Brazo
- [`EBA_01.00.010_basement.step`](stl/01_Base_010_Basement_x1.stl) — Base fija elevada (`112 mm`) para alojar motor `J1` + sección de tuercas (`12 mm`).
- [`EBA_01.00.016_R01_driven_gear.step`](stl/02_Engranaje_Base_016_Driven_Gear_x1.stl) — Engranaje conducido con mamelón de `Ø46 mm`, encaje de `Ø26.0 mm` y hueco de pasador `Ø12.3 mm`.
- [`EBA_01.00.011_round_plate.step`](stl/03_Plato_Giratorio_011_Round_Plate_x1.stl) — Plato giratorio de acoplamiento a la torreta.
- [`EBA_01.00.001.step`](stl/04A_Torreta_Nucleo_Central_001_x1.stl) — Torreta principal con **cunas laterales macizas desde `Z = 0` (`68 mm` de ancho)** y 8 perforaciones para tornillos `M4`.
- [`EBA_01.00.009_servo_plate.step`](stl/05_Abrazadera_Motor_M4_009_Servo_Plate_x2.stl) — Abrazadera superior reforzada (`68 mm` de ancho) para 4 tornillos Allen `M4` (imprimir **2 unidades**).
- [`EBA_01.00.004_forward_drive_arm.step`](stl/06_Brazo_Principal_004_Forward_Drive_Arm_x1.stl) — Brazo principal (`L1 = 160 mm`) con mamelón de `Ø46 mm`, hueco de `Ø26.0 mm` y pasador `Ø12.3 mm`.
- [`EBA_01.00.002_vertical_drive_arm.step`](stl/07_Palanca_Motriz_002_Vertical_Drive_Arm_x1.stl) — Palanca motriz (`R = 50 mm`) con mamelón de `Ø46 mm`, hueco de `Ø26.0 mm` y pasador `Ø12.3 mm`.
- [`EBA_01.00.003_link.step`](stl/08_Biela_Inferior_155mm_003_Link_x2.stl) — Biela de `160 mm` para el paralelogramo inferior (imprimir **2 unidades**).
- [`EBA_01.00.003_link_forearm.step`](stl/09_Biela_Superior_130mm_003_Link_Forearm_x1.stl) — Biela superior del antebrazo de `150 mm` (imprimir **1 unidad**).
- [`EBA_01.00.005_horizontal_arm.step`](stl/10_Antebrazo_Horizontal_005_Horizontal_Arm_x1.stl) — Antebrazo horizontal (`150 mm + 50 mm`).
- [`EBA_01.00.006_triangular_link.step`](stl/11_Escuadra_Codo_006_Triangular_Link_x1.stl) — Escuadra triangular del codo.
- [`EBA_01.00.020_wrist_pitch_bracket.step`](stl/12A_Soporte_Muneca_Pitch_020_Con_Cuna_Servo_x1.stl) — **NUEVA PIEZA:** Soporte de muñeca con horquilla y alojamiento para el servo `SG90` de cabeceo (Pitch).
- [`EBA_01.00.012_R01_claw_support.step`](stl/13_Soporte_Garra_Pitch_012_Claw_Support_x1.stl) — Soporte de la garra con orejas de inclinación Pitch.
- [`EBA_01.00.013_R01_right_finger.step`](stl/15_Dedo_Derecho_013_Right_Finger_x1.stl), [`EBA_01.00.014_R01_left_finger.step`](stl/16_Dedo_Izquierdo_014_Left_Finger_x1.stl), [`EBA_01.00.015_drive_gear.step`](stl/14_Engranaje_Garra_015_Drive_Gear_x1.stl) — Dedos y engranaje motriz de la garra.
- [`EBA_01.00.018_maestro_holder.step`](stl/17_Soporte_Maestro_018_Holder_x1_OPCIONAL.stl) — Soporte trasero de controlador.

### Pasadores y Ejes Imprimibles en 3D
- [`Pin_Imprimible_12mm_Motor.step`](stl/Pin_12mm_Motor_x3.stl) — Pasador de **`Ø11.75 x 46.0 mm`** para atravesar el hueco de `Ø12.0 mm` de los 3 ejes metálicos y los mamelones de `Ø46 mm` (imprimir **3 unidades** con 100% de relleno / perímetros).
- [`Pin_Imprimible_8mm_Articulacion.step`](stl/Pin_8mm_Articulacion_x8.stl) — Pasador de **`Ø7.75 x 18.0 mm`** para articulaciones del paralelogramo (imprimir **8 unidades**).
- [`Pin_Imprimible_8mm_Codo_Largo.step`](stl/Pin_8mm_Codo_Largo_x1.stl) — Pasador principal del codo `E1` de **`Ø7.75 x 46.0 mm`** (imprimir **1 unidad**).
- [`Pin_Imprimible_4mm_Dedos.step`](stl/Pin_4mm_Dedos_Garra_x2.stl) — Pasador de **`Ø3.80 x 14.0 mm`** para los dedos de la pinza (imprimir **2 unidades**).
- [`Tubo_Central_O1_Imprimible.step`](stl/Tubo_Central_O1_x1.stl) — Eje tubular pasivo central `O1` de **`Ø7.75 x 22.0 mm`** (imprimir **1 unidad**).

### Ensamble Completo Verificado
- [`Ensamble_EBA_40cm_NEMA_Planetaria_Final.step`](step/Ensamble_EBA_40cm_NEMA_Planetaria_Final.step) — Ensamble completo de 48 sólidos con motores, tornillos `M4`, pasadores y garra con grado de libertad Pitch.
