<div align="center">

# ◈ Doctel
### Multi-Modal AI Document Intelligence Pipeline

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-DC244C?style=for-the-badge)](https://qdrant.tech)
[![Groq](https://img.shields.io/badge/Groq-Llama_3-F55036?style=for-the-badge)](https://groq.com)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**Ask questions about your PDFs using semantic search + LLM reasoning**

[Live Demo](https://doc-intel.streamlit.app/) · [API Docs](https://doc-intelligence-r2kv.onrender.com/docs) · [Report Bug](https://github.com/arushrai007/Doc-Intelligence/issues)

<img src="https://raw.githubusercontent.com/arushrai007/Doc-Intelligence/main/assets/demo.png" alt="DocIntel Demo" width="800"/>

</div>

---

## 📌 What is DocIntel?

DocIntel is a production-grade **Retrieval-Augmented Generation (RAG)** system that lets you upload any PDF and ask natural language questions about it. Unlike simple keyword search, DocIntel understands the *meaning* of your question and retrieves the most relevant context — including full tables and figures.

```
You ask  →  "What was the Q3 revenue?"
DocIntel →  Finds the exact table, reads the full page, answers with citation
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                         │
│                    Streamlit Dashboard                       │
└──────────────────────┬──────────────────────────────────────┘
                       │  HTTP
┌──────────────────────▼──────────────────────────────────────┐
│                    FastAPI Backend                           │
│              /ingest  /query  /stats  /health               │
└──────┬───────────────┬─────────────────────────────────────┘
       │               │
┌──────▼──────┐  ┌─────▼──────────────────────────────────┐
│  PyMuPDF    │  │           RAG Pipeline                  │
│  PDF Parser │  │                                         │
│             │  │  Query → Embed → Search → LLM → Answer  │
│ Parent Docs │  │                                         │
│ Child Chunks│  └─────┬──────────────┬───────────────────┘
└─────────────┘        │              │
                ┌──────▼──────┐ ┌────▼────────┐
                │   Qdrant    │ │  Groq Cloud │
                │ Vector DB   │ │  Llama 3.1  │
                │ (Cloud)     │ │  (LLM)      │
                └─────────────┘ └─────────────┘
```

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🧠 **Parent-Document Retrieval** | Embeds small chunks for precision, retrieves full pages for context |
| 📊 **Table Understanding** | Extracts and queries tabular data that normal RAG systems miss |
| ⚡ **Sub-second Search** | Qdrant HNSW index returns nearest vectors in milliseconds |
| 🔄 **Model Fallback** | Auto-switches between Groq models if rate limit is hit |
| 🐳 **Dockerized** | One command to run anywhere |
| 🌐 **Production Deployed** | Live on Render + Streamlit Cloud |

---

## 🚀 The Innovation — Parent-Document Retrieval

Most RAG systems **fail at tables** because they retrieve tiny chunks that contain half a table — useless for answering financial or data questions.

DocIntel solves this with a two-level chunking strategy:

```
PDF Page (Parent) ──────────────────────────────────────────
│  Full page text including complete tables and figures      │
│                                                            │
│   Child Chunk 1  │  Child Chunk 2  │  Child Chunk 3       │
│   (300 words)    │  (300 words)    │  (300 words)          │
└────────────────────────────────────────────────────────────┘

Search:   User query → embed → find closest Child chunk
Retrieve: Return the full Parent page to the LLM

Result:   LLM sees the complete table, not just a fragment
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **PDF Parsing** | PyMuPDF | Extract text and tables locally |
| **Embeddings** | `all-MiniLM-L6-v2` | 384-dim semantic vectors, runs on CPU |
| **Vector DB** | Qdrant Cloud | HNSW-indexed similarity search |
| **LLM** | Groq (Llama 3.1 8B) | Ultra-fast inference, free tier |
| **Backend** | FastAPI | REST API with auto-generated docs |
| **Frontend** | Streamlit | Dark-themed dashboard |
| **Container** | Docker | Reproducible deployment |
| **Hosting** | Render + Streamlit Cloud | Free tier, zero cost |

**Total infrastructure cost: $0**

---

## 📦 Project Structure

```
doc-intelligence/
├── app/
│   ├── main.py              # FastAPI endpoints
│   ├── ingest.py            # PDF parsing + chunking
│   ├── ingest_pipeline.py   # Indexing orchestration
│   ├── embeddings.py        # HuggingFace embedding model
│   ├── vector_store.py      # Qdrant operations
│   ├── retriever.py         # Query pipeline
│   └── llm.py               # Groq LLM integration
├── frontend/
│   └── streamlit_app.py     # UI dashboard
├── data/
│   └── uploads/             # Temporary PDF storage
├── Dockerfile
├── requirements.txt
└── .env                     # API keys (never commit)
```

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.11+
- Docker
- Free accounts: [Qdrant Cloud](https://cloud.qdrant.io) · [Groq](https://console.groq.com)

### 1. Clone the repo
```bash
git clone https://github.com/arushrai007/Doc-Intelligence.git
cd Doc-Intelligence
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
```

Edit `.env`:
```env
GROQ_API_KEY=your_groq_key_here
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_key_here
COLLECTION_NAME=doc_intelligence
```

### 5. Run with Docker
```bash
docker build -t doc-intelligence .
docker run -p 8000:8000 --env-file .env doc-intelligence
```

### 6. Run Streamlit
```bash
streamlit run frontend/streamlit_app.py
```

Open `http://localhost:8501` 🎉

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/stats` | Qdrant storage statistics |
| `POST` | `/ingest` | Upload and index a PDF |
| `POST` | `/query` | Ask a question |
| `DELETE` | `/delete-doc/{filename}` | Remove a document |
| `DELETE` | `/reset` | Wipe all data |

### Example — Query
```bash
curl -X POST "https://doc-intelligence-r2kv.onrender.com/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the total revenue?", "top_k": 4}'
```

Response:
```json
{
  "answer": "Based on the annual report (Page 14), total revenue was $4.2B...",
  "sources": [
    {"source": "annual_report.pdf", "page": 14, "relevance_score": 0.94}
  ]
}
```

---

## 🌐 Deployment

### Backend — Render
1. Push to GitHub
2. Connect repo on [render.com](https://render.com)
3. Set runtime to **Docker**, port **8000**
4. Add environment variables
5. Deploy ✓

### Frontend — Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect GitHub repo
3. Set main file: `frontend/streamlit_app.py`
4. Deploy ✓

---

## 🗺️ Roadmap

- [ ] Multi-user session isolation with user_id filtering
- [ ] OCR support for scanned/image PDFs
- [ ] Re-ranking with cross-encoder for better precision
- [ ] Document comparison across multiple PDFs
- [ ] Chat history persistence
- [ ] Support for DOCX, TXT, CSV files

---

## 🤝 Contributing

Pull requests welcome. For major changes please open an issue first.

```bash
git checkout -b feature/your-feature
git commit -m "add: your feature"
git push origin feature/your-feature
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built with ❤️ by [Arush Rai](https://github.com/arushrai007)

⭐ Star this repo if you found it helpful

</div>