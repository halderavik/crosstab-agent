import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
import json
from datetime import datetime
from main import app
from api.endpoints.chat import chat_sessions

client = TestClient(app)

# Test data setup
TEST_SESSION_ID = "test_session_123"
TEST_MESSAGE = {
    "role": "user",
    "content": "What is the relationship between var1 and var2?",
    "timestamp": datetime.now().isoformat()
}

@pytest.fixture(autouse=True)
def setup_and_cleanup():
    """Setup test environment and cleanup after tests."""
    # Create test chat session
    chat_sessions[TEST_SESSION_ID] = {
        "messages": [],
        "analysis_references": set()
    }
    
    yield
    
    # Cleanup
    chat_sessions.clear()

def test_chat_completion():
    """Test chat completion endpoint."""
    response = client.post(
        "/api/v1/chat/completion",
        json={
            "messages": [TEST_MESSAGE],
            "analysis_id": "test_analysis_123",
            "stream": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"]["role"] == "assistant"
    assert "content" in data["message"]
    assert "analysis_references" in data

def test_get_chat_session():
    """Test getting chat session history."""
    # First add some messages
    chat_sessions[TEST_SESSION_ID]["messages"].append(TEST_MESSAGE)
    chat_sessions[TEST_SESSION_ID]["analysis_references"].add("test_analysis_123")
    
    response = client.get(f"/api/v1/chat/session/{TEST_SESSION_ID}")
    
    assert response.status_code == 200
    data = response.json()
    assert "messages" in data
    assert "analysis_references" in data
    assert len(data["messages"]) == 1
    assert "test_analysis_123" in data["analysis_references"]

def test_delete_chat_session():
    """Test deleting chat session."""
    response = client.delete(f"/api/v1/chat/session/{TEST_SESSION_ID}")
    
    assert response.status_code == 200
    assert response.json()["message"] == "Chat session deleted successfully"
    assert TEST_SESSION_ID not in chat_sessions

def test_nonexistent_chat_session():
    """Test operations with non-existent chat session."""
    # Test getting non-existent session
    response = client.get("/api/v1/chat/session/nonexistent")
    assert response.status_code == 404
    
    # Test deleting non-existent session
    response = client.delete("/api/v1/chat/session/nonexistent")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_websocket_chat():
    """Test WebSocket chat functionality."""
    # Create WebSocket connection
    with client.websocket_connect(f"/api/v1/chat/ws/{TEST_SESSION_ID}") as websocket:
        # Send message
        await websocket.send_text(json.dumps(TEST_MESSAGE))
        
        # Receive response chunks
        while True:
            data = json.loads(websocket.receive_text())
            if data["type"] == "complete":
                break
            assert data["type"] == "chunk"
            assert "content" in data

@pytest.mark.asyncio
async def test_websocket_error_handling():
    """Test WebSocket error handling."""
    with client.websocket_connect(f"/api/v1/chat/ws/{TEST_SESSION_ID}") as websocket:
        # Send invalid message
        await websocket.send_text("invalid json")
        
        # Receive error message
        data = json.loads(websocket.receive_text())
        assert data["type"] == "error"
        assert "content" in data

def test_chat_completion_with_streaming():
    """Test chat completion with streaming."""
    response = client.post(
        "/api/v1/chat/completion",
        json={
            "messages": [TEST_MESSAGE],
            "analysis_id": "test_analysis_123",
            "stream": True
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"]["role"] == "assistant"
    assert "content" in data["message"]
    assert "analysis_references" in data 