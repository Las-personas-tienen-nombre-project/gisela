"""Proyección de las misiones visibles. No filtra identificadores ocultos."""

from __future__ import annotations


def public_quests(plan: dict, progress: dict) -> list[dict]:
    """Publica solo títulos, estados y objetivos expresamente visibles."""
    result = []
    for key, mission in sorted(plan["missions"].items()):
        if mission.get("visibility", "hidden") != "public":
            continue
        children = [plan["objectives"][name] for name in mission["objectives"]]
        objectives = [
            {"title": item["title"], "completed": progress["objectives"][item["id"]]}
            for item in children
            if item.get("visibility") == "public"
        ]
        result.append(
            {
                "id": key,
                "title": mission["title"],
                "status": progress["missions"][key],
                "objectives": objectives,
            }
        )
    return result
