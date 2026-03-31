"""
Test Suite completa per ReasoningEngine.

Categorie:
1. Knowledge Graph
2. Rule Engine + Math Module
3. NLP Parser
4. Deductive Reasoner
5. Inductive Reasoner
6. Analogical Reasoner
7. LLM Bridge (mock)
8. Engine Integrato (end-to-end)
"""

import sys
import os

# Aggiungi la directory del progetto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import ReasoningEngine, LLMClient, LLMBridge
from engine.knowledge_graph import KnowledgeGraph, Concept
from engine.rule_engine import RuleEngine
from engine.nlp_parser import parse
from engine.deductive import DeductiveReasoner
from engine.inductive import InductiveReasoner
from engine.analogical import AnalogicalReasoner
from engine.llm_bridge import ExtractedFact


# ============================================================
# TEST RUNNER
# ============================================================

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def assert_eq(self, actual, expected, msg=""):
        if actual == expected:
            self.passed += 1
            return True
        self.failed += 1
        self.errors.append(f"FAIL: {msg}\n  Expected: {expected}\n  Got: {actual}")
        return False

    def assert_true(self, condition, msg=""):
        if condition:
            self.passed += 1
            return True
        self.failed += 1
        self.errors.append(f"FAIL: {msg} — condition was False")
        return False

    def assert_near(self, actual, expected, tolerance=0.01, msg=""):
        if abs(actual - expected) <= tolerance:
            self.passed += 1
            return True
        self.failed += 1
        self.errors.append(f"FAIL: {msg}\n  Expected: ~{expected}\n  Got: {actual}")
        return False

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"📊 Risultati: {self.passed}/{total} passati, {self.failed} falliti")
        if self.errors:
            print(f"\n❌ Errori:")
            for e in self.errors:
                print(f"  {e}")
        print(f"{'='*60}")
        return self.failed == 0


