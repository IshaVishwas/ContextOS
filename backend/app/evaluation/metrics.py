from pydantic import BaseModel
from typing import Optional

class EvaluationMetrics(BaseModel):
    query: str
    provider: str
    conversation_id: int
    
    retrieved_memories: int = 0
    selected_memories: int = 0
    
    compression_ratio: float = 0.0
    original_tokens: int = 0
    compressed_tokens: int = 0
    token_saved: int = 0
    
    retriever_latency: float = 0.0
    cam_latency: float = 0.0
    scc_latency: float = 0.0
    apc_latency: float = 0.0
    llm_latency: float = 0.0
    total_latency: float = 0.0
