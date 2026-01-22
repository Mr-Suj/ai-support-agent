import faiss
import numpy as np
import os
import pickle
from typing import List, Optional
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")

# =============================
# Gemini Embedding Client
# =============================
_gemini_client = None


def get_gemini_client():
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _gemini_client


def generate_embeddings(texts: List[str]) -> np.ndarray:
    """
    Generate embeddings using Gemini (Production-safe)
    """
    client = get_gemini_client()
    embeddings = []

    for text in texts:
        res = client.models.embed_content(
            model="text-embedding-004",
            contents=text
        )
        embeddings.append(res.embedding)

    return np.array(embeddings).astype("float32")


# =============================
# VectorDB class
# =============================
class VectorDB:
    def __init__(self, index_path: str, metadata_path: str):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index = None
        self.metadata = []

        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            self._load_index()

    def _load_index(self):
        with open(self.metadata_path, "rb") as f:
            self.metadata = pickle.load(f)

        self.index = faiss.read_index(self.index_path)

    def _save_index(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "wb") as f:
            pickle.dump(self.metadata, f)

    def add_documents(self, documents: List[dict]):
        texts = [doc["text"] for doc in documents]
        embeddings = generate_embeddings(texts)

        if self.index is None:
            dim = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dim)

        self.index.add(embeddings)
        self.metadata.extend(documents)
        self._save_index()

    def search(self, query: str, top_k: int = 5) -> List[dict]:
        if self.index is None:
            return []

        query_embedding = generate_embeddings([query])

        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for idx in indices[0]:
            if idx < len(self.metadata):
                results.append(self.metadata[idx])

        return results


# =============================
# GLOBAL DB INSTANCE
# =============================
VECTOR_DB = VectorDB(
    index_path="database/vector.index",
    metadata_path="database/metadata.pkl"
)


# =============================
# BACKWARD-COMPATIBILITY API
# =============================

def search_products(query: str, top_k: int = 5) -> List[dict]:
    return VECTOR_DB.search(query, top_k)


def search_products_by_ids(product_ids: List[int], query: str = "") -> List[dict]:
    if not VECTOR_DB.metadata:
        return []

    return [
        item for item in VECTOR_DB.metadata
        if item.get("product_id") in product_ids
    ]


def get_product_by_id(product_id: int) -> Optional[dict]:
    if not VECTOR_DB.metadata:
        return None

    for item in VECTOR_DB.metadata:
        if item.get("product_id") == product_id:
            return item

    return None
