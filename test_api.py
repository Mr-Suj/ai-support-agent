import requests
import json

API_URL = "http://localhost:8000/api/v1/chat"

# Test queries
test_cases = [
    {
        "name": "Order Status Query",
        "query": "Where is my order?",
        "expected_intent": "ORDER_DETAILS"
    },
    {
        "name": "Product Information Query",
        "query": "Tell me about Samsung Galaxy S23 features",
        "expected_intent": "PRODUCT_DETAILS"
    },
    {
        "name": "Hybrid Query (Order + Product)",
        "query": "What's the current price of the phone I ordered last month?",
        "expected_intent": "ORDER_PRODUCT_DETAILS"
    },
    {
        "name": "Product Search Query",
        "query": "Do you have wireless headphones with noise cancellation?",
        "expected_intent": "PRODUCT_DETAILS"
    }
]

print("="*80)
print("TESTING FASTAPI CHAT ENDPOINT")
print("="*80)

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*80}")
    print(f"Test {i}: {test['name']}")
    print(f"{'='*80}")
    print(f"📝 Query: '{test['query']}'")
    print(f"🎯 Expected Intent: {test['expected_intent']}")
    
    # Send POST request
    try:
        response = requests.post(
            API_URL,
            json={
                "query": test['query'],
                "user_email": "john@example.com"
            },
            timeout=30
        )
        
        # Parse response
        if response.status_code == 200:
            data = response.json()
            
            # Check if intent matches
            intent_match = "✅" if data['intent'] == test['expected_intent'] else "❌"
            
            print(f"\n{intent_match} Detected Intent: {data['intent']}")
            print(f"📊 Data Source: {data['data_source']}")
            print(f"✅ Success: {data['success']}")
            
            print(f"\n💬 AI Response:")
            print("-" * 80)
            print(data['response'])
            print("-" * 80)
            
            if data.get('metadata'):
                print(f"\n📌 Metadata:")
                print(f"   - Context Length: {data['metadata'].get('context_length', 'N/A')} chars")
                print(f"   - Reasoning: {data['metadata'].get('reasoning', 'N/A')}")
        else:
            print(f"\n❌ Error: HTTP {response.status_code}")
            print(response.json())
    
    except requests.exceptions.Timeout:
        print("\n⏱️ Request timed out (LLM might be slow on first run)")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

print("\n" + "="*80)
print("✅ API TEST COMPLETE!")
print("="*80)