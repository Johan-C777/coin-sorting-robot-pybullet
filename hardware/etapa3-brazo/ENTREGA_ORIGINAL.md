# Entrega Robot 4 GDL + Garra (CAD + Firmware ESP32)

Paquete organizado con la versión más reciente y verificada de los modelos CAD (brazo robótico de 4 grados de libertad, garra SG90 actualizada y caja reductora planetaria 16:1), el código para ESP32, las interfaces HTML por USB Serial y las guías técnicas generadas hasta ahora.

---

## 1. Contenido de la carpeta

- **`01_CAD_Brazo_Completo/`**
  - `Ensamble_EBA_40cm_NEMA_Planetaria_Final.step` — Ensamble 3D completo del brazo robótico.
  - `00_MicroServo_SG90.step` y `00_NEMA17_Planetaria_25mm.step` — Modelos de referencia de los actuadores.
  - `INFORME_ERRORES_CAD.md` — Auditoría CAD con tolerancias de impresión 3D y corrección de colisiones.
  - `referencia_motor.png` — Referencia dimensional del acople real del motorreductor.
  - `PIEZAS_IMPRIMIBLES_3D/` — Piezas individuales listas para laminar en `STEP/` y `STL/`, junto con `GUIA_DE_IMPRESION_3D.md`.
  - `Scripts_Generadores/` — Scripts Python (`generar_brazo_step.py`, `exportar_imprimibles.py`, `generar_garra_sg90.py`).
  > **Nota importante:** Los archivos `12A..16` dentro de `01_CAD_Brazo_Completo/PIEZAS_IMPRIMIBLES_3D/` corresponden a la versión anterior de muñeca/garra. Para la versión final calibrada a servos SG90 reales y palas de `22 mm`, **usa los archivos de `02_CAD_Garra_SG90_Actualizada/`**.

- **`02_CAD_Garra_SG90_Actualizada/`**
  - `Imprimibles_STL/` — Las 7 piezas STL actualizadas de muñeca (Pitch) y garra para SG90 con palas blancas de `22 mm`.
  - `SolidWorks/` — Archivos nativos `.SLDPRT` / `.SLDASM` y respaldo `Ensamble_Garra_SG90.step`.
  - `GUIA_ENSAMBLE_E_IMPRESION.md` — Instrucciones de impresión y armado paso a paso de la muñeca y pinza.

- **`03_CAD_Caja_Reductora_Planetaria_16a1/`**
  - `00_Ensamble_Caja_con_Motor_NEMA17.step` y `00_Ensamble_Caja_Reductora_16a1.step` — Ensambles de la caja reductora planetaria de doble etapa (`16:1`).
  - `Imprimibles/` — Piezas imprimibles en STL/STEP de la reductora.
  - `generar_caja_planetaria.py` — Script paramétrico de la caja planetaria.

- **`04_Codigo_ESP32/`**
  - `ESP32_Calibracion_Robot4GDL/` — Firmware completo de calibración por USB Serial (`ESP32_Calibracion_Robot4GDL.ino`), interfaz web (`interfaz_calibracion.html`), puente local sin dependencias externas (`servidor_serial.py`) y guía (`GUIA_CONEXIONES_Y_CALIBRACION.md`) para fijar el cero (`0`), medir topes en pasos hacia cada lado y generar `robot_4gdl_calibracion.json` para la Fase 2 (control angular).
  - `ESP32_Solo_Motores/` — Código mínimo (`ESP32_Solo_Motores.ino` + `index.html`) para pruebas directas de movimiento de los 3 motores paso a paso vía Web Serial (`Chrome`/`Edge`), manteniendo ambos servos en `90°`.

---

## 2. Especificaciones principales del diseño CAD

- **Arquitectura mecánica:** Doble paralelogramo tipo EEZYbotARM (`40 cm` de alcance aprox.), con reductoras planetarias `16:1` en J1, J2 y J3, y 2 micro-servos SG90 para J4 (cabeceo/Pitch) y apertura/cierre de garra.
- **Dimensiones cinemáticas clave (`generar_brazo_step.py`):**
  - Brazo principal (`004_forward_drive_arm`, `L1`): `155.0 mm`
  - Antebrazo horizontal (`005_horizontal_arm`, `L2`): `130.0 mm`
  - Muñeca (`W1` a eje Pitch, `L_pitch`): `28.0 mm`
  - Garra (eje Pitch a punta de dedos, `L3`): `90.0 mm`
  - Brazo de palanca motriz (`002_vertical_drive_arm`, `R_crank`): `50.0 mm`
  - Altura global del eje del hombro `O1` desde la base (`Z_O1`): `197.0 mm` (`Z_TORRETA = 149.0 mm + 48.0 mm`)

---

## 3. Pinout verificado de la ESP32 (DevKit 30 y 38 pines)

