import unittest
import time
from engine import ReasoningEngine
from engine.core.types import SourceMetadata

class TestReasoningEngineV2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = ReasoningEngine()

    def test_01_communication_channels_trust(self):
        """Verifica che l'engine preferisca la fonte con Trust Score più alto."""
        concept = "TestConcept"
        
        # Impariamo da una fonte poco affidabile
        self.engine.learn(
            concept=concept,
            examples=["Esempio A"],
            description="Descrizione inaffidabile",
            channel="web_scraping",
            trust_score=0.3
        )
        
        # Impariamo da una fonte affidabile
        self.engine.learn(
            concept=concept,
            examples=["Esempio B"],
            description="Descrizione ufficiale",
            channel="official_source",
            trust_score=0.9
        )
        
        # Recuperiamo il concetto
        c = self.engine.knowledge.get(concept)
        best_info = c.get_best_info()
        
        self.assertEqual(best_info["channel"], "official_source")
        self.assertEqual(best_info["description"], "Descrizione ufficiale")

    def test_02_symbolic_math(self):
        """Verifica la risoluzione simbolica di equazioni."""
        # Test equazione di secondo grado
        res = self.engine.math.solve_symbolically("x^2 - 9 = 0")
        self.assertTrue(res["success"])
        # Le soluzioni dovrebbero contenere -3 e 3 (come stringhe da sympy)
        solutions = res["solutions"]
        self.assertIn("-3", solutions)
        self.assertIn("3", solutions)

    def test_03_identity_intent(self):
        """Verifica che l'engine riconosca la propria identità."""
        res = self.engine.reason("Chi sei?")
        self.assertIsNotNone(res.answer)
        self.assertIn("ReasoningEngine", res.answer)
        # Verifica che il canale sia 'system'
        has_system_step = any(s.channel == "system" for s in res.steps)
        self.assertTrue(has_system_step)

    def test_04_financial_ticker_detection(self):
        """Verifica che la query NLP rilevi correttamente i ticker finanziari."""
        res = self.engine.reason("Qual è il prezzo di AAPL?")
        # Dovrebbe aver attivato il canale finanziario (anche se fallisce la rete, lo step deve esserci)
        financial_step = any(s.type == "financial" for s in res.steps)
        self.assertTrue(financial_step)

    def test_05_data_analysis_stats(self):
        """Verifica l'integrazione del DataAnalysisTool."""
        data = [10, 20, 30, 40, 50]
        res = self.engine.data_analyzer.analyze_series(data, name="test_series")
        self.assertTrue(res["success"])
        self.assertEqual(res["stats"]["mean"], 30.0)
        self.assertEqual(res["trend"], "crescente")

    def test_06_knowledge_migration(self):
        """Verifica che il KnowledgeGraph gestisca il vecchio formato (legacy)."""
        # Creiamo un finto dato vecchio stile
        old_data = {
            "OldConcept": {
                "name": "OldConcept",
                "description": "Descrizione vecchia",
                "examples": ["Ex1"],
                "category": "test",
                "relations": {"tipo": ["Target"]}
            }
        }
        # Invochiamo il caricamento logico (usando la logica di migrazione interna)
        # Questo testa la robustezza del caricamento JSON scritto precedentemente
        import json
        import os
        temp_path = "data/test_migration.json"
        os.makedirs("data", exist_ok=True)
        with open(temp_path, "w") as f:
            json.dump(old_data, f)
            
        self.engine.knowledge.load(temp_path)
        c = self.engine.knowledge.get("OldConcept")
        self.assertIsNotNone(c)
        self.assertIn("legacy", c.channels)
        
        # Pulizia
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    unittest.main()
