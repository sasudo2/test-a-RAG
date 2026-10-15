import requests
import streamlit as st

st.title("Upload documents")

files = st.file_uploader(
	"Text files",
	type=["txt"],
	accept_multiple_files=True,
	key="upload_files",
)

if st.button("Upload", disabled=not files, icon=":material/upload:"):
	multipart_files = [
		("files", (file.name, file.getvalue(), file.type or "text/plain"))
		for file in files
	]
	form_data = {}
	if st.session_state.session_id:
		form_data["session_id"] = st.session_state.session_id

	try:
		with st.spinner("Uploading..."):
			response = requests.post(
				f"{st.session_state.api_url}/documents/upload",
				data=form_data,
				files=multipart_files,
				timeout=120,
			)
			response.raise_for_status()
			result = response.json()
			if not isinstance(result, dict) or not result.get("session_id"):
				raise ValueError("The API did not return a session ID.")
			if not isinstance(result.get("documents"), list) or not result["documents"]:
				raise ValueError("The API did not return uploaded documents.")
			if any(not isinstance(document, dict) or not document.get("document_id")
			       for document in result["documents"]):
				raise ValueError("The API returned invalid document records.")

		st.session_state.session_id = result["session_id"]
		st.session_state.documents.extend(result["documents"])
		st.session_state.rag_ready = False
		st.session_state.messages = []
		st.success(f"Uploaded {len(result['documents'])} file(s).")
	except (requests.RequestException, KeyError, ValueError) as error:
		st.error(f"Upload failed: {error}")

if st.session_state.documents:
	st.dataframe(st.session_state.documents, hide_index=True, use_container_width=True)
	if st.button("Select RAG method", icon=":material/arrow_forward:"):
		st.switch_page("pages/method.py")
