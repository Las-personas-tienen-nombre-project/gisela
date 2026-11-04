"""Frontera de ejecución optativa, neutral al tipo de solicitante.

El anfitrión autentica a sus clientes y conserva este gateway privado. El
identificador de principal NO se toma de Act ni constituye autenticación.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass

from .action_handler import act as execute_act
from .runtime import GiselaSession

_ALLOWED = frozenset(
    {"act", "observe_player", "export_private", "debug_private", "observe_glauquir"}
)
_ID = re.compile(r"^[a-z][a-z0-9_.-]{0,95}$")


class GatewayError(ValueError):
    """Configuración, persistencia o frontera de confianza inválida."""


@dataclass(frozen=True)
class Principal:
    """Identidad y capacidades otorgadas por un anfitrión confiable."""

    identifier: str
    capabilities: frozenset[str]

    def __post_init__(self):
        if not isinstance(self.identifier, str) or not _ID.fullmatch(self.identifier):
            raise GatewayError("Identificador de principal inválido")
        if (
            not isinstance(self.capabilities, frozenset)
            or not self.capabilities <= _ALLOWED
        ):
            raise GatewayError("Capacidades desconocidas")


def _digest_request(request: dict) -> str:
    """Vincula un command_id a su contenido, sin depender del orden JSON."""
    encoded = json.dumps(
        request, sort_keys=True, separators=(",", ":"), allow_nan=False
    )
    if len(encoded) > 65536:
        raise GatewayError("Comando excede el presupuesto")
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class BoundClient:
    """Fachada de una identidad previamente autenticada por el anfitrión."""

    def __init__(self, gateway, principal: Principal):
        self._gateway = gateway
        self._principal = principal

    def observe(self, language: str | None = None) -> dict:
        return self._gateway._observe(self._principal, language)

    def observe_glauquir(self, language: str | None = None) -> dict:
        return self._gateway._observe_glauquir(self._principal, language)

    def act(self, request: dict, command_id: str) -> dict:
        return self._gateway._act(self._principal, request, command_id)

    def export(self) -> dict:
        return self._gateway._export(self._principal)

    def debug_query(self, request: dict) -> dict:
        return self._gateway._debug_query(self._principal, request)


class ExecutionGateway:
    """Un único escritor por sesión y recibos opcionalmente durables."""

    def __init__(self, session: GiselaSession, principals: dict, store=None):
        if session._gateway_attached:
            raise GatewayError("La sesión ya tiene gateway")
        self._lock = session._lock
        self._principals = dict(principals)
        if not self._principals or any(
            name != item.identifier or not isinstance(item, Principal)
            for name, item in self._principals.items()
        ):
            raise GatewayError("Registro de principales inválido")
        self._store = store
        self._receipts = {}
        self._uncertain = False
        self._session = session
        if store is not None:
            store.claim()
            try:
                self._load_or_initialize(session)
            except Exception:
                store.release()
                raise
        session._gateway_attached = True
        self._session._gateway_attached = True

    def _load_or_initialize(self, session: GiselaSession) -> None:
        checkpoint = self._store.load()
        if checkpoint is None:
            self._store.save(self._checkpoint(session._state, {}))
            return
        if (
            not isinstance(checkpoint, dict)
            or checkpoint.get("format") != "gisela.gateway.v1"
            or checkpoint.get("session_id") != session._state["session_id"]
            or checkpoint.get("package_digest") != session._admitted.digest
            or not isinstance(checkpoint.get("state"), dict)
            or checkpoint["state"].get("session_id") != session._state["session_id"]
            or not isinstance(checkpoint.get("receipts"), dict)
        ):
            raise GatewayError("Checkpoint no corresponde a esta sesión y paquete")
        from .runtime import restore_session

        self._session = restore_session(
            session._admitted, checkpoint["state"], language=session._language
        )
        self._validate_receipts(checkpoint["receipts"], checkpoint["state"]["revision"])
        self._receipts = copy.deepcopy(checkpoint["receipts"])

    def _validate_receipts(self, receipts: dict, revision: int) -> None:
        """Rechaza recibos incompletos y presupuestos corruptos al restaurar."""
        if len(receipts) > 10000:
            raise GatewayError("Checkpoint excede máximo de recibos")
        for key, record in receipts.items():
            if (
                not isinstance(key, str)
                or key.count(":") != 1
                or any(not _ID.fullmatch(part) for part in key.split(":"))
                or not isinstance(record, dict)
                or not isinstance(record.get("fingerprint"), str)
                or not re.fullmatch(r"[0-9a-f]{64}", record["fingerprint"])
                or not isinstance(record.get("response"), dict)
                or record["response"].get("status") not in ("ok", "error")
                or type(record["response"].get("revision")) is not int
                or not 0 <= record["response"]["revision"] <= revision
            ):
                raise GatewayError("Recibo de comando corrupto")

    def _checkpoint(self, state: dict, receipts: dict) -> dict:
        return {
            "format": "gisela.gateway.v1",
            "session_id": state["session_id"],
            "package_digest": state["package_digest"],
            "state": copy.deepcopy(state),
            "receipts": copy.deepcopy(receipts),
        }

    def bind(self, principal_id: str) -> BoundClient:
        """Solo el anfitrión autenticado debe invocar esta operación."""
        if principal_id not in self._principals:
            raise GatewayError("Principal no registrado")
        return BoundClient(self, self._principals[principal_id])

    def _permit(self, principal: Principal, capability: str) -> None:
        if self._uncertain:
            raise GatewayError("Persistencia incierta; restaurar desde checkpoint")
        if self._principals.get(principal.identifier) != principal:
            raise GatewayError("Identidad revocada o capacidades modificadas")
        if capability not in principal.capabilities:
            raise GatewayError("Permiso denegado")

    def _observe(self, principal: Principal, language: str | None = None) -> dict:
        with self._lock:
            self._permit(principal, "observe_player")
            return copy.deepcopy(self._session.observe(language))

    def _observe_glauquir(
        self, principal: Principal, language: str | None = None
    ) -> dict:
        with self._lock:
            self._permit(principal, "observe_player")
            self._permit(principal, "observe_glauquir")
            return copy.deepcopy(self._session.observe_glauquir(language))

    def _export(self, principal: Principal) -> dict:
        with self._lock:
            self._permit(principal, "export_private")
            return self._session.export()

    def _debug_query(self, principal: Principal, request: dict) -> dict:
        with self._lock:
            self._permit(principal, "debug_private")
            return copy.deepcopy(self._session.debug_query(request))

    def _act(self, principal: Principal, request: dict, command_id: str) -> dict:
        with self._lock:
            self._permit(principal, "act")
            if not isinstance(command_id, str) or not _ID.fullmatch(command_id):
                raise GatewayError("command_id inválido")
            if not isinstance(request, dict):
                raise GatewayError("Act debe ser objeto JSON")
            fingerprint = _digest_request(request)
            key = principal.identifier + ":" + command_id
            if key in self._receipts:
                receipt = self._receipts[key]
                if receipt["fingerprint"] != fingerprint:
                    raise GatewayError("command_id reutilizado con otra solicitud")
                previous = copy.deepcopy(receipt["response"])
                return (
                    _redact(previous)
                    if "observe_player" not in principal.capabilities
                    else previous
                )
            if len(self._receipts) >= 10000:
                raise GatewayError("Límite de recibos; cierre y archive la sesión")
            current = self._session._state
            response = execute_act(self._session, request)
            if response["status"] == "error":
                response = _safe_error(response)
            if "observe_player" not in principal.capabilities:
                response = _redact(response)
            self._persist_receipt(
                key, {"fingerprint": fingerprint, "response": response}, current
            )
            return copy.deepcopy(response)

    def _persist_receipt(self, key: str, receipt: dict, previous: dict) -> None:
        """Persiste estado y comprobante juntos; falla cerrado ante ambigüedad."""
        updated = dict(self._receipts)
        updated[key] = copy.deepcopy(receipt)
        if self._store is not None:
            try:
                self._store.save(self._checkpoint(self._session._state, updated))
            except Exception as exc:
                if getattr(exc, "uncertain", False):
                    self._uncertain = True
                else:
                    self._session._state = previous
                raise GatewayError("No se pudo confirmar el checkpoint") from exc
        self._receipts = updated

    def close(self) -> None:
        """Libera el bloqueo de almacenamiento y deja inutilizable el gateway."""
        with self._lock:
            self._uncertain = True
            if self._store is not None:
                self._store.release()


def _safe_error(response: dict) -> dict:
    """No publica mensajes internos ni referencias del mundo en clientes externos."""
    safe = copy.deepcopy(response)
    safe["error"]["message"] = "Operación rechazada"
    safe["error"].pop("detail", None)
    return safe


def _redact(response: dict) -> dict:
    """Un escritor sin permiso de lectura no recibe proyección ni detalles."""
    result = {
        key: value for key, value in response.items() if key not in ("view", "error")
    }
    if response["status"] == "error":
        result["error"] = {
            "code": response["error"]["code"],
            "message": "Operación rechazada",
        }
    return result
