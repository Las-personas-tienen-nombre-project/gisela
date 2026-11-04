"""Cierre del catálogo: cartas pendientes, variantes y prioridades autorales."""

import json

from build_expressions import (
    lit,
)


def _disable_missing(builder, design):
    cards = builder.cards
    implemented = {
        "slash",
        "blai",
        "hachazo",
        "eviscerate",
        "double_slash",
        "concentracion_clarisa",
        "concentracion_iosepus",
        "curacion",
        "magic_blast",
        "firebreath",
        "armadura_magica",
        "firesteel",
        "regeneracion",
        "groupal_shield",
        "bastonazo_clarisa",
        "bastonazo_iosepus",
        "dentellada",
        "zarpa",
        "coletazo",
        "fenix",
        "grito_de_guerra",
        "wingblast",
        "preponderancia",
        "agarraguirre",
        "stance_aggressive",
    }
    passive = {
        s["id"] for s in design["skills"] if s["type"] in ("passive", "triggered")
    }
    for cid, card in cards.items():
        if cid in implemented or cid in passive:
            continue
        card["play"]["requires"] = {"constant": False}
        card["description"] = {
            "text": "No ejecutable en v0.7.1: requiere contrato general o decisión autoral pendiente."
        }
        card["play"]["effects"] = []

    return len(implemented)


def _add_variants(builder):
    package, cards = builder.package, builder.cards
    HEROES = builder.people[:-1]
    # Especializaciones de destinatario generadas en la CAPA AUTORAL.
    # El motor solo recibe cartas y efectos ordinarios; no conoce prioridades
    # de sanadores, recursos HP ni identificadores de participantes.
    variants = {
        "curacion": "clarisa",
        "fenix": "clarisa",
        "regeneracion": "clarisa",
        "armadura_magica": "iosepus",
        "firesteel": "iosepus",
    }
    for base_id, owner in variants.items():
        base_card = cards[base_id]
        for who in HEROES:
            if who == "parnecio":
                continue
            clone = json.loads(
                json.dumps(base_card, ensure_ascii=False)
                .replace("parnecio", who)
                .replace("Parnecio", who.capitalize())
            )
            clone["id"] = base_id + "_" + who
            package["cards"].append(clone)
            package["initial_state"]["skills"].append(
                {
                    "id": clone["id"] + "_01",
                    "card": clone["id"],
                    "character": owner,
                    "zone": "hand",
                }
            )
            if base_id == "regeneracion":
                builder.define("regen_snapshot_" + who, 0)
            if base_id in ("regeneracion", "armadura_magica", "firesteel"):
                original = {
                    "regeneracion": "ef_regen_parnecio",
                    "armadura_magica": "ef_armadura_parnecio",
                    "firesteel": "ef_firesteel_parnecio",
                }[base_id]
                eff = next(c for c in package["cards"] if c["id"] == original)
                copy_effect = json.loads(
                    json.dumps(eff, ensure_ascii=False)
                    .replace("parnecio", who)
                    .replace("Parnecio", who.capitalize())
                )
                package["cards"].append(copy_effect)


PRIORITIES = {
    "gillius": ["stance_aggressive", "grito_de_guerra", "eviscerate", "hachazo"],
    "clarisa": [
        "fenix",
        "groupal_shield",
        "regeneracion",
        "curacion",
        "concentracion_clarisa",
        "bastonazo_clarisa",
    ],
    "iosepus": [
        "agarraguirre",
        "armadura_magica",
        "firesteel",
        "magic_blast",
        "concentracion_iosepus",
        "bastonazo_iosepus",
    ],
    "tegularis": [
        "firebreath",
        "wingblast",
        "coletazo",
        "zarpa",
        "dentellada",
        "preponderancia",
    ],
}


def _npc_candidates(builder):
    package = builder.package
    HEROES = builder.people[:-1]
    # NPC: solo candidatos implementados para no consumir oportunidades con NO-OP.
    by_actor = {actor: list(items) for actor, items in PRIORITIES.items()}
    # Las variantes compiladas son cartas distintas y se cuentan en la
    # capacidad declarada para esta práctica, no se modifica la regla del motor.
    for capacity in package["initial_state"]["capacities"]:
        capacity["hand"] = sum(
            x["character"] == capacity["character"] and x["zone"] == "hand"
            for x in package["initial_state"]["skills"]
        )
    # Prioridades condicionadas tras CADA acción; el validador comprueba
    # propiedad y parámetros. La selección de objetivo es una carta del autor.
    for w in HEROES:
        if w != "parnecio":
            by_actor["clarisa"].insert(0, "fenix_" + w)
            by_actor["clarisa"].insert(4, "curacion_" + w)
            by_actor["clarisa"].insert(5, "regeneracion_" + w)
            by_actor["iosepus"].insert(1, "armadura_magica_" + w)
            by_actor["iosepus"].insert(2, "firesteel_" + w)
    for p in package["actuation"]["participants"]:
        if p["character"] in by_actor:
            p["candidates"] = [
                {
                    "skill_instance": cid + "_01",
                    **({"arguments": {"x": lit(10)}} if cid == "magic_blast" else {}),
                }
                for cid in by_actor[p["character"]]
            ]
            p["allow_pass"] = True


def complete_catalog(builder, design):
    count = _disable_missing(builder, design)
    _add_variants(builder)
    _npc_candidates(builder)
    return count
