# Cambios

## 0.5.1 · Ranuras del riel con los diámetros oficiales

- **Corrección antes de imprimir R01:** la ranura 3 medía 21,5 mm y la $50 antigua mide 21,5 mm (Banco de la República, circular DTE-190), así que no habría caído por ella. Ahora la ranura 3 es de 22,0 mm y la 4 de 22,8 mm (antes 22,9; retiene mejor la $100 antigua: 0,2 mm en vez de 0,1). La $500 antigua pasa a 23,7 mm y 7,14 g (antes 23,5 y 7,43). Regenerados D3 a D8, R01, patas, ensamble y visor.
- Prueba nueva que lee `scripts/generar_clasificador.py` y comprueba diámetros oficiales, caída de 0,4 mm y retención de la moneda siguiente.

## 0.5.0 · Avance consolidado y repositorio por etapas

- Integra en `main` todo el trabajo de la etapa 1 física (0.4.0 a 0.4.2) y la guía de armado.
- `hardware/` por etapa: `etapa1-clasificador/` (24 STL + BOM), `etapa2-transporte/` (restricciones para la banda), `etapa3-brazo/` (planos, rack, bandeja, BOM) y `archivo/etapa1-v1/` (riel con varillas M5 y su 3MF). Generadores actualizados a las rutas nuevas.
- Visor 3D movido a `docs/ensamble-etapa1.html` para que abra en GitHub Pages; enlazado en la portada.
- Docs renumerados: `09-clasificador-fisico.md`, `10-guia-armado-etapa1.md`; el despiece v1 pasa a `docs/archivo/`.
- `bom-etapa1.csv` rehecho según la guía (quedaban varillas M5, SG90 de paleta y piezas de banda de la v1).
- La prueba que cruza el firmware del contador con el modelo de monedas compara ahora los 9 ductos del riel físico con las 8 estaciones del modelo (fallaba desde 0.4.0).
- README y entrega de avances con tabla de avance por etapa.

## 0.4.2 · Ductos y base en PVC

- Los siete ductos pasan a tubo PVC de presión de 1" (Ø ext 33,4, interior ≈ 30) con un adaptador impreso de 65 mm: caja de la ranura con IR y clavijas, embudo de 36° y collar. Salidas separadas ≥ 37 mm.
- Base: dos bases de ABS (P01) y patas, tees y largueros de tubo PVC de 3/4"; lámina de MDF de 9 mm. Hueco para la banda de 123 × 490 mm con 70 mm bajo la banda. Se quitan P01/P02 anteriores.
- Total impreso de 1143 a 612 cm³ macizos (≈ 800 a ≈ 480 g, ≈ 48 a ≈ 33 h).

## 0.4.1 · Etapa 1 sin tornillos ni soportes

- Corregida la alineación de la $500: las salidas quedaban 100-137 mm fuera de la línea de vasos. Nuevo bifurcador D6 con plato basculante (SG90 a 55°/125°) y dos columnas alineadas con los demás ductos.
- Clavijas Ø6, llaves de mariposa y bridas de nailon en lugar de M3. Piezas orientadas para imprimir sin soportes.
- Visor 3D con simulación de monedas a los vasos.
- Sin mangueras: ductos alargados hasta los nueve vasos Ø34 (salidas separadas ≥35 mm; riel 36 mm más largo, columnas de D6 abiertas). Base de lámina sobre patas de tubo PVC con codos impresos P01/P02.

## 0.4.0 · Clasificador físico para impresión FDM

- `scripts/generar_clasificador.py` (manifold3d): tolva de 40° con disco de 4
  cavidades (28BYJ-48 o SG90 continuo), riel de 22° en dos módulos con cola de
  milano, 7 ranuras + extremo abierto, 7 ductos y la bifurcación de $500 con
  alojamientos para TCS34725/TCS3200, SG90 y barreras IR de 5 mm. STL en
  `hardware/stl/`, guía en `docs/08-clasificador-fisico.md`.
- Firmware del contador: 9 ductos con interrupción IR, lectura I2C del
  TCS34725 (`color500.h`, `bifurcacion.*`), aguja SG90 por LEDC y tolva a
  1 moneda / 1,5 s. Nuevo mapa de pines en `config.h`.

## 0.3.0 · Entrega de avances del segundo parcial

### Monedas antiguas y nuevas
- Catálogo de las dos familias del Banco de la República en
  `software/brazo/monedas.py`, con el diseño del riel calculado a partir de los
  diámetros: 8 estaciones, luces entre 17,60 y 27,30 mm.
- Las dos $500 (idénticas) comparten estación; la $1.000 de 1996 se rechaza por
  quedar a 0,17 mm de la $50 antigua.
- Los vasos guardan cuántas monedas son antiguas, y el peso las cuenta. Nuevo
  criterio de orden: `antiguas`.
- Trama `VASOS:` con `aN` opcional (`50x30a6`) y evento `M:<den>,<estación>,<familia>`.
- Firmware del contador con 8 barreras IR y conteo por estación y por vaso.
- Firmware del brazo: lee el lote con antiguas (`Protocolo::leerVasos`), las
  pesa y ordena por ellas.
- Riel de 8 ranuras regenerado en STL (paso de 40 mm, dos tramos de 200 y
  180 mm), embudo corto con espiga para tubo de 3/4" y 3MF de 58 piezas.
- Simulaciones web de la etapa 1 y del sistema completo con las 8 estaciones y
  los tubos colectores.

### Ruta de A a B
- Los cuatro obstáculos tienen nivel de dificultad (1 a 4) y se rotulan en la
  simulación junto con el punto A y el punto B.
- Planificador de evasión en Python (`software/brazo/obstaculos.py`), probado
  contra el JavaScript de la simulación con `scripts/verificar_simulador.js`.
- Figuras nuevas: `selector-monedas.png` y `ruta-obstaculos.png`.

### Correcciones
- `POST /api/pose` en el brazo validaba la trama y no movía los servos.
- El comando `ENVIAR` del contador estaba documentado y no existía.
- En la simulación, una moneda rápida con pocos cuadros por segundo podía
  saltarse su ranura; ahora se integra en sub-pasos de 3 mm.
- `docs/despiece.md` enlazaba una imagen que no estaba en el repositorio.

### Repositorio
- README reescrito, `docs/00-entrega-avances.md`, `07-monedas.md`,
  `08-obstaculos.md` y portada `docs/index.html` para GitHub Pages.
- GitHub Actions corre las pruebas en cada push; `.gitignore`.
- Pruebas: de 36 a 60 en Python y de 32 a 43 en C++.

## 0.2.0 · Etapa 1 completa
- Riel selector de 5 estaciones, contador, banda, simulación de la etapa 1,
  STL y 3MF de la celda, memoria de cálculo y simulación del sistema completo.
