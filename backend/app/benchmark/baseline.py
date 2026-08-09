import time
from typing import Dict, Any, List
from app.benchmark.metrics import BenchmarkResult
from app.evaluation.latency_tracker import Timer
from app.llm.provider_factory import ProviderFactory

def calculate_tokens(text: str) -> int:
    # Standard approximation
    return len(text) // 4

def check_fact_retention(prompt: str, expected_facts: List[str]) -> int:
    return sum(1 for fact in expected_facts if fact.lower() in prompt.lower())

def run_baseline(iteration: int, data: Dict[str, Any], provider_name: str = "gemini") -> BenchmarkResult:
    size = data["size"]
    messages = data["messages"]
    query = data["query"]
    expected_facts = data["expected_facts"]
    
    with Timer() as total_timer:
        # 1. Monolithic concatenation
        monolithic_prompt = "You are an AI.\n"
        for msg in messages:
            monolithic_prompt += f"{msg['role']}: {msg['content']}\n"
        monolithic_prompt += f"user: {query}"
        
        # 2. Fake LLM Execution (we just measure pipeline overhead, so maybe skip actual LLM call
        # but to be fair, let's call the mock provider if we want total latency)
        with Timer() as llm_timer:
            provider = ProviderFactory.get_provider(provider_name)
            # provider.generate_response(monolithic_prompt) # We can skip actual network to isolate pipeline

    orig_tokens = calculate_tokens(monolithic_prompt)
    retained_facts = check_fact_retention(monolithic_prompt, expected_facts)
    
    # In baseline, everything is retained because we just dump everything.
    # Irrelevant information removed is 0% because everything is passed.
    
    return BenchmarkResult(
        pipeline="baseline",
        conversation_size=size,
        iteration=iteration,
        original_tokens=orig_tokens,
        final_prompt_tokens=orig_tokens, # Baseline passes everything
        token_reduction=0,
        token_reduction_percentage=0.0,
        retrieval_count=0,
        selected_memory_count=0,
        compression_ratio=1.0,
        retrieval_latency=0.0,
        cam_latency=0.0,
        scc_latency=0.0,
        apc_latency=0.0,
        total_pipeline_latency=total_timer.duration,
        relevant_facts_originally_present=len(expected_facts),
        relevant_facts_retained=retained_facts,
        relevant_fact_retention_percentage=100.0 if expected_facts else 100.0,
        irrelevant_information_removed_percentage=0.0
    )
