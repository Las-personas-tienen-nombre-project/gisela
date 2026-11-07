"""Ejecución común de cartas; origen jugador o guion, misma autoridad de estado."""

from __future__ import annotations

from dataclasses import dataclass, replace

from .causal_trace import correlate
from .conditions import predicate
from .conditions import value as evaluate_value
from .effect_context import EffectContext
from .world_base import WorldError, find
from .world_skills import SkillReturn, return_from_play, take_for_play

MAX_NESTED_PLAYS = 8


@dataclass(frozen=True)
class SkillRequest:
    """Identificador de la carta y respuestas del jugador en la transacción."""

    identifier: str
    decisions: object


@dataclass(frozen=True)
class SkillExecution:
    """Datos de una ejecución; no concede autoridad para confirmar el estado."""

    skill: dict
    card: dict
    context: EffectContext
    apply_group: object
    origin: str
    arguments: dict | None = None


class _NoScriptChoices:
    """Nunca solicita a la interfaz una decisión auxiliar perteneciente a un NPC."""

    def select(self, *args, **kwargs):
        raise WorldError(
            "SCRIPT_CHOICE_REQUIRED",
            "La habilidad del guion requiere una decisión auxiliar no declarada",
        )


def _matched(state: dict, clauses: list[dict], definitions) -> list[dict]:
    return [item for item in clauses if predicate(state, item["when"], definitions)]


def _destination(state: dict, card: dict, definitions) -> str:
    policy = card.get("return_policy", {"default": "discard"})
    options = {
        item["to"]
        for item in policy.get("when", [])
        if predicate(state, item["if"], definitions)
    }
    if len(options) > 1:
        raise WorldError("RETURN_POLICY_CONFLICT", "Políticas de retorno incompatibles")
    return next(iter(options)) if options else policy["default"]


def _trace(state: dict, execution: SkillExecution) -> None:
    skill, origin, arguments = execution.skill, execution.origin, execution.arguments
    seq = len(state["history"]["facts"]) + len(state["history"]["trace"]) + 1
    detail = {"card": skill["card"], "actor": skill["character"], "origin": origin}
    if arguments:
        detail["arguments"] = arguments
    if state["status"] == "node":
        cursor = state["cursor"]
        detail.update(
            {"execution_id": cursor["execution_id"], "step_id": cursor["step"]}
        )
    else:
        detail["scene"] = state["current_scene"]
    state["history"]["trace"].append(
        {
            "sequence": seq,
            "kind": "skill_played",
            "source": skill["id"],
            "detail": detail,
        }
    )
    correlate(state["history"]["trace"][-1], execution.context)


def _start_execution(state: dict, execution: SkillExecution) -> SkillExecution:
    """La identidad deriva de la secuencia del borrador, sin contador ni RNG."""
    if "actuation" not in state:
        return execution
    trace = state["history"]["trace"]
    sequence = len(state["history"]["facts"]) + len(trace) + 1
    context = replace(execution.context, causal_execution_id=f"action_{sequence:08d}")
    trace.append(
        {
            "sequence": sequence,
            "kind": "skill_started",
            "source": execution.skill["id"],
            "causal_execution_id": context.causal_execution_id,
            "detail": {
                "card": execution.skill["card"],
                "actor": execution.skill["character"],
                "origin": execution.origin,
            },
        }
    )
    return replace(execution, context=context)


def _run(state, execution: SkillExecution):
    """Proceso compartido: toma, efectos, outcomes, retorno e historial."""
    execution = _start_execution(state, execution)
    skill, card, context = execution.skill, execution.card, execution.context
    take_for_play(state, skill)
    events = []
    events.extend(execution.apply_group(state, card["play"]["effects"], context) or [])
    for outcome in _matched(
        state, card["play"].get("outcomes", []), context.definitions
    ):
        events.extend(execution.apply_group(state, outcome["effects"], context) or [])
    destination = _destination(state, card, context.definitions)
    return_from_play(state, skill, SkillReturn(destination, context.decisions))
    _trace(state, execution)
    return events


def execute(session, state: dict, request: SkillRequest) -> None:
    """Acción del jugador: conserva exactamente su autorización y los asentamientos."""
    from .skill_window import allowed

    skill = find(state, "skills", request.identifier)
    if not allowed(state, skill, session):
        raise WorldError("INVALID_ACTION", "La habilidad no está habilitada")
    card = session._cards[skill["card"]]
    _run(
        state,
        SkillExecution(
            skill,
            card,
            EffectContext(skill["id"], request.decisions, session._definitions),
            lambda draft, operations, ctx: session._operations(draft, operations, ctx),
            "player",
        ),
    )


