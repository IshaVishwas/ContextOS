from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.llm.llm_service import llm_service
from app.llm.config import LLMConfig
from app.api import deps
from app import crud

router = APIRouter()

class ChatRequest(BaseModel):
    conversation_id: int
    query: str
    provider: Optional[str] = None
    system_prompt: Optional[str] = "You are ContextOS, an advanced AI assistant."

@router.post("/chat")
def chat_with_llm(
    request: ChatRequest,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
):
    # Verify conversation exists and belongs to user
    conversation = crud.conversation.get(db=db, id=request.conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # Fetch recent messages
    # We might want to limit this in the future, but for now we fetch all existing context
    db_messages = crud.message.get_by_conversation(db=db, conversation_id=request.conversation_id)
    recent_messages = [{"role": msg.role, "content": msg.content} for msg in db_messages]

    provider_name = request.provider or LLMConfig.DEFAULT_PROVIDER
    try:
        result = llm_service.execute_pipeline(
            provider_name=provider_name,
            user_query=request.query,
            conversation_id=request.conversation_id,
            system_prompt=request.system_prompt,
            recent_messages=recent_messages
        )
        result["provider"] = provider_name
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

