import requests
import streamlit as st

st.title("Chat")

if not st.session_state.documents:
    st.warning("No documents uploaded.")
    st.page_link("pages/upload.py", label="Upload documents", icon=":material/upload_file:")
    st.stop()

if not st.session_state.rag_method or not st.session_state.rag_ready:
    st.warning("Select a RAG method and prepare the documents before chatting.")
    st.page_link("pages/method.py", label="RAG method", icon=":material/tune:")
    st.chat_input("Ask about your documents", disabled=True)
    st.stop()

st.caption(st.session_state.rag_method)
if st.button("Clear conversation", icon=":material/delete:"):
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask about your documents")
if prompt and prompt.strip():
    with st.chat_message("user"):
        st.markdown(prompt)
    try:
        with st.spinner("Generating answer..."):
            response = requests.post(
                f"{st.session_state.api_url}/documents/pure_RAG/query",
                json={
                    "session_id": st.session_state.session_id,
                    "query": prompt,
                    "history": st.session_state.messages,
                },
                timeout=120,
            )
            response.raise_for_status()
            result = response.json()
        if result is None:
            st.warning("The server's Pure RAG query endpoint is not implemented yet.")
        elif not isinstance(result, dict) or not isinstance(result.get("answer"), str) or not result["answer"].strip():
            st.error("The server did not return an answer.")
        else:
            st.session_state.messages.extend([
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": result["answer"]},
            ])
            with st.chat_message("assistant"):
                st.markdown(result["answer"])
    except (requests.RequestException, ValueError) as error:
        st.error(f"Query failed: {error}")