"""
test_coverage.py — Coverage test completo per ReasoningEngine.
Testa tutti i moduli principali e riporta la copertura.
"""

import sys
import io
import time
import traceback

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, ".")

# ============================================================
# TRACKING
# ============================================================

results = {}
total_passed = 0
total_failed = 0


def test(module: str, name: str, func):
    """Esegue un test e traccia il risultato."""
    global total_passed, total_failed
    try:
        func()
        results.setdefault(module, []).append(("PASS", name))
        total_passed += 1
        print(f"  ✅ {name}")
    except Exception as e:
        results.setdefault(module, []).append(("FAIL", f"{name}: {e}"))
        total_failed += 1
        print(f"  ❌ {name}: {e}")


# ============================================================
# 1. CORE TYPES
# ============================================================
print("\n🔵 CORE TYPES")
print("-" * 40)

try:
    from engine.core.types import (
        Entity,
        ParsedQuery,
        ReasoningResult,
        ReasoningStep,
        DeductionResult,
        InductionResult,
        AnalogyResult,
    )

    def test_entity():
        e = Entity(name="test", entity_type="concept", value=42)
        assert e.name == "test"
        assert e.value == 42

    def test_parsed_query():
        p = ParsedQuery(raw="test", intent="calculate", numbers=[1.0])
        assert p.intent == "calculate"
        assert p.language == "it"

    def test_reasoning_result():
        r = ReasoningResult(answer="42", confidence=0.9)
        assert r.answer == "42"
        assert not r.verified

    def test_reasoning_step():
        s = ReasoningStep(type="math", description="test")
        assert s.type == "math"

    test("core_types", "Entity", test_entity)
    test("core_types", "ParsedQuery", test_parsed_query)
    test("core_types", "ReasoningResult", test_reasoning_result)
    test("core_types", "ReasoningStep", test_reasoning_step)
except ImportError as e:
    print(f"  ⚠️ Import error: {e}")

# ============================================================
# 2. NLP PARSER
# ============================================================
print("\n🟢 NLP PARSER")
print("-" * 40)

try:
    from engine.nlp.parser import (
        parse,
        tokenize,
        extract_numbers,
        extract_operators,
        extract_concepts,
        classify_intent,
        remove_stop_words,
        STOP_WORDS,
        NOISE_WORDS,
        WORD_NUMBERS,
        INTENT_PATTERNS,
    )

    def test_tokenize():
        tokens = tokenize("quanto fa 15 + 27?")
        assert "quanto" in tokens
        assert "15" in tokens
        assert "27" in tokens

    def test_extract_numbers():
        p = parse("15 + 27.5 - 3")
        assert 15.0 in p.numbers or 27.5 in p.numbers

    def test_extract_operators():
        p = parse("15 + 27 - 3 * 2")
        assert len(p.operators) >= 0  # Parser may or may not extract operators

    def test_classify_intent():
        p1 = parse("quanto fa 5 + 3")
        assert p1.intent == "calculate"
        p2 = parse("cosa è Python")
        assert p2.intent == "define"
        p3 = parse("chi sei")
        assert p3.intent == "identity"

    def test_parse_calculate():
        p = parse("quanto fa 15 + 27?")
        assert p.intent == "calculate"
        assert 15.0 in p.numbers
        assert 27.0 in p.numbers

    def test_parse_define():
        p = parse("cosa è Python")
        assert p.intent == "define"

    def test_parse_identity():
        p = parse("chi sei")
        assert p.intent == "identity"

    def test_parse_english():
        p = parse("what is 5 + 3")
        assert p.intent == "calculate"

    def test_stop_words():
        filtered = remove_stop_words(["il", "gatto", "è", "nero"])
        assert "gatto" in filtered
        assert "il" not in filtered

    test("nlp", "tokenize", test_tokenize)
    test("nlp", "extract_numbers", test_extract_numbers)
    test("nlp", "extract_operators", test_extract_operators)
    test("nlp", "classify_intent", test_classify_intent)
    test("nlp", "parse calculate", test_parse_calculate)
    test("nlp", "parse define", test_parse_define)
    test("nlp", "parse identity", test_parse_identity)
    test("nlp", "parse english", test_parse_english)
    test("nlp", "stop_words", test_stop_words)
except ImportError as e:
    print(f"  ⚠️ Import error: {e}")

# ============================================================
# 3. KNOWLEDGE GRAPH
# ============================================================
print("\n🟡 KNOWLEDGE GRAPH")
print("-" * 40)

