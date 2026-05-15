import streamlit as st
import requests

# ---- Page config ----
st.set_page_config(
    page_title="Doc Intelligence",
    page_icon="📄",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000" 

# ---- Header ----
st.title("📄 Doc Intelligence Pipeline")
st.caption("Multi-modal RAG with Parent-Document Retrieval")

# ---- Sidebar: Upload ----
with st.sidebar:
    st.header("Upload Documents")
    uploaded_file = st.file_uploader(
        "Choose a PDF", type=["pdf"]
    )
    
    if uploaded_file and st.button("Index Document"):
        with st.spinner("Processing PDF..."):
            response = requests.post(
                f"{API_URL}/ingest",
                files={"file": (uploaded_file.name, 
                                uploaded_file, 
                                "application/pdf")}
            )
        if response.status_code == 200:
            st.success(f"✅ {uploaded_file.name} indexed!")
        else:
            st.error(f"Error: {response.text}")
    
    st.divider()
    top_k = st.slider("Pages to retrieve", 1, 10, 4)

# ---- Main: Query ----
st.subheader("Ask a Question")

# Chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("sources"):
            with st.expander("📚 Sources"):
                for s in msg["sources"]:
                    st.markdown(
                        f"**{s['source']}** — Page {s['page']} "
                        f"(relevance: {s['relevance_score']})"
                    )

# Input
if question := st.chat_input("Ask about your documents..."):
    # Show user message
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )
    with st.chat_message("user"):
        st.write(question)
    
    # Get answer
    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            resp = requests.post(
                f"{API_URL}/query",
                json={"question": question, "top_k": top_k}
            )
        
        if resp.status_code == 200:
            data = resp.json()
            st.write(data["answer"])
            
            with st.expander("📚 Sources"):
                for s in data["sources"]:
                    st.markdown(
                        f"**{s['source']}** — Page {s['page']} "
                        f"(score: {s['relevance_score']})"
                    )
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": data["answer"],
                "sources": data["sources"]
            })
        else:
            st.error("Error connecting to backend")