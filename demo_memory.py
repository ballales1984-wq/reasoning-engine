#!/usr/bin/env python3
"""
Demo del MemoryModule — Memoria completa.

Esegui: python demo_memory.py
"""

from engine.memory import MemoryModule


def main():
    print("=" * 60)
    print("🧠 MemoryModule — Memoria completa")
    print("=" * 60)
    print()
    
    memory = MemoryModule(max_working_memory=5)
    
    # === MEMORIA SEMANTICA ===
    print("📚 MEMORIA SEMANTICA (conoscenza generale)")
    print("-" * 40)
    
    id1 = memory.remember(
        "I gatti sono mammiferi domestici",
        memory_type="semantic",
        tags=["animali", "biologia", "gatti"],
        importance=0.8
    )
    print(f"  Memorizzato: I gatti sono mammiferi (id: {id1})")
    
    id2 = memory.remember(
        "I mammiferi sono animali a sangue caldo",
        memory_type="semantic",
        tags=["animali", "biologia", "mammiferi"],
        importance=0.9
    )
    print(f"  Memorizzato: I mammiferi sono a sangue caldo (id: {id2})")
    
    # Associa i due concetti
    memory.associate(id1, id2)
    print(f"  Associati: gatti ↔ mammiferi")
    print()
    
    # === MEMORIA EPISODICA ===
    print("📅 MEMORIA EPISODICA (eventi specifici)")
    print("-" * 40)
    
    id3 = memory.remember(
        "Oggi ho imparato che 2+3=5",
        memory_type="episodic",
        tags=["matematica", "apprendimento", "addizione"],
        importance=0.6,
        metadata={"date": "2026-03-31", "source": "demo"}
    )
    print(f"  Memorizzato: evento di apprendimento (id: {id3})")
    
    id4 = memory.remember(
        "Ho sbagliato 6+9=14, la risposta corretta è 15",
        memory_type="episodic",
        tags=["matematica", "errore", "correzione"],
        importance=0.7
    )
    print(f"  Memorizzato: errore e correzione (id: {id4})")
    print()
    
    # === MEMORIA PROCEDURALE ===
    print("🔧 MEMORIA PROCEDURALE (abilità)")
    print("-" * 40)
    
    id5 = memory.remember(
        "Per fare un'addizione: prendi il primo numero, aggiungi il secondo",
        memory_type="procedural",
        tags=["matematica", "procedura", "addizione"],
        importance=0.9
    )
    print(f"  Memorizzato: procedura addizione (id: {id5})")
    print()
    
    # === WORKING MEMORY ===
    print("💭 WORKING MEMORY (cosa sto pensando ora)")
    print("-" * 40)
    
    memory.remember("Sto pensando alla matematica", memory_type="working", tags=["focus"])
    memory.remember("Devo risolvere 15 + 27", memory_type="working", tags=["task"])
    memory.remember("Forse devo usare l'addizione", memory_type="working", tags=["ipotesi"])
    
    context = memory.get_context()
    print(f"  Focus: {context['focus']}")
    print(f"  Working memory: {len(context['working_memory'])} elementi")
    for item in memory.working_memory:
        print(f"    • {item.content}")
    print()
    
    # === RICERCA ===
    print("🔍 RICERCA NELLA MEMORIA")
    print("-" * 40)
    
    results = memory.recall("gatti")
    print(f"  Ricerca 'gatti': {len(results)} risultati")
    for r in results:
        print(f"    • [{r.memory_type}] {r.content}")
    print()
    
    results = memory.recall("matematica")
    print(f"  Ricerca 'matematica': {len(results)} risultati")
    for r in results:
        print(f"    • [{r.memory_type}] {r.content}")
    print()
    
    # === MEMORIE ASSOCIATE ===
    print("🔗 MEMORIE ASSOCIATE")
    print("-" * 40)
    
    associated = memory.recall_associated(id1)
    print(f"  Associato a 'gatti sono mammiferi':")
    for a in associated:
        print(f"    • {a.content}")
    print()
    
    # === RAFFORZAMENTO ===
    print("💪 RAFFORZAMENTO MEMORIA")
    print("-" * 40)
    
    item = memory._get_item_by_id(id3)
    print(f"  Prima: importanza = {item.importance:.1%}")
    
    memory.strengthen(id3, amount=0.2)
    item = memory._get_item_by_id(id3)
    print(f"  Dopo 3 accessi: importanza = {item.importance:.1%}")
    print()
    
    # === CONSOLIDAMENTO ===
    print("📦 CONSOLIDAMENTO (working → lungo termine)")
    print("-" * 40)
    
    # Riempi la working memory oltre il limite
    for i in range(8):
        memory.remember(
            f"Elemento temporaneo {i}",
            memory_type="working",
            tags=["temp"],
            importance=0.3
        )
    
    stats = memory.get_stats()
    print(f"  Working memory: {stats['working_memory']}")
    print(f"  Episodic: {stats['episodic_memory']}")
    print(f"  Semantic: {stats['semantic_memory']}")
    print(f"  Consolidamenti: {stats['consolidations']}")
    print()
    
    # === ESPORTAZIONE ===
    print("💾 ESPORTAZIONE")
    print("-" * 40)
    
    exported = memory.export()
    print(f"  Elementi esportati: {exported['stats']['total_items']}")
    print(f"  Working: {exported['stats']['working_memory']}")
    print(f"  Episodic: {exported['stats']['episodic_memory']}")
    print(f"  Semantic: {exported['stats']['semantic_memory']}")
    print(f"  Procedural: {exported['stats']['procedural_memory']}")
    print()
    
    # === RIEPILOGO ===
    print("=" * 60)
    print("🎯 COSA SA FARE LA MEMORIA:")
    print()
    print("  ✅ Memoria semantica (conoscenza)")
    print("  ✅ Memoria episodica (eventi)")
    print("  ✅ Memoria procedurale (abilità)")
    print("  ✅ Working memory (pensiero corrente)")
    print("  ✅ Consolidamento automatico")
    print("  ✅ Ricerca per contenuto e tag")
    print("  ✅ Associazioni tra memorie")
    print("  ✅ Rafforzamento/debolezza")
    print("  ✅ Esportazione/importazione")
    print("=" * 60)


if __name__ == "__main__":
    main()
