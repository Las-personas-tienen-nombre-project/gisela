"""El nuevo conjunto de esquemas no invalida ni sustituye a v1.2."""
from pathlib import Path
import json
import unittest
from jsonschema import Draft202012Validator
from gisela.contracts.semantic_validator import Validator

ROOT = Path(__file__).resolve().parent


class SchemaV13Tests(unittest.TestCase):
    def test_all_thirteen_new_schemas_are_meta_valid(self):
        paths = sorted((ROOT / 'v1_3').glob('*.schema.json'))
        self.assertEqual(len(paths), 13)
        for path in paths:
            with self.subTest(path=path.name):
                Draft202012Validator.check_schema(json.loads(path.read_text()))

    def test_versions_are_distinct_and_supported(self):
        validator = Validator()
        self.assertTrue({'1.2', '1.3'} <= set(validator.schema_versions))
        self.assertEqual(validator.schema_versions['1.2']['package'].schema['$defs']['manifest']['properties']['format_version']['const'], '1.2')
        self.assertEqual(validator.schema_versions['1.3']['package'].schema['$defs']['manifest']['properties']['format_version']['const'], '1.3')
