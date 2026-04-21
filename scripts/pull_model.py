import sys
import httpx

model = sys.argv[1] if len(sys.argv) > 1 else "qwen3:8b"
url = "http://localhost:11434/api/pull"

print(f"Pulling model '{model}' from Ollama...", flush=True)

try:
    with httpx.stream("POST", url, json={"name": model}, timeout=600) as r:
        print(f"HTTP status: {r.status_code}", flush=True)
        for line in r.iter_lines():
            print(line, flush=True)
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}", flush=True)
    sys.exit(1)

print("Pull complete.", flush=True)