def _bind_arguments(
    state: dict, binding: tuple[dict, dict], definitions
) -> tuple[dict, dict]:
    """Liga los argumentos del guion a una copia de la carta; no muta el catálogo.

    Los parámetros de tipo character se sustituyen como referencias; los
    parámetros enteros se sustituyen por expresiones literales. La sustitución
    es estructural, no evalúa cadenas ni expresiones arbitrarias.
    """
    effect, card = binding
    specifications = {p["id"]: p for p in card["play"].get("parameters", [])}
    supplied = effect.get("arguments", {})
    if set(supplied) != set(specifications):
        raise WorldError("INVALID_PARAMETERS", "Argumentos ausentes o desconocidos")
    values = {}
    for name, spec in specifications.items():
        item = evaluate_value(state, supplied[name], definitions)
        if spec["kind"] == "integer":
            if type(item) is not int:
                raise WorldError(
                    "TYPE_MISMATCH", "El parámetro debe ser entero: " + name
                )
            if ("min" in spec and item < spec["min"]) or (
                "max" in spec and item > spec["max"]
            ):
                raise WorldError(
                    "PROPERTY_RANGE", "Parámetro fuera de límites: " + name
                )
        elif spec["kind"] == "character":
            if type(item) is not str:
                raise WorldError("TYPE_MISMATCH", "El objetivo debe ser un personaje")
            find(state, "characters", item)
        values[name] = item

    def substitute(node, depth=0):
        if depth > 32:
            raise WorldError("BUDGET_EXCEEDED", "Plantilla demasiado profunda")
        if isinstance(node, dict):
            if set(node) == {"parameter"}:
                name = node["parameter"]
                if name not in values:
                    raise WorldError(
                        "INVALID_PARAMETERS", "Parámetro sin declarar: " + name
                    )
                return (
                    values[name]
                    if specifications[name]["kind"] == "character"
                    else {"literal": values[name]}
                )
            return {key: substitute(item, depth + 1) for key, item in node.items()}
        if isinstance(node, list):
            return [substitute(item, depth + 1) for item in node]
        return node

    # Solo se preparan las reglas de la habilidad. El catálogo compartido
    # permanece inmutable para las demás instancias y sesiones.
    bound = dict(card)
    bound["play"] = substitute(card["play"])
    return bound, values


def execute_scripted(state: dict, effect: dict, context: EffectContext) -> list[dict]:
    """Activa una carta de NPC desde una operación autoral admitida.

    El jugador no recibe una acción ajena. Todas las mutaciones se realizan en el
    borrador que el runtime ya mantiene, y sus eventos se entregan al asentamiento
    causal exterior. No se permiten selecciones auxiliares interactivas.
    """
    from .consequences import apply_operation

    if context.skill_depth >= MAX_NESTED_PLAYS:
        raise WorldError("BUDGET_EXCEEDED", "Demasiadas habilidades anidadas")
    skill = find(state, "skills", effect["skill_instance"])
    if skill["character"] == state.get("player_character"):
        raise WorldError("INVALID_ACTION", "El guion no puede sustituir al jugador")
    if skill["zone"] != "hand":
        raise WorldError("INVALID_ACTION", "La habilidad de NPC no está en la mano")
    find(state, "characters", skill["character"])
    card = context.definitions.cards[skill["card"]]
    if card["kind"] != "skill":
        raise WorldError("INVALID_STATE", "Instancia sin carta de habilidad")
    if card.get("passive_traits"):
        raise WorldError("INVALID_ACTION", "Una habilidad pasiva no se juega")
    bound_card, arguments = _bind_arguments(state, (effect, card), context.definitions)
    if not predicate(
        state,
        bound_card["play"].get("requires", {"constant": True}),
        context.definitions,
    ):
        raise WorldError("INVALID_ACTION", "La habilidad de NPC no cumple requisitos")
    decisions = _NoScriptChoices()

    def run_operations(draft, operations, subcontext):
        events = []
        nested_context = replace(
            subcontext,
            decisions=decisions,
            definitions=context.definitions,
            skill_depth=context.skill_depth + 1,
        )
        for operation in operations:
            events.extend(apply_operation(draft, operation, nested_context))
        return events

    return _run(
        state,
        SkillExecution(
            skill,
            bound_card,
            EffectContext(skill["id"], decisions, context.definitions),
            run_operations,
            "script",
            arguments,
        ),
    )


def _eligible_candidate(state, candidate, context):
    """Return (skill, reason) while preserving the selection error policy."""
    if "when" in candidate and not predicate(
        state, candidate["when"], context.definitions
    ):
        return None, "guard_false"
    skill = next(
        (
            item
            for item in state["world"]["skills"]
            if item["id"] == candidate["skill_instance"]
        ),
        None,
    )
    if skill is None:
        return None, "missing_instance"
    if skill["character"] == state.get("player_character"):
        raise WorldError("INVALID_ACTION", "El guion no puede sustituir al jugador")
    find(state, "characters", skill["character"])
    card = context.definitions.cards[skill["card"]]
    if card["kind"] != "skill":
        raise WorldError("INVALID_STATE", "Instancia sin carta de habilidad")
    if card.get("passive_traits"):
        return None, "passive"
    if skill["zone"] != "hand":
        return None, "not_in_hand"
    bound_card, _ = _bind_arguments(state, (candidate, card), context.definitions)
    if not predicate(
        state,
        bound_card["play"].get("requires", {"constant": True}),
        context.definitions,
    ):
        return None, "requirements_false"
    return skill, "selected"


def execute_first_available(
    state: dict, effect: dict, context: EffectContext
) -> list[dict]:
    """Selecciona la primera carta ejecutable de una lista ordenada del autor.

    Solo se omiten candidatos por guardas falsas, zona no disponible o
    requisitos incumplidos. Una ejecución que comienza y falla aborta la
    transacción completa; nunca se oculta un error como fallback.
    """
    from .consequences import apply_operation

    if context.skill_depth >= MAX_NESTED_PLAYS:
        raise WorldError("BUDGET_EXCEEDED", "Demasiadas habilidades anidadas")
    from .candidate_diagnostics import record as record_candidates

    assessments = []
    for candidate in effect["candidates"]:
        skill, reason = _eligible_candidate(state, candidate, context)
        assessments.append(reason)
        if skill is None:
            continue
        record_candidates(
            skill["character"], (effect["candidates"], skill["id"]), assessments
        )
        return execute_scripted(
            state,
            {
                "op": "play_skill",
                "skill_instance": skill["id"],
                "arguments": candidate.get("arguments", {}),
            },
            context,
        )
    record_candidates(context.source, (effect["candidates"], None), assessments)
    events = []
    fallback_context = replace(
        context,
        skill_depth=context.skill_depth + 1,
    )
    for operation in effect.get("otherwise", []):
        events.extend(apply_operation(state, operation, fallback_context))
    return events
