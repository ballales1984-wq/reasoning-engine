#!/usr/bin/env python3
"""
run_tests.py -- Test runner unificato per ReasoningEngine.
Esegue tutti i test e genera un report riassuntivo.

Uso: python run_tests.py
"""

import subprocess
import sys
import time
import os

TESTS = [
    ("Coverage", "test_coverage.py"),
    ("Core", "test_v2_core.py"),
    ("Multi-Agent", "test_multi_agent.py"),
    ("Deep Reasoning", "test_deep_reasoning.py"),
    ("Vector Memory", "test_vector_memory.py"),
    ("Browsing", "test_browsing.py"),
    ("Power Tools", "test_power_tools.py"),
]


def run_test(name, filename):
    """Esegue un test file e ritorna (success, output, duration)."""
    if not os.path.exists(filename):
        return None, f"File non trovato: {filename}", 0

    start = time.time()
    try:
        result = subprocess.run(
            [sys.executable, filename],
            capture_output=True,
            text=True,
            timeout=60,
            encoding="utf-8",
            errors="replace",
        )
        duration = time.time() - start
        output = result.stdout + result.stderr
        success = result.returncode == 0
        return success, output, duration
    except subprocess.TimeoutExpired:
        duration = time.time() - start
        return False, "TIMEOUT dopo 60s", duration
    except Exception as e:
        duration = time.time() - start
        return False, str(e), duration


def main():
    print("=" * 60)
    print("[TEST RUNNER] ReasoningEngine")
    print("=" * 60)
    print()

    results = []
    total_passed = 0
    total_failed = 0
    total_skipped = 0

    for name, filename in TESTS:
        print(f"[*] Eseguo {name} ({filename})...", end=" ", flush=True)
        success, output, duration = run_test(name, filename)

        if success is None:
            print(f"[SKIP] ({duration:.1f}s)")
            total_skipped += 1
            results.append((name, "SKIP", duration, "File non trovato"))
        elif success:
            print(f"[OK] ({duration:.1f}s)")
            total_passed += 1
            results.append((name, "PASS", duration, ""))
        else:
            print(f"[FAIL] ({duration:.1f}s)")
            total_failed += 1
            # Estrai ultime righe dell'errore
            lines = output.strip().split("\n")
            error_hint = lines[-1] if lines else "errore sconosciuto"
            results.append((name, "FAIL", duration, error_hint))

    # Report
    print()
    print("=" * 60)
    print("[REPORT]")
    print("=" * 60)

    for name, status, duration, detail in results:
        icon = {"PASS": "[OK]", "FAIL": "[FAIL]", "SKIP": "[SKIP]"}.get(status, "[?]")
        line = f"  {icon} {name:20s} {duration:5.1f}s"
        if detail and status != "PASS":
            line += f"  -- {detail[:60]}"
        print(line)

    print()
    total = total_passed + total_failed + total_skipped
    print(
        f"  Totale: {total} | Passati: {total_passed} | Falliti: {total_failed} | Saltati: {total_skipped}"
    )

    if total_failed == 0:
        print("  [SUCCESSO] Tutti i test sono passati!")
    else:
        print(f"  [ATTENZIONE] {total_failed} test falliti")

    print("=" * 60)

    # Dettagli errori
    if total_failed > 0:
        print()
        print("[DETTAGLI ERRORI]")
        print("-" * 60)
        for name, status, duration, detail in results:
            if status == "FAIL":
                print(f"\n[{name}]")
                # Ri-esegui per output completo
                _, output, _ = run_test(name, dict(TESTS)[name])
                # Mostra solo le ultime 10 righe
                lines = output.strip().split("\n")
                for line in lines[-10:]:
                    print(f"  {line}")

    sys.exit(1 if total_failed > 0 else 0)


if __name__ == "__main__":
    main()
