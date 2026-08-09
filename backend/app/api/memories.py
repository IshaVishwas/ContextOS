from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app import crud, schemas

router = APIRouter()

@router.post("/", response_model=schemas.Memory)
def create_memory(
    *,
    db: Session = Depends(deps.get_db),
    memory_in: schemas.MemoryCreate,
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new memory manually.
    """
    conversation = crud.conversation.get(db=db, id=memory_in.conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    memory = crud.memory.create(db=db, obj_in=memory_in)
    return memory

@router.get("/", response_model=List[schemas.Memory])
def get_memories(
    conversation_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve memories for a conversation.
    """
    conversation = crud.conversation.get(db=db, id=conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    memories = crud.memory.get_by_conversation(db=db, conversation_id=conversation_id, skip=skip, limit=limit)
    return memories

@router.post("/index", response_model=schemas.Memory)
def index_memory(
    request: schemas.MemoryIndexRequest,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    Index a message into semantic memory.
    """
    from app.rag.memory_indexer import memory_indexer
    try:
        memory = memory_indexer.index_message(db=db, message_id=request.message_id)
        return memory
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
def search_memories(
    request: schemas.MemorySearchRequest,
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    Search semantic memories.
    """
    from app.rag.retriever import retriever
    try:
        results = retriever.semantic_search(
            query=request.query,
            top_k=request.top_k,
            metadata_filter=request.metadata_filter,
            similarity_threshold=request.similarity_threshold
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reindex", response_model=schemas.Memory)
def reindex_memory(
    request: schemas.MemoryReindexRequest,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    Reindex an existing memory.
    """
    from app.rag.memory_indexer import memory_indexer
    try:
        memory = memory_indexer.reindex_memory(db=db, memory_id=request.memory_id)
        return memory
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vector/{id}")
def get_vector(
    id: str,
    current_user = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve raw vector from ChromaDB.
    """
    from app.rag.vector_store import vector_store
    try:
        vector = vector_store.get_vector(collection_name="memories", id=id)
        if not vector or not vector.get('ids'):
            raise HTTPException(status_code=404, detail="Vector not found")
        return {"vector": vector}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

