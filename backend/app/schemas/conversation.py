from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from .message import Message
from .memory import Memory

class ConversationBase(BaseModel):
    title: Optional[str] = None

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(ConversationBase):
    pass

class ConversationInDBBase(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Conversation(ConversationInDBBase):
    pass

class ConversationWithDetails(Conversation):
    messages: List[Message] = []
    memories: List[Memory] = []
