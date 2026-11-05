"""Documentation evidence for positive and negative Dodge context matching."""

from gisela.engine.tests.test_npc_contests_v05 import contests, package, run


def test_reference_dodge_matches_only_defender_evasion():
    cases = [
        ("defender", "evasion", 2),
        ("defender", "hit", 0),
        ("actor", "evasion", 0),
    ]
    for role, tag, expected in cases:
        authored = package()
        skill = next(card for card in authored["cards"] if card["id"] == "magic_blast")
        contest = skill["play"]["effects"][1]
        contest["right"]["context"] = {
            "participants": [{"entity": "parnecio", "role": role}],
            "tags": [tag],
        }
        _, _, state = run(pkg=authored)
        assert contests(state)[-1]["right"]["bonus"] == expected
