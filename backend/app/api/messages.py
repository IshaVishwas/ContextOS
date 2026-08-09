from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app import crud, schemas

router = APIRouter()

@router.post("/", response_model=schemas.Message)
def create_message(
    *,
    db: Session = Depends(deps.get_db),
    message_in: schemas.MessageCreate,
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    Create new message.
    """
    # Verify conversation belongs to user
    conversation = crud.conversation.get(db=db, id=message_in.conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    message = crud.message.create(db=db, obj_in=message_in)
    return message

@router.get("/{id}", response_model=schemas.Message)
def get_message(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    Get message by ID.
    """
    message = crud.message.get(db=db, id=id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
        
    conversation = crud.conversation.get(db=db, id=message.conversation_id)
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return message
