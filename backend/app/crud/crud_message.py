from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageUpdate

class CRUDMessage(CRUDBase[Message, MessageCreate, MessageUpdate]):
    def get_by_conversation(self, db: Session, *, conversation_id: int, skip: int = 0, limit: int = 100) -> List[Message]:
        return db.query(self.model).filter(self.model.conversation_id == conversation_id).offset(skip).limit(limit).all()

message = CRUDMessage(Message)
