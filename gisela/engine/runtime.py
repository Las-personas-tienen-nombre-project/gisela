"""GISELA MVP H2 y H3 parcial. Autoridad de sesión y ejecución de nodos.

Contrato público: new_session(), restore_session(), observe(), act(), export().
ALBERTO no modifica estado confirmado por su cuenta. Todas las operaciones
se ejecutan sobre una copia que solo se confirma tras completar reacciones.
"""

from __future__ import annotations

import copy
from threading import RLock

from gisela.contracts.admit_package import AdmittedPackage
from gisela.contracts.semantic_validator import Validator

from .action_handler import act as handle_act
from .conditions import predicate
from .consequences import apply_operation
from .effect_context import EffectContext
from .errors import EngineFailure
from .initialization import initial_state
from .pending import DecisionReplay, DecisionRequired, EvaluationPause
from .projection import observe as project_observe
from .reactions import ReactionContext, settle
from .skill_window import exhausted
from .support import check_supported
from .world import WorldError
from .world_values import WorldDefinitions

MAX_AUTOMATIC_STEPS = 512


def _text(value: object) -> str:
    """Extrae texto localizado en el idioma principal de la vertical."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict) and isinstance(value.get("text"), str):
        return value["text"]
    raise WorldError("INVALID_STATE", "Texto localizado sin variante principal")


class GiselaSession:
    """Autoridad de estado confirmado, proyección y transacción narrativa."""

    def __init__(self, admitted: AdmittedPackage, state: dict):
        """Copia definiciones y estado; rechaza formatos no ejecutables."""
        self._admitted = admitted
        self._package = admitted.materialize()
        check_supported(self._package)
        self._nodes = {node["id"]: node for node in self._package["nodes"]}
        self._cards = {card["id"]: card for card in self._package["cards"]}
        manifest = self._package["manifest"]
        from traits import compile_catalog

        self._traits = (
            compile_catalog(self._package["traits"])
            if "traits" in self._package
            else None
        )
        self._definitions = WorldDefinitions(
            self._cards,
            {f["id"]: f for f in manifest.get("relationship_fields", [])},
            {(v["scope"], v["id"]): v for v in manifest.get("variables", [])},
            manifest.get("sofia_scale", {"min": 0, "max": 10}),
            self._traits,
        )
        self._rules = self._package["rules"]
        from mary import compile_plan

        self._mary = (
            compile_plan(self._package["mary"]) if "mary" in self._package else None
        )
        self._scenes = {scene["id"]: scene for scene in self._package["scenes"]}
        from .evaluation_execution import EvaluationRoutes

        self._evaluations = EvaluationRoutes(self._package)
        self._state = copy.deepcopy(state)
        self._lock = RLock()
        self._gateway_attached = False

    @classmethod
    def new_session(
        cls,
        admitted: AdmittedPackage,
        session_id: str = "mvp_session",
        seed: str = "0" * 64,
    ) -> GiselaSession:
        """Inicializa y valida hasta un paso observable o rechaza la creación."""
        pkg = admitted.materialize()
        state = initial_state(
            pkg, admitted.digest, {"session_id": session_id, "seed": seed}
        )
        session = cls(admitted, state)
        if "scene" in pkg["manifest"]["entry"]:
            session._start_scene_entry(state)
            from .reading_log import entry

            entry(session, state)
            session._validate_state(state)
            session._project_state(state)
            return session
        draft = copy.deepcopy(state)
        try:
            session._start_entry(draft, DecisionReplay())
        except EvaluationPause as paused:
            session._publish_evaluation(
                {
                    "current": state,
                    "draft": draft,
                    "intent": {
                        "origin": "mandatory",
                        "source": {"kind": "session_start"},
                        "initiated_revision": 0,
                        "answers": [],
                    },
                    "paused": paused,
                    "initial": True,
                }
            )
            return session
        except DecisionRequired as required:
            if "current_scene" not in state:
                state["status"] = "preparing"
                state["preparing_for"] = pkg["manifest"]["entry"]["node"]
            session._publish_pending(
                state,
                {
                    "origin": "mandatory",
                    "source": {"kind": "session_start"},
                    "initiated_revision": 0,
                    "answers": [],
                    "request": required.request,
                },
            )
            return session
        return session._confirm_initial(draft, state)

    def _confirm_initial(self, draft: dict, state: dict) -> GiselaSession:
        """Confirma el primer paso y su texto, si terminó sin solicitudes."""
        if (
            draft["world"] != state["world"]
            or draft["narrative"] != state["narrative"]
            or draft["history"]["facts"] != state["history"]["facts"]
            or draft.get("mary") != state.get("mary")
            or draft.get("current_scene") != state.get("current_scene")
            or draft["world_time"] != state["world_time"]
        ):
            draft["world_revision"] += 1
        draft["revision"] += 1
        if draft["status"] == "exploring" and "current_scene" not in draft:
            raise EngineFailure(
                "INVALID_STATE", "Nodo agotado sin escena, transición ni final"
            )
        from .reading_log import entry

        entry(self, draft)
        self._validate_state(draft)
        self._project_state(draft)
        self._state = draft
        return self

    @classmethod
    def restore_session(
        cls, admitted: AdmittedPackage, snapshot: dict
    ) -> GiselaSession:
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
        session = cls(admitted, frozen)
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

    def _start_scene_entry(self, state: dict) -> None:
        """Valida una entrada exploratoria sin iniciar turno ficticio."""
        state["current_scene"] = self._package["manifest"]["entry"]["scene"]
        settle(
            state,
            [],
            ReactionContext(
                self._rules, DecisionReplay(), self._definitions, self._mary
            ),
        )
        self._validate_state(state)
        self._project_state(state)
        self._state = state

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

    def export(self) -> dict:
        """Snapshot confirmado, copiado; el anfitrión decide cómo guardarlo."""
        with self._lock:
            return copy.deepcopy(self._state)

    def _validate_state(self, state: dict) -> None:
        """Rechaza un borrador que incumpla el schema o invariantes semánticas."""
        issues = Validator()._validate_admitted_session(
            state, self._package, self._admitted.digest
        )
        errors = [i for i in issues if i.severity == "error"]
        if errors:
            raise WorldError(
                "INVALID_STATE",
                f"Sesión inconsistente: {errors[0].code} {errors[0].message}",
            )

    def _current_step(self, state: dict) -> dict:
        """Resuelve el cursor de un nodo activo a su definición de paso."""
        cursor = state["cursor"]
        return next(
            step
            for step in self._nodes[cursor["node"]]["steps"]
            if step["id"] == cursor["step"]
        )

    def _start_entry(self, state: dict, decisions: DecisionReplay) -> None:
        """Repite la entrada del paquete sin confirmar cambios intermedios."""
        self._enter_node(state, self._package["manifest"]["entry"]["node"], decisions)
        self._run_automatic(state, decisions)

    def _enter_node(self, state: dict, node_id: str, decisions=None) -> None:
        """Abre una ejecución y un turno en el borrador; resuelve turn_started."""
        state["turn"] += 1
        eid = f"execution_{state['turn']:06d}"
        node = self._nodes[node_id]
        state["history"]["executions"].append(
            {
                "execution_id": eid,
                "node": node_id,
                "turn": state["turn"],
                "started_at": state["world_time"],
                "completed": False,
                "selected_options": [],
            }
        )
        state["cursor"] = {
            "node": node_id,
            "step": node["steps"][0]["id"],
            "execution_id": eid,
        }
        state["status"] = "node"
        settle(
            state,
            [{"on": "turn_started"}],
            ReactionContext(self._rules, decisions, self._definitions, self._mary),
        )

    def _close_node(self, state: dict, decisions=None) -> None:
        """Cierra la ejecución y resuelve juntos node_completed y turn_ended."""
        old_id = state["cursor"]["node"]
        item = state["history"]["executions"][-1]
        item["completed"] = True
        item["completed_at"] = state["world_time"]
        del state["cursor"]
        state["status"] = "exploring"
        settle(
            state,
            [{"on": "node_completed", "node": old_id}, {"on": "turn_ended"}],
            ReactionContext(self._rules, decisions, self._definitions, self._mary),
        )

    def _jump(self, state: dict, destination: dict | None, decisions=None) -> None:
        """Avanza de paso o cierra el nodo antes de entrar en otro."""
        if destination is not None and "node" in destination:
            self._close_node(state, decisions)
            self._enter_node(state, destination["node"], decisions)
            return
        steps = self._nodes[state["cursor"]["node"]]["steps"]
        if destination is None:
            idx = (
                next(
                    i for i, s in enumerate(steps) if s["id"] == state["cursor"]["step"]
                )
                + 1
            )
            if idx == len(steps):
                self._close_node(state, decisions)
                return
            step_id = steps[idx]["id"]
        else:
            step_id = destination["step"]
        state["cursor"]["step"] = step_id

    def _operations(
        self, state: dict, operations: list[dict], context: EffectContext
    ) -> None:
        """Aplica consecuencias y sus reacciones dentro del mismo borrador."""
        events = []
        for op in operations:
            events.extend(apply_operation(state, op, context))
        settle(
            state,
            events,
            ReactionContext(
                self._rules, context.decisions, context.definitions, self._mary
            ),
        )

    def _evaluate(self, state: dict, key: tuple, decisions) -> dict:
        """Resuelve una rama oculta en el mismo borrador causal."""
        return self._evaluations.execute(self, state, (key, decisions))

    def _scene_step(self, state: dict, step: dict) -> None:
        """Valida y presenta un cambio de escena declarado."""
        if step["scene"] not in self._scenes:
            raise WorldError("INVALID_REFERENCE", "Escena inexistente")
        state["current_scene"] = step["scene"]

    def _run_automatic(self, state: dict, decisions=None) -> None:
        """Ejecuta pasos no observables hasta un límite de 512 por acción."""
        for _ in range(MAX_AUTOMATIC_STEPS):
            if state["status"] != "node":
                return
            step = self._current_step(state)
            op = step["op"]
            if op in ("narrate", "dialogue", "choice"):
                return
            if op == "skill_window" and not exhausted(state, step):
                return
            if op == "skill_window":
                self._jump(state, None, decisions)
                continue
            if op == "scene":
                self._scene_step(state, step)
                self._jump(state, None, decisions)
            elif op == "evaluate":
                self._automatic_evaluation(state, step, decisions)
                continue
            elif op == "effect":
                self._operations(
                    state,
                    step["effects"],
                    EffectContext(step["id"], decisions, self._definitions),
                )
                self._jump(state, None, decisions)
            elif op in ("condition", "transition"):
                self._automatic_branch(state, step, decisions)
            elif op == "ending":
                ending_id = step["ending"]
                self._close_node(state, decisions)
                state["status"] = "ended"
                state["ending"] = ending_id
                return
            else:
                raise WorldError("INVALID_STATE", f"Paso no implementado: {op}")
        raise WorldError(
            "BUDGET_EXCEEDED", "Cadena de pasos automáticos demasiado extensa"
        )

    def _automatic_evaluation(self, state: dict, step: dict, decisions) -> None:
        """Resuelve un paso de evaluación oculto sin crear cursor público."""
        key = ("step", state["cursor"]["node"], step["id"])
        branch = self._evaluate(state, key, decisions)
        self._jump(state, branch.get("next"), decisions)

    def _automatic_branch(self, state: dict, step: dict, decisions) -> None:
        """Resuelve bifurcaciones estáticas o condicionadas en un borrador."""
        if step["op"] == "condition":
            branch = (
                "then" if predicate(state, step["test"], self._definitions) else "else"
            )
            destination = step.get(branch)
        else:
            destination = step["next"]
        self._jump(state, destination, decisions)

    def debug_query(self, request: dict) -> dict:
        """Diagnóstico explícito para autores, ajeno a Observe del jugador."""
        from .queries import query

        with self._lock:
            return query(self, request)

    def scoresheet(self, character: str) -> dict:
        """Consulta atributos y cartas desde el estado confirmado."""
        from .sofia import scoresheet

        with self._lock:
            return scoresheet(self._state, character, self._definitions)

    def read_public(self, identifier: str) -> dict:
        """Entrega solo una ficha que el jugador puede conocer."""
        from .public_view import inspect

        with self._lock:
            return inspect(self, identifier)

    def player_status(self) -> dict:
        """Consulta únicamente los atributos del protagonista visible."""
        from .public_view import status

        with self._lock:
            return status(self)

    def read_history(self, limit: int | None = None) -> list[dict]:
        """Consulta los textos narrativos confirmados, nunca los borradores."""
        from .reading_log import history

        with self._lock:
            return history(self, limit)

    def _project_state(self, candidate: dict) -> dict:
        """Proyecta un candidato sin cambiar el estado confirmado."""
        temporary = copy.copy(self)
        temporary._state = candidate
        result = project_observe(temporary)
        validator = Validator()
        validator.use_version(candidate["schema_version"])
        if not validator.check_schema("observe", result):
            raise WorldError(
                "INVALID_STATE", "La proyección candidata incumple el contrato"
            )
        return result

    def observe(self) -> dict:
        """Entrega la proyección confirmada sin publicar el borrador."""
        with self._lock:
            return project_observe(self)

    def _source_start(self, draft: dict, decisions: DecisionReplay) -> None:
        """Reproduce el inicio de sesión desde el estado confirmado."""
        if (
            draft["status"] not in ("exploring", "preparing")
            or draft["turn"] != 0
            or draft["history"]["executions"]
            or "cursor" in draft
            or (
                draft["status"] == "preparing"
                and draft.get("preparing_for")
                != self._package["manifest"]["entry"]["node"]
            )
        ):
            raise WorldError("REPLAY_MISMATCH", "El inicio de sesión ya fue ejecutado")
        draft.pop("preparing_for", None)
        draft["status"] = "exploring"
        self._start_entry(draft, decisions)

    def _source_step(
        self, draft: dict, source: dict, decisions: DecisionReplay
    ) -> None:
        """Revalida la procedencia exacta de un avance de paso."""
        step = self._current_step(draft)
        if (
            draft["status"] != "node"
            or draft["cursor"]["node"] != source["node"]
            or step["id"] != source["step"]
            or step["op"] not in ("narrate", "dialogue", "skill_window")
        ):
            raise WorldError(
                "REPLAY_MISMATCH", "Ya no existe el paso de avance original"
            )
        self._jump(draft, None, decisions)

    def _source_choice(
        self, draft: dict, source: dict, decisions: DecisionReplay
    ) -> None:
        """Revalida la elección y sus condiciones antes de aplicarla."""
        step = self._current_step(draft)
        if (
            draft["status"] != "node"
            or draft["cursor"]["node"] != source["node"]
            or step["id"] != source["step"]
            or step["op"] != "choice"
        ):
            raise WorldError("REPLAY_MISMATCH", "Ya no existe la elección original")
        option = next((o for o in step["options"] if o["id"] == source["option"]), None)
        if (
            option is None
            or not predicate(
                draft, option.get("visible_if", {"constant": True}), self._definitions
            )
            or not predicate(
                draft, option.get("enabled_if", {"constant": True}), self._definitions
            )
        ):
            raise WorldError(
                "REPLAY_MISMATCH", "La opción original ya no está autorizada"
            )
        draft["history"]["executions"][-1]["selected_options"].append(
            {"step_id": step["id"], "option_id": option["id"]}
        )
        if "evaluation" in option:
            key = ("choice", source["node"], step["id"], option["id"])
            branch = self._evaluate(draft, key, decisions)
            self._jump(draft, branch.get("next"), decisions)
        else:
            self._operations(
                draft,
                option.get("effects", []),
                EffectContext(step["id"], decisions, self._definitions),
            )
            self._jump(draft, option.get("next"), decisions)

    def _source_skill(
        self, draft: dict, source: dict, decisions: DecisionReplay
    ) -> None:
        """Revalida el uso de una habilidad desde la ventana activa."""
        from .skill_execution import SkillRequest, execute
        from .skill_window import exhausted

        if draft["status"] == "exploring":
            if not self._scenes[draft["current_scene"]].get("allow_skill_play", False):
                raise WorldError(
                    "REPLAY_MISMATCH", "La escena no permite jugar habilidades"
                )
        else:
            step = self._current_step(draft)
            if (
                draft["status"] != "node"
                or step["op"] != "skill_window"
                or exhausted(draft, step)
            ):
                raise WorldError(
                    "REPLAY_MISMATCH", "La ventana de habilidad ya no está abierta"
                )
        execute(self, draft, SkillRequest(source["skill_instance"], decisions))

    def _execute_source(
        self, draft: dict, source: dict, decisions: DecisionReplay
    ) -> None:
        """Reconstruye una intención sin guardar estados provisionales."""
        draft.pop("pending_transaction", None)
        kind = source["kind"]
        if kind == "session_start":
            self._source_start(draft, decisions)
        elif kind == "node_step":
            self._source_step(draft, source, decisions)
        elif kind == "choice_option":
            self._source_choice(draft, source, decisions)
        elif kind == "skill_play":
            self._source_skill(draft, source, decisions)
        elif kind == "scene_action":
            from .scene_actions import execute_source

            execute_source(self, draft, (source, decisions))
        else:
            raise WorldError(
                "UNSUPPORTED_FORMAT", f"Origen pendiente no ejecutable: {kind}"
            )
        if kind != "session_start":
            self._run_automatic(draft, decisions)
        decisions.completed()

    def _publish_evaluation(self, data: dict) -> dict:
        from .evaluation_pending import publish

        return publish(self, data)

    def _publish_pending(self, current: dict, intent: dict) -> None:
        """Guarda intención y solicitud; eleva revision sin publicar borrador."""
        pending = copy.deepcopy(current)
        pending["pending_transaction"] = {
            "origin": intent["origin"],
            "source": copy.deepcopy(intent["source"]),
            "initiated_revision": intent["initiated_revision"],
            "context": {},
            "answers": copy.deepcopy(intent["answers"]),
            "request": copy.deepcopy(intent["request"]),
        }
        pending["revision"] += 1
        self._validate_state(pending)
        view = self._project_state(pending)
        self._state = pending
        return {"status": "ok", "revision": pending["revision"], "view": view}

    def _commit(self, current: dict, draft: dict) -> dict:
        """Valida y sustituye el estado confirmado en un único punto."""
        draft.pop("pending_transaction", None)
        draft.pop("pending_evaluation", None)
        if (
            draft["world"] != current["world"]
            or draft["narrative"] != current["narrative"]
            or draft["history"]["facts"] != current["history"]["facts"]
            or draft.get("mary") != current.get("mary")
            or draft.get("current_scene") != current.get("current_scene")
            or draft["world_time"] != current["world_time"]
        ):
            draft["world_revision"] += 1
        draft["revision"] += 1
        if draft["status"] == "exploring" and "current_scene" not in draft:
            raise WorldError(
                "INVALID_STATE", "Nodo agotado sin escena, transición ni final"
            )
        from .reading_log import entry

        entry(self, draft, current)
        self._validate_state(draft)
        view = self._project_state(draft)
        self._state = draft
        return {"status": "ok", "revision": draft["revision"], "view": view}

    def act(self, request: dict) -> dict:
        """Frontera local; una sesión vinculada debe usarse mediante gateway."""
        with self._lock:
            if self._gateway_attached:
                return self._fail(
                    "INVALID_ACTION", "La sesión requiere acceso autorizado"
                )
            return handle_act(self, request)

    def _fail(self, code: str, message: str) -> dict:
        """Construye un resultado de rechazo sin mutar la sesión."""
        return {
            "status": "error",
            "revision": self._state["revision"],
            "error": {"code": code, "message": message},
        }


def new_session(
    admitted: AdmittedPackage, *, session_id: str = "mvp_session", seed: str = "0" * 64
) -> GiselaSession:
    """API pública de creación a partir de un paquete previamente admitido."""
    return GiselaSession.new_session(admitted, session_id=session_id, seed=seed)


def restore_session(admitted: AdmittedPackage, snapshot: dict) -> GiselaSession:
    """API pública de restauración contra el mismo digest de paquete."""
    return GiselaSession.restore_session(admitted, snapshot)
