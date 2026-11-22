"""Regression checks for local AI's explicit 0% startup state."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHAT = ROOT / "web" / "chat.js"
LOADER = ROOT / "llm_local.py"
INDEX = ROOT / "web" / "index.html"


class LocalAiZeroProgressTests(unittest.TestCase):
    def test_zero_percent_is_not_treated_as_missing_progress(self):
        source = CHAT.read_text(encoding="utf-8")
        self.assertIn("m.state === 'starting' && m.pct != null ? Math.max", source)
        self.assertIn("l.pct != null ? ' ' + l.pct + '%' : '…'", source)
        self.assertIn("m.state === 'starting' && m.pct != null ? ` ${m.pct}%` : ''", source)
        self.assertNotIn("m.state === 'starting' && m.pct ? ", source)
        self.assertNotIn("l.pct ? ' ' + l.pct", source)

    def test_initial_unknown_progress_and_shipped_first_load_wording(self):
        loader = LOADER.read_text(encoding="utf-8")
        source = CHAT.read_text(encoding="utf-8")
        self.assertIn("self.state, self.pct, self.message = 'loading', None, ''", loader)
        self.assertIn("Local AI available · your first question loads it and may take a while", source)
        self.assertIn("if self.proc is proc:", loader)
        self.assertIn("self.pct = ev.get('p')", loader)

    def test_chat_asset_version_bumped(self):
        index = INDEX.read_text(encoding="utf-8")
        self.assertIn('/ui/chat.js?v=15', index)

    def test_unknown_progress_still_uses_starting_ellipsis(self):
        source = CHAT.read_text(encoding="utf-8")
        self.assertIn("l.pct != null ? ' ' + l.pct + '%' : '…'", source)
        self.assertIn("pct === null ? ' run' : ''", source)
        self.assertIn("Starting the local AI", source)


if __name__ == "__main__":
    unittest.main()
