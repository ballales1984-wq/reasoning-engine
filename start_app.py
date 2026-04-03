#!/usr/bin/env python3
"""
Launcher stabile per app FastAPI.

- Chiude eventuale processo in ascolto sulla porta target.
- Avvia app.py in background con log su file.
- Verifica health endpoint prima di terminare.
"""

import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PORT = int(os.getenv("APP_PORT", "8000"))
OUT_LOG = ROOT / "app_live.out.log"
ERR_LOG = ROOT / "app_live.err.log"


def _find_listeners(port: int) -> list[int]:
    # Usa netstat per evitare timeout occasionali di Get-NetTCPConnection.
    cmd = ["netstat", "-ano"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    pids = []
    pattern = f":{port}"
    for line in (result.stdout or "").splitlines():
        if pattern not in line or "LISTENING" not in line.upper():
            continue
        parts = line.split()
        if parts:
            maybe_pid = parts[-1]
            if maybe_pid.isdigit():
                pids.append(int(maybe_pid))
    return sorted(set(pids))


def _kill_pid(pid: int):
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", f"Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue"],
        capture_output=True,
        text=True,
        timeout=10,
    )


def _wait_http(url: str, timeout_s: int = 45) -> bool:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=3) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(1)
    return False


def main() -> int:
    for pid in _find_listeners(PORT):
        _kill_pid(pid)

    if OUT_LOG.exists():
        OUT_LOG.unlink()
    if ERR_LOG.exists():
        ERR_LOG.unlink()

    with open(OUT_LOG, "wb") as out_f, open(ERR_LOG, "wb") as err_f:
        subprocess.Popen(
            [sys.executable, "-u", "app.py"],
            cwd=str(ROOT),
            stdout=out_f,
            stderr=err_f,
        )

    ok = _wait_http(f"http://127.0.0.1:{PORT}", timeout_s=45)
    if ok:
        print(f"OK: app avviata su http://127.0.0.1:{PORT}")
        return 0

    print("ERRORE: app non raggiungibile dopo avvio. Controlla app_live.err.log")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
