"""Compila variantes de presentación autocontenidas desde el canon v0.7.8.

Las variantes cambian solo ``presentation``. Nunca alteran lógica, eventos,
actuación, ni contratos. El archivo de fuente identifica variantes por nombre,
no por índices ni rutas dentro de un JSON Patch.
"""

import json
import argparse
from pathlib import Path
import sys

# Allow execution by absolute script path without installing authoring tools.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.authoring_composition import replace_field, safe_output

HERE = Path(__file__).resolve().parent
CANON = HERE / "10_balance_v078.package.json"
SOURCES = HERE / "v081_v082_presentations.json"


def compile_variants(directory=HERE, check=False):
    """Genera cada variante completa. Valida todas las fuentes antes de escribir."""
    directory = Path(directory)
    canon = json.loads((directory / CANON.name).read_text(encoding="utf-8"))
    definitions = json.loads((directory / SOURCES.name).read_text(encoding="utf-8"))
    if not isinstance(definitions, dict) or not definitions:
        raise ValueError("La lista de variantes de presentación está vacía")
    payloads = {}
    for filename, presentation in definitions.items():
        if not isinstance(filename, str) or not filename.endswith(".package.json"):
            raise ValueError("Nombre de variante inválido")
        if filename == CANON.name:
            raise ValueError("La variante debe ser distinta al canon")
        safe_output(directory, filename, depth=1)
        if not isinstance(presentation, dict) or not isinstance(presentation.get("id"), str):
            raise ValueError(f"Presentación inválida: {filename}")
        package = replace_field(canon, "presentation", presentation)
        payloads[filename] = (json.dumps(package, ensure_ascii=False, indent=2) + "\n")
    for filename, payload in payloads.items():
        target = directory / filename
        if check:
            if not target.is_file() or target.read_bytes() != payload.encode("utf-8"):
                raise ValueError(f"Variante diferente de la fuente: {filename}")
        else:
            if not target.is_file() or target.read_bytes() != payload.encode("utf-8"):
                target.write_text(payload, encoding="utf-8")
    return sorted(payloads)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verificar sin escribir")
    args = parser.parse_args()
    for filename in compile_variants(check=args.check):
        print("Compilado:", filename)
