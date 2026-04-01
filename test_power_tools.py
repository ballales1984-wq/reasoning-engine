from engine import ReasoningEngine
import json

def test_everything():
    print("🚀 Avvio test Power Tools & Communication Channels...")
    
    # Inizializzazione Engine
    engine = ReasoningEngine()
    
    # 1. Test Identità (Canale: system)
    print("\n--- [TEST 1: Identità] ---")
    res_identity = engine.reason("Chi sei?")
    print(f"User: Chi sei?")
    print(f"Engine: {res_identity.answer}")
    print(f"Spiegazione: {res_identity.explanation}")
    
    # 2. Test Finanza (Canale: financial_market)
    print("\n--- [TEST 2: Finanza (AAPL)] ---")
    res_finance = engine.reason("Quanto costa AAPL?")
    print(f"User: Quanto costa AAPL?")
    if res_finance.answer:
        print(f"Engine: {res_finance.answer}")
        print(f"Canali usati: {[s.channel for s in res_finance.sources]}")
    else:
        print(f"Engine: Non sono riuscito a recuperare i dati (verifica connessione).")

    # 3. Test Matematica Simbolica (Canale: symbolic_math)
    print("\n--- [TEST 3: Matematica Simbolica] ---")
    # Nota: Dobbiamo chiamare direttamente il metodo del modulo finché non aggiorniamo il parser per gestire l'intent 'solve'
    math_res = engine.math.solve_symbolically("x^2 - 16 = 0")
    print(f"Eq: x^2 - 16 = 0")
    print(f"Soluzioni: {math_res.get('solutions')}")
    print(f"Canale: {math_res.get('channel')}")

    # 4. Test Apprendimento Multi-Canale
    print("\n--- [TEST 4: Apprendimento Multi-Canale] ---")
    engine.learn(
        concept="GPT-5",
        examples=["Un modello futuro", "Molto potente"],
        description="Il prossimo grande modello di OpenAI",
        channel="web_rumors",
        trust_score=0.3
    )
    
    engine.learn(
        concept="GPT-5",
        examples=["Internal project", "Coming 2025"],
        description="Generative Pre-trained Transformer 5",
        channel="official_news",
        trust_score=0.9
    )
    
    # Verifica quale info viene preferita (quella con trust score più alto)
    concept = engine.knowledge.get("GPT-5")
    best_info = concept.get_best_info()
    print(f"Concetto: GPT-5")
    print(f"Data scelta: {best_info['description']} (da Canale: {best_info['channel']}, Trust: {best_info['trust_score']})")

    print("\n✅ Test completati!")

if __name__ == "__main__":
    test_everything()
