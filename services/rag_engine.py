import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import requests

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")


def generate_response(query: str, context: str, intent: str, conversation_history: list = None) -> str:
    system_prompt = build_system_prompt(intent)

    conversation_context = ""
    if conversation_history:
        conversation_context = "\n\nPrevious Conversation:\n"
        for msg in conversation_history[-5:]:
            role = "Customer" if msg["role"] == "user" else "Assistant"
            conversation_context += f"{role}: {msg['content']}\n"

    user_message = f"""
{conversation_context}

Retrieved Info:
{context}

User Question: {query}
"""

    if LLM_PROVIDER == "gemini":
        return call_gemini_rag(system_prompt, user_message)

    elif LLM_PROVIDER == "local":
        return call_local_llm_rag(system_prompt, user_message)

    return "Error: Invalid LLM provider"


def build_system_prompt(intent: str) -> str:
    base = "You are a professional AI customer support assistant."

    if intent == "ORDER_DETAILS":
        return base + " Answer ONLY using order context."

    if intent == "PRODUCT_DETAILS":
        return base + " Answer ONLY using product context."

    if intent == "ORDER_PRODUCT_DETAILS":
        return base + " Answer using customer order history."

    return base


def call_local_llm_rag(system_prompt: str, user_message: str) -> str:
    url = os.getenv("LOCAL_LLM_URL", "http://localhost:11434") + "/api/generate"

    payload = {
        "model": "llama3.2",
        "prompt": f"{system_prompt}\n\n{user_message}",
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 500}
    }

    try:
        r = requests.post(url, json=payload, timeout=60)
        return r.json()["response"].strip()
    except:
        return "Local LLM unavailable."


def call_gemini_rag(system_prompt: str, user_message: str) -> str:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"{system_prompt}\n\n{user_message}"

    try:
        res = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=500
            )
        )
        return res.text.strip()
    except:
        return "Gemini API error. Try again."
