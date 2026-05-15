
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

# This downloads the model once (~80MB) to your local machine
# After first run, it's cached and loads instantly
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

class EmbeddingModel:
    def __init__(self):
        print("Loading embedding model... (first time takes ~30 sec)")
        self.model = SentenceTransformer(MODEL_NAME)
        print(f"Model loaded! Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
        # Will print: Embedding dimension: 384
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Convert a list of text strings into a list of vectors.
        Each vector is a list of 384 floats.
        """
        embeddings = self.model.encode(
            texts,
            batch_size=32,       # Process 32 chunks at once
            show_progress_bar=True,
            normalize_embeddings=True  # L2 normalize for cosine similarity
        )
        return embeddings.tolist()
    
    def embed_query(self, query: str) -> List[float]:
        """Embed a single user query for search."""
        embedding = self.model.encode(
            query, 
            normalize_embeddings=True
        )
        return embedding.tolist()


# Quick test — run this file directly to verify
if __name__ == "__main__":
    model = EmbeddingModel()
    
    texts = ["What is machine learning?", 
             "ML is a subset of AI",
             "I love cooking pasta"]
    
    vecs = model.embed_texts(texts)
    print(f"Shape: {len(vecs)} vectors, each {len(vecs[0])} dims")
    
    # Cosine similarity (dot product since normalized)
    v1, v2, v3 = np.array(vecs[0]), np.array(vecs[1]), np.array(vecs[2])
    print(f"ML ↔ AI similarity: {np.dot(v1,v2):.3f}")   # ~0.82 (high)
    print(f"ML ↔ pasta similarity: {np.dot(v1,v3):.3f}") # ~0.04 (low)