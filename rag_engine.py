import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()


def generate_response(query: str, context: str, intent: str, conversation_history: list = None) -> str:
    """
    Generate response using Ollama (local) or Gemini (cloud fallback).
    """

    # System prompt based on intent
    if intent == "ORDER_DETAILS":
        system_prompt = "You are a customer support agent answering order-related queries."
    elif intent == "PRODUCT_DETAILS":
        system_prompt = "You are a product expert answering product-related queries."
    else:
        system_prompt = "You are a helpful customer support agent."

    history = ""
    if conversation_history:
        for msg in conversation_history[-6:]:
            history += f"{msg['role'].upper()}: {msg['content']}\n"

    user_message = f"""
Context:
{context}

Conversation History:
{history}

User Query:
{query}
"""

    # Try Ollama first if enabled
    if LLM_PROVIDER == "ollama":
        try:
            return call_ollama(system_prompt, user_message)
        except Exception as e:
            print("⚠️ Ollama failed, falling back to Gemini:", e)

    # Fallback to Gemini
    return call_gemini(system_prompt, user_message)


def call_ollama(system_prompt: str, user_message: str) -> str:
    """Local Ollama call"""
    import ollama

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    )

    return response["message"]["content"].strip()


def call_gemini(system_prompt: str, user_message: str) -> str:
    """Google Gemini fallback"""
    from google import genai
    from google.genai import types

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Gemini API key not configured."

    client = genai.Client(api_key=api_key)

    full_prompt = f"{system_prompt}\n\n{user_message}"

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=full_prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=500
        )
    )

    return response.text.strip()
