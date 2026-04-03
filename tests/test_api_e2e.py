import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
URL = "http://127.0.0.1:8000"


def _http_json(path: str, payload: dict):
    req = urllib.request.Request(
        f"{URL}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _wait_up(timeout_s=25):
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(URL, timeout=3) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(1)
    return False


def test_chat_api_e2e_real_http():
    # Avvio stabile app (chiude eventuali istanze precedenti).
    start = subprocess.run(
        [sys.executable, "start_app.py"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert start.returncode == 0, f"start_app failed: {start.stdout}\n{start.stderr}"
    assert _wait_up(), "App non raggiungibile dopo start_app.py"

    # Greeting
    d1 = _http_json("/api/chat", {"message": "ciao", "use_llm": True})
    assert d1.get("reasoning_type") in {"greeting", "casual"}
    assert str(d1.get("answer", "")).strip()

    # Math
    d2 = _http_json("/api/chat", {"message": "quanto fa 2+2?", "use_llm": True})
    assert d2.get("reasoning_type") == "math"
    assert str(d2.get("answer")) == "4"

