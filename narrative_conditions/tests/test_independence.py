"""Contrato de independencia del núcleo de condiciones."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class NarrativeConditionsIndependence(unittest.TestCase):
    def test_independent_imports(self):
        script = "import narrative_conditions; import sys; assert 'gisela' not in sys.modules; assert 'dice' not in sys.modules; assert 'traits' not in sys.modules; assert 'mary' not in sys.modules"
        result = subprocess.run([sys.executable, '-c', script], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
