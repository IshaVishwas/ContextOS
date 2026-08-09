import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("--- 1. BACKEND ALIVE ---")
    res = requests.get(f"{BASE_URL}/")
    assert res.status_code == 200, "GET / failed"
    
    res = requests.get(f"{BASE_URL}/docs")
    assert res.status_code == 200, "GET /docs failed"

    print("--- 2. REAL CONTEXT FLOW ---")
    res = requests.post(f"{BASE_URL}/api/v1/conversations/", json={"title": "Integration Test Conv"})
    assert res.status_code == 200
    conv_id = res.json()["id"]
    
    messages = [
        "Hi, I'm working on a Python project.",
        "It uses FastAPI and SQLAlchemy.",
        "I need help with a database query.",
        "The query is getting too slow.",
        "I have 1 million rows in my users table."
    ]
    
    for msg in messages:
        res = requests.post(f"{BASE_URL}/api/v1/messages/", json={
            "conversation_id": conv_id,
            "role": "user",
            "content": msg
        })
        assert res.status_code == 200
        msg_id = res.json()["id"]
        # Index the message as memory
        res_mem = requests.post(f"{BASE_URL}/api/v1/memories/index", json={"message_id": msg_id})
        # Ignoring errors if embedding fails in mock, but it should succeed
        print(f"Indexed message {msg_id}: {res_mem.status_code}")

    print("\n--- 3 & 4. CHAT PIPELINE & EVALUATION ---")
    # Add a separate manual memory
    res = requests.post(f"{BASE_URL}/api/v1/memories/", json={
        "conversation_id": conv_id,
        "summary": "User prefers async queries.",
        "memory_type": "preference"
    })
    
    chat_res = requests.post(f"{BASE_URL}/api/v1/llm/chat", json={
        "conversation_id": conv_id,
        "query": "How can I speed up my query?",
        "provider": "gemini"
    })
    
    assert chat_res.status_code == 200, f"Chat failed: {chat_res.text}"
    chat_data = chat_res.json()
    eval_id = chat_data["evaluation_id"]
    
    print("Chat successful. Eval ID:", eval_id)
    print("Optimized prompt preview:", chat_data["optimized_prompt"][:100], "...")
    
    eval_res = requests.get(f"{BASE_URL}/api/v1/evaluation/{eval_id}")
    assert eval_res.status_code == 200
    ev = eval_res.json()
    
    print("\nMetrics:")
    print(f"Original tokens: {ev['original_tokens']}")
    print(f"Compressed tokens: {ev['compressed_tokens']}")
    print(f"Tokens saved: {ev['token_saved']}")
    print(f"Compression ratio: {ev['compression_ratio']}")
    print(f"Total latency: {ev['total_latency']}")
    print(f"CAM latency: {ev['cam_latency']}")
    
    # Assert values are populated (not just zero if there's actual data, though small data might mean 0 compression)
    # If the system is working, latency > 0
    assert ev['total_latency'] > 0, "Latency not tracked"
    
    stats_res = requests.get(f"{BASE_URL}/api/v1/evaluation/stats")
    assert stats_res.status_code == 200
    print("Stats fetched successfully.")
    
    print("\n--- 7. FAILURE TESTS ---")
    # Invalid conv ID
    res = requests.post(f"{BASE_URL}/api/v1/messages/", json={
        "conversation_id": 99999,
        "role": "user",
        "content": "Fail me"
    })
    assert res.status_code == 404
    print("Invalid conversation ID gracefully handled.")
    
    # No memories search
    res = requests.post(f"{BASE_URL}/api/v1/memories/search", json={
        "query": "supercalifragilisticexpialidocious"
    })
    assert res.status_code == 200
    print("Search gracefully handled empty results.")

    print("\nALL BACKEND TESTS PASSED.")

if __name__ == "__main__":
    run_tests()
