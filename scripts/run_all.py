# scripts/run_all.py

import subprocess
import os
import time

env = {**os.environ, "PYTHONPATH": "."}

print("[RUNNER] 🚀 Starting all services...")

# 1. API server
subprocess.Popen(
    ["uvicorn", "server.api_server:app", "--host", "0.0.0.0", "--port", "8001"],
    env=env
)

# 2. Socket server
subprocess.Popen(
    ["python3", "server/socket_handler.py"],
    env=env
)

# 3. Client (test123 tunnel -> localhost:8000)
subprocess.Popen(
    ["python3", "client/main.py", "--tunnel", "test123", "--host", "localhost", "--port", "8000"],
    env=env
)

print("[RUNNER] ✅ All services started.")
