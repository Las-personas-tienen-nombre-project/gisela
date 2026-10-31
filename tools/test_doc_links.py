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
            (root / 'README.md').write_text('[missing](missing.md)\n', encoding='utf-8')
            self.assertEqual(1, len(broken_links(root)))

    def test_external_url_is_out_of_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'README.md').write_text('[external](https://example.org/x)\n', encoding='utf-8')
            self.assertEqual([], broken_links(root))


if __name__ == '__main__':
    unittest.main()
