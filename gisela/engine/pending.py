"""Decisiones auxiliares de una única transacción de GISELA.

No serializa borradores. Las respuestas se consumen al reconstruir la acción
sobre el último estado confirmado. Ninguna decisión se obtiene del frontend
sin comprobar nuevamente el conjunto de opciones del motor.
"""

from __future__ import annotations

from dataclasses import dataclass

from .world import WorldError


@dataclass(frozen=True)
class DecisionRequired(Exception):
    """Solicitud auxiliar producida durante el replay del borrador."""

    request: dict


class DecisionReplay:
    """Consume respuestas en orden y exige coincidencia con opciones vigentes."""

    def __init__(self, answers: list[dict] | None = None, evaluations=None):
        """Copia las respuestas guardadas sin tomar posesión de su lista."""
        self.answers = list(answers or [])
        self.index = 0
        self.evaluations = (
            evaluations if evaluations is not None else EvaluationReplay()
        )

    def select(self, purpose: str, options: list[str], description: str) -> str:
        """Devuelve una respuesta válida o suspende con una solicitud select_one."""
        request = {
            "request_id": f"auxiliar_{self.index + 1:04d}",
            "kind": "select_one",
            "purpose": purpose,
            "options": sorted(options),
            "description": description,
        }
        if not request["options"]:
            raise WorldError(
                "NO_LEGAL_CHOICE", "No hay opciones legales para resolver la operación"
            )
        if self.index == len(self.answers):
            raise DecisionRequired(request)
        answer = self.answers[self.index]
        if (
            answer.get("request_id") != request["request_id"]
            or answer.get("option_id") not in request["options"]
        ):
            raise WorldError(
                "REPLAY_MISMATCH",
                "La respuesta guardada no coincide con las opciones actuales",
            )
        self.index += 1
        return answer["option_id"]

    def completed(self) -> None:
        """Rechaza respuestas sobrantes después de completar la operación."""
        if self.index != len(self.answers):
            raise WorldError(
                "REPLAY_MISMATCH",
                "La operación no consumió todas las respuestas guardadas",
            )
        self.evaluations.completed()


@dataclass(frozen=True)
class EvaluationPause(Exception):
    """Suspensión antes de aplicar consecuencias; incluye un resultado fijable."""

    entry: dict


class EvaluationReplay:
    """Cinta de resultados visibles dentro de una única intención causal.

    No es un segundo RNG: cada entrada se verifica reejecutando el evaluador
    sobre el estado provisional reconstruido con el checkpoint RNG original.
    """

    def __init__(self, fixed: list[dict] | None = None, *, validate_pending=False):
        self.fixed = list(fixed or [])
        self.index = 0
        self.validate_pending = validate_pending

    def resolve(self, evaluation: tuple) -> None:
        key, plan, state, computed = evaluation
        import copy

        entry = {
            "key": list(key),
            "presentation": plan["presentation"],
            "result": copy.deepcopy(computed["dice"]),
            "rng_before": copy.deepcopy(state["rng"]),
            "rng_after": copy.deepcopy(computed["rng_after"]),
        }
        if plan["presentation"] == "hidden":
            state["rng"] = copy.deepcopy(entry["rng_after"])
            return
        if self.index < len(self.fixed):
            previous = self.fixed[self.index]
            if previous != entry:
                raise WorldError(
                    "REPLAY_MISMATCH",
                    "La evaluación fija no coincide con la reconstrucción",
                )
            self.index += 1
            state["rng"] = copy.deepcopy(entry["rng_after"])
            if self.validate_pending and self.index == len(self.fixed):
                raise EvaluationPause(entry)
            return
        state["rng"] = copy.deepcopy(entry["rng_after"])
        raise EvaluationPause(entry)

    def completed(self) -> None:
        if self.index != len(self.fixed):
            raise WorldError(
                "REPLAY_MISMATCH", "Quedaron resultados fijados sin reproducir"
            )
