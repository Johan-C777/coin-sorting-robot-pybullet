# Pruebas

Todo lo que se afirma en la documentación está respaldado por una prueba que se
corre en el PC, sin hardware.

## Python

```bash
pip install -r requirements.txt
pytest software/tests -q
```

| Archivo | Qué comprueba |
| --- | --- |
| `test_kinematics.py` | Reposo en (15, 0, 19); DH contra forma cerrada; ejemplo de R1; ida y vuelta en los diez puestos; límites; singularidad |
| `test_planner.py` | Cinco movimientos desde la entrada; reordenar un rack lleno usando huecos; no mover lo ya ordenado |
| `test_protocol.py` | Tramas `S:90,90,90,30,90,85` y `S:114,49,83,64,90,85`; anchos de pulso; JSON del dashboard |
| `test_trajectory.py` | Extremos y picos del perfil quíntico; ocho tramos por vaso; alturas y holgura sobre los vasos |
| `test_statics.py` | Pares de la memoria (13,60 / 6,82 / 22,07 kg·cm); factores de seguridad; momento de vuelco |
| `test_urdf.py` | El URDF de PyBullet reproduce la misma cadena y los mismos límites |

## Firmware

```bash
make -C firmware/tests
```

Compila el núcleo del firmware con `g++` (sin Arduino) y corre las mismas
comprobaciones numéricas, más el ciclo completo del secuenciador con un
`BusServos` de banco: verifica que el rack queda ordenado de $50 a $1.000, que el
brazo vuelve al reposo y que el ciclo dura lo previsto.

```
  ok   ik del puesto R1 coincide con la memoria de calculo
  ok   trama del puesto R1
  ok   el rack queda ordenado de $50 a $1000
  ciclo simulado: 37.0 s en 1851 vueltas de control
```

## Integración manual

1. `python software/apps/cli_demo.py` para ver el plan y las tramas.
2. `python sim/pybullet/run_sim.py` para verlo en 3D con física.
3. `python software/apps/cli_demo.py --puerto /dev/ttyUSB0` contra el ESP32 real.
