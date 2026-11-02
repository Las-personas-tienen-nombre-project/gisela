"""Color narrativo y disposición privada con acciones confirmadas."""

import unittest
from pathlib import Path

from gisela.contracts.admit_package import admit_package, admit_package_file
from gisela.engine.presentation import disposition
from gisela.engine.runtime import new_session, restore_session

PACKAGE = (
    Path(__file__).resolve().parents[2]
    / "packages/h46b_central_clasificadora.package.json"
)


def fixture():
    package = admit_package_file(PACKAGE).materialize()
    package["manifest"]["relationship_fields"].append(
        {"id": "affinity_score", "type": "integer", "initial": 0}
    )
    package["manifest"]["disposition_display"] = {
        "field": "affinity_score",
        "minimum": -10,
        "neutral": 0,
        "maximum": 10,
    }
    card = next(c for c in package["cards"] if c["id"] == "araya")
    card["presentation"] = {"color": "blue"}
    card["properties"] = [
        {"id": "presentation_color", "type": "string", "initial": "inherit"}
    ]
    scene = package["scenes"][0]
    scene["actors"][0]["presentation"] = {"color": "yellow"}
    scene["actors"][0]["public_id"] = "guardia_turno"
    for name, value in (("color_red", "red"), ("color_inherit", "inherit")):
        scene["actions"].append(
            {
                "id": name,
                "label": {"text": name},
                "effects": [
                    {
                        "op": "set",
                        "target": {
                            "property": {"entity": "araya", "key": "presentation_color"}
                        },
                        "value": {"literal": value},
                    }
                ],
            }
        )
    return admit_package(package)


def take(session, identifier):
    view = session.observe()
    action = next(a for a in view["actions"] if a["id"] == identifier)
    result = session.act(
        {
            "session_id": view["session_id"],
            "revision": view["revision"],
            "action_id": action["action_id"],
        }
    )
    if result["status"] != "ok":
        raise RuntimeError(str(result))


class PresentationColorTest(unittest.TestCase):
    def test_object_color_changes_only_one_instance(self):
        package = admit_package_file(PACKAGE).materialize()
        card = next(c for c in package["cards"] if c["id"] == "casete")
        card["presentation"] = {"color": "blue"}
        card["properties"] = [
            {"id": "presentation_color", "type": "string", "initial": "inherit"}
        ]
        package["initial_state"]["objects"].append(
            {"id": "casete_otro", "card": "casete", "location": "porteria"}
        )
        scene = package["scenes"][0]
        scene["elements"].extend(
            [
                {
                    "id": "casete_visible",
                    "label": {"text": "Casete"},
                    "entity": "casete_copia",
                },
                {
                    "id": "otro_visible",
                    "label": {"text": "Otro casete"},
                    "entity": "casete_otro",
                },
            ]
        )
        scene["actions"].append(
            {
                "id": "tintar",
                "label": {"text": "Tintar"},
                "effects": [
                    {
                        "op": "set",
                        "target": {
                            "property": {
                                "entity": "casete_copia",
                                "key": "presentation_color",
                            }
                        },
                        "value": {"literal": "red"},
                    }
                ],
            }
        )
        session = new_session(admit_package(package))
        self.assertEqual(
            [e["color"] for e in session.observe()["elements"]], ["blue", "blue"]
        )
        take(session, "tintar")
        self.assertEqual(
            [e["color"] for e in session.observe()["elements"]], ["red", "blue"]
        )

    def test_public_action_alias_keeps_act_authorization(self):
        package = fixture().materialize()
        action = package["scenes"][0]["actions"][-2]
        action["public_id"] = "cambiar_color"
        session = new_session(admit_package(package))
        self.assertNotIn(action["id"], [a["id"] for a in session.observe()["actions"]])
        take(session, "cambiar_color")
        self.assertEqual(session.observe()["actors"][0]["color"], "red")

    def test_exact_category_boundaries(self):
        session = new_session(fixture())
        for value, category in (
            (-10, "hostile"),
            (-6, "unfriendly"),
            (-2, "neutral"),
            (0, "neutral"),
            (2, "neutral"),
            (6, "friendly"),
            (10, "very_friendly"),
        ):
            with self.subTest(value=value):
                session._state["world"]["relationships"] = [
                    {
                        "from": "araya",
                        "to": "alberto",
                        "key": "affinity_score",
                        "value": value,
                    }
                ]
                self.assertEqual(disposition(session, "araya")["category"], category)

    def test_asymmetric_and_zero_to_ten_scales(self):
        for minimum, neutral, maximum, value, expected in (
            (0, 5, 10, 5, 0),
            (0, 5, 10, 0, -100),
            (-100, 0, 100, 60, 60),
            (-2, 0, 8, 4, 50),
        ):
            with self.subTest(scale=(minimum, neutral, maximum), value=value):
                package = fixture().materialize()
                config = package["manifest"]["disposition_display"]
                config.update(minimum=minimum, neutral=neutral, maximum=maximum)
                session = new_session(admit_package(package))
                session._state["world"]["relationships"] = [
                    {
                        "from": "araya",
                        "to": "alberto",
                        "key": "affinity_score",
                        "value": value,
                    }
                ]
                self.assertEqual(disposition(session, "araya")["normalized"], expected)

    def test_action_restore_inherit_and_diagnostic(self):
        admitted = fixture()
        session = new_session(admitted)
        actor = session.observe()["actors"][0]
        self.assertEqual((actor["id"], actor["color"]), ("guardia_turno", "yellow"))
        self.assertNotIn("affinity_score", str(session.observe()))
        diagnostic = session.debug_query(
            {"kind": "disposition", "actor": "guardia_turno"}
        )
        self.assertEqual(
            (diagnostic["value"], diagnostic["category"], diagnostic["color_source"]),
            (0, "neutral", "scene"),
        )
        take(session, "color_red")
        restored = restore_session(admitted, session.export())
        self.assertEqual(restored.observe(), session.observe())
        self.assertEqual(restored.observe()["actors"][0]["color"], "red")
        take(restored, "color_inherit")
        self.assertEqual(restored.observe()["actors"][0]["color"], "yellow")
        self.assertNotIn("araya", str(restored.observe()["actors"]))

    def test_bad_scale_is_rejected(self):
        package = fixture().materialize()
        package["manifest"]["disposition_display"]["neutral"] = 10
        from gisela.contracts.admit_package import PackageRejected

        with self.assertRaises(PackageRejected):
            admit_package(package)


if __name__ == "__main__":
    unittest.main()
