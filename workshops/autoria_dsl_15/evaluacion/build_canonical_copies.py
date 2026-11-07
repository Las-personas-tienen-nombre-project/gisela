"""Compile workshop exercises/solutions from the immutable productive package.

Each overlay is a small, reviewed set of edits. List elements with stable identities
are addressed by identifier; anonymous list elements require an explicit old-value
precondition, so a changed canonical structure fails instead of silently corrupting
an exercise. This operates only at authoring time, never in the runtime.
"""

import argparse
import json
from pathlib import Path
import sys

# Keep direct command-line execution independent of Python installation mode.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.authoring_composition import apply_overlay, safe_output

ROOT = Path(__file__).resolve().parents[3]
WORKSHOP = ROOT / "workshops" / "autoria_dsl_15"
CANON = ROOT / "packages" / "tegularis_the_son_of_the_volcan" / "14_presentacion_semantica_v082d.package.json"
OVERLAYS = Path(__file__).with_name("canonical_overlays.json")


def compile_copies(write=False, canon_path=CANON, overlays_path=OVERLAYS, workshop=WORKSHOP):
    canon = json.loads(Path(canon_path).read_text(encoding="utf-8"))
    overlays = json.loads(Path(overlays_path).read_text(encoding="utf-8"))
    if not isinstance(overlays, dict) or len(overlays) != 68:
        raise ValueError("Expected 68 declared workshop copies (units 3–8)")
    outputs = {}
    for relative, operations in sorted(overlays.items()):
        target = safe_output(workshop, relative, depth=3)
        path = Path(relative)
        if path.parts[0] not in ("ejercicios", "soluciones") or not path.name.endswith(".package.json"):
            raise ValueError(f"Invalid exercise path: {relative!r}")
        try:
            result = apply_overlay(canon, operations)
        except ValueError as exc:
            raise ValueError(f"Invalid copy {relative!r}: {exc}") from exc
        outputs[target] = result
    # Validate all outputs before writing any file.
    if not write:
        for target, result in outputs.items():
            if not target.is_file() or json.loads(target.read_text(encoding="utf-8")) != result:
                raise ValueError(f"Workshop copy differs from declared source: {target}")
    else:
        for target, result in outputs.items():
            if target.is_file() and json.loads(target.read_text(encoding="utf-8")) == result:
                continue  # Keep reviewed original formatting and timestamps unchanged.
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(outputs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate the 68 copies")
    args = parser.parse_args()
    print("Workshop copies verified/generated:", compile_copies(write=args.write))
