from typing import Dict, Any, List
from app.graph.workflow import contextos_graph
from app.graph.state import ContextOSState

class LLMService:
    def execute_pipeline(
        self, 
        provider_name: str, 
        user_query: str, 
        conversation_id: int = 0,
        system_prompt: str = "You are ContextOS, an advanced AI assistant.", 
        recent_messages: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        if recent_messages is None:
            recent_messages = []

        initial_state: ContextOSState = {
            "user_query": user_query,
            "provider_name": provider_name,
            "conversation_id": conversation_id,
            "system_prompt": system_prompt,
            "recent_messages": recent_messages,
            "retriever_results": None,
            "scc_results": None,
            "apc_result": None,
            "llm_response": None,
            "latencies": {},
            "evaluation_id": None,
            "error": None
        }

        # Execute compiled LangGraph workflow
        final_state = contextos_graph.invoke(initial_state)

        scc_result = final_state.get("scc_results") or {}
        apc_result = final_state.get("apc_result")
        llm_response = final_state.get("llm_response")

        formatted_prompt = apc_result.formatted_prompt if apc_result else user_query
        apc_metrics = {
            "estimated_tokens": apc_result.estimated_tokens,
            "memory_tokens": apc_result.memory_tokens,
            "conversation_tokens": apc_result.conversation_tokens,
            "system_tokens": apc_result.system_tokens,
            "user_query_tokens": apc_result.user_query_tokens
        } if apc_result else {}

        response_dict = llm_response.model_dump() if hasattr(llm_response, "model_dump") else (llm_response.__dict__ if hasattr(llm_response, "__dict__") else {})

        return {
            "evaluation_id": final_state.get("evaluation_id"),
            "optimized_prompt": formatted_prompt,
            "pipeline_metrics": {
                "scc_metrics": scc_result,
                "apc_metrics": apc_metrics
            },
            "llm_response": response_dict
        }

llm_service = LLMService()
