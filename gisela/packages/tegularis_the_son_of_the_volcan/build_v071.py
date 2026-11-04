"""Compila las reglas conocidas del workshop a un paquete DSL 1.5.

No introduce algoritmos de combate en el motor. Las cartas incompletas
permanecen deshabilitadas, no se simulan como ataques gratuitos.
"""

from __future__ import annotations

import json
from pathlib import Path

from build_authoring import AttackDefinition, CardBuilder, EffectDefinition, SkillPlay
from build_catalog import complete_catalog
from build_expressions import (
    ResourceGain,
    active,
    add,
    calc,
    cond_all,
    cost,
    damage,
    eq,
    evasion,
    gain,
    has_resource,
    heal,
    inc,
    lit,
    maximum,
    message,
    minimum,
    mul,
    put,
    reduce_damage,
    roll,
    stat,
    sub,
    trait,
    var,
)
from build_json import compact_json

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "05_actuacion_v07_laboratorio.package.json"
OUTPUT = ROOT / "07_cartas_v071.package.json"
DESIGN = json.loads((ROOT / "02_diseno_productivo_completo.json").read_text())
PEOPLE = ("parnecio", "gillius", "clarisa", "iosepus", "tegularis")
HEROES = PEOPLE[:-1]


package = json.loads(SOURCE.read_text())
package["manifest"]["id"] = "tegularis_cartas_v071_contratos_parciales"
# La práctica narrativa heredada mantiene su propio contador de daño y TP.
# El encuentro nuevo NO la ejecuta como punto de entrada: evita dos fuentes
# de verdad y conserva el paquete de práctica como archivo independiente.
package["manifest"]["entry"] = {"node": "entrada_v071"}
package["nodes"] = [
    {
        "id": "entrada_v071",
        "steps": [
            {
                "id": "introduccion",
                "op": "narrate",
                "text": {
                    "text": "Tegularis, el Hijo del Volcán. Encuentro declarativo v0.7.1. "
                    "Las rondas se recorren en GLAUQUIR con --actuation."
                },
            }
        ],
    }
]

builder = CardBuilder(package)
define = builder.define
equip = builder.equip
hit_and_damage = builder.hit_and_damage
effect_card = builder.effect_card


builder.initial_resources()
builder.setup_resources()
# single-use area shield declared in package; duration not managed in this stage.
define("group_shield", 0)
# improve existing skill declarations; no old phantom damage accounting
cards = builder.cards


# Ataques de acuerdo con las reglas explícitas. Las evasiones fijas se
# conservan como límite de la vertical anterior y no se presentan como dinámicas.
hit_and_damage(AttackDefinition("slash", "parnecio", "tegularis", tp_gain=10))
hit_and_damage(AttackDefinition("blai", "parnecio", "tegularis", extra=8, tp_cost=30))
hit_and_damage(AttackDefinition("hachazo", "gillius", "tegularis", tp_gain=10))
hit_and_damage(
    AttackDefinition("eviscerate", "gillius", "tegularis", extra=8, tp_cost=30)
)


# Double Slash: dos conjuntos separados de tiradas, ambos con consecuencias
# independientes; la primera tirada no determina el resultado de la segunda.


# Los outcomes se evalúan después de todos los effects, pero las tiradas
# son independientes y cada resultado mantiene su identificador.
builder.double_slash()
# Concentración: restaurar MP con tope efectivo y sin inventar tiradas.
for cid, w in [
    ("concentracion_clarisa", "clarisa"),
    ("concentracion_iosepus", "iosepus"),
]:
    equip(
        cid,
        SkillPlay(
            [
                gain(w, "mp", ResourceGain(lit(30), 1000)),
                put("mp_" + w, minimum(var("max_mp_" + w), var("mp_" + w))),
                message(w + " recuperó maná: {mp} MP.", mp=var("mp_" + w)),
            ],
            cond_all(active(w), eq(var("mp_" + w), "lt", var("max_mp_" + w))),
        ),
    )
