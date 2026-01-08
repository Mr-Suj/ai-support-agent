import requests
import json

API_URL = "http://localhost:8000/api/v1/chat"

print("="*80)
print("TESTING CONVERSATION HISTORY & CONTEXT AWARENESS")
print("="*80)

# Start a new conversation
session_id = "test_session_001"

# Conversation flow
conversation = [
    "Where is my order?",
    "Tell me about the latest order",
    "What products were in it?",
    "Tell me more about the headphones",
    "Do they have noise cancellation?",
]

print(f"\n🆔 Session ID: {session_id}\n")

for i, query in enumerate(conversation, 1):
    print(f"{'='*80}")
    print(f"Message {i}/{len(conversation)}")
    print(f"{'='*80}")
    print(f"👤 User: {query}")
    
    response = requests.post(
        API_URL,
        json={
            "query": query,
            "user_email": "john@example.com",
            "session_id": session_id
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"🤖 Bot: {data['response']}\n")
        print(f"📊 Intent: {data['intent']}")
        print(f"📚 Data Source: {data['data_source']}")
        print(f"💬 Conversation Length: {data['metadata'].get('conversation_length', 0)} messages")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.json())
    
    print()

# Get full conversation history
print(f"{'='*80}")
print("RETRIEVING FULL CONVERSATION HISTORY")
print(f"{'='*80}\n")

history_response = requests.get(f"http://localhost:8000/api/v1/conversation/{session_id}")

if history_response.status_code == 200:
    history_data = history_response.json()
    print(f"Total Messages: {history_data['message_count']}\n")
    
    for msg in history_data['messages']:
        role_emoji = "👤" if msg['role'] == "user" else "🤖"
        print(f"{role_emoji} {msg['role'].upper()}: {msg['content'][:100]}...")
        print()

print("="*80)
print("✅ Conversation history test complete!")
print("="*80)