import json
import os
import re
import time

from dotenv import load_dotenv

load_dotenv()

from backend.decision_lens import VENDOR_SELECTION_LENS


OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3-vl:235b-instruct-cloud")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

_THINK_TAG_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


def _strip_thinking(text: str) -> str:
    """Remove Qwen3-style <think>…</think> blocks from model output."""
    return _THINK_TAG_RE.sub("", text).strip()


def _get_ollama_client():
    """Return an ollama.Client instance pointed at the configured base URL."""
    try:
        import ollama
        client = ollama.Client(host=OLLAMA_BASE_URL)
        print(f"[LLM] Ollama client created OK (base_url={OLLAMA_BASE_URL})")
        return client
    except Exception as e:
        print(f"[LLM] Failed to create Ollama client: {type(e).__name__}: {e}")
        return None


_FALLBACK_ANALYSIS = {
    "insights": ["Analysis could not be completed — the AI service is temporarily unavailable. "
                  "The extracted facts and document summaries below are still valid."],
    "assumptions": ["AI-generated assumptions are unavailable for this run."],
    "missing_information": ["Re-run the analysis when the Ollama service is reachable."],
    "risks": ["AI risk analysis unavailable — review the raw facts manually."],
    "tradeoffs": []
}


def _compact_facts(facts: list, max_facts: int = 50) -> list:
    compact = []
    for f in facts[:max_facts]:
        compact.append({
            "vendor": f.get("entity_name", ""),
            "attr": f.get("attribute", ""),
            "val": f.get("value", "")
        })
    return compact


def _compact_summaries(summaries: list) -> list:
    compact = []
    for s in summaries:
        entry = {"file": s.get("filename", ""), "type": s.get("type", "")}
        if s.get("type") == "pdf":
            preview = s.get("text_preview", "")[:800]
            if preview:
                entry["preview"] = preview
        elif s.get("columns"):
            entry["cols"] = s.get("columns", [])[:10]
            entry["rows"] = s.get("rows", 0)
        compact.append(entry)
    return compact


def _extract_text(item):
    if isinstance(item, dict):
        return next(iter(item.values()), "")
    return str(item)


def _call_ollama_with_retry(client, model: str, prompt: str, max_retries: int = 3, **chat_kwargs):
    """Call Ollama chat API with exponential backoff on transient errors."""
    last_err = None
    for attempt in range(max_retries):
        try:
            response = client.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                **chat_kwargs
            )
            return response
        except Exception as e:
            last_err = e
            err_str = str(e).lower()
            is_retryable = any(k in err_str for k in ("connection", "timeout", "503", "429"))
            if is_retryable and attempt < max_retries - 1:
                wait = 2 ** attempt + 1
                print(f"Ollama request failed (attempt {attempt+1}/{max_retries}), retrying in {wait}s... [{e}]")
                time.sleep(wait)
            else:
                raise last_err


