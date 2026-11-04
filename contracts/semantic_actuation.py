"""Invariantes del plan autoral y de su reloj persistido."""

from __future__ import annotations


class ActuationPackageMixin:
    def _check_actuation_plan(self, pkg: dict) -> None:
        plan = pkg.get("actuation")
        if plan is None:
            return
        actors = {x["id"] for x in pkg["initial_state"]["characters"]}
        seen = set()
        for index, person in enumerate(plan["participants"]):
            prefix = f"/actuation/participants/{index}"
            actor = person["character"]
            if actor not in actors:
                self.report(
                    "UNKNOWN_ACTOR", prefix + "/character", "Actor de actuación ausente"
                )
            if actor in seen:
                self.report("DUPLICATE_ACTOR", prefix + "/character", "Actor repetido")
            seen.add(actor)
            self._check_actuation_candidates(person, prefix, pkg)
            if (
                not person.get("allow_pass", False)
                and not person.get("candidates")
                and actor != pkg["initial_state"].get("player_character")
            ):
                self.report("ACTUATION_NO_POLICY", prefix, "NPC sin política ni pase")
        for index, op in enumerate(plan.get("setup", [])):
            self.operation(op, f"/actuation/setup/{index}")
        marks = [x["at"] for x in plan.get("thresholds", [])]
        if marks != sorted(set(marks)):
            self.report(
                "ACTUATION_THRESHOLDS",
                "/actuation/thresholds",
                "Umbrales deben ser crecientes y únicos",
            )

    def _check_actuation_candidates(self, person, prefix, pkg):
        actor = person["character"]
        owners = {x["id"]: x["character"] for x in pkg["initial_state"]["skills"]}
        cards = {x["id"]: x for x in pkg["cards"]}
        for j, candidate in enumerate(person.get("candidates", [])):
            key = candidate["skill_instance"]
            if key not in owners or owners[key] != actor:
                self.report(
                    "ACTUATION_SKILL_OWNER",
                    prefix + f"/candidates/{j}",
                    "Carta de otro actor o ausente",
                )
            else:
                instance = next(
                    x for x in pkg["initial_state"]["skills"] if x["id"] == key
                )
                card = cards[instance["card"]]
                if card.get("kind") != "skill" or card.get("passive_traits"):
                    self.report(
                        "ACTUATION_PASSIVE",
                        prefix + f"/candidates/{j}",
                        "Carta no ejecutable",
                    )
                declared = {p["id"] for p in card["play"].get("parameters", [])}
                if set(candidate.get("arguments", {})) != declared:
                    self.report(
                        "ACTUATION_PARAMETERS",
                        prefix + f"/candidates/{j}",
                        "Parámetros no coinciden",
                    )
            if "when" in candidate:
                self.condition(candidate["when"], prefix + f"/candidates/{j}/when")


class ActuationSnapshotMixin:
    def _check_actuation_snapshot(self, snapshot: dict, package: dict) -> None:
        """No acepta relojes huérfanos ni cursors ajenos al plan autoral."""
        plan = package.get("actuation")
        clock = snapshot.get("actuation")
        if plan is None:
            if clock is not None:
                self.report(
                    "ACTUATION_UNEXPECTED", "/actuation", "Reloj sin plan autoral"
                )
            return
        if clock is None:
            self.report("ACTUATION_MISSING", "/actuation", "Falta reloj del plan")
            return
        self._check_clock_policies(clock, plan)
        self._check_clock_initiative(clock, plan)
        self._check_clock_position(clock)
        self._check_clock_effects(snapshot, plan)

    def _check_clock_policies(self, clock, plan):
        if clock.get("event_policies", []) != plan.get("event_policies", []):
            self.report(
                "ACTUATION_POLICIES", "/actuation/event_policies", "Políticas alteradas"
            )
        if clock.get("outcome_policies", []) != plan.get("outcome_policies", []):
            self.report(
                "ACTUATION_POLICIES",
                "/actuation/outcome_policies",
                "Desenlaces alterados",
            )
        declared_events = {p["id"] for p in plan.get("event_policies", [])}
        if not set(clock.get("fired", [])).issubset(declared_events):
            self.report(
                "ACTUATION_POLICIES", "/actuation/fired", "Acontecimientos desconocidos"
            )
        declared_results = {p["id"] for p in plan.get("outcome_policies", [])}
        if (
            clock.get("outcome") is not None
            and clock["outcome"] not in declared_results
        ):
            self.report(
                "ACTUATION_POLICIES", "/actuation/outcome", "Desenlace desconocido"
            )

    def _check_clock_initiative(self, clock, plan):
        expected = [p["character"] for p in plan["participants"]]
        order = clock["order"]
        if len(expected) != len(set(expected)):
            self.report(
                "ACTUATION_DUPLICATE",
                "/actuation/order",
                "Plan con personajes repetidos",
            )
        if set(order) != set(expected) or len(order) != len(expected):
            self.report(
                "ACTUATION_ORDER", "/actuation/order", "Participantes alterados"
            )
        initiative = clock["initiative"]
        if [p["actor"] for p in initiative] != order:
            self.report(
                "ACTUATION_INITIATIVE",
                "/actuation/initiative",
                "Orden y puntuación no coinciden",
            )
        for index, item in enumerate(initiative):
            if (
                item["score"]
                != item["strength"] + item["awareness"] + item["fortune"] + item["die"]
                or not 1 <= item["die"] <= plan["initiative_die"]
            ):
                self.report(
                    "ACTUATION_INITIATIVE",
                    f"/actuation/initiative/{index}",
                    "Puntuación inválida",
                )

    def _check_clock_position(self, clock):
        order = clock["order"]
        if not 0 <= clock["index"] <= len(order):
            self.report(
                "ACTUATION_CURSOR", "/actuation/index", "Cursor fuera del orden"
            )
        if clock["index"] == len(order) and not clock["complete"]:
            self.report(
                "ACTUATION_CURSOR", "/actuation/index", "Cursor activo fuera del orden"
            )
        if clock["remaining"] > 0 and clock["complete"]:
            self.report(
                "ACTUATION_CURSOR",
                "/actuation/remaining",
                "Reloj finalizado con acciones",
            )
        if [e["sequence"] for e in clock["events"]] != list(
            range(1, len(clock["events"]) + 1)
        ):
            self.report(
                "ACTUATION_TRACE", "/actuation/events", "Secuencia causal inconsistente"
            )

    def _check_clock_effects(self, snapshot, plan):
        clock = snapshot["actuation"]
        expected = [p["character"] for p in plan["participants"]]
        if len({e["id"] for e in clock["effects"]}) != len(clock["effects"]):
            self.report(
                "ACTUATION_EFFECTS", "/actuation/effects", "Identidades duplicadas"
            )
        for effect in clock["effects"]:
            if effect["beneficiary"] not in expected:
                self.report(
                    "ACTUATION_EFFECTS",
                    "/actuation/effects",
                    "Beneficiario no participante",
                )
            if effect.get("linked") and not any(
                x["id"] == effect["id"] and x["target"] == effect["beneficiary"]
                for x in snapshot["world"]["effects"]
            ):
                self.report(
                    "ACTUATION_EFFECTS",
                    "/actuation/effects",
                    "Efecto enlazado ausente del mundo",
                )
