# ================================================================
# FILE: frontend/app.py
# CHANGE: Only upload logic modified
#   - Single file  → POST /api/upload       (same as before)
#   - Multiple files → POST /api/upload/multiple (NEW)
# UI, CSS, layout — completely unchanged
# ================================================================

import streamlit as st
import requests

BACKEND = "http://localhost:8000"

# ── Page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Document Insights",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Master CSS — UNCHANGED ────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg:        #212121;
    --sb:        #171717;
    --card:      #2F2F2F;
    --card2:     #1E1E1E;
    --border:    rgba(255,255,255,0.08);
    --border2:   rgba(255,255,255,0.13);
    --accent:    #10A37F;
    --accent2:   rgba(16,163,127,0.15);
    --text:      #ECECEC;
    --muted:     #8E8EA0;
    --dim:       #565869;
    --user-bg:   #2A2A2A;
    --amber:     #F0A14A;
}

html, body, [data-testid="stApp"] {
    background: var(--bg) !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
    color: var(--text) !important;
}
* { box-sizing: border-box; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] { gap: 0 !important; }

[data-testid="stSidebar"] {
    background: var(--sb) !important;
    border-right: 1px solid var(--border) !important;
    min-width: 270px !important;
    max-width: 270px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
    background: var(--sb) !important;
}
section[data-testid="stSidebar"] { padding: 0 !important; }

[data-testid="stFileUploader"] { background: transparent !important; }
[data-testid="stFileUploadDropzone"] {
    background: var(--card) !important;
    border: 1.5px dashed rgba(16,163,127,0.35) !important;
    border-radius: 10px !important;
    transition: border-color 0.2s, background 0.2s !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: var(--accent) !important;
    background: rgba(16,163,127,0.04) !important;
}
[data-testid="stFileUploadDropzone"] p,
[data-testid="stFileUploadDropzone"] span {
    color: var(--muted) !important; font-size: 13px !important;
}

.stButton > button {
    background: var(--card) !important;
    color: var(--muted) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    transition: all 0.18s !important;
    padding: 6px 14px !important;
}
.stButton > button:hover {
    background: var(--card2) !important;
    color: var(--text) !important;
    border-color: var(--accent) !important;
}

[data-testid="stSelectbox"] > div > div {
    background: var(--card) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-size: 13px !important;
}

[data-testid="stChatInput"] {
    position: fixed !important;
    bottom: 0 !important;
    left: 270px !important;
    right: 0 !important;
    background: linear-gradient(to top, #212121 75%, transparent) !important;
    padding: 16px 32px 24px !important;
    z-index: 9999 !important;
}
[data-testid="stChatInput"] > div {
    background: var(--card) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 16px !important;
    box-shadow: 0 2px 20px rgba(0,0,0,0.4) !important;
    max-width: 780px !important;
    margin: 0 auto !important;
    transition: border-color 0.2s !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 2px 24px rgba(16,163,127,0.15) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--dim) !important; }
[data-testid="stChatInputSubmitButton"] button {
    background: var(--accent) !important;
    border-radius: 10px !important;
    border: none !important;
    width: 36px !important;
    height: 36px !important;
    margin: 4px !important;
    padding: 0 !important;
}

[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 2px 0 !important;
}
[data-testid="stChatMessageContent"] {
    background: transparent !important;
    color: var(--text) !important;
    font-size: 14px !important;
    line-height: 1.75 !important;
}

