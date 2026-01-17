from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import pickle
from typing import List, Optional

# =============================
# Lazy-loaded embedding model
# =============================
_embedding_model = None


def get_embedding_model():
    """
    Lazily load the embedding model to avoid Railway build timeouts.
    """
    global _embedding_model

    if _embedding_model is None:
        print("Loading embedding model (lazy)...")
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        print("✅ Embedding model loaded!")

    return _embedding_model


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
        model = get_embedding_model()

        texts = [doc["text"] for doc in documents]
        embeddings = model.encode(texts, convert_to_numpy=True)
        embeddings = np.array(embeddings).astype("float32")

        if self.index is None:
            dim = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dim)

        self.index.add(embeddings)
        self.metadata.extend(documents)
        self._save_index()

    def search(self, query: str, top_k: int = 5) -> List[dict]:
        if self.index is None:
            return []

        model = get_embedding_model()
        query_embedding = model.encode([query], convert_to_numpy=True)
        query_embedding = np.array(query_embedding).astype("float32")

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
# (Required by retriever.py)
# =============================

def search_products(query: str, top_k: int = 5) -> List[dict]:
    return VECTOR_DB.search(query, top_k)


def search_products_by_ids(product_ids: List[int]) -> List[dict]:
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
