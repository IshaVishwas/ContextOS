import requests
import json
import time
import random

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print("--- CONTEXTOS QA SCRIPT ---")
    
    email = f"qa_user_{random.randint(1000,9999)}@example.com"
    print("\n0. Testing Authentication...")
    reg = requests.post(f"{BASE_URL}/api/v1/auth/register", json={
        "email": email,
        "password": "qa_password",
        "full_name": "QA Tester"
    })
    
    if reg.status_code == 200 or reg.status_code == 400: # 400 if already exists
        login = requests.post(f"{BASE_URL}/api/v1/auth/login", data={
            "username": email,
            "password": "qa_password"
        })
        if login.status_code == 200:
            token = login.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            print(f"SUCCESS: Logged in as {email}")
        else:
            print(f"FAILED to login: {login.text}")
            return
    else:
        print(f"FAILED to register: {reg.text}")
        return

    # 1. Test Conversation Creation
    print("\n1. Testing Conversation Creation...")
    res = requests.post(f"{BASE_URL}/api/v1/conversations/", json={"title": "QA Test Conversation"}, headers=headers)
    if res.status_code == 200:
        conv = res.json()
        conv_id = conv['id']
        print(f"SUCCESS: Conversation created: ID {conv_id}")
    else:
        print(f"FAILED to create conversation: {res.text}")
        return

    # 2. Add User Message
    print("\n2. Testing Message Creation...")
    res = requests.post(f"{BASE_URL}/api/v1/messages/", json={
        "conversation_id": conv_id,
        "role": "user",
        "content": "Hello ContextOS! This is a QA test."
    }, headers=headers)
    if res.status_code == 200:
        print("SUCCESS: User message added.")
    else:
        print(f"FAILED to add message: {res.text}")
        return

    # 3. Add Memory
    print("\n3. Testing Memory Creation...")
    res = requests.post(f"{BASE_URL}/api/v1/memories/", json={
        "conversation_id": conv_id,
        "summary": "The QA tester's favorite color is electric blue.",
        "memory_type": "qa_fact",
        "metadata_": {"source": "qa_script", "importance": 0.9}
    }, headers=headers)
    if res.status_code == 200:
        print("SUCCESS: Memory added.")
    else:
        print(f"FAILED to add memory: {res.text}")

    # 4. LLM Chat Pipeline
    print("\n4. Testing LLM Chat Pipeline...")
    res = requests.post(f"{BASE_URL}/api/v1/llm/chat", json={
        "conversation_id": conv_id,
        "provider": "gemini",
        "query": "What is my favorite color?"
    }, headers=headers)
    if res.status_code == 200:
        chat_data = res.json()
        print("SUCCESS: Chat Pipeline Success!")
        print(f"   Provider: {chat_data.get('provider')}")
        print(f"   Evaluation ID: {chat_data.get('evaluation_id')}")
        eval_id = chat_data.get('evaluation_id')
    else:
        print(f"FAILED Chat Pipeline Failed: {res.text}")
        eval_id = None

    # 5. Evaluation Details
    if eval_id:
        print(f"\n5. Testing Evaluation Details ({eval_id})...")
        res = requests.get(f"{BASE_URL}/api/v1/evaluation/{eval_id}", headers=headers)
        if res.status_code == 200:
            ev = res.json()
            print("SUCCESS: Evaluation retrieval success!")
            print(f"   Compression Ratio: {ev.get('compression_ratio')}")
            print(f"   Tokens Saved: {ev.get('token_saved')}")
            print(f"   Total Latency: {ev.get('total_latency')}")
        else:
            print(f"FAILED Evaluation Retrieval Failed: {res.text}")

if __name__ == "__main__":
    test_api()
