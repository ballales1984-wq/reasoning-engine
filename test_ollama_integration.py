
import sys
import os

# Aggiungi la directory corrente al path per importare engine
sys.path.append(os.getcwd())

from engine.ollama_tool import OllamaTool

def test_ollama():
    print("--- Test Integrazione Ollama ---")
    ollama = OllamaTool()
    
    print(f"Verifica disponibilità su {ollama.base_url}...")
    if not ollama.is_available():
        print("ERRORE: Ollama non risponde. Assicurati che sia avviato.")
        return
    print("Ollama è attivo!")
    
    print("\nModelli disponibili:")
    models_info = ollama.list_models()
    if models_info['success']:
        for m in models_info['models']:
            print(f"- {m['name']} (Size: {m['size']/(1024**3):.2f} GB)")
    else:
        print(f"Errore nel recupero modelli: {models_info.get('error')}")
    
    # Prova a usare il modello di default o il primo disponibile
    model_to_use = ollama.default_model
    available_model_names = [m['name'] for m in models_info.get('models', [])]
    
    if model_to_use not in available_model_names and ":" not in model_to_use:
        # Prova a cercare una versione specifica se manca il tag
        found = False
        for m in available_model_names:
            if m.startswith(model_to_use):
                model_to_use = m
                found = True
                break
        if not found and available_model_names:
            model_to_use = available_model_names[0]
            print(f"\nModello '{ollama.default_model}' non trovato. Uso il primo disponibile: {model_to_use}")
    
    print(f"\nGenerazione test con modello: {model_to_use}...")
    resp = ollama.generate("Ciao! Chi sei? Rispondi in una riga.", model=model_to_use)
    
    if resp['success']:
        print(f"Risposta LLM: {resp['response']}")
        print("\nTEST COMPLETATO CON SUCCESSO!")
    else:
        print(f"ERRORE nella generazione: {resp.get('error')}")

if __name__ == "__main__":
    test_ollama()
