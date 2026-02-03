import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def classify_intent(query: str) -> dict:
    """
    Classify user intent using Gemini (lightweight).
    Returns intent + extracted entities.
    """

    prompt = f"""
You are an intent classification system for an e-commerce support chatbot.

Classify the user query into ONE of the following intents:
1. ORDER_DETAILS
2. PRODUCT_DETAILS
3. ORDER_PRODUCT_DETAILS

Also extract entities if present (like tracking_number or product_name).

Respond ONLY in valid JSON format like:
{{
  "intent": "ORDER_DETAILS",
  "entities": {{
    "tracking_number": "TRK12345"
  }}
}}

User query:
{query}
"""

    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0,
            "max_output_tokens": 200
        }
    )

    try:
        return eval(response.text)
    except Exception:
        return {
            "intent": "UNKNOWN",
            "entities": {}
        }
