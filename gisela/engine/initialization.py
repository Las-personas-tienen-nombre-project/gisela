"""Construcción del estado confirmado inicial de una sesión nueva."""

from __future__ import annotations

import copy


def _traits_initial(state: dict, pkg: dict) -> None:
    """Materializa rasgos solo en paquetes que usan formato v1.3 o posterior."""
    if pkg["manifest"]["format_version"] in ("1.3", "1.4", "1.5", "1.6"):
        from .world_traits import materialize

        materialize(state, pkg)


def initial_state(pkg: dict, digest: str, options: dict) -> dict:
    """Crea la instantánea inicial, sin abrir todavía el primer nodo."""
    session_id, seed = options["session_id"], options["seed"]
    initial = pkg["initial_state"]
    groups = ("locations", "characters", "objects", "skills", "effects")
    instance_ids = [item["id"] for name in groups for item in initial[name]]
    world_groups = groups + ("capacities", "relationships")
    state = {
        "schema_version": pkg["manifest"]["format_version"],
        "package_id": pkg["manifest"]["id"],
        "package_digest": digest,
        "session_id": session_id,
        "revision": 0,
        "world_revision": 0,
        "turn": 0,
        "status": "exploring",
        "world_time": initial["world_time"],
        "world": {name: copy.deepcopy(initial.get(name, [])) for name in world_groups},
        "narrative": {
            "session_variables": copy.deepcopy(initial.get("session_variables", {}))
        },
        "history": {"facts": [], "executions": [], "trace": [], "reading": []},
        "rng": {"algorithm": "sha256_counter_v1", "seed": seed, "counter": 0},
        "identity": {"used_instance_ids": instance_ids, "next_sequence": 1},
    }
    _traits_initial(state, pkg)
    if "mary" in pkg:
        from mary import compile_plan, initial_progress

        state["mary"] = initial_progress(compile_plan(pkg["mary"]))
    state["world"]["world_variables"] = copy.deepcopy(
        initial.get("world_variables", {})
    )
    for name in ("current_scene", "player_character"):
        if name in initial:
            state[name] = initial[name]
    for fact in initial.get("facts", []):
        name = fact if isinstance(fact, str) else fact["fact"]
        state["history"]["facts"].append(
            {
                "sequence": len(state["history"]["facts"]) + 1,
                "fact": name,
                "source": "initial_state",
            }
        )
    return state
