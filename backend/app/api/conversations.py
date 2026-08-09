from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app import crud, schemas

router = APIRouter()

@router.post("/", response_model=schemas.Conversation)
def create_conversation(
    *,
    db: Session = Depends(deps.get_db),
    conversation_in: schemas.ConversationCreate,
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    Create new conversation.
    """
    conversation = crud.conversation.create_with_user(db=db, obj_in=conversation_in, user_id=current_user.id)
    return conversation

@router.get("/history", response_model=List[schemas.Conversation])
def get_conversation_history(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve conversation history.
    """
    conversations = crud.conversation.get_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)
    return conversations

@router.get("/{id}", response_model=schemas.ConversationWithDetails)
def get_conversation(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    Get conversation by ID.
    """
    conversation = crud.conversation.get(db=db, id=id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return conversation

@router.delete("/{id}", response_model=schemas.Conversation)
def delete_conversation(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a conversation.
    """
    conversation = crud.conversation.get(db=db, id=id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    conversation = crud.conversation.remove(db=db, id=id)
    return conversation
