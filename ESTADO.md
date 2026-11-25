# Estado del proyecto

Resumen técnico de una página, al 24 de noviembre de 2026. El detalle de cada etapa está en los
documentos enlazados.

## Etapas

| Etapa | Controlador | Estado | Documento |
|---|---|---|---|
| 1 · Clasificador de monedas | ESP32-S3 | Torre v5 impresa, armada, cableada y probada con monedas reales; ajustes de diseño H02e (disco de 5 bolsillos Ø40), H04 (tope trasero) y G03 (paleta plana) impresos y montados; firmware de operación a 5 bolsillos | [09](docs/09-clasificador-v5.md), [11](docs/11-electronica-etapa1.md), [12](docs/12-pruebas-fisicas-etapa1.md) |
| 2 · Banda transportadora | RAMBo (Marlin 2.1.2.5) | v7 de motor fijo con barra dentada impresa y montada; mueve el cartucho de 9 vasos (42,44 pasos/mm, 38 mm entre vasos, carrera 774 mm) | [hardware/etapa2-transporte](hardware/etapa2-transporte/README.md) |
| 3 · Brazo de 4 GDL | ESP32 DevKit + 2 TB6560 + TB6600 | Doble paralelogramo con 3 NEMA17 y reductora planetaria 16:1, cabeceo y garra con SG90; impreso, armado y probado tomando y trasladando un vaso | [13](docs/13-etapa3-brazo.md) |

Las tres etapas se operan desde el [panel de control web](docs/panel-control.html) y se ven juntas en
el [sitio del proyecto](https://johan-c777.github.io/coin-sorting-robot-pybullet/).

## Decisiones de diseño principales

- **Medición por tiempo de vuelo:** dos barreras IR miden el diámetro de cada moneda
  (D = h + c²/4h, aceleración constante en la pista de 22°); el TCS3200 separa las dos $500 por color.
- **Un controlador por etapa:** cada módulo se prueba y se repara por separado; la trama `VASOS:`
  define el enlace de datos entre ellos.
- **Todo impreso, sin soportes ni tornillos en la torre:** clavijas y encajes a presión; generadores
  paramétricos en `scripts/` producen todas las piezas.
- **Brazo de paralelogramo:** los motores pesados van en la base y la garra conserva su orientación;
  cinemática cerrada en [`software/brazo/brazo4gdl.py`](software/brazo/brazo4gdl.py).

## Verificación

- 71 pruebas Python (`pytest software/tests`) y 64 pruebas C++ de firmware, en GitHub Actions.
- Simulación MuJoCo de la tolva (1.728/1.728 monedas de canto) y del embudo (81/81).
- Evidencia física en video y foto en `docs/pruebas/etapa1`, `etapa2` y `etapa3`.

## Organización

- Mapa completo del repositorio: [docs/MAPA-DEL-REPOSITORIO.md](docs/MAPA-DEL-REPOSITORIO.md).
- Plan por fases y procedimiento de calibración: [TODO.md](TODO.md).
- Historial de versiones: [CHANGELOG.md](CHANGELOG.md).
- Diseños reemplazados (clasificador v1 a v4, banda v3 a v6, brazo de servos): carpetas `archivo/` y
  las versiones anteriores dentro de `hardware/etapa2-transporte/`, conservadas como registro del
  proceso de diseño.
