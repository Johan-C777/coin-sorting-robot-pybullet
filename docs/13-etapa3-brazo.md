# Etapa 3 · Brazo real y su integración

## 1. Qué es el brazo construido

| Parámetro | Valor |
|---|---|
| Cinemática | Doble paralelogramo: J2 mueve el brazo principal, J3 el antebrazo; la garra queda horizontal |
| Articulaciones | J1 base, J2 hombro, J3 codo (NEMA 17 + planetaria 16:1) · J4 cabeceo ±45° (SG90) · pinza (SG90) |
| Medidas (mm) | Hombro a 197 de la base · L₁ 155 · L₂ 130 · muñeca–cabeceo 28 · garra 90 |
| Alcance horizontal de la punta | ≈ 362 mm a 50 mm de altura, ≈ 378 mm a 80 mm |
| Resolución | 200 × 2 (1/2 paso) × 16 = 6.400 pasos/vuelta de salida ≈ 17,8 pasos/° |
| Drivers | 2× TB6560 + 1× TB6600 a 24 V, 1,9 A |
| Controlador | ESP32 clásica: STEP/DIR J1 26/25, J2 33/32, J3 27/14, EN 13, servos 18 y 19 |

## 2. Cómo se une a las etapas 1 y 2

1. **Dos controladores.** Las etapas 1 y 2 usan una ESP32-S3 (GPIO 1–21) y el brazo una ESP32 clásica. Los pines 26–37 de la S3 no están disponibles, así que no se pueden fundir. Cada una conserva su pinout.
2. **Alimentación.** 24 V para los drivers del brazo, 12 V para el A4988 de la banda, 5 V para servos y 5 V de la placa de la S3. Todas las tierras unidas.
3. **Comunicación.** Enlace serie entre placas: TX de la S3 (GPIO 38) a RX2 de la ESP32 (GPIO 16) y TX2 (GPIO 17) a RX de la S3 (GPIO 39). Misma trama `VASOS:` que ya define [`04-protocolo.md`](04-protocolo.md); alternativa por Wi-Fi (`POST /api/vasos`).
4. **Mecánica.** El punto A es el final de la banda (cartucho con vaso 1, X = 470 mm en el marco de la banda). La base del brazo se coloca de modo que A quede a ≤ 330 mm del eje de J1 y el rack en un arco de radio 270–330 mm (a 9,5° hay 46–55 mm entre vasos, para vasos de 34 mm).
5. **Software.** Perfil `entrega` en `software/brazo/config.py` con las medidas del CAD, para sustituir al perfil `cad` anterior.

## 3. Diferencias con el modelo simulado

| Simulación | Brazo real | Consecuencia |
|---|---|---|
| 5 servos con PCA9685 | 3 pasos a paso + 2 servos | Hay que sustituir `servo_bus` por salidas STEP/DIR con rampa |
| Pinza vertical (−90°) | Pinza siempre horizontal (±45°) | El agarre del vaso es lateral, a media altura (≈ 50–80 mm) |
| 5 GDL (J5 giro) | 4 GDL | Sin giro de pinza: el vaso se toma de frente |
| Radio de arco 230 mm | 270–330 mm | Rack y puntos A/B recalculados |
| Sin topes | Sin finales de carrera | Cero de cada eje fijado a mano con la interfaz de calibración |

## 4. Plan

| # | Tarea | Resultado |
|---|---|---|
| 1 | Importar la entrega y archivar el diseño anterior | Hecho |
| 2 | Documentar brazo, garra, reductora, cableado y BOM | Hecho (`hardware/etapa3-brazo/`) |
| 3 | Perfil `entrega` en `software/brazo/config.py`, cinemática del paralelogramo y comprobación de alcance de A, B y los nueve puestos | Pendiente |
| 4 | Rehacer el rack (B11) y la bandeja (B12) para el arco real | Pendiente |
| 5 | Visor 3D de las tres etapas con el brazo real | Pendiente |
| 6 | Firmware de ángulos (Fase 2) con el JSON de calibración | Pendiente de datos |
| 7 | Fotos y tabla de pruebas físicas de la etapa 3 | Pendiente de fotos |
| 8 | README, Pages, CHANGELOG, MAPA y entrega final | En curso |

## 5. Riesgos

- La pinza SG90 (≈ 1,8 kg·cm) no sostiene un vaso con 40 monedas (≈ 430 g). Se limita la carga por vaso o se refuerza la pinza con almohadillas de TPU.
- La guía recomienda microstepping 1/8 (71 pasos/°) y el README verificado usa 1/2 (17,8 pasos/°): hay que fijar un único valor en el firmware.
- Las reductoras de plástico tienen holgura; la repetibilidad se mide antes de prometer posiciones en el rack.
- Falta el archivo `robot_4gdl_calibracion.json` con ceros y límites.
