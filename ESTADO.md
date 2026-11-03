# ESTADO

## Etapas
| Etapa | Estado |
|---|---|
| 1 Tolva + selección | **v5** diseño completo y **todas las camas impresas**; en montaje y calibración. Firmware de operación `firmware/etapa1_clasificador/` (0.8.0, PR #7 fusionado) |
| 2 Banda transportadora | Cadena de tablillas impresa, PR #5 abierto |
| 3 Brazo A→B + orden | Recibe 9 vasos (9+9 puestos); simulado, firmware probado en PC (61 pytest, 48 C++); falta montar |

## Repositorio ordenado (0.9.1) — 2026-11-03
- Mapa completo: `docs/MAPA-DEL-REPOSITORIO.md`. Versiones viejas en carpetas `archivo/` con README: `scripts/archivo/`, `firmware/archivo/esp32_contador_v4/`, `docs/archivo/` (visores v1 y v4), `sim/mujoco/descartados/`, `hardware/archivo/`.
- `scripts/generar_clasificador.py` sigue en `scripts/` porque `generar_v5.py` importa `escribir_stl`.

## Pruebas físicas 1ª ronda (0.9.0) — 2026-11-03
- `docs/12-pruebas-fisicas-etapa1.md` + `docs/pruebas/etapa1/{video,img}`. OK: $100 y $500 antiguas, cartucho/vasos, torre armada.
- H1 caída por detrás → rampa trasera. H2 bolsillos justos ($200/$500 n atascan, $1000 no entra) → disco 6 bolsillos + firmware 6/vuelta. H3 fricción disco → lijar, lubricante seco, nervios, bajar VMAX. H4 moneda se cuela en compuerta → 2ª paleta. H5 monedas verticales no se acuestan con tolva llena → abierto. H6 jumpers cortos → IR y TCS3200 sin probar.

## Firmware clasificador (0.8.0, PR #7) — 2026-10-31
- `firmware/etapa1_clasificador/`: lib portable (Clasificador, Calibrador, Secuenciador/Planta) + `src/hal` (ISR barreras timer 4 kHz+ADC o flanco, PCNT TCS3200, tolva núcleo 0, SG90, botón GPIO 9). CI compila esp32s3 (RAM 6,5 %, flash 9,8 %) + 16 Unity native.
- Medición: D = h + c²/4h, h=10, SEP 24, MRUA 3 ecuaciones; tolerancia/clase min(0,60; vecino/2−0,05); dorado (R+G)/2B>1,30 → N500; A50 dorada → rechazo (A1000 1996).
- Calibración física: `[CAL-01..12]` en `include/`; procedimiento en `TODO.md` fase 4.
- Resuelto en CI: macro `B1` de Arduino (enum → Primera/Segunda); IRAM_ATTR en header → `l32r` (ISR a `Boton.cpp`).
- Pages: `docs/clasificador-v5.html`, `docs/banda-etapa2.html` (visibles al fusionar en main).
- 2026-10-31: impresión completa (8 camas). Docs sin "pendiente" de impresión ni compras (0.8.1).
- Siguiente: armar; cablear; cargar firmware; calibrar.

## Etapa 1 v5 (vigente, 0.7.0)
- Piezas: `scripts/generar_v5.py --ensamble` → `hardware/etapa1-clasificador/{stl,despiece.csv,ensamble*}`; camas `scripts/armar_camas_v5.py` → `impresion/` (CAMAS.md, orden "sin electrónica primero").
- Docs: `docs/09-clasificador-v5.md`, `docs/11-electronica-etapa1.md` (+ `img/etapa1-cableado.svg`, `img/etapa1-v5.png`).
- Pines S3: tolva 4,5,6,7; SG90 15; IR 1,2 (ADC1); TCS3200 OUT 14, S2 16, S3 17, S0 18, S1 21; banda STEP 10/DIR 11/EN 12, ref 13.
- Pendiente: armar, probar motor con carga, calibrar `[CAL-xx]` (firmware 0.8.0), confirmar shield; `Ajustes.3mf` (perfil propio de la K1C) no está en el repo.
- Archivo: v4 → `hardware/archivo/etapa1-v4/`, probetas v3 → `hardware/archivo/etapa1-v3-canto/`, docs v4 → `docs/archivo/*-v4.md`. `firmware/archivo/esp32_contador_v4` es de la v4 (lo usan las pruebas).

## Histórico v4 (archivado)
### Decisiones / parámetros v4
- Generador único `scripts/generar_clasificador.py` (manifold3d) → `hardware/etapa1-clasificador/stl/`; visor `scripts/archivo/exportar_visor_3d.py` → `docs/archivo/ensamble-etapa1-v4.html`.
- Sin tornillos ni soportes: clavijas Ø6 (agujero 6,1; `AJUSTE_PRESION`), llaves R04, bridas.
- Riel 22°, ranuras 17,5/20,8/22,0/22,8/23,4/24,1/24,9 + extremo (diámetros oficiales Banrep). 9 salidas ≥ 37 mm → 9 vasos Ø34×60, uno por tipo.
- $500: TCS34725 antes de ranura 6; plato D6 SG90 55° antigua / 125° nueva.
- Ductos: adaptador impreso + PVC 1" RDE 21 (cortes 196/181/167/152/128/85/69). Base: MDF 9 mm 560×198, PVC 3/4" (4×134, 4×29, 2×490) + 4 tees + 2 P01 ABS. Hueco banda 123×490, 70 mm bajo banda.
- Pines: IR 34,35,36,39,32,33,25,26,27; I2C 21/22; servo 13; tolva 16-19; banda 14/4/23.
- Impresión: 8 camas, ≈480 g (PLA+ negro 230, PETG azul 180, ABS 75), ≈33 h.

## Archivos (0.5.0)
- Repo por etapa: `hardware/{etapa1-clasificador,etapa2-transporte,etapa3-brazo,archivo/etapa1-v1}`, `hardware/README.md`.
- Docs: `09-clasificador-fisico.md`, `10-guia-armado-etapa1.md`, `archivo/despiece-etapa1-v1.md`, `ensamble-etapa1.html`; README, 00-entrega, index.html, CHANGELOG.
- `bom-etapa1.csv` rehecho; `software/tests/test_monedas.py` (9 ductos vs 8 estaciones).

## Etapa 1 v5 (prototipo final) lista para imprimir
- Torre de 33 cm de pie sobre la banda (3 caballetes + patines). Tolva de disco inclinado 45° (28BYJ-48, 8 bolsillos, rascador) → la moneda cae de canto a la pista (sim 1728/1728, `sim/mujoco/disco.py`) → 2 barreras IR + TCS34725 → embudo Ø90 a 45° (sim 81/81) → compuerta SG90 con bisagra → cartucho de 9 vasos que mueve la banda. Rechazo: rampa C02 en la punta del cartucho a un vaso puesto a mano.
- Piezas: `scripts/generar_v5.py` → `hardware/etapa1-clasificador/v5/` (STL, despiece, guía de armado). Sin choques, todo cabe en la K1C, ~850 g.
- No validado: una sola moneda por bolsillo, compuerta, posición del cartucho (depende de la banda, etapa 2), sensores reales. Meta 90%.

## Resuelto
- $500 alineada, STL cerrados, PVC en ductos y base, sin choques.
- Prueba firmware↔modelo de monedas fallando desde 0.4.0 → corregida.

## Pendiente / riesgos
- Probar la $1000 en el tubo de 1" antes de cortar (SCH 40 atasca). Medir la tee real (`F_ACC` 11 mm).
- Calibrar `COMPENSACION_RANURA`, `umbralDorado`; vasos Ø34 con 0,8 mm de holgura entre D5 y D6a.
- **Reimprimir R01** si ya se imprimió con la ranura 3 de 21,5 mm: la $50 antigua mide 21,5 y no caía (ahora 22,0; ranura 4 a 22,8).
- PyBullet no se ejecutó (no compila aquí): correr `python sim/pybullet/run_sim_integrada.py --headless` en el PC.
- Rack de 9 puestos con vasos Ø34 a 9,5°: solo 4 mm libres entre vasos; el brazo del CAD (r_arco 9,7 cm) no los alcanza en su arco.
- `MONEDAS_POR_VASO = 40` es carga de diseño (416 g); un vaso Ø34×60 admite ≈ 26 monedas de $1.000.
- `docs/memoria-calculo.html` aún muestra las cifras del perfil de 5 vasos (lleva aviso).
- Confirmar diámetros de $50 y $500 antiguas con moneda real (ahora los oficiales: 21,5 / 23,7 mm; 7,14 g).

## Siguiente paso
Imprimir camas 1 y 2 de prueba (R01, patas R03_1, D1 adaptador, D6, B02, B03) y medir; en paralelo, diseñar la banda.

## Etapa 1: montaje y primeras pruebas — 2026-11-02
- Camas impresas; falta solo A01 (adaptador TCS3200, corte de L01 + cianoacrilato; B01/B03 de `archivo/` obsoletos). Sensor vigente = TCS3200.
- Firmware de banco que arranca en la placa (COM8/UART0, Arduino-ESP32 3.x, LEDC servo, `pulse_cnt`) subido a `firmware/etapa1_prueba_motor/`; el del repo era la versión vieja que colgaba. `platformio.ini` apunta a pioarduino.
- Guía: `hardware/etapa1-clasificador/GUIA-MONTAJE-PRUEBAS.md` (armado, cableado, pio, pruebas f/b, t, o/p, m, d/a).
- Pendiente: operación (`etapa1_clasificador`) usa espressif32 6.x + CDC_ON_BOOT: adaptar a UART0/pioarduino tras validar banco; cablear; calibrar [CAL-xx] con monedas reales.
- Siguiente: imprimir A01, cablear, `pio run -t upload`, probar `f`, `m`, `o/p`.
- 2026-11-03 usuario: $200 antigua (Ø24,4×1,7) atasca el disco y algunas monedas caen en la subida (H01 queda algo inclinado). Hecho: `scripts/generar_ajustes_tolva.py` → `stl/ajustes/` H02b (bolsillo Ø30 + chaflán 0,5) y H04 (cuña de apoyo H01↔L01, 45 cm³). Sin probar con monedas.
- Confirmado usuario: 9 vasos OK (50×2, 100×2, 200×2, 500×2, 1000×1) + vaso de rechazo = 10. La entrada A1000 (21,67 mm) de `monedas.py` no existe como moneda real (solo se rechazaba); no cambia vasos ni firmware. Grosores reales: $50 N 1,3; $100 N 1,5; $200 N 1,6; $500 N 2,2; $1000 2,7; antiguas $50 Ø21,0×1,3; $100 Ø23,0×1,5; $200 24,4×1,7; $500 Ø23,5×2,0.
- Siguiente: probar H02b/H04 con monedas reales.
- 2026-11-03 banco en modo continuo: `AUTO_AL_ARRANCAR 1`, `PARAR_SI_VACIA 0`, espera por bolsillo 1200 ms (config.h/main.cpp de `etapa1_prueba_motor`). Sin compilar aquí; probar en placa. Siguiente: subir y ver ciclo con monedas.
- 2026-11-03 banco subido a la placa desde el PC (COM8, pio ok). Motor: `GIRO_AL_ARRANCAR 1` gira continuo sin sensores (`g` alterna, `v<pps>` velocidad); `AUTO_AL_ARRANCAR 0`. BUG pendiente: barreras IR leen ~30/4095 (base 26) = sin cablear/LED IR apagado; GPIO13 flota (banda sin montar). Siguiente: cablear barreras, `m`, luego `a`.
- 2026-11-03 (ronda 1 de pruebas) retirada la cuña H04 (bloqueaba el pasillo H01↔L01) y H02b. Nuevo `stl/ajustes/H02c_disco_6_bolsillos.stl`: 6 bolsillos Ø33, radio 50, 6 radios de apoyo 0,4 mm, bolsillo a 90°; 0 choques con H01/H03. `BOLSILLOS=6` (operación y banco), vacíos=6. 2ª paleta: reimprimir G02. Pendiente: rampa trasera H1 (confirmar por dónde se escapa la moneda), H5 monedas verticales. Siguiente: imprimir H02c, probar con las 7 monedas.