# Curación sin resurrección, objetivo autoral provisional: integrante más herido
# parametrización elegible desde Observe/Act pertenece a la siguiente integración.
equip(
    "curacion",
    SkillPlay(
        [
            cost("clarisa", "mp", 20),
            roll("scratch_damage_clarisa"),
            put(
                "scratch_damage_clarisa",
                add(
                    lit(20),
                    stat("clarisa", "intelligence"),
                    var("scratch_damage_clarisa"),
                ),
            ),
            heal("parnecio", var("scratch_damage_clarisa")),
            message(
                "CURACIÓN restauró salud a Parnecio; HP actual: {hp}.",
                hp=var("hp_parnecio"),
            ),
        ],
        cond_all(
            active("clarisa"),
            active("parnecio"),
            has_resource("clarisa", "mp", 20),
            eq(var("hp_parnecio"), "lt", var("max_hp_parnecio")),
        ),
    ),
)
# Magic Blast con parámetro autoral x; el NPC utiliza x=10 y sigue
# estando sujeto a costo y disponibilidad de maná. No se permite x negativo.
magic = cards["magic_blast"]
magic["play"]["parameters"] = [{"id": "x", "kind": "integer", "min": 0, "max": 100}]
x = {"parameter": "x"}
# x se liga antes de interpretar la expresión.
magic_cost = add(lit(1), x)
magic_hit_bonus = calc("floor_divide", x, lit(10))
magic_effects = [
    put("mp_iosepus", sub(var("mp_iosepus"), magic_cost)),
    roll("scratch_hit_iosepus"),
    inc(
        "scratch_hit_iosepus",
        add(
            stat("iosepus", "awareness"),
            magic_hit_bonus,
            trait("iosepus", ["hit"], "actor"),
        ),
    ),
    roll("scratch_eva_iosepus"),
    inc("scratch_eva_iosepus", evasion("tegularis")),
    roll("scratch_damage_iosepus"),
    put(
        "scratch_damage_iosepus",
        add(var("scratch_damage_iosepus"), stat("iosepus", "intelligence"), x),
    ),
]
magic_hit = eq(var("scratch_hit_iosepus"), "gt", var("scratch_eva_iosepus"))
equip(
    "magic_blast",
    SkillPlay(
        magic_effects,
        cond_all(
            active("iosepus"),
            active("tegularis"),
            eq(var("mp_iosepus"), "gte", magic_cost),
        ),
        [
            {
                "when": magic_hit,
                "effects": [
                    damage(
                        "tegularis",
                        maximum(
                            lit(0),
                            sub(
                                var("scratch_damage_iosepus"),
                                reduce_damage("tegularis", "magic"),
                            ),
                        ),
                    ),
                    message(
                        "MAGIC BLAST hizo {damage} puntos a Tegularis.",
                        damage=maximum(
                            lit(0),
                            sub(
                                var("scratch_damage_iosepus"),
                                reduce_damage("tegularis", "magic"),
                            ),
                        ),
                    ),
                ],
            },
            {
                "when": {"not": magic_hit},
                "effects": [message("Tegularis esquivó MAGIC BLAST.")],
            },
        ],
    ),
)
# Firebreath: daño común por ataque; cada héroe hace su propia
# tirada de Hit/Evasion. Las protecciones específicas están pendientes.
for w in HEROES:
    define("fire_hit_" + w, 0)
    define("fire_eva_" + w, 0)
fire = [
    cost("tegularis", "mp", 50),
    roll("fire_common"),
    put(
        "fire_common",
        add(lit(25), stat("tegularis", "intelligence"), var("fire_common")),
    ),
]
define("fire_common", 0)
for w in HEROES:
    fire.extend(
        [
            roll("fire_hit_" + w),
            inc(
                "fire_hit_" + w,
                add(
                    stat("tegularis", "awareness"), trait("tegularis", ["hit"], "actor")
                ),
            ),
            roll("fire_eva_" + w),
            inc("fire_eva_" + w, evasion(w)),
        ]
    )
fire_out = []
for w in HEROES:
    check = cond_all(active(w), eq(var("fire_hit_" + w), "gt", var("fire_eva_" + w)))
    amount = maximum(
        lit(0),
        sub(sub(var("fire_common"), var("defense_" + w)), reduce_damage(w, "magic")),
    )
    fire_out.append(
        {
            "when": check,
            "effects": [
                damage(w, amount),
                message("FIREBREATH hizo {damage} puntos a " + w + ".", damage=amount),
            ],
        }
    )
    fire_out.append(
        {
            "when": cond_all(
                active(w), {"not": eq(var("fire_hit_" + w), "gt", var("fire_eva_" + w))}
            ),
            "effects": [message(w + " esquivó FIREBREATH.")],
        }
    )
equip(
    "firebreath",
    SkillPlay(
        fire,
        cond_all(active("tegularis"), has_resource("tegularis", "mp", 50)),
        fire_out,
    ),
)


# Efectos autorales ligados al turno del beneficiario. Las cartas de
# efectos usan exactamente el mismo contrato público de GISELA.


