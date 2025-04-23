"""
Backend integration tests for the SPSS Analyzer application.

This module contains tests that verify the interaction between core backend components:
- Data processing pipeline
- Analysis engine
- Storage and caching
- Error handling and recovery
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import json
import os
import shutil
from datetime import datetime
from core.data_processor import DataProcessor
from core.crosstab_engine import CrosstabEngine
from core.visualization_engine import VisualizationEngine
from core.export_engine import ExportEngine
from core.storage import StorageManager
from core.cache import CacheManager
from core.crosstab_result import CrosstabResult, CrosstabStatistics

# Test data paths
TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_DATA_DIR.mkdir(exist_ok=True)
SAMPLE_DATA_FILE = TEST_DATA_DIR / "sample.csv"

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
def sample_data_file(sample_data):
    """Create a sample data file for testing."""
    sample_data.to_csv(SAMPLE_DATA_FILE, index=False)
    yield SAMPLE_DATA_FILE
    if SAMPLE_DATA_FILE.exists():
        SAMPLE_DATA_FILE.unlink()

@pytest.fixture
def storage_manager():
    """Create a storage manager for testing."""
    storage = StorageManager(TEST_DATA_DIR)
    yield storage
    # Cleanup
    shutil.rmtree(TEST_DATA_DIR / "uploads", ignore_errors=True)
    shutil.rmtree(TEST_DATA_DIR / "exports", ignore_errors=True)

@pytest.fixture
def cache_manager():
    """Create a cache manager for testing."""
    cache = CacheManager()
    yield cache
    cache.clear()

def test_data_processing_pipeline(sample_data, storage_manager):
    """Test the data processing pipeline."""
    # 1. Initialize components
    data_processor = DataProcessor()
    data_processor.data = sample_data
    data_processor.metadata = {
        'missing_ranges': {
            'age': [{'value': 99}],
            'income': [{'lo': 98, 'hi': 99}]
        }
    }
    export_engine = ExportEngine(TEST_DATA_DIR)

    # 2. Process data
    processed_data = data_processor.clean_data()
    assert isinstance(processed_data, pd.DataFrame)
    assert not processed_data.empty

    # 3. Export processed data
    export_path = export_engine.export_data(
        data=processed_data,
        format='csv'
    )
    assert export_path.exists()
    assert export_path.suffix == '.csv'

    # 4. Store processing metadata
    processing_metadata = {
        'original_columns': list(sample_data.columns),
        'processed_columns': list(processed_data.columns),
        'export_path': str(export_path)
    }
    storage_manager.store_metadata(export_path.stem, processing_metadata)
    assert storage_manager.metadata_exists(export_path.stem)

def test_analysis_engine_integration(sample_data, cache_manager):
    """Test integration between analysis engine and caching."""
    # 1. Initialize components
    crosstab_engine = CrosstabEngine(sample_data)
    cache_key = f"analysis_{datetime.now().isoformat()}"

    # 2. Perform analysis
    result = crosstab_engine.create_crosstab(
        row_var='gender',
        col_var='satisfaction',
        include_percentages=True,
        include_statistics=True
    )
    assert isinstance(result, CrosstabResult)
    assert hasattr(result, 'table')
    assert hasattr(result, 'row_percentages')
    assert hasattr(result, 'column_percentages')
    assert hasattr(result, 'total_percentages')
    assert hasattr(result, 'statistics')

    # 3. Cache the result
    cache_manager.set(cache_key, result)
    cached_result = cache_manager.get(cache_key)
    assert cached_result is not None
    assert isinstance(cached_result, CrosstabResult)

def test_visualization_pipeline(sample_data, storage_manager):
    """Test the visualization pipeline."""
    # 1. Initialize components
    visualization_engine = VisualizationEngine()
    export_engine = ExportEngine(TEST_DATA_DIR)

    # 2. Create visualization
    fig = visualization_engine.create_bar_chart(
        data=sample_data,
        x='gender',
        y='satisfaction',
        chart_title='Gender vs Satisfaction'
    )
    assert fig is not None

    # 3. Export visualization
    export_path = export_engine.export_visualization(
        fig=fig,
        filename='test_visualization',
        format='png'
    )
    assert export_path.exists()
    assert export_path.suffix == '.png'

    # 4. Store visualization metadata
    visualization_metadata = {
        'type': 'bar_chart',
        'variables': ['gender', 'satisfaction'],
        'export_path': str(export_path)
    }
    storage_manager.store_metadata(export_path.stem, visualization_metadata)
    assert storage_manager.metadata_exists(export_path.stem)

def test_error_recovery(sample_data):
    """Test error handling and recovery in the backend pipeline."""
    # 1. Initialize components
    processor = DataProcessor()
    processor.data = sample_data
    processor.metadata = {
        'missing_ranges': {
            'age': [{'value': 99}],
            'income': [{'lo': 98, 'hi': 99}]
        }
    }

    # 2. Simulate processing error
    try:
        # Force an error by passing invalid data
        processor.data = None
        processor.clean_data()
    except Exception as e:
        assert str(e)  # Error should be caught and logged

    # 3. Recover and retry with valid data
    processor.data = sample_data
    cleaned_data = processor.clean_data()
    assert isinstance(cleaned_data, pd.DataFrame)
    assert len(cleaned_data) == len(sample_data)

def test_data_transformation_pipeline(sample_data):
    """Test the data transformation pipeline."""
    # 1. Initialize components
    processor = DataProcessor()
    processor.data = sample_data
    processor.metadata = {
        'missing_ranges': {
            'age': [{'value': 99}],
            'income': [{'lo': 98, 'hi': 99}]
        }
    }
    crosstab_engine = CrosstabEngine(sample_data)

    # 2. Transform data
    transformed_data = processor.transform_data(
        operations=[
            {'type': 'filter', 'column': 'age', 'operator': '>', 'value': 30},
            {'type': 'groupby', 'column': 'gender', 'agg': 'mean', 'numeric_only': True}
        ]
    )
    assert isinstance(transformed_data, pd.DataFrame)
    assert len(transformed_data) <= len(sample_data)
    assert 'age' in transformed_data.columns
    assert 'income' in transformed_data.columns

    # 3. Use transformed data in analysis
    crosstab_engine.data = sample_data  # Use original data for crosstab
    result = crosstab_engine.create_crosstab(
        row_var='gender',
        col_var='satisfaction'
    )
    assert isinstance(result, CrosstabResult)
    assert hasattr(result, 'table')

def test_concurrent_processing(sample_data, storage_manager):
    """Test concurrent data processing and storage operations."""
    import concurrent.futures

    def process_and_store(data_chunk, chunk_id):
        processor = DataProcessor()
        processor.data = data_chunk
        cleaned_data = processor.clean_data()
        return storage_manager.store_data(cleaned_data, f"chunk_{chunk_id}.csv")

    # 1. Split data into chunks
    chunks = np.array_split(sample_data, 3)
    
    # 2. Process chunks concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(process_and_store, chunk, i)
            for i, chunk in enumerate(chunks)
        ]
        file_ids = [f.result() for f in futures]

    # 3. Verify all chunks were processed and stored
    assert len(file_ids) == 3
    for file_id in file_ids:
        assert storage_manager.file_exists(file_id)
        data = storage_manager.get_data(file_id)
        assert isinstance(data, pd.DataFrame)
        assert not data.empty

def test_memory_management(sample_data):
    """Test memory management during large data processing."""
    # 1. Create large dataset
    large_data = pd.concat([sample_data] * 1000)
    assert len(large_data) == len(sample_data) * 1000

    # 2. Process in chunks
    processor = DataProcessor()
    chunk_size = 1000
    processed_chunks = []

    for i in range(0, len(large_data), chunk_size):
        chunk = large_data.iloc[i:i + chunk_size]
        processor.data = chunk
        processed_chunk = processor.clean_data()
        processed_chunks.append(processed_chunk)
        # Force garbage collection
        del chunk
        del processed_chunk

    # 3. Combine results
    final_data = pd.concat(processed_chunks)
    assert len(final_data) == len(large_data)
    assert list(final_data.columns) == list(sample_data.columns)

def test_crosstab_edge_cases(sample_data):
    """Test edge cases and error handling in CrosstabEngine."""
    # 1. Test empty data
    empty_df = pd.DataFrame()
    with pytest.raises(ValueError, match="DataFrame is empty"):
        CrosstabEngine(empty_df)

    # 2. Test missing variables
    engine = CrosstabEngine(sample_data)
    with pytest.raises(ValueError, match="not found in data"):
        engine.create_crosstab('nonexistent', 'gender')

    # 3. Test single value in column
    single_value_df = pd.DataFrame({
        'gender': ['Male'] * 4,
        'satisfaction': ['High', 'Medium', 'Low', 'High']
    })
    engine = CrosstabEngine(single_value_df)
    result = engine.create_crosstab('gender', 'satisfaction')
    assert isinstance(result, CrosstabResult)
    assert result.statistics.chi_square == 0  # Chi-square should be 0 for single value

    # 4. Test all null values
    null_df = pd.DataFrame({
        'gender': [None] * 4,
        'satisfaction': ['High', 'Medium', 'Low', 'High']
    })
    engine = CrosstabEngine(null_df)
    with pytest.raises(ValueError, match="contains all null"):
        engine.create_crosstab('gender', 'satisfaction')

def test_crosstab_result_properties(sample_data):
    """Test properties of CrosstabResult objects."""
    # 1. Create a crosstab
    engine = CrosstabEngine(sample_data)
    result = engine.create_crosstab('gender', 'satisfaction')

    # 2. Verify table structure
    assert isinstance(result.table, pd.DataFrame)
    assert result.table.index.name == 'gender'
    assert result.table.columns.name == 'satisfaction'
    assert 'All' in result.table.index
    assert 'All' in result.table.columns

    # 3. Verify percentage calculations
    assert isinstance(result.row_percentages, pd.DataFrame)
    assert isinstance(result.column_percentages, pd.DataFrame)
    assert isinstance(result.total_percentages, pd.DataFrame)
    
    # Check that percentages sum to 100%
    # Convert to float and exclude 'All' row/column for percentage checks
    row_sums = result.row_percentages.iloc[:, :-1].astype(float).sum(axis=1)
    col_sums = result.column_percentages.iloc[:-1, :].astype(float).sum(axis=0)
    total_sum = result.total_percentages.iloc[:-1, :-1].astype(float).sum().sum()
    
    assert np.allclose(row_sums, 100)
    assert np.allclose(col_sums, 100)
    assert np.isclose(total_sum, 100)

    # 4. Verify statistics
    assert isinstance(result.statistics, CrosstabStatistics)
    assert isinstance(result.statistics.chi_square, float)
    assert isinstance(result.statistics.p_value, float)
    assert isinstance(result.statistics.degrees_of_freedom, float)
    assert isinstance(result.statistics.cramers_v, float)
    
    # Check value ranges
    assert result.statistics.chi_square >= 0
    assert 0 <= result.statistics.p_value <= 1
    assert result.statistics.degrees_of_freedom > 0
    assert 0 <= result.statistics.cramers_v <= 1 