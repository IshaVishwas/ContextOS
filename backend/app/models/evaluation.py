from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    
    retrieved_memories = Column(Integer, default=0)
    selected_memories = Column(Integer, default=0)
    
    compression_ratio = Column(Float, default=0.0)
    original_tokens = Column(Integer, default=0)
    compressed_tokens = Column(Integer, default=0)
    token_saved = Column(Integer, default=0)
    
    retriever_latency = Column(Float, default=0.0)
    cam_latency = Column(Float, default=0.0)
    scc_latency = Column(Float, default=0.0)
    apc_latency = Column(Float, default=0.0)
    llm_latency = Column(Float, default=0.0)
    total_latency = Column(Float, default=0.0)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
