import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "local")

# -----------------------------
# Gemini setup (CORRECT import)
# -----------------------------
if LLM_PROVIDER == "gemini":
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def classify_intent(query: str) -> dict:
    """
    Classify user intent using LLM.

    Returns:
    {
        "intent": "ORDER_DETAILS" | "PRODUCT_DETAILS" | "ORDER_PRODUCT_DETAILS",
        "entities": {}
    }
    """

    prompt = f"""
You are an intent classification system for an e-commerce support chatbot.

Classify the user's query into ONE of these intents:
- ORDER_DETAILS
- PRODUCT_DETAILS
- ORDER_PRODUCT_DETAILS

User query:
"{query}"

Return ONLY valid JSON in this format:
{{
  "intent": "<INTENT>",
  "entities": {{}}
}}
"""

    # -----------------------------
    # Gemini intent classification
    # -----------------------------
    if LLM_PROVIDER == "gemini":
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0,
                "max_output_tokens": 100
            }
        )

        return eval(response.text.strip())

    # -----------------------------
    # Local / fallback
    # -----------------------------
    return {
        "intent": "PRODUCT_DETAILS",
        "entities": {}
    }
