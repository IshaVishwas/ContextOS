from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class MessageBase(BaseModel):
    role: str
    content: str

class MessageCreate(MessageBase):
    conversation_id: int
    token_count: Optional[int] = 0

class MessageUpdate(MessageBase):
    pass

class MessageInDBBase(MessageBase):
    id: int
    conversation_id: int
    timestamp: datetime
    token_count: int

    model_config = ConfigDict(from_attributes=True)

class Message(MessageInDBBase):
    pass
