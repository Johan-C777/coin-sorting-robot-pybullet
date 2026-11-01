# Esquema de conexiones · etapa 1

Un ESP32-S3-DevKitC-1 controla toda la torre. Lista de conexiones (netlist) en
[`conexiones.csv`](conexiones.csv); el firmware usa exactamente estos pines
([`pines.h`](../../../firmware/etapa1_clasificador/include/pines.h)) y una prueba de CI
verifica que no se repiten ni caen en pines reservados del S3.

![Diagrama de cableado](../../../docs/img/etapa1-cableado.svg)

```mermaid
flowchart LR
    subgraph P5["Fuente 5 V ≥ 2 A"]
    end
    subgraph ESP["ESP32-S3-DevKitC-1"]
        G4["GPIO 4-7"]
        G15["GPIO 15"]
        G1["GPIO 1 · ADC1_CH0"]
        G2["GPIO 2 · ADC1_CH1"]
        G14["GPIO 14 · PCNT"]
        G16["GPIO 16,17,18,21"]
        G9["GPIO 9"]
        G10["GPIO 10,11,12,13"]
    end
    G4 --> ULN["ULN2003"] --> M["28BYJ-48<br/>tolva"]
    G15 --> SG["SG90<br/>compuerta"]
    IR1["LED IR + fototransistor<br/>barrera 1 (105 mm)"] --> G1
    IR2["LED IR + fototransistor<br/>barrera 2 (129 mm)"] --> G2
    TCS["TCS3200<br/>(adaptador A01, 152 mm)"] --> G14
    G16 --> TCS
    BTN["Pulsador (opcional)"] --> G9
    G10 -.-> A4["A4988 + NEMA17 y haz de referencia<br/>banda, etapa 2"]
    P5 --> ULN & SG & IR1 & IR2
```

## Circuito de cada barrera

```
 5V ──[330 Ω]──►|── GND          LED IR 940 nm (≈ 11 mA), siempre encendido
                     ·  haz (ventana Ø1,6 en L01, a 10 mm sobre la repisa)
 3V3 ──C╲ fototransistor
         E──┬── GPIO 1 / 2 (ADC)
            └─[10 kΩ]── GND      haz libre: tensión alta · moneda: baja
```

## Alimentación

| Rama | Fuente | Consumo aprox. |
|---|---|---|
| ESP32-S3, TCS3200, fototransistores | USB (3V3 de la placa) | < 250 mA |
| 28BYJ-48 por ULN2003, paso completo | 5 V externos | ≈ 240 mA |
| SG90 | 5 V externos, 220 µF junto al servo | 150 mA, picos de 650 mA |
| 2 LED IR | 5 V externos | 22 mA |
| NEMA17 (etapa 2) | 12 V por el A4988 | según Vref |

GND de todas las fuentes unido al GND del ESP32.

## Al cablear

- Comprobar que el shield del ESP32-S3 deja libres todos estos pines.
- Unir primero las tierras y medir 5 V en el riel antes de conectar el ESP32
  (procedimiento completo en la [fase 4 de TODO.md](../../../TODO.md#fase-4--montaje-y-calibración-física)).
