#!/usr/bin/env python3
"""Combina Parquet de temporadas por familia sin alterar los archivos de origen."""
from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent.parent
ORIGEN = BASE / "wnba_stats"
SALIDA = BASE / "datos_globales"
PATRON = re.compile(r"(?P<familia>.+)_(?P<anio>(?:19|20)\d{2})\.parquet$", re.I)
NOMBRES = {("game_lineups", "wnba_lineups"): "line_ups_global.parquet"}


def buscar_grupos(categoria, desde, hasta):
    grupos = defaultdict(list)
    for archivo in sorted(ORIGEN.glob("*/parquet/*.parquet")):
        cat = archivo.parent.parent.name
        if categoria and cat != categoria:
            continue
        encontrado = PATRON.fullmatch(archivo.name)
        if not encontrado:
            print(f"[OMITIDO] Nombre sin año final: {archivo.name}")
            continue
        anio = int(encontrado["anio"])
        if (desde is not None and anio < desde) or (hasta is not None and anio > hasta):
            continue
        grupos[(cat, encontrado["familia"])].append((anio, archivo))
    return grupos


def combinar(categoria, familia, archivos):
    tablas = []
    esquemas = []
    for anio, archivo in sorted(archivos):
        tabla = pd.read_parquet(archivo, engine="pyarrow")
        if "anio" in tabla.columns:
            raise ValueError(f"Ya existe la columna 'anio' en {archivo}")
        if "season" in tabla.columns:
            temporadas = set(pd.to_numeric(tabla["season"], errors="coerce").dropna().astype(int))
            if temporadas and temporadas != {anio}:
                print(f"[AVISO] season no coincide con el nombre de {archivo.name}: {temporadas}")
        esquemas.append(set(tabla.columns))
        tabla.insert(0, "anio", anio)
        tablas.append(tabla)
        print(f"  {archivo.name}: {len(tabla):,} registros")

    if len(set(map(frozenset, esquemas))) > 1:
        print("[AVISO] Algunas columnas difieren entre años; los valores ausentes serán nulos.")

    global_df = pd.concat(tablas, ignore_index=True, sort=False)
    global_df["anio"] = global_df["anio"].astype("int32")

    destino = SALIDA / categoria
    destino.mkdir(parents=True, exist_ok=True)
    nombre = NOMBRES.get((categoria, familia), f"{familia}_global.parquet")
    ruta_salida = destino / nombre
    global_df.to_parquet(ruta_salida, engine="pyarrow", index=False, compression="snappy")
    print(f"  => {ruta_salida.relative_to(BASE)}: {len(global_df):,} filas")
    return ruta_salida


def main():
    p = argparse.ArgumentParser(description="Combina Parquet anuales por categoría y crea anio.")
    p.add_argument("--categoria", help="Por ejemplo: game_lineups, pbp, leaguedash")
    p.add_argument("--desde", type=int, help="Primer año, inclusivo")
    p.add_argument("--hasta", type=int, help="Último año, inclusivo")
    args = p.parse_args()
    if not ORIGEN.is_dir():
        p.error(f"No encontré los datos en {ORIGEN}")
    if args.desde and args.hasta and args.desde > args.hasta:
        p.error("--desde debe ser menor o igual a --hasta")
    grupos = buscar_grupos(args.categoria, args.desde, args.hasta)
    if not grupos:
        p.error("No encontré archivos que coincidan con los filtros.")
    for (categoria, familia), archivos in sorted(grupos.items()):
        print(f"\n[{categoria}] {familia} — {len(archivos)} archivos")
        combinar(categoria, familia, archivos)
    print("\nListo. Los originales no se modificaron.")


if __name__ == "__main__":
    main()