| Actuador | Función en el robot | Señal | Pin ESP32 | Notas |
| :--- | :--- | :---: | :---: | :--- |
| **Motor J1** (NEMA 17 + Planetaria 16:1) | Base / Giro torreta | `STEP` (`CLK+`) | **GPIO 26** | Conectar `CLK-` a `GND` de la ESP32 |
| **Motor J1** (NEMA 17 + Planetaria 16:1) | Base / Giro torreta | `DIR` (`CW+`) | **GPIO 25** | Conectar `CW-` a `GND` de la ESP32 |
| **Motor J2** (NEMA 17 + Planetaria 16:1) | Hombro / Brazo principal `004` | `STEP` (`CLK+`) | **GPIO 33** | Conectar `CLK-` a `GND` de la ESP32 |
| **Motor J2** (NEMA 17 + Planetaria 16:1) | Hombro / Brazo principal `004` | `DIR` (`CW+`) | **GPIO 32** | Conectar `CW-` a `GND` de la ESP32 |
| **Motor J3** (NEMA 17 + Planetaria 16:1) | Codo / Palanca `002` → antebrazo `005` | `STEP` (`CLK+`) | **GPIO 27** | Conectar `CLK-` a `GND` de la ESP32 |
| **Motor J3** (NEMA 17 + Planetaria 16:1) | Codo / Palanca `002` → antebrazo `005` | `DIR` (`CW+`) | **GPIO 14** | Conectar `CW-` a `GND` de la ESP32 |
| **Enable común** (opcional, activo `LOW`) | Habilitar / soltar motores | `EN+` | **GPIO 13** | En **TB6560/TB6600** puede quedar desconectado (habilitado por defecto) |
| **Servo J4** (SG90 / MG90S) | Muñeca / Cabeceo Pitch (`020` → `012`) | `PWM` | **GPIO 18** | **Fijo en `90°`** durante Fase 1 / pruebas |
| **Servo Garra** (SG90 / MG90S) | Pinza abrir / cerrar | `PWM` | **GPIO 19** | **Fijo en `90°`** durante Fase 1 / pruebas |

---

## 4. Configuración verificada de los drivers a 24V

Configuración recomendada y verificada sobre tus drivers reales (**2× TB6560** y **1× TB6600**) alimentados a **24V** *(apagar la fuente de 24V antes de mover cualquier switch)*:

- **2× Drivers TB6560 (DIP rojo `1..6` + switches `SW1..SW3`):**
  - **Corriente `1.9 A`:** `SW1 = ON`, `SW2 = ON`, `SW3 = OFF`, `S1 = ON`
  - **Torque en reposo (`Stop` 50%):** `S2 = OFF`
  - **Microstepping `1/2`:** `S3 = ON`, `S4 = OFF`
  - **`Decay` para 24V:** `Decay 50%` (`S5 = OFF`, `S6 = ON`) o `Decay 100%` (`S5 = ON`, `S6 = ON`)
- **1× Driver TB6600 (DIP rosa `S1..S6`):**
  - **Microstepping `1/2`:** `S1 = OFF`, `S2 = ON`, `S3 = ON`
  - **Corriente `1.9 A`:** `S4 = ON`, `S5 = ON`, `S6 = OFF`

### Notas clave de cableado y potencia:
- **Fuente de `24V`:** usar cable grueso de cobre (**`18–22 AWG`**) en las borneras de potencia (`+24V`, `GND` y salidas de motor), evitando cables Dupont delgados en potencia.
- **Tierra común (`GND`):** unir el `GND` de la ESP32 con `CLK-` y `CW-` de los drivers, el `GND` de la fuente de `5V` (servos) y la referencia común del sistema.
- **Servos SG90:** alimentar con **fuente externa de `5V`** (no desde el pin `3V3` de la ESP32).

---

## 5. Cómo ejecutar los proyectos de ESP32

> Recuerda cerrar el Monitor Serie de Arduino IDE antes de usar cualquiera de las interfaces Web/Serial para que el puerto COM (ej. `COM5`) quede libre.

### Opción A: Prueba mínima directa (`04_Codigo_ESP32/ESP32_Solo_Motores/`)
1. Abre `ESP32_Solo_Motores.ino` en Arduino IDE (placa `ESP32 Dev Module`, sin librerías externas) y súbelo a la ESP32.
2. Abre `index.html` en **Google Chrome** o **Microsoft Edge** (usa **Web Serial API** directo a `115200 baud`, sin servidor Python).
3. Haz clic en **Conectar ESP32 (USB Serial)**, selecciona tu puerto COM (ej. `COM5`) y mueve los motores J1, J2 y J3 con los sliders o botones de pasos. Ambos servos permanecen fijos en `90°`.

### Opción B: Interfaz completa de Calibración de Cero y Límites (`04_Codigo_ESP32/ESP32_Calibracion_Robot4GDL/`)
1. Abre `ESP32_Calibracion_Robot4GDL.ino` en Arduino IDE y súbelo a la ESP32.
2. Ejecuta el puente Serial <-> Web en Python (no requiere `pip install`):
   ```powershell
   python ".\04_Codigo_ESP32\ESP32_Calibracion_Robot4GDL\servidor_serial.py" COM5
   ```
3. Abre **`http://127.0.0.1:5050`** en tu navegador.
4. Mueve cada motor paso a paso para fijar su **Cero (`0`)**, mide su límite **NEG (`-`)** y límite **POS (`+`)**, y pulsa **Guardar JSON en proyecto** (o **Descargar .json**) para obtener **`robot_4gdl_calibracion.json`**, el cual servirá como entrada directa para programar la **Fase 2 (control angular y cinemática del robot)**.
