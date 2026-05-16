from app.embeddings import EmbeddingModel
from app.vector_store import VectorStore
from app.llm import answer_with_context

embedder = EmbeddingModel()
store = VectorStore()

def query_documents(question: str, top_k: int = 4) -> dict:
    """Complete query pipeline: question → answer"""

    # Step 1: Embed the user's question
    query_vector = embedder.embed_query(question)

    # Step 2: Search Qdrant — returns parent pages
    contexts = store.search(query_vector, top_k=top_k)

    # Step 3: Handle empty results gracefully
    if not contexts:
        return {
            "answer": "I couldn't find any relevant information in the indexed documents. Please make sure a PDF has been uploaded and indexed first.",
            "sources": []
        }

    # Step 4: Generate answer with Groq
    answer = answer_with_context(question, contexts)

    return {
        "answer": answer,
        "sources": [
            {
                "source": c["source"],
                "page": c["page"],
                "relevance_score": round(c["score"], 3)
            }
            for c in contexts
        ]
    }