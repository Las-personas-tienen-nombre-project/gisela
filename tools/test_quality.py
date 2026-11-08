"""Regresiones de la política de tamaño para código mantenido."""

import ast
import tempfile
import unittest
from pathlib import Path

from tools.check_quality import (
    MAX_FILE_LINES,
    MAX_FUNCTION_LINES,
    check,
    function_lines,
    function_parameters,
    problems,
)


class QualityGuardTest(unittest.TestCase):
    def test_only_history_archive_is_excluded_from_structural_limits(self):
        for folder, archived in (
            ("docs/history", True),
            ("docs/history/workshops/legacy", True),
            ("docs/workshop/es", False),
            ("docs/guides", False),
            ("docs/history_extra", False),
            ("gisela/history", False),
        ):
            with (
                self.subTest(folder=folder),
                tempfile.TemporaryDirectory() as directory,
            ):
                root = Path(directory)
                path = root / folder / "example.py"
                path.parent.mkdir(parents=True)
                source = "def f(a, b, c, d): pass\n" + "# preserved\n" * MAX_FILE_LINES
                path.write_text(source, encoding="utf-8")
                issues = check(root)
                if archived:
                    self.assertEqual(issues, [])
                else:
                    self.assertEqual(len(issues), 2)
                    self.assertIn("4 parámetros, máximo 3", " ".join(issues))
                    self.assertIn("701 líneas, máximo 700", " ".join(issues))
                self.assertEqual(path.read_text(encoding="utf-8"), source)

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

    def test_public_session_factory_exception_is_narrow(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "gisela/engine/runtime.py"
            path.parent.mkdir(parents=True)
            path.write_text(
                "def new_session(a, b, c, d): pass\n"
                "class GiselaSession:\n"
                "    def new_session(cls, a, b, c, d): pass\n"
                "    def other(cls, a, b, c, d): pass\n"
            )
            self.assertEqual(len(problems(path, root)), 1)
            self.assertIn("other, 4 parámetros", problems(path, root)[0])

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
