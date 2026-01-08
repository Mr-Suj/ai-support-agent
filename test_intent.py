from services.intent_classifier import classify_intent

print("="*60)
print("TESTING INTENT CLASSIFICATION")
print("="*60)

# Test queries
test_queries = [
    "Where is my order?",
    "Track order TRACK123456",
    "Tell me about Samsung Galaxy S23",
    "Do you have wireless headphones with noise cancellation?",
    "What's the current price of the laptop I bought last month?",
    "Does the phone I ordered recently support fast charging?",
    "Show me tablets under $600",
    "When will my package arrive?",
]

for query in test_queries:
    print(f"\n📝 Query: '{query}'")
    result = classify_intent(query)
    print(f"   ✅ Intent: {result['intent']}")
    print(f"   💡 Reasoning: {result['reasoning']}")
    if result['entities']:
        print(f"   📌 Entities: {result['entities']}")
    print()

print("="*60)
print("✅ Intent classification test complete!")
print("="*60)