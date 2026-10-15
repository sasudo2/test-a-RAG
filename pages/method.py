import requests
import streamlit as st

st.title("RAG method")

if not st.session_state.documents:
    st.warning("No documents uploaded.")
    st.page_link("pages/upload.py", label="Upload documents", icon=":material/upload_file:")
    st.stop()

selected_method = st.radio("Method", ["Pure RAG"])
if st.session_state.rag_method != selected_method:
    st.session_state.rag_method = selected_method
    st.session_state.rag_ready = False
    st.session_state.messages = []

st.caption(f"{len(st.session_state.documents)} document(s) in this session")

if st.button("Prepare documents", icon=":material/play_arrow:"):
    st.session_state.rag_ready = False
    st.session_state.messages = []
    try:
        with st.spinner("Preparing documents..."):
            response = requests.post(
                f"{st.session_state.api_url}/documents/pure_RAG",
                json={"session_id": st.session_state.session_id},
                timeout=120,
            )
            response.raise_for_status()
            result = response.json()
        if result is None:
            st.warning("The server's Pure RAG preparation endpoint is not implemented yet.")
        elif not isinstance(result, dict) or result.get("status") != "ready":
            st.error("The server did not confirm that the documents are ready.")
        else:
            st.session_state.rag_ready = True
    except (requests.RequestException, ValueError) as error:
        st.error(f"Preparation failed: {error}")

if st.session_state.rag_ready:
    st.success("Documents ready")
    if st.button("Open chat", icon=":material/arrow_forward:"):
        st.switch_page("pages/chat.py")