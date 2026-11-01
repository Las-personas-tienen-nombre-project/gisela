"""E1: admisión semántica de evaluaciones, sin ejecutar DICE ni el mundo."""

from __future__ import annotations

if __package__:
    from .evaluation_plan import (
        EvaluationPlanError,
        normalize_evaluation,
        profile_catalog,
    )
    from .semantic_shared import RefLocation
else:
    from evaluation_plan import (
        EvaluationPlanError,
        normalize_evaluation,
        profile_catalog,
    )
    from semantic_shared import RefLocation


class EvaluationsMixin:
    def _prepare_evaluations(self, package: dict) -> None:
        """Valida el catálogo una vez; nunca habilita ejecución de paquetes E1."""
        self.evaluation_profiles = {}
        try:
            self.evaluation_profiles = profile_catalog(package)
        except (EvaluationPlanError, KeyError, TypeError) as exc:
            self.report("DICE_PROFILE_INVALID", "/dice_profiles", str(exc))

    def _check_evaluation(self, spec: dict, node: dict | None, path: str) -> None:
        """Exige un plan completo y comprueba la procedencia de cada referencia."""
        try:
            normalize_evaluation(spec, self.evaluation_profiles)
        except (EvaluationPlanError, KeyError, TypeError) as exc:
            self.report("EVALUATION_INVALID", path, str(exc))
        self._check_evaluation_inputs(spec, path)
        self._check_evaluation_destinations(spec, node, path)

    def _check_evaluation_inputs(self, spec: dict, path: str) -> None:
        base = spec["inputs"]["base"]
        if "stat" in base:
            stat = base["stat"]
            char = stat["character"]
            point = path + "/inputs/base/stat/character"
            self.entity_ref(char, "character", RefLocation(point))
            # Las entidades creadas durante la ejecución pueden no existir aún,
            # pero si la carta es conocida debe disponer de S.O.F.I.A.
            entry = self.instances.get(char)
            if entry and entry[0] == "character":
                card = self.cards["character"].get(entry[1]["card"], {})
                if "sofia" not in card:
                    self.report(
                        "MISSING_SOFIA",
                        point,
                        "Referencia de evaluación sin carta S.O.F.I.A.",
                    )
        participants = spec.get("context", {}).get("participants", [])
        ids = set()
        for i, participant in enumerate(participants):
            entity = participant["entity"]
            point = f"{path}/context/participants/{i}/entity"
            if entity in ids:
                self.report("DUPLICATE_PARTICIPANT", point, "Entidad TRAITS repetida")
            ids.add(entity)
            self.entity_ref(
                entity, {"character", "object", "location"}, RefLocation(point)
            )

    def _check_evaluation_destinations(
        self, spec: dict, node: dict | None, path: str
    ) -> None:
        for i, branch in enumerate(spec["branches"]):
            if "next" in branch:
                point = f"{path}/branches/{i}/next"
                if node is None and "step" in branch["next"]:
                    self.report(
                        "INVALID_SCENE_DESTINATION",
                        point,
                        "Una acción de escena no puede saltar a un paso local",
                    )
                else:
                    self.destination(branch["next"], node, point)
