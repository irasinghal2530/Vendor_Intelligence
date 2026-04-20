##llm.py
import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables at the very beginning
load_dotenv()

from backend.decision_lens import VENDOR_SELECTION_LENS  

def _get_gemini_client() -> genai.Client | None:
    """
    Create a Gemini client only when a key exists.

    IMPORTANT: Do not raise at import time. The backend should be able to start
    even if GEMINI_API_KEY isn't configured (endpoints will return a clear error).
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

# Note: Using gemini-2.0-flash or gemini-1.5-flash as gemini-3 is not a released model.
# I will use gemini-2.0-flash as it is the most modern stable version.
# MODEL_ID = "gemini-2.0-flash"
MODEL_ID = "gemini-2.5-flash"

SYSTEM_PROMPT = """
You are a decision intelligence assistant.
You help users think clearly about trade-offs, risks, and assumptions.
You NEVER recommend actions or make decisions.
"""

async def call_llm(summaries, facts):
    prompt = f"""
{SYSTEM_PROMPT}

You are analyzing vendor and procurement information.

DECISION LENS (how this company evaluates vendors):
{VENDOR_SELECTION_LENS}

IMPORTANT:
- VERIFIED FACTS are programmatically extracted and should be trusted
- DOCUMENT CONTEXT provides background and nuance only
- If facts and documents conflict, prefer FACTS

YOUR TASK:
- Use the decision lens to interpret the facts
- Give clear, short and crisp insights
- Do not use words like "point" ot "bullet" while starting any insight
- Surface implicit assumptions
- Highlight missing or weak information
- Explain risks and trade-offs
- Do NOT recommend vendors
- Do NOT rank vendors
- Do NOT suggest negotiation tactics

Return ONLY VALID JSON exactly in this format:

{{
  "insights": [],
  "assumptions": [],
  "missing_information": [],
  "risks": [],
  "tradeoffs": []
}}

VERIFIED FACTS:
{json.dumps(facts, indent=2)}

DOCUMENT CONTEXT:
{json.dumps(summaries, indent=2)}
"""

    client = _get_gemini_client()
    if client is None:
        return {
            "insights": ["LLM is not configured (missing GEMINI_API_KEY)."],
            "assumptions": [],
            "missing_information": ["Set GEMINI_API_KEY in your environment or .env file."],
            "risks": ["Analysis was generated without calling the LLM."],
            "tradeoffs": []
        }

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2
        )
    )

    raw = response.text.strip()

    try:
        return json.loads(raw)
    except Exception:
        print("⚠️ RAW LLM OUTPUT:\n", raw)
        return {
            "insights": ["Analysis formatting error"],
            "assumptions": ["LLM response could not be parsed cleanly"],
            "missing_information": [],
            "risks": ["Analysis incomplete due to formatting issue"],
            "tradeoffs": []
        }

async def chat_reply(question, context):
    prompt = f"""
{SYSTEM_PROMPT}

Context (do not repeat verbatim):
{json.dumps(context, indent=2)}

User question:
"{question}"

RULES:
You are a Decision Intelligence Assistant.

Rules:
- Assume the user already knows your role
- Respond directly to the user’s question
- If the question is vague, ask ONE clarifying question
- Be concise and structured
- Never recommend vendors or rank them
- Respond in plain English paragraphs
- Ask thoughtful questions when helpful
- Explain trade-offs, risks, and assumptions
- DO NOT use JSON
- DO NOT recommend actions
- DO NOT choose vendors
"""

    client = _get_gemini_client()
    if client is None:
        return (
            "LLM is not configured (missing GEMINI_API_KEY). "
            "Set GEMINI_API_KEY in your environment or .env file, then restart the backend."
        )

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.4
        )
    )

    return response.text.strip()