effect_card(
    EffectDefinition(
        "ef_armadura_parnecio",
        2,
        [inc("defense_parnecio", lit(3))],
        [inc("defense_parnecio", lit(-3))],
    )
)
effect_card(
    EffectDefinition(
        "ef_firesteel_parnecio",
        2,
        [inc("firesteel_parnecio", lit(3))],
        [inc("firesteel_parnecio", lit(-3))],
    )
)
define("regen_snapshot_parnecio", 0)
effect_card(
    EffectDefinition(
        "ef_regen_parnecio",
        3,
        [put("regen_snapshot_parnecio", stat("clarisa", "intelligence"))],
        [put("regen_snapshot_parnecio", lit(0))],
        [
            roll("scratch_damage_clarisa"),
            put(
                "scratch_damage_clarisa",
                minimum(
                    maximum(lit(0), sub(var("max_hp_parnecio"), var("hp_parnecio"))),
                    mul(
                        minimum(lit(1), var("hp_parnecio")),
                        add(
                            lit(5),
                            var("regen_snapshot_parnecio"),
                            var("scratch_damage_clarisa"),
                        ),
                    ),
                ),
            ),
            heal("parnecio", var("scratch_damage_clarisa")),
            message(
                "REGENERACIÓN restauró {amount} HP a Parnecio.",
                amount=var("scratch_damage_clarisa"),
            ),
        ],
    )
)
for cid, who, mp, effect in [
    ("armadura_magica", "iosepus", 30, "ef_armadura_parnecio"),
    ("firesteel", "iosepus", 30, "ef_firesteel_parnecio"),
    ("regeneracion", "clarisa", 30, "ef_regen_parnecio"),
]:
    equip(
        cid,
        SkillPlay(
            [
                cost(who, "mp", mp),
                {"op": "apply_effect", "effect": effect, "target": "parnecio"},
                message(cid.upper() + " se aplicó a Parnecio."),
            ],
            cond_all(
                active(who),
                active("parnecio"),
                has_resource(who, "mp", mp),
                {"not": {"has_effect": {"target": "parnecio", "effect": effect}}},
            ),
        ),
    )
builder.groupal_shield(fire_out)

# Ataques físicos básicos también usan el contrato común de Hit/Evasion,
# puntuación efectiva de TRAITS y reducción por impacto.
hit_and_damage(AttackDefinition("bastonazo_clarisa", "clarisa", "tegularis"))
hit_and_damage(AttackDefinition("bastonazo_iosepus", "iosepus", "tegularis"))
hit_and_damage(
    AttackDefinition("dentellada", "tegularis", "parnecio", extra=8, tp_cost=30)
)
# Zarpa: la incapacitación del 5% solo se considera si hubo acierto y
# daño efectivo positivo. El objetivo es fijo en este paquete de laboratorio.
hit_and_damage(AttackDefinition("zarpa", "tegularis", "parnecio", extra=15, tp_cost=20))
zarpa = cards["zarpa"]
zarpa["play"]["effects"].append(roll("zarpa_incap", 20))
define("zarpa_incap", 0)
zarpa_hit = eq(var("scratch_hit_tegularis"), "gt", var("scratch_eva_tegularis"))
zarpa_damage = maximum(
    lit(0),
    sub(
        sub(var("scratch_damage_tegularis"), var("defense_parnecio")),
        reduce_damage("parnecio", "physical"),
    ),
)
zarpa["play"]["outcomes"].append(
    {
        "when": cond_all(
            zarpa_hit,
            eq(zarpa_damage, "gt", lit(0)),
            eq(var("zarpa_incap"), "eq", lit(1)),
        ),
        "effects": [
            put("hp_parnecio", lit(0)),
            message("ZARPA incapacitó a Parnecio."),
        ],
    }
)
# Coletazo: cada objetivo recibe un Hit/Evasion/daño independiente.
coletazo = [cost("tegularis", "tp", 20)]
coletazo_out = []
for w in HEROES:
    for prefix in ("hit", "eva", "dmg"):
        define("tail_" + prefix + "_" + w, 0)
    hit = "tail_hit_" + w
    eva = "tail_eva_" + w
    dmg = "tail_dmg_" + w
    coletazo += [
        roll(hit),
        inc(
            hit,
            add(stat("tegularis", "awareness"), trait("tegularis", ["hit"], "actor")),
        ),
        roll(eva),
        inc(eva, evasion(w)),
        roll(dmg),
        put(dmg, add(var(dmg), mul(lit(3), stat("tegularis", "strength")))),
    ]
    successful = eq(var(hit), "gt", var(eva))
    amount = maximum(
        lit(0), sub(sub(var(dmg), var("defense_" + w)), reduce_damage(w, "physical"))
    )
    coletazo_out.append(
        {
            "when": cond_all(
                active(w), successful, eq(var("group_shield"), "eq", lit(0))
            ),
            "effects": [
                damage(w, amount),
                message("COLETAZO hizo {damage} puntos a " + w + ".", damage=amount),
            ],
        }
    )
    coletazo_out.append(
        {
            "when": cond_all(
                active(w), {"not": successful}, eq(var("group_shield"), "eq", lit(0))
            ),
            "effects": [message(w + " esquivó COLETAZO.")],
        }
    )
