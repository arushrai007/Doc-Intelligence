import streamlit as st
import requests

# ---- Page config ----
st.set_page_config(
    page_title="Doc Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Custom Premium UI Styling ----
st.markdown("""
    <style>
    /* Main Background & Fonts */
    .main {
        background-color: #0e1117;
    }
    
    /* Sleek Title Treatment */
    .main-title {
        font-size: 3rem !important;
        font-weight: 800 !important;
        background: linear-gradient(45deg, #FF4B4B, #FF8383);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    /* Custom Card Containers for Sources */
    .source-card {
        background-color: #1e222b;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
        border-left: 4px solid #FF4B4B;
    }
    
    /* Target the Chat input bar styling */
    .stChatInputContainer {
        border-radius: 20px !important;
    }
    </style>
""", unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8000" 

# ---- Sidebar: Upload & Settings ----
with st.sidebar:
    st.markdown("<h2 style='color: #FF4B4B;'>⚙️ Control Panel</h2>", unsafe_allow_html=True)
    st.write("Manage your knowledge base and parameters.")
    
    with st.container(border=True):
        st.subheader("📁 Upload Space")
        uploaded_file = st.file_uploader(
            "Upload reference PDF", 
            type=["pdf"],
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            if st.button("🚀 Index Document", use_container_width=True):
                with st.spinner("Parsing document vectors..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/ingest",
                            files={"file": (uploaded_file.name, 
                                            uploaded_file, 
                                            "application/pdf")}
                        )
                        if response.status_code == 200:
                            st.success("Indexing successful!")
                            st.toast(f"✅ {uploaded_file.name} is ready!", icon="🎉")
                        else:
                            st.error(f"Backend error: {response.text}")
                    except Exception as e:
                        st.error(f"Could not reach backend: {e}")
                        
    st.markdown("---")
    
    with st.container(border=True):
        st.subheader("🎯 Retrieval Model")
        top_k = st.slider(
            "Context windows (Pages to retrieve)", 
            min_value=1, 
            max_value=10, 
            value=4,
            help="Higher values provide more context, but use more tokens."
        )

# ---- Main Content Layout ----
col1, col2 = st.columns([2, 1], gap="medium")

with col1:
    st.markdown("<h1 class='main-title'>⚡ Doc Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #808495; font-size: 1.1rem;'>Multi-modal Parent-Document Retrieval Pipeline</p>", unsafe_allow_html=True)

# Chat history state init
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display interactive chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("🔍 View Context Sources", expanded=False):
                for s in msg["sources"]:
                    st.markdown(
                        f"""<div class="source-card">
                        <strong>📄 {s['source']}</strong><br/>
                        <span style='color: #808495; font-size: 0.85rem;'>Page {s['page']} | Confidence Score: {s['relevance_score']}</span>
                        </div>""", 
                        unsafe_allow_html=True
                    )

# Text query execution input
if question := st.chat_input("Ask about your structural datasets or documents..."):
    
    # 1. Show user message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    
    # 2. Query processing
    with st.chat_message("assistant"):
        with st.spinner("Scanning vectorized shards..."):
            try:
                resp = requests.post(
                    f"{API_URL}/query",
                    json={"question": question, "top_k": top_k}
                )
                
                if resp.status_code == 200:
                    data = resp.json()
                    answer = data["answer"]
                    sources = data["sources"]
                    
                    # Render response
                    st.markdown(answer)
                    
                    # Highlighted responsive metrics for source metadata
                    with st.expander("🔍 View Context Sources", expanded=True):
                        for s in sources:
                            st.markdown(
                                f"""<div class="source-card">
                                <strong>📄 {s['source']}</strong><br/>
                                <span style='color: #808495; font-size: 0.85rem;'>Page {s['page']} | Relevance Score: {s['relevance_score']}</span>
                                </div>""", 
                                unsafe_allow_html=True
                            )
                    
                    # Cache history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                    
                else:
                    st.error("⚠️ Backend failed to parse answer payload.")
            except Exception as e:
                st.error(f"📡 Connection dropped. Engine offline: {e}")