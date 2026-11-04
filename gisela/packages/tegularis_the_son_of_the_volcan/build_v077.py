"""Cierre autoral incremental: Bless y redirección de Protección.

La compilación transforma cartas y condiciones; el motor no sabe qué es un
ataque, una protección ni un punto de vida.
"""

import copy
import json
from pathlib import Path

from build_expressions import (
    active,
    calc,
    cond_all,
    cost,
    damage,
    eq,
    lit,
    maximum,
    message,
    reduce_damage,
    sub,
    var,
)
from build_json import compact_json

HERE = Path(__file__).resolve().parent
PACKAGE = json.loads((HERE / "08_desenlaces_v072.package.json").read_text())
HEROES = ("parnecio", "gillius", "clarisa", "iosepus")
ALLIES = HEROES[1:]
CARDS = {c["id"]: c for c in PACKAGE["cards"]}
MAIN = {x["character"]: x["main_stat"] for x in PACKAGE["actuation"]["participants"]}


def skill(name, target, play):
    effects, requires = play
    template = copy.deepcopy(CARDS[name])
    ident = name if target == "parnecio" else name + "_" + target
    template["id"] = ident
    template["play"]["effects"] = effects
    template["play"]["requires"] = requires
    template["play"]["outcomes"] = []
    if ident == name:
        CARDS[name].update(template)
    else:
        PACKAGE["cards"].append(template)
        PACKAGE["initial_state"]["skills"].append(
            {
                "id": ident + "_01",
                "card": ident,
                "character": template.get(
                    "owner", "clarisa" if name == "bless" else "parnecio"
                ),
                "zone": "hand",
            }
        )
    return ident


def bless():
    for who in HEROES:
        effect = "ef_bless_" + who
        PACKAGE["cards"].append(
            {
                "id": effect,
                "kind": "effect",
                "title": {"text": "Bless"},
                "stacking": "unique_per_target",
                "on_reapply": "refresh",
                "actuation_turns": 3,
                "modifiers": [{"stat": MAIN[who], "amount": 2}],
            }
        )
        skill(
            "bless",
            who,
            (
                [
                    cost("clarisa", "mp", 10),
                    {"op": "apply_effect", "effect": effect, "target": who},
                    message("BLESS aumentó en 2 el atributo principal de " + who + "."),
                ],
                cond_all(
                    active("clarisa"),
                    active(who),
                    eq(var("mp_clarisa"), "gte", lit(10)),
                ),
            ),
        )
        if who != "parnecio":
            PACKAGE["actuation"]["participants"][2]["candidates"].insert(
                12, {"skill_instance": "bless_" + who + "_01"}
            )
    PACKAGE["actuation"]["participants"][2]["candidates"].insert(
        12, {"skill_instance": "bless_01"}
    )


def protection():
    for who in ALLIES:
        effect = "ef_proteccion_" + who
        PACKAGE["cards"].append(
            {
                "id": effect,
                "kind": "effect",
                "title": {"text": "Protección"},
                "stacking": "unique_per_target",
                "on_reapply": "refresh",
                "actuation_turns": 2,
                "expire_on_actor_turn_start": True,
            }
        )
        skill(
            "proteccion",
            who,
            (
                [
                    {"op": "apply_effect", "effect": effect, "target": "parnecio"},
                    message("Parnecio protege a " + who + " con su escudo."),
                ],
                cond_all(
                    active("parnecio"),
                    active(who),
                    *[
                        {
                            "not": {
                                "has_effect": {
                                    "target": "parnecio",
                                    "effect": "ef_proteccion_" + x,
                                }
                            }
                        }
                        for x in ALLIES
                    ],
                ),
            ),
        )
    # No asignamos efectos sobre los participantes ni nuevas reglas en el motor.


def protected(who):
    return {"has_effect": {"target": "parnecio", "effect": "ef_proteccion_" + who}}


def _mitigated(raw, style):
    # Orden: reducción defensiva del defensor, luego 50 % del remanente.
    remainder = maximum(
        lit(0), sub(sub(raw, var("defense_parnecio")), reduce_damage("parnecio", style))
    )
    return calc("floor_divide", remainder, lit(2))


