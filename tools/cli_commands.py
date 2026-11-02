"""Comandos de consola para desarrollo y depuración, sin lógica de juego."""

from __future__ import annotations

import json

from gisela.engine.world_base import WorldError


def _query_words(words: list[str]) -> dict:
    """Traduce comandos explícitos a consultas tipadas del motor."""
    formats = {
        "personaje": ("character", "character"),
        "entidad": ("entity", "entity"),
        "propiedad": ("property", "entity", "key"),
        "relacion": ("relationship", "from", "to", "key"),
        "scoresheet": ("scoresheet", "character"),
        "hechos": ("facts",),
    }
    fields = formats.get(words[0]) if words else None
    if fields is None or len(words) != len(fields):
        raise WorldError(
            "INVALID_QUERY",
            "Consulta: personaje ID, entidad ID, propiedad ENTIDAD CAMPO, "
            "relacion ORIGEN DESTINO CAMPO, scoresheet ID o hechos",
        )
    return {"kind": fields[0], **dict(zip(fields[1:], words[1:]))}


def inspect(session, words: list[str]) -> None:
    """Imprime una consulta del motor solo en modo de desarrollo."""
    try:
        answer = session.debug_query(_query_words(words))
        print(json.dumps(answer, ensure_ascii=False, indent=2, default=str))
    except (WorldError, ValueError, KeyError, TypeError) as exc:
        print("Consulta rechazada: " + str(exc))


def instructions() -> None:
    """Muestra los comandos disponibles sin atribuirles autoridad narrativa."""
    print(
        "GLAUQUIR: comandos mirar, mirar ELEMENTO, acciones, examinar OBJETO, ficha CARTA, inventario,"
    )
    print("cartas, habilidades, estado, hablar PERSONA, ir LUGAR, dar OBJETO,")
    print("tomar OBJETO, dejar OBJETO, usar OBJETO, jugar HABILIDAD.")
    print(
        "También: misiones, history [N|all], guardar RUTA, cargar RUTA, ayuda, salir."
    )
    print("Para ejecutar una oferta específica: accion ID (consulte acciones).")
    print(
        "Con --developer: consultar personaje ID, entidad ID, propiedad ENTIDAD CAMPO,"
    )
    print("relacion ORIGEN DESTINO CAMPO, scoresheet ID, hechos.")
