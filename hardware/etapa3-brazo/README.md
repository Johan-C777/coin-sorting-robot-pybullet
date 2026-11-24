# Etapa 3 · Brazo de 4 GDL con garra

Brazo de doble paralelogramo (tipo EEZYbotARM, alcance ≈ 40 cm) diseñado en SolidWorks por Javier León y
Samuel Rubio. Tres NEMA 17 con reductora planetaria impresa 16:1 mueven la base (J1), el hombro (J2) y el
codo (J3); dos micro servos SG90 mueven el cabeceo de la muñeca (J4) y la pinza.

| Carpeta | Contenido |
|---|---|
| [`brazo/`](brazo) | 25 STL (`stl/`), ensamble y actuadores en STEP (`step/`), [`GUIA_IMPRESION.md`](brazo/GUIA_IMPRESION.md), [`INFORME_CAD.md`](brazo/INFORME_CAD.md), scripts generadores |
| [`garra/`](garra) | Muñeca y pinza para SG90 (7 STL, SolidWorks nativo + STEP), [`GUIA_ENSAMBLE.md`](garra/GUIA_ENSAMBLE.md) |
| [`reductora/`](reductora) | Caja planetaria 16:1 (STL, STEP, generador paramétrico) |
| [`firmware/`](firmware) | ESP32 de calibración y de prueba de motores con interfaz web por USB Serial; pinout y ajuste de drivers en [`GUIA_CONEXIONES_Y_CALIBRACION.md`](firmware/ESP32_Calibracion_Robot4GDL/GUIA_CONEXIONES_Y_CALIBRACION.md) |
| [`bom.csv`](bom.csv) | Lista de materiales del brazo |
| [`ENTREGA_ORIGINAL.md`](ENTREGA_ORIGINAL.md) | Índice y pinout tal como llegó el paquete |

Los archivos `12A`–`16` de `brazo/stl/` son la muñeca y pinza anteriores; la versión vigente es la de `garra/`.

Medidas del CAD (mm): hombro a 197 sobre la base, L₁ = 155, L₂ = 130, muñeca a eje de cabeceo 28, garra 90,
palanca motriz 50. Cómo se integra con las etapas 1 y 2: [`docs/13-etapa3-brazo.md`](../../docs/13-etapa3-brazo.md).

La versión anterior (brazo de 5 servos con PCA9685) quedó en [`../archivo/etapa3-brazo-v1/`](../archivo/etapa3-brazo-v1).
