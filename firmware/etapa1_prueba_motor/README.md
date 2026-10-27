# Etapa 1 completa (ESP32-S3)
`pio run -t upload && pio device monitor` · consola serie: `?` para ayuda.

## Pines (ESP32-S3-DevKitC-1; no se usan 0,3,45,46,19,20,26-37,43,44,48)
| Función | GPIO | Notas |
|---|---|---|
| ULN2003 IN1..IN4 (28BYJ-48) | 4, 5, 6, 7 | motor y ULN2003 a **5 V externos**, GND común |
| SG90 compuerta (señal) | 15 | SG90 a 5 V externos |
| Fototransistor barrera 1 / 2 | 1 / 2 | ADC1; colector 3V3, emisor→GPIO + 10 kΩ→GND |
| LED IR de las barreras | — | 330 Ω a 5 V, siempre encendidos |
| TCS34725 SDA / SCL | 8 / 9 | 3V3; pin LED del módulo a 3V3 |
| A4988 STEP / DIR / EN | 10 / 11 / 12 | EN activo en bajo; banda (`HABILITAR_BANDA 1`) |
| Haz de referencia banda | 13 | mismo circuito que las barreras |
| Libres | 14,16,17,18,21,38-42,47 | |

Alimentación: fuente 5 V ≥ 2 A para ULN2003 + SG90; 220 µF cerca de ambos; GND de la fuente unido al del ESP32.

Esquema y explicación: [docs/11-electronica-etapa1.md](../../docs/11-electronica-etapa1.md).
