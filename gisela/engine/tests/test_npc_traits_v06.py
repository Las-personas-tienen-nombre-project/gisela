"""v0.6: source-derived traits, source lifecycle, generic contribution expressions."""

import copy
import json
from pathlib import Path

import pytest

from gisela.contracts.admit_package import (
    PackageRejected,
    admit_package,
    admit_package_file,
)
from gisela.engine.conditions import predicate, value
from gisela.engine.runtime import GiselaSession, restore_session
from gisela.engine.tests.test_scripted_npc_skills import advance, character, play_until
from gisela.engine.traits_dice_bridge import contribution_total
from gisela.engine.world_skills import discard_skill
from gisela.engine.world_traits import effective

SOURCE = (
    Path(__file__).resolve().parents[2]
    / "packages"
    / "tegularis_npc_traits_v06.package.json"
)
SEED = "c" * 64


def pkg():
    return json.loads(SOURCE.read_text())


def session(package=None, seed=SEED):
    admitted = (
        admit_package(package) if package is not None else admit_package_file(SOURCE)
    )
    return GiselaSession.new_session(admitted, seed=seed), admitted


def run(marker, package=None, seed=SEED):
    s, a = session(package, seed)
    play_until(s, marker)
    return s, a


def v(s, name):
    return s.export()["narrative"]["session_variables"][name]


def instances(s, card):
    return [x for x in s.export()["world"]["effects"] if x["card"] == card]


def trait_bonus(s, who, tag):
    return contribution_total(
        s.export(),
        {"tags": [tag], "participants": [{"entity": who, "role": "defender"}]},
        s._definitions,
    )


def test_admission_and_passive_source_projection():
    s, _ = session()
    st = s.export()
    assert "dodge" not in character(s, "parnecio").get("traits", [])
    assert "dodge" in effective(st, "parnecio", s._definitions)
    assert predicate(
        st, {"has_trait": {"entity": "parnecio", "trait": "dodge"}}, s._definitions
    )
    assert "magic_redux" in effective(st, "iosepus", s._definitions)
    assert "escamas" in effective(st, "tegularis", s._definitions)
    assert trait_bonus(s, "parnecio", "evasion") == 2
    assert trait_bonus(s, "iosepus", "magic_damage_reduction") == 3
    assert trait_bonus(s, "tegularis", "physical_damage_reduction") == 5


def test_passive_cannot_be_played_or_implicitly_offered():
    s, _ = session()
    assert not any(a.get("id") == "dodge_parnecio_01" for a in s.observe()["actions"])
    view = s.observe()
    snapshot = s.export()
    response = s.act(
        {
            "session_id": view["session_id"],
            "revision": view["revision"],
            "action_id": "play_dodge_parnecio_01",
        }
    )
    assert (
        response["status"] == "error" and response["error"]["code"] == "INVALID_ACTION"
    )
    assert s.export() == snapshot


def test_discard_source_without_erasing_base_traits():
    s, _ = session()
    st = copy.deepcopy(s.export())
    discard_skill(st, {"character": "parnecio", "skill_instance": "dodge_parnecio_01"})
    assert "dodge" not in effective(st, "parnecio", s._definitions)
    assert "enorme" in effective(st, "tegularis", s._definitions)
    assert "escamas" in effective(st, "tegularis", s._definitions)
    # A second source for the same trait keeps it effective once the first leaves.
    st["world"]["characters"][0]["traits"].append("dodge")
    assert effective(st, "parnecio", s._definitions).count("dodge") == 1


def test_dynamic_effect_traits_sofia_and_resource_costs():
    s, _ = run("Parnecio puede ejecutar Slash")
    st = s.export()
    assert v(s, "mana_iosepus") == 30  # 90 -30 -30
    assert v(s, "tp_tegularis") == 58
    assert v(s, "mana_tegularis") == 78
    assert s.scoresheet("tegularis")["stats"][4]["effective"] == 5
    assert "resistente" in effective(st, "parnecio", s._definitions)
    assert "protegido" in effective(st, "tegularis", s._definitions)
    assert len(instances(s, "efecto_protegido")) == 1
    assert trait_bonus(s, "tegularis", "damage_reduction") == 5
    assert trait_bonus(s, "parnecio", "damage_reduction") == 3
    assert "resistente" not in character(s, "parnecio")["traits"]
    assert "protegido" not in character(s, "tegularis")["traits"]


def test_contest_uses_agarraguirre_and_trait_reduction_for_damage():
    # Search only enough deterministic seeds to see a hit; no randomness in fixtures.
    for n in range(30):
        s, _ = run("Tegularis vuelve a utilizar Preponderancia", seed=f"{n:064x}")
        entry = [
            x["detail"]
            for x in s.export()["history"]["trace"]
            if x["kind"] == "contest_resolved"
        ]
        assert len(entry) == 1
        assert entry[0]["right"]["base"] == 10  # (STR15 + effective AWA5) //2
        assert entry[0]["right"]["bonus"] == -5  # Enorme
        if entry[0]["winner"] == "left":
            dice = v(s, "dmg_1")
            assert character(s, "tegularis")["properties"]["heridas"] == max(
                0, 3 * 8 + dice - 5 - 5
            )
            break
    else:
        pytest.fail("No successful deterministic Slash found")


