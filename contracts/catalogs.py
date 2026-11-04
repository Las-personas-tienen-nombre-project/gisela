"""Ensamblado determinista de catálogos externos para paquetes GISELA.

Los archivos de autoría no se consultan después de admitir el paquete.
"""

from __future__ import annotations

import argparse
import copy
from pathlib import Path

from .admit_package import admit_package
from .canonical import canonical_json
from .semantic_validator import load_json_strict


def assemble(source: dict, catalogs: dict[str, dict[str, str]]) -> dict:
    """Construye un paquete nuevo; nunca muta la entrada."""
    result = copy.deepcopy(source)
    embedded = result.setdefault("strings", {})
    for language, entries in sorted(catalogs.items()):
        if language in embedded:
            raise ValueError("Catálogo duplicado: " + language)
        if not isinstance(entries, dict):
            raise TypeError("Catálogo inválido: " + language)
        embedded[language] = copy.deepcopy(entries)
    admit_package(result)  # Estructura, claves, idioma base, semántica.
    return result


def assemble_files(source: Path, directory: Path, destination: Path) -> str:
    """Lee JSON estricto, verifica admisión y emite una salida canónica."""
    if not directory.is_dir():
        raise ValueError("Directorio de catálogos inexistente")
    catalogs = {
        file.stem: load_json_strict(file) for file in sorted(directory.glob("*.json"))
    }
    if not catalogs:
        raise ValueError("No se encontraron catálogos JSON")
    package = assemble(load_json_strict(source), catalogs)
    digest = admit_package(package).digest
    destination.write_bytes(canonical_json(package) + b"\n")
    return digest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Ensamblar localizaciones GISELA")
    parser.add_argument("package", type=Path)
    parser.add_argument("locales", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    print(assemble_files(args.package, args.locales, args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
