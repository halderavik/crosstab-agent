"""
Test suite for API endpoints.

This module contains tests for all FastAPI endpoints including:
- File upload
- Analysis
- Chat
- Visualization
"""

import pytest
from fastapi.testclient import TestClient
from main import app
import pandas as pd
import numpy as np
from pathlib import Path
import json
import os
import shutil
from datetime import datetime
import sav

# Initialize test client
client = TestClient(app)

# Test data paths
TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_DATA_DIR.mkdir(exist_ok=True)
SAMPLE_SPSS_FILE = TEST_DATA_DIR / "sample.sav"

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return pd.DataFrame({
        'gender': ['Male', 'Female', 'Male', 'Female'],
        'age': [25, 30, 35, 40],
        'satisfaction': ['High', 'Medium', 'Low', 'High']
    })

@pytest.fixture
def sample_spss_file(sample_data):
    """Create a sample SPSS file for testing."""
    # Create a temporary SPSS file
    with sav.SavWriter(str(SAMPLE_SPSS_FILE), sample_data.columns.tolist()) as writer:
        for _, row in sample_data.iterrows():
            writer.writerow(row.tolist())
    yield SAMPLE_SPSS_FILE
    # Cleanup
    if SAMPLE_SPSS_FILE.exists():
        SAMPLE_SPSS_FILE.unlink()

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "SPSS Analyzer API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "active"

def test_upload_file(sample_spss_file):
    """Test file upload endpoint."""
    with open(sample_spss_file, "rb") as f:
        response = client.post(
            "/api/v1/upload/",
            files={"file": ("sample.sav", f, "application/x-spss-sav")}
        )
    assert response.status_code == 200
    data = response.json()
    assert "filename" in data
    assert "file_size" in data
    assert "upload_id" in data
    assert "status" in data
    return data["upload_id"]

def test_upload_progress():
    """Test upload progress endpoint."""
    # First upload a file
    upload_id = test_upload_file()
    
    # Then check its progress
    response = client.get(f"/api/v1/upload/{upload_id}/progress")
    assert response.status_code == 200
    data = response.json()
    assert "upload_id" in data
    assert "progress" in data
    assert "status" in data

def test_delete_upload():
    """Test delete upload endpoint."""
    # First upload a file
    upload_id = test_upload_file()
    
    # Then delete it
    response = client.delete(f"/api/v1/upload/{upload_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Upload deleted successfully"

def test_crosstab_analysis(sample_spss_file):
    """Test cross-tabulation analysis endpoint."""
    # First upload a file
    upload_id = test_upload_file()
    
    # Then perform analysis
    response = client.post(
        f"/api/v1/analyze/crosstab/{upload_id}",
        json={
            "row_variable": "gender",
            "column_variable": "satisfaction",
            "filters": None,
            "include_percentages": True,
            "include_totals": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert "status" in data
    assert "results" in data
    return data["analysis_id"]

def test_statistical_analysis(sample_spss_file):
    """Test statistical analysis endpoint."""
    # First upload a file
    upload_id = test_upload_file()
    
    # Then perform analysis
    response = client.post(
        f"/api/v1/analyze/statistical/{upload_id}",
        json={
            "variables": ["age", "satisfaction"],
            "test_type": "chi-square",
            "confidence_level": 0.95
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert "status" in data
    assert "results" in data

def test_visualization(sample_spss_file):
    """Test visualization endpoint."""
    # First perform an analysis
    analysis_id = test_crosstab_analysis(sample_spss_file)
    
    # Then generate visualization
    response = client.post(
        f"/api/v1/visualize/{analysis_id}",
        json={
            "chart_type": "bar",
            "data": {"x": "gender", "y": "count"},
            "options": {"title": "Gender Distribution"}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert "status" in data
    assert "results" in data

def test_export_analysis(sample_spss_file):
    """Test export analysis endpoint."""
    # First perform an analysis
    analysis_id = test_crosstab_analysis(sample_spss_file)
    
    # Then export in different formats
    for format in ["csv", "excel", "json"]:
        response = client.get(f"/api/v1/export/{analysis_id}/{format}")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith(f"application/{format}")

def test_chat_completion():
    """Test chat completion endpoint."""
    response = client.post(
        "/api/v1/chat/completion",
        json={
            "messages": [
                {
                    "role": "user",
                    "content": "What is the distribution of gender in the data?",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "analysis_id": None,
            "stream": False
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "analysis_references" in data
    assert data["message"]["role"] == "assistant"

def test_get_chat_session():
    """Test get chat session endpoint."""
    # First create a chat session
    test_chat_completion()
    
    # Then get the session
    response = client.get("/api/v1/chat/session/1")
    assert response.status_code == 200
    data = response.json()
    assert "messages" in data
    assert "analysis_references" in data

def test_delete_chat_session():
    """Test delete chat session endpoint."""
    # First create a chat session
    test_chat_completion()
    
    # Then delete it
    response = client.delete("/api/v1/chat/session/1")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Chat session deleted successfully"

def test_invalid_file_upload():
    """Test invalid file upload."""
    # Try to upload a non-SPSS file
    response = client.post(
        "/api/v1/upload/",
        files={"file": ("test.txt", b"test content", "text/plain")}
    )
    assert response.status_code == 422
    assert "Only SPSS .sav files are supported" in response.json()["detail"]

def test_invalid_analysis_request():
    """Test invalid analysis request."""
    # First upload a file
    upload_id = test_upload_file()
    
    # Then try invalid analysis
    response = client.post(
        f"/api/v1/analyze/crosstab/{upload_id}",
        json={
            "row_variable": "nonexistent",
            "column_variable": "satisfaction"
        }
    )
    assert response.status_code == 500
    assert "Analysis failed" in response.json()["detail"]

def test_invalid_visualization_request():
    """Test invalid visualization request."""
    # First perform an analysis
    analysis_id = test_crosstab_analysis()
    
    # Then try invalid visualization
    response = client.post(
        f"/api/v1/visualize/{analysis_id}",
        json={
            "chart_type": "invalid",
            "data": {"x": "gender", "y": "count"}
        }
    )
    assert response.status_code == 500
    assert "Visualization generation failed" in response.json()["detail"]

def test_invalid_export_request():
    """Test invalid export request."""
    # First perform an analysis
    analysis_id = test_crosstab_analysis()
    
    # Then try invalid export format
    response = client.get(f"/api/v1/export/{analysis_id}/invalid")
    assert response.status_code == 500
    assert "Export failed" in response.json()["detail"]

def test_error_handling():
    """Test error handling in API endpoints."""
    # Test 404 for non-existent endpoint
    response = client.get("/api/nonexistent")
    assert response.status_code == 404
    
    # Test 422 for invalid request body
    response = client.post(
        "/api/analysis/crosstab",
        json={"invalid": "data"}
    )
    assert response.status_code == 422

def test_rate_limiting():
    """Test rate limiting implementation."""
    # Make multiple rapid requests
    for _ in range(10):
        response = client.post(
            "/api/chat",
            json={
                "message": "Test message",
                "file_id": "test_file"
            }
        )
    
    # Next request should be rate limited
    response = client.post(
        "/api/chat",
        json={
            "message": "Test message",
            "file_id": "test_file"
        }
    )
    assert response.status_code == 429 