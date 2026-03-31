"""
Demo Fase 6 — Persistenza.

Testa: salva → distruggi → ricarica → verifica che tutto sia tornato.
"""

from engine import ReasoningEngine
from engine.persistence import Persistence
import tempfile
import os


def main():
    print("=" * 60)
    print("💾 ReasoningEngine — Fase 6: Persistenza")
    print("=" * 60)

    # Usa una directory temporanea per il test
    tmpdir = tempfile.mkdtemp()
    print(f"\n📁 Directory temporanea: {tmpdir}")

    # ============================================================
    # STEP 1: Crea e popola un engine
    # ============================================================
    print("\n🔧 STEP 1: Creo e popolo un engine...")

    engine = ReasoningEngine()

    # Insegna concetti
    engine.learn("gatto", ["miao", "4 zampe", "peloso"], "felino domestico", "biologia")
    engine.learn("cane", ["bau", "4 zampe", "fedele"], "mammifero domestico", "biologia")
    engine.learn("7", ["7 cose"], "il sette", "math/numbers")
    engine.learn("8", ["8 cose"], "l'otto", "math/numbers")

    # Aggiungi relazioni
    engine.knowledge.add("mammifero", category="biologia")
    engine.knowledge.add("animale", category="biologia")
    engine.knowledge.connect("gatto", "è_un_tipo_di", "mammifero")
    engine.knowledge.connect("cane", "è_un_tipo_di", "mammifero")
    engine.knowledge.connect("mammifero", "è_un_tipo_di", "animale")
    engine.knowledge.connect("animale", "ha_caratteristica", "si_muove")
    engine.knowledge.connect("mammifero", "ha_caratteristica", "allatta")

    # Testa
    r = engine.reason("quanto fa 7 + 8?")
    print(f"   Test: 7 + 8 = {r['answer']} ✅")

    r = engine.reason("il gatto è un animale?")
    print(f"   Test: gatto è animale? {r['answer']} ✅")

    info = engine.what_do_you_know()
    print(f"   Concetti: {info['stats']['total_concepts']}")
    print(f"   Regole: {info['stats']['total_rules']}")

    # ============================================================
    # STEP 2: Salva
    # ============================================================
    print("\n💾 STEP 2: Salvo lo stato...")

    filepath = engine.save("test_engine", tmpdir)
    print(f"   Salvato in: {filepath}")

    # Salva anche come testo
    text_export = engine.export_text()
    text_path = os.path.join(tmpdir, "export.txt")
    with open(text_path, "w") as f:
        f.write(text_export)
    print(f"   Export testo: {text_path}")

    # ============================================================
    # STEP 3: Distruggi l'engine
    # ============================================================
    print("\n💥 STEP 3: Distruggo l'engine...")

    engine2 = ReasoningEngine()
    info2 = engine2.what_do_you_know()
    print(f"   Nuovo engine - Concetti: {info2['stats']['total_concepts']}")
    print(f"   Nuovo engine - Regole: {info2['stats']['total_rules']}")

    r = engine2.reason("il gatto è un animale?")
    print(f"   Test: gatto è animale? → {r['answer'] or 'non sa'} ❌ (come previsto)")

    # ============================================================
    # STEP 4: Ricarica
    # ============================================================
    print("\n📂 STEP 4: Ricarico da disco...")

    loaded = engine2.load("test_engine", tmpdir)
    print(f"   Caricato: {loaded}")

    info3 = engine2.what_do_you_know()
    print(f"   Concetti dopo load: {info3['stats']['total_concepts']}")
    print(f"   Regole dopo load: {info3['stats']['total_rules']}")

    # ============================================================
    # STEP 5: Verifica integrità
    # ============================================================
    print("\n✅ STEP 5: Verifica integrità...")

    checks = []

    # Check 1: 7 + 8 = 15
    r = engine2.reason("quanto fa 7 + 8?")
    ok = r["answer"] == 15.0 and r["verified"]
    checks.append(("7 + 8 = 15", ok))
    print(f"   {'✅' if ok else '❌'} 7 + 8 = {r['answer']}")

    # Check 2: gatto è animale (deduzione)
    r = engine2.reason("il gatto è un animale?")
    ok = r["answer"] is not None and "animale" in str(r["answer"])
    checks.append(("gatto → animale", ok))
    print(f"   {'✅' if ok else '❌'} gatto è animale: {r['answer']}")

    # Check 3: gatto ha descrizione
    gatto = engine2.knowledge.get("gatto")
    ok = gatto is not None and "felino" in gatto.description
    checks.append(("gatto description", ok))
    print(f"   {'✅' if ok else '❌'} gatto: {gatto.description if gatto else 'N/A'}")

    # Check 4: relazioni
    ok = gatto and "mammifero" in gatto.relations.get("è_un_tipo_di", [])
    checks.append(("gatto → mammifero", ok))
    print(f"   {'✅' if ok else '❌'} gatto → mammifero")

    # Check 5: geometria (regole built-in)
    r = engine2.reason("area cerchio raggio 5")
    ok = r["answer"] is not None and abs(r["answer"] - 78.54) < 0.1
    checks.append(("area cerchio", ok))
    print(f"   {'✅' if ok else '❌'} area cerchio raggio 5 = {r['answer']}")

    # Check 6: apprendimento LLM persistente (se c'è)
    if engine2.learner.learning_history:
        ok = len(engine2.learner.learning_history) >= 2
        checks.append(("learning history", ok))
        print(f"   {'✅' if ok else '❌'} learning history: {len(engine2.learner.learning_history)} entries")

    # ============================================================
    # STEP 6: Lista salvataggi
    # ============================================================
    print("\n📋 STEP 6: Lista salvataggi...")

    p = Persistence(tmpdir)
    saves = p.list_saves()
    for s in saves:
        print(f"   • {s['name']}: {s['concepts']} concetti, {s['size_kb']} KB, salvato {s['saved_at'][:19]}")

    # ============================================================
    # RISULTATO
    # ============================================================
    passed = sum(1 for _, ok in checks if ok)
    total = len(checks)

    print(f"\n{'='*60}")
    print(f"📊 Risultati: {passed}/{total} verifiche passate")

    if passed == total:
        print("🎉 Persistenza funziona perfettamente!")
    else:
        print("⚠️ Alcune verifiche fallite")
    print(f"{'='*60}")

    # Pulizia
    import shutil
    shutil.rmtree(tmpdir)
    print(f"\n🧹 Directory temporanea pulita")


if __name__ == "__main__":
    main()
