from pydantic import BaseModel
from typing import Optional

class Message(BaseModel):
    message: str
    conversation_id: Optional[str] = None
