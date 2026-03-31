#!/usr/bin/env python3
"""
Demo completa — Architettura Claude Code integrata.

Esegui: python demo_claude_architecture.py
"""

from engine import ReasoningEngine
from engine.reasoning_loop import ReasoningLoop
from engine.context_manager import ContextManager, CompactionStrategy
from engine.state_manager import StateManager
from engine.prompt_builder import PromptBuilder
from engine.memory import MemoryModule


def main():
    print("=" * 60)
    print("🏗️ Architettura Claude Code — Demo Completa")
    print("=" * 60)
    print()
    
    # Inizializza tutti i componenti
    engine = ReasoningEngine()
    loop = ReasoningLoop(engine, max_turns=5)
    context = ContextManager(max_tokens=10000)
    state = StateManager()
    prompt = PromptBuilder()
    memory = MemoryModule(max_working_memory=5)
    
    # === TEST 1: Reasoning Loop ===
    print("🔄 REASONING LOOP (come query.ts)")
    print("-" * 40)
    
    state.set_question("quanto fa 12 * 8?")
    
    for event in loop.run("quanto fa 12 * 8?"):
        if event.type == "thought":
            print(f"  💭 {event.content}")
        elif event.type == "tool_call":
            state.increment_tool_calls()
            print(f"  🔧 {event.content['tool']}")
        elif event.type == "answer":
            state.set_confidence(event.confidence)
            state.mark_complete()
            print(f"  ✅ Risposta: {event.content}")
            print(f"  📊 Confidenza: {event.confidence:.0%}")
    
    print()
    
    # === TEST 2: Context Manager ===
    print("📦 CONTEXT MANAGER (gestione contesto)")
    print("-" * 40)
    
    # Simula messaggi
    messages = [
        {"role": "system", "content": "Sei un assistente"},
        {"role": "user", "content": "quanto fa 2+2?"},
        {"role": "assistant", "content": "4"},
        {"role": "user", "content": "e 3+3?"},
        {"role": "assistant", "content": "6"},
    ]
    
    pressure = context.get_pressure_level(messages)
    print(f"  Pressione: {pressure['level']}")
    print(f"  Token usati: {pressure['tokens_used']}/{context.max_tokens}")
    print(f"  Uso: {pressure['usage_percent']:.1f}%")
    
    # Simula compattazione
    if pressure["should_compact"]:
        print(f"  ⚠️ Serve compattare!")
        messages = context.compact(messages, CompactionStrategy.SUMMARIZE)
        print(f"  ✅ Compattato: {len(messages)} messaggi")
    else:
        print(f"  ✅ Contesto OK")
    
    print()
    
    # === TEST 3: State Manager ===
    print("📊 STATE MANAGER (gestione stato)")
    print("-" * 40)
    
    stats = state.get_stats()
    print(f"  Sessione: {stats['current_session']['id']}")
    print(f"  Turni: {stats['current_session']['turns']}")
    print(f"  Tool calls: {stats['current_session']['tool_calls']}")
    print(f"  Confidenza: {stats['current_session']['confidence']:.0%}")
    print(f"  Sessioni totali: {stats['global']['total_sessions']}")
    
    print()
    
    # === TEST 4: Prompt Builder ===
    print("📝 PROMPT BUILDER (assemblaggio prompt)")
    print("-" * 40)
    
    built_prompt = prompt.build()
    lines = built_prompt.split("\n")
    print(f"  Segmenti: {len(prompt.segments)}")
    print(f"  Righe prompt: {len(lines)}")
    print(f"  Prime 3 righe:")
    for line in lines[:3]:
        print(f"    {line}")
    
    print()
    
    # === TEST 5: Memory Integration ===
    print("🧠 MEMORY (integrazione)")
    print("-" * 40)
    
    memory.remember("12 * 8 = 96", memory_type="semantic", tags=["matematica"])
    memory.remember("Ho risolto moltiplicazione", memory_type="episodic", tags=["ragionamento"])
    
    results = memory.recall("moltiplicazione")
    print(f"  Memorizzato e richiamato: {len(results)} risultati")
    for r in results:
        print(f"    • [{r.memory_type}] {r.content}")
    
    print()
    
    # === RIEPILOGO ===
    print("=" * 60)
    print("🎯 ARCHITETTURA CLAUDE CODE INTEGRATA:")
    print()
    print("  ✅ Reasoning Loop (come query.ts)")
    print("  ✅ Tool System (10 tool)")
    print("  ✅ Context Manager (pressione + compaction)")
    print("  ✅ State Manager (bootstrap + reactive store)")
    print("  ✅ Prompt Builder (assemblaggio dinamico)")
    print("  ✅ Memory Module (4 tipi)")
    print("  ✅ Verification Layer")
    print("  ✅ Transition Tracking")
    print()
    print(f"  📊 Totale: {state.get_stats()['global']['total_reasoning_steps']} passi ragionamento")
    print("=" * 60)


if __name__ == "__main__":
    main()
