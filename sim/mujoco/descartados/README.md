# Simulaciones de ideas descartadas

Antes de llegar a la torre v5 se probaron en MuJoCo otras formas de poner la moneda de
canto o de separarla. Ninguna se usa en el diseño final; quedan como registro de por qué
se eligió el disco inclinado y la pista con barreras.

| Archivo | Idea probada |
|---|---|
| `bandeja.py` | Bandeja basculante que levanta la moneda plana hasta dejarla de canto |
| `barredor.py` | Cuchilla que barre monedas planas hacia agujeros por diámetro |
| `empujador.py` | Riel horizontal de canto con ventanas por altura y un dedo empujador |
| `entrada.py` | Entrada con torsión de plana a canto y un tope que baja lento |

Las simulaciones vigentes están en `sim/mujoco/`: `disco.py`, `rodar.py`, `embudo.py` y
`compuerta.py` (con `riel_canto.py` como módulo común).
