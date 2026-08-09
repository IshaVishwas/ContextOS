import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def create_user_and_get_token():
    email = f"test_{uuid.uuid4()}@example.com"
    password = "password123"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Test User"}
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password}
    )
    return response.json()["access_token"]

def test_authenticated_conversation_creation():
    token = create_user_and_get_token()
    response = client.post(
        "/api/v1/conversations/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "My Conversation", "system_prompt": "You are helpful."}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data

def test_unauthorized_conversation_access():
    token = create_user_and_get_token()
    # Create conversation
    response = client.post(
        "/api/v1/conversations/",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "My Conversation", "system_prompt": "You are helpful."}
    )
    conv_id = response.json()["id"]
    
    # Access without token
    response2 = client.get(f"/api/v1/conversations/{conv_id}")
    assert response2.status_code == 401

def test_cross_user_conversation_access():
    token1 = create_user_and_get_token()
    token2 = create_user_and_get_token()
    
    # User 1 creates conversation
    response = client.post(
        "/api/v1/conversations/",
        headers={"Authorization": f"Bearer {token1}"},
        json={"title": "My Conversation", "system_prompt": "You are helpful."}
    )
    conv_id = response.json()["id"]
    
    # User 2 tries to access User 1's conversation
    response2 = client.get(
        f"/api/v1/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response2.status_code == 403

def test_cross_user_message_access():
    token1 = create_user_and_get_token()
    token2 = create_user_and_get_token()
    
    # User 1 creates conversation and message
    conv_res = client.post(
        "/api/v1/conversations/",
        headers={"Authorization": f"Bearer {token1}"},
        json={"title": "My Conversation", "system_prompt": "You are helpful."}
    )
    conv_id = conv_res.json()["id"]
    
    msg_res = client.post(
        "/api/v1/messages/",
        headers={"Authorization": f"Bearer {token1}"},
        json={"conversation_id": conv_id, "role": "user", "content": "Hello"}
    )
    msg_id = msg_res.json()["id"]
    
    # User 2 tries to access User 1's message
    response2 = client.get(
        f"/api/v1/messages/{msg_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response2.status_code == 403

def test_cross_user_memory_access():
    token1 = create_user_and_get_token()
    token2 = create_user_and_get_token()
    
    # User 1 creates conversation and memory
    conv_res = client.post(
        "/api/v1/conversations/",
        headers={"Authorization": f"Bearer {token1}"},
        json={"title": "My Conversation", "system_prompt": "You are helpful."}
    )
    conv_id = conv_res.json()["id"]
    
    mem_res = client.post(
        "/api/v1/memories/",
        headers={"Authorization": f"Bearer {token1}"},
        json={"conversation_id": conv_id, "summary": "A fact about me", "memory_type": "semantic"}
    )
    assert mem_res.status_code == 200
    
    # User 2 tries to list User 1's memories by passing conversation_id
    response2 = client.get(
        f"/api/v1/memories/?conversation_id={conv_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response2.status_code == 403
