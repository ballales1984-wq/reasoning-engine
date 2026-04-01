import unittest
from engine import ReasoningEngine


class TestWebBrowsing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = ReasoningEngine()

    def test_01_direct_url_browsing(self):
        """Verifica che l'engine visiti un URL e ne estragga il contenuto."""
        url = "http://example.com/"
        query = f"Cosa c'e su questo sito? {url}"

        print(f"\n[Test Browsing] in corso su: {url}...")
        res = self.engine.reason(query)

        self.assertIsNotNone(res.answer)
        has_browsing_step = any(s.type == "browsing" for s in res.steps)
        self.assertTrue(has_browsing_step)

        has_correct_channel = any(s.channel == "web_browsing" for s in res.steps)
        self.assertTrue(has_correct_channel)

        print(f"[OK] Browsing riuscito. Estratto: {res.answer[:100]}...")

    def test_02_parsing_broken_url(self):
        """Verifica che l'engine gestisca URL non validi senza crashare."""
        url = "https://questo-sito-non-esiste-123456.com"
        res = self.engine.reason(f"Visita {url}")

        self.assertIsNotNone(res.answer)
        print("[OK] Gestione URL non valido superata.")


if __name__ == "__main__":
    unittest.main()
