from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class Document(BaseModel):
    session_id: UUID
    filename: str = Field(min_length=1)
    text: str
