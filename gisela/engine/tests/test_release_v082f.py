"""Cross-presentation deterministic replay and bounded restore checkpoints."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from gisela.contracts.admit_package import admit_package_file
from gisela.engine.runtime import new_session, restore_session

ROOT = Path(__file__).resolve().parents[3]
VARIANTS = (
    "11_presentacion_participantes_v081.package.json",
    "11_presentacion_decisiones_v081.package.json",
    "11_presentacion_cronica_v081.package.json",
    "12_tablas_v082_parcial.package.json",
    "13_tablas_causal_v082c.package.json",
    "14_presentacion_semantica_v082d.package.json",
)
LOGIC_KEYS = (
    "revision",
    "world_revision",
    "turn",
    "status",
    "world_time",
    "world",
    "narrative",
    "history",
    "rng",
    "actuation",
    "cursor",
)


def _logic(session):
    state = session.export()
    return {key: state[key] for key in LOGIC_KEYS}


def _action(observation):
    valid = [action for action in observation["actions"] if action["enabled"]]
    if not valid:
        return None
    chosen = valid[0]
    return {
        "session_id": observation["session_id"],
        "revision": observation["revision"],
        "action_id": chosen["action_id"],
    }


@pytest.mark.parametrize("seed", ["0" * 64, "f" * 64])
def test_replay_variants_and_restoration_keep_logic_identical(seed):
    folder = ROOT / "packages/tegularis_the_son_of_the_volcan"
    packages = [admit_package_file(folder / name) for name in VARIANTS]
    sessions = [new_session(package, seed=seed) for package in packages]
    baseline = new_session(packages[0], seed=seed)
    for index in range(2):
        observations = [session.observe() for session in sessions]
        frozen = [_logic(session) for session in sessions]
        assert all(state == frozen[0] for state in frozen)
        assert _logic(baseline) == frozen[0]
        assert all(
            observation["actuation"] == observations[0]["actuation"]
            for observation in observations
        )
        assert [_action(observation) for observation in observations] == [
            _action(observations[0])
        ] * len(observations)
        assert frozen == [_logic(session) for session in sessions]
        if index in (1,):
            sessions = [
                restore_session(package, json.loads(json.dumps(session.export())))
                for package, session in zip(packages, sessions)
            ]
            assert [_logic(session) for session in sessions] == frozen
        request = _action(observations[0])
        if request is None:
            break
        for session in (*sessions, baseline):
            assert session.act(copy.deepcopy(request))["status"] == "ok"
    assert all(_logic(session) == _logic(baseline) for session in sessions)


def test_restore_rejects_tampered_snapshot_without_changing_live_session():
    folder = ROOT / "packages/tegularis_the_son_of_the_volcan"
    admitted = admit_package_file(folder / VARIANTS[0])
    session = new_session(admitted, seed="1" * 64)
    original = session.export()
    altered = copy.deepcopy(original)
    altered["package_digest"] = "invalid"
    from gisela.engine.runtime import EngineFailure

    with pytest.raises((EngineFailure, ValueError, KeyError)):
        restore_session(admitted, altered)
    assert session.export() == original


def test_legacy_noncombat_package_public_actions_restore_and_finish():
    admitted = admit_package_file(ROOT / "packages/ejemplo_minimo.package.json")
    session = new_session(admitted, seed="b" * 64)
    first = session.observe()
    assert not first.get("actuation", {}).get("active", False)
    assert session.act(_action(first))["status"] == "ok"
    restored = restore_session(admitted, json.loads(json.dumps(session.export())))
    assert restored.observe() == session.observe()
    for _ in range(8):
        view = session.observe()
        request = _action(view)
        if request is None:
            break
        assert session.act(request)["status"] == "ok"
        assert restored.act(request)["status"] == "ok"
        assert restored.export() == session.export()
    assert session.export() == restored.export()


def _noncombat_presentation():
    return {
        "id": "inspeccion",
        "views": [
            {
                "id": "equipos",
                "component": "table",
                "source": "actuation.effects",
                "columns": [
                    {"id": "beneficiary", "label": "Equipo"},
                    {"id": "remaining", "label": "Pendientes"},
                ],
            },
            {
                "id": "registro",
                "component": "event_log",
                "source": "actuation.causal",
                "kinds": ["event_triggered", "author_message"],
                "limit": 3,
                "event_formats": [
                    {
                        "kind": "event_triggered",
                        "role": "neutral",
                        "template": "Inspección: {event}",
                    },
                    {"kind": "author_message", "role": "neutral", "template": "{text}"},
                ],
            },
        ],
        "regions": [
            {"id": "tabla", "component": "table", "view": "equipos"},
            {"id": "log", "component": "event_log", "view": "registro"},
        ],
    }


def test_noncombat_public_table_event_selection_and_template_rendering():
    from gisela.contracts.presentation_validation import errors
    from gisela.engine.author_presentation import project

    definition = _noncombat_presentation()
    observation = {
        "actuation": {
            "effects": [{"beneficiary": "bomba_1", "remaining": 2}],
            "causal": [
                {
                    "sequence": 1,
                    "kind": "event_triggered",
                    "detail": {"event": "revision"},
                },
                {
                    "sequence": 2,
                    "kind": "author_message",
                    "detail": {"text": "Revisión finalizada"},
                },
            ],
        }
    }
    assert errors(definition) == []
    original = copy.deepcopy(observation)
    projected = project(definition, observation)
    assert projected == project(definition, observation)
    assert observation == original
    table, events = projected["regions"]
    assert table["rows"] == [["bomba_1", "2"]]
    assert [event["display_text"] for event in events["items"]] == [
        "Inspección: revision",
        "Revisión finalizada",
    ]
    assert all(event["semantic_role"] == "neutral" for event in events["items"])
