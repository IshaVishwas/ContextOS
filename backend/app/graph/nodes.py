from typing import Dict, Any
from app.graph.state import ContextOSState
from app.rag.retriever import retriever
from app.algorithms.apc.prompt_builder import apc_engine
from app.llm.provider_factory import ProviderFactory
from app.evaluation.latency_tracker import Timer
from app.evaluation.metrics import EvaluationMetrics
from app.evaluation.benchmark import benchmark_manager
from app.evaluation.token_counter import calculate_savings, calculate_ratio
from app.db.session import SessionLocal

def retrieve_and_adapt_node(state: ContextOSState) -> Dict[str, Any]:
    with Timer() as timer:
        recent_messages = state.get("recent_messages") or []
        retriever_result = retriever.semantic_search(
            query=state["user_query"],
            top_k=None,
            conversation_size=len(recent_messages)
        )
    
    latencies = dict(state.get("latencies") or {})
    ret_latencies = retriever_result.get("latencies", {})
    latencies["retriever_latency"] = ret_latencies.get("retriever_latency", timer.duration)
    latencies["cam_latency"] = ret_latencies.get("cam_latency", 0.0)
    latencies["scc_latency"] = ret_latencies.get("scc_latency", 0.0)

    scc_result = retriever_result.get("scc_result", {})
    return {
        "retriever_results": retriever_result,
        "scc_results": scc_result,
        "latencies": latencies
    }

def rank_cam_node(state: ContextOSState) -> Dict[str, Any]:
    # CAM ranking is integrated within retriever.semantic_search
    return {}

def compress_scc_node(state: ContextOSState) -> Dict[str, Any]:
    # SCC compression is integrated within retriever.semantic_search
    return {}

def compile_apc_node(state: ContextOSState) -> Dict[str, Any]:
    with Timer() as apc_timer:
        scc_result = state.get("scc_results") or {}
        compressed_context = scc_result.get("compressed_context", "") if isinstance(scc_result, dict) else ""
        apc_result = apc_engine.build_prompt(
            user_query=state["user_query"],
            compressed_context=compressed_context,
            recent_messages=state.get("recent_messages") or [],
            system_instructions=state.get("system_prompt") or "You are ContextOS, an advanced AI assistant.",
            provider=state.get("provider_name", "openai")
        )

    latencies = dict(state.get("latencies") or {})
    latencies["apc_latency"] = apc_timer.duration
    return {
        "apc_result": apc_result,
        "latencies": latencies
    }

def execute_llm_node(state: ContextOSState) -> Dict[str, Any]:
    with Timer() as llm_timer:
        provider_name = state.get("provider_name", "openai")
        apc_result = state.get("apc_result")
        formatted_prompt = apc_result.formatted_prompt if apc_result else state["user_query"]
        
        provider = ProviderFactory.get_provider(provider_name)
        llm_response = provider.generate_response(formatted_prompt)

    latencies = dict(state.get("latencies") or {})
    latencies["llm_latency"] = llm_timer.duration
    return {
        "llm_response": llm_response,
        "latencies": latencies
    }

def record_evaluation_node(state: ContextOSState) -> Dict[str, Any]:
    scc_result = state.get("scc_results") or {}
    latencies = state.get("latencies") or {}
    retriever_results = state.get("retriever_results") or {}

    orig_tokens = scc_result.get("original_memory_count", 0) * 50 if isinstance(scc_result, dict) else 0
    comp_tokens = scc_result.get("compressed_memory_count", 0) * 30 if isinstance(scc_result, dict) else 0
    
    total_latency = sum(latencies.values())

    metrics = EvaluationMetrics(
        query=state["user_query"],
        provider=state.get("provider_name", "openai"),
        conversation_id=state.get("conversation_id", 0),
        retrieved_memories=len(retriever_results.get("ranked_results", [])) if isinstance(retriever_results, dict) else 0,
        selected_memories=scc_result.get("original_memory_count", 0) if isinstance(scc_result, dict) else 0,
        compression_ratio=calculate_ratio(orig_tokens, comp_tokens),
        original_tokens=orig_tokens,
        compressed_tokens=comp_tokens,
        token_saved=calculate_savings(orig_tokens, comp_tokens),
        retriever_latency=latencies.get("retriever_latency", 0.0),
        cam_latency=latencies.get("cam_latency", 0.0),
        scc_latency=latencies.get("scc_latency", 0.0),
        apc_latency=latencies.get("apc_latency", 0.0),
        llm_latency=latencies.get("llm_latency", 0.0),
        total_latency=total_latency
    )

    evaluation_id = None
    db = SessionLocal()
    try:
        evaluation_id = benchmark_manager.save_evaluation_run(db, metrics)
    except Exception as e:
        print(f"Failed to save evaluation run: {e}")
    finally:
        db.close()

    return {
        "evaluation_id": evaluation_id
    }
