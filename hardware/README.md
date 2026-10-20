# Hardware

| Carpeta | Qué hay | Estado |
|---|---|---|
| [`etapa1-clasificador/`](etapa1-clasificador) | Tolva y selección: 24 STL (`stl/`), tabla de piezas y [`bom-etapa1.csv`](etapa1-clasificador/bom-etapa1.csv) | Diseño cerrado, listo para imprimir |
| [`etapa2-transporte/`](etapa2-transporte) | Banda transportadora y vasos | En diseño |
| [`etapa3-brazo/`](etapa3-brazo) | Planos del brazo (SolidWorks), puestos del rack, bandeja de electrónica y [`bom.csv`](etapa3-brazo/bom.csv) | Diseñado; falta medir L₂ y L₃ en el CAD |
| [`archivo/etapa1-v1/`](archivo/etapa1-v1) | Primera versión de la etapa 1 (riel con varillas M5) y su 3MF | Reemplazada, solo referencia |

[`materiales.md`](materiales.md) justifica la elección de materiales.

- Etapa 1: `python scripts/generar_clasificador.py` regenera los STL y `python scripts/exportar_visor_3d.py` el visor 3D ([`docs/ensamble-etapa1.html`](../docs/ensamble-etapa1.html)). Guía de armado: [`docs/10-guia-armado-etapa1.md`](../docs/10-guia-armado-etapa1.md).
- Etapa 3 y archivo: `python scripts/generar_stl.py` y `python scripts/generar_3mf.py`.
