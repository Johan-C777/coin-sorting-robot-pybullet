# Guía de Conexiones y Calibración — Robot 4 GDL + Garra (Fase 1)

Esta guía acompaña al firmware [`ESP32_Calibracion_Robot4GDL.ino`](file:///C:/Users/samue/PycharmProjects/REI/ESP32_Calibracion_Robot4GDL/ESP32_Calibracion_Robot4GDL.ino), diseñado a partir del ensamble CAD en [`CAD/generar_brazo_step.py`](file:///C:/Users/samue/PycharmProjects/REI/CAD/generar_brazo_step.py) y [`CAD/Caja_Reductora_Planetaria/generar_caja_planetaria.py`](file:///C:/Users/samue/PycharmProjects/REI/CAD/Caja_Reductora_Planetaria/generar_caja_planetaria.py).

---

## 1. Tabla de Pines de la ESP32 (Compatible con DevKit 30 y 38 pines)

Todos los pines elegidos son salidas 100% seguras (se evitaron los pines *strapping* `GPIO 0, 2, 5, 12, 15`, los de solo entrada `34–39` y los de flash `6–11`).

| Actuador | Función en el CAD | Señal | Pin ESP32 | Notas |
| :--- | :--- | :---: | :---: | :--- |
| **Motor J1** (NEMA 17 + Planetaria) | Base / Giro torreta (`010` → `016` → `011`) | `STEP` | **GPIO 26** | Pulso de paso al driver J1 |
| **Motor J1** (NEMA 17 + Planetaria) | Base / Giro torreta | `DIR` | **GPIO 25** | Dirección al driver J1 |
| **Motor J2** (NEMA 17 + Planetaria) | Hombro / Brazo principal (`004`, lado izq.) | `STEP` | **GPIO 33** | Pulso de paso al driver J2 |
| **Motor J2** (NEMA 17 + Planetaria) | Hombro / Brazo principal | `DIR` | **GPIO 32** | Dirección al driver J2 |
| **Motor J3** (NEMA 17 + Planetaria) | Codo / Palanca antebrazo (`002` → `005`, lado der.) | `STEP` | **GPIO 27** | Pulso de paso al driver J3 |
| **Motor J3** (NEMA 17 + Planetaria) | Codo / Palanca antebrazo | `DIR` | **GPIO 14** | Dirección al driver J3 |
| **Enable común (3 drivers)** | Activar / soltar torque desde la web | `EN` | **GPIO 13** | Conectar en paralelo a `EN` de los 3 drivers (activo en LOW). Opcional: si lo dejas a `GND`, quedan siempre activos. |
| **Servo J4** (SG90 / MG90S) | Muñeca / Cabeceo Pitch (`020` → `012`) | `PWM` (Naranja/Amarillo) | **GPIO 18** | **Fijo en 90°** en esta fase |
| **Servo Garra** (SG90 / MG90S) | Pinza abrir/cerrar (`012` / `013` / `014`) | `PWM` (Naranja/Amarillo) | **GPIO 19** | **Fijo en 90°** en esta fase |

---

## 2. Esquema de Alimentación y Cableado (MUY IMPORTANTE)

```text
  [Fuente 12V o 24V (3A-5A)] ──┬── VMOT / GND ──> Driver J1 (+ capacitor 100uF) ──> NEMA 17 J1 (1A,1B,2A,2B)
                               ├── VMOT / GND ──> Driver J2 (+ capacitor 100uF) ──> NEMA 17 J2 (1A,1B,2A,2B)
                               └── VMOT / GND ──> Driver J3 (+ capacitor 100uF) ──> NEMA 17 J3 (1A,1B,2A,2B)

  [Fuente 5V externa (1A-2A)] ─┬── +5V (Rojo) y GND (Café) ──> Servo J4 (Pitch)   [Señal -> GPIO 18]
                               └── +5V (Rojo) y GND (Café) ──> Servo Garra        [Señal -> GPIO 19]

  [ESP32 DevKit (USB o 5V VIN)]
       ├── 3V3 ──> VDD lógico de los 3 drivers (solo A4988 / TMC2208 / TMC2209; DRV8825 no tiene VDD)
       └── GND ──> UNIR TODAS LAS TIERRAS EN COMÚN (GND ESP32 + GND Drivers + GND Fuente 5V + GND Fuente 12V/24V)
```

### Checklist obligatorio antes de encender:
1. **Puente `RESET` + `SLEEP`** (en **A4988** y **DRV8825**): deben estar unidos entre sí en cada driver; de lo contrario el motor no girará.
2. **Capacitor electrolítico de `100 µF` (≥ 35V)** entre `VMOT` y `GND` cerca de cada driver para evitar picos de voltaje que quemen el driver al conectar la fuente.
3. **Nunca desconectes un NEMA 17 con la fuente de 12V/24V encendida**: destruye el driver al instante.
4. **Ajusta la corriente `Vref`** en el potenciómetro de cada driver antes de probar (para NEMA 17 típicos de 1.2A–1.5A, empieza suave alrededor de 0.8A–1.0A para que no se calienten las piezas impresas en PLA).
5. **Tierra común (`GND`)**: el `GND` de la ESP32, el `GND` de la fuente de 5V de los servos y el `GND` lógico de los drivers deben estar conectados entre sí.
6. **Microstepping recomendado (`1/8` o `1/16`)**: con la reductora planetaria 16:1 del CAD, `1/8` da `200 × 8 × 16 = 25,600 pasos/vuelta` (`71.11 pasos/grado`), logrando movimiento suave y preciso sin exigir demasiada frecuencia de pasos a la ESP32.

| Microstepping | A4988 (`MS1, MS2, MS3`) | DRV8825 (`M0, M1, M2`) | TMC2208/2209 (`MS1, MS2`) |
| :---: | :---: | :---: | :---: |
| **1/1** | L, L, L | L, L, L | — |
| **1/2** | H, L, L | H, L, L | H, L (1/2) |
| **1/4** | L, H, L | L, H, L | L, H (1/4) |
| **1/8** | H, H, L | H, H, L | L, L (**1/8 por defecto**) |
| **1/16** | H, H, H | L, L, H | H, H (**1/16**) |

*(L = desconectado o a GND, H = conectado a 3.3V)*

---

## 3. Cómo Subir el Código y Abrir la Interfaz HTML (por USB Serial)

1. Abre [`ESP32_Calibracion_Robot4GDL.ino`](file:///C:/Users/samue/PycharmProjects/REI/ESP32_Calibracion_Robot4GDL/ESP32_Calibracion_Robot4GDL.ino) en **Arduino IDE** (o compílalo con `arduino-cli`).
2. Selecciona `ESP32 Dev Module` y tu puerto COM (ej. `COM5`). **No necesitas instalar librerías externas.**
3. Sube el código. Al arrancar:
   - Ambos servos (**J4 Pitch** y **Garra**) se colocan automáticamente en **90°** (aprovecha para atornillar las palas blancas centradas si aún no lo hiciste).
   - La ESP32 escucha comandos en **USB Serial a 115200 baud** (sin Wi-Fi, con pulsos más estables).
4. Ejecuta el puente serial local (no requiere `pip install`):
   ```powershell
   python "C:\Users\samue\PycharmProjects\REI\ESP32_Calibracion_Robot4GDL\servidor_serial.py" COM5
   ```
5. Abre **`http://127.0.0.1:5050`** en tu navegador. *(Cierra el Monitor Serie de Arduino IDE si estaba abierto, ya que solo un programa puede usar `COM5` a la vez).*

---

## 4. Procedimiento de Calibración (Para generar el archivo de la Fase 2)

1. En **Configuración de Hardware**, selecciona tu driver, los pasos por vuelta (`200`), el microstepping real que pusiste en los jumpers y revisa la relación de reductora en cada motor (`16` por defecto según el CAD).
2. Para **cada motor (J1, J2, J3)**:
   - Mueve el motor con los botones de pasos (`-50`, `+50`, `-10`, `+10`, `-1`, `+1`) hasta colocarlo en su **postura de CERO (0)**:
     - **J1 (Base):** Torreta mirando al frente (`+X`).
     - **J2 (Hombro):** Brazo principal `004` vertical (`90°`) — o la postura exacta que prefieras y anotes en el campo *"Descripción de la postura en CERO"*.
     - **J3 (Codo):** Antebrazo `005` completamente horizontal (`0°`).
   - Si al pulsar `+` gira al sentido contrario del que prefieres como positivo, marca **`Invertir sentido físico (invert_dir)`**.
   - Pulsa **`🎯 1. Fijar CERO (0) aquí`**.
   - Avanza poco a poco hacia el lado **negativo (`◀ -`)** hasta justo antes del tope mecánico seguro (deja un pequeño margen sin forzar las piezas 3D) y pulsa **`⬅️ 2. Límite NEG`**.
   - Regresa pasando por `0` hacia el lado **positivo (`+ ▶`)** hasta el tope mecánico seguro y pulsa **`3. Límite POS ➡️`**.
   - *(Opcional pero muy útil)*: despliega *"Datos para el archivo JSON"* y escribe hacia dónde se movió físicamente al sumar pasos `+`, y si mides los ángulos en los topes con un transportador, anótalos para calcular `pasos_por_grado_calibrado_real`.
3. Pulsa **`💾 Guardar en ESP32`** y luego **`⬇️ Descargar robot_4gdl_calibracion.json`**.
4. En nuestra siguiente sesión (**Fase 2**), pásame ese archivo `robot_4gdl_calibracion.json` y con esos datos programaremos el control exacto por ángulos (y cinemática directa/inversa si la necesitas) para los 4 GDL + garra.
