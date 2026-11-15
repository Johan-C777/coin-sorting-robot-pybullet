# Guía de montaje, cableado y primera prueba · etapa 1

Orden: **A** sensor → **B** armado → **C** cableado → **D** firmware → **E** pruebas.
Pines: [`pines.h`](../../firmware/etapa1_clasificador/include/pines.h) = [`conexiones.csv`](esquematico/conexiones.csv).

## A. Pieza del sensor actual (TCS3200)

No se reimprime L01. Solo se imprime **A01** (`stl/A01_adaptador_tcs3200.stl`, PLA+ negro, de lado, soportes mínimos) y:

1. Corta a ras de la repisa (z = 6 mm) el bloque que sostenía el TCS34725; queda un muñón de 22 × 5,5 mm.
2. Pega A01 sobre el muñón con cianoacrilato (se centra con patillas y faldón).
3. Mete la placa TCS3200 desde arriba por los rieles: LED hacia la pista, cabecera arriba.
4. Comprueba que la placa mide 28,5 mm (supuesto de A01); si no entra, lima el bolsillo.

(`B01/B03_*tcs*` de `archivo/` son del diseño viejo: no se usan.)

## B. Armado en seco (sin pegar, sin motor)

Sigue los pasos 1-9 de [README.md](README.md#armado-sin-tornillos). Orden recomendado:
marco (T01/S01/S02/R01/R02) → K01/K02 → pista L01 + B01 → tolva H01 + disco H02 + H03a → embudo F01/F02 → compuerta G01/G02 → cartucho.
Antes de pegar nada, comprueba con una moneda: una sola por bolsillo, cae de canto y rueda por la pista.

## C. Cableado

Regla: **primero tierras, luego 5 V medidos con multímetro, y el ESP32 al final.** GND de la fuente 5 V unido al GND del ESP32.

| Elemento | Conexión |
|---|---|
| ULN2003 / 28BYJ-48 | IN1-IN4 → GPIO **4, 5, 6, 7**; + a 5 V externos; GND común |
| SG90 | señal (naranja) → GPIO **15**; rojo a 5 V externos; café a GND; 220 µF entre V+ y GND junto al servo |
| Barrera 1 (a 105 mm) | LED IR: 5 V → 330 Ω → ánodo, cátodo a GND. Fototransistor: C → 3V3, E → GPIO **1** y de E a GND 10 kΩ |
| Barrera 2 (a 129 mm) | igual, E → GPIO **2** |
| TCS3200 | VCC → 3V3; GND y **OE** → GND; OUT → GPIO **14**; S2 → **16**; S3 → **17**; S0 → **18**; S1 → **21** |
| Banda (etapa 2) | no conectar aún (STEP 10, DIR 11, EN 12, haz ref 13) |

Fototransistor: la pata larga (emisor en la mayoría) va al GPIO + 10 kΩ; si lees siempre 0 o siempre 4095, invierte C y E.
El LED IR se ve con la cámara del celular (luz violeta).

## D. Subir el firmware (PlatformIO)

Usa el firmware de banco `firmware/etapa1_prueba_motor/` (el que ya arrancó en tu placa por **COM8**, UART0).
Necesita Arduino-ESP32 3.x: el `platformio.ini` ya apunta a pioarduino.

```
cd firmware/etapa1_prueba_motor
pio run -t upload          # sube
pio device monitor         # consola 115200
```

- Puerto UART (CH343, el que usas): no cambies nada. Puerto USB nativo: añade `-DARDUINO_USB_CDC_ON_BOOT=1`.
- Si no sube: mantén BOOT, pulsa RST, suelta BOOT. No lances dos `pio run` a la vez (dañan `tool-esptoolpy`).
- Al arrancar debe imprimir `tolva ok · servo ok · IR base … · tcs ok · tarea pasos ok`. Si se cuelga antes de `tcs ok`, revisa que sea pioarduino (no espressif32 6.x).
- El firmware de operación (`firmware/etapa1_clasificador/`) usa espressif32 6.x y `ARDUINO_USB_CDC_ON_BOOT=1`; para tu placa por UART hay que quitar esa bandera. Se usa **después** de estas pruebas.

## E. Pruebas en orden (consola; `?` = ayuda)

1. **Motor tolva.** `f` avanza un bolsillo, `b` retrocede. Si gira al revés: `TOLVA_SENTIDO = -1` en `config.h`. Si vibra sin girar: baja `s` (v0) a 120 o revisa el orden IN1-IN4.
2. **Velocidad.** Con la tolva cargada, `t` (barrido de 400 a 1400 pps). Usa ~75 % de la última velocidad sin perder pasos con `v<pps>`.
3. **Servo.** `o` abre, `p` cierra. Ajusta `SERVO_ABIERTA/SERVO_CERRADA` en `config.h`; monta el brazo con la compuerta horizontal en `p`.
4. **Barreras IR.** `m` imprime `IR1=lectura/base IR2=… REF=… TCS razon=… total=…` cada 200 ms. Pasa una moneda por cada haz: la lectura debe caer por debajo del 50 % de la base. Si no cambia, revisa LED IR (celular) y polaridad del fototransistor.
5. **TCS3200.** Con `m`, `total` debe ser > 0 y cambiar al tapar el sensor. Moneda dorada ($500 nueva) frente a A01: `razon` > 1,30; plateada < 1,30. Ajusta `UMBRAL_DORADO`.
6. **Ciclo completo.** `d` = una moneda (avanza, mide, abre compuerta); `a` = automático; `r` = resumen. Calibra con la fase 4 de [`TODO.md`](../../TODO.md).

Reporta aquí cualquier línea rara de la consola y se ajusta; no se inventan valores sin monedas reales.

## F. Ajustes tras la primera ronda de pruebas (`stl/ajustes/`, generador `scripts/generar_ajustes_tolva.py`)

- **H02c** disco de **6 bolsillos Ø33** (antes 8 de Ø29), con un bolsillo en la posición de salida y radio 50. Cara trasera plana como el H02 anterior, sin soportes. Mismo eje y grosor; sirve con H01 y con H03a/b/c (para la $1.000 usa H03c, 2,8 mm). El firmware pasa a `BOLSILLOS = 6`.
- **H04 tope trasero:** rectángulo extruido de 40 × 10 × 3 mm. Se pega con cianoacrilato sobre la placa de L01, centrado sobre el hueco de salida y a 48 mm sobre la repisa, para que la moneda que rebota hacia arriba no salga por la cuña abierta entre L01 y el aro de H01.
- **G03 paleta plana:** rectángulo extruido de 34 × 34 × 2,5 mm (las medidas de G02, sin bisagra, cubo ni rebaje del servo) para pegar encima de G02 y tapar los huecos.
- Sin probar con monedas reales.
