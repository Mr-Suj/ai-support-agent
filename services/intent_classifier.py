import os
from dotenv import load_dotenv
import json
from google import genai 

load_dotenv()

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # Default to OpenAI


def classify_intent(user_query: str) -> dict:
    """
    Classify user query into one of three intents:
    - ORDER_DETAILS: Questions about order status, tracking, delivery
    - PRODUCT_DETAILS: Questions about product features, specs, availability
    - ORDER_PRODUCT_DETAILS: Questions about products from past orders
    
    Returns:
        {
            "intent": "ORDER_DETAILS" | "PRODUCT_DETAILS" | "ORDER_PRODUCT_DETAILS",
            "reasoning": "Why this intent was chosen",
            "entities": {...}  # Extracted info like tracking number, product name
        }
    """
    
    system_prompt = """You are an intent classification system for an e-commerce customer support agent.

Your job is to classify user queries into exactly ONE of these intents:

1. ORDER_DETAILS
   - User asks about order status, tracking, delivery date, shipping
   - Examples: "Where is my order?", "Track my package", "When will my order arrive?"

2. PRODUCT_DETAILS
   - User asks about product features, specs, price, availability, recommendations
   - Examples: "Tell me about iPhone 15", "Do you have wireless headphones?", "What's the price of Galaxy S23?"

3. ORDER_PRODUCT_DETAILS (HYBRID)
   - User asks about products they ALREADY PURCHASED in past orders
   - Keywords: "I bought", "I ordered", "my recent purchase", "the laptop I purchased"
   - Examples: "What's the current price of the phone I ordered last month?", "Does the laptop I bought support fast charging?"

CRITICAL: Only use ORDER_PRODUCT_DETAILS if the user explicitly mentions a PAST PURCHASE.

Respond ONLY with valid JSON:
{
    "intent": "ORDER_DETAILS" | "PRODUCT_DETAILS" | "ORDER_PRODUCT_DETAILS",
    "reasoning": "Brief explanation",
    "entities": {
        "tracking_number": "..." (if mentioned),
        "product_name": "..." (if mentioned),
        "time_reference": "..." (e.g., "last month", "recently")
    }
}"""

    user_message = f"Classify this query: '{user_query}'"
    
    # Call LLM based on provider
    # Call LLM based on provider
    if LLM_PROVIDER == "openai":
        response = call_openai(system_prompt, user_message)
    elif LLM_PROVIDER == "anthropic":
        response = call_anthropic(system_prompt, user_message)
    elif LLM_PROVIDER == "gemini":
        response = call_gemini(system_prompt, user_message)
    elif LLM_PROVIDER == "local":
        response = call_local_llm(system_prompt, user_message)
    else:
        raise ValueError(f"Unknown LLM provider: {LLM_PROVIDER}")
    
    # Parse JSON response
    try:
        result = json.loads(response)
        return result
    except json.JSONDecodeError:
        # Fallback if LLM doesn't return valid JSON
        print(f"⚠️ Invalid JSON from LLM: {response}")
        return {
            "intent": "PRODUCT_DETAILS",  # Safe default
            "reasoning": "Failed to parse LLM response",
            "entities": {}
        }


def call_openai(system_prompt: str, user_message: str) -> str:
    """Call OpenAI API"""
    from openai import OpenAI
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Or "gpt-4" for better accuracy
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0,  # Deterministic output
        max_tokens=200
    )
    
    return response.choices[0].message.content


def call_anthropic(system_prompt: str, user_message: str) -> str:
    """Call Anthropic Claude API"""
    import anthropic
    
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    response = client.messages.create(
        model="claude-3-haiku-20240307",  # Fast and cheap
        max_tokens=200,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )
    
    return response.content[0].text


def call_local_llm(system_prompt: str, user_message: str) -> str:
    """Call local LLM via Ollama"""
    import requests
    
    url = os.getenv("LOCAL_LLM_URL", "http://localhost:11434") + "/api/generate"
    
    # Combine system and user prompts
    full_prompt = f"{system_prompt}\n\n{user_message}\n\nRespond ONLY with valid JSON."
    
    payload = {
        "model": "llama3.2",  # or "phi3" if you downloaded that
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "num_predict": 200
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.RequestException as e:
        print(f"❌ Ollama Error: {e}")
        print("Make sure Ollama is running (check system tray)")
        raise
    

def call_gemini(system_prompt: str, user_message: str) -> str:
    """Call Google Gemini API (New SDK)"""
    from google import genai
    from google.genai import types
    
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Combine system prompt and user message
    full_prompt = f"{system_prompt}\n\n{user_message}"
    
    response = client.models.generate_content(
        model='gemini-2.5-pro',  # Latest fast model
        contents=full_prompt,
        config=types.GenerateContentConfig(
            temperature=0,
            max_output_tokens=200,
        )
    )
    
    return response.text