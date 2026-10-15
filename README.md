# test-a-RAG

## Streamlit

Run the backend and frontend in separate terminals:

```bash
uvicorn app.main:app --reload --host 0.0.0.0
streamlit run streamlit_app.py
```

The app has three pages: Upload, RAG method, and Chat. Only Pure RAG has
server routes at present. Configure the server URL in the sidebar or with
`FASTAPI_URL`. Changing servers or starting a new session clears frontend state.

Uploads use the existing multipart `/documents/upload` endpoint. The RAG
routes are currently placeholders, so preparation and chat cannot complete yet.
The frontend expects the following contracts when those routes are implemented:

- `POST /documents/pure_RAG`: JSON `{"session_id": "<UUID>"}`;
	response `{"status": "ready"}` only after the session's documents are indexed.
- `POST /documents/pure_RAG/query`: JSON containing `session_id`, `query`,
	and `history` (a list of `role`/`content` messages); response `{"answer": "..."}`.

These RAG contracts are frontend expectations, not implemented backend behavior.
Session state is local to the current Streamlit connection and is not durable.