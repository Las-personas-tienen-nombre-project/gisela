"""A failure in a dependency must retain its original missing-module name."""

import builtins
import importlib
import unittest
from unittest.mock import patch


class ImportErrorProvenance(unittest.TestCase):
    def test_dependency_error_is_not_masked_by_fallback(self):
        real_import = builtins.__import__

        def fail_jsonschema(name, *args, **kwargs):
            if name == "jsonschema":
                raise ModuleNotFoundError(
                    "No module named 'jsonschema'", name="jsonschema"
                )
            return real_import(name, *args, **kwargs)

        with (
            patch("builtins.__import__", side_effect=fail_jsonschema),
            self.assertRaises(ModuleNotFoundError) as caught,
        ):
            importlib.reload(
                importlib.import_module("gisela.contracts.semantic_shared")
            )
        self.assertEqual(caught.exception.name, "jsonschema")
        importlib.reload(importlib.import_module("gisela.contracts.semantic_shared"))
