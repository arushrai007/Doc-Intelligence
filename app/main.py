from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware #Without CORS: browser blocks API calls
from pydantic import BaseModel #request/response validation
import shutil
import os
from app.ingest_pipeline import index_pdf
from app.retriever import query_documents

# Create the FastAPI app
app = FastAPI(
    title="Doc Intelligence API",
    description="Multi-modal RAG pipeline with parent-document retrieval",
    version="1.0.0"
)

# Allow Streamlit frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #Allows all frontend origins.
    allow_methods=["*"],
    allow_headers=["*"], 
)

# Pydantic model for query request
#basically a structure of ans
class QueryRequest(BaseModel):
    question: str
    top_k: int = 4  # Default: retrieve 4 parent pages

class QueryResponse(BaseModel):
    answer: str
    sources: list

# ---------- ENDPOINTS ----------

@app.get("/health")
async def health_check():
    """Simple health check — AWS load balancer pings this."""
    return {"status": "healthy", "service": "doc-intelligence"}


@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """
    Upload a PDF. Extracts, embeds, and indexes it into Qdrant.
    The UploadFile type handles multipart/form-data automatically.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files accepted")
    
    # Save uploaded file temporarily
    upload_dir = "data/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = f"{upload_dir}/{file.filename}"
    
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    try:
        index_pdf(file_path) #This calls: complete RAG indexing pipeline
        return {"message": f"Successfully indexed: {file.filename}"}
    except Exception as e:
        raise HTTPException(500, f"Indexing failed: {str(e)}")
    finally:
        os.remove(file_path)  # Clean up temp file


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Ask a question. Returns an answer + source citations.
    """
    if not request.question.strip():
        raise HTTPException(400, "Question cannot be empty")
    
    try:
        result = query_documents(request.question, request.top_k)
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(500, f"Query failed: {str(e)}")