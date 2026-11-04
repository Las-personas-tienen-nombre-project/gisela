"""Referencias, variables e identidades del borrador de ALBERTO."""

from __future__ import annotations


class WorldError(ValueError):
    """Error de dominio que GISELA transforma en respuesta tipada."""

    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


def find(state: dict, collection: str, identifier: str) -> dict:
    """Exige una instancia explícita de la categoría solicitada."""
    for item in state["world"][collection]:
        if item["id"] == identifier:
            return item
    raise WorldError("INVALID_REFERENCE", f"No existe {identifier} en {collection}")


def instance(state: dict, identifier: str) -> tuple[str, dict]:
    """Resuelve un identificador global sin seleccionar coincidencias implícitas."""
    for collection in ("characters", "objects", "locations", "skills", "effects"):
        for item in state["world"][collection]:
            if item["id"] == identifier:
                return collection, item
    raise WorldError("INVALID_REFERENCE", f"Instancia desconocida: {identifier}")


def var_access(state: dict, ref: dict) -> tuple[dict, str]:
    """Exige que una variable exista y pertenezca al ámbito declarado."""
    scope = ref["scope"]
    if scope == "session":
        variables = state["narrative"]["session_variables"]
    elif scope == "world":
        variables = state["world"]["world_variables"]
    else:
        raise WorldError(
            "UNSUPPORTED_FORMAT", f"Ámbito de variable no disponible: {scope}"
        )
    key = ref["key"]
    if key not in variables:
        raise WorldError("INVALID_REFERENCE", f"Variable no declarada: {scope}.{key}")
    return variables, key


def allocate_id(state: dict, prefix: str, explicit: str | None = None) -> str:
    """Reserva un ID en el borrador sin reutilizar los eliminados."""
    identity = state["identity"]
    used = identity["used_instance_ids"]
    if explicit is not None:
        if explicit in used:
            raise WorldError("INSTANCE_COLLISION", f"ID ya utilizado: {explicit}")
        used.append(explicit)
        return explicit
    number = identity["next_sequence"]
    candidate = f"{prefix}_{number:06d}"
    while candidate in used:
        number += 1
        candidate = f"{prefix}_{number:06d}"
    identity["next_sequence"] = number + 1
    used.append(candidate)
    return candidate
