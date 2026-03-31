#!/usr/bin/env python3
"""
Demo del ReasoningEngine — Modulo Finanziario.

Esegui: python demo_finance.py
"""

from engine import ReasoningEngine
from engine.finance_module import FinanceModule


def main():
    print("=" * 60)
    print("💰 ReasoningEngine — Demo Finanza")
    print("=" * 60)
    print()
    
    engine = ReasoningEngine()
    finance = FinanceModule(engine.knowledge, engine.rules)
    
    # === INTERESSE SEMPLICE ===
    print("💵 INTERESSE SEMPLICE")
    print("-" * 40)
    
    result = finance.calculate("simple_interest", principal=1000, rate=0.05, years=2)
    print(f"  {result.explanation}")
    print()
    
    result = finance.calculate("simple_interest", principal=5000, rate=0.03, years=10)
    print(f"  {result.explanation}")
    print()
    
    # === INTERESSE COMPOSTO ===
    print("📈 INTERESSE COMPOSTO")
    print("-" * 40)
    
    result = finance.calculate("compound_interest", principal=1000, rate=0.05, years=2)
    print(f"  {result.explanation}")
    print()
    
    result = finance.calculate("compound_interest", principal=1000, rate=0.07, years=30)
    print(f"  {result.explanation}")
    print(f"  💡 Con 1000€ al 7% per 30 anni, avrai {result.result:.2f}€!")
    print()
    
    # === ROI ===
    print("📊 ROI (Return on Investment)")
    print("-" * 40)
    
    result = finance.calculate("roi", gain=15000, cost=10000)
    print(f"  {result.explanation}")
    print()
    
    result = finance.calculate("roi", gain=8000, cost=10000)
    print(f"  {result.explanation}")
    print(f"  ⚠️ ROI negativo! Hai perso il {abs(result.result):.1f}%")
    print()
    
    # === MUTUO ===
    print("🏠 CALCOLO MUTUO")
    print("-" * 40)
    
    result = finance.calculate("mortgage_payment", principal=200000, monthly_rate=0.003, months=360)
    print(f"  {result.explanation}")
    print()
    
    result = finance.calculate("mortgage_payment", principal=150000, monthly_rate=0.0025, months=240)
    print(f"  {result.explanation}")
    print()
    
    # === MARGINE DI PROFITTO ===
    print("💎 MARGINE DI PROFITTO")
    print("-" * 40)
    
    result = finance.calculate("profit_margin", revenue=50000, cost=35000)
    print(f"  {result.explanation}")
    print()
    
    result = finance.calculate("profit_margin", revenue=100000, cost=95000)
    print(f"  {result.explanation}")
    print(f"  ⚠️ Margine basso! Solo il {result.result:.1f}%")
    print()
    
    # === BREAK-EVEN ===
    print("⚖️ PUNTO DI PAREGGIO")
    print("-" * 40)
    
    result = finance.calculate("break_even", fixed_costs=10000, price=50, variable_cost=30)
    print(f"  {result.explanation}")
    print()
    
    # === RISCHIO/RENDIMENTO ===
    print("🎲 RAPPORTO RISCHIO/RENDIMENTO")
    print("-" * 40)
    
    result = finance.calculate("risk_reward_ratio", potential_gain=300, potential_loss=100)
    print(f"  {result.explanation}")
    print()
    
    result = finance.calculate("risk_reward_ratio", potential_gain=150, potential_loss=200)
    print(f"  {result.explanation}")
    print(f"  ⚠️ Non conviene! Rischio più del guadagno potenziale")
    print()
    
    # === CONFRONTO INVESTIMENTI ===
    print("🔍 CONFRONTO: Interesse Semplice vs Composto")
    print("-" * 40)
    
    capitale = 10000
    tasso = 0.05
    anni = 20
    
    simple = finance.calculate("simple_interest", principal=capitale, rate=tasso, years=anni)
    compound = finance.calculate("compound_interest", principal=capitale, rate=tasso, years=anni)
    
    print(f"  Capitale: {capitale}€ | Tasso: {tasso*100}% | Anni: {anni}")
    print(f"  Semplice: {capitale}€ + {simple.result:.2f}€ = {capitale + simple.result:.2f}€")
    print(f"  Composto: {compound.result:.2f}€")
    print(f"  Differenza: {compound.result - (capitale + simple.result):.2f}€ in più con il composto!")
    print()
    
    # === CONCETTI FINANZIARI ===
    print("📚 CONCETTI FINANZIARI REGISTRATI")
    print("-" * 40)
    
    info = engine.what_do_you_know()
    finance_concepts = [c for c in info['concepts'] if 'finance' in c.get('category', '')]
    
    for concept in finance_concepts:
        print(f"  • {concept['name']}: {concept['description'][:60]}...")
    
    print()
    print("=" * 60)
    print(f"📊 Totale: {len(finance_concepts)} concetti finanziari + {len(engine.rules.list_all())} regole")
    print("=" * 60)
    print()
    print("🎉 Demo Finanza completata!")


if __name__ == "__main__":
    main()
