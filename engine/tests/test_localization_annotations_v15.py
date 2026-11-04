"""Contratos de localización y anotaciones, compatibles con sesiones v1.5."""

from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from gisela.cli.color import Styler
from gisela.cli.render import show
from gisela.contracts.admit_package import PackageRejected, admit_package
from gisela.contracts.catalogs import assemble_files
from gisela.engine.authorized_gateway import ExecutionGateway, GatewayError, Principal
from gisela.engine.runtime import new_session, restore_session

BASE = Path(__file__).resolve().parents[2] / "packages"


def story():
    pkg = json.loads((BASE / "ejemplo_minimo.package.json").read_text())
    pkg["manifest"]["languages"] = ["es_cl", "en"]
    pkg["strings"] = {
        "es_cl": {"inicio": "¿Cómo te llamái?", "info": "Nota editorial"},
        "en": {"inicio": "What's your name?", "info": "Editorial note"},
    }
    pkg["nodes"][0]["annotations"] = [
        {"audience": "glauquir", "text": {"text_key": "info"}}
    ]
    pkg["nodes"][0]["steps"][0]["text"] = {"text_key": "inicio"}
    pkg["nodes"][0]["steps"][0]["annotations"] = [
        {"audience": "glauquir", "text": {"text": "Solo ayuda al lector."}}
    ]
    return pkg


def scene_story():
    pkg = json.loads((BASE / "h46b_central_clasificadora.package.json").read_text())
    scene = pkg["scenes"][0]
    scene["annotations"] = [
        {"audience": "glauquir", "text": {"text": "Contexto de la Base."}}
    ]
    scene["actions"][0]["annotations"] = [
        {"audience": "glauquir", "text": {"text": "Inspeccione el turno."}}
    ]
    scene["actions"].append(
        {
            "id": "accion_oculta_localizacion",
            "label": {"text": "Oculta"},
            "visible_if": {"constant": False},
            "annotations": [{"audience": "glauquir", "text": {"text": "SECRETO"}}],
        }
    )
    return pkg


