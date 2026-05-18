FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only torch first (much smaller than GPU version)
RUN pip install --no-cache-dir torch==2.2.0+cpu --extra-index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir \
    pymupdf==1.24.0 \
    sentence-transformers==2.7.0 \
    qdrant-client==1.9.0 \
    langchain==0.2.0 \
    langchain-groq==0.1.0 \
    fastapi==0.111.0 \
    uvicorn==0.30.0 \
    python-dotenv==1.0.1 \
    python-multipart==0.0.9 \
    groq==0.4.2

# Pre-download the embedding model during build
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Copy application code
COPY . .

RUN mkdir -p data/uploads

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]