# Estado final de las tres etapas

Cierre del proyecto a noviembre de 2026: arquitectura final, qué se construyó y probó en cada
etapa, los ajustes que salieron de las pruebas y las mejoras previstas para la siguiente
iteración. Los números de desempeño que no salen de una prueba física se marcan como simulación.

## Arquitectura final: cada etapa con su controlador

| Etapa | Controlador | Actuadores | Enlace |
|---|---|---|---|
| **1 · Clasificador** | ESP32-S3-DevKitC-1 | Tolva 28BYJ-48 (ULN2003), compuerta SG90, barreras IR, TCS3200 | Consola serie (USB-UART CH343) |
| **2 · Banda** | RAMBo con Marlin 2.1.2.5 | NEMA17 en el driver X (42,44 pasos/mm), corriente fijada por software | G-code por USB |
| **3 · Brazo** | ESP32 propia | NEMA17 con drivers TB6560/TB6600 y reductora 16:1, dos SG90 | Independiente ([13-etapa3-brazo.md](13-etapa3-brazo.md)) |

La etapa 1 decide el vaso de cada moneda y pide la posición de la banda. Esa orden sale por la
consola de la ESP32-S3 como una línea de G-code con el prefijo `@`, y el
[panel de control web](panel-control.html) la reenvía a la RAMBo y le devuelve el `ok` cuando el
movimiento termina (`M400`). Así la compuerta solo abre con el vaso ya quieto bajo el embudo.

```
ESP32-S3 (etapa 1) ──USB──► PC: panel web ──USB──► RAMBo (etapa 2)
     "@G1 X38 F3500"            reenvía                 mueve la banda
     "@M400"                                            responde "ok"
       ◄────────────────────── "@ok" ◄────────────────────┘
```

El firmware conserva además la opción de enlace directo por UART1 (GPIO 41/42 con divisor a
3,3 V) y la del A4988 en la misma ESP32-S3 (entornos `esp32s3_rambo` y `esp32s3`).

## Panel de control web

[`docs/panel-control.html`](panel-control.html) se abre en Chrome o Edge y se conecta por Web
Serial a la ESP32-S3 y a la RAMBo. Desde ahí se maneja todo con botones:

- Ciclo automático, un ciclo, paro y rearme, con el estado de la máquina en vivo.
- Tolva (bolsillo adelante y atrás, velocidad y rampa) y compuerta con ángulo ajustable.
- Barreras IR y color del TCS3200 en vivo, conteo por vaso y tabla de las últimas monedas.
- Banda: cada vaso, la rampa de rechazo, barra de posición en milímetros y pasos, avance fino de
  ±1 y ±10 mm, cero y liberación del motor.
- Calibración de la medición y del umbral de color, guardado en flash.

## Resumen

| Etapa | Diseño | Construcción | Electrónica y firmware | Prueba física |
|---|---|---|---|---|
| **1 · Clasificador** | ✅ CAD paramétrico v5, 24 piezas sin tornillos ni soportes | ✅ Impresa y armada, con la segunda ronda de piezas ajustadas | ✅ ESP32-S3, firmware 0.9.0, 16 pruebas automáticas y compilación en CI | ✅ Tolva, pista y compuerta con monedas reales ([12](12-pruebas-fisicas-etapa1.md)); sensor de color verificado en el montaje |
| **2 · Banda** | ✅ v7 motor fijo con barra dentada, 0 choques en 130 posiciones | ✅ Impresa (13 piezas, ≈ 372 g) y montada | ✅ RAMBo con Marlin; posición de cada vaso pedida desde la etapa 1 | ✅ Lleva el cartucho bajo la torre ([video](pruebas/etapa2/video/banda_mueve_cartucho.mp4)) |
| **3 · Brazo** | ✅ 4 GDL de doble paralelogramo, reductora 16:1 | ✅ Impreso y armado | ✅ ESP32 propia y drivers TB6560/TB6600 | ✅ Toma un vaso del cartucho ([13](13-etapa3-brazo.md)) |

---

## Etapa 1 · Clasificador

