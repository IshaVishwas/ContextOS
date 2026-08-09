from typing import Dict, Any, List, Optional
from typing_extensions import TypedDict

class ContextOSState(TypedDict):
    user_query: str
    provider_name: str
    conversation_id: int
    system_prompt: str
    recent_messages: List[Dict[str, str]]
    
    # Node outputs
    retriever_results: Optional[Dict[str, Any]]
    scc_results: Optional[Dict[str, Any]]
    apc_result: Optional[Any]
    llm_response: Optional[Any]
    
    # Metrics
    latencies: Dict[str, float]
    evaluation_id: Optional[int]
    error: Optional[str]
