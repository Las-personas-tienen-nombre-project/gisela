"""Private campaign diagnostics derived only from confirmed snapshots.

Never inspected by the player Observe interface. A non-observed skill is not
reported as unreachable: coverage only describes the sampled campaign.
"""

from collections import Counter


def confirmed_delta(before, after):
    """Count only events appended by a successfully committed action."""
    trace_before = before.get("history", {}).get("trace", [])
    trace_after = after.get("history", {}).get("trace", [])
    clock_before = before.get("actuation") or {}
    clock_after = after.get("actuation") or {}
    events_before = clock_before.get("events", [])
    events_after = clock_after.get("events", [])
    if trace_after[: len(trace_before)] != trace_before:
        raise ValueError("El historial de trazas no conserva el prefijo confirmado")
    if events_after[: len(events_before)] != events_before:
        raise ValueError("El historial de actuación no conserva el prefijo confirmado")
    skills = Counter(
        item["source"]
        for item in trace_after[len(trace_before) :]
        if item.get("kind") == "skill_played"
    )
    effects = Counter(
        item["detail"].get("effect")
        for item in events_after[len(events_before) :]
        if item.get("kind") in ("effect_started", "effect_refreshed")
        and item.get("detail", {}).get("effect") is not None
    )
    return {
        "skills_played": dict(sorted(skills.items())),
        "effects_applied_or_refreshed": dict(sorted(effects.items())),
    }


def merge_coverage(destination, delta):
    """Combine committed event counts; never mutate incoming event records."""
    for key in ("skills_played", "effects_applied_or_refreshed"):
        count = Counter(destination.get(key, {}))
        count.update(delta[key])
        destination[key] = dict(sorted(count.items()))


def summarize_decisions(decisions):
    reasons = Counter()
    chosen = Counter()
    for decision in decisions:
        if decision["selected"] is not None:
            chosen[decision["selected"]] += 1
        for candidate in decision["candidates"]:
            reasons[candidate["reason"]] += 1
    return {
        "selected": dict(sorted(chosen.items())),
        "candidate_reasons": dict(sorted(reasons.items())),
    }
