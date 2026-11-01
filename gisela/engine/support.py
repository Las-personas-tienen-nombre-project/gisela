"""Admisión dinámica: subconjunto del lenguaje que ejecuta el motor H3."""

from __future__ import annotations

from .errors import EngineFailure

SUPPORTED_STEPS = {
    "evaluate",
    "narrate",
    "dialogue",
    "choice",
    "condition",
    "effect",
    "scene",
    "transition",
    "ending",
    "skill_window",
}
SUPPORTED_OPS = {
    "set",
    "add",
    "transfer",
    "move_character",
    "learn_fact",
    "set_belief",
    "move_skill",
    "discard_skill",
    "create_instance",
    "remove_instance",
    "advance_time",
    "record_fact",
    "set_scene",
    "grant_skill",
    "roll",
    "apply_effect",
    "end_effect",
    "assign_trait",
    "remove_trait",
}
SUPPORTED_CONDITIONS = {
    "constant",
    "all",
    "any",
    "not",
    "has_fact",
    "knows",
    "believes",
    "has_skill",
    "has_trait",
    "has_effect",
    "owns",
    "at_location",
    "compare",
}
SUPPORTED_TRIGGERS = {
    "fact_recorded",
    "state_changed",
    "turn_started",
    "turn_ended",
    "node_completed",
    "effect_expired",
}


def _explicit(ref, label: str) -> None:
    """Prohíbe contextos que el ejecutor aún no sabe vincular."""
    if not isinstance(ref, str) or ref.startswith("$"):
        raise EngineFailure("UNSUPPORTED_FORMAT", f"H3 requiere {label} explícito")


def check_value(expression: dict) -> None:
    """Solo acepta expresiones que el ejecutor puede resolver sin ligaduras."""
    key = next(iter(expression))
    if key in ("literal", "clock", "turn"):
        return
    if key == "var":
        if expression["var"]["scope"] in ("session", "world"):
            return
        raise EngineFailure("UNSUPPORTED_FORMAT", "Variable de instancia no disponible")
    if key == "stat":
        _explicit(expression[key]["character"], "personaje S.O.F.I.A.")
        return
    if key == "property":
        _explicit(expression[key]["entity"], "entidad de propiedad")
        return
    if key == "relationship":
        _explicit(expression[key]["from"], "origen de relación")
        _explicit(expression[key]["to"], "destino de relación")
        return
    raise EngineFailure("UNSUPPORTED_FORMAT", "Expresión de valor no disponible")


def check_condition(cond: dict) -> None:
    """Rechaza condiciones no implementadas antes de iniciar una historia."""
    key = next(iter(cond))
    if key not in SUPPORTED_CONDITIONS:
        raise EngineFailure("UNSUPPORTED_FORMAT", f"Condición aún no disponible: {key}")
    if key in ("all", "any"):
        for item in cond[key]:
            check_condition(item)
    if key == "not":
        check_condition(cond[key])
    if key == "has_trait":
        _explicit(cond[key]["entity"], "entidad TRAITS")
    if key == "has_effect":
        _explicit(cond[key]["target"], "destino de efecto")
    if key in ("owns", "at_location", "knows", "believes", "has_skill"):
        for name, val in cond[key].items():
            if name in ("character", "location", "object", "owner"):
                _explicit(val, name)
    if key == "compare":
        for side in ("left", "right"):
            check_value(cond[key][side])


def check_effect(effect: dict) -> None:
    """Comprueba una consecuencia ejecutable y sus referencias."""
    op = effect["op"]
    if op not in SUPPORTED_OPS:
        raise EngineFailure("UNSUPPORTED_FORMAT", f"Operación aún no disponible: {op}")
    for name in (
        "character",
        "location",
        "object",
        "from",
        "to",
        "owner",
        "instance",
        "skill_instance",
        "effect_instance",
    ):
        if name in effect and not (name == "to" and op == "move_skill"):
            _explicit(effect[name], name)
    if op in ("assign_trait", "remove_trait"):
        _explicit(effect["entity"], "entidad TRAITS")
    if op == "apply_effect":
        _explicit(effect["target"], "destino de efecto")
    if op == "roll":
        target = effect["store"]
        if "var" not in target or target["var"]["scope"] not in ("session", "world"):
            raise EngineFailure(
                "UNSUPPORTED_FORMAT", "roll exige una variable declarada"
            )
        if effect["sides"] > 9007199254740991:
            raise EngineFailure(
                "UNSUPPORTED_FORMAT", "roll admite como máximo 2^53-1 caras"
            )
    if op in ("set", "add"):
        check_value(effect["target"])
        check_value(effect["value"])


