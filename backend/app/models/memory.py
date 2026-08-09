from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=True)
    summary = Column(Text, nullable=False)
    memory_type = Column(String, index=True, nullable=False) # e.g., entity, summary, fact
    importance_score = Column(Float, default=0.0)
    embedding_reference = Column(String, nullable=True) # Ref to ChromaDB
    metadata_ = Column("metadata", JSON, nullable=True) # Renamed to avoid conflicts with SQLAlchemy Base.metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    conversation = relationship("Conversation", back_populates="memories")
