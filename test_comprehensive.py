import requests
import json

API_URL = "http://localhost:8000/api/v1/chat"

print("="*80)
print("COMPREHENSIVE TESTING - EDGE CASES & ERROR HANDLING")
print("="*80)

# Test cases including edge cases
test_cases = [
    # === VALID QUERIES ===
    {
        "category": "✅ VALID - Order Status",
        "query": "Where is my order?",
        "should_succeed": True
    },
    {
        "category": "✅ VALID - Specific Tracking",
        "query": "Track order TRACK123456",
        "should_succeed": True
    },
    {
        "category": "✅ VALID - Product Info",
        "query": "Tell me about Dell XPS 13 laptop",
        "should_succeed": True
    },
    {
        "category": "✅ VALID - Product Comparison",
        "query": "Compare Samsung Galaxy S23 and Apple iPad Air",
        "should_succeed": True
    },
    {
        "category": "✅ VALID - Hybrid Query",
        "query": "What features does the laptop I purchased have?",
        "should_succeed": True
    },
    
    # === EDGE CASES ===
    {
        "category": "⚠️ EDGE - Empty Query",
        "query": "",
        "should_succeed": False,
        "expected_error": "Query cannot be empty"
    },
    {
        "category": "⚠️ EDGE - Only Whitespace",
        "query": "    ",
        "should_succeed": False,
        "expected_error": "Query cannot be empty"
    },
    {
        "category": "⚠️ EDGE - Invalid Tracking Number",
        "query": "Track order INVALID999",
        "should_succeed": True,  # Should succeed but say "not found"
        "check_response": lambda r: "not found" in r.lower() or "no order" in r.lower()
    },
    {
        "category": "⚠️ EDGE - Non-existent Product",
        "query": "Tell me about the SuperUltraMega Phone 5000",
        "should_succeed": True,  # Should succeed but give best match or say not found
    },
    {
        "category": "⚠️ EDGE - Ambiguous Query",
        "query": "hello",
        "should_succeed": True  # Should handle gracefully
    },
    {
        "category": "⚠️ EDGE - Very Long Query",
        "query": "Can you please tell me " + "very " * 100 + "detailed information about all products?",
        "should_succeed": True
    },
]

results = {
    "passed": 0,
    "failed": 0,
    "total": len(test_cases)
}

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*80}")
    print(f"Test {i}/{len(test_cases)}: {test['category']}")
    print(f"{'='*80}")
    print(f"📝 Query: '{test['query'][:100]}{'...' if len(test['query']) > 100 else ''}'")
    
    try:
        response = requests.post(
            API_URL,
            json={
                "query": test['query'],
                "user_email": "john@example.com"
            },
            timeout=30
        )
        
        if test['should_succeed']:
            if response.status_code == 200:
                data = response.json()
                
                # Check custom validation if provided
                if 'check_response' in test:
                    if test['check_response'](data['response']):
                        print(f"✅ PASSED - Correct behavior")
                        results['passed'] += 1
                    else:
                        print(f"❌ FAILED - Response doesn't meet criteria")
                        results['failed'] += 1
                else:
                    print(f"✅ PASSED")
                    print(f"   Intent: {data['intent']}")
                    print(f"   Response: {data['response'][:150]}...")
                    results['passed'] += 1
            else:
                print(f"❌ FAILED - Expected success but got HTTP {response.status_code}")
                results['failed'] += 1
        else:
            # Should fail
            if response.status_code != 200:
                error_data = response.json()
                print(f"✅ PASSED - Correctly rejected")
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                results['passed'] += 1
            else:
                print(f"❌ FAILED - Should have been rejected")
                results['failed'] += 1
    
    except requests.exceptions.Timeout:
        print(f"⏱️ TIMEOUT - LLM took too long")
        results['failed'] += 1
    except Exception as e:
        print(f"❌ FAILED - Exception: {str(e)}")
        results['failed'] += 1

# Summary
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)
print(f"Total Tests: {results['total']}")
print(f"✅ Passed: {results['passed']}")
print(f"❌ Failed: {results['failed']}")
print(f"Success Rate: {(results['passed']/results['total']*100):.1f}%")
print("="*80)