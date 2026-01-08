from database.vector_db import init_vector_db, search_products, get_product_by_id, search_products_by_ids

# Initialize vector database
print("="*60)
print("INITIALIZING VECTOR DATABASE")
print("="*60)
init_vector_db()

print("\n" + "="*60)
print("TESTING VECTOR SEARCH")
print("="*60)

# Test 1: Semantic search for phones
print("\n1️⃣ Search: 'phone with good camera'")
results = search_products("phone with good camera", top_k=2)
for i, result in enumerate(results, 1):
    product = result['product']
    score = result['similarity_score']
    print(f"\n   Result {i} (Score: {score:.3f}):")
    print(f"   Name: {product['name']}")
    print(f"   Price: ${product['price']}")
    print(f"   Category: {product['category']}")

# Test 2: Search for audio products
print("\n2️⃣ Search: 'wireless headphones with noise cancellation'")
results = search_products("wireless headphones with noise cancellation", top_k=2)
for i, result in enumerate(results, 1):
    product = result['product']
    score = result['similarity_score']
    print(f"\n   Result {i} (Score: {score:.3f}):")
    print(f"   Name: {product['name']}")
    print(f"   Price: ${product['price']}")

# Test 3: Get product by ID
print("\n3️⃣ Get product by ID: PROD003")
product = get_product_by_id("PROD003")
if product:
    print(f"   Name: {product['name']}")
    print(f"   Description: {product['description'][:100]}...")

# Test 4: Hybrid search (by IDs with query)
print("\n4️⃣ Hybrid Search: Products PROD001, PROD003 filtered by 'tablet'")
products = search_products_by_ids(["PROD001", "PROD003"], query="tablet for drawing")
for product in products:
    print(f"   - {product['name']}")

print("\n✅ Vector DB test complete!")