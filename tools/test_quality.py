"""Regresiones de la política de tamaño para código mantenido."""

import ast
import tempfile
import unittest
from pathlib import Path

from tools.check_quality import (
    MAX_FILE_LINES,
    MAX_FUNCTION_LINES,
    function_lines,
    function_parameters,
    problems,
)


class QualityGuardTest(unittest.TestCase):
    def test_function_without_docblock(self):
        node = ast.parse("def f():\n    x = 1\n    return x\n").body[0]
        self.assertEqual(function_lines(node), 3)

    def test_docblock_does_not_count(self):
        node = ast.parse(
            'def f():\n    """Primera.\n    Segunda.\n    """\n    return 1\n'
        ).body[0]
        self.assertEqual(function_lines(node), 2)

    def test_rejects_long_function(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "long.py"
            path.write_text("def f():\n" + "    x = 1\n" * MAX_FUNCTION_LINES)
            self.assertIn(
                f"f, {MAX_FUNCTION_LINES + 1} líneas", " ".join(problems(path, root))
            )

    def test_accepts_function_at_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "limit.py"
            path.write_text("def f():\n" + "    x = 1\n" * (MAX_FUNCTION_LINES - 1))
            self.assertEqual(problems(path, root), [])

    def test_three_parameters_are_valid(self):
        """Acepta tres argumentos explícitos en una función normal."""
        node = ast.parse("def f(a, b, c): pass").body[0]
        self.assertEqual(function_parameters(node), 3)

    def test_four_parameters_are_rejected(self):
        """Cuenta parámetros con valores predeterminados y nombrados."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "four.py"
            path.write_text("def f(a, b=1, *, c=2, d=3): pass\n")
            self.assertIn("4 parámetros, máximo 3", " ".join(problems(path, root)))

    def test_receiver_does_not_count_as_explicit_parameter(self):
        """Permite self y cls, que Python entrega implícitamente."""
        node = ast.parse("class C:\n    def f(self, a, b, c): pass\n").body[0].body[0]
        self.assertEqual(function_parameters(node, method=True), 3)

    def test_free_function_named_self_is_not_exempt(self):
        """No permite eludir la regla nombrando self a un argumento."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "free.py"
            path.write_text("def f(self, a, b, c): pass\n")
            self.assertIn("4 parámetros, máximo 3", " ".join(problems(path, root)))

    def test_rejects_long_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "long.txt"
            path.write_text("línea\n" * (MAX_FILE_LINES + 1))
            self.assertIn(
                f"{MAX_FILE_LINES + 1} líneas", " ".join(problems(path, root))
            )

    def test_accepts_file_at_limit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "limit.txt"
            path.write_text("línea\n" * MAX_FILE_LINES)
            self.assertEqual(problems(path, root), [])


if __name__ == "__main__":
    unittest.main()