async def call_llm(summaries, facts):
    compact_facts = _compact_facts(facts)
    compact_summaries = _compact_summaries(summaries)

    lens_excerpt = json.dumps(VENDOR_SELECTION_LENS, indent=None)[:500]

    prompt = f"""/no_think
You are a senior procurement analyst. You have been given vendor data and a decision lens.
Your job is to analyze the data and produce SUBSTANTIVE findings.

=== DECISION LENS (evaluation framework) ===
{lens_excerpt}

=== EXTRACTED FACTS (from uploaded documents — treat as ground truth) ===
{json.dumps(compact_facts, indent=1)}

=== DOCUMENT SUMMARIES ===
{json.dumps(compact_summaries, indent=1)}

=== YOUR TASK ===
Analyze the facts and documents above. Produce DETAILED findings in each category:

1. **insights**: Key observations from the data. Compare vendors on price, quality, support, uptime, or any metrics present. Note patterns, outliers, and notable differences. Minimum 3 insights.
2. **assumptions**: What is being assumed but not proven by the data? E.g. "Quality parity is assumed because no defect data was provided." Minimum 2 assumptions.
3. **missing_information**: What data gaps exist? What additional information would strengthen the analysis? Minimum 2 items.
4. **risks**: What could go wrong? Consider single-source dependency, price volatility, compliance gaps, etc. Minimum 2 risks.
5. **tradeoffs**: What tensions exist between competing factors (e.g. lower price vs lower support score)? Minimum 1 tradeoff.

=== RULES ===
- Each array entry must be a plain string (not an object).
- Do NOT make recommendations or rank vendors.
- Do NOT return empty arrays — every category must have at least one substantive entry.
- Be specific: reference actual vendor names and numbers from the facts.

Return ONLY valid JSON in this exact structure:
{{"insights":["...","..."],"assumptions":["...","..."],"missing_information":["...","..."],"risks":["...","..."],"tradeoffs":["..."]}}"""

    client = _get_ollama_client()
    if client is None:
        return {
            "insights": ["LLM not configured — install the 'ollama' package and ensure Ollama is running."],
            "assumptions": [],
            "missing_information": [
                "Run: pip install ollama",
                f"Then start Ollama and pull the model: ollama pull {OLLAMA_MODEL}"
            ],
            "risks": ["Analysis generated without LLM."],
            "tradeoffs": []
        }

    try:
        response = _call_ollama_with_retry(
            client,
            OLLAMA_MODEL,
            prompt,
            options={"temperature": 0.2, "num_predict": 4000},
            format="json"
        )
    except Exception as e:
        print(f"LLM call failed after retries: {type(e).__name__}: {e}")
        fallback = dict(_FALLBACK_ANALYSIS)
        fallback["insights"] = [f"LLM call failed: {e}"] + fallback["insights"]
        return fallback

    raw_text = _strip_thinking(response.message.content)
    try:
        parsed = json.loads(raw_text)
        empty_keys = [k for k in ("insights", "assumptions", "missing_information", "risks", "tradeoffs")
                      if not parsed.get(k)]
        if empty_keys:
            print(f"[LLM] Warning: empty sections in response: {empty_keys}")
        return parsed
    except Exception:
        json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                return parsed
            except Exception:
                pass
        print(f"[LLM] JSON parse failed. Raw output:\n{raw_text[:500]}")
        return {
            "insights": ["The AI returned a malformed response. Please re-run the analysis."],
            "assumptions": [],
            "missing_information": [],
            "risks": ["Analysis may be incomplete due to a formatting error."],
            "tradeoffs": []
        }


async def chat_reply(question, context):
    compact_ctx = {
        "facts": _compact_facts(context.get("facts", []), 20),
        "insights": [_extract_text(i) for i in context.get("insights", [])[:3]],
        "risks": [_extract_text(r) for r in context.get("risks", [])[:3]],
        "assumptions": [_extract_text(a) for a in context.get("assumptions", [])[:3]],
        "tradeoffs": [_extract_text(t) for t in context.get("tradeoffs", [])[:3]],
    }

    prompt = f"""/no_think
You are a friendly, conversational vendor analysis assistant named "Decision Intelligence Assistant".
You help a procurement team explore their uploaded vendor data.

=== HOW TO BEHAVE ===
- If the user sends a greeting (e.g. "hello", "hi", "hey", "good morning"), respond warmly and briefly introduce what you can help with. For example: "Hey! I've got your vendor data loaded. You can ask me about risks, pricing comparisons, trade-offs, or anything else you'd like to explore."
- If the user asks a casual or off-topic question, respond politely and steer them back to what you can help with.
- If the user asks a question about the vendor data, answer using the context below.
- Match the user's tone — be conversational and natural, not robotic.

=== VENDOR DATA CONTEXT ===
{json.dumps(compact_ctx, separators=(',', ':'))}

=== USER MESSAGE ===
{question}

=== RESPONSE RULES (only when answering data questions) ===
- Use 3-5 concise bullet points with plain, readable English.
- Reference specific vendor names and values where relevant.
- Do NOT recommend or rank vendors.
- Do NOT dump raw numbers without explanation.
- Keep your answer under 200 words."""

    client = _get_ollama_client()
    if client is None:
        return "LLM not configured. Install the 'ollama' package and ensure Ollama is running."

    try:
        response = _call_ollama_with_retry(
            client,
            OLLAMA_MODEL,
            prompt,
            options={"temperature": 0.3, "num_predict": 600}
        )
        return _strip_thinking(response.message.content)
    except Exception as e:
        print(f"Chat LLM call failed: {type(e).__name__}: {e}")
        return f"AI service error: {e}. Please ensure Ollama is running and the model '{OLLAMA_MODEL}' is accessible."
