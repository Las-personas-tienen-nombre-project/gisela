import tempfile
import unittest
from pathlib import Path

from tools.check_doc_links import broken_links


class LocalDocumentationLinks(unittest.TestCase):
    def test_repository_links(self):
        self.assertEqual([], broken_links())

    def test_missing_target_is_reported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("[missing](missing.md)\n", encoding="utf-8")
            self.assertEqual(1, len(broken_links(root)))

    def test_external_url_is_out_of_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(
                "[external](https://example.org/x)\n", encoding="utf-8"
            )
            self.assertEqual([], broken_links(root))


class OperationalDocumentationCommands(unittest.TestCase):
    def test_current_entrypoints_do_not_reference_removed_orchestrators(self):
        root = Path(__file__).resolve().parents[1]
        pages = [
            root / "README.md",
            root / "docs/guides/QUICK_START.md",
            root / "gisela/engine/README.md",
            root / "gisela/contracts/README.md",
            root / "gisela/contracts/README_SEMANTIC_VALIDATOR.md",
            root / "gisela/contracts/SEMANTIC_VALIDATION.md",
            root / "narrative_conditions/README.md",
        ]
        obsolete = (
            "python tools/check_project.py",
            "python tools/check_documentation.py",
        )
        for page in pages:
            with self.subTest(page=page.relative_to(root)):
                content = page.read_text(encoding="utf-8")
                self.assertFalse(any(command in content for command in obsolete))


class CurrentDocumentationIntegrity(unittest.TestCase):
    def test_current_architecture_and_entrypoints_use_existing_checks(self):
        root = Path(__file__).resolve().parents[1]
        pages = [
            root / "README.md",
            *sorted((root / "docs/architecture").glob("*.md")),
            root / "docs/guides/VERIFICACION_GISELA.md",
        ]
        for page in pages:
            with self.subTest(page=str(page.relative_to(root))):
                body = page.read_text(encoding="utf-8")
                self.assertNotIn("python tools/check_project.py", body)
                for name in (
                    "check_gisela.py",
                    "check_quality.py",
                    "check_doc_links.py",
                    "verify_e0_invariants.py",
                    "verify_e1_invariants.py",
                    "verify_e2_invariants.py",
                    "verify_e3_invariants.py",
                ):
                    if "python tools/" + name in body:
                        self.assertTrue((root / "tools" / name).is_file())


if __name__ == "__main__":
    unittest.main()
