from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app import crud, schemas

router = APIRouter()

@router.get("/", response_model=schemas.Analytics)
def get_analytics(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve user analytics.
    """
    analytics = crud.analytics.get_by_user(db=db, user_id=current_user.id)
    if not analytics:
        # Create empty analytics if not exists
        analytics = crud.analytics.create_with_user(db=db, user_id=current_user.id)
    return analytics
