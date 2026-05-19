from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue
)
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

COLLECTION_NAME = os.getenv("COLLECTION_NAME", "doc_intelligence")
VECTOR_DIM = 384

class VectorStore:
    def __init__(self):
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
            timeout=30,
        )
        try:
            self._ensure_collection()
        except Exception as e:
            print(f"WARNING: Qdrant connection issue on startup: {e}")

    def _ensure_collection(self):
        collections = [c.name for c in self.client.get_collections().collections]
        if COLLECTION_NAME not in collections:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=VECTOR_DIM,
                    distance=Distance.COSINE
                )
            )
            print(f"Created collection: {COLLECTION_NAME}")
        else:
            print(f"Collection exists: {COLLECTION_NAME}")

    def upsert_chunks(self, chunks: list, embeddings: list):
        points = []
        for chunk, embedding in zip(chunks, embeddings):
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "text": chunk["text"],
                    "parent_content": chunk["parent_content"],
                    "source": chunk["source"],
                    "page_num": chunk["parent_page"],
                    "chunk_id": chunk["chunk_id"],
                }
            ))
        self.client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"Uploaded {len(points)} chunks to Qdrant")

    def search(self, query_vector: list, top_k: int = 5) -> list:
        print("--- SEARCH CALLED ---")

        results = None

        # Try new API first (qdrant-client >= 1.7.0)
        if hasattr(self.client, 'query_points'):
            try:
                response = self.client.query_points(
                    collection_name=COLLECTION_NAME,
                    query=query_vector,
                    limit=top_k,
                    with_payload=True,
                )
                results = response.points
                print(f"query_points SUCCESS: {len(results)} results")
            except Exception as e:
                print(f"query_points failed: {e}")
                results = None

        # Fallback to old API (qdrant-client < 1.7.0)
        if results is None and hasattr(self.client, 'search'):
            try:
                results = self.client.search(
                    collection_name=COLLECTION_NAME,
                    query_vector=query_vector,
                    limit=top_k,
                    with_payload=True,
                )
                print(f"search SUCCESS: {len(results)} results")
            except Exception as e:
                print(f"search failed: {e}")
                results = None

        # Last resort — use REST API directly
        if results is None:
            try:
                import requests as req
                url = f"{os.getenv('QDRANT_URL')}/collections/{COLLECTION_NAME}/points/search"
                headers = {"api-key": os.getenv("QDRANT_API_KEY"), "Content-Type": "application/json"}
                payload = {"vector": query_vector, "limit": top_k, "with_payload": True}
                resp = req.post(url, json=payload, headers=headers)
                data = resp.json()
                results = data.get("result", [])
                print(f"REST API SUCCESS: {len(results)} results")

                contexts = []
                for r in results:
                    payload_data = r.get("payload", {})
                    contexts.append({
                        "parent_content": payload_data.get("parent_content", ""),
                        "source": payload_data.get("source", "unknown"),
                        "page": payload_data.get("page_num", 0),
                        "score": round(r.get("score", 0), 3),
                        "child_text": payload_data.get("text", ""),
                    })
                return contexts
            except Exception as e:
                print(f"REST API failed: {e}")
                raise Exception("All search methods failed")

        contexts = []
        for r in results:
            contexts.append({
                "parent_content": r.payload["parent_content"],
                "source": r.payload["source"],
                "page": r.payload["page_num"],
                "score": round(r.score, 3),
                "child_text": r.payload["text"],
            })
        return contexts

    def get_stats(self) -> dict:
        try:
            info = self.client.get_collection(COLLECTION_NAME)
            total_vectors = info.vectors_count
            sources = set()
            offset = None
            while True:
                results, offset = self.client.scroll(
                    collection_name=COLLECTION_NAME,
                    limit=100,
                    offset=offset,
                    with_payload=["source"],
                    with_vectors=False,
                )
                for r in results:
                    if r.payload and "source" in r.payload:
                        sources.add(r.payload["source"])
                if offset is None:
                    break
            return {
                "total_vectors": total_vectors,
                "total_documents": len(sources),
                "documents": sorted(list(sources)),
            }
        except Exception as e:
            return {
                "total_vectors": 0,
                "total_documents": 0,
                "documents": [],
                "error": str(e)
            }

    def delete_by_source(self, filename: str):
        self.client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=Filter(
                must=[FieldCondition(
                    key="source",
                    match=MatchValue(value=filename)
                )]
            )
        )
        print(f"Deleted all chunks from: {filename}")

    def delete_collection(self):
        self.client.delete_collection(COLLECTION_NAME)
        self._ensure_collection()
        print("Collection reset — all documents removed.")