coletazo_out.insert(
    0,
    {
        "when": eq(var("group_shield"), "gt", lit(0)),
        "effects": [
            put("group_shield", lit(0)),
            message("GROUPAL SHIELD bloqueó COLETAZO."),
        ],
    },
)
equip(
    "coletazo",
    SkillPlay(
        coletazo,
        cond_all(active("tegularis"), has_resource("tegularis", "tp", 20)),
        coletazo_out,
    ),
)
# Fénix restaura exactamente la mitad redondeada hacia arriba al héroe
# indicado por esta vertical fija; el selector de objetivos queda pendiente.
equip(
    "fenix",
    SkillPlay(
        [
            cost("clarisa", "mp", 50),
            put(
                "hp_parnecio",
                calc("floor_divide", add(var("max_hp_parnecio"), lit(1)), lit(2)),
            ),
            message("FÉNIX devolvió a Parnecio con {hp} HP.", hp=var("hp_parnecio")),
        ],
        cond_all(
            active("clarisa"),
            eq(var("hp_parnecio"), "eq", lit(0)),
            has_resource("clarisa", "mp", 50),
        ),
    ),
)
# Grito de guerra: no acumulativo, con duración por cada beneficiario,
# incluidos los héroes que actúan varias veces por ronda.
for w in HEROES:
    effect_card(
        EffectDefinition(
            "ef_warcry_" + w,
            3,
            [inc("warcry_" + w, lit(3))],
            [inc("warcry_" + w, lit(-3))],
        )
    )
war = [cost("gillius", "tp", 10)]
for w in HEROES:
    war.append({"op": "apply_effect", "effect": "ef_warcry_" + w, "target": w})
war.append(message("GRITO DE GUERRA aumentó el daño físico del grupo."))
equip(
    "grito_de_guerra",
    SkillPlay(
        war,
        cond_all(
            active("gillius"),
            has_resource("gillius", "tp", 10),
            {
                "not": {
                    "has_effect": {"target": "gillius", "effect": "ef_warcry_gillius"}
                }
            },
        ),
    ),
)

# Wingblast usa un daño común, evasiones individuales y Resistencias
# independientes; Paralizado consume un turno entero del beneficiario.
for w in HEROES:
    effect_card(EffectDefinition("ef_paralizado_" + w, 1))
    package["cards"][-1]["actuation_blocks_actions"] = True
    for prefix in ("hit", "eva", "res"):
        define("wing_" + prefix + "_" + w, 0)
define("wing_common", 0)
wing = [
    cost("tegularis", "mp", 50),
    roll("wing_common"),
    put("wing_common", add(lit(10), stat("tegularis", "strength"), var("wing_common"))),
]
wing_out = []
for w in HEROES:
    hit = "wing_hit_" + w
    eva = "wing_eva_" + w
    res = "wing_res_" + w
    wing.extend(
        [
            roll(hit),
            inc(
                hit,
                add(
                    stat("tegularis", "awareness"), trait("tegularis", ["hit"], "actor")
                ),
            ),
            roll(eva),
            inc(eva, evasion(w)),
            roll(res),
            inc(res, add(stat(w, "strength"), stat(w, "fortune"))),
        ]
    )
    # FOR es Fortune en el modelo S.O.F.I.A.; la resistencia se calcula
    # STR+FOR+1d10 y falla solo cuando el resultado es menor que 19.
    success = eq(var(hit), "gt", var(eva))
    amount = maximum(
        lit(0),
        sub(sub(var("wing_common"), var("defense_" + w)), reduce_damage(w, "magic")),
    )
    visible = cond_all(active(w), eq(var("group_shield"), "eq", lit(0)))
    wing_out.append(
        {
            "when": cond_all(visible, success),
            "effects": [
                damage(w, amount),
                message("WINGBLAST hizo {damage} puntos a " + w + ".", damage=amount),
            ],
        }
    )
    wing_out.append(
        {
            "when": cond_all(visible, {"not": success}),
            "effects": [message(w + " esquivó WINGBLAST.")],
        }
    )
    wing_out.append(
        {
            "when": cond_all(
                visible,
                success,
                eq(var(res), "lt", lit(19)),
                eq(var("hp_" + w), "gt", amount),
            ),
            "effects": [
                {"op": "apply_effect", "effect": "ef_paralizado_" + w, "target": w},
                message(w + " quedó PARALIZADO."),
            ],
        }
    )
