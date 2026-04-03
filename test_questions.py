import sys, time
sys.path.insert(0, '.')
from engine import ReasoningEngine

engine = ReasoningEngine()

questions = [
    # Math
    ("quanto fa 25 * 47?", "math"),
    ("radice quadrata di 1024", "math"),
    ("calcola il 18% di 350", "math"),
    ("volume di una sfera raggio 7", "math"),
    # Deductive reasoning
    ("tutti i gatti sono mammiferi, Felix è un gatto, quindi Felix è", "deductive"),
    ("se tutti i metalli conducono elettricità e il rame è un metallo, il rame conduce?", "deductive"),
    # Analogical
    ("sole sta a giorno come luna sta a", "analogical"),
    # Finance
    ("interesse semplice: 5000 euro al 4% per 3 anni", "finance"),
    ("ROI: investiti 10000 guadagnati 13500", "finance"),
    # Knowledge
    ("cosa è un atomo?", "knowledge"),
    # Edge cases
    ("quanto fa 0 elevato alla -1?", "edge"),
    ("se A > B e B > C, A > C?", "edge"),
]

header = "{:<55} {:<12} {:<42} {:>10} {:>8}".format("DOMANDA", "TIPO", "RISPOSTA", "CONFIDENZA", "TEMPO")
print(header)
print("-" * 130)

results = []

for q, qtype in questions:
    start = time.time()
    try:
        result = engine.reason(q)
        elapsed = time.time() - start
        answer = str(result.get('answer', 'N/A'))[:40]
        conf = "{:.0%}".format(result.get('confidence', 0))
        method = "verified" if result.get('verified') else "unverified"
    except Exception as e:
        elapsed = time.time() - start
        answer = "ERRORE: {}".format(str(e)[:30])
        conf = "N/A"
        method = "error"
    row = "{:<55} {:<12} {:<42} {:>10} {:>7.2f}s".format(q[:53], qtype, answer, conf, elapsed)
    print(row)
    results.append((q, qtype, answer, conf, elapsed, method))

print()
print("=" * 130)
print("STATISTICHE:")
total_time = sum(r[4] for r in results)
avg_time = total_time / len(results)
fastest = min(results, key=lambda r: r[4])
slowest = max(results, key=lambda r: r[4])
print("  Domande totali: {}".format(len(results)))
print("  Tempo totale: {:.2f}s".format(total_time))
print("  Tempo medio: {:.2f}s".format(avg_time))
print("  Più veloce: {:.2f}s - {}".format(fastest[4], fastest[0][:50]))
print("  Più lenta:  {:.2f}s - {}".format(slowest[4], slowest[0][:50]))
print()
print("DETTAGLIO METODI:")
for q, qtype, answer, conf, elapsed, method in results:
    print("  [{:<12}] {} -> {} (conf: {})".format(qtype, q[:45], method, conf))
