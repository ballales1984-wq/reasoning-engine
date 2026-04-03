"""
Demo: Question-Based Reasoner completo

Mostra come usare:
1. HypothesisSpace diretto
2. Integrazione con Knowledge Graph
3. Soft probability updates
4. Confidence threshold
5. Risposte unknown/maybe
6. LLM Feature Extractor (simulato)
7. Auto Researcher (simulato)
"""

from engine.question_based import (
    HypothesisSpace,
    QuestionReasoner,
    ReasoningStatus,
    AnswerConfidence,
    KnowledgeGraphBridge,
    create_space_from_knowledge,
)


def demo_basic():
    """Demo base: ipotesi fisse."""
    print("\n" + "=" * 50)
    print("🦊 Demo 1: Indovina l'animale (base)")
    print("=" * 50)
    
    hypotheses = {
        "cane": {"domestico": True, "coda_lunga": False, "fa_miao": False},
        "gatto": {"domestico": True, "coda_lunga": True, "fa_miao": True},
        "volpe": {"domestico": False, "coda_lunga": True, "fa_miao": False},
    }
    
    # Risposte simulate
    answers = {"domestico": True, "coda_lunga": True}
    
    def mock_handler(feature):
        return answers.get(feature, False), AnswerConfidence.HIGH
    
    space = HypothesisSpace(hypotheses)
    reasoner = QuestionReasoner(space, confidence_threshold=0.9)
    
    result = reasoner.run(mock_handler)
    
    print(f"\n📊 Status: {result['status']}")
    print(f"🎯 Conclusione: {result['final_hypothesis']}")
    print(f"📝 Passi: {result['num_steps']}")
    print("\n🔍 Trace:")
    for i, step in enumerate(result["trace"], 1):
        print(f"  {i}. {step['question']} → {step['answer']}")


def demo_soft_probability():
    """Demo: soft probability con risposte uncertain."""
    print("\n" + "=" * 50)
    print("🎲 Demo 2: Soft Probability (risposte incerte)")
    print("=" * 50)
    
    hypotheses = {
        "cane": {"domestico": True, "coda_lunga": False},
        "gatto": {"domestico": True, "coda_lunga": True},
        "volpe": {"domestico": False, "coda_lunga": True},
    }
    
    # Simulazione: risposta "non so" sulla coda
    def uncertain_handler(feature):
        if feature == "domestico":
            return True, AnswerConfidence.HIGH
        return "unknown", AnswerConfidence.UNKNOWN
    
    space = HypothesisSpace(hypotheses)
    reasoner = QuestionReasoner(space, confidence_threshold=0.8)
    
    result = reasoner.run(uncertain_handler)
    
    print(f"\n📊 Status: {result['status']}")
    print(f"🎯 Conclusione: {result['final_hypothesis']}")
    print(f"📈 Probabilità finali:")
    for h, p in result["final_probabilities"].items():
        if p > 0.01:
            print(f"   {h}: {p:.1%}")


def demo_ambiguous():
    """Demo: stato ambiguo."""
    print("\n" + "=" * 50)
    print("❓ Demo 3: Stato ambiguo")
    print("=" * 50)
    
    hypotheses = {
        "gatto": {"domestico": True, "coda_lunga": True},
        "coniglio": {"domestico": True, "coda_lunga": True},  # Stesse feature!
    }
    
    def handler(feature):
        return True, AnswerConfidence.HIGH
    
    space = HypothesisSpace(hypotheses)
    reasoner = QuestionReasoner(space, confidence_threshold=0.95)
    
    result = reasoner.run(handler)
    
    print(f"\n📊 Status: {result['status']}")
    print(f"📝 Messaggio: {result['message']}")
    print(f"📈 Probabilità:")
    for h, p in result["final_probabilities"].items():
        print(f"   {h}: {p:.1%}")


def demo_knowledge_graph():
    """Demo: integrazione con Knowledge Graph."""
    print("\n" + "=" * 50)
    print("🧠 Demo 4: Knowledge Graph Bridge")
    print("=" * 50)
    
    # Crea KG con animali
    from engine.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    
    # Aggiungi concetti
    kg.add("cane", "Animale domestico", category="mammifero")
    kg.concepts["cane"].add_relation("è_domestico", "true")
    kg.concepts["cane"].add_relation("ha_coda", "corta")
    
    kg.add("gatto", "Animale domestico", category="mammifero")
    kg.concepts["gatto"].add_relation("è_domestico", "true")
    kg.concepts["gatto"].add_relation("ha_coda", "lunga")
    
    kg.add("volpe", "Animale selvatico", category="mammifero")
    kg.concepts["volpe"].add_relation("è_domestico", "false")
    kg.concepts["volpe"].add_relation("ha_coda", "lunga")
    
    # Crea HypothesisSpace dal KG
    bridge = KnowledgeGraphBridge(kg)
    space = bridge.build_hypothesis_space(
        ["cane", "gatto", "volpe"],
        default_features=["domestico", "coda"]
    )
    
    print(f"\n📦 HypothesisSpace creato dal KG:")
    print(f"   Ipotesi: {space.remaining()}")
    print(f"   Feature: {space.features()}")
    print(f"   Priors: {dict(space.priors)}")


