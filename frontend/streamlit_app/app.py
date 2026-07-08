import streamlit as st
import requests

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="Smart Document Insights",
    page_icon="📄",
    layout="wide"
)

# ===== TITLE =====
st.title("📄 Smart Document Insights")
st.markdown("Upload a document and ask anything about it.")
st.divider()

# ===== TWO COLUMN LAYOUT =====
col1, col2 = st.columns([1, 2])

# ===== LEFT COLUMN — UPLOAD =====
with col1:
    st.subheader("Upload Document")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF or TXT file",
        type=["pdf", "txt"]
    )
    
    if uploaded_file is not None:
        if st.button("Process Document", type="primary"):
            with st.spinner("Processing..."):
                try:
                    response = requests.post(
                        "http://localhost:8000/api/upload",
                        files={"file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type
                        )}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"Done! {data['chunks_created']} chunks created.")
                        st.session_state["doc_id"] = data["doc_id"]
                        st.session_state["filename"] = data["filename"]
                    else:
                        st.error(f"Error: {response.text}")
                        
                except Exception as e:
                    st.error(f"Backend se connect nahi hua: {e}")
    
    # Show uploaded doc info
    if "filename" in st.session_state:
        st.info(f"Active: {st.session_state['filename']}")

# ===== RIGHT COLUMN — CHAT =====
with col2:
    st.subheader("Ask Questions")
    
    # Chat history
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    
    # Show previous messages
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # Question input
    question = st.chat_input("Ask anything about your document...")
    
    if question:
        if "doc_id" not in st.session_state:
            st.warning("Pehle document upload karo!")
        else:
            # Show user message
            st.session_state["messages"].append({
                "role": "user",
                "content": question
            })
            with st.chat_message("user"):
                st.write(question)
            
            # Get AI answer
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = requests.post(
                            "http://localhost:8000/api/query",
                            json={"question": question}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            answer = data["answer"]
                            st.write(answer)
                            
                            # Show sources
                            if "sources" in data:
                                with st.expander("Sources"):
                                    for src in data["sources"]:
                                        st.caption(src)
                            
                            st.session_state["messages"].append({
                                "role": "assistant",
                                "content": answer
                            })
                        else:
                            st.error(f"Error: {response.text}")
                            
                    except Exception as e:
                        st.error(f"Error: {e}")