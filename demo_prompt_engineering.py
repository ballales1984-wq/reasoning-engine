#!/usr/bin/env python3
"""
Demo PromptBuilder + PromptOptimizer — Prompt Engineering avanzato.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import ReasoningEngine
from engine.prompt_engineering import PromptBuilder, PromptOptimizer, PromptStyle, ReasoningType, ModelTarget


def main():
    print("=" * 60)
    print("📝 PromptBuilder + PromptOptimizer")
    print("=" * 60)
    print()
    
    engine = ReasoningEngine()
    builder = PromptBuilder(engine)
    optimizer = PromptOptimizer(engine)
    
    # === TEST 1: PROMPT SEMPLICE ===
    print("1️⃣ PROMPT SEMPLICE")
    print("-" * 40)
    
    result = builder.build(
        task="Spiega cos'è l'interesse composto",
        style=PromptStyle.SIMPLE,
        reasoning_type=ReasoningType.CHAIN_OF_THOUGHT
    )
    
    print(result.prompt[:500])
    print("...")
    print(f"Token stimati: {result.tokens_estimate}")
    print()
    
    # === TEST 2: PROMPT CON FEW-SHOT ===
    print("2️⃣ PROMPT CON FEW-SHOT")
    print("-" * 40)
    
    # Insegna concetti all'engine
    engine.learn("interesse_composto", 
                 examples=["1000€ al 5% per 2 anni = 1102.50€"],
                 description="Interesse su interesse")
    
    result = builder.build(
        task="Calcola il rendimento di un investimento di 5000€ al 7% per 10 anni",
        style=PromptStyle.STEP_BY_STEP,
        reasoning_type=ReasoningType.CHAIN_OF_THOUGHT,
        add_fewshot=True,
        template_name="zero_shot"  # Usa zero-shot invece di financial
    )
    
    print(result.prompt[:500])
    print("...")
    print(f"Token stimati: {result.tokens_estimate}")
    print()
    
    # === TEST 3: PROMPT FINANZARIO ===
    print("3️⃣ PROMPT FINANZARIO")
    print("-" * 40)
    
    result = builder.build(
        task="Analizza se conviene investire in azioni o obbligazioni",
        style=PromptStyle.TECHNICAL,
        template_name="financial",
        formula="ROI = (Guadagno - Costo) / Costo × 100",
        data="Azioni: ROI medio 10%, volatilità alta. Obbligazioni: ROI medio 4%, volatilità bassa."
    )
    
    print(result.prompt[:500])
    print("...")
    print()
    
    # === TEST 4: PROMPT CODING ===
    print("4️⃣ PROMPT CODING")
    print("-" * 40)
    
    result = builder.build(
        task="Scrivi una funzione Python che calcola l'interesse composto",
        style=PromptStyle.TECHNICAL,
        template_name="coding",
        requirements="- Input: capitale, tasso, anni\n- Output: valore finale\n- Gestisci errori",
        constraints="- Solo Python standard library\n- Type hints",
        code_style="Clean code, PEP8"
    )
    
    print(result.prompt[:500])
    print("...")
    print()
    
    # === TEST 5: PROMPT ANALOGICO ===
    print("5️⃣ PROMPT ANALOGICO")
    print("-" * 40)
    
    result = builder.build(
        task="Spiega cos'è un'opzione finanziaria usando analogie",
        style=PromptStyle.ANALOGICAL,
        reasoning_type=ReasoningType.ANALOGICAL,
        template_name="analogical"  # Forza template analogico
    )
    
    print(result.prompt[:500])
    print("...")
    print()
    
    # === TEST 6: PROMPT TREE-OF-THOUGHT ===
    print("6️⃣ PROMPT TREE-OF-THOUGHT")
    print("-" * 40)
    
    result = builder.build(
        task="Quale approccio è migliore per imparare la matematica?",
        style=PromptStyle.CREATIVE,
        reasoning_type=ReasoningType.TREE_OF_THOUGHT,
        template_name="tree_of_thought"
    )
    
    print(result.prompt[:500])
    print("...")
    print()
    
    # === TEST 7: PROMPT PER CLAUDE ===
    print("7️⃣ PROMPT PER CLAUDE 3.5")
    print("-" * 40)
    
    result = builder.build(
        task="Spiega il modello Black-Scholes per le opzioni",
        style=PromptStyle.TEACHER,
        reasoning_type=ReasoningType.CHAIN_OF_THOUGHT,
        model_target=ModelTarget.CLAUDE_35,
        add_fewshot=True,
        template_name="chain_of_thought",
        formula="C = S*N(d1) - K*e^(-rT)*N(d2)",
        data="S=100, K=105, T=1, r=0.05, σ=0.2"
    )
    
    print(result.prompt[:500])
    print("...")
    print(f"Modello target: {result.model_target.value}")
    print()
    
    # === TEST 8: OTTIMIZZAZIONE ===
    print("8️⃣ OTTIMIZZAZIONE PROMPT")
    print("-" * 40)
    
    mio_prompt = "Dimmi di black scholes"
    
    ottimizzato = optimizer.optimize(
        prompt=mio_prompt,
        goal="massima chiarezza per non-esperti",
        iterations=2,
        check_with_verifier=True
    )
    
    print(f"Originale: {ottimizzato['original_prompt']}")
    print(f"Ottimizzato: {ottimizzato['optimized_prompt'][:300]}...")
    print(f"Miglioramenti: {len(ottimizzato['improvements'])}")
    for imp in ottimizzato['improvements']:
        print(f"  • {imp['description']}")
    print()
    
    # === TEMPLATE DISPONIBILI ===
    print("📋 TEMPLATE DISPONIBILI")
    print("-" * 40)
    
    for template in builder.list_templates():
        print(f"  • {template['name']}: {template['description']}")
    
    print()
    
    # === RIEPILOGO ===
    print("=" * 60)
    print("🎯 PROMPT ENGINEERING INTEGRATO:")
    print()
    print("  ✅ 8 template (zero-shot, few-shot, CoT, ToT, socratico, analogico, financial, coding)")
    print("  ✅ 8 stili (semplice, tecnico, creativo, step-by-step, etc.)")
    print("  ✅ 6 tipi ragionamento (CoT, ToT, deduttivo, induttivo, analogico, socratico)")
    print("  ✅ 9 modelli target (Claude, GPT, Llama, Mistral, Grok, Gemini)")
    print("  ✅ PromptOptimizer con Verifier")
    print("  ✅ Integrazione KnowledgeGraph + Learner")
    print("  ✅ Memoria prompt che funzionano")
    print("=" * 60)


if __name__ == "__main__":
    main()
