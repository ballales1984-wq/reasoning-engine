"""
Demo Fase 4 — LLM Bridge (Mock Mode).

Testa il bridge senza chiamare un vero LLM.
Per usare un vero LLM: engine = ReasoningEngine(llm_api_key='sk-...')
"""

from engine import ReasoningEngine, LLMClient, LLMBridge
from engine.llm_bridge import ExtractedFact


class MockLLM(LLMClient):
    """LLM mock per test senza API calls."""

    def __init__(self):
        super().__init__(api_key="mock-testing")

    def is_configured(self):
        return True

    def ask(self, prompt, system=None, max_tokens=500):
        p = prompt.lower()
        if "fotosintesi" in p:
            return '{"descrizione": "Processo biologico con cui le piante convertono luce solare in energia", "categoria": "biologia", "proprieta": ["richiede luce", "produce ossigeno", "usa CO2"], "esempi": ["piante verdi", "alghe"], "relazioni": [["pianta", "usa", "fotosintesi"], ["fotosintesi", "produce", "ossigeno"]]}'
        if "atomo" in p:
            return '{"descrizione": "La piu piccola particella di un elemento chimico", "categoria": "fisica", "proprieta": ["ha nucleo", "ha elettroni"], "esempi": ["idrogeno", "carbonio"], "relazioni": [["atomo", "ha_parte", "nucleo"]]}'
        if "velocit" in p:
            return '{"risposta": "299792458 m/s", "spiegazione": "Costante fisica", "passaggi": ["Luce nel vuoto"], "confidenza": 0.99}'
        return '{"descrizione": "N/A", "categoria": "generale", "proprieta": [], "esempi": [], "relazioni": []}'


def main():
    print("=" * 60)
    print("🧠 LLM Bridge — Demo (Mock)")
    print("=" * 60)

    engine = ReasoningEngine()
    engine.llm = LLMBridge(MockLLM(), engine.knowledge, engine.verifier)

    # TEST 1: Knowledge Provider
    print("\n📚 TEST 1: LLM come Knowledge Provider")
    print("-" * 40)

    for concept in ["fotosintesi", "atomo"]:
        resp = engine.llm.provide_knowledge(concept)
        print(f"\n  '{concept}': {len(resp.facts)} fatti, confidenza {resp.confidence:.0%}")
        for f in resp.facts[:3]:
            print(f"    • {f.subject} → {f.relation} → {f.value}")

    # TEST 2: Engine + LLM Integration
    print("\n⚙️ TEST 2: Engine integrato con LLM")
    print("-" * 40)

    questions = [
        "cos'è la fotosintesi?",
        "cosa è un atomo?",
        "qual è la velocità della luce?",
    ]

    for q in questions:
        r = engine.reason(q, use_llm=True) or {}
        print(f"\n  ❓ {q}")
        print(f"     💡 {r.get('answer', 'N/A')}")
        print(f"     📊 Confidenza: {r.get('confidence', 0):.0%}")
        print(f"     🔧 {r.get('rule_used', 'N/A')}")

    # TEST 3: KG dopo apprendimento LLM
    print("\n📚 TEST 3: Knowledge Graph dopo apprendimento")
    print("-" * 40)

    for name in ["fotosintesi", "atomo"]:
        c = engine.knowledge.get(name)
        if c:
            print(f"\n  '{name}':")
            print(f"    Descrizione: {c.description}")
            print(f"    Categoria: {c.category}")
            print(f"    Relazioni: {dict(c.relations)}")

    # TEST 4: Storico
    print("\n📋 TEST 4: Storico chiamate LLM")
    print("-" * 40)
    for i, entry in enumerate(engine.llm.get_history(), 1):
        print(f"  {i}. {entry['action']} → confidenza {entry.get('confidence', 0):.0%}")

    print("\n" + "=" * 60)
    print("🎉 LLM Bridge demo completata!")
    print("=" * 60)
    print("\n💡 Per usare un vero LLM:")
    print("   engine = ReasoningEngine(llm_api_key='sk-...')")
    print("   result = engine.reason('domanda', use_llm=True)")


if __name__ == "__main__":
    main()
