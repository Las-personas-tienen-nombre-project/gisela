"""E0-C: las respuestas de error existentes cumplen los esquemas públicos."""

import re
import unittest
from pathlib import Path

from gisela.contracts.semantic_validator import Validator
from gisela.engine.tests.test_h34a_values import PROP, load, op, ready, rule, send

ROOT = Path(__file__).resolve().parents[2]


class ErrorContractDrift(unittest.TestCase):
    def test_e0_c01_all_declared_world_errors_are_contractual(self):
        sources = (ROOT / "engine").glob("*.py")
        codes = set()
        for path in sources:
            codes.update(re.findall(r"WorldError\('([A-Z_]+)'", path.read_text()))
        for version in ("1.2", "1.3"):
            validator = Validator()
            validator.use_version(version)
            schema = validator.schemas["result"].schema
            allowed = schema["oneOf"][1]["properties"]["error"]["properties"]["code"][
                "enum"
            ]
            self.assertFalse(
                codes - set(allowed), (version, sorted(codes - set(allowed)))
            )

    def test_e0_c02_domain_error_is_valid_public_result(self):
        pkg = load()
        for identifier in ("confianza_2", "confianza_3"):
            rule(pkg, identifier, [op("add", PROP, {"literal": 5})])
        _, session = ready(pkg)
        result = send(session, "prestar")
        self.assertEqual(result["error"]["code"], "PROPERTY_RANGE")
        validator = Validator()
        self.assertTrue(validator.check_schema("result", result))

    def test_e0_c03_access_error_valid_under_v12(self):
        _, session = ready()
        validator = Validator()
        view = session.observe()
        response = session.act(
            {
                "session_id": view["session_id"],
                "revision": view["revision"],
                "action_id": "inventado",
            }
        )
        self.assertEqual(response["status"], "error")
        self.assertTrue(validator.check_schema("result", response))
