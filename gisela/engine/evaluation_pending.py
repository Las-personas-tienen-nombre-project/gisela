"""E3: guardado y verificación de una evaluación suspendida.

La autoridad y el único commit siguen siendo de GiselaSession.
"""

from __future__ import annotations

import copy

from .errors import EngineFailure
from .pending import DecisionReplay, DecisionRequired, EvaluationPause, EvaluationReplay
from .world_base import WorldError


def validate_replay(session, snapshot: dict) -> None:
    """Restauración adversarial: verifica lugar, resultados y RNG sin commit."""
    pending = snapshot["pending_evaluation"]
    draft = copy.deepcopy(snapshot)
    draft.pop("pending_evaluation")
    draft["rng"] = copy.deepcopy(pending["rng_initial"])
    auxiliary = pending.get("auxiliary_request")
    decisions = DecisionReplay(
        pending["answers"],
        EvaluationReplay(pending["fixed"], validate_pending=not bool(auxiliary)),
    )
    try:
        session._execute_source(draft, pending["source"], decisions)
    except EvaluationPause as paused:
        if (
            auxiliary
            or paused.entry != pending["fixed"][-1]
            or draft["rng"] != snapshot["rng"]
        ):
            raise EngineFailure("RESTORE_MISMATCH", "RNG o resultado fijo incoherente")
    except DecisionRequired as required:
        if (
            not auxiliary
            or required.request != auxiliary
            or decisions.evaluations.index != len(pending["fixed"])
        ):
            raise EngineFailure(
                "RESTORE_MISMATCH", "Solicitud auxiliar no reconstruible"
            )
    except (WorldError, KeyError, TypeError, ValueError, StopIteration) as exc:
        raise EngineFailure(
            "RESTORE_MISMATCH", f"No se reconstruye la tirada fija: {exc}"
        ) from exc
    else:
        raise EngineFailure("RESTORE_MISMATCH", "Evaluación pendiente ya aplicada")


def publish(session, data: dict) -> dict:
    """Confirma únicamente RNG y resultado, sin efectos provisionales."""
    current, draft = data["current"], data["draft"]
    intent, paused = data["intent"], data["paused"]
    initial = data.get("initial", False)
    previous = current.get("pending_evaluation")
    fixed = copy.deepcopy(previous["fixed"]) if previous else []
    fixed.append(copy.deepcopy(paused.entry))
    pending = copy.deepcopy(current)
    pending.pop("pending_transaction", None)
    pending["revision"] += 1
    pending["rng"] = copy.deepcopy(draft["rng"])
    if initial and "current_scene" not in current:
        pending["status"] = "preparing"
        pending["preparing_for"] = session._package["manifest"]["entry"]["node"]
    pending["pending_evaluation"] = {
        "evaluation_id": f"evaluation_{pending['revision']:06d}",
        "prepared_revision": pending["revision"],
        "origin": intent["origin"],
        "source": copy.deepcopy(intent["source"]),
        "initiated_revision": intent["initiated_revision"],
        "rng_initial": copy.deepcopy(
            previous["rng_initial"] if previous else current["rng"]
        ),
        "fixed": fixed,
        "answers": copy.deepcopy(intent["answers"]),
    }
    session._validate_state(pending)
    view = session._project_state(pending)
    session._state = pending
    return {"status": "ok", "revision": pending["revision"], "view": view}
