from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.conversation import Conversation
from app.schemas.conversation import ConversationCreate, ConversationUpdate

class CRUDConversation(CRUDBase[Conversation, ConversationCreate, ConversationUpdate]):
    def get_by_user(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> List[Conversation]:
        return db.query(self.model).filter(self.model.user_id == user_id).offset(skip).limit(limit).all()

    def create_with_user(self, db: Session, *, obj_in: ConversationCreate, user_id: int) -> Conversation:
        db_obj = self.model(
            title=obj_in.title,
            user_id=user_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

conversation = CRUDConversation(Conversation)