def main():
    t = TestRunner()

    # ============================================================
    # 1. KNOWLEDGE GRAPH
    # ============================================================
    print("📚 1. Knowledge Graph...")

    kg = KnowledgeGraph()
    kg.add("gatto", "felino domestico", ["miao", "4 zampe"], "biologia")
    kg.add("cane", "mammifero fedele", ["bau", "4 zampe"], "biologia")
    kg.add("mammifero", "animale che allatta", [], "biologia")
    kg.add("animale", "essere vivente", [], "biologia")

    t.assert_true(kg.get("gatto") is not None, "KG: gatto esiste")
    t.assert_eq(kg.get("gatto").description, "felino domestico", "KG: descrizione gatto")
    t.assert_eq(kg.get("gatto").category, "biologia", "KG: categoria gatto")
    t.assert_eq(len(kg.get("gatto").examples), 2, "KG: esempi gatto")

    kg.connect("gatto", "è_un_tipo_di", "mammifero")
    kg.connect("mammifero", "è_un_tipo_di", "animale")
    t.assert_true("mammifero" in kg.get("gatto").relations["è_un_tipo_di"], "KG: relazione gatto→mammifero")

    found = kg.find(["gatto", "cane", "sconosciuto"])
    t.assert_true(found["gatto"] is not None, "KG: find gatto")
    t.assert_true(found["sconosciuto"] is None, "KG: find sconosciuto = None")

    search = kg.search("felino")
    t.assert_eq(len(search), 1, "KG: search trova gatto")

    # ============================================================
    # 2. RULE ENGINE + MATH
    # ============================================================
    print("🧮 2. Rule Engine + Math...")

    engine = ReasoningEngine()
    engine.learn("5", ["5 cose"], "il cinque", "math")
    engine.learn("3", ["3 cose"], "il tre", "math")

    # Operazioni base
    tests = [
        ("quanto fa 5 + 3?", 8.0),
        ("quanto fa 10 - 4?", 6.0),
        ("quanto fa 6 × 7?", 42.0),
        ("quanto fa 15 ÷ 3?", 5.0),
    ]
    for question, expected in tests:
        r = engine.reason(question)
        t.assert_near(r["answer"], expected, msg=f"Math: {question}")

    # Matematica avanzata
    adv_tests = [
        ("2 alla terza", 8.0),
        ("radice di 144", 12.0),
        ("5 fattoriale", 120),
        ("il 20% di 150", 30.0),
        ("area cerchio raggio 5", 78.54),
        ("ipotenusa cateti 3 4", 5.0),
    ]
    for question, expected in adv_tests:
        r = engine.reason(question)
        t.assert_near(r["answer"], expected, tolerance=0.1, msg=f"Math advanced: {question}")

    # Equazioni
    r = engine.reason("x + 5 = 12")
    t.assert_near(r["answer"], 7.0, msg="Math: equazione x + 5 = 12")

    # ============================================================
    # 3. NLP PARSER
    # ============================================================
    print("📝 3. NLP Parser...")

    p = parse("quanto fa 15 + 27?")
    t.assert_eq(p.intent, "calculate", "NLP: calculate intent")
    t.assert_eq(p.operation, "addition", "NLP: addition operation")
    t.assert_near(p.numbers[0], 15.0, msg="NLP: numbers[0]")
    t.assert_near(p.numbers[1], 27.0, msg="NLP: numbers[1]")

    p = parse("cos'è un atomo?")
    t.assert_eq(p.intent, "define", "NLP: define intent")

    p = parse("il gatto è un mammifero")
    t.assert_eq(p.intent, "learn", "NLP: learn intent")

    p = parse("il gatto è un animale?")
    t.assert_eq(p.intent, "verify", "NLP: verify intent (con ?)")

    p = parse("area cerchio raggio 5")
    t.assert_eq(p.operation, "area_circle", "NLP: area_circle operation")

    p = parse("5 fattoriale")
    t.assert_eq(p.operation, "factorial", "NLP: factorial operation")

    p = parse("perché il cielo è blu?")
    t.assert_eq(p.intent, "explain", "NLP: explain intent")

    # ============================================================
    # 4. DEDUCTIVE REASONER
    # ============================================================
    print("🔍 4. Deductive Reasoner...")

    engine2 = ReasoningEngine()
    engine2.knowledge.add("animale", category="biologia")
    engine2.knowledge.add("mammifero", category="biologia")
    engine2.knowledge.add("felino", category="biologia")
    engine2.knowledge.add("gatto", "felino domestico", category="biologia")
    engine2.knowledge.add("cane", category="biologia")
    engine2.knowledge.connect("mammifero", "è_un_tipo_di", "animale")
    engine2.knowledge.connect("felino", "è_un_tipo_di", "mammifero")
    engine2.knowledge.connect("gatto", "è_un_tipo_di", "felino")
    engine2.knowledge.connect("cane", "è_un_tipo_di", "mammifero")
    engine2.knowledge.connect("animale", "ha_caratteristica", "si_muove")
    engine2.knowledge.connect("mammifero", "ha_caratteristica", "allatta")

    # Catena transitiva: gatto → felino → mammifero → animale
    r = engine2.deductive.deduce("gatto", "animale")
    t.assert_true(r.found, "Deductive: gatto → animale")
    t.assert_true(r.steps_count >= 3, "Deductive: catena lunga >= 3")

    # Proprietà ereditata
    r = engine2.deductive.deduce("gatto", "si_muove")
    t.assert_true(r.found, "Deductive: gatto si_muove (ereditato)")

    r = engine2.deductive.deduce("gatto", "allatta")
    t.assert_true(r.found, "Deductive: gatto allatta (ereditato)")

    r = engine2.deductive.deduce("cane", "si_muove")
    t.assert_true(r.found, "Deductive: cane si_muove (ereditato)")

    # Negativo: gatto non ha "vola"
    r = engine2.deductive.deduce("gatto", "vola")
    t.assert_true(not r.found, "Deductive: gatto NON vola")

    # ============================================================
    # 5. INDUCTIVE REASONER
    # ============================================================
    print("📊 5. Inductive Reasoner...")

    examples = [
        "il cane ha 4 zampe",
        "il gatto ha 4 zampe",
        "il cavallo ha 4 zampe",
        "la mucca ha 4 zampe",
    ]
    r = engine2.inductive.induce_from_examples(examples)
    t.assert_true(r.found, "Inductive: pattern trovato")
    t.assert_true(len(r.patterns) > 0, "Inductive: almeno 1 pattern")

    # Verifica che il pattern sia "tutti hanno 4"
    numeric_patterns = [p for p in r.patterns if "4" in str(p.value)]
    t.assert_true(len(numeric_patterns) > 0, "Inductive: pattern '4 zampe'")

    # ============================================================
    # 6. ANALOGICAL REASONER
    # ============================================================
    print("🔄 6. Analogical Reasoner...")

    engine2.knowledge.add("sistema_solare", category="astronomia")
    engine2.knowledge.add("atomo", category="fisica")
    engine2.knowledge.add("cuore", category="biologia")
    engine2.knowledge.add("pompa", category="meccanica")
    engine2.knowledge.connect("sistema_solare", "ha_parte", "sole")
    engine2.knowledge.connect("atomo", "ha_parte", "nucleo")
    engine2.knowledge.connect("cuore", "ha_funzione", "pompa")
    engine2.knowledge.connect("pompa", "ha_funzione", "spinge")

    r = engine2.analogical.find_analogies("sistema_solare")
    t.assert_true(r.found, "Analogical: analogie per sistema_solare")
    t.assert_true(r.best_analogy is not None, "Analogical: best_analogy exists")

    # Confronto diretto
    exp = engine2.explain_analogy("cuore", "pompa")
    t.assert_true("similarity" in exp.lower() or "simile" in exp.lower() or "comune" in exp.lower(),
                  "Analogical: explain_analogy produce output")

    # ============================================================
    # 7. LLM BRIDGE (MOCK)
    # ============================================================
    print("🤖 7. LLM Bridge (mock)...")

    class MockLLM(LLMClient):
        def __init__(self): super().__init__(api_key="mock")
        def is_configured(self): return True
        def ask(self, prompt, system=None, max_tokens=500):
            p = prompt.lower()
            if "gravità" in p:
                return '{"descrizione": "Forza di attrazione tra masse", "categoria": "fisica", "proprieta": ["9.8 m/s2 sulla Terra"], "esempi": ["mela che cade"], "relazioni": [["terra", "ha", "gravita"]]}'
            return '{"descrizione": "N/A", "categoria": "generale", "proprieta": [], "esempi": [], "relazioni": []}'

    engine3 = ReasoningEngine()
    engine3.llm = LLMBridge(MockLLM(), engine3.knowledge, engine3.verifier)

    # Knowledge provider
    resp = engine3.llm.provide_knowledge("gravità")
    t.assert_true(len(resp.facts) > 0, "LLM: facts estratte per gravità")

    # Engine integration
    r = engine3.reason("cos'è la gravità?", use_llm=True)
    t.assert_true(r is not None, "LLM: engine.reason returns dict")
    if r:
        t.assert_true(r.get("answer") is not None, "LLM: engine ha una risposta")
        # Verifica che gravità sia nel KG
        t.assert_true(engine3.knowledge.get("gravità") is not None, "LLM: gravità nel KG dopo learn")

    # ============================================================
    # 8. ENGINE END-TO-END
    # ============================================================
    print("⚙️ 8. Engine End-to-End...")

    e = ReasoningEngine()

    # Learn + Reason
    e.learn("7", ["7 cose"], "il sette", "math")
    e.learn("8", ["8 cose"], "l'otto", "math")
    r = e.reason("quanto fa 7 + 8?")
    t.assert_near(r["answer"], 15.0, msg="E2E: 7+8=15")
    t.assert_true(r["verified"], "E2E: 7+8 verificato")
    t.assert_true(r["confidence"] > 0.9, "E2E: alta confidenza")

    # Verification con passi
    t.assert_true(len(r["steps"]) >= 4, "E2E: ha reasoning steps")

    # Explanation
    t.assert_true(len(r["explanation"]) > 50, "E2E: explanation non vuota")

    # Lookup
    r = e.reason("cosa è 7?")
    t.assert_true(r["answer"] is not None, "E2E: lookup 7")

    # Composite test: geometria
    r = e.reason("area triangolo base 10 altezza 5")
    t.assert_near(r["answer"], 25.0, msg="E2E: area triangolo")

    # what_do_you_know
    info = e.what_do_you_know()
    t.assert_true(info["stats"]["total_concepts"] > 0, "E2E: ha concetti")
    t.assert_true(info["stats"]["total_rules"] > 10, "E2E: ha >10 regole")

    # ============================================================
    # RISULTATO
    # ============================================================
    return t.summary()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
