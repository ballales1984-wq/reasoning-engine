#!/usr/bin/env python3
"""
Test completo del ReasoningEngine -- tutti i moduli.
Esegui: python test_all.py
"""

from engine import ReasoningEngine
from engine.tools.finance import FinanceModule


def run_test(name, test_func):
    """Esegue un test e mostra il risultato."""
    try:
        result = test_func()
        status = "[OK]" if result else "[FAIL]"
        print(f"  {status} {name}")
        return result
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("[TEST] ReasoningEngine -- Test Suite Completa")
    print("=" * 60)
    print()

    engine = ReasoningEngine()
    finance = FinanceModule(engine.knowledge, engine.rules)

    passed = 0
    total = 0

    # === MATEMATICA ===
    print("[MATEMATICA]")

    def test_addition():
        r = engine.reason("quanto fa 15 + 27?")
        return r.answer == 42.0

    total += 1
    if run_test("Addizione", test_addition):
        passed += 1

    def test_subtraction():
        r = engine.reason("quanto fa 100 - 37?")
        return r.answer == 63.0

    total += 1
    if run_test("Sottrazione", test_subtraction):
        passed += 1

    def test_power():
        r = engine.math.solve("2 alla seconda")
        return r["answer"] == 4.0

    total += 1
    if run_test("Potenza", test_power):
        passed += 1

    def test_sqrt():
        r = engine.math.solve("radice di 144")
        return r["answer"] == 12.0

    total += 1
    if run_test("Radice quadrata", test_sqrt):
        passed += 1

    def test_geometry():
        r = engine.math.solve("ipotenusa cateti 3 4")
        return abs(r["answer"] - 5.0) < 0.001

    total += 1
    if run_test("Pitagora", test_geometry):
        passed += 1

    print()

    # === RAGIONAMENTO ===
    print("[RAGIONAMENTO]")

    def test_deductive():
        engine.learn(
            "mammifero", examples=[], description="animale", category="biologia"
        )
        engine.learn(
            "animale", examples=[], description="essere vivente", category="biologia"
        )
        engine.learn("gatto", examples=[], description="mammifero", category="biologia")
        engine.knowledge.connect("gatto", "è_un_tipo_di", "mammifero")
        engine.knowledge.connect("mammifero", "è_un_tipo_di", "animale")
        result = engine.deductive.deduce("gatto")
        return "animale" in result.conclusion

    total += 1
    if run_test("Deduttivo", test_deductive):
        passed += 1

    def test_inductive():
        result = engine.inductive.induce_from_examples(
            [
                "il cane ha 4 zampe",
                "il gatto ha 4 zampe",
                "il cavallo ha 4 zampe",
            ]
        )
        return len(result.patterns) > 0

    total += 1
    if run_test("Induttivo", test_inductive):
        passed += 1

    def test_analogical():
        engine.learn("sole", examples=[], description="stella", category="astronomia")
        engine.learn(
            "nucleo", examples=[], description="centro atomo", category="fisica"
        )
        engine.learn(
            "sistema_solare",
            examples=[],
            description="sole con pianeti",
            category="astronomia",
        )
        engine.learn(
            "atomo", examples=[], description="nucleo con elettroni", category="fisica"
        )
        engine.knowledge.connect("sistema_solare", "ha_parte", "sole")
        engine.knowledge.connect("atomo", "ha_parte", "nucleo")
        result = engine.analogical.find_analogies("sistema_solare")
        return result.found

    total += 1
    if run_test("Analogico", test_analogical):
        passed += 1

    print()

    # === FINANZA ===
    print("[FINANZA]")

    def test_simple_interest():
        r = finance.calculate("simple_interest", principal=1000, rate=0.05, years=2)
        return r.result == 100.0

    total += 1
    if run_test("Interesse semplice", test_simple_interest):
        passed += 1

    def test_compound_interest():
        r = finance.calculate("compound_interest", principal=1000, rate=0.05, years=2)
        return abs(r.result - 1102.50) < 0.01

    total += 1
    if run_test("Interesse composto", test_compound_interest):
        passed += 1

    def test_roi():
        r = finance.calculate("roi", gain=15000, cost=10000)
        return r.result == 50.0

    total += 1
    if run_test("ROI", test_roi):
        passed += 1

    def test_mortgage():
        r = finance.calculate(
            "mortgage_payment", principal=200000, monthly_rate=0.003, months=360
        )
        return r.result > 0

    total += 1
    if run_test("Mutuo", test_mortgage):
        passed += 1

    def test_break_even():
        r = finance.calculate(
            "break_even", fixed_costs=10000, price=50, variable_cost=30
        )
        return r.result == 500.0

    total += 1
    if run_test("Break-even", test_break_even):
        passed += 1

    def test_risk_reward():
        r = finance.calculate(
            "risk_reward_ratio", potential_gain=300, potential_loss=100
        )
        return r.result == 3.0

    total += 1
    if run_test("Rischio/Rendimento", test_risk_reward):
        passed += 1

    print()

    # === NLP ===
    print("[NLP]")

    def test_nlp_math():
        from engine.nlp.parser import parse

        parsed = parse("quanto fa 5 + 3")
        return parsed.intent == "calculate"

    total += 1
    if run_test("Parsing matematico", test_nlp_math):
        passed += 1

    def test_nlp_define():
        from engine.nlp.parser import parse

        parsed = parse("cos'e un atomo?")
        return parsed.intent == "define"

    total += 1
    if run_test("Parsing definizione", test_nlp_define):
        passed += 1

    print()

    # === RIEPILOGO ===
    print("=" * 60)
    print(f"[RISULTATI] {passed}/{total} test passati ({passed / total * 100:.0f}%)")

    if passed == total:
        print("[SUCCESSO] TUTTI I TEST PASSATI!")
    else:
        print(f"[ATTENZIONE] {total - passed} test falliti")

    print("=" * 60)


if __name__ == "__main__":
    main()
