# Plan de trabajo · Módulo clasificador de monedas (etapa 1)

Estado final, 24 de noviembre de 2026. Cada casilla marcada tiene detrás un archivo del
repositorio, una prueba automática o un video que la respalda.

**Resumen:** el diseño mecánico, el cálculo de la medición, la electrónica y el firmware
están completos y verificados en simulación y en el PC; la torre está impresa, armada,
cableada y probada con monedas reales, y los ajustes de diseño de esas pruebas están
impresos y montados. La banda y el brazo están montados y en movimiento. El procedimiento
de calibración fina queda documentado parámetro por parámetro para la operación.

| Fase | Avance |
|---|---|
| 1. Requisitos y diseño de la medición | ██████████ 100 % |
| 2. CAD e impresión | ██████████ 100 % |
| 3. Electrónica y firmware | ██████████ 100 % |
| 4. Montaje y pruebas físicas | ██████████ 100 % |
| 5. Banda y brazo | ██████████ 100 % montados y en movimiento |

---

## Fase 1 · Requisitos y diseño de la medición

- [x] Catálogo de las 9 monedas en circulación (dos familias) con diámetros oficiales del
      Banco de la República → [`software/brazo/monedas.py`](software/brazo/monedas.py)
- [x] Decisión: medir el diámetro por tiempo de vuelo con 2 barreras IR en lugar de una
      ranura por moneda (v4) → [09-clasificador-v5.md](docs/09-clasificador-v5.md)
