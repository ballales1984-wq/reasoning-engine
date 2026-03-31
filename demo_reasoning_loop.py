#!/usr/bin/env python3
"""
Demo del ReasoningLoop — architettura ispirata a Claude Code.

Esegui: python demo_reasoning_loop.py
"""

from engine import ReasoningEngine
from engine.reasoning_loop import ReasoningLoop, ReasoningEvent


def main():
    print("=" * 60)
    print("🔄 ReasoningLoop — Architettura Claude Code")
    print("=" * 60)
    print()
    
    engine = ReasoningEngine()
    loop = ReasoningLoop(engine, max_turns=5)
    
    # Aggiungi concetti per testare il ragionamento
    engine.learn('mammifero', examples=[], description='animale che allatta', category='biologia')
    engine.learn('animale', examples=[], description='essere vivente', category='biologia')
    engine.learn('gatto', examples=['miao'], description='mammifero domestico', category='biologia')
    engine.knowledge.connect('gatto', 'è_un_tipo_di', 'mammifero')
    engine.knowledge.connect('mammifero', 'è_un_tipo_di', 'animale')
    
    # === TEST 1: Matematica ===
    print("📐 TEST 1: Matematica")
    print("-" * 40)
    
    for event in loop.run("quanto fa 15 + 27?"):
        if event.type == "thought":
            print(f"  💭 {event.content}")
        elif event.type == "parsed":
            print(f"  🔍 Intent: {event.content['intent']}, Op: {event.content['operation']}")
        elif event.type == "tool_call":
            print(f"  🔧 Tool: {event.content['tool']}")
        elif event.type == "tool_result":
            print(f"  ✅ Risultato: {event.content}")
        elif event.type == "answer":
            print(f"  🎯 RISPOSTA: {event.content}")
            print(f"  📊 Confidenza: {event.confidence:.0%}")
            print(f"  🔄 Turni: {event.metadata['turns']}")
            print(f"  🔧 Tool usati: {event.metadata['tools_used']}")
        elif event.type == "verification":
            print(f"  ✔️ {event.content}")
        elif event.type == "terminal":
            print(f"  🏁 Terminale: {event.content}")
    
    print()
    
    # === TEST 2: Definizione ===
    print("📚 TEST 2: Definizione")
    print("-" * 40)
    
    for event in loop.run("cosa è un gatto?"):
        if event.type == "thought":
            print(f"  💭 {event.content}")
        elif event.type == "tool_call":
            print(f"  🔧 Tool: {event.content['tool']}")
        elif event.type == "tool_result":
            print(f"  ✅ Risultato: {event.content}")
        elif event.type == "answer":
            print(f"  🎯 RISPOSTA: {event.content}")
            print(f"  📊 Confidenza: {event.confidence:.0%}")
    
    print()
    
    # === TEST 3: Deduzione ===
    print("🧠 TEST 3: Deduzione")
    print("-" * 40)
    
    for event in loop.run("il gatto è un animale?"):
        if event.type == "thought":
            print(f"  💭 {event.content}")
        elif event.type == "tool_call":
            print(f"  🔧 Tool: {event.content['tool']}")
        elif event.type == "tool_result":
            print(f"  ✅ Risultato: {event.content}")
        elif event.type == "answer":
            print(f"  🎯 RISPOSTA: {event.content}")
            print(f"  📊 Confidenza: {event.confidence:.0%}")
    
    print()
    
    # === RIEPILOGO ===
    print("=" * 60)
    print("🎯 ARCHITETTURA (come Claude Code):")
    print()
    print("  ✅ Reasoning Loop (come query.ts)")
    print("  ✅ Tool System (10 tool registrati)")
    print("  ✅ Pre/Post processing")
    print("  ✅ Verification layer")
    print("  ✅ Transition tracking")
    print("  ✅ Event streaming")
    print("  ✅ Error recovery")
    print("=" * 60)


if __name__ == "__main__":
    main()