wing_out.insert(
    0,
    {
        "when": eq(var("group_shield"), "gt", lit(0)),
        "effects": [
            put("group_shield", lit(0)),
            message("GROUPAL SHIELD bloqueó WINGBLAST."),
        ],
    },
)
equip(
    "wingblast",
    SkillPlay(
        wing,
        cond_all(active("tegularis"), has_resource("tegularis", "mp", 50)),
        wing_out,
    ),
)
# Preponderancia se retira AL COMENZAR el siguiente turno propio,
# no al finalizar el turno actual ni al avanzar una escena narrativa.
effect_card(
    EffectDefinition(
        "ef_preponderancia",
        2,
        [inc("defense_tegularis", lit(5))],
        [inc("defense_tegularis", lit(-5))],
    )
)
package["cards"][-1]["expire_on_actor_turn_start"] = True
equip(
    "preponderancia",
    SkillPlay(
        [
            put("tp_tegularis", minimum(lit(60), add(var("tp_tegularis"), lit(8)))),
            put(
                "mp_tegularis",
                minimum(var("max_mp_tegularis"), add(var("mp_tegularis"), lit(8))),
            ),
            {
                "op": "apply_effect",
                "effect": "ef_preponderancia",
                "target": "tegularis",
            },
            message("PREPONDERANCIA recuperó 8 TP y 8 MP; Tegularis está protegido."),
        ],
        cond_all(
            active("tegularis"),
            {
                "not": {
                    "has_effect": {"target": "tegularis", "effect": "ef_preponderancia"}
                }
            },
        ),
    ),
)

# Agarraguirre altera la lectura EFECTIVA de Awareness a través de
# modificadores S.O.F.I.A. y caduca por turno del dragón.
effect_card(EffectDefinition("ef_agarraguirre", 2))
package["cards"][-1]["modifiers"] = [{"stat": "awareness", "amount": -2}]
equip(
    "agarraguirre",
    SkillPlay(
        [
            cost("iosepus", "mp", 30),
            {"op": "apply_effect", "effect": "ef_agarraguirre", "target": "tegularis"},
            message("AGARRAGUIRRE redujo Awareness de Tegularis en 2."),
        ],
        cond_all(
            active("iosepus"),
            active("tegularis"),
            has_resource("iosepus", "mp", 30),
            {
                "not": {
                    "has_effect": {"target": "tegularis", "effect": "ef_agarraguirre"}
                }
            },
        ),
    ),
)
# La postura utiliza TRAITS del catálogo, y cuesta una oportunidad de
# actuación. No se puede aplicar dos veces.
for t in package["traits"]["traits"]:
    if t["id"] == "stance_aggressive":
        t["contributions"].append(
            {
                "id": "evasion_penalty",
                "when": {"role": "defender", "all_tags": ["evasion"]},
                "add": {"slot": "bonus", "amount": -2},
            }
        )
for instance in package["initial_state"]["skills"]:
    if instance["card"] == "stance_aggressive":
        instance["zone"] = "hand"
equip(
    "stance_aggressive",
    SkillPlay(
        [
            {"op": "assign_trait", "entity": "gillius", "trait": "stance_aggressive"},
            message("Gillius adoptó STANCE AGGRESSIVE: +2 Hit y -2 Evasion."),
        ],
        cond_all(
            active("gillius"),
            {"not": {"has_trait": {"entity": "gillius", "trait": "stance_aggressive"}}},
        ),
    ),
)
# Consultas de Hit toman los TRAITS del atacante de forma contextual.
# No se agrega un modificador de Hit especial al motor.
# Protección en v0.7.1 debe permanecer deshabilitada hasta que exista la
# redirección del impacto (no equivale a una simple reducción de daño).
# Mantener las pasivas sin efectos de ejecución, tal como fueron diseñadas.
# Las demás cartas sin semántica suficiente se bloquean explícitamente.
implemented_count = complete_catalog(builder, DESIGN)
# Aún faltan los acontecimientos finales de v0.7.2 y la selección pública de v0.7.3.
OUTPUT.write_text(compact_json(package))
print(
    "wrote",
    OUTPUT,
    "cards implemented",
    implemented_count,
    "variables",
    len(package["manifest"]["variables"]),
)