def test_refresh_reuses_same_effect_instance_and_caps_resources():
    s, _ = run("La demostración termina retirando")
    effects = instances(s, "efecto_protegido")
    assert len(effects) == 1
    assert effects[0]["id"] == "protegido_tegularis_01"
    assert v(s, "tp_tegularis") == 60  # min(60,50+8+8)
    assert v(s, "mana_tegularis") == 86
    assert trait_bonus(s, "tegularis", "damage_reduction") == 5


def test_effect_expiration_removes_only_its_granted_trait():
    s, _ = session(seed=SEED)
    for _ in range(40):
        if s.export()["status"] == "ended":
            break
        assert advance(s)["status"] == "ok"
    assert s.export()["status"] == "ended"
    assert s.export()["world"]["effects"] == []
    assert "resistente" not in effective(s.export(), "parnecio", s._definitions)
    assert "dodge" in effective(s.export(), "parnecio", s._definitions)
    assert "protegido" not in effective(s.export(), "tegularis", s._definitions)
    assert "escamas" in effective(s.export(), "tegularis", s._definitions)
    assert s.scoresheet("tegularis")["stats"][4]["effective"] == 7
    assert v(s, "mana_iosepus") == 30


def test_repeatability_and_restore_with_active_sources():
    a, admitted = run("Parnecio puede ejecutar Slash")
    b, _ = run("Parnecio puede ejecutar Slash")
    assert a.export() == b.export()
    restored = restore_session(admitted, a.export())
    assert restored.export() == a.export()
    assert restored.observe() == a.observe()
    assert "resistente" in effective(
        restored.export(), "parnecio", restored._definitions
    )


def test_unknown_passive_or_effect_traits_rejected_at_admission():
    for card_id, field in [
        ("dodge_parnecio", "passive_traits"),
        ("efecto_protegido", "granted_traits"),
    ]:
        p = pkg()
        next(x for x in p["cards"] if x["id"] == card_id)[field] = ["no_existe"]
        with pytest.raises(PackageRejected):
            admit_package(p)


def test_passive_with_executable_effects_rejected():
    p = pkg()
    next(x for x in p["cards"] if x["id"] == "dodge_parnecio")["play"]["effects"] = [
        {"op": "record_fact", "fact": "dodge_presente"}
    ]
    with pytest.raises(PackageRejected):
        admit_package(p)


def test_unknown_trait_total_reference_rejected():
    p = pkg()
    slash = next(x for x in p["cards"] if x["id"] == "slash")
    slash["play"]["effects"][0]["on_win"][1]["value"]["math"]["right"]["math"]["right"][
        "trait_total"
    ]["participants"][0]["entity"] = "desconocido"
    with pytest.raises(PackageRejected):
        admit_package(p)


def test_invalid_trait_sources_conflict_at_effect_application():
    p = pkg()
    trait = p["traits"]["traits"]
    trait.append(
        {
            "id": "incompatible",
            "label": "Incompatible",
            "entity_kinds": ["character"],
            "visibility": "public",
            "excludes": ["dodge"],
            "contributions": [],
        }
    )
    next(c for c in p["cards"] if c["id"] == "efecto_resistente")["granted_traits"] = [
        "incompatible"
    ]
    s, _ = session(p)
    play_until(s, "Iosepus debilita Awareness")
    before = s.export()
    response = advance(s)
    assert response["status"] == "error"
    assert s.export() == before


def test_trait_total_is_generic_and_does_not_advance_rng():
    s, _ = run("Parnecio puede ejecutar Slash")
    st = s.export()
    before = copy.deepcopy(st["rng"])
    assert (
        value(
            st,
            {
                "trait_total": {
                    "tags": ["damage_reduction"],
                    "participants": [{"entity": "tegularis", "role": "defender"}],
                }
            },
            s._definitions,
        )
        == 5
    )
    assert st["rng"] == before


def test_unique_effect_refresh_does_not_repeat_on_apply():
    p = pkg()
    next(c for c in p["cards"] if c["id"] == "efecto_protegido")["on_apply"] = [
        {"op": "record_fact", "fact": "reduccion_temporal"}
    ]
    s, _ = run("La demostración termina retirando", package=p)
    facts = [x["fact"] for x in s.export()["history"]["facts"]]
    assert facts.count("reduccion_temporal") == 1


def test_original_unique_effect_rejects_duplicate():
    p = pkg()
    next(c for c in p["cards"] if c["id"] == "efecto_protegido").pop("on_reapply")
    s, _ = session(p)
    play_until(s, "Tegularis vuelve a utilizar Preponderancia")
    before = s.export()
    r = advance(s)
    assert r["status"] == "error" and r["error"]["code"] == "EFFECT_ALREADY_ACTIVE"
    assert s.export() == before
