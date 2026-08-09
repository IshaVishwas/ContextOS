from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime

class MemoryBase(BaseModel):
    title: Optional[str] = None
    summary: str
    memory_type: str
    importance_score: Optional[float] = 0.0
    embedding_reference: Optional[str] = None
    metadata_: Optional[Dict[str, Any]] = None

class MemoryCreate(MemoryBase):
    conversation_id: int

class MemoryUpdate(MemoryBase):
    pass

class MemoryInDBBase(MemoryBase):
    id: int
    conversation_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Memory(MemoryInDBBase):
    pass

class MemoryIndexRequest(BaseModel):
    message_id: int

class MemoryReindexRequest(BaseModel):
    memory_id: int

class MemorySearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    metadata_filter: Optional[Dict[str, Any]] = None
    similarity_threshold: Optional[float] = 0.0
