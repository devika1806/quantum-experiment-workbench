import importlib.util
from pathlib import Path
import unittest


@unittest.skipUnless(importlib.util.find_spec("streamlit"), "Optional UI dependencies not installed")
class AppTests(unittest.TestCase):
    def test_both_modes_and_stale_settings(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1]/"app.py"), default_timeout=30).run()
        self.assertFalse(app.exception)
        app.number_input[0].set_value(100)
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["result"]["settings"]["noise"], "bit")
        self.assertEqual(len(app.metric), 3)
        app.slider[0].set_value(.2).run()
        self.assertTrue(any("Settings changed" in w.value for w in app.warning))
        app.selectbox[0].set_value("Phase flips · see the limitation").run()
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["result"]["settings"]["initial"], "+")
        self.assertEqual(app.session_state["result"]["settings"]["noise"], "phase")
