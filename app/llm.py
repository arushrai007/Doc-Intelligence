#this file handles groq + llam3  for answer generation

from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def answer_with_context(query: str, contexts: list) -> str:
    """
    Send the retrieved context + user query to Groq's Llama 3.
    The context is the parent pages (full content with tables).
    """
    
    # Build context string from retrieved parent pages
    context_str = ""
    for i, ctx in enumerate(contexts):
        context_str += f"\n--- Source: {ctx['source']}, Page {ctx['page']} ---\n"
        context_str += ctx["parent_content"] + "\n"
    
    system_prompt = """You are a pro document analysis assistant.
Answer questions based ONLY on the provided document context.
If the answer is not in the context, say "I couldn't find that in the provided documents."
Always cite your source (document name and page number)."""
    
    user_message = f"""Context from documents:
{context_str}


User question: {query} 


Answer based on the context above:"""
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # Fast + free on Groq
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.1,   # Low = more factual, less creative
        max_tokens=1000,  #response size
    )
    
    return response.choices[0].message.content