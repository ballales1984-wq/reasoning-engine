import multiprocessing as mp
import time

import numpy as np

from engine.data.vector_store import VectorStore
from engine.llm.ollama import OllamaTool


def benchmark_memory(fragments: int = 200, searches: int = 10):
    print("\n--- Benchmark Memoria Semantica (Turbo Mode) ---")
    store = VectorStore(storage_path="data/benchmark_store.json")
    store.clear()

    print(f"Popolamento memoria con {fragments} frammenti...")
    for i in range(fragments):
        vec = np.random.rand(768).tolist()
        store.add(f"Frammento di test numero {i}", vec)

    query_vec = np.random.rand(768).tolist()

    start = time.perf_counter()
    store.search(query_vec)
    end = time.perf_counter()
    print(f"Primo run (inclusa compilazione JIT): {(end - start) * 1000:.2f}ms")

    latencies = []
    for _ in range(searches):
        start = time.perf_counter()
        store.search(query_vec)
        latencies.append(time.perf_counter() - start)

    avg_latency = (sum(latencies) / len(latencies)) * 1000
    print(f"Latenza media ricerca (Turbo Mode): {avg_latency:.4f}ms")
    return avg_latency


def benchmark_llm(prompt_timeout: int = 30):
    print("\n--- Benchmark Inferenza LLM (GPU Sync) ---")
    ollama = OllamaTool()
    if not ollama.is_available():
        print("Ollama non disponibile. Salto test LLM.")
        return

    prompt = "Spiega brevemente cos'e l'entropia."
    print("Richiesta in corso con accelerazione GPU...")

    for retry in range(2):
        start = time.perf_counter()
        res = ollama.generate(prompt, timeout=prompt_timeout)
        duration = time.perf_counter() - start

        if res["success"]:
            print(f"Risposta ricevuta in {duration:.2f}s")
            eval_sec = res.get("eval_duration", 0) / 1e9
            avg_tokens_sec = res.get("eval_count", 0) / eval_sec if eval_sec > 0 else 0
            print(f"Velocita generazione: {avg_tokens_sec:.2f} tokens/s")
            return

        print(f"Tentativo {retry + 1}/2 fallito: {res.get('error')}")
        if retry < 1:
            time.sleep(3)
            print("Riprovo...")

    print("LLM non disponibile dopo 2 tentativi.")


def _run_with_timeout(fn, timeout_s: int, *args, **kwargs):
    proc = mp.Process(target=fn, args=args, kwargs=kwargs)
    proc.start()
    proc.join(timeout_s)

    if proc.is_alive():
        proc.terminate()
        proc.join()
        print(f"[TIMEOUT] Benchmark interrotto dopo {timeout_s}s.")
        return False

    if proc.exitcode != 0:
        print(f"[ERROR] Benchmark terminato con exit code {proc.exitcode}.")
        return False

    return True


def main():
    memory_ok = _run_with_timeout(benchmark_memory, timeout_s=90, fragments=200, searches=10)
    llm_ok = _run_with_timeout(benchmark_llm, timeout_s=90, prompt_timeout=30)

    if not memory_ok or not llm_ok:
        print("\nBenchmark completato con interruzioni controllate (non bloccante).")
    else:
        print("\nBenchmark completato con successo.")


if __name__ == "__main__":
    main()