class LocalizationAnnotationsV15(TestCase):
    def test_narrative_and_annotation_localization_is_pure(self):
        admitted = admit_package(story())
        session = new_session(admitted, language="en")
        snapshot = session.export()
        self.assertEqual(session.observe()["content"]["text"], "What's your name?")
        self.assertEqual(
            session.observe(language="es_cl")["content"]["text"], "¿Cómo te llamái?"
        )
        self.assertNotIn("annotations", session.observe())
        annotations = session.observe_glauquir()["annotations"]
        self.assertEqual(
            [a["text"] for a in annotations],
            ["Editorial note", "Solo ayuda al lector."],
        )
        self.assertEqual(session.observe_glauquir(), session.observe_glauquir())
        self.assertEqual(snapshot, session.export())
        self.assertEqual(session.read_history()[0]["text"], "What's your name?")
        session.set_language("es_cl")
        self.assertEqual(snapshot, session.export())
        self.assertEqual(session.read_history()[0]["text"], "What's your name?")
        self.assertEqual(
            restore_session(admitted, snapshot, language="en").export(), snapshot
        )

    def test_missing_translation_warns_and_falls_back(self):
        pkg = story()
        del pkg["strings"]["en"]["inicio"]
        admitted = admit_package(pkg)
        self.assertIn("MISSING_TRANSLATION", [d.code for d in admitted.diagnostics])
        self.assertEqual(
            new_session(admitted, language="en").observe()["content"]["text"],
            "¿Cómo te llamái?",
        )

    def test_missing_base_key_and_undeclared_catalog_are_errors(self):
        pkg = story()
        del pkg["strings"]["es_cl"]["inicio"]
        with self.assertRaises(PackageRejected) as raised:
            admit_package(pkg)
        self.assertIn("MISSING_TEXT", [d.code for d in raised.exception.diagnostics])
        pkg = story()
        del pkg["strings"]["en"]
        with self.assertRaises(PackageRejected) as raised:
            admit_package(pkg)
        self.assertIn("MISSING_CATALOG", [d.code for d in raised.exception.diagnostics])
        pkg = story()
        pkg["strings"]["fr"] = {"inicio": "Nom?"}
        with self.assertRaises(PackageRejected) as raised:
            admit_package(pkg)
        self.assertIn(
            "UNDECLARED_LANGUAGE", [d.code for d in raised.exception.diagnostics]
        )

    def test_invalid_audience_or_annotation_shape_rejected(self):
        pkg = story()
        pkg["nodes"][0]["annotations"][0]["audience"] = "renpy"
        with self.assertRaises(PackageRejected):
            admit_package(pkg)
        pkg = story()
        pkg["nodes"][0]["annotations"][0]["effects"] = []
        with self.assertRaises(PackageRejected):
            admit_package(pkg)

    def test_scene_visible_actions_only_and_no_ansi(self):
        session = new_session(admit_package(scene_story()))
        snapshot = session.export()
        self.assertNotIn("annotations", session.observe())
        notes = session.observe_glauquir()["annotations"]
        self.assertEqual([a["scope"] for a in notes], ["scene", "action"])
        self.assertFalse(any("SECRETO" in a["text"] for a in notes))
        buffer = StringIO()
        with redirect_stdout(buffer):
            show(session.observe_glauquir(), styler=Styler("never"))
        self.assertIn("INFORMACIÓN", buffer.getvalue())
        self.assertNotIn("\x1b[", buffer.getvalue())
        self.assertEqual(snapshot, session.export())

    def test_gateway_requires_host_capability(self):
        session = new_session(admit_package(scene_story()))
        ordinary = Principal("renpy", frozenset({"observe_player"}))
        enhanced = Principal(
            "glauquir", frozenset({"observe_player", "observe_glauquir"})
        )
        only_notes = Principal("notes", frozenset({"observe_glauquir"}))
        gateway = ExecutionGateway(
            session, {p.identifier: p for p in (ordinary, enhanced, only_notes)}
        )
        self.assertNotIn("annotations", gateway.bind("renpy").observe())
        with self.assertRaises(GatewayError):
            gateway.bind("renpy").observe_glauquir()
        with self.assertRaises(GatewayError):
            gateway.bind("notes").observe_glauquir()
        self.assertEqual(
            gateway.bind("glauquir").observe_glauquir()["annotations"][0]["scope"],
            "scene",
        )

    def test_gateway_two_views_do_not_share_language_preference(self):
        session = new_session(admit_package(story()))
        left = Principal("left", frozenset({"observe_player"}))
        right = Principal("right", frozenset({"observe_player"}))
        gateway = ExecutionGateway(session, {p.identifier: p for p in (left, right)})
        original = session.export()
        en = gateway.bind("left").observe(language="en")
        es = gateway.bind("right").observe(language="es_cl")
        self.assertEqual(en["content"]["text"], "What's your name?")
        self.assertEqual(es["content"]["text"], "¿Cómo te llamái?")
        self.assertEqual(en["revision"], es["revision"])
        self.assertEqual(session.export(), original)

    def test_two_languages_same_action_and_history(self):
        admitted = admit_package(story())
        es = new_session(admitted, language="es_cl")
        en = restore_session(admitted, es.export(), language="en")
        self.assertEqual(es.observe()["revision"], en.observe()["revision"])
        request = {
            "session_id": es.observe()["session_id"],
            "revision": es.observe()["revision"],
            "action_id": "advance",
        }
        self.assertEqual(es.act(request)["status"], "ok")
        self.assertEqual(en.act(request)["status"], "ok")
        self.assertEqual(es.export()["revision"], en.export()["revision"])
        self.assertEqual(es.export()["rng"], en.export()["rng"])
        self.assertNotEqual(
            es.observe()["content"], en.observe()["content"]
        ) if es.observe()["content"].get("text") else None

    def test_parameter_mismatch_is_rejected(self):
        pkg = story()
        pkg["strings"]["es_cl"]["inicio"] = "Hola, {nombre}"
        pkg["strings"]["en"]["inicio"] = "Hello, {other}"
        with self.assertRaises(PackageRejected) as raised:
            admit_package(pkg)
        self.assertIn(
            "TRANSLATION_PARAMETERS", [d.code for d in raised.exception.diagnostics]
        )

    def test_language_choice_does_not_change_future_action_or_rng(self):
        pkg = story()
        pkg["strings"]["es_cl"]["opcion"] = "Abrir"
        pkg["strings"]["en"]["opcion"] = "Open"
        pkg["nodes"][0]["steps"][1]["options"][0]["label"] = {"text_key": "opcion"}
        admitted = admit_package(pkg)
        es = new_session(admitted, language="es_cl", seed="a" * 64)
        en = new_session(admitted, language="en", seed="a" * 64)
        for choice in ("advance", "choose_abrir"):
            ve, vn = es.observe(), en.observe()
            self.assertEqual(ve["revision"], vn["revision"])
            for session, view in ((es, ve), (en, vn)):
                self.assertEqual(
                    session.act(
                        {
                            "session_id": view["session_id"],
                            "revision": view["revision"],
                            "action_id": choice,
                        }
                    )["status"],
                    "ok",
                )
        self.assertEqual(es.export()["world"], en.export()["world"])
        self.assertEqual(es.export()["rng"], en.export()["rng"])
        self.assertEqual(es.export()["revision"], en.export()["revision"])
        self.assertIn("Abrir", [row["text"] for row in es.read_history()])
        self.assertIn("Open", [row["text"] for row in en.read_history()])

    def test_assembled_catalogs_are_self_contained_and_stable(self):
        pkg = story()
        del pkg["strings"]
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "locales").mkdir()
            source = root / "src.json"
            source.write_text(json.dumps(pkg, ensure_ascii=False))
            for lang, values in story()["strings"].items():
                (root / "locales" / (lang + ".json")).write_text(
                    json.dumps(values, ensure_ascii=False)
                )
            a, b = root / "a.json", root / "b.json"
            digest_a = assemble_files(source, root / "locales", a)
            digest_b = assemble_files(source, root / "locales", b)
            self.assertEqual(digest_a, digest_b)
            self.assertEqual(a.read_bytes(), b.read_bytes())
            self.assertEqual(admit_package(json.loads(a.read_text())).digest, digest_a)
            self.assertEqual(
                new_session(
                    admit_package(json.loads(a.read_text())), language="en"
                ).observe()["content"]["text"],
                "What's your name?",
            )
