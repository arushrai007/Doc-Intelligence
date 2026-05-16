import streamlit as st
import requests

# ---- 1. PAGE CONFIGURATION ----
st.set_page_config(
    page_title="Doc Intelligence AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://127.0.0.1:8000" 

# ---- 2. STATE MANAGEMENT ----
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "Landing"

# ---- 3. THEME ENGINE & CUSTOM STYLING ----
with st.sidebar:
    st.markdown("<h2 style='margin-bottom:0px;'>🎛️ Navigation</h2>", unsafe_allow_html=True)
    
    page_selection = st.radio(
        "Select Workspace View",
        ["✨ Portal Home", "🔬 Research Lab"],
        label_visibility="collapsed"
    )
    st.session_state.current_page = "Landing" if "Portal" in page_selection else "Research"
    
    st.markdown("---")
    st.markdown("<h2>🎨 Interface Profile</h2>", unsafe_allow_html=True)
    theme_choice = st.selectbox(
        "Active Theme UI",
        ["Coffee House Cozy", "Deep Space Dark", "Clean Studio Light"]
    )

# Advanced Dynamic Layout Engine Configuration
if theme_choice == "Coffee House Cozy":
    accent = "#D4A373"
    text_main = "#FAEDCD"
    text_muted = "#CCD5AE"
    research_node_bg = "#2C221E"
    research_node_border = "#D4A3734D"
    
    # Warm Ambient Coffee Mesh Gradient Background
    bg_style = """
    background-color: #1A120B;
    background-image: 
        radial-gradient(at 0% 0%, rgba(212, 163, 115, 0.08) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(60, 42, 33, 0.15) 0px, transparent 50%),
        radial-gradient(at 50% 50%, rgba(141, 110, 89, 0.05) 0px, transparent 60%);
    background-attachment: fixed;
    """
    glass_card_style = """
    background: rgba(44, 34, 30, 0.65);
    border: 1px solid rgba(212, 163, 115, 0.15);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    """
    chat_input_bg = "#231A16"
    chat_input_border = "rgba(212, 163, 115, 0.2)"
    sidebar_bg = "#150E0A"

elif theme_choice == "Deep Space Dark":
    accent = "#00F5D4"
    text_main = "#F8FAFC"
    text_muted = "#94A3B8"
    research_node_bg = "#111625"
    research_node_border = "#00F5D433"
    
    bg_style = """
    background-color: #060814;
    background-image: 
        radial-gradient(at 0% 0%, rgba(0, 245, 212, 0.07) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(123, 44, 191, 0.08) 0px, transparent 50%),
        radial-gradient(at 50% 0%, rgba(255, 75, 75, 0.04) 0px, transparent 50%);
    background-attachment: fixed;
    """
    glass_card_style = """
    background: rgba(13, 17, 26, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.06);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    """
    chat_input_bg = "#0D111A"
    chat_input_border = "rgba(255, 255, 255, 0.1)"
    sidebar_bg = "#090d16"

else:  # Clean Studio Light
    accent = "#FF4B4B"
    text_main = "#1E293B"
    text_muted = "#64748B"
    research_node_bg = "#F8FAFC"
    research_node_border = "#E2E8F0"
    
    bg_style = """
    background-color: #F3F4F6;
    background-image: 
        radial-gradient(at 100% 0%, rgba(255, 75, 75, 0.04) 0px, transparent 40%),
        radial-gradient(at 0% 100%, rgba(0, 245, 212, 0.03) 0px, transparent 40%);
    background-attachment: fixed;
    """
    glass_card_style = """
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(0, 0, 0, 0.05);
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    """
    chat_input_bg = "#FFFFFF"
    chat_input_border = "#E2E8F0"
    sidebar_bg = "#FFFFFF"

# Global Stylesheet Compilation Injection
st.markdown(f"""
    <style>
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        {bg_style}
        color: {text_main} !important;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
    }}
    
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown, [data-testid="stWidgetLabel"] p {{
        color: {text_main} !important;
    }}
    
    .gradient-header {{
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, {accent} 0%, #6F4E37 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
        margin-bottom: 0.5rem;
    }}
    
    .glass-card {{
        {glass_card_style}
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }}
    
    .research-node {{
        background-color: {research_node_bg};
        border: 1px solid {research_node_border};
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border-left: 5px solid {accent};
    }}
    
    .metric-badge {{
        background: rgba(0, 0, 0, 0.2);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-family: monospace;
        color: {accent};
        border: 1px solid {research_node_border};
    }}
    
    .stChatInputContainer {{
        border-radius: 24px !important;
        border: 1px solid {chat_input_border} !important;
        background: {chat_input_bg} !important;
    }}
    
    textarea {{
        color: {text_main} !important;
    }}
    </style>
""", unsafe_allow_html=True)


# ---- 4. APP VIEW ROUTING ----

# ==========================================
# VIEW A: PORTAL LANDING PAGE
# ==========================================
if st.session_state.current_page == "Landing":
    
    st.markdown("<div style='text-align: center; margin-top: 5vh; margin-bottom: 8vh;'>", unsafe_allow_html=True)
    st.markdown("<h1 class='gradient-header'>Doc Intelligence Pipeline</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: {text_muted}; font-size: 1.3rem; max-width: 700px; margin: 0 auto;'>An advanced multi-modal engine powered by hierarchical parent-document chunking and semantic vector topologies.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="large")
    
    with col1:
        st.markdown(f"""
            <div class="glass-card">
                <h3 style="color: {accent}; margin-top:0;">⚡ Sub-Chunk Splitting</h3>
                <p style="color: {text_muted}; font-size:0.95rem; line-height:1.6;">Documents are split into precise semantic atom fragments for pinpoint embedding matching accuracy, avoiding diluted context vectors.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
            <div class="glass-card">
                <h3 style="color: {accent}; margin-top:0;">🧬 Parent Reconstruction</h3>
                <p style="color: {text_muted}; font-size:0.95rem; line-height:1.6;">Upon retrieval, targeted sub-chunks instantly pull their overarching structural parent document context to preserve synthesis consistency.</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <div class="glass-card">
                <h3 style="color: {accent}; margin-top:0;">🔬 Research Synthesis</h3>
                <p style="color: {text_muted}; font-size:0.95rem; line-height:1.6;">A split-pane terminal optimized for deep analysis, multi-source trace matrices, and analytical cross-referencing capabilities.</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    c_left, c_right = st.columns([2, 1], gap="medium")
    with c_left:
        with st.container(border=True):
            st.markdown("### 📂 Fast Ingestion Gateway")
            fast_file = st.file_uploader("Drop target documentation to vectorize into active memory space", type=["pdf"])
            if fast_file and st.button("Initialize Fast Ingestion Pipeline", use_container_width=True):
                with st.spinner("Processing structural shards..."):
                    try:
                        res = requests.post(f"{API_URL}/ingest", files={"file": (fast_file.name, fast_file, "application/pdf")})
                        if res.status_code == 200:
                            st.toast(f"Vector Space Updated with {fast_file.name}!", icon="🧬")
                            st.success("Analysis targets mounted successfully.")
                    except:
                        st.error("System pipeline offline.")
    with c_right:
        st.markdown(f"""
            <div class="glass-card" style="height: 100%;">
                <h4 style="margin-top:0;">System Node Health</h4>
                <p style="font-size:0.85rem; color:{text_muted}; margin-bottom:6px;">• Vector Store: <span style="color:#10B981;">Online</span></p>
                <p style="font-size:0.85rem; color:{text_muted}; margin-bottom:6px;">• Embeddings Engine: <span style="color:#10B981;">Ready</span></p>
                <p style="font-size:0.85rem; color:{text_muted}; margin-bottom:12px;">• Active Theme: <span style="color:{accent}; font-weight:600;">{theme_choice}</span></p>
                <hr style="border-color:rgba(0,0,0,0.08);"/>
                <p style="font-size:0.8rem; color:{text_muted};">Flip the left sidebar menu controller to <strong>🔬 Research Lab</strong> to begin asking questions.</p>
            </div>
        """, unsafe_allow_html=True)


# ==========================================
# VIEW B: RESEARCH WORKSPACE INTERFACE
# ==========================================
elif st.session_state.current_page == "Research":
    
    with st.sidebar:
        st.markdown("<h2>⚙️ Lab Control Shards</h2>", unsafe_allow_html=True)
        with st.container(border=True):
            st.subheader("📚 File Manager")
            uploaded_file = st.file_uploader("Upload PDF Data Targets", type=["pdf"], key="lab_uploader", label_visibility="collapsed")
            if uploaded_file and st.button("⚡ Index Corpus", use_container_width=True):
                with st.spinner("Analyzing vectors..."):
                    try:
                        response = requests.post(f"{API_URL}/ingest", files={"file": (uploaded_file.name, uploaded_file, "application/pdf")})
                        if response.status_code == 200:
                            st.toast(f"✅ Indexed {uploaded_file.name}")
                        else:
                            st.error("Ingestion failed.")
                    except Exception as e:
                        st.error(f"Backend network connection dropped: {e}")
                        
        with st.container(border=True):
            st.subheader("🔬 Hyperparameters")
            top_k = st.slider("Context Expansion (k-neighbors)", 1, 12, 4, help="Alters parent retrieval horizon breadth.")

    pane_chat, pane_analytics = st.columns([5, 4], gap="large")

    with pane_chat:
        st.markdown(f"### 💬 Research Terminal (<span style='color:{accent}; font-size:1.1rem;'>Interactive Inference</span>)", unsafe_allow_html=True)
        
        chat_container = st.container(height=550)
        with chat_container:
            if not st.session_state.messages:
                st.markdown(f"<p style='color:{text_muted}; text-align:center; padding-top:100px;'>Inference session blank. State payload clear.<br/>Transmit query down below to construct knowledge vectors.</p>", unsafe_allow_html=True)
            
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        if question := st.chat_input("Input analytical cross-examination query..."):
            st.session_state.messages.append({"role": "user", "content": question})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(question)
                
                with st.chat_message("assistant"):
                    with st.spinner("Processing deep tensor traversal..."):
                        try:
                            resp = requests.post(f"{API_URL}/query", json={"question": question, "top_k": top_k})
                            if resp.status_code == 200:
                                data = resp.json()
                                st.markdown(data["answer"])
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": data["answer"],
                                    "sources": data["sources"]
                                })
                                st.rerun()
                            else:
                                st.error("Inference node returned invalid execution sequence response.")
                        except Exception as e:
                            st.error(f"Execution Error: {e}")

    with pane_analytics:
        st.markdown("### 📊 Document Lineage Matrix")
        
        if st.session_state.messages and "sources" in st.session_state.messages[-1]:
            last_assistant_msg = st.session_state.messages[-1]
            st.markdown(f"<p style='color:{text_muted}; font-size:0.85rem; margin-bottom:15px;'>Real-time lineage metadata retrieved from the latest query token emission.</p>", unsafe_allow_html=True)
            
            for index, s in enumerate(last_assistant_msg["sources"]):
                st.markdown(f"""
                    <div class="research-node">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <strong>🗂️ Node Source [{index + 1}]</strong>
                            <span class="metric-badge">Conf: {s['relevance_score']}</span>
                        </div>
                        <p style="margin:0 0 4px 0; font-size:0.9rem;"><strong>File Path:</strong> {s['source']}</p>
                        <p style="margin:0; font-size:0.9rem;"><strong>Parent Page Context Anchor:</strong> Page {s['page']}</p>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="border: 1px dashed {text_muted}; border-radius:12px; padding:40px; text-align:center; color:{text_muted}; margin-top:20px;">
                    <span style="font-size:2rem;">📡</span><br/>
                    <strong>Awaiting Structural Payload Tracing</strong><br/>
                    Execute an interrogation query via the inference terminal to stream vector shard source matrices here.
                </div>
            """, unsafe_allow_html=True)