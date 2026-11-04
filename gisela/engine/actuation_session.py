"""Interfaz de laboratorio del reloj autoral sobre la sesión transaccional."""

from __future__ import annotations

import copy

from .actuation import ActuationDuration


class ActuationSessionMixin:
    def actuation_observe(self) -> dict:
        """Vista del reloj autoral confirmado; no revela estado provisional."""
        with self._lock:
            if "actuation" not in self._state:
                return {"active": False}
            from .actuation import current

            clock = self._state["actuation"]
            actor = current(self._state)
            offers = []
            if actor == self._state.get("player_character"):
                from .conditions import predicate

                for skill in self._state["world"]["skills"]:
                    if skill["character"] != actor or skill["zone"] != "hand":
                        continue
                    card = self._cards[skill["card"]]
                    if (
                        card["kind"] != "skill"
                        or card.get("passive_traits")
                        or card["play"].get("parameters")
                    ):
                        continue
                    offers.append(
                        {
                            "id": skill["id"],
                            "label": skill["card"],
                            "enabled": predicate(
                                self._state,
                                card["play"].get("requires", {"constant": True}),
                                self._definitions,
                            ),
                        }
                    )
                person = next(
                    p
                    for p in self._package["actuation"]["participants"]
                    if p["character"] == actor
                )
                if person.get("allow_pass", False):
                    offers.append({"id": "pasar", "label": "Pasar", "enabled": True})
            elif actor is not None:
                offers.append({"id": "continuar", "label": "Actuar", "enabled": True})
            return {
                "offers": offers,
                "active": not clock["complete"],
                "outcome": clock.get("outcome"),
                "revision": self._state["revision"],
                "round": clock["round"],
                "actor": current(self._state),
                "remaining": clock["remaining"],
                "order": list(clock["order"]),
                "events": copy.deepcopy(clock["events"]),
            }

    def actuation_step(self, revision: int, skill_instance: str | None = None) -> dict:
        """Confirma una oportunidad en la misma sesión y RNG de GISELA.

        API de laboratorio para integraciones confiables; no reemplaza Act
        autenticado ni está todavía disponible para el jugador en GLAUQUIR.
        """
        from .actuation import step
        from .world_base import WorldError

        with self._lock:
            if self._gateway_attached:
                return self._fail("INVALID_ACTION", "Se requiere gateway autorizado")
            if revision != self._state["revision"]:
                return self._fail("STALE_PROJECTION", "Revisión vencida")
            if self._state.get("pending_transaction") or self._state.get(
                "pending_evaluation"
            ):
                return self._fail(
                    "INVALID_ACTION", "No se puede actuar durante una espera"
                )
            draft = copy.deepcopy(self._state)
            try:
                step(self, draft, skill_instance)
                draft["revision"] += 1
                draft["world_revision"] += 1
                self._validate_state(draft)
                self._project_state(draft)
            except (WorldError, ValueError, TypeError, KeyError) as exc:
                return self._fail(getattr(exc, "code", "INVALID_ACTION"), str(exc))
            self._state = draft
            return {
                "status": "ok",
                "revision": draft["revision"],
                "actuation": self.actuation_observe(),
            }

    def actuation_add_duration(
        self, revision: int, duration: ActuationDuration
    ) -> dict:
        """Declaración controlada de laboratorio; efectos de carta aún no enlazados."""
        from .actuation import add_duration
        from .world_base import WorldError

        with self._lock:
            if self._gateway_attached or revision != self._state["revision"]:
                return self._fail(
                    "INVALID_ACTION", "Acceso no autorizado o revisión vencida"
                )
            draft = copy.deepcopy(self._state)
            try:
                add_duration(draft, duration)
                draft["revision"] += 1
                self._validate_state(draft)
            except (WorldError, ValueError, TypeError, KeyError) as exc:
                return self._fail(getattr(exc, "code", "INVALID_ACTION"), str(exc))
            self._state = draft
            return {"status": "ok", "revision": draft["revision"]}
