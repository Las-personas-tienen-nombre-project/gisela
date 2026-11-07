"""Independent noncombat C9 example: build a whole package from authoring sources.

Does not read another package, template or runtime state. Explicit --write is
required to update the tracked artifact; --check never writes.
"""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import authoring_narrative as n
from tools import authoring_package as p
from tools.authoring_expressions import eq, lit, put, var

OUTPUT = ROOT / "gisela/packages/c9_turno_noche.package.json"


def opening_node():
    """The authored choice is independent of the package layout."""
    return n.node(
        "inicio",
        [
            n.narrate("guardia", "El teléfono de portería suena durante la ronda."),
            n.choice(
                "decision",
                [
                    n.option(
                        "atender",
                        "Contestar el teléfono",
                        {
                            "next": n.target_node("contestada"),
                            "effects": [
                                n.record_fact("llamada_atendida"),
                                put("contesto", lit(True)),
                            ],
                        },
                    ),
                    n.option(
                        "ignorar",
                        "Seguir con la ronda",
                        {"next": n.target_node("ignorada")},
                    ),
                ],
            ),
        ],
    )


def build_package():
    """Represent two narrative choices, state change and a fact reaction."""
    start = opening_node()
    answered = n.node(
        "contestada",
        [
            n.narrate("voz", "Al otro lado de la línea no responde nadie."),
            n.ending("fin", "silencio"),
        ],
    )
    ignored = n.node(
        "ignorada",
        [
            n.narrate("pasos", "El timbre deja de sonar a tus espaldas."),
            n.ending("fin", "ronda"),
        ],
    )
    meta = p.manifest("c9_turno_noche", "inicio")
    meta["variables"] = [p.variable("contesto", False), p.variable("eco", False)]
    meta["facts"] = ["llamada_atendida"]
    reaction = n.fact_reaction(
        "eco_de_llamada",
        "llamada_atendida",
        {
            "when": n.negated(eq(var("eco"), "eq", lit(True))),
            "effects": [put("eco", lit(True))],
        },
    )
    return p.assemble(
        {
            "manifest": meta,
            "nodes": [start, answered, ignored],
            "rules": [reaction],
            "initial_state": p.initial_state(variables=meta["variables"]),
            "endings": [
                p.ending("silencio", "Silencio en la línea"),
                p.ending("ronda", "La ronda continúa"),
            ],
        }
    )


def rendered():
    return (json.dumps(build_package(), ensure_ascii=False, indent=2) + "\n").encode(
        "utf-8"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    from gisela.contracts.admit_package import admit_package

    admit_package(build_package())
    generated = rendered()
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_bytes() != generated:
            raise SystemExit("ERROR: independent narrative package has drifted")
        print("OK: independent narrative package matches authored source")
        return
    # Single-file atomic replace; no claim of atomic multi-artifact updates.
    handle, temp = tempfile.mkstemp(prefix=".c9-", dir=OUTPUT.parent)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(generated)
        os.replace(temp, OUTPUT)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    print(f"Written: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