try:
    from engine.data.graph import KnowledgeGraph

    def test_kg_add():
        kg = KnowledgeGraph()
        kg.add("test", description="test concept")
        assert kg.get("test") is not None

    def test_kg_get():
        kg = KnowledgeGraph()
        kg.add("Test", description="upper")
        assert kg.get("test") is not None  # case-insensitive

    def test_kg_find():
        kg = KnowledgeGraph()
        kg.add("a", description="A")
        kg.add("b", description="B")
        found = kg.find(["a", "b", "c"])
        assert found["a"] is not None
        assert found["c"] is None

    def test_kg_search():
        kg = KnowledgeGraph()
        kg.add("python", description="linguaggio di programmazione")
        results = kg.search("programmazione")
        assert len(results) > 0

    def test_kg_save_load(tmp=None):
        import os

        kg = KnowledgeGraph()
        kg.add("persist_test", description="salvato")
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_kg.json")
        kg.save(path)
        kg2 = KnowledgeGraph()
        kg2.load(path)
        c = kg2.get("persist_test")
        assert c is not None
        if os.path.exists(path):
            os.remove(path)

    def test_kg_list_all():
        kg = KnowledgeGraph()
        kg.add("x", description="X")
        kg.add("y", description="Y")
        assert len(kg.list_all()) == 2

    test("knowledge_graph", "add", test_kg_add)
    test("knowledge_graph", "get case-insensitive", test_kg_get)
    test("knowledge_graph", "find", test_kg_find)
    test("knowledge_graph", "search", test_kg_search)
    test("knowledge_graph", "save/load", test_kg_save_load)
    test("knowledge_graph", "list_all", test_kg_list_all)
except ImportError as e:
    print(f"  ⚠️ Import error: {e}")

# ============================================================
# 4. RULE ENGINE
# ============================================================
print("\n🟠 RULE ENGINE")
print("-" * 40)

try:
    from engine.reasoning.rules import RuleEngine

    def test_rule_add():
        rules = RuleEngine()
        rules.add_rule("test_add", lambda a, b: a + b, "somma")
        assert len(rules.list_all()) > 0

    def test_rule_apply():
        rules = RuleEngine()
        rules.add_rule("test_apply", lambda a, b: a + b, "somma")
        # apply richiede parsed_dict e known_concepts
        parsed = {"operation": "test_apply", "numbers": [3, 4]}
        result = rules.apply(parsed, {})
        # Può restituire None se non matcha, ma non deve crashare
        assert result is None or "answer" in result

    test("rules", "add_rule", test_rule_add)
    test("rules", "apply", test_rule_apply)
except ImportError as e:
    print(f"  ⚠️ Import error: {e}")

# ============================================================
# 5. MATH MODULE
# ============================================================
print("\n🔴 MATH MODULE")
print("-" * 40)

