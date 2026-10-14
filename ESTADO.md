# ESTADO

## Decisiones / parámetros
- Clasificador físico paramétrico: `scripts/generar_clasificador.py` (manifold3d) → `hardware/stl/` + `piezas_clasificador.csv` + `ensamble/`.
- FDM: holgura 0,35; M3 rosca Ø3,2, paso Ø3,4, cabeza Ø6,5×3; IR Ø5,2 + tope Ø3.
- Riel 22°, peralte 10°, canal 30; 2 módulos (201,7 / 180,4 mm) con cola de milano + 2 M3. Ranuras 17,5/20,8/21,5/22,9/23,4/24,1/24,9 + extremo abierto.
- Tolva: semiángulo 40° (de la vertical), disco Ø80×3 con 4 cavidades Ø28; 28BYJ-48 (1019 medios pasos/moneda, 1,5 s) o SG90 continuo.
- Bifurcación $500: rodadura de canto en ranura 4,2 mm a 25°, TCS34725 sobre el anillo, aguja SG90 0° = A500, 45° = N500.
- 9 ductos/IR: N50, N100, A50, N200, A100, A500, N500, A200, N1000. Pines IR 34,35,36,39,32,33,25,26,27 (RISING, pull-up ext. 10 k); I2C 21/22; aguja 13; tolva 16-19; banda 14/4/23.

## Archivos
- Nuevos: `scripts/generar_clasificador.py`, `hardware/stl/*`, `docs/08-clasificador-fisico.md`, `firmware/esp32_contador/{bifurcacion.h,bifurcacion.cpp,color500.h}`.
- Modificados: `firmware/esp32_contador/{config.h,dosificador.*,sensores.*,conteo.h,comms.cpp,esp32_contador.ino}`, `firmware/tests/test_conteo.cpp`, `requirements.txt`, `CHANGELOG.md`.

## Resuelto
- Choque de pines banda (19/21) con tolva/I2C → banda a 14/4/23.
- GPIO36/39 con pulsos falsos por Wi-Fi → `WiFi.setSleep(false)`.
- Verificado: STL válidos y dentro de la cama, sin interferencias en el ensamble, `make -C firmware/tests` OK.

## Pendiente
- Apoyo de 0,10 mm (A100 sobre ranura 4, A500 sobre ranura 5) y 0,20 mm (A50 sobre ranura 2): calibrar `COMPENSACION_RANURA` tras imprimir.
- Calibrar `umbralDorado`, neutro del SG90 continuo y cotas reales del SG90.
- `software/brazo/monedas.py` y la simulación siguen con el riel anterior de 8 estaciones.
- TCS3200 sin driver (solo STL).

## Aligeramiento (v2)
- Conjunto impreso ~445 cm3 macizo (antes ~718). Ducto = tubo recto pared 2 mm + brida minima; riel base 5/pared 2,4; cunas 22x28; bifurcacion de perfil delgado.
- Orientacion auto (giro X cada 5 grados): voladizo 0 en R01, T02; <=120 mm2 en ductos/cuna/base/cono; R02 741 mm2 (puente 14 mm de la cola de milano); B01 1614 mm2 (rampa 25 grados, girada 155 grados).
- Sin interferencias en el ensamble. docs/08 con cifras antiguas: actualizar.

## Siguiente paso
Imprimir R01 + D1 + una cuna, medir ranuras y ajustar COMPENSACION_RANURA; B01 con soporte minimo solo en la rampa.
