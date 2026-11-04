"""Compila v0.7.2 desde la definición v0.7.1, sin modificar el catálogo v0.7.1."""

import json
from pathlib import Path

from build_expressions import (
    active,
    add,
    cond_all,
    damage,
    eq,
    lit,
    maximum,
    message,
    mul,
    put,
    reduce_damage,
    roll,
    stat,
    sub,
    var,
)
from build_json import compact_json

HERE = Path(__file__).resolve().parent
source = HERE / "07_cartas_v071.package.json"
output = HERE / "08_desenlaces_v072.package.json"
package = json.loads(source.read_text())
package["manifest"]["id"] = "tegularis_acontecimientos_v072_laboratorio"
variables = {v["id"] for v in package["manifest"]["variables"]}


def define(name, value):
    if name not in variables:
        package["manifest"]["variables"].append(
            {"scope": "session", "id": name, "type": "integer", "initial": value}
        )
        package["initial_state"]["session_variables"][name] = value
        variables.add(name)


def any_heroes():
    return {"any": [active(w) for w in ("parnecio", "gillius", "clarisa", "iosepus")]}


def no_heroes():
    return {"not": any_heroes()}


def covered_damage(w):
    # Ataque final sin Hit ni Evasion: reducción mágica por destinatario.
    amount = maximum(
        lit(0),
        sub(sub(var("burst_raw"), var("defense_" + w)), reduce_damage(w, "magic")),
    )
    return [
        damage(w, amount),
        message(
            "ÚLTIMA LLAMA hizo {amount} puntos de daño a " + w + ".", amount=amount
        ),
    ]


def needs_pride():
    return cond_all(
        active("tegularis"),
        eq(
            mul(var("hp_tegularis"), lit(10)),
            "lte",
            mul(var("max_hp_tegularis"), lit(3)),
        ),
    )


def dead_dragon():
    return eq(var("hp_tegularis"), "lte", lit(0))


def add_pride_effect():
    package["cards"].append(
        {
            "id": "ef_pride_volcan",
            "kind": "effect",
            "title": {"text": "Pride of the Volcan Son"},
            "stacking": "unique_per_target",
            "on_reapply": "refresh",
            "modifiers": [
                {"stat": name, "amount": 1}
                for name in (
                    "strength",
                    "openness",
                    "fortune",
                    "intelligence",
                    "awareness",
                )
            ],
            "granted_traits": ["pride_redux"],
        }
    )
    # Trait para las consultas efectivamente utilizadas por las cartas.
    pride = next(x for x in package["traits"]["traits"] if x["id"] == "pride_redux")
    for label in ("physical_damage_reduction", "magic_damage_reduction"):
        pride["contributions"].append(
            {
                "id": "contrib_" + label,
                "when": {"role": "defender", "all_tags": [label]},
                "add": {"slot": "bonus", "amount": 1},
            }
        )


def add_policies():
    define("burst_die", 0)
    define("burst_raw", 0)
    # exact-once y persistencia de disparos en el reloj autoral (no variables globales).
    package["actuation"]["event_policies"] = [
        {
            "id": "pride_of_the_volcan_son",
            "phase": "immediate",
            "when": needs_pride(),
            "effects": [
                {
                    "op": "apply_effect",
                    "effect": "ef_pride_volcan",
                    "target": "tegularis",
                },
                message(
                    "Tegularis despierta PRIDE OF THE VOLCAN SON (+1 a los cinco atributos)."
                ),
            ],
        },
        {
            "id": "ultima_llama",
            "phase": "after_action",
            "when": dead_dragon(),
            "effects": [
                roll("burst_die"),
                put(
                    "burst_raw",
                    add(lit(30), stat("tegularis", "intelligence"), var("burst_die")),
                ),
                message(
                    "Tegularis desata ÚLTIMA LLAMA: {raw} puntos de daño bruto.",
                    raw=var("burst_raw"),
                ),
            ],
            "outcomes": [
                {
                    "when": eq(var("group_shield"), "gt", lit(0)),
                    "effects": [
                        put("group_shield", lit(0)),
                        message("GROUPAL SHIELD neutralizó la explosión final."),
                    ],
                },
                {
                    "when": eq(var("group_shield"), "eq", lit(0)),
                    "effects": [
                        op
                        for w in ("parnecio", "gillius", "clarisa", "iosepus")
                        for op in covered_damage(w)
                    ],
                },
            ],
        },
    ]
    # Resultado resuelto únicamente después del disparo final.
    package["actuation"]["outcome_policies"] = [
        {"id": "destruccion_mutua", "when": cond_all(dead_dragon(), no_heroes())},
        {"id": "victoria", "when": cond_all(dead_dragon(), any_heroes())},
        {"id": "derrota", "when": cond_all({"not": dead_dragon()}, no_heroes())},
    ]
    _snapshot_burst_shield()


def _snapshot_burst_shield():
    # Las dos ramas de la explosión deben elegirse con el estado ANTERIOR
    # a sus consecuencias; la regla del motor evalúa ramas independientes.
    # Por eso se incorpora la protección como dos reglas exclusivas antes
    # de afectar el escudo; ver la normalización posterior.
    burst = package["actuation"]["event_policies"][1]
    # La rama con escudo deja group_shield=0, por lo que la otra rama debe
    # descartarse antes. Una variable local de instantánea es autoral.
    define("burst_shield_snapshot", 0)
    burst["effects"].insert(0, put("burst_shield_snapshot", var("group_shield")))
    burst["outcomes"][0]["when"] = eq(var("burst_shield_snapshot"), "gt", lit(0))
    burst["outcomes"][1]["when"] = eq(var("burst_shield_snapshot"), "eq", lit(0))


add_pride_effect()
add_policies()
output.write_text(compact_json(package))
print(output)
