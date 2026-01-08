import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import os

# Initialize embedding model
print("Loading embedding model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Embedding model loaded!")

# Paths
PRODUCTS_FILE = "data/products.json"
INDEX_FILE = "data/faiss_index.bin"
METADATA_FILE = "data/product_metadata.pkl"


def load_products():
    """Load product data from JSON"""
    with open(PRODUCTS_FILE, 'r') as f:
        return json.load(f)


def create_product_text(product):
    """Convert product dict to searchable text"""
    text = f"""
    Product: {product['name']}
    Category: {product['category']}
    Price: ${product['price']}
    Description: {product['description']}
    Features: {', '.join(product['features'])}
    Specs: {json.dumps(product['specs'])}
    """
    return text.strip()


def init_vector_db():
    """Create FAISS index and store product embeddings"""
    
    # Load products
    products = load_products()
    print(f"📦 Loaded {len(products)} products")
    
    # Generate embeddings
    print("🔄 Generating embeddings...")
    product_texts = [create_product_text(p) for p in products]
    embeddings = embedding_model.encode(product_texts, show_progress_bar=True)
    
    # Create FAISS index
    dimension = embeddings.shape[1]  # 384 for all-MiniLM-L6-v2
    index = faiss.IndexFlatL2(dimension)  # L2 distance (Euclidean)
    index.add(embeddings.astype('float32'))
    
    # Save index
    faiss.write_index(index, INDEX_FILE)
    print(f"✅ FAISS index saved to {INDEX_FILE}")
    
    # Save metadata (product info)
    with open(METADATA_FILE, 'wb') as f:
        pickle.dump(products, f)
    print(f"✅ Product metadata saved to {METADATA_FILE}")
    
    return index, products


def load_vector_db():
    """Load existing FAISS index and metadata"""
    if not os.path.exists(INDEX_FILE) or not os.path.exists(METADATA_FILE):
        print("⚠️ Vector DB not found. Creating new one...")
        return init_vector_db()
    
    index = faiss.read_index(INDEX_FILE)
    with open(METADATA_FILE, 'rb') as f:
        products = pickle.load(f)
    
    print(f"✅ Loaded vector DB with {len(products)} products")
    return index, products


def search_products(query: str, top_k: int = 3):
    """Search for products using semantic similarity"""
    
    # Load index and metadata
    index, products = load_vector_db()
    
    # Generate query embedding
    query_embedding = embedding_model.encode([query]).astype('float32')
    
    # Search FAISS index
    distances, indices = index.search(query_embedding, top_k)
    
    # Get matching products
    results = []
    for idx, distance in zip(indices[0], distances[0]):
        product = products[idx]
        results.append({
            "product": product,
            "similarity_score": float(1 / (1 + distance))  # Convert distance to similarity
        })
    
    return results


def get_product_by_id(product_id: str):
    """Get specific product by ID"""
    _, products = load_vector_db()
    
    for product in products:
        if product['product_id'] == product_id:
            return product
    
    return None


def search_products_by_ids(product_ids: list, query: str = None):
    """
    Get products by IDs, optionally filtered by query relevance.
    Used for hybrid queries (SQL + Vector).
    """
    _, products = load_vector_db()
    
    # Filter products by IDs
    filtered_products = [p for p in products if p['product_id'] in product_ids]
    
    if not query:
        return filtered_products
    
    # If query provided, rank by relevance
    product_texts = [create_product_text(p) for p in filtered_products]
    query_embedding = embedding_model.encode([query]).astype('float32')
    product_embeddings = embedding_model.encode(product_texts).astype('float32')
    
    # Calculate similarities
    similarities = np.dot(product_embeddings, query_embedding.T).flatten()
    
    # Sort by similarity
    sorted_indices = np.argsort(similarities)[::-1]
    ranked_products = [filtered_products[i] for i in sorted_indices]
    
    return ranked_products