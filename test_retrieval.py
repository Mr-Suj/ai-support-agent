from services.intent_classifier import classify_intent
from services.retriever import retrieve

print("="*70)
print("TESTING RETRIEVAL LOGIC")
print("="*70)

# Test cases with expected intents
test_cases = [
    ("Where is my order?", "ORDER_DETAILS"),
    ("Tell me about Samsung Galaxy S23", "PRODUCT_DETAILS"),
    ("What's the current price of the phone I bought last month?", "ORDER_PRODUCT_DETAILS"),
]

for query, expected_intent in test_cases:
    print(f"\n{'='*70}")
    print(f"📝 Query: '{query}'")
    print(f"🎯 Expected Intent: {expected_intent}")
    print(f"{'='*70}")
    
    # Step 1: Classify intent
    intent_result = classify_intent(query)
    detected_intent = intent_result['intent']
    entities = intent_result['entities']
    
    print(f"\n✅ Detected Intent: {detected_intent}")
    
    # Step 2: Retrieve data
    retrieval_result = retrieve(
        intent=detected_intent,
        query=query,
        entities=entities,
        user_email="john@example.com"
    )
    
    print(f"📊 Data Source: {retrieval_result['data_source']}")
    print(f"\n📄 Context for LLM:\n")
    print(retrieval_result['context'][:500] + "..." if len(retrieval_result['context']) > 500 else retrieval_result['context'])
    print()

print("="*70)
print("✅ Retrieval test complete!")
print("="*70)