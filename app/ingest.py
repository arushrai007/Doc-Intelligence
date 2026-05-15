import fitz #module name for pymupdf 
import os 
from pathlib import Path #used for cleaner file path handling 
from typing import List, Dict 

def extract_pages(pdf_path: str) -> List[Dict]:
    """
    Extract each page as a 'parent' document.
    Returns a list of dicts with page text + metadata.
    """
    doc = fitz.open(pdf_path)
    pages = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Extract plain text
        text = page.get_text("text")
        
        # Extract tables (returns list of table objects)
        tables = page.find_tables()
        table_text = ""
        for table in tables:
            # Convert table to markdown string
            df = table.to_pandas()
            table_text += df.to_markdown() + "\n\n"
        
        pages.append({
            "page_num": page_num + 1,
            "text": text,
            "tables": table_text,
            "full_content": text + "\n" + table_text,
            "source": Path(pdf_path).name,
        })
    
    doc.close()
    return pages

def create_child_chunks(pages: List[Dict], 
                        chunk_size: int = 300) -> List[Dict]:
    """
    Split each parent page into smaller child chunks.
    Each child chunk stores a reference to its parent page.
    THIS IS THE KEY INNOVATION.
    """
    children = []
    
    for page in pages:
        text = page["full_content"]
        words = text.split()
        
        # Sliding window chunking with 50-word overlap
        for i in range(0, len(words), chunk_size - 50):
            chunk_words = words[i : i + chunk_size]
            chunk_text = " ".join(chunk_words)
            
            if len(chunk_text.strip()) < 50:
                continue  # Skip tiny fragments
            
            children.append({
                "text": chunk_text,          # Small chunk for embedding
                "parent_page": page["page_num"],
                "parent_content": page["full_content"],  # FULL page
                "source": page["source"],
                "chunk_id": f"{page['source']}_p{page['page_num']}_c{i}"
            })
    
    return children