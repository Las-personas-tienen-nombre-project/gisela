"""Contrato de independencia del núcleo de condiciones."""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class NarrativeConditionsIndependence(unittest.TestCase):
    def test_independent_imports(self):
        script = (
            "import narrative_conditions\nimport sys\n"
            "unexpected = [name for name in ('gisela', 'dice', 'traits', 'mary') "
            "if name in sys.modules]\n"
            "if unexpected:\n"
            "    raise SystemExit(f'Unexpected imports: {unexpected}')\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
