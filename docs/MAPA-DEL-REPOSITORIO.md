# Mapa del repositorio

Dónde está cada cosa, para encontrarla rápido. Lo marcado como **archivo** son versiones
anteriores que ya no se usan y se guardan como historia del diseño.

## Si el profesor pide…

| Pide | Dónde está |
|---|---|
| El estado del módulo de monedas | [README](../README.md#estado-estratégico) y [TODO.md](../TODO.md) |
| Las pruebas físicas (videos, fotos, fallos) | [12-pruebas-fisicas-etapa1.md](12-pruebas-fisicas-etapa1.md) |
| El diseño de la torre clasificadora | [09-clasificador-v5.md](09-clasificador-v5.md) y el [visor 3D](https://johan-c777.github.io/coin-sorting-robot-pybullet/clasificador-v5.html) |
| Las piezas para imprimir | [`hardware/etapa1-clasificador/stl/`](../hardware/etapa1-clasificador/stl) y las camas en [`impresion/`](../hardware/etapa1-clasificador/impresion) |
| La guía de armado | [`hardware/etapa1-clasificador/README.md`](../hardware/etapa1-clasificador/README.md) |
| La lista de materiales (BOM) | [README, sección BOM](../README.md#lista-de-materiales-bom), [`despiece.csv`](../hardware/etapa1-clasificador/despiece.csv) y [`compras.md`](../hardware/etapa1-clasificador/compras.md) |
| El esquema eléctrico y los pines | [`esquematico/`](../hardware/etapa1-clasificador/esquematico) y [`pines.h`](../firmware/etapa1_clasificador/include/pines.h) |
| El código del clasificador | [`firmware/etapa1_clasificador/`](../firmware/etapa1_clasificador) (máquina de estados en `lib/Secuenciador`, interrupciones en `src/hal/Barreras.cpp`) |
| Los cálculos de la medición del diámetro | [README del firmware](../firmware/etapa1_clasificador/README.md#medición-del-diámetro) |
| Las monedas y sus diámetros | [07-monedas.md](07-monedas.md) y [`software/brazo/monedas.py`](../software/brazo/monedas.py) |
| La cinemática del brazo | [02-cinematica.md](02-cinematica.md) y la [memoria de cálculo](https://johan-c777.github.io/coin-sorting-robot-pybullet/memoria-calculo.html) |
| Los obstáculos de A a B | [08-obstaculos.md](08-obstaculos.md) |
| Las simulaciones | [Sistema completo en el navegador](https://johan-c777.github.io/coin-sorting-robot-pybullet/simulacion_sistema_completo.html), [`sim/pybullet/`](../sim/pybullet) y [`sim/mujoco/`](../sim/mujoco) |
| La app web | [`software/apps/streamlit_app.py`](../software/apps/streamlit_app.py) |
| Que todo compila y pasa pruebas | Pestaña **Actions** de GitHub ([`pruebas.yml`](../.github/workflows/pruebas.yml)) |

## Raíz

| Archivo | Para qué |
|---|---|
| `README.md` | Presentación del proyecto, centrada en el módulo clasificador (etapa 1) |
| `TODO.md` | Plan del módulo por fases: lo hecho y lo que sigue |
| `CHANGELOG.md` | Historial de versiones del repositorio (0.4 a 0.9) |
| `ESTADO.md` | Bitácora corta de decisiones y parámetros |
| `requirements.txt` | Librerías de Python |
| `LICENSE` | Licencia MIT |
| `.github/workflows/pruebas.yml` | Pruebas automáticas en cada cambio |

## `docs/`: documentación y sitio web (GitHub Pages)

| Archivo | Contenido |
|---|---|
| `00-entrega-avances.md` | Qué pidió el segundo parcial y dónde está cada cosa |
| `01-arquitectura.md` | Arquitectura del sistema completo |
| `02-cinematica.md` | Cinemática, trayectorias y cargas del brazo |
| `03-electronica.md` | Electrónica y potencia del brazo |
| `04-protocolo.md` | Tramas entre clasificador, brazo y app |
| `05-pruebas.md` | Pruebas automáticas (Python y C++) |
| `06-medidas-cad.md` | Cotas del brazo construido frente a las del código |
| `07-monedas.md` | Monedas antiguas y nuevas: diámetros y selector |
| `08-obstaculos.md` | Ruta de A a B con cuatro obstáculos |
| `09-clasificador-v5.md` | **Diseño de la torre clasificadora v5 (vigente)** |
| `11-electronica-etapa1.md` | Pines, alimentación y sensores del ESP32-S3 |
| `12-pruebas-fisicas-etapa1.md` | **Pruebas con la torre armada: videos, fotos y hallazgos** |
| `index.html` | Portada del sitio de demos |
| `clasificador-v5.html` | Visor 3D de la torre v5 |
| `banda-etapa2.html` | Visor 3D de la banda (etapa 2) |
| `simulacion_sistema_completo.html` | Simulación del sistema completo |
| `memoria-calculo.html` | Memoria de cálculo del brazo con calculadoras |
| `img/` | Figuras del README y la documentación |
| `pruebas/etapa1/` | Videos (`video/`), fotos, miniaturas y GIF (`img/`) de las pruebas físicas |
| `archivo/` | **Archivo:** documentos y visores de la v1 y la v4 ([qué es cada uno](archivo/README.md)) |

## `firmware/`: código de los microcontroladores

| Carpeta | Contenido | Estado |
|---|---|---|
| `etapa1_clasificador/` | Firmware de operación del clasificador (ESP32-S3, PlatformIO): medición, máquina de estados, interrupciones, calibración, 16 pruebas | **Vigente** |
| `etapa1_prueba_motor/` | Banco de pruebas de motor, sensores y compuerta (ESP32-S3, PlatformIO) | Vigente, para probar piezas sueltas |
| `esp32_brazo/` | Firmware del brazo: cinemática, trayectorias, planificador, PCA9685, Wi-Fi | Vigente (etapa 3) |
| `tests/` | Núcleo de los firmwares compilado y probado en el PC (48 comprobaciones) | Vigente |
| `archivo/esp32_contador_v4/` | **Archivo:** contador de la etapa 1 v4; lo usan las pruebas ([detalle](../firmware/archivo/README.md)) | Archivo |

## `hardware/`: piezas y planos

| Carpeta | Contenido | Estado |
|---|---|---|
| `etapa1-clasificador/stl/` | 24 piezas de la torre v5 y el adaptador del TCS3200 | **Vigente**, impresas |
| `etapa1-clasificador/impresion/` | 8 camas `.3mf` para la Creality K1C y `CAMAS.md` | Vigente |
| `etapa1-clasificador/esquematico/` | Lista de conexiones, diagrama y potencia | Vigente |
| `etapa1-clasificador/` (raíz) | Guía de armado, `despiece.csv`, `compras.md`, ensamble de referencia | Vigente |
| `etapa2-transporte/` | Medidas de interfaz para la banda | En diseño |
| `etapa3-brazo/` | Planos del brazo (PDF de SolidWorks), puesto del rack, bandeja y BOM | Diseñado |
| `materiales.md` | Justificación de materiales del brazo | Vigente |
| `archivo/` | **Archivo:** etapa 1 v1, v3 y v4 ([qué es cada una](../hardware/archivo/README.md)) | Archivo |

## `scripts/`: generadores

| Script | Qué genera |
|---|---|
| `generar_v5.py` | **Las 24 piezas de la torre v5**, el despiece y el ensamble (y revisa choques) |
| `armar_camas_v5.py` | Las camas `.3mf` de impresión |
| `generar_adaptador_tcs3200.py` | El adaptador A01 del sensor de color |
| `generar_clasificador.py` | Riel v4; se conserva porque `generar_v5.py` y las pruebas lo usan |
| `generar_stl.py`, `geometria_stl.py` | Rack y bandeja del brazo |
| `generar_figuras.py` | Figuras de la documentación |
| `verificar_alcance.py`, `verificar_simulador.js` | Comprobaciones del alcance del brazo y del simulador web |
| `archivo/` | **Archivo:** generadores de la v1, v3 y v4 ([detalle](../scripts/archivo/README.md)) |

## `sim/`: simulaciones físicas

| Carpeta | Contenido |
|---|---|
| `mujoco/` | Simulaciones de la torre v5: `disco.py` (salida de canto), `rodar.py` (medición del diámetro), `embudo.py`, `compuerta.py` |
| `mujoco/descartados/` | **Archivo:** ideas probadas y descartadas antes de la v5 ([detalle](../sim/mujoco/descartados/README.md)) |
| `pybullet/` | Brazo (URDF), celda y simulación integrada de las etapas |

## `software/`: Python

| Carpeta | Contenido |
|---|---|
| `brazo/` | Monedas, cinemática, obstáculos, planificador, trayectorias, estática y protocolo |
| `apps/` | `cli_demo.py` (demo en consola) y `streamlit_app.py` (dashboard web) |
| `tests/` | 65 pruebas con pytest |

## Versiones de la etapa 1

| Versión | Idea | Dónde quedó |
|---|---|---|
| v1 | Riel con varillas M5 y una estación por diámetro | `hardware/archivo/etapa1-v1/`, `docs/archivo/` |
| v3 | Probetas del riel de canto | `hardware/archivo/etapa1-v3-canto/` |
| v4 | Riel de 8 ranuras con ductos de PVC | `hardware/archivo/etapa1-v4/`, `docs/archivo/`, `firmware/archivo/` |
| **v5** | **Torre de canto: disco, 2 barreras IR, color, compuerta y cartucho de 9 vasos** | **`hardware/etapa1-clasificador/`, `firmware/etapa1_clasificador/`** |
