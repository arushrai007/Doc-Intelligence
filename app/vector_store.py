from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct
)
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

COLLECTION_NAME = os.getenv("COLLECTION_NAME", "doc_intelligence")
VECTOR_DIM = 384  # Must match embedding model output

class VectorStore:
    def __init__(self):
        # Connect to Qdrant Cloud
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
        )
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        collections = [c.name for c in 
                       self.client.get_collections().collections]
        
        if COLLECTION_NAME not in collections:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=VECTOR_DIM,
                    distance=Distance.COSINE  # Cosine similarity search
                )
            )
            print(f"Created collection: {COLLECTION_NAME}")
        else:
            print(f"Collection exists: {COLLECTION_NAME}")
    
    def upsert_chunks(self, chunks: list, embeddings: list):
        """
        Store child chunks + their embeddings.
        The parent_content (full page) is stored in the payload.
        """
        points = []
        for chunk, embedding in zip(chunks, embeddings):
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "text": chunk["text"],               # child chunk
                    "parent_content": chunk["parent_content"],  # FULL page
                    "source": chunk["source"],
                    "page_num": chunk["parent_page"],
                    "chunk_id": chunk["chunk_id"],
                }
            ))
        
        # Batch upload (100 points per request)
        self.client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        print(f"Uploaded {len(points)} chunks to Qdrant")
    
    def search(self, query_vector: list, top_k: int = 5) -> list:
        """
        Find the top_k most similar chunks.
        Returns parent_content (full page) for context.
        """
        results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=top_k,
            with_payload=True
        )
        
        # Return parent content, not child chunks!
        # This is the Parent-Document Retrieval magic
        contexts = []
        for r in results.points:
            contexts.append({
                "parent_content": r.payload["parent_content"],
                "source": r.payload["source"],
                "page": r.payload["page_num"],
                "score": r.score,
                "child_text": r.payload["text"],
            })
        return contexts