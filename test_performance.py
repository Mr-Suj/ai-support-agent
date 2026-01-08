import requests
import time
import statistics

API_URL = "http://localhost:8000/api/v1/chat"

queries = [
    "Where is my order?",
    "Tell me about Samsung Galaxy S23",
    "What's the current price of the headphones I bought?"
]

print("="*80)
print("PERFORMANCE TESTING")
print("="*80)

response_times = []

for i in range(5):  # Run 5 times each
    for query in queries:
        print(f"\n🔄 Testing: '{query[:50]}...'")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                API_URL,
                json={"query": query, "user_email": "john@example.com"},
                timeout=60
            )
            
            end_time = time.time()
            elapsed = end_time - start_time
            response_times.append(elapsed)
            
            if response.status_code == 200:
                print(f"   ⏱️ Response Time: {elapsed:.2f}s")
            else:
                print(f"   ❌ Failed: HTTP {response.status_code}")
        
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

# Statistics
print("\n" + "="*80)
print("PERFORMANCE SUMMARY")
print("="*80)
print(f"Total Requests: {len(response_times)}")
print(f"Average Response Time: {statistics.mean(response_times):.2f}s")
print(f"Median Response Time: {statistics.median(response_times):.2f}s")
print(f"Min Response Time: {min(response_times):.2f}s")
print(f"Max Response Time: {max(response_times):.2f}s")
print(f"Std Deviation: {statistics.stdev(response_times):.2f}s")
print("="*80)