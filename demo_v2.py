#!/usr/bin/env python3
"""
Demo completa — ReasoningEngine v2 con architettura Claude Code.
"""

import sys
import os

# Aggiungi il path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importa dalla struttura v2
from engine.core import ReasoningEngine
from engine.core.loop import ReasoningLoop
from engine.core.state import StateManager
from engine.core.context import ContextManager, CompactionStrategy
from engine.tools import ToolRegistry, Tool
from engine.memory import MemorySystem
from engine.permissions import PermissionChecker, PermissionLevel
from engine.persistence import Storage


def main():
    print("=" * 60)
    print("🚀 ReasoningEngine v2 — Architettura Claude Code")
    print("=" * 60)
    print()
    
    # Inizializza tutti i sistemi
    engine = ReasoningEngine()
    state = StateManager()
    context = ContextManager(max_tokens=10000)
    memory = MemorySystem(max_working=10)
    permissions = PermissionChecker()
    storage = Storage("./data")
    
    # === TEST 1: MOTORE PRINCIPALE ===
    print("🧠 MOTORE PRINCIPALE")
    print("-" * 40)
    
    # Matematica
    result = engine.reason("quanto fa 15 + 27?")
    print(f"  15 + 27 = {result['answer']}")
    print(f"  Confidenza: {result['confidence']:.0%}")
    print(f"  Turni: {result['turns']}")
    print()
    
    # Geometria
    result = engine.reason("area cerchio raggio 5")
    r = engine.math.solve("area cerchio raggio 5")
    print(f"  Area cerchio (r=5): {r['answer']:.4f}")
    print()
    
    # === TEST 2: STATE MANAGER ===
    print("📊 STATE MANAGER")
    print("-" * 40)
    
    state.set_question("test domanda")
    state.increment_turns()
    state.increment_tool_calls()
    state.set_confidence(0.95)
    
    stats = state.get_stats()
    print(f"  Sessione: {stats['current_session']['id']}")
    print(f"  Turni: {stats['current_session']['turns']}")
    print(f"  Confidenza: {stats['current_session']['confidence']:.0%}")
    print()
    
    # === TEST 3: CONTEXT MANAGER ===
    print("📦 CONTEXT MANAGER")
    print("-" * 40)
    
    messages = [{"role": "user", "content": "test " * 100}]
    pressure = context.get_pressure_level(messages)
    print(f"  Pressione: {pressure['level']}")
    print(f"  Token: {pressure['tokens_used']}")
    print()
    
    # === TEST 4: MEMORY SYSTEM ===
    print("🧠 MEMORY SYSTEM")
    print("-" * 40)
    
    memory.remember("15 + 27 = 42", memory_type="semantic", tags=["matematica"])
    memory.remember("Ho imparato addizione", memory_type="episodic", tags=["apprendimento"])
    
    results = memory.recall("addizione")
    print(f"  Memorie richiamate: {len(results)}")
    for r in results:
        print(f"    • [{r.memory_type}] {r.content}")
    print()
    
    # === TEST 5: PERMISSIONS ===
    print("🔐 PERMISSIONS")
    print("-" * 40)
    
    permissions.set_permission("math_solve", PermissionLevel.EXECUTE)
    permissions.set_permission("llm_query", PermissionLevel.WRITE)
    permissions.block("dangerous_tool")
    
    print(f"  math_solve (execute): {permissions.check('math_solve', PermissionLevel.EXECUTE)}")
    print(f"  dangerous_tool: {permissions.check('dangerous_tool', PermissionLevel.READ)}")
    print()
    
    # === TEST 6: STORAGE ===
    print("💾 STORAGE")
    print("-" * 40)
    
    storage.save("test", {"data": "hello", "value": 42})
    loaded = storage.load("test")
    print(f"  Salvato e caricato: {loaded}")
    print()
    
    # === TEST 7: REASONING LOOP ===
    print("🔄 REASONING LOOP")
    print("-" * 40)
    
    loop = ReasoningLoop(engine, max_turns=3)
    
    for event in loop.run("quanto fa 8 × 7?"):
        if event.type == "thought":
            print(f"  💭 {event.content}")
        elif event.type == "tool_call":
            print(f"  🔧 {event.content['tool']}")
        elif event.type == "answer":
            print(f"  ✅ Risposta: {event.content}")
            print(f"  📊 Confidenza: {event.confidence:.0%}")
            break
    
    print()
    
    # === RIEPILOGO ===
    print("=" * 60)
    print("🎯 ARCHITETTURA CLAUDE CODE — TUTTI I SISTEMI:")
    print()
    print("  ✅ Core Engine (motore principale)")
    print("  ✅ Reasoning Loop (come query.ts)")
    print("  ✅ State Manager (bootstrap + reactive)")
    print("  ✅ Context Manager (pressione + compaction)")
    print("  ✅ Memory System (4 tipi)")
    print("  ✅ Tool Registry")
    print("  ✅ Permission System")
    print("  ✅ Storage/Persistence")
    print()
    print(f"  📊 Moduli: 23+")
    print(f"  📊 Righe: 8.000+")
    print("=" * 60)


if __name__ == "__main__":
    main()
