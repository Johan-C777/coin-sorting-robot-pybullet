# Pruebas

Todo lo que se afirma en la documentación está respaldado por una prueba que se
corre en el PC, sin hardware. En GitHub las corre Actions en cada push
(`.github/workflows/pruebas.yml`).

## Python: 61 pruebas

```bash
pip install -r requirements.txt
pytest software/tests -q
```

| Archivo | Qué comprueba |
| --- | --- |
| `test_monedas.py` | Ocho estaciones en orden de diámetro; cada moneda cae en la suya; márgenes de al menos 0,25 mm; las dos $500 comparten estación; la $1.000 de 1996 se rechaza; **el firmware del contador usa las mismas luces, masas y vasos**; peso con antiguas; las antiguas cambian el orden por peso; la carga de diseño sigue en 416 g; trama `VASOS:` de ida y vuelta |
| `test_obstaculos.py` | Cuatro obstáculos entre A y B con nivel creciente; la maniobra de cada uno; las cifras 15,5 cm, ρ = 8,3 cm, 16,1 cm y 2,1 cm; sin maniobra cada uno tapa la ruta; con maniobra queda libre; el nivel 3 deja ventana; las poses de evasión tienen inversa; **el planificador de Python y el de la simulación web dan lo mismo** |
| `test_kinematics.py` | Reposo en (15, 0, 19); DH contra forma cerrada; ejemplo resuelto (24° a 6,8 cm); ida y vuelta en los dieciocho puestos; límites; singularidad |
| `test_planner.py` | Nueve movimientos desde la entrada; reordenar un rack lleno usando huecos; no mover lo ya ordenado |
| `test_protocol.py` | Tramas `S:90,90,90,30,90,85` y `S:114,49,83,64,90,85`; anchos de pulso; JSON del dashboard |
| `test_trajectory.py` | Extremos y picos del perfil quíntico; ocho tramos por vaso; alturas y holgura sobre los vasos |
| `test_statics.py` | Pares de la memoria (13,60 / 6,82 / 22,07 kg·cm); factores de seguridad; momento de vuelco |
| `test_urdf.py` | El URDF de PyBullet reproduce la misma cadena y los mismos límites |

La comparación con la simulación web necesita Node: corre
`scripts/verificar_simulador.js`, que extrae de la página las funciones del
planificador y las evalúa sin navegador. Si Node no está instalado, esa prueba se
salta y las demás corren igual.

## Firmware: 48 comprobaciones

```bash
make -C firmware/tests
```

Compila el núcleo de los dos firmwares con `g++` (sin Arduino) y corre las
mismas comprobaciones numéricas:

- **Brazo (28):** cinemática, tramas, perfil quíntico, planificador, lectura del
  lote `VASOS:` con antiguas, peso con antiguas, criterios por nombre, orden por
  peso y el ciclo completo del secuenciador con un `BusServos` de banco.
- **Contador (15):** conteo por estación y por vaso, antiguas, valor y peso,
  trama y JSON para el brazo, capacidad del vaso y que cada luz del riel deje
  pasar su moneda y retenga la siguiente.

```
  ok   lectura del lote VASOS con antiguas
  ok   orden por peso con monedas antiguas
  ok   el rack queda ordenado de $50 a $1000
  ok   las antiguas caen en el vaso de su denominacion
  ok   trama con antiguas que entiende el ESP32 del brazo
  ciclo simulado: 37.0 s en 1851 vueltas de control
```

## Simulaciones web

Las dos páginas se probaron en Chromium sin errores de consola. En la de la
etapa 1 y en la del sistema completo se instrumentó la caída de cada moneda: en
corridas de 53 y 80 monedas, ninguna cayó en una estación que no fuera la suya.

## Integración manual

1. `python software/apps/cli_demo.py` para ver el lote, la ruta de A a B, el plan
   y las tramas.
2. `python sim/pybullet/run_sim.py` para verlo en 3D con física.
3. `python software/apps/cli_demo.py --puerto /dev/ttyUSB0` contra el ESP32 real.
