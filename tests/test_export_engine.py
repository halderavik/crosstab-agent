"""
Tests for the ExportEngine module.

This module contains tests for verifying the functionality of:
- Data export in various formats
- Visualization export
- Error handling
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import os
from core.export_engine import ExportEngine
import matplotlib.pyplot as plt

@pytest.fixture
def export_dir(tmp_path):
    """Create a temporary export directory."""
    export_dir = tmp_path / "exports"
    export_dir.mkdir()
    return export_dir

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return pd.DataFrame({
        'gender': ['Male', 'Female', 'Male', 'Female'],
        'age': [25, 30, 35, 40],
        'satisfaction': ['High', 'Medium', 'Low', 'High']
    })

@pytest.fixture
def sample_visualization():
    """Create a sample visualization for testing."""
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4], [1, 4, 9, 16])
    return fig

def test_export_data_csv(export_dir, sample_data):
    """Test exporting data to CSV format."""
    engine = ExportEngine(export_dir)
    export_path = engine.export_data(sample_data, format='csv')
    
    assert export_path.exists()
    assert export_path.suffix == '.csv'
    assert export_path.parent == export_dir
    
    # Verify data integrity
    loaded_data = pd.read_csv(export_path)
    pd.testing.assert_frame_equal(loaded_data, sample_data)

def test_export_data_excel(export_dir, sample_data):
    """Test exporting data to Excel format."""
    engine = ExportEngine(export_dir)
    export_path = engine.export_data(sample_data, format='excel')
    
    assert export_path.exists()
    assert export_path.suffix == '.xlsx'
    assert export_path.parent == export_dir
    
    # Verify data integrity
    loaded_data = pd.read_excel(export_path)
    pd.testing.assert_frame_equal(loaded_data, sample_data)

def test_export_visualization_png(export_dir, sample_visualization):
    """Test exporting visualization to PNG format."""
    engine = ExportEngine(export_dir)
    export_path = engine.export_visualization(
        fig=sample_visualization,
        filename='test_plot',
        format='png'
    )
    
    assert export_path.exists()
    assert export_path.suffix == '.png'
    assert export_path.parent == export_dir
    assert export_path.stem == 'test_plot'

def test_export_visualization_svg(export_dir, sample_visualization):
    """Test exporting visualization to SVG format."""
    engine = ExportEngine(export_dir)
    export_path = engine.export_visualization(
        fig=sample_visualization,
        filename='test_plot',
        format='svg'
    )
    
    assert export_path.exists()
    assert export_path.suffix == '.svg'
    assert export_path.parent == export_dir
    assert export_path.stem == 'test_plot'

def test_export_data_invalid_format(export_dir, sample_data):
    """Test handling of invalid export format."""
    engine = ExportEngine(export_dir)
    with pytest.raises(ValueError, match="Unsupported export format"):
        engine.export_data(sample_data, format='invalid')

def test_export_visualization_invalid_format(export_dir, sample_visualization):
    """Test handling of invalid visualization format."""
    engine = ExportEngine(export_dir)
    with pytest.raises(ValueError, match="Unsupported visualization format"):
        engine.export_visualization(
            fig=sample_visualization,
            filename='test_plot',
            format='invalid'
        )

def test_export_data_empty(export_dir):
    """Test exporting empty data."""
    engine = ExportEngine(export_dir)
    empty_data = pd.DataFrame()
    export_path = engine.export_data(empty_data, format='csv')
    
    assert export_path.exists()
    loaded_data = pd.read_csv(export_path)
    assert loaded_data.empty

def test_export_data_large(export_dir):
    """Test exporting large datasets."""
    engine = ExportEngine(export_dir)
    large_data = pd.DataFrame(np.random.rand(10000, 10))
    export_path = engine.export_data(large_data, format='csv')
    
    assert export_path.exists()
    loaded_data = pd.read_csv(export_path)
    assert len(loaded_data) == 10000
    assert len(loaded_data.columns) == 10

def test_export_data_special_characters(export_dir):
    """Test exporting data with special characters."""
    engine = ExportEngine(export_dir)
    special_data = pd.DataFrame({
        'text': ['Hello, World!', 'Test & Test', '100%', 'Line\nBreak']
    })
    export_path = engine.export_data(special_data, format='csv')
    
    assert export_path.exists()
    loaded_data = pd.read_csv(export_path)
    pd.testing.assert_frame_equal(loaded_data, special_data)

def test_export_visualization_high_resolution(export_dir, sample_visualization):
    """Test exporting high-resolution visualizations."""
    engine = ExportEngine(export_dir)
    export_path = engine.export_visualization(
        fig=sample_visualization,
        filename='test_plot',
        format='png',
        dpi=300
    )
    
    assert export_path.exists()
    # Verify file size is larger than default DPI
    assert export_path.stat().st_size > 1000 