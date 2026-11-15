# Visor 3D de las etapas 1 y 2

Genera `docs/visor-etapas-1-2.html`: la torre de la etapa 1 (v5 con el disco H02e, el tope H04, la paleta G03 y el adaptador A01 del TCS3200), la banda v7 de la etapa 2 y la electrónica con su cableado, en los colores de filamento del montaje.

```bash
pip install manifold3d numpy trimesh
cd scripts/visor_etapas
python torre.py ../ torre.json ../../hardware/etapa1-clasificador/stl/A01_adaptador_tcs3200.stl
python banda.py ../../hardware/etapa2-transporte/v7-motor-fijo/generador torre.json datos.json
python construir.py datos.json plantilla.html ../../docs/visor-etapas-1-2.html
```

- `torre.py`: piezas de la etapa 1 desde `scripts/generar_v5.py` y `scripts/generar_ajustes_tolva.py`, más el 28BYJ-48, el SG90, las barreras IR y el TCS3200. Pasa todo al marco de la banda (X igual, Y = z, Z = y).
- `banda.py`: piezas de la v7, el NEMA17, la barrera de referencia, la caja de la electrónica (ESP32-S3, placa de expansión, protoboard con A4988, ULN2003, fuente) y el recorrido de los cables.
- `construir.py`: inserta los datos en `plantilla.html`. Nota: al construir la página de `docs/` hay que añadir la cabecera HTML (doctype, charset y viewport).
