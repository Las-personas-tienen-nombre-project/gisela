"""Auditoría de lectura: la salida no altera datos autoritativos."""

import copy
import json
from pathlib import Path

from gisela.cli.render import show_presentation
from gisela.contracts.admit_package import admit_package
from gisela.engine.runtime import new_session

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "packages/tegularis_the_son_of_the_volcan"


def test_reader_hints_and_no_mutation(capsys):
    path = PACKAGE / "11_presentacion_participantes_v081.package.json"
    admitted = admit_package(json.loads(path.read_text(encoding="utf-8")))
    session = new_session(admitted, seed="0" * 64)
    view = session.observe_glauquir()
    before = copy.deepcopy(session.export())
    show_presentation(view["presentation"])
    text = capsys.readouterr().out
    assert "ORDEN DE ACTUACIÓN" in text
    assert "TIRADAS DE INICIATIVA" in text
    assert "Elija una letra o escriba: accion <id>" in text
    assert "Últimos 10 de" in text
    assert "Pendiente de confirmación" in text
    assert session.export() == before


def test_layouts_share_identical_rules():
    files = sorted(PACKAGE.glob("11_presentacion_*_v081.package.json"))
    bodies = []
    for path in files:
        package = json.loads(path.read_text(encoding="utf-8"))
        package.pop("presentation")
        bodies.append(package)
    assert len(files) == 3
    assert bodies[0] == bodies[1] == bodies[2]
