import uuid
from sqlalchemy.orm import Session
from app import crud
from app.rag.embedding_service import embedding_service
from app.rag.vector_store import vector_store
from app.schemas.memory import MemoryCreate
from app.models.memory import Memory

class MemoryIndexer:
    def __init__(self, collection_name: str = "memories"):
        self.collection_name = collection_name

    def index_message(self, db: Session, message_id: int) -> Memory:
        # Fetch the message
        message = crud.message.get(db=db, id=message_id)
        if not message:
            raise ValueError(f"Message {message_id} not found")

        # Generate embedding
        embedding = embedding_service.generate_embedding(message.content)

        # Generate a unique ChromaDB ID
        chroma_id = str(uuid.uuid4())

        # Metadata for ChromaDB
        metadata = {
            "conversation_id": message.conversation_id,
            "message_id": message.id,
            "role": message.role,
            "type": "message_index"
        }

        # Store in ChromaDB
        vector_store.insert_vector(
            collection_name=self.collection_name,
            id=chroma_id,
            vector=embedding,
            metadata=metadata,
            document=message.content
        )

        # Create Memory record
        memory_in = MemoryCreate(
            conversation_id=message.conversation_id,
            title=f"Memory from message {message.id}",
            summary=message.content[:200] + "..." if len(message.content) > 200 else message.content,
            memory_type="message_index",
            importance_score=1.0, # Default score
            embedding_reference=chroma_id,
            metadata_={"message_id": message.id}
        )

        memory = crud.memory.create(db=db, obj_in=memory_in)
        return memory

    def reindex_memory(self, db: Session, memory_id: int) -> Memory:
        memory = crud.memory.get(db=db, id=memory_id)
        if not memory:
            raise ValueError(f"Memory {memory_id} not found")

        # Generate new embedding based on summary
        embedding = embedding_service.generate_embedding(memory.summary)

        metadata = {
            "conversation_id": memory.conversation_id,
            "memory_id": memory.id,
            "type": memory.memory_type
        }
        
        # If no embedding_reference exists, create one
        if not memory.embedding_reference:
            chroma_id = str(uuid.uuid4())
            memory.embedding_reference = chroma_id
            db.commit()
            
            vector_store.insert_vector(
                collection_name=self.collection_name,
                id=memory.embedding_reference,
                vector=embedding,
                metadata=metadata,
                document=memory.summary
            )
        else:
            vector_store.update_vector(
                collection_name=self.collection_name,
                id=memory.embedding_reference,
                vector=embedding,
                metadata=metadata,
                document=memory.summary
            )
            
        return memory

memory_indexer = MemoryIndexer()
