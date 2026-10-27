# Compras etapa 1 (cruce con el inventario)

Cotas leídas de los STL (no de memoria): bolsillos y agujeros de L01, B01, H01, H02, G01.

## Faltan
| Cant. | Componente (referencia) | Cota que debe cumplir | Pieza |
|---|---|---|---|
| 1 (+1 repuesto) | Motor paso a paso 28BYJ-48 **5 V** con driver ULN2003 | Eje Ø5 con 2 planos a 3 mm (H02: 5,3 x 3,3). Resalte Ø9 (H01: 10 x 10). Orejas a 35 mm centro a centro (H01: agujeros 4 mm, P03 Ø3,9) | H01, H02, P03 |
| 1 (+1 repuesto) | Micro servo SG90 9 g con brazo simple (MG90S también calza) | Cuerpo 22,7 x 12,2 mm (G01: bolsillo 23,1 x 12,8) | G01, G02 |
| 3 | LED infrarrojo 5 mm (T-1¾), 940 nm | Cuerpo Ø5,0 (B01: agujero Ø5,2) | B01 x2 |
| 3 | Fototransistor 5 mm (T-1¾), 940 nm, del mismo kit/fabricante | Cuerpo Ø5,0 (L01: agujeros Ø5,2 a 105 y 129 mm) | L01 |
| 1 | Módulo TCS34725 con placa de ~20 mm de ancho (tipo Adafruit 1334) | Ranura L01 de 22,0 de ancho x 5,5 de grueso, a 152 mm. Mide tu placa con calibrador antes: ≤ 21,5 x ≤ 5 (con pines soldados por fuera de la ranura) | L01 |
| 1 | Cianoacrilato (pegante instantáneo) | Pegar el brazo del servo en G02 | G02 |
| opc. | Cables Dupont hembra-hembra y macho-hembra (20 de cada) | Si tu kit no los trae | — |

## Ya tienes (inventario)
ESP32-S3 DevKitC-1 con shield (control de la etapa 1 y la banda), cable USB de datos, 330 Ω (x13, LED IR a 5 V ≈ 11 mA), 10 kΩ (x23, resistencia de emisor del fototransistor), 2N3904 (x5) + 1 kΩ (x11) solo si se modula el IR, electrolítico 220 µF (x1) para el servo, protoboard, jumpers, regleta 1x10, fuente 5 V (≥ 2 A; la variable 0-20 V / 1,5 A sirve ajustada a 5,0 V solo para la tolva y el servo).

## No comprar todavía
Banda (NEMA17, A4988): depende del diseño de la etapa 2 ([`hardware/etapa2-transporte/`](../etapa2-transporte)).