def rewrite_area(card_id, style, raw):
    """Una única intercepción en un área: protegido no recibe el golpe."""
    card = CARDS[card_id]
    outcomes = card["play"]["outcomes"]
    for outcome in list(outcomes):
        effects = outcome.get("effects", [])
        if not effects:
            continue
        # Solo ramas que causan daño, nunca ramas de evasión/parálisis.
        hit = next(
            (
                x
                for x in effects
                if x.get("op") == "set"
                and x.get("target", {}).get("var", {}).get("key", "").startswith("hp_")
            ),
            None,
        )
        if hit is None:
            continue
        target = hit["target"]["var"]["key"][3:]
        if target not in HEROES:
            continue
        old = copy.deepcopy(outcome["when"])
        if target in ALLIES:
            outcome["when"] = cond_all(old, {"not": protected(target)})
            outcomes.append(
                {
                    "when": cond_all(old, protected(target)),
                    "effects": [
                        damage("parnecio", _mitigated(raw(target), style)),
                        message(
                            "PROTECCIÓN: Parnecio recibió {amount} de "
                            + card_id
                            + " al cubrir a "
                            + target
                            + ".",
                            amount=_mitigated(raw(target), style),
                        ),
                    ],
                }
            )
        elif target == "parnecio":
            # En área, Parnecio recibe solo el ataque desviado, nunca el suyo además.
            outcome["when"] = cond_all(old, *[{"not": protected(w)} for w in ALLIES])
    return card


def group_protection():
    # El ataque de área conserva sus tiradas, pero redirige solo la rama
    # del aliado cubierto; la unicidad del efecto garantiza un solo desvío.
    rewrite_area("coletazo", "physical", lambda w: var("tail_dmg_" + w))
    rewrite_area("firebreath", "magic", lambda w: var("fire_common"))
    rewrite_area("wingblast", "magic", lambda w: var("wing_common"))


def protect_statuses():
    """Un golpe interceptado no paraliza a quien estaba protegido."""
    for outcome in CARDS["wingblast"]["play"]["outcomes"]:
        for operation in outcome["effects"]:
            if operation.get("op") != "apply_effect":
                continue
            who = operation.get("target")
            if who in ALLIES:
                outcome["when"] = cond_all(outcome["when"], {"not": protected(who)})


def protect_burst():
    """Explosión: única absorción de refilón y demás aliados intactos."""
    event = next(
        p for p in PACKAGE["actuation"]["event_policies"] if p["id"] == "ultima_llama"
    )
    branch = event["outcomes"][1]
    old = branch["effects"]
    if len(old) != len(HEROES) * 2:
        raise ValueError(
            f"ultima_llama: se esperaban {len(HEROES) * 2} efectos; hay {len(old)}"
        )
    base = eq(var("burst_shield_snapshot"), "eq", lit(0))
    replacements = []
    for index, who in enumerate(HEROES):
        ordinary = (
            cond_all(base, *[{"not": protected(x)} for x in ALLIES])
            if who == "parnecio"
            else cond_all(base, {"not": protected(who)})
        )
        replacements.append(
            {"when": ordinary, "effects": old[index * 2 : index * 2 + 2]}
        )
    for who in ALLIES:
        amount = _mitigated(var("burst_raw"), "magic")
        replacements.append(
            {
                "when": cond_all(base, protected(who)),
                "effects": [
                    damage("parnecio", amount),
                    message(
                        "PROTECCIÓN desvió ÚLTIMA LLAMA: {amount} puntos de refilón.",
                        amount=amount,
                    ),
                ],
            }
        )
    event["outcomes"][1:] = replacements


def capacities():
    for cap in PACKAGE["initial_state"]["capacities"]:
        cap["hand"] = sum(
            x["zone"] == "hand" and x["character"] == cap["character"]
            for x in PACKAGE["initial_state"]["skills"]
        )


bless()
protection()
group_protection()
protect_statuses()
protect_burst()
capacities()
PREFIXES = (
    "hp_",
    "mp_",
    "tp_",
    "defense_",
    "scratch_",
    "double_",
    "tail_",
    "wing_",
    "fire_common",
    "burst_",
    "zarpa_",
)
PACKAGE["actuation"]["public_trace_variables"] = [
    name
    for name in (item["id"] for item in PACKAGE["manifest"]["variables"])
    if name.startswith(PREFIXES)
] + ["group_shield"]
PACKAGE["manifest"]["id"] = "tegularis_v077_reglas_autorales"
(HERE / "09_cierre_autoral_v077.package.json").write_text(compact_json(PACKAGE))
print("Compilado", len(PACKAGE["cards"]), "cartas y efectos")
