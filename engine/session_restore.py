"""Validación de restauración y reconstrucción de sesiones."""

from __future__ import annotations

import copy
from typing import Self

from gisela.contracts.admit_package import AdmittedPackage
from gisela.contracts.semantic_validator import Validator

from .errors import EngineFailure
from .pending import DecisionReplay, DecisionRequired
from .world import WorldError


class RestoreMixin:
    """Reconstruye snapshots sin confirmar borradores."""

    @classmethod
    def restore_session(
        cls, admitted: AdmittedPackage, snapshot: dict, language: str | None = None
    ) -> Self:
        """Congela la entrada, valida y reconstruye sin confirmar borradores."""
        frozen = copy.deepcopy(snapshot)
        issues = Validator().validate_session(
            frozen, admitted.materialize(), expected_digest=admitted.digest
        )
        errors = [i for i in issues if i.severity == "error"]
        if errors:
            raise EngineFailure(
                "RESTORE_MISMATCH",
                f"{errors[0].code} {errors[0].path}: {errors[0].message}",
            )
        session = cls(admitted, frozen, language)
        if frozen["status"] == "preparing" and (
            not (frozen.get("pending_transaction") or frozen.get("pending_evaluation"))
            or (frozen.get("pending_transaction") or frozen.get("pending_evaluation"))[
                "source"
            ]["kind"]
            != "session_start"
        ):
            raise EngineFailure(
                "INVALID_STATE", "Preparación exige un inicio pendiente"
            )
        try:
            if frozen["status"] == "node":
                step = session._current_step(frozen)
                if step["op"] not in ("narrate", "dialogue", "choice", "skill_window"):
                    raise WorldError("INVALID_STATE", "Cursor no observable")
            if frozen.get("pending_transaction"):
                session._validate_replay(frozen)
            if frozen.get("pending_evaluation"):
                session._validate_evaluation_replay(frozen)
            session._project_state(frozen)
        except (WorldError, KeyError, TypeError, ValueError, StopIteration) as exc:
            raise EngineFailure(
                "RESTORE_MISMATCH", f"Proyección restaurada inválida: {exc}"
            ) from exc
        return session

    def _validate_replay(self, snapshot: dict) -> None:
        """Comprueba que una espera guardada se reconstruya exactamente."""
        pending = snapshot["pending_transaction"]
        kind = pending["source"]["kind"]
        expected = (
            "voluntary"
            if kind in ("choice_option", "skill_play", "scene_action")
            else "mandatory"
        )
        if (
            kind
            in (
                "choice_option",
                "skill_play",
                "scene_action",
                "node_step",
                "session_start",
            )
            and pending["origin"] != expected
        ):
            raise EngineFailure(
                "RESTORE_MISMATCH", "Origen y cancelabilidad no coinciden"
            )
        draft = copy.deepcopy(snapshot)
        del draft["pending_transaction"]
        try:
            self._execute_source(
                draft, pending["source"], DecisionReplay(pending["answers"])
            )
        except DecisionRequired as required:
            if required.request != pending["request"]:
                raise EngineFailure(
                    "RESTORE_MISMATCH", "Solicitud distinta de la reconstrucción"
                )
        except (WorldError, KeyError, TypeError, ValueError, StopIteration) as exc:
            raise EngineFailure(
                "RESTORE_MISMATCH", f"Falló la reconstrucción: {exc}"
            ) from exc
        else:
            raise EngineFailure(
                "RESTORE_MISMATCH", "La operación ya no necesita respuesta"
            )

    def _validate_evaluation_replay(self, snapshot: dict) -> None:
        from .evaluation_pending import validate_replay

        validate_replay(self, snapshot)
