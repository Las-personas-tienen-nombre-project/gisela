"""DSL 1.6 absolute-time admission, transaction and legacy parity."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gisela.contracts.admit_package import PackageRejected, admit_package
from gisela.engine.runtime import new_session, restore_session

BASE = (
    Path(__file__).resolve().parents[2]
    / "packages/h46b_central_clasificadora.package.json"
)
START = "1998-07-24T19:00:00-04:00"
DEST = "1998-07-24T23:00:00-04:00"


def package(operation, *, version="1.6", start=START):
    story = json.loads(BASE.read_text(encoding="utf-8"))
    story["manifest"]["format_version"] = version
    story["initial_state"]["world_time"] = start
    story["scenes"][0]["actions"].insert(
        0,
        {
            "id": "test_jump",
            "label": {"text": "Test jump"},
            "effects": [operation],
        },
    )
    return story


def execute(story):
    admitted = admit_package(story)
    session = new_session(admitted, session_id="clock", seed="1" * 64)
    initial = session.export()
    action = next(a for a in session.observe()["actions"] if a["id"] == "test_jump")
    result = session.act(
        {"session_id": "clock", "revision": 0, "action_id": action["action_id"]}
    )
    return admitted, session, initial, result


class AbsoluteTimeV16(unittest.TestCase):
    def test_relative_equivalence_including_history_rng_and_observation(self):
        absolute = package({"op": "advance_time_to", "at": DEST})
        relative = package({"op": "advance_time", "minutes": 240})
        a, sa, before, ra = execute(absolute)
        b, sb, _, rb = execute(relative)
        self.assertEqual((ra["status"], rb["status"]), ("ok", "ok"))
        left, right = sa.export(), sb.export()
        self.assertEqual(left["world_time"], DEST)
        self.assertEqual(left["rng"], before["rng"])
        left.pop("package_digest")
        right.pop("package_digest")
        self.assertEqual(left, right)
        self.assertEqual(sa.observe(), sb.observe())
        self.assertEqual(restore_session(a, sa.export()).export(), sa.export())
        self.assertEqual(restore_session(b, sb.export()).export(), sb.export())

    def test_effect_expiration_matches_relative_jump(self):
        from datetime import datetime, timedelta

        from gisela.engine.tests.test_h34a_values import ready, send
        from gisela.engine.tests.test_h34c_effects import (
            chosen,
            grant,
        )
        from gisela.engine.tests.test_h34c_effects import (
            package as effects_package,
        )

        outputs = []
        for absolute in (False, True):
            story = effects_package(
                {"mode": "any", "clauses": [{"after_minutes": 5}]},
                behavior={"expire": [{"op": "record_fact", "fact": "valor_termino"}]},
            )
            story["manifest"]["format_version"] = "1.6"
            start = datetime.fromisoformat(story["initial_state"]["world_time"])
            endpoint = (start + timedelta(minutes=5)).isoformat()
            operation = (
                {"op": "advance_time_to", "at": endpoint}
                if absolute
                else {"op": "advance_time", "minutes": 5}
            )
            story = chosen(story, [grant("valor_01"), operation])
            admitted, session = ready(story)
            self.assertEqual(send(session, "prestar")["status"], "ok")
            snapshot = session.export()
            self.assertEqual(restore_session(admitted, snapshot).export(), snapshot)
            self.assertEqual(
                sum(f["fact"] == "valor_termino" for f in snapshot["history"]["facts"]),
                1,
            )
            self.assertFalse(snapshot["world"]["effects"])
            snapshot.pop("package_digest")
            outputs.append(snapshot)
        self.assertEqual(outputs[0], outputs[1])

    def test_failed_expiration_rolls_back_absolute_jump(self):
        from datetime import datetime, timedelta

        from gisela.engine.tests.test_h34a_values import ready, send
        from gisela.engine.tests.test_h34c_effects import (
            chosen,
            grant,
        )
        from gisela.engine.tests.test_h34c_effects import (
            package as effects_package,
        )

        story = effects_package(
            {"mode": "any", "clauses": [{"after_minutes": 5}]},
            behavior={"expire": [{"op": "remove_instance", "instance": "alberto"}]},
        )
        story["manifest"]["format_version"] = "1.6"
        begin = datetime.fromisoformat(story["initial_state"]["world_time"])
        target = (begin + timedelta(minutes=5)).isoformat()
        story = chosen(
            story, [grant("valor_01"), {"op": "advance_time_to", "at": target}]
        )
        _, session = ready(story)
        previous = session.export()
        self.assertEqual(send(session, "prestar")["status"], "error")
        self.assertEqual(session.export(), previous)

    def test_strictly_future_and_offset_are_enforced_at_runtime(self):
        for target in (START, "1998-07-24T18:59:00-04:00", "1998-07-24T23:00:00-03:00"):
            with self.subTest(at=target):
                _, session, before, result = execute(
                    package(
                        {
                            "op": "advance_time_to",
                            "at": target,
                        }
                    )
                )
                self.assertEqual(result["status"], "error")
                self.assertEqual(session.export(), before)

    def test_subminute_state_is_rejected_without_mutation(self):
        _, session, before, result = execute(
            package(
                {
                    "op": "advance_time_to",
                    "at": DEST,
                },
                start="1998-07-24T19:00:30-04:00",
            )
        )
        self.assertEqual(result["status"], "error")
        self.assertEqual(session.export(), before)

    def test_invalid_calendar_and_noncanonical_timestamps_are_rejected(self):
        for target in (
            "1998-02-30T23:00:00-04:00",
            "1998-07-24T23:00Z",
            "1998-07-24T23:00:01-04:00",
            "1998-07-24T23:00:00",
            "1998-07-24T23:00:00-25:00",
        ):
            with self.subTest(at=target), self.assertRaises(PackageRejected):
                admit_package(package({"op": "advance_time_to", "at": target}))

    def test_extra_fields_and_old_version_reject_new_operation(self):
        for scenario in (
            package({"op": "advance_time_to", "at": DEST, "minutes": 2}),
            package({"op": "advance_time_to", "at": DEST}, version="1.5"),
        ):
            with (
                self.subTest(version=scenario["manifest"]["format_version"]),
                self.assertRaises(PackageRejected),
            ):
                admit_package(scenario)

    def test_original_version_15_is_still_executable(self):
        story = json.loads(BASE.read_text(encoding="utf-8"))
        admitted = admit_package(story)
        session = new_session(admitted)
        self.assertEqual(session.export()["schema_version"], "1.5")
        self.assertEqual(
            restore_session(admitted, session.export()).export(), session.export()
        )

    def test_rollback_previous_fact_on_invalid_time(self):
        story = package({"op": "advance_time_to", "at": START})
        story["scenes"][0]["actions"][0]["effects"].insert(
            0,
            {
                "op": "record_fact",
                "fact": story["manifest"]["facts"][0],
            },
        )
        _, session, before, result = execute(story)
        self.assertEqual(result["status"], "error")
        self.assertEqual(session.export(), before)

    def test_invalid_operation_does_not_persist_rng_or_revision(self):
        story = package({"op": "advance_time_to", "at": START})
        _, session, before, _ = execute(story)
        self.assertEqual(session.export()["revision"], before["revision"])
        self.assertEqual(session.export()["rng"], before["rng"])


if __name__ == "__main__":
    unittest.main()
