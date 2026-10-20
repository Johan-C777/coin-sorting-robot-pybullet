# Protocolo de comunicación

## Nivel bajo: una línea por pose

```
S:114,49,83,64,90,85
```

Seis ángulos de servo en grados enteros: J1 a J5 y la pinza (0 a 90°). La trama
ocupa 21 caracteres, unos 1,8 ms a 115200 baudios; enviándola a 50 Hz usa el 9 %
del enlace. Es la misma cadena que muestra la simulación 3D, así que pasar de
simulado a real no cambia la lógica de control.

## Lote del contador al brazo

```
VASOS:50x24,100x20,50x6a6,200x18,100x4a4,500x9,500x5a5,200x3a3,1000x12
```

Un vaso por ducto (N50, N100, A50, N200, A100, N500, A500, A200, N1000), en el orden de los puestos de entrada. Las $500 antiguas y nuevas van a vasos distintos. `50x6a6` es
el vaso de $50 con 6 monedas, todas de la familia anterior. El
`aN` se omite cuando no hay antiguas, así que una línea sin él sigue siendo
válida. La lee `Protocolo::leerVasos()` en el firmware y
`brazo.protocol.parsear_vasos()` en Python; las dos rechazan un vaso con más
antiguas que monedas.

Cada moneda contada sale además por el serie del contador:

```
M:100,5,antigua            denominación, estación del riel y familia
```

## Comandos del ESP32 del brazo por el puerto serie

| Comando | Efecto |
| --- | --- |
| `S:j1,j2,j3,j4,j5,pinza` | Pose directa, modo manual |
| `VASOS:500x12a12,100x30,1000x8,50x25,200x17,100x10a10,50x9a9,500x8,200x6a6` | Carga el lote de la entrada (9 vasos) |
| `ORDEN:valor,asc` | Clasifica (`valor`, `peso`, `cantidad`, `denominacion`, `antiguas`) |
| `ESTADO` | Devuelve el JSON de estado |
| `HOME` | Lleva el brazo al reposo |
| `PAUSA` / `SIGUE` | Pausa o reanuda la secuencia |
| `STOP` | Aborta el plan |
| `TORQUE0` / `TORQUE1` | Corta o repone el torque de los servos |

## Comandos del ESP32 del contador

| Comando | Efecto |
| --- | --- |
| `ALIM:3.5` | Monedas por segundo que suelta la tolva |
| `BANDA:0.6` | Velocidad de la banda, de 0 a 1 |
| `CONTEO` | Devuelve la línea `VASOS:` actual |
| `ENVIAR` | Cierra la tanda ya y entrega el lote al brazo |
| `ESTADO` | JSON con conteo y estado de los actuadores |
| `REINICIAR` / `PARAR` | Pone el conteo en cero / detiene tolva y banda |

## Nivel alto: JSON por Wi-Fi

| Ruta | Quién la usa | Contenido |
| --- | --- | --- |
| `POST /api/vasos` | Módulo contador | denominación, cantidad y antiguas de cada puesto |
| `POST /api/ordenar` | App Streamlit | criterio y sentido |
| `POST /api/pose` | Modo manual | una trama `S:`, que mueve los servos |
| `GET /api/estado` | Dashboard | pose, paso en curso y contenido del rack |

```json
{
  "estado": "moviendo",
  "paso": 3, "total": 5,
  "q": [24.0, 49.0, -82.5, -56.5, 0.0],
  "pinza_mm": 49,
  "trama": "S:114,49,83,64,90,85",
  "vasos": [
    {"zona": "rack", "puesto": 1, "den": 50, "n": 25, "antiguas": 9, "valor": 1250, "peso_g": 90.5}
  ]
}
```

## Secuencia típica

```mermaid
sequenceDiagram
    participant C as Contador
    participant A as App Streamlit
    participant E as ESP32
    participant S as Servos
    C->>E: POST /api/vasos
    A->>E: POST /api/ordenar {"criterio":"valor","sentido":"asc"}
    E->>E: planificar y resolver la inversa
    loop cada 20 ms
        E->>S: seis pulsos por I2C y PWM
        A->>E: GET /api/estado
        E-->>A: pose, paso y rack
    end
    E-->>A: estado "listo"
```

La app consulta el estado cada 500 ms, suficiente para la barra de progreso y el
mapa de la ruta. Si el contador termina siendo otro ESP32, el enlace entre los dos
puede hacerse por ESP-NOW y dejar el Wi-Fi solo para la app.
