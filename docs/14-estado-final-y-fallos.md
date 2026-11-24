# Estado final de las tres etapas, fallos y correcciones

Cierre del proyecto a noviembre de 2026: qué se construyó en cada etapa, qué se probó con
el montaje real, qué falla, por qué falla y cómo se corrige. Los números de desempeño que no
salen de una prueba física están marcados como simulación.

## Resumen

| Etapa | Diseño | Construcción | Electrónica y firmware | Prueba física |
|---|---|---|---|---|
| **1 · Clasificador** | ✅ CAD paramétrico v5, 24 piezas sin tornillos ni soportes | ✅ Impresa y armada; correcciones de la primera ronda impresas | ✅ ESP32-S3, firmware 0.9.0 con 16 pruebas en el PC y compilación en CI | ⚠️ Primera ronda hecha con monedas reales ([12](12-pruebas-fisicas-etapa1.md)); el ciclo automático completo aún no |
| **2 · Banda** | ✅ v7 motor fijo con barra dentada, 0 choques en 130 posiciones | ✅ Impresa (13 piezas, ≈ 372 g), montada y conectada | ✅ A4988 + NEMA17 desde el mismo ESP32-S3; banda activada en el firmware 0.9.0 | ⚠️ Mueve el cartucho de punta a punta; pierde posición por dos fallos mecánicos |
| **3 · Brazo** | ✅ Brazo real de 4 GDL (25 STL, garra y reductora 16:1); planificador entre 4 obstáculos | ⏳ En impresión y armado ([13](13-etapa3-brazo.md)) | ✅ Firmware de calibración del brazo; app Streamlit probada en el PC | ⏳ Sin prueba completa |

---

## Etapa 1 · Clasificador

### Qué funciona

- La tolva de disco sube las monedas una a una y las deja en la pista L01 (videos en
  [12-pruebas-fisicas-etapa1.md](12-pruebas-fisicas-etapa1.md)).
- Las monedas ruedan de canto por la pista hasta la compuerta y la compuerta las deja en el vaso.
- El firmware corre en el ESP32-S3: secuenciador de 11 estados, tolva con rampa, servo y consola serie.

### Fallos y correcciones

| # | Fallo | Causa | Corrección | Estado |
|---|---|---|---|---|
| H1 | La moneda cae por detrás del disco | Hueco detrás del punto de caída | Tope trasero H04 (40 × 10 × 3) | Impreso, en prueba |
| H2 | $200 y $500 se atascan; la $1.000 no entra | Bolsillos Ø29 sin holgura para las grandes | Disco H02e de 5 bolsillos Ø40; firmware a 5 bolsillos | Impreso, en prueba |
| H3 | El disco se traba | Fricción con el portadisco sin alisar y par bajo del 28BYJ-48 | Lijado, lubricante seco, holgura axial, bajar `TOLVA_VMAX` `[CAL-09]` | En curso |
| H4 | La moneda se cuela por la paleta antes de abrir | Huecos entre la paleta G02 y el embudo | Paleta plana G03 pegada sobre G02 | Impresa, en prueba |
| H5 | Monedas de canto que no se acuestan con la tolva llena | El rascador H03 queda alto para ellas | Nervios bajos en el plato, más vaivén del disco, menos carga | Abierto |
| H6 | No se probaron las barreras IR ni el TCS3200 | Jumpers cortos | Jumpers largos y cables agrupados por sensor | Recableado |

### Lo que falta para cerrar la etapa

