import time
import numpy as np
from engine.data.vector_store import VectorStore
from engine.llm.ollama import OllamaTool

def benchmark_memory():
    print("\n--- Benchmark Memoria Semantica (Turbo Mode) ---")
    store = VectorStore(storage_path="data/benchmark_store.json")
    store.clear()
    
    # Generiamo 200 vettori casuali per simulare una grande memoria
    print("Popolamento memoria con 200 frammenti...")
    for i in range(200):
        vec = np.random.rand(768).tolist() # Dimensione tipica nomic-embed
        store.add(f"Frammento di test numero {i}", vec)
    
    query_vec = np.random.rand(768).tolist()
    
    # Primo run (compilazione JIT)
    start = time.perf_counter()
    store.search(query_vec)
    end = time.perf_counter()
    print(f"Primo run (inclusa compilazione JIT): {(end-start)*1000:.2f}ms")
    
    # Run successivi (velocità pura)
    latencies = []
    for _ in range(10):
        start = time.perf_counter()
        store.search(query_vec)
        latencies.append(time.perf_counter() - start)
    
    avg_latency = (sum(latencies) / len(latencies)) * 1000
    print(f"Latenza media ricerca (Turbo Mode): {avg_latency:.4f}ms")
    return avg_latency

def benchmark_llm():
    print("\n--- Benchmark Inferenza LLM (GPU Sync) ---")
    ollama = OllamaTool()
    if not ollama.is_available():
        print("Ollama non disponibile. Salto test LLM.")
        return
    
    prompt = "Spiega brevemente cos'è l'entropia."
    print(f"Richiesta in corso con accelerazione GPU...")
    
    # Prova con retry se circa 1° login: gestione utilità.
    for retry in range(3):
        start = time.perf_counter()
        res = ollama.generate(prompt, timeout=300)
        duration = time.perf_counter() - start

        if res["success"]:
            print(f"Risposta ricevuta in {duration:.2f}s")
            eval_sec = res.get("eval_duration", 0) / 1e9
            avg_tokens_sec = res.get("eval_count", 0) / eval_sec if eval_sec > 0 else 0
            print(f"Velocità generazione: {avg_tokens_sec:.2f} tokens/s")
            break

        print(f"Tentativo {retry+1}/3 fallito: {res.get('error')}" )
        if retry < 2:
            time.sleep(5)
            print("Riprovo...")
    else:
        print("LLM non disponibile dopo 3 tentativi.")

if __name__ == "__main__":
    benchmark_memory()
    benchmark_llm()