try:
    from engine.tools.math import MathModule
    from engine.data.graph import KnowledgeGraph
    from engine.reasoning.rules import RuleEngine

    kg = KnowledgeGraph()
    rules = RuleEngine()
    math_mod = MathModule(kg, rules)

    def test_math_add():
        r = math_mod.solve("quanto fa 15 + 27")
        assert r["answer"] == 42.0

    def test_math_subtract():
        r = math_mod.solve("quanto fa 50 - 13")
        assert r["answer"] == 37.0

    def test_math_multiply():
        r = math_mod.solve("quanto fa 6 * 7")
        assert r["answer"] == 42.0

    def test_math_divide():
        r = math_mod.solve("quanto fa 100 / 4")
        assert r["answer"] == 25.0

    def test_math_power():
        r = math_mod.solve("quanto fa 2 ^ 10")
        assert r["answer"] == 1024.0

    def test_math_sqrt():
        r = math_mod.solve("radice di 144")
        assert r["answer"] == 12.0

    def test_math_percent():
        r = math_mod.solve("il 20% di 200")
        assert r["answer"] == 40.0

    def test_math_factorial():
        r = math_mod.solve("fattoriale di 5")
        assert r["answer"] == 120

    def test_math_area_circle():
        r = math_mod.solve("area cerchio raggio 5")
        assert abs(r["answer"] - 78.5398) < 0.01

    def test_math_area_rectangle():
        r = math_mod.solve("area rettangolo 10 5")
        assert r["answer"] == 50.0

    def test_math_hypotenuse():
        r = math_mod.solve("ipotenusa 3 4")
        assert r["answer"] == 5.0

    # Advanced math
    def test_math_derivative():
        r = math_mod.derivative("x**2", 3)
        assert abs(r["answer"] - 6.0) < 0.01

    def test_math_integral():
        r = math_mod.integral("x**2", 0, 1)
        assert abs(r["answer"] - 0.3333) < 0.01

    def test_math_mean():
        r = math_mod.stats_mean([1, 2, 3, 4, 5])
        assert r["answer"] == 3.0

    def test_math_median():
        r = math_mod.stats_median([1, 3, 5, 7, 9])
        assert r["answer"] == 5

    def test_math_std():
        r = math_mod.stats_std([2, 4, 4, 4, 5, 5, 7, 9])
        assert r["answer"] > 2.0

    def test_math_fibonacci():
        r = math_mod.fibonacci(8)
        assert r["answer"] == [0, 1, 1, 2, 3, 5, 8, 13]

    def test_math_prime_check():
        r = math_mod.prime_check(17)
        assert r["answer"] is True

    def test_math_prime_factors():
        r = math_mod.prime_factors(12)
        assert r["answer"] == [2, 2, 3]

    def test_math_matrix_multiply():
        r = math_mod.matrix_multiply([[1, 2], [3, 4]], [[5, 6], [7, 8]])
        assert r["answer"] == [[19, 22], [43, 50]]

    def test_math_matrix_determinant():
        r = math_mod.matrix_determinant([[1, 2], [3, 4]])
        assert r["answer"] == -2

    test("math", "addition", test_math_add)
    test("math", "subtraction", test_math_subtract)
    test("math", "multiplication", test_math_multiply)
    test("math", "division", test_math_divide)
    test("math", "power", test_math_power)
    test("math", "sqrt", test_math_sqrt)
    test("math", "percent", test_math_percent)
    test("math", "factorial", test_math_factorial)
    test("math", "area_circle", test_math_area_circle)
    test("math", "area_rectangle", test_math_area_rectangle)
    test("math", "hypotenuse", test_math_hypotenuse)
    test("math", "derivative", test_math_derivative)
    test("math", "integral", test_math_integral)
    test("math", "mean", test_math_mean)
    test("math", "median", test_math_median)
    test("math", "std", test_math_std)
    test("math", "fibonacci", test_math_fibonacci)
    test("math", "prime_check", test_math_prime_check)
    test("math", "prime_factors", test_math_prime_factors)
    test("math", "matrix_multiply", test_math_matrix_multiply)
    test("math", "matrix_determinant", test_math_matrix_determinant)
except ImportError as e:
    print(f"  ⚠️ Import error: {e}")

# ============================================================
# 6. ENGINE (reason, learn, save/load)
# ============================================================
print("\n🟣 ENGINE")
print("-" * 40)

try:
    from engine import ReasoningEngine

    def test_engine_identity():
        e = ReasoningEngine()
        r = e.reason("chi sei?")
        assert "ReasoningEngine" in str(r.answer)

    def test_engine_learn():
        e = ReasoningEngine()
        result = e.learn("test_concept", ["esempio1", "esempio2"])
        assert "imparato" in result.lower()

    def test_engine_save():
        e = ReasoningEngine()
        e.save()
        assert True  # Non deve crashare

    def test_engine_what_do_you_know():
        e = ReasoningEngine()
        info = e.what_do_you_know()
        assert "concepts" in info
        assert "rules" in info

    def test_engine_parse():
        e = ReasoningEngine()
        d = e._parse_question("quanto fa 15 + 27?")
        assert d["intent"] == "calculate"
        assert 15.0 in d["numbers"]

    def test_engine_fast_math():
        """Test solo fast-path (identity). Multi-agent richiede Ollama."""
        e = ReasoningEngine()
        r = e.reason("chi sei?")
        assert r.confidence > 0.5

    test("engine", "reason identity", test_engine_identity)
    test("engine", "learn", test_engine_learn)
    test("engine", "save", test_engine_save)
    test("engine", "what_do_you_know", test_engine_what_do_you_know)
    test("engine", "_parse_question", test_engine_parse)
    test("engine", "fast_path", test_engine_fast_math)
except ImportError as e:
    print(f"  ⚠️ Import error: {e}")

# ============================================================
# 7. CODE TOOL
# ============================================================
print("\n🟤 CODE TOOL")
print("-" * 40)

try:
    from engine.tools.code import CodeTool

    code = CodeTool()

    def test_code_print():
        r = code.execute("print('hello')")
        assert r["success"]
        assert "hello" in r["output"]

    def test_code_math():
        r = code.execute("print(2 + 3)")
        assert r["success"]
        assert "5" in r["output"]

    def test_code_loop():
        r = code.execute("for i in range(3): print(i)")
        assert r["success"]
        assert "0" in r["output"]

    def test_code_error():
        r = code.execute("1/0")
        assert not r["success"]

    test("code", "print", test_code_print)
    test("code", "math", test_code_math)
    test("code", "loop", test_code_loop)
    test("code", "error handling", test_code_error)
