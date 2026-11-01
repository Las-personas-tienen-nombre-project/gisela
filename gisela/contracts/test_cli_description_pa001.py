"""PA-001 H7: la ayuda pública no anuncia una versión única obsoleta."""

import contextlib
import io
import unittest

from gisela.contracts.admit_package import cli


class TestAdmissionCliHelp(unittest.TestCase):
    def test_help_does_not_claim_legacy_only(self):
        output = io.StringIO()
        with (
            contextlib.redirect_stdout(output),
            self.assertRaises(SystemExit) as result,
        ):
            cli(["--help"])
        self.assertEqual(result.exception.code, 0)
        self.assertIn("paquetes autorales", output.getvalue())
        self.assertNotIn("contratos v1.2", output.getvalue())
