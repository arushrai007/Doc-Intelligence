from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Models in priority order — falls back if one hits rate limit
MODELS = [
    "llama-3.1-8b-instant",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "llama-3.3-70b-versatile",
]

def answer_with_context(query: str, contexts: list) -> str:
    """Send retrieved context + user query to Groq LLM."""

    context_str = ""
    for ctx in contexts:
        context_str += f"\n--- Source: {ctx['source']}, Page {ctx['page']} ---\n"
        context_str += ctx["parent_content"] + "\n"

    system_prompt = """You are a professional document analysis assistant.
Answer questions based ONLY on the provided document context.
If the answer is not in the context, say "I couldn't find that in the provided documents."
Always cite your source (document name and page number)."""

    user_message = f"""Context from documents:
{context_str}

User question: {query}

Answer based on the context above:"""

    last_error = None
    for model in MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                max_tokens=1000,
            )
            print(f"LLM answered using model: {model}")
            return response.choices[0].message.content
        except Exception as e:
            print(f"Model {model} failed: {e}")
            last_error = e
            continue

    raise Exception(f"All models failed. Last error: {last_error}")