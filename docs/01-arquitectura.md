# Arquitectura del sistema

La celda tiene dos etapas. La primera recibe monedas colombianas antiguas y
nuevas, las separa, las cuenta y las embala en nueve vasos (uno por ducto) sobre una banda. La
segunda es el brazo: toma cada vaso en el punto A, lo lleva al punto B
esquivando cuatro obstáculos y deja el rack ordenado según la orden de la app.

```mermaid
flowchart LR
    T["Tolva<br/>monedas antiguas y nuevas"] --> R["Riel de 8 ranuras<br/>separa por diámetro"]
    R --> IR["8 barreras IR<br/>denominación y familia"]
    IR --> C["Tubos colectores<br/>9 vasos, uno por ducto"]
    C --> B["Banda transportadora"]
    B --> A(["Punto A<br/>fin de la banda"])
    A --> O1["N1 · O1<br/>por debajo"] --> O2["N2 · O2<br/>rodeo"] --> O3["N3 · O3<br/>ventana"] --> O4["N4 · O4<br/>por debajo y bajada cronometrada"]
    O4 --> Bp(["Punto B<br/>rack R1 a R9"])
    APP["App Streamlit"] -. "orden: criterio y sentido" .-> Bp
```

## Requisitos

| Código | Requisito | Dónde se verifica |
| --- | --- | --- |
| RF0 | Separar monedas de la familia nueva (2012) y de la anterior, contarlas por denominación y por familia | `software/tests/test_monedas.py`, `firmware/tests/test_conteo.cpp` |
| RF1 | Recoger vasos en el punto A y depositarlos en los nueve puestos del rack (punto B) | `software/tests/test_trajectory.py`, `firmware/tests` |
| RF1b | Llegar de A a B esquivando cuatro obstáculos de dificultad creciente | `software/tests/test_obstaculos.py`, [08-obstaculos.md](08-obstaculos.md) |
| RF2 | Ordenar por denominación, cantidad, valor, peso o cantidad de antiguas, en ambos sentidos | `software/tests/test_planner.py`, `test_monedas.py` |
| RF3 | Recibir órdenes y datos de vasos (con sus antiguas) desde la app y el contador | `docs/04-protocolo.md` |
| RF4 | Reportar pose, estado y contenido del rack | `brazo/protocol.py::estado_json` |
| RF5 | Modo manual articular y cartesiano para calibrar | simulación 3D y comando `S:` |
| RNF1 | Mínimo 4 GDL | 5 GDL más pinza |
| RNF2 | Carga útil de 416 g (vaso con 40 monedas de $1.000) | `software/tests/test_statics.py` |
| RNF3 | Tolerancia de ±5 mm en los puestos | resolución de 1,8 mm, holgura de pinza de 7 mm |
| RNF4 | Ciclo menor a 10 s por vaso a velocidad 1× | 7,1 s medidos en `cli_demo` |
| RNF5 | Potencia de servos separada de la lógica, con tierra común | `docs/03-electronica.md` |
| RNF6 | Piezas imprimibles en 3D y componentes de bajo costo | `hardware/etapa3-brazo/bom.csv`, `hardware/etapa1-clasificador/despiece.csv`, `hardware/etapa1-clasificador/compras.md` |

## Bloques del brazo

```mermaid
flowchart LR
    APP["App Streamlit<br/>dashboard y asistente"]
    CONT["Módulo contador<br/>denominación y cantidad"]
    ESP["ESP32 del brazo<br/>estado, planificador,<br/>cinemática inversa"]
    PCA["PCA9685<br/>6 PWM a 50,03 Hz"]
    SRV["Servos J1 a J5<br/>y pinza"]
    FTE["Fuente 6 V / 10 A"]
    SIM["Simulación 3D y PyBullet<br/>misma trama de servos"]

    APP <-->|"Wi-Fi, JSON"| ESP
    CONT -->|"datos de vasos"| ESP
    SIM -->|"serie 115200"| ESP
    ESP -->|"I2C 0x40"| PCA
    PCA -->|"pulsos 500 a 2500 us"| SRV
    FTE -->|"6 V por bornera"| SRV
```

## Responsabilidades

| Bloque | Qué hace | Qué no hace |
| --- | --- | --- |
| App Streamlit | Elige criterio y sentido, muestra ruta, valor, peso y cantidad | No calcula cinemática |
| ESP32 | Guarda el estado de los dieciocho puestos, planifica, resuelve la inversa y comanda | No decide el criterio |
| PCA9685 | Genera los seis PWM por hardware | No conoce la geometría |
| Simulación | Reemplaza al hardware mientras se construye | No sustituye la calibración real |

## La celda

Dieciocho puestos sobre un arco de radio 23 cm: entrada E1 a E9 entre −88° y −12°,
rack R1 a R9 entre 12° y 88°, separados 9,5°. La cuerda entre puestos vecinos es
3,81 cm y el vaso (el de la etapa 1, Ø34 mm) mide 3,4 cm, así que quedan solo
4 mm libres: la pinza cerrada (31 mm) baja sobre el vaso y se abre a 66 mm, pero
el margen de colocación es de ±2 mm. Como todos comparten
radio, la postura del brazo es la misma en los dieciocho y solo cambia θ₁: eso
simplifica el plan y hace que el error de posicionamiento sea parejo.

## Algoritmo de orden

```mermaid
flowchart TD
    A["Lote de 9 vasos"] --> B["Ordenar por la clave elegida<br/>desempate por denominación"]
    B --> C{"Puesto j del rack<br/>j = 1 a 9"}
    C --> D{"¿El vaso correcto<br/>ya está ahí?"}
    D -->|sí| C
    D -->|no| E{"¿El puesto está<br/>ocupado por otro?"}
    E -->|sí| F["Llevar ese vaso a un<br/>hueco libre de la entrada"]
    E -->|no| G["Mover el vaso correcto<br/>hasta el puesto j"]
    F --> G
    G --> C
    C -->|"j = 9 terminado"| H["Rack ordenado"]
```

Desde la entrada son exactamente nueve movimientos. Reordenando un rack ya lleno
son como máximo dieciocho, porque cada vez que se saca un vaso del rack se libera un
hueco de entrada.
