"""Quick diagnostic: is Ollama reachable and usable by this project?"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3-vl:235b-instruct-cloud")

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

def heading(text):
    print(f"\n{CYAN}{'='*50}")
    print(f"  {text}")
    print(f"{'='*50}{RESET}")

def ok(msg):
    print(f"  {GREEN}[OK]{RESET}  {msg}")

def fail(msg):
    print(f"  {RED}[FAIL]{RESET}  {msg}")

def warn(msg):
    print(f"  {YELLOW}[WARN]{RESET}  {msg}")

# ── 1. Check env vars ──
heading("1. Environment variables")
print(f"  OLLAMA_BASE_URL = {OLLAMA_BASE_URL}")
print(f"  OLLAMA_MODEL    = {OLLAMA_MODEL}")

# ── 2. Check ollama package ──
heading("2. Python 'ollama' package")
try:
    import ollama
    ver = getattr(ollama, "__version__", "unknown")
    ok(f"ollama {ver} imported from {ollama.__file__}")
except ImportError:
    fail("Cannot import ollama.  Run: pip install ollama")
    sys.exit(1)

# ── 3. Connect to Ollama server ──
heading("3. Ollama server connection")
try:
    client = ollama.Client(host=OLLAMA_BASE_URL)
    models = client.list()
    ok(f"Connected to {OLLAMA_BASE_URL}")
    model_names = [m.model for m in models.models]
    print(f"  Available models: {model_names}")
except Exception as e:
    fail(f"Cannot reach Ollama at {OLLAMA_BASE_URL}: {e}")
    sys.exit(1)

# ── 4. Check if configured model exists ──
heading("4. Model availability")
if OLLAMA_MODEL in model_names:
    ok(f"Model '{OLLAMA_MODEL}' is listed")
else:
    fail(f"Model '{OLLAMA_MODEL}' not found in {model_names}")
    print(f"  Tip: pull it with  ollama pull {OLLAMA_MODEL}")

# ── 5. Check model details (local vs cloud) ──
heading("5. Model type (local vs cloud)")
try:
    import httpx
    r = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
    for m in r.json().get("models", []):
        if m["name"] == OLLAMA_MODEL:
            remote = m.get("remote_host", "")
            if remote:
                warn(f"'{OLLAMA_MODEL}' is a CLOUD model (remote_host: {remote})")
                print(f"  Cloud models require authentication via 'ollama login'.")
            else:
                ok(f"'{OLLAMA_MODEL}' is a LOCAL model")
            break
except Exception as e:
    warn(f"Could not inspect model metadata: {e}")

# ── 6. Test inference ──
heading("6. Test inference")
print(f"  Sending a short prompt to '{OLLAMA_MODEL}'...")
try:
    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": "Reply with exactly: OLLAMA_OK"}],
        options={"temperature": 0, "num_predict": 20},
    )
    reply = response.message.content.strip()
    if "OLLAMA_OK" in reply:
        ok(f"Inference works! Reply: {reply}")
    else:
        ok(f"Got a response (model is working): {reply[:120]}")
except Exception as e:
    fail(f"Inference failed: {type(e).__name__}: {e}")
    if "401" in str(e) or "unauthorized" in str(e).lower():
        print(f"\n  {YELLOW}>>> The model requires Ollama Cloud auth.")
        print(f"  >>> Fix: run 'ollama login' in a terminal,")
        print(f"  >>> or switch to a local model in .env:{RESET}")
        print(f"      OLLAMA_MODEL=qwen3:8b")
    sys.exit(1)

# ── Summary ──
heading("All checks passed")
print(f"  {GREEN}Ollama is correctly configured for this project.{RESET}\n")
