"""
Pytest configuration file with fixtures and settings for testing.
"""

import pytest
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"

@pytest.fixture(scope="session")
def test_data_dir():
    """Provide the test data directory path."""
    return TEST_DATA_DIR

@pytest.fixture(scope="session")
def sample_spss_file(test_data_dir):
    """Provide path to sample SPSS file."""
    return test_data_dir / "sample.sav"

@pytest.fixture(scope="session")
def mock_llm_response():
    """Provide mock LLM responses for testing."""
    return {
        "analysis": "This is a mock analysis response",
        "interpretation": "This is a mock interpretation",
        "suggestions": ["Suggestion 1", "Suggestion 2"]
    }

@pytest.fixture(scope="session")
def mock_crosstab_result():
    """Provide mock cross-tabulation results for testing."""
    return {
        "table": {
            "Male": {"High": 1, "Medium": 0, "Low": 1},
            "Female": {"High": 1, "Medium": 1, "Low": 0}
        },
        "statistics": {
            "chi_square": 1.5,
            "p_value": 0.22,
            "cramers_v": 0.3
        }
    }

@pytest.fixture(scope="session")
def mock_visualization_config():
    """Provide mock visualization configuration for testing."""
    return {
        "chart_type": "bar",
        "title": "Test Chart",
        "x_axis": "gender",
        "y_axis": "count",
        "theme": "light"
    }

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test."""
    # Set test environment variables
    os.environ["TESTING"] = "true"
    os.environ["DEEPSEEK_API_KEY"] = "test_key"
    
    yield
    
    # Cleanup after each test
    if os.path.exists("test_uploads"):
        for file in os.listdir("test_uploads"):
            os.remove(os.path.join("test_uploads", file))
        os.rmdir("test_uploads") 