def demo_llm_extractor():
    """Demo: LLM Feature Extractor."""
    print("\n" + "=" * 50)
    print("🤖 Demo 5: LLM Feature Extractor")
    print("=" * 50)
    
    from engine.question_based import LLMFeatureExtractor
    
    extractor = LLMFeatureExtractor(llm_client=None)  # Nessun LLM per ora
    
    print("""
LLM Feature Extractor pronto!

Usage:
    extractor = LLMFeatureExtractor(llm_client)
    
    features = extractor.extract_features(
        new_concept="lupo",
        existing_hypotheses=["cane", "gatto", "volpe"],
        context="animale mammifero"
    )
    
    # Output: {"selvatico": true, "ulula": true, "caccia_in_branco": true, ...}

Nota: Serve un LLM configurato (Ollama, OpenAI) per funzionare.
Passalo nel costruttore: LLMFeatureExtractor(llm_client=ollama)
""")


def demo_auto_researcher():
    """Demo: Auto Researcher."""
    print("\n" + "=" * 50)
    print("🌐 Demo 6: Auto Researcher")
    print("=" * 50)
    
    from engine.question_based import AutoResearcher
    
    researcher = AutoResearcher()
    
    print("""
Auto Researcher pronto!

Usage:
    researcher = AutoResearcher(web_tool, vector_store, llm_extractor)
    
    result = researcher.full_research_cycle(
        kg,
        new_concept="lupo",
        existing_hypotheses=["cane", "gatto", "volpe"],
        description="Mammifero carnivoro"
    )
    
    # result["features"] → {"selvatico": true, ...}
    # result["knowledge_graph"] → KG aggiornato

Nota: Richiede web_tool e vector_store configurati.
""")


def demo_full_cycle():
    """Demo: ciclo completo Question-Based Reasoning."""
    print("\n" + "=" * 50)
    print("🔄 Demo 7: Ciclo Completo")
    print("=" * 50)
    
    # Scenario: utente introduce un nuovo concetto "lupo"
    new_concept = "lupo"
    existing = ["cane", "gatto", "volpe"]
    
    print(f"\nScenario: Aggiungere '{new_concept}' a {existing}")
    
    # Step 1: LLM genera feature per il nuovo concetto
    from engine.question_based import LLMFeatureExtractor
    extractor = LLMFeatureExtractor()
    
    # (Senza LLM reale, simuliamo)
    new_features = {
        "selvatico": True,
        "coda_lunga": True,
        "ulula": True,
        "caccia_branco": True,
    }
    print(f"\n1. LLM genera feature per '{new_concept}':")
    print(f"   {new_features}")
    
    # Step 2: Aggiungi al KG
    from engine.knowledge_graph import KnowledgeGraph
    kg = KnowledgeGraph()
    kg.add(new_concept, "Mammifero carnivoro della famiglia Canidae")
    for feat, val in new_features.items():
        kg.concepts[new_concept].add_relation(f"ha_{feat}", str(val))
    
    # Aggiungi anche gli altri
    for h in existing:
        kg.add(h, "Animale")
        kg.concepts[h].add_relation("ha_domestico", "true" if h != "volpe" else "false")
    
    # Step 3: Crea HypothesisSpace
    bridge = KnowledgeGraphBridge(kg)
    space = bridge.build_hypothesis_space(
        [new_concept] + existing,
        default_features=["domestico", "coda_lunga", "ulula", "caccia_branco"]
    )
    
    print(f"\n2. HypothesisSpace costruito:")
    print(f"   Ipotesi: {space.remaining()}")
    
    # Step 4: Esegui ragionamento
    # Risposte: è domestico? NO, ha coda lunga? SI, ulula? SI
    def answer_handler(feature):
        answers = {
            "domestico": False,
            "coda_lunga": True,
            "ulula": True,
            "caccia_branco": True,
        }
        return answers.get(feature, False), AnswerConfidence.HIGH
    
    reasoner = QuestionReasoner(space, confidence_threshold=0.9)
    result = reasoner.run(answer_handler)
    
    print(f"\n3. Risultato:")
    print(f"   Status: {result['status']}")
    print(f"   Conclusione: {result['final_hypothesis']}")
    print(f"   Passi: {result['num_steps']}")
    
    print(f"\n✅ Ciclo completo: KG → LLM → Reasoner → KG aggiornato")


def main():
    """Esegue tutti i demo."""
    print("╔══════════════════════════════════════════════════╗")
    print("║    🧠 Question-Based Reasoner - Demo Suite       ║")
    print("╚══════════════════════════════════════════════════╝")
    
    # Run demos
    demo_basic()
    demo_soft_probability()
    demo_ambiguous()
    demo_knowledge_graph()
    demo_llm_extractor()
    demo_auto_researcher()
    demo_full_cycle()
    
    print("\n" + "=" * 50)
    print("✅ Tutti i demo completati!")
    print("=" * 50)


if __name__ == "__main__":
    main()