"""
Integration tests for the SPSS Analyzer application.

This module contains tests that verify the interaction between different components:
- Data processing and analysis
- File upload and analysis
- Chat and analysis integration
- Visualization and export integration
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
from core.data_processor import DataProcessor
from core.crosstab_engine import CrosstabEngine
from core.visualization_engine import VisualizationEngine
from core.export_engine import ExportEngine

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
        'satisfaction': ['High', 'Medium', 'Low', 'High'],
        'income': [50000, 60000, 70000, 80000]
    })

@pytest.fixture
def sample_spss_file(sample_data):
    """Create a sample SPSS file for testing."""
    with sav.SavWriter(str(SAMPLE_SPSS_FILE), sample_data.columns.tolist()) as writer:
        for _, row in sample_data.iterrows():
            writer.writerow(row.tolist())
    yield SAMPLE_SPSS_FILE
    if SAMPLE_SPSS_FILE.exists():
        SAMPLE_SPSS_FILE.unlink()

def test_full_analysis_workflow(sample_spss_file):
    """Test the complete workflow from file upload to analysis and export."""
    # 1. Upload file
    with open(sample_spss_file, "rb") as f:
        upload_response = client.post(
            "/api/v1/upload/",
            files={"file": ("sample.sav", f, "application/x-spss-sav")}
        )
    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    upload_id = upload_data["upload_id"]

    # 2. Check upload progress
    progress_response = client.get(f"/api/v1/upload/{upload_id}/progress")
    assert progress_response.status_code == 200
    progress_data = progress_response.json()
    assert progress_data["status"] == "completed"

    # 3. Perform cross-tabulation analysis
    analysis_response = client.post(
        f"/api/v1/analyze/crosstab/{upload_id}",
        json={
            "row_variable": "gender",
            "column_variable": "satisfaction",
            "filters": None,
            "include_percentages": True,
            "include_totals": True
        }
    )
    assert analysis_response.status_code == 200
    analysis_data = analysis_response.json()
    analysis_id = analysis_data["analysis_id"]

    # 4. Generate visualization
    viz_response = client.post(
        f"/api/v1/visualize/{analysis_id}",
        json={
            "chart_type": "bar",
            "data": {"x": "gender", "y": "count"},
            "options": {"title": "Gender Distribution"}
        }
    )
    assert viz_response.status_code == 200
    viz_data = viz_response.json()
    assert "results" in viz_data

    # 5. Export results
    export_response = client.get(f"/api/v1/export/{analysis_id}/csv")
    assert export_response.status_code == 200
    assert export_response.headers["content-type"].startswith("application/csv")

    # 6. Clean up
    delete_response = client.delete(f"/api/v1/upload/{upload_id}")
    assert delete_response.status_code == 200

def test_chat_analysis_integration(sample_spss_file):
    """Test integration between chat and analysis components."""
    # 1. Upload file
    with open(sample_spss_file, "rb") as f:
        upload_response = client.post(
            "/api/v1/upload/",
            files={"file": ("sample.sav", f, "application/x-spss-sav")}
        )
    assert upload_response.status_code == 200
    upload_id = upload_response.json()["upload_id"]

    # 2. Perform analysis
    analysis_response = client.post(
        f"/api/v1/analyze/crosstab/{upload_id}",
        json={
            "row_variable": "gender",
            "column_variable": "satisfaction",
            "filters": None,
            "include_percentages": True,
            "include_totals": True
        }
    )
    assert analysis_response.status_code == 200
    analysis_id = analysis_response.json()["analysis_id"]

    # 3. Chat about the analysis
    chat_response = client.post(
        "/api/v1/chat/completion",
        json={
            "messages": [
                {
                    "role": "user",
                    "content": "What is the relationship between gender and satisfaction?",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "analysis_id": analysis_id,
            "stream": False
        }
    )
    assert chat_response.status_code == 200
    chat_data = chat_response.json()
    assert "message" in chat_data
    assert "analysis_references" in chat_data
    assert analysis_id in chat_data["analysis_references"]

def test_data_processing_analysis_integration(sample_data):
    """Test integration between data processing and analysis components."""
    # 1. Initialize components
    processor = DataProcessor()
    processor.data = sample_data
    processor.metadata = {
        'missing_ranges': {
            'age': [{'value': 99}],
            'income': [{'lo': 98, 'hi': 99}]
        }
    }

    # 2. Clean data
    cleaned_data = processor.clean_data()
    assert isinstance(cleaned_data, pd.DataFrame)
    assert len(cleaned_data) == len(sample_data)

    # 3. Perform analysis
    crosstab_engine = CrosstabEngine(cleaned_data)
    result = crosstab_engine.create_crosstab(
        row_var='gender',
        col_var='satisfaction',
        include_percentages=True,
        include_totals=True
    )
    assert isinstance(result, dict)
    assert 'table' in result
    assert 'statistics' in result

def test_visualization_export_integration(sample_data):
    """Test integration between visualization and export components."""
    # 1. Initialize components
    visualization_engine = VisualizationEngine()
    export_engine = ExportEngine(TEST_DATA_DIR)

    # 2. Create visualization
    chart_data = {
        'x': 'gender',
        'y': 'count',
        'data': sample_data
    }
    visualization = visualization_engine.create_chart(
        chart_type='bar',
        data=chart_data,
        options={'title': 'Test Chart'}
    )
    assert isinstance(visualization, dict)
    assert 'chart' in visualization

    # 3. Export visualization
    export_path = export_engine.export_visualization(
        visualization=visualization,
        format='png'
    )
    assert export_path.exists()
    assert export_path.suffix == '.png'

def test_error_handling_integration(sample_spss_file):
    """Test error handling across multiple components."""
    # 1. Upload invalid file
    with open(sample_spss_file, "rb") as f:
        upload_response = client.post(
            "/api/v1/upload/",
            files={"file": ("invalid.txt", f, "text/plain")}
        )
    assert upload_response.status_code == 422

    # 2. Try analysis with invalid upload ID
    analysis_response = client.post(
        "/api/v1/analyze/crosstab/invalid_id",
        json={
            "row_variable": "gender",
            "column_variable": "satisfaction"
        }
    )
    assert analysis_response.status_code == 404

    # 3. Try visualization with invalid analysis ID
    viz_response = client.post(
        "/api/v1/visualize/invalid_id",
        json={
            "chart_type": "bar",
            "data": {"x": "gender", "y": "count"}
        }
    )
    assert viz_response.status_code == 404

    # 4. Try chat with invalid analysis ID
    chat_response = client.post(
        "/api/v1/chat/completion",
        json={
            "messages": [
                {
                    "role": "user",
                    "content": "Test message",
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "analysis_id": "invalid_id",
            "stream": False
        }
    )
    assert chat_response.status_code == 404

def test_concurrent_operations(sample_spss_file):
    """Test handling of concurrent operations."""
    # 1. Upload multiple files
    upload_ids = []
    for i in range(3):
        with open(sample_spss_file, "rb") as f:
            response = client.post(
                "/api/v1/upload/",
                files={"file": (f"sample_{i}.sav", f, "application/x-spss-sav")}
            )
        assert response.status_code == 200
        upload_ids.append(response.json()["upload_id"])

    # 2. Perform concurrent analyses
    analysis_ids = []
    for upload_id in upload_ids:
        response = client.post(
            f"/api/v1/analyze/crosstab/{upload_id}",
            json={
                "row_variable": "gender",
                "column_variable": "satisfaction"
            }
        )
        assert response.status_code == 200
        analysis_ids.append(response.json()["analysis_id"])

    # 3. Clean up
    for upload_id in upload_ids:
        response = client.delete(f"/api/v1/upload/{upload_id}")
        assert response.status_code == 200 