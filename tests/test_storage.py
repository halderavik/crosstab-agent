"""
Tests for the storage manager module.

This module contains tests for verifying the functionality of:
- Data storage and retrieval
- File operations
- Error handling
- Data integrity
"""

import os
import json
import pytest
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import tempfile
import shutil
import threading
import time
from core.storage import StorageManager
import plotly.graph_objects as go

@pytest.fixture
def storage_manager(tmp_path):
    """Create a temporary StorageManager instance."""
    return StorageManager(tmp_path)

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35]
    })

def test_save_load_data(storage_manager, sample_data):
    """Test saving and loading data."""
    file_id = storage_manager.save_data("test.csv", sample_data)
    loaded_data = storage_manager.load_data(file_id)
    pd.testing.assert_frame_equal(sample_data, loaded_data)

def test_save_load_visualization(storage_manager):
    """Test saving and loading visualizations."""
    fig = plt.figure()
    plt.plot([1, 2, 3], [1, 2, 3])
    viz_id = "test_plot"
    file_path = storage_manager.save_visualization(viz_id, fig)
    loaded_data = storage_manager.load_visualization(viz_id)
    assert isinstance(loaded_data, bytes)
    plt.close(fig)

def test_file_not_found(storage_manager):
    """Test handling of non-existent files."""
    with pytest.raises(FileNotFoundError):
        storage_manager.load_data("nonexistent")

def test_file_exists(storage_manager, sample_data):
    """Test file existence check."""
    file_id = storage_manager.save_data("test.csv", sample_data)
    assert storage_manager.file_exists(file_id)
    assert not storage_manager.file_exists("nonexistent")

def test_delete_file(storage_manager, sample_data):
    """Test file deletion."""
    file_id = storage_manager.save_data("test.csv", sample_data)
    storage_manager.delete_file(file_id)
    assert not storage_manager.file_exists(file_id)

def test_list_files(storage_manager, sample_data):
    """Test listing files."""
    file_id = storage_manager.save_data("test.csv", sample_data)
    files = storage_manager.list_files()
    assert any(file_id in f for f in files)

def test_metadata(storage_manager):
    """Test metadata operations."""
    metadata = {"description": "Test data", "timestamp": "2024-03-14"}
    file_id = storage_manager.save_data("test.json", {"data": [1, 2, 3]})
    storage_manager.store_metadata(file_id, metadata)
    assert storage_manager.metadata_exists(file_id)
    loaded_metadata = storage_manager.get_metadata(file_id)
    assert loaded_metadata == metadata

def test_storage_cleanup(storage_manager, sample_data):
    """Test storage cleanup."""
    file_id = storage_manager.save_data("test.csv", sample_data)
    storage_manager.cleanup()
    assert not storage_manager.file_exists(file_id)
    assert storage_manager.storage_dir.exists()
    assert storage_manager.uploads_dir.exists()
    assert storage_manager.exports_dir.exists()
    assert storage_manager.metadata_dir.exists()
    assert storage_manager.visualizations_dir.exists()

def test_file_permissions(storage_manager, sample_data):
    """Test file permissions after save."""
    file_id = storage_manager.save_data("test.csv", sample_data)
    file_path = storage_manager.uploads_dir / f"{file_id}.csv"
    assert os.access(file_path, os.R_OK)  # Check read permission
    assert os.access(file_path, os.W_OK)  # Check write permission

