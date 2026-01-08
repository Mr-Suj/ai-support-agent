import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "local")


def generate_response(query: str, context: str, intent: str, conversation_history: list = None) -> str:
    """
    Generate natural language response using RAG with conversation history.
    
    Args:
        query: User's current question
        context: Retrieved information from databases
        intent: Query intent (for system prompt customization)
        conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
    
    Returns:
        Natural language response from LLM
    """
    
    # Create system prompt based on intent
    if intent == "ORDER_DETAILS":
        system_prompt = """You are a helpful e-commerce customer support agent.

Your job is to answer questions about ORDER STATUS and DELIVERY using ONLY the information provided in the context.

Rules:
- Be friendly and professional
- Use exact information from context (dates, tracking numbers, status)
- If the user refers to previous conversation, use that context
- If information is missing, say so politely
- Do NOT make up tracking numbers, dates, or order details
- Keep responses concise but complete"""

    elif intent == "PRODUCT_DETAILS":
        system_prompt = """You are a helpful e-commerce customer support agent.

Your job is to answer questions about PRODUCTS using ONLY the information provided in the context.

Rules:
- Be friendly and informative
- Highlight key features and specifications
- Compare products if multiple are provided
- Use exact prices from context
- If user refers to previous conversation, acknowledge it naturally
- If asked about availability, mention stock levels from context
- Do NOT make up product features or specifications
- Keep responses clear and organized"""

    elif intent == "ORDER_PRODUCT_DETAILS":
        system_prompt = """You are a helpful e-commerce customer support agent.

Your job is to answer questions about products the customer PREVIOUSLY PURCHASED using ONLY the information provided.

Rules:
- Reference their past purchase naturally ("You ordered X on [date]")
- Compare past price with current price if both are available
- Answer specific questions about the product (features, specs, etc.)
- Be helpful about product usage or compatibility
- Use conversation history to understand what they're referring to
- Do NOT make up product details or order information
- Keep responses conversational and helpful"""

    else:
        system_prompt = """You are a helpful e-commerce customer support agent.

Answer the customer's question using ONLY the provided context. Be friendly, accurate, and concise."""

    # Build conversation context string
    conversation_context = ""
    if conversation_history and len(conversation_history) > 0:
        conversation_context = "\n\nPrevious Conversation:\n"
        for msg in conversation_history[-5:]:  # Last 5 messages for context
            role_label = "Customer" if msg["role"] == "user" else "You"
            conversation_context += f"{role_label}: {msg['content']}\n"
        conversation_context += "\n"

    # Create user message with context
    user_message = f"""
{conversation_context}
Retrieved Information:
{context}

Current Customer Question: {query}

Provide a helpful, natural response based on the information above. If you need to refer to the conversation history, do so naturally.
"""

    # Call LLM based on provider
    if LLM_PROVIDER == "openai":
        return call_openai_rag(system_prompt, user_message)
    elif LLM_PROVIDER == "anthropic":
        return call_anthropic_rag(system_prompt, user_message)
    elif LLM_PROVIDER == "gemini":
        return call_gemini_rag(system_prompt, user_message)
    elif LLM_PROVIDER == "local":
        return call_local_llm_rag(system_prompt, user_message)
    else:
        return "Error: Unknown LLM provider"


def call_local_llm_rag(system_prompt: str, user_message: str) -> str:
    """Call local LLM via Ollama for RAG"""
    import requests
    
    url = os.getenv("LOCAL_LLM_URL", "http://localhost:11434") + "/api/generate"
    
    full_prompt = f"""{system_prompt}

{user_message}

Provide a helpful, natural language response:"""

    payload = {
        "model": "llama3.2",
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 500
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["response"].strip()
    except Exception as e:
        return f"Error generating response: {str(e)}"


def call_openai_rag(system_prompt: str, user_message: str) -> str:
    """Call OpenAI for RAG"""
    from openai import OpenAI
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.3,
        max_tokens=500
    )
    
    return response.choices[0].message.content.strip()


def call_anthropic_rag(system_prompt: str, user_message: str) -> str:
    """Call Anthropic Claude for RAG"""
    import anthropic
    
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=500,
        temperature=0.3,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )
    
    return response.content[0].text.strip()


def call_gemini_rag(system_prompt: str, user_message: str) -> str:
    """Call Google Gemini for RAG"""
    from google import genai
    from google.genai import types
    
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    full_prompt = f"{system_prompt}\n\n{user_message}"
    
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=500,
            )
        )
        return response.text.strip()
    except:
        return "Error: Gemini API quota exceeded. Please use local LLM."