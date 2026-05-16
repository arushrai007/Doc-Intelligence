from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil, os
from app.ingest_pipeline import index_pdf
from app.retriever import query_documents
from app.vector_store import VectorStore

app = FastAPI(
    title="Doc Intelligence API",
    description="Multi-modal RAG pipeline with parent-document retrieval",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

store = VectorStore()

class QueryRequest(BaseModel):
    question: str
    top_k: int = 4

class QueryResponse(BaseModel):
    answer: str
    sources: list


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "doc-intelligence"}


@app.get("/stats")
async def get_stats():
    try:
        return store.get_stats()
    except Exception as e:
        return {"total_vectors": 0, "total_documents": 0, "documents": [], "error": str(e)}


@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files accepted")

    upload_dir = "data/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = f"{upload_dir}/{file.filename}"

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        index_pdf(file_path)
        return {"message": f"Successfully indexed: {file.filename}"}
    except Exception as e:
        raise HTTPException(500, f"Indexing failed: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(400, "Question cannot be empty")
    try:
        result = query_documents(request.question, request.top_k)
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(500, f"Query failed: {str(e)}")


@app.delete("/delete-doc/{filename}")
async def delete_document(filename: str):
    try:
        store.delete_by_source(filename)
        return {"message": f"Deleted: {filename}"}
    except Exception as e:
        raise HTTPException(500, f"Delete failed: {str(e)}")


@app.delete("/reset")
async def reset_all():
    try:
        store.delete_collection()
        return {"message": "Collection reset. All documents removed."}
    except Exception as e:
        raise HTTPException(500, f"Reset failed: {str(e)}")