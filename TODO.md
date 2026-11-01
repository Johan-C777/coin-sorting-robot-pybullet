# Plan de trabajo · Módulo clasificador de monedas (etapa 1)

Estado al 31 de octubre de 2026. Cada casilla marcada tiene detrás un archivo del
repositorio o una prueba automática que la respalda.

**Resumen:** el diseño mecánico, el cálculo de la medición, la electrónica y el firmware
están completos y verificados en simulación y en el PC, y **todas las piezas están
impresas**. El módulo entra a la fase de montaje: armar la torre, cablear, cargar el
firmware y calibrar con monedas reales siguiendo el procedimiento de la fase 4.

| Fase | Avance |
|---|---|
| 1. Requisitos y diseño de la medición | ██████████ 100 % |
| 2. CAD e impresión | ██████████ 100 % |
| 3. Electrónica y firmware | ██████████ 100 % |
| 4. Montaje y calibración física | ▶ fase actual |
| 5. Integración con banda y brazo | Etapas 2 y 3 del proyecto |

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

## Fase 4 · Montaje y calibración física

Procedimiento de puesta en marcha. Cada paso de calibración indica la etiqueta del
parámetro en `firmware/etapa1_clasificador/include/`.

**Montaje**

- [ ] Medir con calibrador las cotas críticas impresas: agujeros Ø5,2 de L01, bolsillos Ø29
      del disco, bolsillo del SG90 (23,1 × 12,8)
- [ ] Armar la torre según [la guía](hardware/etapa1-clasificador/README.md)
- [ ] Elegir el rascador H03 (2,5 / 2,6 / 2,8 mm) con monedas reales
- [ ] Cablear según [`conexiones.csv`](hardware/etapa1-clasificador/esquematico/conexiones.csv)
      y comprobar que el shield del ESP32-S3 deja libres los pines asignados
- [ ] Cargar el firmware y verificar la consola (`i`, `m`)

**Calibración**

- [ ] **[CAL-09]** Barrido `t` de la tolva cargada; fijar `TOLVA_VMAX` al 75 % del límite
- [ ] **[CAL-10]** Ángulos de la compuerta con `w<grados>`; tiempo de apertura
- [ ] **[CAL-08] [CAL-07]** Monitor `m`: niveles de las barreras con y sin moneda; decidir modo ADC o digital
- [ ] **[CAL-01]** Medir la separación real entre los haces en L01
- [ ] **[CAL-02] [CAL-03]** `c<vaso>` con ≥ 3 monedas de ≥ 3 tipos, `C`, `g`: altura y ancho del haz
- [ ] **[CAL-05]** Umbral de dorado con una $500 antigua y una nueva frente a A01
- [ ] **[CAL-06]** Cerrar los rangos de velocidad y aceleración con las líneas `#D`
- [ ] **[CAL-12]** Tiempo de llegada a la compuerta (video a cámara lenta)
- [ ] **[CAL-04]** Ajustar la tolerancia si el error RMS supera 0,10 mm

**Aceptación**

- [ ] 100 monedas revueltas: meta ≥ 90 % bien clasificadas y el resto en rechazo, sin
      atascos; registrar la matriz de confusión en [05-pruebas.md](docs/05-pruebas.md)

## Fase 5 · Integración con las etapas 2 y 3

- [x] Protocolo de lote `VASOS:` hacia el brazo y su prueba de ida y vuelta
- [x] Simulación del sistema completo en el navegador y en PyBullet
- [x] Banda (etapa 2) propuesta: cadena de tablillas impresa → [visor](https://johan-c777.github.io/coin-sorting-robot-pybullet/banda-etapa2.html)
- [ ] **[CAL-11]** Con la banda montada: `HABILITAR_BANDA 1`, posiciones de los vasos y de la rampa C02
- [ ] Referenciar el cartucho con el haz de `PIN_IR_REF`
- [ ] Enviar `VASOS:` al ESP32 del brazo por Wi-Fi (`POST /api/vasos`)
- [ ] Medir el ciclo real moneda a moneda y compararlo con la simulación