Calibración física `[CAL-01]` a `[CAL-12]` (procedimiento en [TODO.md](../TODO.md#fase-4--montaje-y-calibración-física))
y la prueba de 100 monedas revueltas, con meta ≥ 90 % bien clasificadas.

---

## Etapa 2 · Banda transportadora

### Qué funciona

- El motor fijo con piñón mueve la barra dentada de 810 mm y la barra arrastra el carro con el
  cartucho de 9 vasos por todo el riel, de punta a punta.
- La electrónica (A4988 en la protoboard, NEMA17 a 12 V) está conectada al ESP32-S3 de la etapa 1.

### Fallos y correcciones

| # | Fallo | Causa | Corrección | Estado |
|---|---|---|---|---|
| B1 | El NEMA17 se desplaza en su soporte al arrancar y frenar | La reacción del empuje del piñón (hasta 33 N con el par máximo) la toma solo el encaje del motor en el soporte, sin sujeción | Brida por las ranuras del soporte, base del soporte pegada a la mesa; rampa más suave en el firmware 0.9.0 (8.000 pasos/s²) | Firmware hecho; sujeción por hacer |
| B2 | El piñón resbala en el eje del motor y la barra pierde pasos | El agujero en D impreso queda holgado sobre el plano del eje; el piñón de 3 g no tiene prisionero | Gota de cianoacrilato en el plano de la D, o piñón con agujero 0,1 mm más cerrado y cubo con prisionero M3 | Por hacer |
| B3 | La banda no se movía con el firmware de la etapa 1 | La banda estaba desactivada (`HABILITAR_BANDA 0`) y con la calibración de la banda v3 (33,3 pasos/mm, 40 mm entre vasos) | Firmware 0.9.0: banda activada, 42,44 pasos/mm y 38 mm entre vasos | ✅ Corregido |
| B4 | El cero de la banda depende de dónde quede el cartucho al encender | No hay rutina de referencia con el haz de `PIN_IR_REF` | Rutina de búsqueda del cero: avanzar despacio hasta que el carro corte el haz | Por hacer |

### Lo que falta para cerrar la etapa

Fijar motor y piñón, medir los pasos reales por milímetro (20.000 pasos y medir el avance),
las posiciones de cada vaso con `z<vaso>` `[CAL-11]` y la rutina de cero con el haz.

---

## Etapa 3 · Brazo

El brazo construido es de 4 GDL con doble paralelogramo: J1, J2 y J3 con NEMA17 y reductora
planetaria impresa 16:1, cabeceo y pinza con SG90, y su propia ESP32. Medidas, integración con las
etapas 1 y 2, diferencias con el modelo simulado, plan y riesgos en
[13-etapa3-brazo.md](13-etapa3-brazo.md).

### Qué está hecho

- Brazo diseñado (25 STL, garra en SolidWorks, reductora) y firmware de calibración con interfaz web
  ([`hardware/etapa3-brazo/`](../hardware/etapa3-brazo)).
- Planificador de la ruta del punto A al rack entre los cuatro obstáculos, probado en Python y en la
  página web con la misma respuesta ([08-obstaculos.md](08-obstaculos.md)), y app Streamlit con
  dashboard y asistente ([`software/apps/`](../software/apps)). Se hicieron con el modelo simulado de
  5 servos y se están pasando al brazo real.

### Riesgos abiertos

| Riesgo | Causa | Corrección propuesta |
|---|---|---|
| La pinza no sostiene un vaso lleno | El SG90 da ≈ 1,8 kg·cm y un vaso con 40 monedas pesa ≈ 430 g | Limitar la carga por vaso o reforzar la pinza con almohadillas de TPU |
| Agarre distinto al simulado | La garra del brazo real queda siempre horizontal | Agarre lateral del vaso y rack recalculado para el arco real |
| Ceros de los ejes a mano | No hay finales de carrera | Interfaz de calibración y medir la repetibilidad antes de fijar los puestos del rack |

---

## Integración

| Enlace | Estado |
|---|---|
| Clasificador → banda (mismo ESP32-S3) | ✅ En el firmware: el secuenciador mueve la banda al vaso de cada moneda |
| Clasificador → brazo (`POST /api/vasos`) | ✅ En simulación y en el PC; ⏳ sin probar entre las dos placas |
| App ↔ ESP32 por Wi-Fi | ✅ En modo simulación; ⏳ sin probar con las placas |
