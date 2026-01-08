import requests

API_URL = "http://localhost:8000/api/v1/chat"

# Organize by intent
intent_tests = {
    "ORDER_DETAILS": [
        "Where is my order?",
        "Track order TRACK123456",
        "When will my package arrive?",
        "Show me my recent orders",
        "What's the status of my delivery?"
    ],
    "PRODUCT_DETAILS": [
        "Tell me about Samsung Galaxy S23",
        "Do you have wireless headphones?",
        "What's the price of Dell XPS 13?",
        "Compare iPad and laptop",
        "Show me phones under $1000"
    ],
    "ORDER_PRODUCT_DETAILS": [
        "What's the current price of the phone I bought?",
        "Does the laptop I purchased support fast charging?",
        "Tell me about the headphones I ordered last month",
        "What features does my recent purchase have?",
        "Is the product I bought still available?"
    ]
}

print("="*80)
print("TESTING ALL INTENT CLASSIFICATIONS")
print("="*80)

intent_accuracy = {intent: {"correct": 0, "total": 0} for intent in intent_tests.keys()}

for expected_intent, queries in intent_tests.items():
    print(f"\n{'='*80}")
    print(f"Testing Intent: {expected_intent}")
    print(f"{'='*80}")
    
    for query in queries:
        print(f"\n📝 Query: '{query}'")
        
        try:
            response = requests.post(
                API_URL,
                json={"query": query, "user_email": "john@example.com"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                detected_intent = data['intent']
                
                intent_accuracy[expected_intent]["total"] += 1
                
                if detected_intent == expected_intent:
                    print(f"   ✅ Correct: {detected_intent}")
                    intent_accuracy[expected_intent]["correct"] += 1
                else:
                    print(f"   ❌ Wrong: Expected {expected_intent}, Got {detected_intent}")
            else:
                print(f"   ❌ API Error: {response.status_code}")
        
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")

# Summary
print("\n" + "="*80)
print("INTENT CLASSIFICATION ACCURACY")
print("="*80)

total_correct = 0
total_tests = 0

for intent, results in intent_accuracy.items():
    correct = results["correct"]
    total = results["total"]
    accuracy = (correct / total * 100) if total > 0 else 0
    
    total_correct += correct
    total_tests += total
    
    print(f"{intent:25} {correct}/{total} ({accuracy:.1f}%)")

overall_accuracy = (total_correct / total_tests * 100) if total_tests > 0 else 0
print(f"\n{'Overall Accuracy':25} {total_correct}/{total_tests} ({overall_accuracy:.1f}%)")
print("="*80)