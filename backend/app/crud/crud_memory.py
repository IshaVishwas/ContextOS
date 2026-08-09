from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.memory import Memory
from app.schemas.memory import MemoryCreate, MemoryUpdate

class CRUDMemory(CRUDBase[Memory, MemoryCreate, MemoryUpdate]):
    def get_by_conversation(self, db: Session, *, conversation_id: int, skip: int = 0, limit: int = 100) -> List[Memory]:
        return db.query(self.model).filter(self.model.conversation_id == conversation_id).offset(skip).limit(limit).all()

memory = CRUDMemory(Memory)
