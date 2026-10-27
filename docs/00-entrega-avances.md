# Entrega de avances: segundo parcial

Micros y Laboratorio (18203) · Ingeniería Mecatrónica · Universidad Militar
Nueva Granada.

Este documento cruza lo que pide el enunciado del segundo parcial con lo que hay
en el repositorio, y deja claro qué está hecho, qué está a medias y qué sigue.

## El sistema, como quedó planteado

1. Una **tolva** recibe monedas colombianas mezcladas de las dos familias, la
   nueva (2012) y la anterior (1989-1996).
2. Un **riel selector de ocho ranuras** las separa por diámetro; una barrera
   infrarroja por ranura cuenta cada moneda y, por la ranura en que cayó, sabe
   su denominación y su familia.
3. Unos **tubos colectores** llevan cada moneda al vaso de su denominación: nueve
   vasos (uno por ducto) sobre una **banda transportadora**.
4. La banda entrega cada vaso en el **punto A**, el límite del alcance del brazo.
5. El **brazo de 5 GDL** lleva el vaso al **punto B** (el rack) esquivando
   **cuatro obstáculos giratorios de dificultad creciente**.
6. En el rack los deja **ordenados según la orden** que recibe: por valor, peso,
   cantidad de monedas, denominación o cantidad de monedas antiguas, ascendente o
   descendente.
7. Una **app en Streamlit** se conecta por Wi-Fi a los ESP32, da la orden y
   muestra ruta, valor, peso y cantidad, con un asistente que responde sobre el
   lote.

## Objetivos específicos y evidencia

| Objetivo del enunciado | Estado | Evidencia en el repositorio |
| --- | --- | --- |
| **Arquitectura** con requerimientos funcionales y no funcionales, diagramas de bloques por módulo y selección de materiales | Hecho | [01-arquitectura.md](01-arquitectura.md) (RF y RNF con dónde se verifica cada uno, bloques, responsabilidades, algoritmo de orden), [materiales.md](../hardware/materiales.md), [bom.csv](../hardware/etapa3-brazo/bom.csv), [despiece de la etapa 1](../hardware/etapa1-clasificador/despiece.csv), [compras de la etapa 1](../hardware/etapa1-clasificador/compras.md) |
| **Diseño mecánico y electrónico**: CAD, planos, esquemas eléctricos; PyBullet y URDF opcional | Hecho en diseño; falta el esquemático en KiCad | Planos del brazo en SolidWorks ([PLANOS BRACITO.pdf](../hardware/etapa3-brazo/PLANOS%20BRACITO.pdf)); etapa 1 v5 en impresión: 24 STL generados por código, 8 camas y armado en [`hardware/etapa1-clasificador/`](../hardware/etapa1-clasificador/README.md), diseño en [09-clasificador-v5.md](09-clasificador-v5.md), pines y esquema de cableado del ESP32-S3 en [11-electronica-etapa1.md](11-electronica-etapa1.md); [06-medidas-cad.md](06-medidas-cad.md), conexiones y presupuesto de corriente en [03-electronica.md](03-electronica.md), URDF en `sim/pybullet/`, [memoria de cálculo](memoria-calculo.html) con cinemática, pares y selección de servos |
| **Primeros módulos funcionando** (se acepta simulado en PyBullet) | Hecho en simulación | Simulación web de la [etapa 1](simulacion-etapa1.html) y del [sistema completo](simulacion_sistema_completo.html); PyBullet en `sim/pybullet/run_sim.py` y `run_sim_integrada.py`; firmware de los dos ESP32 con su núcleo probado en el PC |
| **App web (Streamlit) inalámbrica con el ESP32**, primeras métricas | Hecho, probado contra la simulación | `software/apps/streamlit_app.py`: modo simulación y modo ESP32 por Wi-Fi (HTTP/JSON), métricas de valor, peso, cantidad y antiguas, ruta del brazo, tabla de obstáculos y asistente; rutas `/api/estado`, `/api/ordenar`, `/api/vasos` y `/api/pose` en el firmware ([04-protocolo.md](04-protocolo.md)) |
| Diferencial: trayectoria con obstáculos hasta la meta | Hecho en simulación y en Python | Cuatro obstáculos por nivel entre A y B, con tres maniobras distintas: [08-obstaculos.md](08-obstaculos.md) |

## Avance después de la entrega