details {
    background: var(--card2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    margin-top: 8px !important;
}
summary {
    color: var(--muted) !important;
    font-size: 12px !important;
    padding: 6px 10px !important;
    cursor: pointer !important;
}

.stSuccess {
    background: rgba(16,163,127,0.1) !important;
    border: 1px solid rgba(16,163,127,0.3) !important;
    border-radius: 8px !important;
    color: var(--accent) !important;
}
.stWarning {
    background: rgba(240,161,74,0.1) !important;
    border: 1px solid rgba(240,161,74,0.3) !important;
    border-radius: 8px !important;
}
.stError {
    background: rgba(239,68,68,0.1) !important;
    border: 1px solid rgba(239,68,68,0.3) !important;
    border-radius: 8px !important;
}
.stSuccess p, .stWarning p, .stError p { font-size: 13px !important; }

.stSpinner > div { border-top-color: var(--accent) !important; }
hr { border-color: var(--border) !important; margin: 10px 0 !important; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #3A3A3A; border-radius: 2px; }
[data-testid="column"] { padding: 0 !important; }
.stCaption { color: var(--dim) !important; font-size: 11px !important; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────
if "messages"  not in st.session_state: st.session_state.messages  = []
if "documents" not in st.session_state: st.session_state.documents = {}
# documents = {doc_id: {"filename": ..., "chunks": ...}}


# ================================================================
# UPLOAD HELPER FUNCTIONS — only these are modified/added
# Everything else below is unchanged
# ================================================================

def is_already_uploaded(filename: str) -> bool:
    """Check karo ye file pehle se upload ho chuki hai session mein"""
    return any(
        info["filename"] == filename
        for info in st.session_state.documents.values()
    )


def _register_doc(doc_id: str, filename: str, chunks: int):
    """
    Helper: ek document ko session state mein add karo
    aur chat mein system message daalo.
    Dono upload functions ye use karte hain — no duplication.
    """
    st.session_state.documents[doc_id] = {
        "filename": filename,
        "chunks":   chunks
    }
    st.session_state.messages.append({
        "role":        "assistant",
        "content":     (
            f"**{filename}** processed successfully. "
            f"{chunks} chunks indexed. "
            "Ready for questions!"
        ),
        "sources":     [],
        "searched_in": ""
    })


def upload_single_file(file) -> bool:
    """
    Single file → POST /api/upload
    Same as before — unchanged behavior.
    Returns True agar success.
    """
    try:
        res = requests.post(
            f"{BACKEND}/api/upload",
            files={"file": (file.name, file.getvalue(), file.type)},
            timeout=120
        )
        if res.status_code == 200:
            data = res.json()
            _register_doc(data["doc_id"], data["filename"], data["chunks_created"])
            return True
        else:
            st.error(f"Upload failed for **{file.name}**: {res.text}")
            return False
    except requests.exceptions.ConnectionError:
        st.error("Backend connect nahi ho raha. Server chalu hai?")
        return False
    except Exception as e:
        st.error(f"Upload error ({file.name}): {e}")
        return False


def upload_multiple_files(files: list) -> bool:
    """
    2+ files → POST /api/upload/multiple
    Sab files ek single HTTP request mein bhejta hai.

    Backend response format:
    {
        "uploaded": [
            {"doc_id": "...", "filename": "...",
             "chunks_created": ..., "upload_time": "..."},
            ...
        ],
        "total_files": ...,
        "total_chunks": ...,
        "message": "..."
    }

    Returns True agar at least ek file success.
    """
    # Multipart form data build karo
    # FastAPI List[UploadFile] ke liye same field name "files" multiple baar
    multipart = []
    for f in files:
        multipart.append(
            ("files", (f.name, f.getvalue(), f.type))
        )

    try:
        res = requests.post(
            f"{BACKEND}/api/upload/multiple",
            files=multipart,
            timeout=300   # multiple files ke liye zyada timeout
        )

        if res.status_code != 200:
            st.error(f"Multiple upload failed: {res.text}")
            return False

        data = res.json()
        uploaded_list = data.get("uploaded", [])
        any_success   = False

        # Har successfully uploaded doc ko register karo
        for doc in uploaded_list:
            doc_id   = doc.get("doc_id")
            filename = doc.get("filename")
            chunks   = doc.get("chunks_created", 0)

            if not doc_id or not filename:
                continue

            # Duplicate check — backend already indexed hai kya?
            if is_already_uploaded(filename):
                st.warning(
                    f"**{filename}** is already uploaded. Skipping."
                )
                continue

            _register_doc(doc_id, filename, chunks)
            any_success = True

        # Backend ka summary message dikhao agar partial failure tha
        backend_msg = data.get("message", "")
        if "failed" in backend_msg.lower():
            st.warning(f"Partial upload: {backend_msg}")

        return any_success

    except requests.exceptions.ConnectionError:
        st.error("Backend is not running. start the Server ")
        return False
    except Exception as e:
        st.error(f"Multiple upload error: {e}")
        return False


def process_new_uploads(uploaded_files: list):
    """
    check uploaded file  — new files move to backend .

    Logic:
      - Already uploaded files skip  (duplicate check)
      - New files:
          1 file  → upload_single_file()
          2+ files → upload_multiple_files()

    Ye function sirf upload logic handle karta hai.
    UI/session update _register_doc() se hota hai.
    """
    # Sirf nayi files filter karo
    new_files = [
        f for f in uploaded_files
        if not is_already_uploaded(f.name)
    ]

    if not new_files:
        # Sab files pehle se upload hain — kuch nahi karna
        return False

    # ── Routing: single vs multiple ──────────────────────────────
    if len(new_files) == 1:
        # Single file — /api/upload
        with st.spinner(f"Processing {new_files[0].name}..."):
            success = upload_single_file(new_files[0])
        return success

    else:
        # Multiple files — /api/upload/multiple
        names = ", ".join(f.name for f in new_files)
        with st.spinner(f"Processing {len(new_files)} files: {names}..."):
            success = upload_multiple_files(new_files)
        return success


# ── Query & delete helpers — UNCHANGED ───────────────────────────

def query_backend(question: str, doc_id: str = None) -> dict | None:
    """Backend se answer lo — unchanged"""
    payload = {"question": question}
    if doc_id:
        payload["doc_id"] = doc_id
    try:
        res = requests.post(
            f"{BACKEND}/api/query",
            json=payload,
            timeout=60
        )
        if res.status_code == 200:
            return res.json()
        st.error(f"Query failed: {res.text}")
        return None
    except Exception as e:
        st.error(f"Query error: {e}")
        return None


def delete_from_backend(doc_id: str) -> bool:
    """Document backend se delete karo — unchanged"""
    try:
        res = requests.delete(
            f"{BACKEND}/api/documents/{doc_id}",
            timeout=10
        )
        return res.status_code == 200
    except:
        return False


# ================================================================
# SIDEBAR — UNCHANGED
# ================================================================
with st.sidebar:

    st.markdown("""
    <div style="padding:20px 16px 14px;
                border-bottom:1px solid rgba(255,255,255,0.07)">
        <div style="display:flex;align-items:center;gap:10px">
            <div style="width:32px;height:32px;
                        background:linear-gradient(135deg,#10A37F,#1A7FBF);
                        border-radius:9px;
                        display:flex;align-items:center;justify-content:center;
                        font-size:16px;flex-shrink:0">📄</div>
            <div>
                <div style="font-size:15px;font-weight:600;
                            color:#ECECEC;letter-spacing:-0.01em">
                    DocMind
                </div>
                <div style="font-size:10px;color:#565869;margin-top:-1px">
                    Smart Document Insights
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="padding:14px 16px 6px">
        <div style="font-size:10px;font-weight:600;color:#565869;
                    letter-spacing:0.07em;text-transform:uppercase">
            Upload Documents
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div style="padding:0 12px">', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "upload_area",
            type=["pdf", "txt"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="uploader"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # ── AUTO PROCESS — uses smart routing ────────────────────────
    if uploaded_files:
        did_upload = process_new_uploads(uploaded_files)
        if did_upload:
            st.rerun()

    # ── Divider between upload and doc list ──────────────────────
    st.markdown("""
    <div style="margin:10px 12px 0">
        <div style="height:1px;background:rgba(255,255,255,0.07)"></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Document List — UNCHANGED ─────────────────────────────────
    if st.session_state.documents:

        st.markdown("""
        <div style="padding:10px 16px 4px">
            <div style="font-size:10px;font-weight:600;color:#565869;
                        letter-spacing:0.07em;text-transform:uppercase">
                Uploaded Documents
            </div>
        </div>
        """, unsafe_allow_html=True)

        docs_to_delete = []
        for doc_id, info in st.session_state.documents.items():
            name  = info["filename"]
            short = (name[:22] + "…") if len(name) > 25 else name

            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(f"""
                <div style="margin:3px 4px;padding:8px 10px;
                            background:#1E1E1E;
                            border:1px solid rgba(255,255,255,0.07);
                            border-left:2.5px solid #10A37F;
                            border-radius:7px">
                    <div style="font-size:12px;font-weight:500;color:#ECECEC">
                        {short}
                    </div>
                    <div style="font-size:10px;color:#10A37F;margin-top:1px">
                        {info['chunks']} sections
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                if st.button("🗑", key=f"del_{doc_id}",
                             help=f"Remove {name}"):
                    docs_to_delete.append(doc_id)

        for doc_id in docs_to_delete:
            if delete_from_backend(doc_id):
                del st.session_state.documents[doc_id]
                st.rerun()

        # ── Search scope selector — UNCHANGED ────────────────────
        st.markdown("""
        <div style="padding:10px 16px 4px">
            <div style="font-size:10px;font-weight:600;color:#565869;
                        letter-spacing:0.07em;text-transform:uppercase">
                Search Scope
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown('<div style="padding:0 12px 6px">', unsafe_allow_html=True)

            scope_options = {"All Documents": None}
            for did, info in st.session_state.documents.items():
                scope_options[info["filename"]] = did

            selected_name = st.selectbox(
                "scope_select",
                list(scope_options.keys()),
                label_visibility="collapsed"
            )
            selected_doc_id = scope_options[selected_name]

            if selected_doc_id:
                st.markdown(f"""
                <div style="font-size:11px;color:#F0A14A;padding:3px 0 4px">
                    ⬤ Searching in: <b>{selected_name}</b>
                </div>
                """, unsafe_allow_html=True)
            else:
                count = len(st.session_state.documents)
                st.markdown(f"""
                <div style="font-size:11px;color:#10A37F;padding:3px 0 4px">
                    ⬤ Searching across all {count} document(s)
                </div>
                """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        # ── Stats — UNCHANGED ─────────────────────────────────────
        total_chunks = sum(
            d["chunks"] for d in st.session_state.documents.values()
        )
        st.markdown(f"""
        <div style="margin:6px 12px 8px;padding:9px 12px;
                    background:#1A1A1A;
                    border:1px solid rgba(255,255,255,0.06);
                    border-radius:8px">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px">
                <span style="font-size:11px;color:#565869">Documents</span>
                <span style="font-size:11px;color:#ECECEC">
                    {len(st.session_state.documents)}
                </span>
            </div>
            <div style="display:flex;justify-content:space-between;margin-bottom:4px">
                <span style="font-size:11px;color:#565869">Total sections</span>
                <span style="font-size:11px;color:#10A37F">{total_chunks}</span>
            </div>
            <div style="display:flex;justify-content:space-between">
                <span style="font-size:11px;color:#565869">Messages</span>
                <span style="font-size:11px;color:#ECECEC">
                    {len(st.session_state.messages)}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="padding:0 12px 4px">', unsafe_allow_html=True)
        if st.button("+ New chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown("""
        <div style="padding:16px;text-align:center;color:#565869;
                    font-size:12px;line-height:1.6">
            Upload a PDF or TXT file above to get started.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="position:absolute;bottom:0;left:0;right:0;
                padding:10px 16px;
                border-top:1px solid rgba(255,255,255,0.06);
                background:#171717">
        <div style="font-size:11px;color:#565869;line-height:1.5">
            LLM: <span style="color:#10A37F">OpenAI GPT-OSS-120B</span> via Groq<br>
            DB: <span style="color:#8E8EA0">ChromaDB</span> ·
            Embed: <span style="color:#8E8EA0">MiniLM-L6</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ================================================================
# MAIN AREA — UNCHANGED
# ================================================================

st.markdown("""
<div style="text-align:center;padding:28px 32px 16px;
            border-bottom:1px solid rgba(255,255,255,0.07)">
    <div style="display:inline-flex;align-items:center;gap:10px">
        <div style="width:34px;height:34px;
                    background:linear-gradient(135deg,#10A37F,#1A7FBF);
                    border-radius:9px;
                    display:flex;align-items:center;justify-content:center;
                    font-size:18px">📄</div>
        <span style="font-size:20px;font-weight:600;color:#ECECEC;
                     letter-spacing:-0.02em">
            Smart Document Insights
        </span>
        <span style="font-size:11px;font-weight:500;color:#10A37F;
                     background:rgba(16,163,127,0.1);
                     border:1px solid rgba(16,163,127,0.2);
                     padding:2px 8px;border-radius:20px">
            RAG
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Chat messages — UNCHANGED ─────────────────────────────────────
with st.container():
    if not st.session_state.messages:
        st.markdown("""
        <div style="display:flex;flex-direction:column;
                    align-items:center;justify-content:center;
                    padding:70px 20px 160px;text-align:center">
            <div style="width:56px;height:56px;
                        background:linear-gradient(135deg,#10A37F,#1A7FBF);
                        border-radius:16px;
                        display:flex;align-items:center;justify-content:center;
                        font-size:26px;margin-bottom:20px;
                        box-shadow:0 4px 28px rgba(16,163,127,0.22)">📄</div>
            <h2 style="font-size:22px;font-weight:600;color:#ECECEC;
                       margin:0 0 8px;letter-spacing:-0.02em">
                What do you want to know?
            </h2>
            <p style="font-size:14px;color:#8E8EA0;
                      max-width:360px;line-height:1.6;margin:0 0 32px">
                Upload a PDF or TXT in the sidebar — I'll process it instantly
                and answer your questions.
            </p>
            <div style="display:grid;grid-template-columns:1fr 1fr;
                        gap:8px;max-width:460px;width:100%">
                <div style="background:#2F2F2F;border:1px solid rgba(255,255,255,0.08);
                            border-radius:10px;padding:12px 13px;text-align:left">
                    <div style="font-size:17px;margin-bottom:4px">🔍</div>
                    <div style="font-size:12px;font-weight:500;color:#ECECEC;margin-bottom:2px">Summarize</div>
                    <div style="font-size:11px;color:#565869">"Give me a summary"</div>
                </div>
                <div style="background:#2F2F2F;border:1px solid rgba(255,255,255,0.08);
                            border-radius:10px;padding:12px 13px;text-align:left">
                    <div style="font-size:17px;margin-bottom:4px">💡</div>
                    <div style="font-size:12px;font-weight:500;color:#ECECEC;margin-bottom:2px">Key insights</div>
                    <div style="font-size:11px;color:#565869">"What are the main findings?"</div>
                </div>
                <div style="background:#2F2F2F;border:1px solid rgba(255,255,255,0.08);
                            border-radius:10px;padding:12px 13px;text-align:left">
                    <div style="font-size:17px;margin-bottom:4px">📋</div>
                    <div style="font-size:12px;font-weight:500;color:#ECECEC;margin-bottom:2px">Action items</div>
                    <div style="font-size:11px;color:#565869">"List all action items"</div>
                </div>
                <div style="background:#2F2F2F;border:1px solid rgba(255,255,255,0.08);
                            border-radius:10px;padding:12px 13px;text-align:left">
                    <div style="font-size:17px;margin-bottom:4px">❓</div>
                    <div style="font-size:12px;font-weight:500;color:#ECECEC;margin-bottom:2px">Deep dive</div>
                    <div style="font-size:11px;color:#565869">"Explain section 3 simply"</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="max-width:780px;margin:0 auto;'
            'padding:24px 24px 160px">',
            unsafe_allow_html=True
        )
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(msg["content"])
                    si = msg.get("searched_in", "")
                    if si and si not in ("", "error", "all documents"):
                        st.caption(f"🔍 Searched in: **{si}**")
                    elif si == "all documents":
                        doc_count = len(st.session_state.documents)
                        if doc_count > 1:
                            st.caption(
                                f"🔍 Searched across all {doc_count} documents"
                            )
                    srcs = msg.get("sources", [])
                    if srcs:
                        with st.expander("Sources"):
                            for src in srcs:
                                st.caption(f"📄 {src}")
        st.markdown('</div>', unsafe_allow_html=True)

# ── Fixed chat input — UNCHANGED ──────────────────────────────────
if not st.session_state.documents:
    placeholder = "Upload a document first to start chatting..."
elif 'selected_name' in dir() and selected_name != "All Documents":
    placeholder = f"Ask about {selected_name}..."
else:
    placeholder = "Ask anything about your document(s)..."

question = st.chat_input(placeholder)

# ── Handle question — UNCHANGED ───────────────────────────────────
if question:
    if not st.session_state.documents:
        st.warning("Please upload at least one document first.")
        st.stop()

    doc_id_to_use = (
        selected_doc_id
        if 'selected_doc_id' in dir() and selected_doc_id
        else None
    )

    st.session_state.messages.append({
        "role":        "user",
        "content":     question,
        "sources":     [],
        "searched_in": ""
    })

    with st.spinner(""):
        data = query_backend(question, doc_id=doc_id_to_use)

    if data:
        st.session_state.messages.append({
            "role":        "assistant",
            "content":     data.get("answer", "No answer received."),
            "sources":     data.get("sources", []),
            "searched_in": data.get("searched_in", "")
        })
    else:
        st.session_state.messages.append({
            "role":        "assistant",
            "content":     (
                "Could not reach the backend. "
                "Make sure the server is running on port 8000."
            ),
            "sources":     [],
            "searched_in": "error"
        })
    st.rerun()