"""
Menu per Question-Based Reasoner

Permette di:
- Scegliere un dominio (animali, diagnosi, ecc.)
- Definire ipotesi iniziali
- Rispondere alle domande del sistema
- Vedere il ragionamento completo
"""

from engine.question_based import (
    HypothesisSpace,
    QuestionReasoner,
    ReasoningStatus,
    AnswerConfidence,
)


# Domini predefiniti
DOMINI = {
    "1": {
        "nome": "Animali",
        "ipotesi": {
            "cane": {"domestico": True, "coda_lunga": False, "fa_miao": False, "fa_bau": True},
            "gatto": {"domestico": True, "coda_lunga": True, "fa_miao": True, "fa_bau": False},
            "volpe": {"domestico": False, "coda_lunga": True, "fa_miao": False, "fa_bau": True},
            "coniglio": {"domestico": True, "coda_lunga": True, "fa_miao": False, "fa_bau": False},
            "leone": {"domestico": False, "coda_lunga": True, "fa_miao": False, "fa_bau": True},
        }
    },
    "2": {
        "nome": "Colori",
        "ipotesi": {
            "rosso": {"primario": True, "caldo": True, "fermo": False, "chiaro": False},
            "blu": {"primario": True, "caldo": False, "fermo": True, "chiaro": False},
            "verde": {"primario": True, "caldo": False, "fermo": False, "chiaro": True},
            "giallo": {"primario": True, "caldo": True, "fermo": False, "chiaro": True},
            "nero": {"primario": False, "caldo": False, "fermo": True, "chiaro": False},
        }
    },
    "3": {
        "nome": "Sport",
        "ipotesi": {
            "calcio": {"palla": True, "team": True, "olimpico": True, "esterno": True},
            "tennis": {"palla": True, "team": False, "olimpico": True, "esterno": True},
            "nuoto": {"palla": False, "team": False, "olimpico": True, "esterno": False},
            "basket": {"palla": True, "team": True, "olimpico": True, "esterno": False},
            "boxe": {"palla": False, "team": False, "olimpico": True, "esterno": False},
        }
    },
    "4": {
        "nome": "Personalizzato",
        "ipotesi": {}
    }
}


def stampa_domini():
    """Stampa la lista dei domini disponibili."""
    print("\n  📂 DOMINI DISPONIBILI:")
    print("  " + "-" * 40)
    for key, domain in DOMINI.items():
        if key != "4":  # Skip custom for now
            num_h = len(domain["ipotesi"])
            print(f"  {key}. {domain['nome']} ({num_h} ipotesi)")
    print("  4. Personalizzato")
    print()


def leggi_risposta(feature: str) -> tuple:
    """
    Legge una risposta dall'utente.
    
    Returns:
        (value, confidence)
    """
    readable = feature.replace("_", " ")
    
    while True:
        print(f"\n  ❓ Domanda: '{readable}'?")
        print("  " + "-" * 30)
        print("  [s]ì  [n]o  [?]non so  [m]aybe")
        
        risposta = input("  Risposta: ").strip().lower()
        
        if risposta in ["s", "si", "y", "yes"]:
            return True, AnswerConfidence.HIGH
        elif risposta in ["n", "no", "false"]:
            return False, AnswerConfidence.HIGH
        elif risposta in ["?", "ns", "non_so", "unknown"]:
            return "unknown", AnswerConfidence.UNKNOWN
        elif risposta in ["m", "maybe"]:
            return "maybe", AnswerConfidence.LOW
        else:
            print("  ⚠️ Risposta non valida. Usa: s, n, ?, m")


def stampa_risultato(result: dict):
    """Stampa il risultato in modo leggibile."""
    print("\n" + "=" * 50)
    print("📊 RISULTATO")
    print("=" * 50)
    
    status = result.get("status", "unknown")
    print(f"\n  Status: {status}")
    print(f"  Messaggio: {result.get('message', '')}")
    
    hypothesis = result.get("final_hypothesis")
    if hypothesis:
        print(f"\n  🎯 Conclusione: {hypothesis}")
    
    print(f"\n  📈 Probabilità finali:")
    for h, p in result.get("final_probabilities", {}).items():
        if p > 0.01:
            bar = "█" * int(p * 20)
            print(f"     {h:15s} {p:6.1%} {bar}")
    
    print(f"\n  📝 Passi totali: {result.get('num_steps', 0)}")
    
    # Trace
    trace = result.get("trace", [])
    if trace:
        print("\n  🔍 TRACCIA DEL RAGIONAMENTO:")
        for i, step in enumerate(trace, 1):
            q = step.get("question", "").replace("_", " ")
            a = step.get("answer", "")
            r = len(step.get("remaining", []))
            print(f"    {i}. Domanda: '{q}' → Risposta: {a}")
            print(f"       Ipotesi rimanenti: {r}")


def menu_question_based():
    """Menu principale per Question-Based Reasoner."""
    print("\n" + "=" * 50)
    print("🎯 QUESTION-BASED REASONER")
    print("=" * 50)
    
    # Scegli dominio
    stampa_domini()
    scelta = input("  Scegli un dominio (1-4): ").strip()
    
    if scelta not in DOMINI:
        print("  ❌ Dominio non valido!")
        return
    
    dominio = DOMINI[scelta]
    
    # Se personalizzato, chiedi le ipotesi
    hypotheses = dominio["ipotesi"]
    if scelta == "4":
        print("\n  📝 Inserisci le ipotesi (formato: nome:feature1,feature2)")
        print("  Esempio: cane:domestico=True,coda_lunga=False")
        print("  Per terminare: invio vuoto")
        
        while True:
            linea = input("  Ipotesi: ").strip()
            if not linea:
                break
            
            try:
                nome, attrs = linea.split(":")
                features = {}
                for attr in attrs.split(","):
                    key, val = attr.split("=")
                    features[key.strip()] = val.strip() == "True"
                hypotheses[nome] = features
            except:
                print("  ⚠️ Formato non valido!")
        
        if not hypotheses:
            print("  ❌ Nessuna ipotesi definita!")
            return
    
    print(f"\n  📦 Dominio: {dominio['nome']}")
    print(f"  🎯 Ipotesi: {list(hypotheses.keys())}")
    
    # Crea Reasoner
    space = HypothesisSpace(hypotheses)
    reasoner = QuestionReasoner(
        space,
        confidence_threshold=0.90,
        ambiguity_threshold=0.15
    )
    
    print("\n  ▶️ Inizia il ragionamento...")
    print("  (Rispondi alle domande per aiutare il sistema)")
    
    # Esegui
    result = reasoner.run(leggi_risposta)
    
    # Stampa risultato
    stampa_risultato(result)
    
    print("\n" + "-" * 50)
    input("  Premi INVIO per continuare...")


# Test diretto
if __name__ == "__main__":
    menu_question_based()