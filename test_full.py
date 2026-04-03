import sys, time
sys.path.insert(0, '.')

from engine import ReasoningEngine
from engine.knowledge_graph import KnowledgeGraph
from engine.rule_engine import RuleEngine
from engine.deductive import DeductiveReasoner
from engine.analogical import AnalogicalReasoner
from engine.finance_module import FinanceModule

kg = KnowledgeGraph()
re = RuleEngine()
engine = ReasoningEngine()
ded = DeductiveReasoner(kg, re)
ana = AnalogicalReasoner(kg)
fin = FinanceModule(kg, re)

# Preload some knowledge for deductive reasoning
kg.add("gatto", "animale", "categoria", [("è_un", "mammifero"), ("tipo", "felino")])
kg.add("mammifero", "categoria", "biologia", [("ha_caratteristica", "allatta i piccoli")])
kg.add("Felix", "un gatto", "individuo", [("è_un", "gatto")])
kg.add("rame", "metallo", "chimica", [("è_un", "metallo"), ("conduce", "elettricità")])
kg.add("metallo", "categoria", "chimica", [("conduce", "elettricità")])

# Preload for analogical
kg.add("sole", "stella che illumina il giorno", "astronomia", [("illumina", "giorno"), ("tipo", "stella")])
kg.add("giorno", "periodo illuminato dal sole", "tempo", [])
kg.add("luna", "satellite che illumina la notte", "astronomia", [("illumina", "notte"), ("tipo", "satellite")])
kg.add("notte", "periodo illuminato dalla luna", "tempo", [])

tests = []

# === ENGINE (reason) ===
print("=" * 100)
print("REASONING ENGINE (reason method)")
print("=" * 100)

engine_qs = [
    ("25 * 47", "math"),
    ("radice quadrata di 1024", "math"),
    ("18% di 350", "math"),
    ("volume sfera raggio 7", "math"),
    ("area cerchio raggio 5", "math"),
    ("5 fattoriale", "math"),
    ("interesse semplice: 5000 euro al 4% per 3 anni", "finance"),
]

for q, cat in engine_qs:
    start = time.time()
    r = engine.reason(q)
    elapsed = time.time() - start
    ans = str(r.get('answer', 'N/A'))[:45]
    conf = "{:.0%}".format(r.get('confidence', 0))
    ver = "OK" if r.get('verified') else "FAIL"
    print("  [{:<8}] {:<48} -> {:<45} conf:{:>5} {}  {:.3f}s".format(cat, q, ans, conf, ver, elapsed))
    tests.append((cat, q, ans, conf, ver, elapsed))

# === DEDUCTIVE ===
print()
print("=" * 100)
print("DEDUCTIVE REASONER")
print("=" * 100)

start = time.time()
r = ded.deduce("Felix", "ha_caratteristica")
elapsed = time.time() - start
print("  Felix -> ha_caratteristica: {} (confidence: {:.0%}) {:.3f}s".format(r.conclusion, r.confidence, elapsed))
tests.append(("deductive", "Felix->prop", str(r.conclusion), "{:.0%}".format(r.confidence), "OK", elapsed))

start = time.time()
r = ded.query("il rame conduce elettricità?")
elapsed = time.time() - start
print("  rame conduce?: {} (confidence: {:.0%}) {:.3f}s".format(r.conclusion, r.confidence, elapsed))
tests.append(("deductive", "rame conduce?", str(r.conclusion), "{:.0%}".format(r.confidence), "OK", elapsed))

start = time.time()
r = ded.deduce("gatto")
elapsed = time.time() - start
print("  gatto -> tutto: {} (confidence: {:.0%}) {:.3f}s".format(r.conclusion, r.confidence, elapsed))
tests.append(("deductive", "gatto->all", str(r.conclusion)[:45], "{:.0%}".format(r.confidence), "OK", elapsed))

# === ANALOGICAL ===
print()
print("=" * 100)
print("ANALOGICAL REASONER")
print("=" * 100)

start = time.time()
r = ana.find_analogies("sole", max_results=3)
elapsed = time.time() - start
print("  Analogie per 'sole':")
if r.analogies:
    for a in r.analogies:
        print("    {} <-> {} (score: {:.0%})".format(a.source_concept, a.target_concept, a.similarity_score))
else:
    print("    Nessuna trovata")
print("  {:.3f}s".format(elapsed))
tests.append(("analogical", "sole analogies", str(len(r.analogies)) + " trovate", "N/A", "OK" if r.analogies else "PARTIAL", elapsed))

# === FINANCE ===
print()
print("=" * 100)
print("FINANCE MODULE")
print("=" * 100)

start = time.time()
r = fin.calculate("simple_interest", principal=5000, rate=4, years=3)
elapsed = time.time() - start
print("  Interesse semplice 5000€ 4% 3anni: {} ({:.3f}s)".format(r, elapsed))
tests.append(("finance", "interesse semplice", str(r), "N/A", "OK", elapsed))

start = time.time()
r = fin.calculate("roi", investment=10000, returns=13500)
elapsed = time.time() - start
print("  ROI 10000->13500: {} ({:.3f}s)".format(r, elapsed))
tests.append(("finance", "ROI", str(r), "N/A", "OK", elapsed))

start = time.time()
r = fin.calculate("compound_interest", principal=1000, rate=7, years=30)
elapsed = time.time() - start
print("  Composto 1000€ 7% 30anni: {} ({:.3f}s)".format(r, elapsed))
tests.append(("finance", "composto", str(r), "N/A", "OK", elapsed))

# === SUMMARY ===
print()
print("=" * 100)
print("RIEPILOGO")
print("=" * 100)
print("{:<12} {:<22} {:<50} {:>8} {:>6}".format("CATEGORIA", "QUERY", "RISULTATO", "TEMPO", "STATO"))
print("-" * 100)
for cat, q, ans, conf, status, elapsed in tests:
    print("{:<12} {:<22} {:<50} {:>7.3f}s {:>6}".format(cat, q[:20], ans[:48], elapsed, status))

total = sum(t[5] for t in tests)
ok = sum(1 for t in tests if t[4] == "OK")
print()
print("Totale: {} test, {} OK, tempo totale: {:.3f}s, media: {:.3f}s".format(len(tests), ok, total, total/len(tests)))
