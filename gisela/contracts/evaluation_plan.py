"""E1: compilación pura de autoría `evaluation` al contrato interno TRAITS–DICE.

No ejecuta DICE, consulta estado, consume RNG ni aplica consecuencias.
Las referencias a entidades se resuelven semánticamente en admisión y en E2
antes de una ejecución efectiva.
"""

from __future__ import annotations

import copy

from dice import DiceError, compile_profile


class EvaluationPlanError(ValueError):
    """Contrato matemático o ramificación inválida, previo a la ejecución."""


def profile_catalog(package: dict) -> dict[str, dict]:
    """Indexa y compila perfiles neutrales sin compartir referencias del autor."""
    result = {}
    for item in package.get("dice_profiles", []):
        identifier = item["id"]
        if identifier in result:
            raise EvaluationPlanError(f"Perfil DICE duplicado: {identifier}")
        try:
            result[identifier] = compile_profile(item)
        except (DiceError, ValueError, TypeError, KeyError) as exc:
            raise EvaluationPlanError(f"Perfil DICE {identifier}: {exc}") from exc
    return result


def normalize_evaluation(evaluation: dict, profiles: dict[str, dict]) -> dict:
    """Compila una declaración en la entrada EXACTA de traits_dice_bridge.resolve.

    El resultado es un plan sin estado: `resolve(state, plan["request"], definitions)`
    será responsable de consultar TRAITS, S.O.F.I.A. y RNG en E2. Ninguna de
    esas lecturas se adelanta a admisión, pues las entidades pueden cambiar.
    """
    profile_id = evaluation["profile"]
    if profile_id not in profiles:
        raise EvaluationPlanError(f"Perfil DICE inexistente: {profile_id}")
    profile = profiles[profile_id]
    expected = {band["id"] for band in profile["bands"]}
    branches = evaluation["branches"]
    outcomes = [branch["outcome"] for branch in branches]
    if len(outcomes) != len(set(outcomes)):
        raise EvaluationPlanError("Ramas de evaluación duplicadas")
    if set(outcomes) != expected:
        raise EvaluationPlanError(
            f"Ramas incompatibles con el perfil {profile_id}: faltan {sorted(expected - set(outcomes))}, sobran {sorted(set(outcomes) - expected)}"
        )
    base_spec = evaluation["inputs"]["base"]
    request = {
        "profile": copy.deepcopy(profile),
        "base": base_spec.get("literal", 0),
        "difficulty": evaluation["inputs"].get("difficulty", {"literal": 0})["literal"],
        "participants": copy.deepcopy(
            evaluation.get("context", {}).get("participants", [])
        ),
        "tags": copy.deepcopy(evaluation.get("context", {}).get("tags", [])),
    }
    if "stat" in base_spec:
        request["stat"] = copy.deepcopy(base_spec["stat"])
    return {
        "id": evaluation["id"],
        "presentation": evaluation["presentation"],
        "request": request,
        "branches": {branch["outcome"]: copy.deepcopy(branch) for branch in branches},
    }


def compile_package_evaluations(package: dict) -> dict[str, dict]:
    """Indexa por ruta estructural, sin asumir IDs globales de acciones o pasos."""
    profiles = profile_catalog(package)
    result = {}
    for ni, node in enumerate(package["nodes"]):
        for si, step in enumerate(node["steps"]):
            root = f"/nodes/{ni}/steps/{si}"
            if "evaluation" in step:
                result[root] = normalize_evaluation(step["evaluation"], profiles)
            for oi, option in enumerate(step.get("options", [])):
                if "evaluation" in option:
                    result[f"{root}/options/{oi}"] = normalize_evaluation(
                        option["evaluation"], profiles
                    )
    for si, scene in enumerate(package["scenes"]):
        for ai, action in enumerate(scene.get("actions", [])):
            if "evaluation" in action:
                result[f"/scenes/{si}/actions/{ai}"] = normalize_evaluation(
                    action["evaluation"], profiles
                )
        for ei, element in enumerate(scene.get("elements", [])):
            for ai, action in enumerate(element.get("actions", [])):
                if "evaluation" in action:
                    result[f"/scenes/{si}/elements/{ei}/actions/{ai}"] = (
                        normalize_evaluation(action["evaluation"], profiles)
                    )
    return result
