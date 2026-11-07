"""Private, opt-in diagnostic capture for author tooling only.

The capture never enters the snapshot, public Observe, or an execution receipt.
A ContextVar isolates simultaneous sessions and nested diagnostic scopes.
"""

from contextlib import contextmanager
from contextvars import ContextVar

_COLLECTOR = ContextVar("gisela_candidate_diagnostics", default=None)


@contextmanager
def capture():
    """Collect candidate decisions during a synchronous session operation."""
    records = []
    token = _COLLECTOR.set(records)
    try:
        yield records
    finally:
        _COLLECTOR.reset(token)


def record(actor, selection, assessments):
    """Called by the selection algorithm; never evaluates a condition twice."""
    sink = _COLLECTOR.get()
    if sink is None:
        return
    candidates, selected = selection
    items = [
        {
            "skill_instance": candidate["skill_instance"],
            "reason": assessments[index]
            if index < len(assessments)
            else "not_evaluated",
        }
        for index, candidate in enumerate(candidates)
    ]
    sink.append({"actor": actor, "selected": selected, "candidates": items})