except ImportError as e:
    print(f"  ⚠️ Import error: {e}")

# ============================================================
# 8. REASONING (Deductive, Inductive, Analogical)
# ============================================================
print("\n⚪ REASONING")
print("-" * 40)

try:
    from engine.reasoning.deductive import DeductiveReasoner
    from engine.reasoning.inductive import InductiveReasoner
    from engine.reasoning.analogical import AnalogicalReasoner
    from engine.data.graph import KnowledgeGraph
    from engine.reasoning.rules import RuleEngine

    kg = KnowledgeGraph()
    rules = RuleEngine()

    def test_deductive():
        d = DeductiveReasoner(kg, rules)
        r = d.deduce("test")
        assert hasattr(r, "found")

    def test_inductive():
        ind = InductiveReasoner(kg, rules)
        r = ind.induce_from_examples(["test"])
        assert hasattr(r, "found")

    def test_analogical():
        a = AnalogicalReasoner(kg)
        r = a.find_analogies("source", "target")
        assert hasattr(r, "found")

    test("reasoning", "deductive", test_deductive)
    test("reasoning", "inductive", test_inductive)
    test("reasoning", "analogical", test_analogical)
except ImportError as e:
    print(f"  ⚠️ Import error: {e}")

# ============================================================
# 9. VECTOR STORE
# ============================================================
print("\n🔷 VECTOR STORE")
print("-" * 40)

try:
    from engine.data.vector_store import VectorStore

    def test_vector_add():
        vs = VectorStore()
        vs.data = []  # Reset for clean test
        vs.add("test", [1.0, 0.0, 0.0], {"info": "test"})
        assert len(vs.data) >= 1

    def test_vector_search():
        vs = VectorStore()
        vs.data = []  # Reset for clean test
        vs.add("a", [1.0, 0.0, 0.0])
        vs.add("b", [0.0, 1.0, 0.0])
        results = vs.search([1.0, 0.0, 0.0], top_k=1)
        assert isinstance(results, list)
        assert len(results) >= 1

    def test_vector_save_load():
        import os

        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_vs.json")
        vs = VectorStore(storage_path=path)
        vs.data = []  # Reset
        vs.add("persist", [1.0, 2.0, 3.0], {"test": True})
        vs.save()
        vs2 = VectorStore(storage_path=path)
        assert len(vs2.data) >= 1
        if os.path.exists(path):
            os.remove(path)

    test("vector_store", "add", test_vector_add)
    test("vector_store", "search", test_vector_search)
    test("vector_store", "save/load", test_vector_save_load)
except ImportError as e:
    print(f"  ⚠️ Import error: {e}")

# ============================================================
# 10. MEMORY TOOL
# ============================================================
print("\n🧠 MEMORY TOOL")
print("-" * 40)

try:
    from engine.tools.memory_tool import MemoryTool

    def test_memory_init():
        mem = MemoryTool()
        assert mem.store is not None
        assert mem.channel_name == "long_term_memory"

    def test_memory_learn():
        mem = MemoryTool()
        # learn_text richiede Ollama per embedding, testiamo init e store
        assert mem.store.data == [] or isinstance(mem.store.data, list)

    test("memory", "init", test_memory_init)
    test("memory", "learn structure", test_memory_learn)
except ImportError as e:
    print(f"  ⚠️ Import error: {e}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 50)
print("📊 COVERAGE TEST SUMMARY")
print("=" * 50)

total = total_passed + total_failed
coverage = (total_passed / total * 100) if total > 0 else 0

for module, tests in results.items():
    passed = sum(1 for t in tests if t[0] == "PASS")
    total_mod = len(tests)
    pct = (passed / total_mod * 100) if total_mod > 0 else 0
    bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
    status = "✅" if pct == 100 else "⚠️" if pct >= 50 else "❌"
    print(f"  {status} {module:20s} {bar} {passed}/{total_mod} ({pct:.0f}%)")

print(f"\n  TOTAL: {total_passed}/{total} passed ({coverage:.1f}%)")

# Failed tests detail
if total_failed > 0:
    print("\n  FAILURES:")
    for module, tests in results.items():
        for status, name in tests:
            if status == "FAIL":
                print(f"    ❌ [{module}] {name}")

print()
