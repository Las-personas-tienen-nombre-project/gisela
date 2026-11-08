"""El taller 08 debe cerrar el reloj con victoria o derrota reproducibles."""

from pathlib import Path

from gisela.contracts.admit_package import admit_package_file
from gisela.engine.runtime import new_session

PACKAGE = (
    Path(__file__).resolve().parents[3]
    / "docs/workshop/es/08_combate/combate.package.json"
)


def encounter(seed):
    admitted = admit_package_file(PACKAGE)
    session = new_session(admitted, seed=seed * 64)
    for _ in range(40):
        view = session.actuation_observe()
        if not view["active"]:
            return session, view
        choice = "interceptar_01" if view["actor"] == "lara" else None
        result = session.actuation_step(view["revision"], choice)
        assert result["status"] == "ok"
    raise AssertionError("El encuentro no terminó dentro del límite")


def test_lara_wins():
    session, clock = encounter("a")
    assert clock["outcome"] == "lara_detiene_intruso"
    variables = session.export()["narrative"]["session_variables"]
    assert variables["resistencia_intruso"] == 0
    assert variables["resistencia_lara"] > 0


def test_intruder_wins():
    session, clock = encounter("d")
    assert clock["outcome"] == "intruso_escapa"
    variables = session.export()["narrative"]["session_variables"]
    assert variables["resistencia_lara"] == 0
    assert variables["resistencia_intruso"] > 0


def test_reproducible():
    first, _ = encounter("a")
    second, _ = encounter("a")
    assert first.export()["history"]["trace"] == second.export()["history"]["trace"]
    assert (
        first.export()["narrative"]["session_variables"]
        == second.export()["narrative"]["session_variables"]
    )
