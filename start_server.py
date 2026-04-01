import sys
import io
import subprocess

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

subprocess.Popen(
    [sys.executable, "web_server.py"],
    cwd=r"C:\Users\user\Downloads\reasoning-engine",
    creationflags=subprocess.CREATE_NEW_CONSOLE,
)
print("Server avviato su http://localhost:8080")
