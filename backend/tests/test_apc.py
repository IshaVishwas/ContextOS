import pytest
from app.algorithms.apc.prompt_builder import apc_engine
from app.algorithms.apc.config import APCConfig

def test_apc_token_budget_pruning():
    # Construct an oversized memory block
    oversized_memory = "A" * 100000  # Will definitely exceed budget
    system_instructions = "You are a helpful assistant."
    user_query = "What is the capital of France?"
    recent_messages = [{"role": "user", "content": "Hello"}]

    result = apc_engine.build_prompt(
        user_query=user_query,
        compressed_context=oversized_memory,
        recent_messages=recent_messages,
        system_instructions=system_instructions,
        provider="openai"
    )

    max_memory_tokens = APCConfig.MAX_TOKENS * APCConfig.ALLOCATION["memory"]
    
    # Assert that memory tokens are capped at the budget limit
    assert result.memory_tokens <= max_memory_tokens
    
    # Ensure system tokens and user query are intact
    assert result.system_tokens > 0
    assert result.user_query_tokens > 0
    assert result.prompt_payload.system_prompt == system_instructions
    assert result.prompt_payload.user_query == user_query

def test_apc_template_openai():
    result = apc_engine.build_prompt(
        user_query="Q",
        compressed_context="Ctx",
        recent_messages=[{"role": "user", "content": "Hi"}],
        system_instructions="Sys",
        provider="openai"
    )
    
    formatted = result.formatted_prompt
    assert isinstance(formatted, list)
    assert formatted[0]["role"] == "system"
    assert "Sys" in formatted[0]["content"]
    assert "Ctx" in formatted[0]["content"]
    assert formatted[1]["role"] == "user"
    assert formatted[1]["content"] == "Hi"
    assert formatted[2]["role"] == "user"
    assert formatted[2]["content"] == "Q"

def test_apc_template_anthropic():
    result = apc_engine.build_prompt(
        user_query="Q",
        compressed_context="Ctx",
        recent_messages=[{"role": "user", "content": "Hi"}],
        system_instructions="Sys",
        provider="anthropic"
    )
    
    formatted = result.formatted_prompt
    assert isinstance(formatted, str)
    assert "<system>\nSys\n</system>" in formatted
    assert "<context>\nCtx\n</context>" in formatted
    assert "<user>Hi</user>" in formatted
    assert "<query>\nQ\n</query>" in formatted