def test_concurrent_access(storage_manager):
    """Test concurrent access to storage manager."""
    def save_data(thread_id):
        data = {"thread": thread_id, "timestamp": time.time()}
        try:
            file_id = storage_manager.save_data(f"test_{thread_id}.json", data)
            # Verify the data was saved correctly
            loaded_data = storage_manager.load_data(file_id)
            assert loaded_data["thread"] == thread_id
        except Exception as e:
            pytest.fail(f"Thread {thread_id} failed: {str(e)}")

    threads = []
    num_threads = 50
    for i in range(num_threads):
        thread = threading.Thread(target=save_data, args=(i,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Verify that all files were created and are unique
    files = storage_manager.list_files()
    assert len(files) == num_threads

    # Verify that each file has unique content
    loaded_data = []
    for file_id in [f.split('.')[0] for f in files]:
        data = storage_manager.load_data(file_id)
        loaded_data.append(data["thread"])
    
    # Check that we have all thread IDs represented
    assert sorted(loaded_data) == list(range(num_threads))

def test_invalid_json(storage_manager):
    """Test handling of invalid JSON data."""
    # Create an invalid JSON file
    file_id = "invalid_json"
    file_path = storage_manager.uploads_dir / f"{file_id}.json"
    with open(file_path, 'w') as f:
        f.write("invalid json data")
    
    with pytest.raises(ValueError, match="Invalid JSON"):
        storage_manager.load_data(file_id)

def test_save_load_large_data(storage_manager):
    """Test saving and loading large data."""
    # Create large data
    large_data = {'data': [i for i in range(1000000)]}

    # Save and load
    file_id = storage_manager.save_data('large_data', large_data)
    loaded_data = storage_manager.load_data(file_id)
    assert loaded_data == large_data

def test_save_load_multiple_formats(storage_manager):
    """Test saving and loading different data formats."""
    test_cases = [
        ('string', 'test string'),
        ('number', 42),
        ('list', [1, 2, 3]),
        ('dict', {'key': 'value'}),
        ('none', None),
        ('bool', True)
    ]

    for name, value in test_cases:
        file_id = storage_manager.save_data(name, value)
        loaded_value = storage_manager.load_data(file_id)
        assert loaded_value == value

def test_storage_directory_creation(storage_manager):
    """Test storage directory creation."""
    assert storage_manager.uploads_dir.exists()
    assert storage_manager.exports_dir.exists()
    assert storage_manager.metadata_dir.exists()
    assert storage_manager.visualizations_dir.exists()

def test_visualization_formats(storage_manager):
    """Test saving visualizations in different formats."""
    import matplotlib.pyplot as plt

    # Create a simple plot
    plt.plot([1, 2, 3], [4, 5, 6])
    fig = plt.gcf()

    # Test different formats
    formats = ['png', 'jpg', 'svg']  # Removed 'pdf' as it's not supported
    for fmt in formats:
        file_id = storage_manager.save_visualization(f'test_plot_{fmt}', fig, format=fmt)
        file_path = storage_manager.visualizations_dir / f'test_plot_{fmt}.{fmt}'
        assert os.path.exists(file_path)
    
    plt.close(fig)

def test_save_load_visualization_matplotlib(storage_manager, tmp_path):
    """Test saving and loading matplotlib visualizations."""
    # Create a simple matplotlib figure
    fig = plt.figure()
    plt.plot([1, 2, 3], [1, 2, 3])
    
    # Test PNG format
    viz_path = storage_manager.save_visualization("test_plot", fig, format='png')
    assert Path(viz_path).exists()
    loaded_data = storage_manager.load_visualization("test_plot", format='png')
    assert isinstance(loaded_data, bytes)
    
    # Test SVG format
    viz_path = storage_manager.save_visualization("test_plot_svg", fig, format='svg')
    assert Path(viz_path).exists()
    loaded_data = storage_manager.load_visualization("test_plot_svg", format='svg')
    assert isinstance(loaded_data, str)
    assert loaded_data.startswith('<?xml')
    
    plt.close(fig)

@pytest.mark.skip(reason="TODO: Investigate kaleido initialization issues on Windows")
def test_save_load_visualization_plotly(storage_manager, tmp_path):
    """Test saving and loading plotly visualizations."""
    # Create a simple plotly figure
    fig = go.Figure(data=go.Scatter(x=[1, 2, 3], y=[1, 2, 3]))
    
    # Test HTML format first (this should work without kaleido)
    viz_path = storage_manager.save_visualization("test_plot_html", fig, format='html')
    assert Path(viz_path).exists()
    loaded_data = storage_manager.load_visualization("test_plot_html", format='html')
    assert isinstance(loaded_data, str)
    assert '<html>' in loaded_data
    
    # Test PNG format - Skip if kaleido is not available
    try:
        import kaleido
        import plotly.io as pio
        if not hasattr(pio, 'kaleido') or not hasattr(pio.kaleido, 'scope'):
            pytest.skip("Kaleido is not properly initialized")
            
        # Try a simple PNG export
        viz_path = storage_manager.save_visualization("test_plot_png", fig, format='png')
        assert Path(viz_path).exists()
        loaded_data = storage_manager.load_visualization("test_plot_png", format='png')
        assert isinstance(loaded_data, bytes)
            
    except (ImportError, ValueError, AttributeError) as e:
        pytest.skip(f"Skipping PNG test due to missing or misconfigured kaleido: {str(e)}")

def test_visualization_errors(storage_manager):
    """Test error handling in visualization methods."""
    # Test invalid format
    fig = plt.figure()
    with pytest.raises(ValueError, match="Unsupported format"):
        storage_manager.save_visualization("test_plot", fig, format='invalid')
    plt.close(fig)
    
    # Test loading non-existent visualization
    with pytest.raises(FileNotFoundError):
        storage_manager.load_visualization("nonexistent", format='png')
    
    # Test invalid figure type
    class InvalidFigure:
        pass
    
    with pytest.raises(ValueError, match="Figure must be either matplotlib.Figure or plotly.graph_objects.Figure"):
        storage_manager.save_visualization("test_plot", InvalidFigure(), format='png') 