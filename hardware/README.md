# Hardware

| Carpeta | Qué hay | Estado |
|---|---|---|
| [`etapa1-clasificador/`](etapa1-clasificador) | Torre de canto v5: 24 STL (`stl/`), 8 camas `.3mf` (`impresion/`), [`despiece.csv`](etapa1-clasificador/despiece.csv), [`compras.md`](etapa1-clasificador/compras.md) y guía de armado en su [README](etapa1-clasificador/README.md) | Camas 1 a 6 impresas; falta la 7 y armar |
| [`etapa2-transporte/`](etapa2-transporte) | Banda transportadora que mueve el cartucho de 9 vasos | En diseño |
| [`etapa3-brazo/`](etapa3-brazo) | Planos del brazo (SolidWorks), puestos del rack, bandeja de electrónica y [`bom.csv`](etapa3-brazo/bom.csv) | Diseñado; falta medir L₂ y L₃ en el CAD |
| [`archivo/`](archivo) | Versiones reemplazadas de la etapa 1: [`etapa1-v1/`](archivo/etapa1-v1) (riel con varillas M5 y 3MF), [`etapa1-v3-canto/`](archivo/etapa1-v3-canto) (probetas del riel de canto) y [`etapa1-v4/`](archivo/etapa1-v4) (riel de 8 ranuras con ductos y base de PVC, su BOM) | Solo referencia |

[`materiales.md`](materiales.md) justifica la elección de materiales.

- Etapa 1: `python scripts/generar_v5.py --ensamble` regenera STL, despiece y ensamble;
  `python scripts/armar_camas_v5.py hardware/etapa1-clasificador/stl hardware/etapa1-clasificador/impresion` las camas.
  Diseño en [`docs/09-clasificador-v5.md`](../docs/09-clasificador-v5.md); pines y cableado en
  [`docs/11-electronica-etapa1.md`](../docs/11-electronica-etapa1.md).
- Etapa 3 y archivo: `python scripts/generar_stl.py`, `python scripts/generar_3mf.py`; la v4 con
  `python scripts/generar_clasificador.py` y `python scripts/exportar_visor_3d.py`.
