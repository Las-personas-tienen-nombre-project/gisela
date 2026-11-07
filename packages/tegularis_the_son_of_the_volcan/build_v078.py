"""Ajuste autoral de balance v0.7.8; modifica exclusivamente datos del encuentro.

Se aplica sobre v0.7.7, sin cambiar el DSL, el motor ni la IA genérica.
"""

import copy
import json
from pathlib import Path

from build_expressions import add, calc, cond_all, eq, lit, minimum, var
from build_json import compact_json

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "09_cierre_autoral_v077.package.json"
TARGET = HERE / "10_balance_v078.package.json"
PACKAGE = json.loads(SOURCE.read_text())
CARDS = {card["id"]: card for card in PACKAGE["cards"]}
ACTORS = {entry["character"]: entry for entry in PACKAGE["actuation"]["participants"]}
ALLIES = ("parnecio", "gillius", "clarisa", "iosepus")


def tune_gillius():
    actor = CARDS["gillius"]
    if actor["sofia"]["awareness"] != 5:
        raise ValueError("Awareness inicial de Gillius no coincide con la base v077")
    actor["sofia"]["awareness"] = 6


def tune_preponderancia():
    card = CARDS["preponderancia"]
    effects = card["play"]["effects"]
    if len(effects) != 4:
        raise ValueError("La carta Preponderancia cambió su contrato")
    for resource, gained in (("tp", 25), ("mp", 15)):
        entry = next(
            e for e in effects if e.get("target", {}).get("var", {}).get("key")
            == resource + "_tegularis"
        )
        expr = entry["value"]["math"]
        if expr["op"] != "min":
            raise ValueError("El recurso no aplica el límite declarado")
        if expr["right"]["math"]["right"] != lit(8):
            raise ValueError("La recuperación base de Preponderancia cambió")
        expr["right"]["math"]["right"] = lit(gained)
    entry = next(e for e in effects if e["op"] == "emit_message")
    entry["template"] = (
        "PREPONDERANCIA recuperó 25 TP y 15 MP; Tegularis está protegido."
    )


def relative_priority(target):
    """Un objetivo vivo, herido y con el menor HP porcentual del grupo."""
    comparisons = []
    for other in ALLIES:
        if other == target:
            continue
        target_ratio = calc("multiply", var("hp_" + target), var("max_hp_" + other))
        other_ratio = calc("multiply", var("hp_" + other), var("max_hp_" + target))
        comparisons.append(
            {"any": [eq(var("hp_" + other), "lte", lit(0)),
                     eq(target_ratio, "lte", other_ratio)]}
        )
    return cond_all(*comparisons)


def tune_clarisa():
    """Priorizar al más herido; ante empates favorecer al frente de batalla."""
    order = ("parnecio", "gillius", "clarisa", "iosepus")
    for prefix in ("curacion", "regeneracion"):
        for target in order:
            cid = prefix if target == "parnecio" else prefix + "_" + target
            card = CARDS[cid]
            previous = copy.deepcopy(card["play"]["requires"])
            card["play"]["requires"] = cond_all(
                previous, relative_priority(target),
                *([eq(var("hp_" + target), "lt", var("max_hp_" + target))]
                  if prefix == "regeneracion" else []),
            )
    candidates = ACTORS["clarisa"]["candidates"]
    previous_ids = [c["skill_instance"] for c in candidates]
    def instances(prefix):
        return [prefix + ("" if w == "parnecio" else "_" + w) + "_01" for w in order]
    chosen = (
        instances("fenix") + instances("curacion")
        + ["groupal_shield_01"] + instances("regeneracion")
        + instances("bless") + ["concentracion_clarisa_01", "bastonazo_clarisa_01"]
    )
    if set(chosen) != set(previous_ids):
        raise ValueError("La política de NPC perdió o añadió una carta")
    existing = {entry["skill_instance"]: entry for entry in candidates}
    candidates[:] = [existing[cid] for cid in chosen]


def tune_iosepus():
    candidates = ACTORS["iosepus"]["candidates"]
    previous_ids = [item["skill_instance"] for item in candidates]
    chosen = ["agarraguirre_01"]
    for spell in ("armadura_magica", "firesteel"):
        for target in ("gillius", "parnecio", "clarisa", "iosepus"):
            cid = spell + ("" if target == "parnecio" else "_" + target) + "_01"
            chosen.append(cid)
    chosen += ["magic_blast_01", "concentracion_iosepus_01", "bastonazo_iosepus_01"]
    if set(chosen) != set(previous_ids):
        raise ValueError("La política de NPC perdió o añadió una carta")
    existing = {entry["skill_instance"]: entry for entry in candidates}
    candidates[:] = [existing[cid] for cid in chosen]


def half_hp(who, op):
    """Compara HP actual contra la mitad del máximo sin dividir ni redondear."""
    return eq(calc("multiply", var("hp_" + who), lit(2)), op, var("max_hp_" + who))


def tune_tegularis():
    """Vuelve alcanzables Wingblast, Zarpa y Dentellada sin tocar cartas ni costos.

    Firebreath y Wingblast cuestan 50 MP; Coletazo y Zarpa, 20 TP; Dentellada,
    30 TP. Con la lista anterior, la primera candidata pagable eclipsaba siempre
    a las siguientes. Sano, el dragón escupe fuego; herido, bate las alas. Con
    Parnecio a la mitad de su HP o menos, lo muerde en lugar de barrer al grupo.
    """
    candidates = ACTORS["tegularis"]["candidates"]
    previous_ids = [item["skill_instance"] for item in candidates]
    parnecio_herido = half_hp("parnecio", "lte")
    chosen = [
        ("firebreath_01", half_hp("tegularis", "gt")),
        ("wingblast_01", None),
        ("dentellada_01", parnecio_herido),
        ("zarpa_01", parnecio_herido),
        ("coletazo_01", None),
        ("preponderancia_01", None),
    ]
    if {cid for cid, _ in chosen} != set(previous_ids):
        raise ValueError("La política de NPC perdió o añadió una carta")
    candidates[:] = [
        {"skill_instance": cid, **({"when": guard} if guard else {})}
        for cid, guard in chosen
    ]


tune_gillius()
tune_preponderancia()
tune_clarisa()
tune_iosepus()
tune_tegularis()
# Public view is authored separately from the combat logic, not copied from TARGET.
VIEW = json.loads((HERE / "v078_public_view.json").read_text(encoding="utf-8"))
PACKAGE["presentation"] = copy.deepcopy(VIEW["presentation"])
for field in ("public_resources", "public_trace_variables"):
    PACKAGE["actuation"][field] = copy.deepcopy(VIEW[field])
PACKAGE["manifest"]["id"] = "tegularis_balance_v078"
TARGET.write_text(json.dumps(PACKAGE, ensure_ascii=False, indent=2) + "\n")
print("Compilado:", TARGET.name)
