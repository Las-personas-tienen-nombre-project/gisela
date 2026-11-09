"""Validación semántica, separada por responsabilidad."""

from __future__ import annotations

if __package__:
    from .semantic_actuation import ActuationSnapshotMixin
    from .semantic_shared import *
else:  # Compatibilidad de ejecución directa desde contracts/
    from semantic_actuation import ActuationSnapshotMixin
    from semantic_shared import *


class SessionsMixin(ActuationSnapshotMixin):
    """Grupo de comprobaciones sessions de un mismo validador."""

    def validate_session(
        self, snapshot: dict, package: dict, expected_digest: str | None = None
    ) -> list[Diagnostic]:
        """Valida snapshot y paquete cuando ambos llegan desde una frontera no confiable."""
        return self._validate_session(snapshot, (package, expected_digest, True))

    def _validate_admitted_session(
        self, snapshot: dict, package: dict, expected_digest: str
    ) -> list[Diagnostic]:
        """Valida solo el snapshot cuando el paquete ya pasó por admisión."""
        return self._validate_session(snapshot, (package, expected_digest, False))

    def _validate_session(self, snapshot: dict, detail: tuple) -> list[Diagnostic]:
        """Implementa las invariantes comunes sin duplicar semántica."""
        package, expected_digest, validate_package = detail
        self.issues = []
        version = (
            package.get("manifest", {}).get("format_version")
            if isinstance(package, dict)
            else None
        )
        if not self.use_version(version):
            return self.issues[:]
        if validate_package and not self.check_schema("package", package):
            return self.issues[:]
        if not self.check_schema("session", snapshot):
            return self.issues[:]
        if snapshot["schema_version"] != version:
            self.report(
                "SCHEMA_VERSION_MISMATCH",
                "/schema_version",
                "Versión de sesión incompatible",
            )
        if version in ("1.3", "1.4", "1.5", "1.6", "1.7"):
            self._check_traits_snapshot(snapshot, package)
        self._index_package(package)
        self._validate_package_identity(snapshot, package, expected_digest)
        self._check_instances_snapshot(snapshot)
        self._check_scene_location(snapshot)
        if "player_character" in snapshot:
            self.entity_ref(
                snapshot["player_character"],
                "character",
                RefLocation("/player_character"),
            )
        if "current_scene" in snapshot and snapshot["current_scene"] not in self.scenes:
            self.report(
                "UNKNOWN_SCENE", "/current_scene", "Escena de sesión inexistente"
            )
        if "preparing_for" in snapshot and snapshot["preparing_for"] not in self.nodes:
            self.report(
                "UNKNOWN_NODE", "/preparing_for", "Nodo en preparación inexistente"
            )
        if "ending" in snapshot and snapshot["ending"] not in self.endings:
            self.report("UNKNOWN_ENDING", "/ending", "Final inexistente")
        self._check_session_history(snapshot)
        self._check_actuation_snapshot(snapshot, package)
        self._check_pending(snapshot)
        if version in ("1.5", "1.6", "1.7"):
            self._check_pending_evaluation(snapshot)
        self._check_mary_snapshot(snapshot, package)
        self._check_revision_order(snapshot)
        return self.issues[:]

    def _validate_package_identity(self, snapshot, package, expected_digest) -> None:
        """Comprueba correspondencia con definiciones y digest confiable."""
        if snapshot["package_id"] != package["manifest"]["id"]:
            self.report(
                "PACKAGE_MISMATCH", "/package_id", "Snapshot pertenece a otro paquete"
            )
        try:
            actual_digest = package_digest(package)
            if expected_digest is not None and actual_digest != expected_digest:
                self.report(
                    "TRUSTED_DIGEST_MISMATCH",
                    "/package_digest",
                    "Digest externo no corresponde a las definiciones entregadas",
                )
            if snapshot["package_digest"] != actual_digest:
                self.report(
                    "DIGEST_MISMATCH",
                    "/package_digest",
                    "El guardado no corresponde al paquete canónico admitido",
                )
        except CanonicalError as exc:
            self.report("CANONICAL_REJECTED", "/package_digest", str(exc))

    def _check_revision_order(self, snapshot: dict) -> None:
        """Rechaza una revisión de mundo posterior a la revisión confirmada."""
        if snapshot["world_revision"] > snapshot["revision"]:
            self.report(
                "REVISION_ORDER",
                "/world_revision",
                "world_revision no puede superar revision",
            )

    def _check_scene_location(self, snapshot: dict) -> None:
        """Verifica que el protagonista ocupe el lugar de la escena física."""
        scene = self.scenes.get(snapshot.get("current_scene"))
        if not scene or "location" not in scene:
            return
        place = scene["location"]
        if place not in {item["id"] for item in snapshot["world"]["locations"]}:
            self.report(
                "SCENE_LOCATION_MISSING",
                "/current_scene",
                "Lugar de escena ausente del mundo",
            )
        player = snapshot.get("player_character")
        actor = next(
            (c for c in snapshot["world"]["characters"] if c["id"] == player), None
        )
        if actor is not None and actor["location"] != place:
            self.report(
                "SCENE_LOCATION_MISMATCH",
                "/current_scene",
                "Protagonista fuera de la ubicación de la escena física",
            )

    def _check_mary_snapshot(self, snapshot: dict, package: dict) -> None:
        """Rechaza progreso ausente o incompatible con el plan declarado."""
        if "mary" not in package:
            if "mary" in snapshot:
                self.report(
                    "MARY_UNEXPECTED", "/mary", "Progreso sin definiciones MARY"
                )
            return
        from mary import MaryError, compile_plan, validate_progress

        if "mary" not in snapshot:
            self.report("MARY_MISSING", "/mary", "Falta progreso MARY")
            return
        try:
            validate_progress(compile_plan(package["mary"]), snapshot["mary"])
        except (MaryError, KeyError, TypeError, ValueError) as exc:
            self.report("MARY_INVALID", "/mary", str(exc))

    def _check_instances_snapshot(self, snapshot):
        # Indexar estado actual (no sobreescribir las cartas).
        """Comprueba entidades del mundo guardado."""
        world = {
            **snapshot["world"],
            "session_variables": snapshot["narrative"]["session_variables"],
        }
        self.instances = {}
        for coll, kind in COLLECTION_KINDS.items():
            for i, item in enumerate(world[coll]):
                self._put_instance(item, kind, pointer("world", coll, i, "id"))
        self._check_instances(world, "world")
        used = snapshot["identity"]["used_instance_ids"]
        if len(used) != len(set(used)):
            self.report(
                "DUPLICATE_USED_ID",
                "/identity/used_instance_ids",
                "Registro de identidades usadas contiene duplicados",
            )
        for item in self.instances:
            if item not in used:
                self.report(
                    "UNRECORDED_ID",
                    "/identity/used_instance_ids",
                    f"Instancia activa {item} no aparece en registro",
                )
        for i, event in enumerate(snapshot["history"]["facts"]):
            if event["fact"] not in self.facts:
                self.report(
                    "UNKNOWN_FACT",
                    pointer("history", "facts", i, "fact"),
                    "Hecho histórico no declarado",
                )

    def _check_session_history(self, snapshot: dict) -> None:
        """Comprueba turnos, selecciones, cursor y secuencias de historial."""
        history = snapshot["history"]
        executions = history["executions"]
        ids, active, turns = set(), [], set()
        if len(executions) != snapshot["turn"]:
            self.report(
                "TURN_COUNT", "/history/executions", "Falta ejecución por turno"
            )
        for index, execution in enumerate(executions):
            path = pointer("history", "executions", index)
            self._check_execution(
                execution, (path, ids, turns, active, snapshot["turn"])
            )
        if turns != set(range(1, snapshot["turn"] + 1)):
            self.report(
                "TURN_SEQUENCE", "/history/executions", "Turnos no consecutivos"
            )
        self._check_cursor(snapshot, active)
        for group in ("facts", "trace"):
            sequence = [event["sequence"] for event in history[group]]
            if len(sequence) != len(set(sequence)):
                self.report(
                    "DUPLICATE_SEQUENCE", "/history/" + group, "Secuencias duplicadas"
                )
            if sequence != sorted(sequence):
                self.report(
                    "UNORDERED_HISTORY", "/history/" + group, "Historial desordenado"
                )
        for index, item in enumerate(history.get("reading", []), 1):
            if item["sequence"] != index or item["turn"] > snapshot["turn"]:
                self.report(
                    "READING_SEQUENCE",
                    "/history/reading",
                    "La lectura debe conservar orden y turnos confirmados",
                )

    def _check_execution(self, execution, detail: tuple) -> None:
        """Verifica la procedencia y el número de una ejecución."""
        path, ids, turns, active, turn = detail
        eid = execution["execution_id"]
        if eid in ids:
            self.report("DUPLICATE_EXECUTION", path + "/execution_id", "ID repetido")
        ids.add(eid)
        node = self.nodes.get(execution["node"])
        if node is None:
            self.report("UNKNOWN_NODE", path + "/node", "Nodo inexistente")
        else:
            for index, selected in enumerate(execution.get("selected_options", [])):
                point = pointer(path, "selected_options", index)
                self._check_selected(node, selected, point)
        if execution["turn"] in turns:
            self.report("DUPLICATE_TURN", path + "/turn", "Turno duplicado")
        turns.add(execution["turn"])
        if execution["turn"] > turn:
            self.report("TURN_MISMATCH", path + "/turn", "Turno futuro")
        if not execution["completed"]:
            active.append(execution)

    def _check_selected(self, node, selected, path) -> None:
        """Verifica que la opción pertenezca al paso de su nodo."""
        steps = {step["id"]: step for step in node["steps"]}
        step = steps.get(selected["step_id"])
        if not step or step["op"] != "choice":
            self.report(
                "UNKNOWN_CHOICE_STEP", path + "/step_id", "Paso no es una elección"
            )
        elif selected["option_id"] not in {item["id"] for item in step["options"]}:
            self.report(
                "UNKNOWN_SELECTED_OPTION", path + "/option_id", "Opción no existe"
            )

    def _check_cursor(self, snapshot, active) -> None:
        """Comprueba que solo la ejecución actual permanezca abierta."""
        cursor = snapshot.get("cursor")
        if snapshot["status"] != "node":
            if active:
                self.report(
                    "ACTIVE_EXECUTION",
                    "/history/executions",
                    "Ejecución activa sin nodo",
                )
            return
        matches = [e for e in active if e["execution_id"] == cursor["execution_id"]]
        if len(matches) != 1 or len(active) != 1:
            self.report(
                "ACTIVE_EXECUTION", "/cursor/execution_id", "Cursor sin ejecución única"
            )
        elif (
            matches[0]["node"] != cursor["node"]
            or matches[0]["turn"] != snapshot["turn"]
        ):
            self.report("CURSOR_MISMATCH", "/cursor", "Nodo o turno distintos")
        node = self.nodes.get(cursor["node"])
        if node and cursor["step"] not in {x["id"] for x in node["steps"]}:
            self.report("UNKNOWN_STEP", "/cursor/step", "Paso del cursor no existe")

    def _check_pending_evaluation(self, snapshot: dict) -> None:
        """El resultado fijado solo admite una identidad y secuencia válidas."""
        pending = snapshot.get("pending_evaluation")
        if not pending:
            return
        path = "/pending_evaluation"
        if "pending_transaction" in snapshot:
            self.report(
                "PENDING_CONFLICT", path, "No pueden coexistir dos procesos pendientes"
            )
        if pending["prepared_revision"] > snapshot["revision"]:
            self.report("EVALUATION_REVISION", path, "Revisión de preparación futura")
        if pending["evaluation_id"] != f"evaluation_{pending['prepared_revision']:06d}":
            self.report(
                "EVALUATION_ID",
                path,
                "Identidad de evaluación incompatible con su revisión",
            )
        if pending["initiated_revision"] >= pending["prepared_revision"]:
            self.report(
                "EVALUATION_REVISION", path, "El origen debe preceder a la preparación"
            )
        if snapshot["rng"] != pending["fixed"][-1]["rng_after"]:
            self.report(
                "EVALUATION_RNG",
                path,
                "RNG confirmado distinto del resultado preparado",
            )
        if pending["origin"] != (
            "voluntary"
            if pending["source"]["kind"]
            in ("choice_option", "scene_action", "skill_play")
            else "mandatory"
        ):
            self.report(
                "EVALUATION_ORIGIN", path, "Autoridad y procedencia no coinciden"
            )
        if pending["source"]["kind"] in ("node_step", "choice_option"):
            self._pending_node(pending["source"], snapshot)
        elif pending["source"]["kind"] == "scene_action":
            self._pending_scene(pending["source"])
        if snapshot["status"] == "preparing" and (
            pending["source"]["kind"] != "session_start"
            or snapshot.get("preparing_for")
            != self.pkg["manifest"]["entry"].get("node")
        ):
            self.report("EVALUATION_START", path, "Preparación inicial incoherente")
        if "auxiliary_request" in pending:
            ids = {a["request_id"] for a in pending["answers"]}
            if pending["auxiliary_request"]["request_id"] in ids:
                self.report(
                    "EVALUATION_AUXILIARY", path, "Solicitud auxiliar ya respondida"
                )

    def _check_pending(self, snapshot) -> None:
        """Comprueba procedencia estática de una única transacción pendiente."""
        pending = snapshot.get("pending_transaction")
        if not pending:
            return
        self._check_pending_answers(pending, snapshot["revision"])
        source = pending["source"]
        kind = source["kind"]
        if kind in ("node_step", "choice_option"):
            self._pending_node(source, snapshot)
        elif kind == "scene_action":
            self._pending_scene(source)
        elif kind == "skill_play":
            if (
                source["skill_instance"] not in self.instances
                or self.instances[source["skill_instance"]][0] != "skill"
            ):
                self.report(
                    "PENDING_SOURCE",
                    "/pending_transaction/source",
                    "Habilidad inexistente",
                )
        elif kind in ("node_start", "node_end") and source["node"] not in self.nodes:
            self.report(
                "PENDING_SOURCE", "/pending_transaction/source", "Nodo inexistente"
            )
        self.warn(
            "REPLAY_UNVERIFIED",
            "/pending_transaction",
            "Reconstrucción dinámica no comprobada por este validador",
        )

    def _check_pending_answers(self, pending, revision) -> None:
        """Comprueba revisiones, respuestas y referencias de contexto."""
        path = "/pending_transaction"
        if pending["initiated_revision"] > revision:
            self.report(
                "PENDING_REVISION",
                path + "/initiated_revision",
                "Revisión de origen futura",
            )
        answered = [item["request_id"] for item in pending["answers"]]
        if len(answered) != len(set(answered)):
            self.report(
                "DUPLICATE_PENDING_ANSWER", path + "/answers", "Solicitud duplicada"
            )
        if pending["request"]["request_id"] in answered:
            self.report(
                "PENDING_REQUEST_REUSED",
                path + "/request/request_id",
                "Solicitud ya respondida",
            )
        for key, value in pending["context"].items():
            if value not in self.instances:
                self.report(
                    "UNBOUND_CONTEXT",
                    path + "/context/" + key,
                    "Entidad de contexto inexistente",
                )

    def _pending_node(self, source, snapshot) -> None:
        """Comprueba la elección o avance que originó la espera."""
        path = "/pending_transaction/source"
        node = self.nodes.get(source["node"])
        step = (
            next((s for s in node["steps"] if s["id"] == source["step"]), None)
            if node
            else None
        )
        if not step:
            self.report("PENDING_SOURCE", path, "Paso de origen inexistente")
        elif source["kind"] == "choice_option":
            if step["op"] != "choice" or source["option"] not in {
                x["id"] for x in step.get("options", [])
            }:
                self.report("PENDING_SOURCE", path, "Opción de origen inexistente")
            cursor = snapshot.get("cursor")
            if (
                snapshot["status"] != "node"
                or not cursor
                or cursor["node"] != source["node"]
                or cursor["step"] != source["step"]
            ):
                self.report(
                    "PENDING_CURSOR", path, "Cursor no coincide con la elección"
                )

    def _pending_scene(self, source) -> None:
        """Comprueba la propiedad de una acción de escena o de elemento."""
        path = "/pending_transaction/source"
        scene = self.scenes.get(source["scene"])
        if scene is None:
            self.report(
                "PENDING_SOURCE", path + "/scene", "Escena de origen inexistente"
            )
            return
        if "element" in source:
            element = next(
                (x for x in scene.get("elements", []) if x["id"] == source["element"]),
                None,
            )
            if element is None:
                self.report("PENDING_SOURCE", path + "/element", "Elemento inexistente")
                return
            actions = element.get("actions", [])
        else:
            actions = scene.get("actions", [])
        if source["action"] not in {item["id"] for item in actions}:
            self.report(
                "PENDING_SOURCE", path + "/action", "Acción de origen inexistente"
            )

    def validate_act_against_observe(self, act: dict, view: dict) -> list[Diagnostic]:
        """Comprueba una solicitud contra una proyección dada."""
        self.issues = []
        if not self.check_schema("observe", view) or not self.check_schema("act", act):
            return self.issues[:]
        if act["session_id"] != view["session_id"]:
            self.report(
                "SESSION_MISMATCH", "/session_id", "Acción pertenece a otra sesión"
            )
        if act["revision"] != view["revision"]:
            self.report("STALE_PROJECTION", "/revision", "Acción utiliza otra revisión")
        available = [a for a in view["actions"] if a["action_id"] == act["action_id"]]
        if len(available) != 1:
            self.report(
                "ACTION_NOT_OFFERED", "/action_id", "Acción no ofrecida o duplicada"
            )
        elif not available[0]["enabled"]:
            self.report("ACTION_DISABLED", "/action_id", "Acción deshabilitada")
        if act.get("parameters"):
            self.warn(
                "PARAMETERS_UNVERIFIED",
                "/parameters",
                "Observe v1.2 no declara parámetros autorizados: requiere comprobación del ejecutor",
            )
        return self.issues[:]
