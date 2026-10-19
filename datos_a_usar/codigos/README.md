# Unificar archivos Parquet WNBA

Instala las dependencias con `python -m pip install pandas pyarrow`.

Ejecuta desde la raíz del repositorio:

```bash
python datos_a_usar/codigos/unificar_parquet.py
```

Para generar solo las alineaciones por juego:

```bash
python datos_a_usar/codigos/unificar_parquet.py --categoria game_lineups
```

Esto genera `datos_a_usar/datos_globales/game_lineups/line_ups_global.parquet`.

Para limitar los años de todas las categorías:

```bash
python datos_a_usar/codigos/unificar_parquet.py --desde 2024 --hasta 2026
```

Cada fila lleva `anio` extraído del nombre del archivo original. Se conserva la columna `season` si existe.
Las variantes de `leaguedash` se mantienen separadas: `lineups_base`, `lineups_advanced`, `lineups_master`, etc.
Los archivos globales se crean al ejecutar el script, sin modificar los originales.

Verificación rápida:

```python
import pandas as pd
df = pd.read_parquet("datos_a_usar/datos_globales/game_lineups/line_ups_global.parquet")
print(df["anio"].value_counts().sort_index())
print(df.head())
```
