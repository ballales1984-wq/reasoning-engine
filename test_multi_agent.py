import unittest
from engine import ReasoningEngine

class TestMultiAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = ReasoningEngine()

    def test_01_multi_agent_flow(self):
        """Verifica il flusso completo tra gli agenti."""
        query = "Chi è l'attuale CEO di Apple?"
        print(f"\n[Multi-Agent Test] Esecuzione per: '{query}'")
        
        res = self.engine.reason(query)
        
        # Verifiche Strutturali
        self.assertIsNotNone(res.answer)
        self.assertEqual(res.reasoning_type, "multi_agent_collaboration")
        
        # Verifica presenza agenti negli step
        agent_names = [s.description for s in res.steps]
        has_researcher = any("Researcher" in d for d in agent_names)
        has_analyst = any("Analyst" in d for d in agent_names)
        has_critic = any("Critic" in d for d in agent_names)
        
        self.assertTrue(has_researcher, "Manca l'agente Ricercatore")
        self.assertTrue(has_analyst, "Manca l'agente Analista")
        self.assertTrue(has_critic, "Manca l'agente Critico")
        
        print(f"✅ Flusso Multi-Agent confermato per tutti i ruoli.")
        print(f"💬 Risposta finale: {res.answer[:100]}...")
        if "[Critica AI:" in res.explanation:
            print("🔍 Feedback del Critico rilevato nella spiegazione.")

if __name__ == "__main__":
    unittest.main()
