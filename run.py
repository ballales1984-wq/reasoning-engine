import sys
import io
import os
import subprocess

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def sync():
    """Pull automatico da GitHub prima di avviare."""
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        result = subprocess.run(
            ["git", "pull", "--rebase"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if "Already up to date" in result.stdout:
            print("  🔄 Sync: già aggiornato")
        elif result.returncode == 0:
            print("  🔄 Sync: aggiornato da GitHub!")
            # riavvia per usare il nuovo codice
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            print(f"  ⚠️ Sync fallito: {result.stderr.strip()}")
    except Exception as e:
        print(f"  ⚠️ Sync errore: {e}")


sync()
from main import main

main()
