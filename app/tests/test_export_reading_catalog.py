"""Fixture tests for the offline reading catalog exporter."""
import json
import tempfile
import unittest
from pathlib import Path
from tools.export_reading_catalog import export

class ReadingCatalogExportTests(unittest.TestCase):
    def test_filters_sorts_and_escapes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog = root / "catalog.json"
            output = root / "catalog.html"
            catalog.write_text(json.dumps([
                {"kind": "video", "title": "Not a book", "collection": "Other"},
                {"kind": "pdf", "title": "<Guide & Notes>", "collection": "Zed"},
                {"kind": "html", "title": "Alpha", "collection": "A"},
                {"kind": "metadata", "title": "Internal", "collection": "A"},
                {"kind": "pptx", "title": "Slides", "collection": "A"},
            ]), encoding="utf-8")
            self.assertEqual(export(catalog, output), 3)
            result = output.read_text(encoding="utf-8")
            self.assertIn("&lt;Guide &amp; Notes&gt;", result)
            self.assertNotIn("Not a book", result)
            self.assertNotIn("Internal", result)
            self.assertLess(result.index("Alpha"), result.index("Slides"))
            self.assertLess(result.index("Slides"), result.index("&lt;Guide"))

    def test_rejects_non_list_catalog(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog = root / "catalog.json"
            catalog.write_text("{}", encoding="utf-8")
            with self.assertRaises(ValueError):
                export(catalog, root / "out.html")

if __name__ == "__main__":
    unittest.main()
