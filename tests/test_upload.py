import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import shutil
import os
from main import app
from api.endpoints.upload import UPLOAD_DIR, upload_progress

client = TestClient(app)

# Test data setup
TEST_FILE_PATH = Path("tests/data/test.sav")
TEST_FILE_CONTENT = b"Mock SPSS file content"

@pytest.fixture(autouse=True)
def setup_and_cleanup():
    """Setup test environment and cleanup after tests."""
    # Create test directories
    UPLOAD_DIR.mkdir(exist_ok=True)
    TEST_FILE_PATH.parent.mkdir(exist_ok=True)
    
    # Create mock SPSS file
    with open(TEST_FILE_PATH, "wb") as f:
        f.write(TEST_FILE_CONTENT)
    
    yield
    
    # Cleanup
    if TEST_FILE_PATH.exists():
        TEST_FILE_PATH.unlink()
    if TEST_FILE_PATH.parent.exists():
        TEST_FILE_PATH.parent.rmdir()
    shutil.rmtree(UPLOAD_DIR, ignore_errors=True)
    upload_progress.clear()

def test_upload_file_success():
    """Test successful file upload."""
    with open(TEST_FILE_PATH, "rb") as f:
        response = client.post(
            "/upload/",
            files={"file": ("test.sav", f, "application/octet-stream")}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.sav"
    assert data["status"] == "uploading"
    assert "upload_id" in data
    assert data["file_size"] > 0

def test_upload_invalid_extension():
    """Test upload with invalid file extension."""
    with open(TEST_FILE_PATH, "rb") as f:
        response = client.post(
            "/upload/",
            files={"file": ("test.txt", f, "text/plain")}
        )
    
    assert response.status_code == 422
    assert "Only SPSS .sav files are supported" in response.json()["detail"]

def test_get_upload_progress():
    """Test getting upload progress."""
    # First upload a file
    with open(TEST_FILE_PATH, "rb") as f:
        response = client.post(
            "/upload/",
            files={"file": ("test.sav", f, "application/octet-stream")}
        )
    
    upload_id = response.json()["upload_id"]
    
    # Check progress
    response = client.get(f"/upload/{upload_id}/progress")
    assert response.status_code == 200
    data = response.json()
    assert data["upload_id"] == upload_id
    assert "progress" in data
    assert "status" in data

def test_get_nonexistent_upload_progress():
    """Test getting progress for non-existent upload."""
    response = client.get("/upload/nonexistent/progress")
    assert response.status_code == 404
    assert "Upload ID not found" in response.json()["detail"]

def test_delete_upload():
    """Test deleting an upload."""
    # First upload a file
    with open(TEST_FILE_PATH, "rb") as f:
        response = client.post(
            "/upload/",
            files={"file": ("test.sav", f, "application/octet-stream")}
        )
    
    upload_id = response.json()["upload_id"]
    
    # Delete the upload
    response = client.delete(f"/upload/{upload_id}")
    assert response.status_code == 200
    assert "Upload deleted successfully" in response.json()["message"]
    
    # Verify file is deleted
    assert not (UPLOAD_DIR / upload_id).exists()
    assert upload_id not in upload_progress

def test_delete_nonexistent_upload():
    """Test deleting a non-existent upload."""
    response = client.delete("/upload/nonexistent")
    assert response.status_code == 404
    assert "File not found" in response.json()["detail"] 