"""Ejecución aislada por sesión y contexto reproducible de una semilla."""

from __future__ import annotations

from dataclasses import dataclass, field

from campaign_diagnostics import confirmed_delta, merge_coverage, summarize_decisions

from gisela.contracts.admit_package import AdmittedPackage
from gisela.engine.candidate_diagnostics import capture as capture_candidates
from gisela.engine.runtime import new_session, restore_session

MAX_ACTIONS = 600
FATAL_ERRORS = (OSError, ImportError, MemoryError)


class CampaignError(RuntimeError):
    """Invariante técnica de la campaña incumplida, ajena al desenlace."""


def choose(view, strategy):
    actions = [x for x in view["actions"] if x["enabled"]]
    if not actions:
        raise CampaignError("Sin acciones antes del desenlace")
    if view["actuation"]["actor"] == "parnecio":
        if strategy == "pass":
            return next((x for x in actions if x["id"] == "pasar"), actions[0])
        if strategy == "shield":
            return next(
                (x for x in actions if x["id"].startswith("proteccion_")), actions[0]
            )
        for prefix in ("blai", "double_slash", "slash"):
            selected = next((x for x in actions if x["id"].startswith(prefix)), None)
            if selected is not None:
                return selected
    return actions[0]


@dataclass
class SeedRun:
    """Solo conserva datos de esta semilla; export() siempre entrega una copia."""

    admitted: AdmittedPackage
    seed: str
    strategy: str
    max_actions: int = MAX_ACTIONS
    diagnostics: bool = False
    coverage: dict = field(default_factory=dict)
    decisions: list = field(default_factory=list)
    phase: str = "initialize"
    actions: int = 0
    initial_turn: int | None = None
    snapshot: dict | None = None
    view: dict = field(default_factory=dict)
    request: dict | None = None
    response: dict | None = None

    def capture(self, session, phase):
        """El snapshot antecede a la operación; no se exporta al manejar el error."""
        self.phase = "export"
        self.snapshot = session.export()
        self.phase = phase
        self.request = self.response = None

    def act(self, session):
        """Conserva el rechazo completo y utiliza la misma comprobación en replay."""
        self.phase = "act"
        if not self.diagnostics:
            self.response = session.act(self.request)
        else:
            before = session.export()
            with capture_candidates() as decisions:
                self.response = session.act(self.request)
            if self.response["status"] == "ok":
                after = session.export()
                merge_coverage(self.coverage, confirmed_delta(before, after))
                self.decisions.extend(decisions)
        if self.response["status"] != "ok":
            raise CampaignError(f"Acción rechazada en paso {self.actions}")

    def verify_restore(self, session):
        """Comprobaciones explícitas, activas también al ejecutar Python con -O."""
        self.capture(session, "restore")
        restored = restore_session(self.admitted, self.snapshot)
        if session.observe() != restored.observe():
            raise CampaignError("Observe difiere después de restaurar")
        if self.snapshot != restored.export():
            raise CampaignError("Snapshot difiere después de restaurar")
        return restored

    def result(self):
        self.phase = "validate_end"
        if self.snapshot["turn"] != self.initial_turn:
            raise CampaignError("El encuentro modificó el turno narrativo")
        result = {
            "type": "seed",
            "status": "success",
            "seed": self.seed,
            "strategy": self.strategy,
            "outcome": self.view["actuation"]["outcome"],
            "actions": self.actions,
            "round": self.view["actuation"]["round"],
            "causal": len(self.snapshot["history"]["trace"]),
        }
        if self.diagnostics:
            result["coverage"] = self.coverage
            result["decision_counts"] = summarize_decisions(self.decisions)
            result["decisions"] = self.decisions
        return result

    def execute(self):
        """Crea una sesión independiente y acepta cualquier desenlace válido."""
        session = new_session(self.admitted, seed=self.seed)
        self.capture(session, "observe")
        self.initial_turn = self.snapshot["turn"]
        while True:
            self.capture(session, "observe")
            self.view = session.observe()
            if self.view["status"] == "ended":
                return self.result()
            self.phase = "limit"
            if self.actions >= self.max_actions:
                raise CampaignError(
                    f"Partida no terminó en {self.max_actions} acciones"
                )
            self.phase = "choose"
            action = choose(self.view, self.strategy)
            self.capture(session, "act")
            self.request = {
                "session_id": self.view["session_id"],
                "revision": self.view["revision"],
                "action_id": action["action_id"],
            }
            self.act(session)
            self.actions += 1
            if self.actions in (13, 37):
                session = self.verify_restore(session)


def run(admitted, seed, strategy):
    """Compatibilidad para los llamantes de la herramienta original."""
    return SeedRun(admitted, seed, strategy).execute()
