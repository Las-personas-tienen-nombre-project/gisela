"""Rebuild the existing noncombat MVP using reusable narrative constructors.

The existing package supplies cards, manifest and initial world; node logic
is compiled from authoring expressions. This is a compatibility proof, not
an alternative runtime or a replacement for the published canonical source.
"""

import argparse
import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import authoring_narrative as n
from tools.authoring_expressions import eq, lit, put, var

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "gisela/packages/mvp_casete.package.json"


def compile_package(base):
    """Rebuild authored nodes and reaction without modifying the input."""
    result = copy.deepcopy(base)
    give = n.option(
        "prestar",
        "Prestar el casete",
        {
            "next": n.target_step("entrega"),
            "enabled_if": n.owns("alberto", "casete_01"),
            "effects": [
                n.transfer("casete_01", "alberto", "gisela"),
                n.record_fact("alberto_presto_casete"),
                put("casete_prestado", lit(True)),
            ],
        },
    )
    keep = n.option(
        "guardar", "Guardar el casete", {"next": n.target_step("despedida")}
    )
    result["nodes"] = [
        n.node(
            "inicio",
            [
                n.narrate(
                    "entrada", "Alberto llega a la portería con un casete de música."
                ),
                n.show_scene("fondo", "porteria_noche"),
                n.dialogue("saludo", "gisela", "Hola, Alberto. ¿Trajiste el casete?"),
                n.choice("decision", [give, keep]),
                n.narrate("entrega", "Gisela recibe el casete."),
                n.transition("ir_a_cierre", n.target_step("cierre")),
                n.narrate("despedida", "Alberto se guarda el casete."),
                n.condition(
                    "cierre",
                    n.has_fact("alberto_presto_casete"),
                    (
                        n.target_node("final_compartido"),
                        n.target_node("final_solitario"),
                    ),
                ),
            ],
        ),
        n.node("final_compartido", [n.ending("terminar", "compartido")]),
        n.node("final_solitario", [n.ending("terminar", "solo")]),
    ]
    result["rules"] = [
        n.fact_reaction(
            "reaccion_gisela",
            "alberto_presto_casete",
            {
                "when": n.negated(eq(var("gisela_reacciono"), "eq", lit(True))),
                "effects": [put("gisela_reacciono", lit(True))],
            },
        )
    ]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check without writing")
    args = parser.parse_args()
    published = json.loads(CANON.read_text(encoding="utf-8"))
    compiled = compile_package(published)
    if args.check:
        if compiled != published:
            raise SystemExit("ERROR: narrative MVP differs from authored output")
        print("OK: narrative MVP matches authored nodes and reaction")
    else:
        print(json.dumps(compiled, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
