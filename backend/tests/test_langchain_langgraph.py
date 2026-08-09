import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.llm.provider_factory import ProviderFactory
from app.llm.openai_provider import OpenAIProvider
from app.llm.gemini_provider import GeminiProvider
from app.llm.anthropic_provider import AnthropicProvider
from app.graph.workflow import contextos_graph
from app.graph.state import ContextOSState

client = TestClient(app)

def test_langchain_provider_instantiation():
    openai_prov = ProviderFactory.get_provider("openai")
    gemini_prov = ProviderFactory.get_provider("gemini")
    anthropic_prov = ProviderFactory.get_provider("anthropic")

    assert isinstance(openai_prov, OpenAIProvider)
    assert isinstance(gemini_prov, GeminiProvider)
    assert isinstance(anthropic_prov, AnthropicProvider)

def test_fallback_behavior_without_api_keys():
    openai_prov = OpenAIProvider()
    resp = openai_prov.generate_response("Hello")
    assert resp.provider == "openai"
    assert resp.response == "OpenAI API Key not configured."

    gemini_prov = GeminiProvider()
    resp = gemini_prov.generate_response("Hello")
    assert resp.provider == "gemini"
    assert "Gemini API Key not configured" in resp.response

    anthropic_prov = AnthropicProvider()
    resp = anthropic_prov.generate_response("Hello")
    assert resp.provider == "anthropic"
    assert resp.response == "Anthropic API Key not configured."

def test_openai_lc_message_conversion():
    prov = OpenAIProvider()
    prompt = [
        {"role": "system", "content": "System text"},
        {"role": "user", "content": "User text"}
    ]
    messages = prov._convert_to_lc_messages(prompt)
    assert len(messages) == 2
    assert messages[0].content == "System text"
    assert messages[1].content == "User text"

def test_langgraph_workflow_execution():
    initial_state: ContextOSState = {
        "user_query": "What is ContextOS?",
        "provider_name": "gemini",
        "conversation_id": 1,
        "system_prompt": "You are a helpful assistant.",
        "recent_messages": [],
        "retriever_results": None,
        "scc_results": None,
        "apc_result": None,
        "llm_response": None,
        "latencies": {},
        "evaluation_id": None,
        "error": None
    }

    final_state = contextos_graph.invoke(initial_state)

    assert final_state["scc_results"] is not None
    assert final_state["apc_result"] is not None
    assert final_state["llm_response"] is not None
    assert "retriever_latency" in final_state["latencies"]
    assert "apc_latency" in final_state["latencies"]
    assert "llm_latency" in final_state["latencies"]

def test_evaluation_stats_endpoint_unauthenticated_and_authenticated():
    # 1. Test GET /api/v1/evaluation/stats without Auth header
    response = client.get("/api/v1/evaluation/stats")
    assert response.status_code == 200

    # 2. Test GET /api/v1/evaluation/stats with Auth header
    reg_res = client.post("/api/v1/auth/register", json={"email": "stats_test@example.com", "password": "password123"})
    login_res = client.post("/api/v1/auth/login", data={"username": "stats_test@example.com", "password": "password123"})
    token = login_res.json()["access_token"]

    response_auth = client.get("/api/v1/evaluation/stats", headers={"Authorization": f"Bearer {token}"})
    assert response_auth.status_code == 200
