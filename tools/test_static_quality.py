"""Regresiones de la política estática y su integración en el kit."""

from __future__ import annotations

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools import check_gisela
from tools import check_static_quality as quality


class RuffPolicyTest(unittest.TestCase):
    def test_lint_and_format_boundaries(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.py"
            config = quality.ROOT / "pyproject.toml"
            path.write_text("value = 1\n")
            self.assertEqual(self._ruff("check", config, path), 0)
            self.assertEqual(self._ruff("format", config, path), 0)
            path.write_text("print(undefined_name)\n")
            self.assertNotEqual(self._ruff("check", config, path), 0)
            path.write_text("value=1\n")
            self.assertNotEqual(self._ruff("format", config, path), 0)

    def _ruff(self, mode: str, config: Path, path: Path) -> int:
        args = [sys.executable, "-m", "ruff", mode, "--config", str(config)]
        if mode == "format":
            args.append("--check")
        return subprocess.run(
            [*args, str(path)], capture_output=True, check=False
        ).returncode


class RadonPolicyTest(unittest.TestCase):
    def test_a_and_c_allowed_d_rejected(self):
        for rank, code in (("A", 0), ("C", 0), ("D", 1)):
            with self.subTest(rank=rank):
                report = {
                    "sample.py": [
                        {
                            "name": "f",
                            "lineno": 3,
                            "complexity": 21 if rank == "D" else 11,
                            "rank": rank,
                        }
                    ]
                }
                issues, count, _ = quality.radon_issues(report)
                self.assertEqual(bool(issues), bool(code))
                self.assertEqual(count, 1)
                if code:
                    self.assertIn("sample.py:3: f, complejidad 21, grado D", issues)

    def test_mi_c_is_informative(self):
        responses = [
            {"sample.py": [{"name": "f", "lineno": 1, "complexity": 1, "rank": "A"}]},
            {"sample.py": {"rank": "C", "mi": 2.0}},
        ]
        with (
            mock.patch.object(quality, "run_json", side_effect=responses),
            contextlib.redirect_stdout(io.StringIO()) as output,
        ):
            self.assertEqual(quality.check_radon(), 0)
        self.assertIn("MI informativo", output.getvalue())


class BanditPolicyTest(unittest.TestCase):
    def test_clean_production_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "gisela" / "engine.py"
            path.parent.mkdir()
            path.write_text("x = 1\n")
            blocking, information = quality.bandit_issues(
                {"results": [], "errors": []}, [], root
            )
            self.assertEqual((blocking, information), ([], []))

    def test_production_low_and_test_medium_high_block(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            production = root / "gisela" / "engine.py"
            test = root / "gisela" / "tests" / "test_engine.py"
            test.parent.mkdir(parents=True)
            production.write_text("x = 1\n")
            test.write_text("x = 1\n")
            findings = [
                self._issue(production, "LOW"),
                self._issue(test, "MEDIUM"),
                self._issue(test, "HIGH"),
            ]
            blocking, _ = quality.bandit_issues(
                {"results": findings, "errors": []}, [], root
            )
            self.assertEqual(len(blocking), 3)

    def test_known_test_low_reports_new_low_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "gisela" / "test_example.py"
            path.parent.mkdir()
            path.write_text("assert True\n")
            issue = self._issue(path, "LOW")
            baseline = [
                {
                    "path": "gisela/test_example.py",
                    "rule": "B101",
                    "source": "assert True",
                    "count": 1,
                }
            ]
            blocking, information = quality.bandit_issues(
                {"results": [issue], "errors": []}, baseline, root
            )
            self.assertEqual(blocking, [])
            self.assertEqual(len(information), 1)
            blocking, _ = quality.bandit_issues(
                {"results": [issue, issue], "errors": []}, baseline, root
            )
            self.assertEqual(len(blocking), 1)

    def test_analysis_error_and_missing_tool_fail(self):
        blocking, _ = quality.bandit_issues(
            {"results": [], "errors": ["bad.py: SyntaxError"]}, [], quality.ROOT
        )
        self.assertTrue(blocking)
        blocking, _ = quality.bandit_issues(
            {"results": [], "errors": [], "files_skipped": ["bad.py"]}, [], quality.ROOT
        )
        self.assertTrue(blocking)
        result = subprocess.CompletedProcess([], 1, "", "No module named radon")
        with (
            mock.patch.object(quality.subprocess, "run", return_value=result),
            self.assertRaisesRegex(ValueError, "radon falló"),
        ):
            quality.run_json("radon", ("cc", "gisela", "-j"))

    def test_omitted_production_file_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "gisela").mkdir()
            (root / "gisela" / "engine.py").write_text("x = 1\n")
            baseline = root / "baseline.json"
            baseline.write_text("[]")
            report = {"results": [], "errors": [], "metrics": {"_totals": {}}}
            with (
                mock.patch.object(quality, "ROOT", root),
                mock.patch.object(quality, "SOURCES", ("gisela",)),
                mock.patch.object(quality, "BASELINE", baseline),
                mock.patch.object(quality, "run_json", return_value=report),
                contextlib.redirect_stdout(io.StringIO()) as output,
            ):
                self.assertEqual(quality.check_bandit(), 1)
            self.assertIn("Bandit no analizó", output.getvalue())

    def test_inventory_excludes_nested_environment_and_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in (
                "gisela/engine.py",
                "gisela/engine/tests/test_new.py",
                "gisela/.venv/lib/site-packages/pip.py",
                "gisela/engine/__pycache__/cached.py",
                "gisela/.git/hook.py",
            ):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("x = 1\n")
            with mock.patch.object(quality, "SOURCES", ("gisela",)):
                self.assertEqual(
                    quality.source_files(root),
                    ("gisela/engine.py", "gisela/engine/tests/test_new.py"),
                )

    def test_scan_uses_inventory_and_normalizes_metric_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "gisela").mkdir()
            (root / "gisela/engine.py").write_text("x = 1\n")
            (root / "baseline.json").write_text("[]")
            report = {
                "results": [],
                "errors": [],
                "metrics": {"_totals": {}, "./gisela/engine.py": {}},
            }
            with (
                mock.patch.object(quality, "ROOT", root),
                mock.patch.object(quality, "SOURCES", ("gisela",)),
                mock.patch.object(quality, "BASELINE", root / "baseline.json"),
                mock.patch.object(quality, "run_json", return_value=report) as run,
                contextlib.redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(quality.check_bandit(), 0)
                self.assertEqual(
                    run.call_args.args,
                    ("bandit", ("gisela/engine.py", "-f", "json", "-q")),
                )

    @staticmethod
    def _issue(path: Path, severity: str) -> dict:
        return {
            "filename": str(path),
            "line_number": 1,
            "test_id": "B101",
            "issue_severity": severity,
            "issue_text": "synthetic",
        }


class OrchestratorPolicyTest(unittest.TestCase):
    def test_all_groups_pass(self):
        commands = [("uno", ("a",)), ("dos", ("b",))]
        success = subprocess.CompletedProcess([], 0)
        with (
            mock.patch.object(check_gisela.subprocess, "run", return_value=success),
            contextlib.redirect_stdout(io.StringIO()) as output,
        ):
            self.assertEqual(check_gisela.run_checks(commands, 7), 0)
        self.assertIn("GISELA: 2/2", output.getvalue())

    def test_commands_have_four_static_groups_and_full_adds_six(self):
        for argv, expected in (([], 12), (["--full"], 18)):
            with (
                self.subTest(argv=argv),
                mock.patch.object(sys, "argv", ["check_gisela.py", *argv]),
                mock.patch.object(check_gisela, "run_checks", return_value=0) as runner,
            ):
                self.assertEqual(check_gisela.main(), 0)
                commands = runner.call_args.args[0]
                self.assertEqual(len(commands), expected)
                self.assertIn(
                    "gisela/packages/tegularis_the_son_of_the_volcan", commands[0][1]
                )
                self.assertEqual(
                    sum(label.startswith("Ruff") for label, _ in commands), 2
                )
                self.assertEqual(
                    sum(label.startswith("Radon") for label, _ in commands), 1
                )
                self.assertEqual(
                    sum(label.startswith("Bandit") for label, _ in commands), 1
                )

    def test_failure_continues_and_returns_failure(self):
        codes = [0, 1, 0]
        responses = [subprocess.CompletedProcess([], code) for code in codes]
        with (
            mock.patch.object(
                check_gisela.subprocess, "run", side_effect=responses
            ) as run,
            contextlib.redirect_stdout(io.StringIO()) as output,
        ):
            result = check_gisela.run_checks(
                [("uno", ("a",)), ("dos", ("b",)), ("tres", ("c",))], 7
            )
        self.assertEqual(result, 1)
        self.assertEqual(run.call_count, 3)
        self.assertIn("FALLÓ: dos", output.getvalue())
        self.assertIn("RESULTADO: tres: exit=0, segundos=", output.getvalue())


if __name__ == "__main__":
    unittest.main()