def _check_step(step: dict, version: str) -> None:
    """Valida un paso y sus operaciones sin ejecutarlo."""
    if step["op"] not in SUPPORTED_STEPS:
        raise EngineFailure("UNSUPPORTED_FORMAT", f"Paso no disponible: {step['op']}")
    if step["op"] == "evaluate":
        _check_evaluation(step["evaluation"], version)
    if step["op"] == "choice":
        for opt in step["options"]:
            for name in ("visible_if", "enabled_if"):
                if name in opt:
                    check_condition(opt[name])
            for effect in opt.get("effects", []):
                check_effect(effect)
            if "evaluation" in opt:
                _check_evaluation(opt["evaluation"], version)
    if step["op"] == "condition":
        check_condition(step["test"])
    if step["op"] == "effect":
        for effect in step["effects"]:
            check_effect(effect)


def check_supported(package: dict) -> None:
    """Comprueba soporte dinámico además de la admisión semántica estática."""
    if package["manifest"]["format_version"] not in ("1.2", "1.3", "1.4", "1.5"):
        raise EngineFailure("UNSUPPORTED_FORMAT", "Versión no ejecutable")
    if not any(k in package["manifest"]["entry"] for k in ("node", "scene")):
        raise EngineFailure("UNSUPPORTED_FORMAT", "Entrada inicial inválida")
    for node in package["nodes"]:
        for step in node["steps"]:
            _check_step(step, package["manifest"]["format_version"])
    for rule in package["rules"]:
        if rule["trigger"]["on"] not in SUPPORTED_TRIGGERS:
            raise EngineFailure("UNSUPPORTED_FORMAT", "Disparador no implementado")
        if rule["trigger"]["on"] == "state_changed":
            target = rule["trigger"]["target"]
            check_value(target)
        check_condition(rule.get("when", {"constant": True}))
        for effect in rule["effects"]:
            check_effect(effect)
    _effect_cards(package)
    _skill_cards(package)
    _effect_cycles(package)
    for scene in package["scenes"]:
        _check_scene(scene, package["manifest"]["format_version"])


def _skill_cards(package: dict) -> None:
    """Comprueba las cartas de habilidad usando una responsabilidad separada."""
    from .support_skills import check_cards

    check_cards(package)


def _effect_cards(package: dict) -> None:
    """Valida las consecuencias de cartas y las condiciones de vencimiento."""
    for card in package["cards"]:
        if card["kind"] != "effect":
            continue
        for clause in card.get("expiration", {}).get("clauses", []):
            if "when" in clause:
                check_condition(clause["when"])
        for name in ("on_apply", "on_expire"):
            for operation in card.get(name, []):
                check_effect(operation)


def _effect_cycles(package: dict) -> None:
    """Rechaza recursión de aplicación directa en definiciones de efectos."""
    graph = {
        c["id"]: {
            o["effect"] for o in c.get("on_apply", []) if o["op"] == "apply_effect"
        }
        for c in package["cards"]
        if c["kind"] == "effect"
    }
    visited, visiting = set(), set()

    def visit(identifier):
        if identifier in visiting:
            raise EngineFailure("UNSUPPORTED_FORMAT", "Aplicación recursiva de efectos")
        if identifier in visited:
            return
        visiting.add(identifier)
        for child in graph.get(identifier, ()):
            visit(child)
        visiting.remove(identifier)
        visited.add(identifier)

    for identifier in graph:
        visit(identifier)


def _check_scene(scene: dict, version: str) -> None:
    """Comprueba el subconjunto ejecutable de acciones de escena."""
    for entry in [
        *scene.get("actions", []),
        *(
            action
            for element in scene.get("elements", [])
            for action in element.get("actions", [])
        ),
    ]:
        for name in ("visible_if", "enabled_if"):
            if name in entry:
                check_condition(entry[name])
        if entry.get("requires", "none") != "none":
            raise EngineFailure(
                "UNSUPPORTED_FORMAT", "Preparación exploratoria no disponible"
            )
        for operation in entry.get("effects", []):
            check_effect(operation)
        if "evaluation" in entry:
            _check_evaluation(entry["evaluation"], version)
        if "next" in entry and "node" not in entry["next"]:
            raise EngineFailure(
                "UNSUPPORTED_FORMAT", "Destino exploratorio debe ser nodo"
            )
    for element in scene.get("elements", []):
        if "visible_if" in element:
            check_condition(element["visible_if"])
        if "entity" in element:
            _explicit(element["entity"], "entidad del elemento")
    for actor in scene.get("actors", []):
        _explicit(actor["character"], "personaje de escena")
        if "visible_if" in actor:
            check_condition(actor["visible_if"])


def _check_evaluation(spec: dict, version: str) -> None:
    """E3 habilita presentación visible solo con contrato v1.5."""
    if version != "1.5" and spec["presentation"] != "hidden":
        raise EngineFailure(
            "UNSUPPORTED_FORMAT", "La evaluación visible pertenece a E3"
        )
    for branch in spec["branches"]:
        for effect in branch.get("effects", []):
            check_effect(effect)
