from app.ingest import extract_pages, create_child_chunks
from app.embeddings import EmbeddingModel
from app.vector_store import VectorStore

# Initialize once (expensive operations)
#If inside function: it reloads every request. Bad for performance.
embedder = EmbeddingModel()
store = VectorStore()

def index_pdf(pdf_path: str):
    """Full pipeline: PDF → chunks → vectors → Qdrant"""
    print(f"\n📄 Processing: {pdf_path}")
    
    # Step 1: Extract parent pages FOREX: PAGE1 PAGE2 ....
    pages = extract_pages(pdf_path)
    print(f"  Extracted {len(pages)} pages")
    
    # Step 2: Create child chunks (with parent refs)
    chunks = create_child_chunks(pages, chunk_size=300)
    print(f"  Created {len(chunks)} child chunks")
    
    # Step 3: Embed all child chunks
    texts = [c["text"] for c in chunks] #EXTRACT TEXTS CHUNKS ONLY
    embeddings = embedder.embed_texts(texts) #converts chunks into vectors
    print(f"  Generated {len(embeddings)} embeddings")
    
    # Step 4: Store in Qdrant
    store.upsert_chunks(chunks, embeddings) #now qdrant stores vectors metadata and parent documents
    print(f"  ✅ Indexed successfully!")