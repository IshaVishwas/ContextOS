from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.analytics import Analytics
from app.schemas.analytics import AnalyticsCreate, AnalyticsUpdate

class CRUDAnalytics(CRUDBase[Analytics, AnalyticsCreate, AnalyticsUpdate]):
    def get_by_user(self, db: Session, *, user_id: int) -> Optional[Analytics]:
        return db.query(self.model).filter(self.model.user_id == user_id).first()

    def create_with_user(self, db: Session, *, user_id: int) -> Analytics:
        db_obj = self.model(user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

analytics = CRUDAnalytics(Analytics)
