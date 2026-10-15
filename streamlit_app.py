import os

import streamlit as st

st.set_page_config(page_title="Document RAG", page_icon="R", layout="centered")


def reset_session():
    st.session_state.update(
        session_id="", documents=[], rag_method=None, rag_ready=False, messages=[]
    )
    st.session_state.pop("upload_files", None)


def change_api():
    st.session_state.api_url = st.session_state.api_input.strip().rstrip("/")
    reset_session()


defaults = {
    "api_url": os.getenv("FASTAPI_URL", "http://127.0.0.1:8000").rstrip("/"),
    "session_id": "",
    "documents": [],
    "rag_method": None,
    "rag_ready": False,
    "messages": [],
}
for name, value in defaults.items():
    if name not in st.session_state:
        st.session_state[name] = value

if "api_input" not in st.session_state:
    st.session_state.api_input = st.session_state.api_url

st.sidebar.title("Document RAG")
st.sidebar.text_input("FastAPI URL", key="api_input", on_change=change_api)
if st.session_state.session_id:
    st.sidebar.caption(f"Session: {st.session_state.session_id}")
st.sidebar.button("New session", icon=":material/add:", on_click=reset_session)

page = st.navigation([
    st.Page("pages/upload.py", title="Upload", icon=":material/upload_file:", default=True),
    st.Page("pages/method.py", title="RAG method", icon=":material/tune:"),
    st.Page("pages/chat.py", title="Chat", icon=":material/chat:"),
])
page.run()