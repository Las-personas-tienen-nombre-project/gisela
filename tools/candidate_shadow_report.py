"""Conservative authoring warning for ordered NPC candidate lists.

This does not prove permanent unreachability: a card may move zones or cease
existing during a session. It only identifies matching eligibility predicates
when an earlier candidate has no additional guard.
"""

import argparse
import json
from pathlib import Path


def candidate_shadows(package):
    cards = {card["id"]: card for card in package.get("cards", [])}
    skills = {
        skill["id"]: skill
        for skill in package.get("initial_state", {}).get("skills", [])
    }
    findings = []
    for participant in package.get("actuation", {}).get("participants", []):
        candidates = participant.get("candidates", [])
        for later_index, later in enumerate(candidates):
            if later.get("when"):
                continue  # A guard may make eligibility incomparable.
            later_skill = skills.get(later.get("skill_instance"), {})
            later_card = cards.get(later_skill.get("card"), {})
            if not later_card or later_skill.get("zone") != "hand":
                continue
            for earlier_index, earlier in enumerate(candidates[:later_index]):
                if earlier.get("when"):
                    continue
                earlier_skill = skills.get(earlier.get("skill_instance"), {})
                earlier_card = cards.get(earlier_skill.get("card"), {})
                if earlier_skill.get("zone") != "hand" or not earlier_card:
                    continue
                if earlier_card.get("play", {}).get("requires") != later_card.get(
                    "play", {}
                ).get("requires"):
                    continue
                if earlier.get("arguments", {}) != later.get("arguments", {}):
                    continue
                findings.append(
                    {
                        "code": "POTENTIAL_CANDIDATE_SHADOW",
                        "participant": participant.get("character"),
                        "earlier": earlier["skill_instance"],
                        "later": later["skill_instance"],
                        "earlier_position": earlier_index + 1,
                        "later_position": later_index + 1,
                    }
                )
                break
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    package = json.loads(args.package.read_text(encoding="utf-8"))
    findings = candidate_shadows(package)
    print(json.dumps(findings, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
