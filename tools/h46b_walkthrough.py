"""Recorridos de la adaptación H4.6b exclusivamente por Observe/Act."""

from __future__ import annotations

import argparse
import json
import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gisela.contracts.admit_package import admit_package_file
from gisela.engine.runtime import new_session, restore_session
from tools.h46_walkthrough import advance

PACKAGE = (
    Path(__file__).resolve().parents[1]
    / "gisela/packages/h46b_central_clasificadora.package.json"
)
SEED = "0" * 64


@lru_cache(maxsize=1)
def admitted():
    return admit_package_file(PACKAGE)


def settle(session, verify=False):
    """Avanza los pasos sin elección; no selecciona opciones por el jugador."""
    while True:
        view = session.observe()
        offered = [a["id"] for a in view["actions"] if a["enabled"]]
        if offered != ["continue"]:
            return view
        if verify:
            clone = restore_session(admitted(), session.export())
            assert clone.observe() == view
            assert clone.export() == session.export()
        advance(session, "continue")


def take(session, name, verify=False):
    advance(session, name)
    return settle(session, verify)


def play(route="casete", seed=SEED, verify=False):
    session = new_session(admitted(), seed=seed)
    take(session, "tomar_turno", verify)
    take(session, "saludar" if route == "casete" else "ponerse_a_trabajar", verify)
    if route == "casete":
        for action in (
            "ir_primer_piso",
            "hablar_marcela",
            "preguntar_futbol",
            "ofrecer_ayuda",
            "llevar_carro",
            "ir_ascensor",
            "comentar_trenza",
            "decir_verdad",
            "volver_porteria",
            "conversar_musica",
            "prestar_casete",
            "preguntar_araya",
            "ir_puesto_b",
            "probar_radio",
            "volver_porteria",
        ):
            take(session, action, verify)
    while session.export()["world_time"] < "1998-07-24T23:00:00-04:00":
        take(session, "esperar_hora", verify)
    take(session, "cerrar_turno", verify)
    take(session, "avisar_base" if route == "radio" else "mirar_fijo", verify)
    assert session.observe()["status"] == "ended"
    return session


def main():
    parser = argparse.ArgumentParser(
        description="H4.6b: jornada de Central Clasificadora"
    )
    parser.add_argument(
        "--route", choices=("casete", "solo", "radio"), default="casete"
    )
    parser.add_argument("--seed", default=SEED)
    parser.add_argument("--verify-restores", action="store_true")
    parser.add_argument("--save", type=Path)
    args = parser.parse_args()
    session = play(args.route, args.seed, args.verify_restores)
    snapshot = session.export()
    if args.save:
        args.save.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps(
            {
                "route": args.route,
                "ending": snapshot["ending"],
                "turn": snapshot["turn"],
                "world_time": snapshot["world_time"],
                "facts": [i["fact"] for i in snapshot["history"]["facts"]],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
