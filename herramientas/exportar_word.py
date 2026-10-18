#!/usr/bin/env python3
"""Expande los archivos \input del proyecto para su conversión a Word."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
PATTERN = re.compile(r"(?m)^(?![ \t]*%)([ \t]*)\\input\{([^}]+)\}")

def expand(path: Path, active: tuple[Path, ...] = ()) -> str:
    path = path.resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f"Entrada fuera del repositorio: {path}")
    if path in active:
        raise ValueError(f"Referencia circular de \\input: {path}")
    text = path.read_text(encoding="utf-8")

    def replace(match: re.Match) -> str:
        relative = match.group(2).strip()
        target = (path.parent / relative)
        if not target.suffix:
            target = target.with_suffix(".tex")
        if not target.is_file():
            raise FileNotFoundError(f"\\input no encontrado: {target}")
        return "\n% INICIO: " + relative + "\n" + expand(target, (*active, path)) + "\n% FIN: " + relative + "\n"

    return PATTERN.sub(replace, text)

if __name__ == "__main__":
    output = ROOT / "build" / "main_expandido.tex"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(expand(ROOT / "main.tex"), encoding="utf-8")
    print(f"Documento expandido: {output}")