- [x] Modelo de medición con aceleración constante y cuerda a la altura del haz
      (D = h + c²/4h) → [README del firmware](firmware/etapa1_clasificador/README.md#medición-del-diámetro)
- [x] Tolerancia por clase sin solapes (mínima 0,25 mm entre la $200 nueva y la $100 antigua)
- [x] Separación de las dos $500 (mismo diámetro) por color con TCS3200
- [x] La $1.000 de 1996 (21,67 mm, casi igual que la $50 antigua) se rechaza por color
- [x] Simulación MuJoCo: disco 1.728/1.728 de canto, embudo 81/81, error de medición 0,03 mm
      → [`sim/mujoco/`](sim/mujoco)

## Fase 2 · CAD e impresión

- [x] Torre v5 paramétrica: 24 STL sin tornillos ni soportes, 0 choques, ≈ 845 g
      → [`scripts/generar_v5.py`](scripts/generar_v5.py), [`hardware/etapa1-clasificador/stl/`](hardware/etapa1-clasificador/stl)
- [x] 8 camas `.3mf` para la Creality K1C con material por cama
      → [`impresion/CAMAS.md`](hardware/etapa1-clasificador/impresion/CAMAS.md)
- [x] Adaptador A01 para el TCS3200 sobre la pista L01
- [x] Despiece, compras y guía de armado → [`hardware/etapa1-clasificador/`](hardware/etapa1-clasificador)
- [x] Todas las camas impresas: tolva, disco, rascadores, pista, soportes, embudo, marco,
      vasos, cartuchos y compuerta

## Fase 3 · Electrónica y firmware

- [x] Mapa de pines del ESP32-S3 sin pines reservados (verificado por prueba automática)
      → [`include/pines.h`](firmware/etapa1_clasificador/include/pines.h)
- [x] Esquema de conexiones y presupuesto de potencia → [`esquematico/`](hardware/etapa1-clasificador/esquematico)
- [x] Firmware de banco para motores y sensores → [`firmware/etapa1_prueba_motor/`](firmware/etapa1_prueba_motor)
- [x] Firmware de operación en PlatformIO por capas → [`firmware/etapa1_clasificador/`](firmware/etapa1_clasificador)
  - [x] Máquina de estados no bloqueante (11 estados, desatasco, tolva vacía, vaso lleno, paro)
  - [x] Barreras por interrupción (timer + ADC o flanco GPIO) con marca de tiempo en la ISR
  - [x] TCS3200 por contador de pulsos PCNT
  - [x] Tolva con rampa trapezoidal en tarea del núcleo 0
  - [x] Calibración por mínimos cuadrados desde la consola y persistencia en NVS
  - [x] Tramas `M:`, `R:` y `VASOS:` compatibles con el brazo
  - [x] 16 pruebas unitarias Unity en el PC y compilación para ESP32-S3 en CI

## Fase 4 · Montaje y pruebas físicas

- [x] Armar la torre según [la guía](hardware/etapa1-clasificador/README.md) → [foto](docs/12-pruebas-fisicas-etapa1.md#montaje-general)
- [x] Cablear según [`conexiones.csv`](hardware/etapa1-clasificador/esquematico/conexiones.csv) y cargar el firmware
- [x] Pruebas mecánicas con monedas reales: 13 evidencias y 6 ajustes de diseño
      → [12-pruebas-fisicas-etapa1.md](docs/12-pruebas-fisicas-etapa1.md)
- [x] Ajustes de diseño impresos y montados: disco de 5 bolsillos Ø40 ([`H02e`](hardware/etapa1-clasificador/stl/ajustes))
      con el firmware a 5 bolsillos, tope trasero H04 y paleta plana G03 en la compuerta
- [x] Consola de operación y [panel de control web](https://johan-c777.github.io/coin-sorting-robot-pybullet/panel-control.html)

**Procedimiento de calibración** (cada paso indica la etiqueta del parámetro en
`firmware/etapa1_clasificador/include/`)

1. **[CAL-09]** Barrido `t` de la tolva cargada; fijar `TOLVA_VMAX` al 75 % del límite
2. **[CAL-10]** Ángulos de la compuerta con `w<grados>`; tiempo de apertura
3. **[CAL-08] [CAL-07]** Monitor `m`: niveles de las barreras con y sin moneda; modo ADC o digital
4. **[CAL-01]** Separación real entre los haces en L01
5. **[CAL-02] [CAL-03]** `c<vaso>` con ≥ 3 monedas de ≥ 3 tipos, `C`, `g`: altura y ancho del haz
6. **[CAL-05]** Umbral de dorado con una $500 antigua y una nueva frente a A01
7. **[CAL-06]** Rangos de velocidad y aceleración con las líneas `#D`
8. **[CAL-12]** Tiempo de llegada a la compuerta (video a cámara lenta)
9. **[CAL-04]** Tolerancia si el error RMS supera 0,10 mm
10. **Aceptación:** 100 monedas revueltas, meta ≥ 90 % bien clasificadas y el resto en rechazo;
    matriz de confusión en [05-pruebas.md](docs/05-pruebas.md)

## Fase 5 · Banda y brazo

- [x] Protocolo de lote `VASOS:` hacia el brazo y su prueba de ida y vuelta
- [x] Simulación del sistema completo en el navegador y en PyBullet
- [x] Banda (etapa 2) v7, motor fijo con barra dentada: impresa, montada y moviendo el cartucho
      → [visor](https://johan-c777.github.io/coin-sorting-robot-pybullet/etapa2/v7-motor-fijo.html),
      [video](docs/pruebas/etapa2/video/banda_mueve_cartucho.mp4)
- [x] Firmware de la banda: 42,44 pasos/mm y 38 mm entre vasos
- [x] Brazo (etapa 3) de 4 GDL impreso y armado, con su ESP32 y drivers; toma y traslada un vaso
      → [13-etapa3-brazo.md](docs/13-etapa3-brazo.md), [video](docs/pruebas/etapa3/video/brazo_toma_vaso.mp4)
- [x] Cinemática del brazo real y visor 3D del ensamble

## Mejoras para una siguiente versión

- Referenciar el cartucho con el haz de `PIN_IR_REF` en lugar del cero al encender.
- Unir los tres controladores en un solo enlace de datos (`VASOS:` por Wi-Fi o UART) para el ciclo
  automático completo y medir su tiempo real frente a la simulación.
- Rascador H03 definitivo y acabado de superficie del portadisco para tolvas muy llenas.
