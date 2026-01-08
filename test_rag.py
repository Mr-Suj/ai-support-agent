from services.intent_classifier import classify_intent
from services.retriever import retrieve
from services.rag_engine import generate_response

print("="*70)
print("TESTING END-TO-END RAG PIPELINE")
print("="*70)

# Test queries
test_queries = [
    "Where is my order?",
    "Tell me about the Samsung Galaxy S23 features",
    "What's the current price of the phone I ordered last month?",
    "Do you have wireless headphones with good noise cancellation?",
    "When will my package arrive?",
]

for query in test_queries:
    print(f"\n{'='*70}")
    print(f"❓ User Query: '{query}'")
    print(f"{'='*70}\n")
    
    # Step 1: Classify intent
    print("🔍 Step 1: Classifying intent...")
    intent_result = classify_intent(query)
    intent = intent_result['intent']
    entities = intent_result['entities']
    print(f"   ✅ Intent: {intent}")
    
    # Step 2: Retrieve relevant data
    print("\n📊 Step 2: Retrieving data...")
    retrieval_result = retrieve(
        intent=intent,
        query=query,
        entities=entities,
        user_email="john@example.com"
    )
    print(f"   ✅ Data Source: {retrieval_result['data_source']}")
    print(f"   📄 Context Length: {len(retrieval_result['context'])} characters")
    
    # Step 3: Generate response using RAG
    print("\n🤖 Step 3: Generating response with RAG...")
    response = generate_response(
        query=query,
        context=retrieval_result['context'],
        intent=intent
    )
    
    print(f"\n💬 AI Response:")
    print("-" * 70)
    print(response)
    print("-" * 70)
    
    print("\n" + "="*70)

print("\n✅ RAG pipeline test complete!")
print("="*70)