- **Etapa 1 v5 y electrónica (0.7.0).** La etapa 1 pasó a una torre de canto: tolva de disco, pista con dos barreras IR que miden el diámetro, TCS3200 para las $500, embudo y compuerta sobre un cartucho de 9 vasos que mueve la banda. 24 STL, 8 camas (1 a 6 ya impresas), despiece y compras en [`hardware/etapa1-clasificador/`](../hardware/etapa1-clasificador/README.md); diseño y simulaciones MuJoCo en [09-clasificador-v5.md](09-clasificador-v5.md); pines del ESP32-S3, esquema y firmware en [11-electronica-etapa1.md](11-electronica-etapa1.md). La v4 quedó en `hardware/archivo/etapa1-v4/`.
- **Nueve vasos al brazo (0.6.0).** El contador, el brazo (Python, ESP32 y simulación web) y PyBullet reciben y ordenan 9 vasos Ø34 × 60 mm en un rack de 9 puestos; las $500 antiguas y nuevas van en vasos distintos. Las ranuras del riel usan los diámetros oficiales del Banco de la República (0.5.1).

- **Etapa 1 lista para imprimir.** Clasificador físico generado por código: riel de 22° en dos módulos, 7 ranuras y extremo abierto, tolva con 28BYJ-48 y las dos $500 separadas por color (TCS34725) con un plato basculante. Nueve salidas, cada una a su propio vaso.
- **Sin tornillos ni soportes**, con ductos y base en tubo PVC: de ≈ 800 a ≈ 480 g de filamento. Visor 3D con simulación y guía de armado completa.
- **Repositorio ordenado por etapa** en `hardware/` (etapa1-clasificador, etapa2-transporte, etapa3-brazo y archivo).

## Qué cambió en esta entrega

- **Monedas antiguas y nuevas.** El riel pasó de 5 a 8 ranuras, calculadas a
  partir de las fichas del Banco de la República
  ([07-monedas.md](07-monedas.md)). Se actualizaron el firmware del contador
  (8 barreras, conteo por familia), el del brazo (peso con monedas antiguas y
  nuevo criterio de orden), las dos simulaciones, los STL y el 3MF.
- **Ruta A→B con niveles.** Los cuatro obstáculos quedaron rotulados por nivel
  en la simulación, el planificador se llevó a Python
  (`software/brazo/obstaculos.py`) y una prueba lo compara contra el JavaScript
  de la página.
- **Errores corregidos.** `POST /api/pose` validaba la trama pero no movía los
  servos; el comando `ENVIAR` del contador estaba documentado y no existía; una
  moneda rápida podía saltarse su ranura en la simulación a baja tasa de cuadros.
- **Integración continua.** Cada push corre las pruebas de Python y del
  firmware en GitHub Actions.

## Resultados verificables

```bash
pytest software/tests -q          # 60 pruebas
make -C firmware/tests            # 45 comprobaciones de los dos firmwares
python scripts/verificar_alcance.py
python software/apps/cli_demo.py --criterio peso
```

| Resultado | Valor |
| --- | --- |
| Monedas admitidas | 9 tipos de las dos familias en 8 estaciones |
| Margen más ajustado del riel | 0,30 mm en la estación 4 |
| Obstáculos entre A y B | 4, niveles 1 a 4, tres maniobras distintas |
| Ciclo del brazo por vaso | 7,1 s sin obstáculos |
| Carga de diseño | 416 g (40 monedas de $1.000) |
| Error entre la cinemática de Python, la del ESP32 y el URDF | ruido de punto flotante |
| Error entre el planificador de Python y el de la simulación web | 10⁻¹⁴ cm |

## Qué sigue

| Pendiente | Para qué |
| --- | --- |
| Imprimir la cama 7 (vasos, cartucho y compuerta) y armar la torre v5 con su [guía](../hardware/etapa1-clasificador/README.md) | Pasar la tolva y la selección de diseño a construido |
| Probar el 28BYJ-48 con la tolva cargada y calibrar barreras y color con monedas reales | Fijar velocidad de la tolva, `K_CUERDA` y `UMBRAL_DORADO` |
| Diseñar la banda transportadora (etapa 2) | Llevar los 9 vasos al punto A |
| Medir L₂ y L₃ en el ensamble de SolidWorks | Cerrar el perfil real del brazo construido |
| Llevar la evasión de obstáculos al firmware del brazo | Hoy corre en simulación y en Python |
| Esquemático eléctrico en KiCad | Hoy está como tabla de conexiones y diagrama |
| Sensor de color en la estación 3 | Admitir la $1.000 de 1996 |
| Montar la celda, calibrar barreras IR y medir el ciclo real | Pasar de simulado a construido |
| Actualizar el orquestador de PyBullet al riel de 8 estaciones | Hoy modela la familia nueva |
