# Scripts archivados

Generadores de versiones reemplazadas. No hacen falta para la torre v5; se dejan para
poder regenerar las piezas del archivo (`hardware/archivo/`).

| Script | Genera |
|---|---|
| `generar_3mf.py` | `.3mf` del sistema completo de la v1 |
| `generar_canto.py` | Probetas del riel de canto (v3) |
| `generar_cuna_prueba.py` | Cuña de prueba de la v3 |
| `exportar_visor_3d.py` + `visor_template.html` | Visor 3D de la v4 (`docs/archivo/ensamble-etapa1-v4.html`) |

`scripts/generar_clasificador.py` (riel v4) sigue en `scripts/` porque `generar_v5.py`
usa su función para escribir STL y las pruebas leen sus diámetros.
