import unittest
from engine import ReasoningEngine

class TestDeepReasoning(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = ReasoningEngine()
        kg = cls.engine.knowledge
        
        # 1. Popoliamo fatti strutturati per Deduzione
        # Relazione: Gatto --> è_un_tipo_di --> Mammifero
        # Relazione: Mammifero --> è_un_tipo_di --> Animale
        kg.add("Gatto", {"description": "Un felino domestico", "category": "Animali"})
        kg.connect("Gatto", "è_un_tipo_di", "Mammifero")
        
        kg.add("Mammifero", {"description": "Animale a sangue caldo con peli", "category": "Animali"})
        kg.connect("Mammifero", "è_un_tipo_di", "Animale")
        
        # 2. Popoliamo fatti per Analogia (Atomo e Sistema Solare)
        kg.add("Sistema Solare", {"category": "Astronomia"})
        kg.connect("Sistema Solare", "contiene", "Sole")
        kg.connect("Sistema Solare", "contiene", "Pianeti")
        kg.connect("Pianeti", "orbita_intorno_a", "Sole")
        
        kg.add("Atomo", {"category": "Fisica"})
        kg.connect("Atomo", "contiene", "Nucleo")
        kg.connect("Atomo", "contiene", "Elettroni")
        kg.connect("Elettroni", "orbita_intorno_a", "Nucleo")

    def test_01_deductive_chain(self):
        """Verifica che l'engine deduca l'appartenenza a lunghe catene logiche."""
        query = "Cosa puoi dirmi del Gatto?"
        print(f"\n[Deduction Test] Esecuzione per: '{query}'")
        res = self.engine.reason(query)
        
        # Verifiche
        self.assertIn("Animale", res.answer) # Dovrebbe aver dedotto la gerarchia
        has_deduction = any(s.type == "agent_action" and "Deduzione" in s.description for s in res.steps)
        self.assertTrue(has_deduction)
        print("✅ Deduzione catena Gatto -> Mammifero -> Animale riuscita.")

    def test_02_analogical_inference(self):
        """Verifica che l'engine trovi l'analogia tra Atomo e Sistema Solare."""
        # Se chiediamo dell'Atomo, dovrebbe vedere la similarità strutturale
        query = "Cos'è un Atomo?"
        print(f"\n[Analogy Test] Esecuzione per: '{query}'")
        res = self.engine.reason(query)
        
        # Dovrebbe citare l'analogia se i dati nel KG sono scarsi
        has_analogy = any(s.type == "agent_action" and "analogia" in s.description.lower() for s in res.steps)
        self.assertTrue(has_analogy)
        print("✅ Analogia Atomo <-> Sistema Solare individuata correttamente.")

if __name__ == "__main__":
    unittest.main()
