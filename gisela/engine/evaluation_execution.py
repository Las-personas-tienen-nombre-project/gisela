"""E2: conecta las rutas declarativas de evaluación con la transacción GISELA."""

from __future__ import annotations

from dice import DiceError
from gisela.contracts.evaluation_plan import compile_package_evaluations
from traits import TraitsError

from .effect_context import EffectContext
from .traits_dice_bridge import resolve
from .world_base import WorldError


class EvaluationRoutes:
    """Índice inmutable por procedencia; ninguna ruta concede autoridad externa."""

    def __init__(self, package: dict):
        """Compila evaluaciones una sola vez, sin consultar el mundo ni RNG."""
        plans = (
            compile_package_evaluations(package)
            if package["manifest"]["format_version"]
            in ("1.4", "1.5", "1.6", "1.7", "1.8")
            else {}
        )
        self.routes = {}
        for ni, node in enumerate(package["nodes"]):
            for si, step in enumerate(node["steps"]):
                path = f"/nodes/{ni}/steps/{si}"
                self._add(("step", node["id"], step["id"]), path, plans)
                for oi, option in enumerate(step.get("options", [])):
                    key = ("choice", node["id"], step["id"], option["id"])
                    self._add(key, f"{path}/options/{oi}", plans)
        for si, scene in enumerate(package["scenes"]):
            path = f"/scenes/{si}"
            for ai, action in enumerate(scene.get("actions", [])):
                self._add(
                    ("scene", scene["id"], None, action["id"]),
                    f"{path}/actions/{ai}",
                    plans,
                )
            for ei, element in enumerate(scene.get("elements", [])):
                for ai, action in enumerate(element.get("actions", [])):
                    key = ("scene", scene["id"], element["id"], action["id"])
                    self._add(key, f"{path}/elements/{ei}/actions/{ai}", plans)

    def _add(self, key: tuple, path: str, plans: dict) -> None:
        """Conserva únicamente las rutas con una evaluación declarada."""
        if path in plans:
            self.routes[key] = plans[path]

    def execute(self, session, state: dict, request: tuple) -> dict:
        """Calcula DICE y confirma la rama solamente en el borrador recibido."""
        key, decisions = request
        plan = self.routes.get(key)
        if plan is None:
            raise WorldError(
                "INVALID_STATE", "No existe evaluación declarada para este origen"
            )
        try:
            resolved = resolve(state, plan["request"], session._definitions)
        except (DiceError, TraitsError, OverflowError) as exc:
            raise WorldError(
                "INVALID_STATE", f"Evaluación efectiva inválida: {exc}"
            ) from exc
        decisions.evaluations.resolve((key, plan, state, resolved))
        branch = plan["branches"][resolved["dice"]["outcome"]]
        session._operations(
            state,
            branch.get("effects", []),
            EffectContext(plan["id"], decisions, session._definitions),
        )
        return branch