### Qué se verificó

- La tolva de disco separa las monedas una a una y las deja en la pista L01.
- Las monedas ruedan de canto por la pista hasta la compuerta, y la compuerta las deja en el vaso.
- El TCS3200 entrega lecturas estables de los tres filtros y responde a la escala de frecuencia.
- El firmware corre en la ESP32-S3: secuenciador de 11 estados, tolva con rampa, servo y consola.
- Diagnóstico de cableado pin por pin (programa aparte) para revisar cada sensor y actuador
  antes de la operación.

### Ajustes realizados con las pruebas

| Ajuste | Motivo | Solución |
|---|---|---|
| Tope trasero H04 | Retener la moneda justo en el punto de caída del disco | Pieza de 40 × 10 × 3 mm |
| Disco H02e de 5 bolsillos Ø40 | Dar holgura a las monedas de $200, $500 y $1.000 | Disco nuevo y firmware a 5 bolsillos |
| Portadisco | Bajar la fricción para el par del 28BYJ-48 | Lijado, lubricante seco, holgura axial y `TOLVA_VMAX` `[CAL-09]` |
| Paleta plana G03 | Cerrar el paso entre la paleta y el embudo | Paleta pegada sobre G02 |
| Medición con un solo haz | Poder operar con una sola barrera IR | Modo `UNA_BARRERA`: velocidad constante calibrada con una moneda conocida (`q<vaso>`) |

### Mejoras para la siguiente iteración

- Nervios bajos en el plato de la tolva para acostar las monedas que llegan de canto.
- Barreras IR en una placa perforada con el LED y el fototransistor fijos y alineados.
- Calibración física `[CAL-01]` a `[CAL-13]` y prueba de 100 monedas revueltas, con meta ≥ 90 %
  bien clasificadas ([procedimiento](../TODO.md#fase-4--montaje-y-pruebas-físicas)).

---

## Etapa 2 · Banda transportadora

### Qué se verificó

- El motor fijo con piñón mueve la barra dentada de 810 mm, y la barra arrastra el carro con el
  cartucho de 9 vasos a lo largo del riel, bajo la torre
  ([video](pruebas/etapa2/video/banda_mueve_cartucho.mp4)).
- La ESP32-S3 pide cada posición, la RAMBo la ejecuta y confirma (`G1 X38` y `G1 X0` con su `ok`).

### Decisiones de diseño

| Decisión | Motivo |
|---|---|
| Driver de la RAMBo en lugar del A4988 en protoboard | Corriente ajustada por software (`M907`), conexiones firmes y rampa de aceleración de Marlin |
| Marlin como controlador de movimiento | Planificador de trayectoria probado, `M400` para sincronizar con la compuerta y G-code legible |
| Motor fijo y barra dentada (v7) | Sin cables en movimiento y posición repetible sin estiramiento de hilo |
| Cero de la banda al encender con el vaso 9 bajo el embudo | Arranque simple, sin final de carrera |

### Mejoras para la siguiente iteración

- Prisionero M3 en el cubo del piñón y brida de sujeción del soporte del motor.
- Búsqueda automática del cero con el haz de referencia (`PIN_IR_REF`).
- Medir los pasos reales por milímetro y las posiciones de cada vaso `[CAL-11]`.

---

## Etapa 3 · Brazo

Brazo de 4 GDL con controlador propio (ESP32 y drivers TB6560/TB6600), NEMA17 con reductora
planetaria impresa 16:1 en J1 a J3 y dos SG90. Mecánica, cálculos, cinemática, control y pruebas
en [13-etapa3-brazo.md](13-etapa3-brazo.md).

---

## Integración

| Enlace | Estado |
|---|---|
| Clasificador → banda | ✅ La ESP32-S3 pide el vaso de cada moneda y la RAMBo lo posiciona (puente por el panel web, probado) |
| Banda → brazo | ✅ El cartucho queda en el punto A, donde el brazo toma el vaso |
| Clasificador → brazo (`POST /api/vasos`) | ✅ En simulación y en el PC |
