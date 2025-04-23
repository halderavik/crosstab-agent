import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import shutil
import os
import json
import pandas as pd
from main import app
from api.endpoints.analysis import analysis_results
from api.endpoints.upload import UPLOAD_DIR

client = TestClient(app)

# Test data setup
TEST_FILE_PATH = Path("tests/data/test.sav")
TEST_FILE_CONTENT = b"Mock SPSS file content"
TEST_ANALYSIS_ID = "test_analysis_123"

@pytest.fixture(autouse=True)
def setup_and_cleanup():
    """Setup test environment and cleanup after tests."""
    # Create test directories
    UPLOAD_DIR.mkdir(exist_ok=True)
    TEST_FILE_PATH.parent.mkdir(exist_ok=True)
    
    # Create mock SPSS file
    with open(TEST_FILE_PATH, "wb") as f:
        f.write(TEST_FILE_CONTENT)
    
    # Create mock analysis result
    analysis_results[TEST_ANALYSIS_ID] = {
        "status": "completed",
        "results": {
            "data": [[1, 2], [3, 4]],
            "columns": ["A", "B"],
            "rows": ["X", "Y"]
        },
        "metadata": {
            "timestamp": "2024-03-21T12:00:00"
        }
    }
    
    yield
    
    # Cleanup
    if TEST_FILE_PATH.exists():
        TEST_FILE_PATH.unlink()
    if TEST_FILE_PATH.parent.exists():
        TEST_FILE_PATH.parent.rmdir()
    shutil.rmtree(UPLOAD_DIR, ignore_errors=True)
    analysis_results.clear()

def test_perform_crosstab():
    """Test cross-tabulation analysis."""
    # First upload a file
    with open(TEST_FILE_PATH, "rb") as f:
        upload_response = client.post(
            "/api/v1/upload/",
            files={"file": ("test.sav", f, "application/octet-stream")}
        )
    
    upload_id = upload_response.json()["upload_id"]
    
    # Perform cross-tabulation
    response = client.post(
        f"/api/v1/analyze/crosstab/{upload_id}",
        json={
            "row_variable": "var1",
            "column_variable": "var2",
            "include_percentages": True,
            "include_totals": True
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert data["status"] == "completed"
    assert "results" in data

def test_perform_statistical_analysis():
    """Test statistical analysis."""
    # First upload a file
    with open(TEST_FILE_PATH, "rb") as f:
        upload_response = client.post(
            "/api/v1/upload/",
            files={"file": ("test.sav", f, "application/octet-stream")}
        )
    
    upload_id = upload_response.json()["upload_id"]
    
    # Perform statistical analysis
    response = client.post(
        f"/api/v1/analyze/statistical/{upload_id}",
        json={
            "variables": ["var1", "var2"],
            "test_type": "chi_square",
            "confidence_level": 0.95
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert data["status"] == "completed"
    assert "results" in data

def test_generate_visualization():
    """Test visualization generation."""
    response = client.post(
        f"/api/v1/visualize/{TEST_ANALYSIS_ID}",
        json={
            "chart_type": "bar",
            "data": {
                "labels": ["A", "B"],
                "values": [1, 2]
            }
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["analysis_id"] == TEST_ANALYSIS_ID
    assert data["status"] == "completed"
    assert "results" in data

def test_export_analysis():
    """Test analysis export."""
    # Test CSV export
    response = client.get(f"/api/v1/export/{TEST_ANALYSIS_ID}/csv")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/csv"
    
    # Test Excel export
    response = client.get(f"/api/v1/export/{TEST_ANALYSIS_ID}/excel")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/excel"
    
    # Test JSON export
    response = client.get(f"/api/v1/export/{TEST_ANALYSIS_ID}/json")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

def test_invalid_analysis_id():
    """Test operations with invalid analysis ID."""
    # Test visualization with invalid ID
    response = client.post(
        "/api/v1/visualize/invalid_id",
        json={
            "chart_type": "bar",
            "data": {"labels": [], "values": []}
        }
    )
    assert response.status_code == 404
    
    # Test export with invalid ID
    response = client.get("/api/v1/export/invalid_id/csv")
    assert response.status_code == 404

def test_invalid_export_format():
    """Test export with invalid format."""
    response = client.get(f"/api/v1/export/{TEST_ANALYSIS_ID}/invalid")
    assert response.status_code == 400 