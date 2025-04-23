"""
Test suite for the data processor module.
"""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil
from core.data_processor import DataProcessor, VariableMetadata

@pytest.fixture
def sample_data():
    """Create a sample data structure for testing."""
    data = {
        'Q1': [1, 2, 3, 4, 5, np.nan],
        'Q2': ['A', 'B', 'A', 'B', 'A', 'B'],
        'Q3': [1.5, 2.5, 3.5, 4.5, 5.5, np.nan]
    }
    df = pd.DataFrame(data)
    
    metadata = {
        'variable_value_labels': {
            'Q1': {1: 'Strongly Disagree', 2: 'Disagree', 3: 'Neutral', 4: 'Agree', 5: 'Strongly Agree'},
            'Q2': {'A': 'Option A', 'B': 'Option B'}
        },
        'missing_ranges': {
            'Q1': [{'value': 99}],
            'Q3': [{'lo': 98, 'hi': 99}]
        }
    }
    
    return df, metadata

@pytest.fixture
def temp_data_file(sample_data):
    """Create a temporary file for testing."""
    df, _ = sample_data
    temp_dir = tempfile.mkdtemp()
    file_path = Path(temp_dir) / 'test.csv'
    df.to_csv(file_path, index=False)
    yield file_path
    shutil.rmtree(temp_dir)

def test_data_processor_initialization():
    """Test DataProcessor initialization."""
    processor = DataProcessor()
    assert processor.data is None
    assert processor.metadata is None

def test_load_data_file(temp_data_file, sample_data):
    """Test loading a data file."""
    processor = DataProcessor()
    df, metadata = processor.load_data_file(temp_data_file)
    
    assert isinstance(df, pd.DataFrame)
    assert isinstance(metadata, dict)
    assert len(df) == len(sample_data[0])
    assert set(df.columns) == set(sample_data[0].columns)

def test_get_variable_info(sample_data):
    """Test getting variable info."""
    processor = DataProcessor()
    processor.data = sample_data[0]
    processor.metadata = sample_data[1]
    
    info = processor.get_variable_info('Q1')
    assert info.name == 'Q1'
    assert info.type == 'float64'  # Due to NaN value
    assert info.value_labels == sample_data[1]['variable_value_labels']['Q1']

def test_clean_data(sample_data):
    """Test data cleaning."""
    processor = DataProcessor()
    processor.data = sample_data[0]
    processor.metadata = sample_data[1]
    
    cleaned_df = processor.clean_data(['Q1', 'Q2'])
    
    assert set(cleaned_df.columns) == {'Q1', 'Q2'}
    assert cleaned_df['Q1'].isna().sum() == 1
    assert not cleaned_df['Q2'].isna().any()

def test_get_variable_summary(sample_data):
    """Test getting variable summaries."""
    processor = DataProcessor()
    processor.data = sample_data[0]
    processor.metadata = sample_data[1]
    
    # Test numeric variable
    q1_summary = processor.get_variable_summary('Q1')
    assert q1_summary['name'] == 'Q1'
    assert q1_summary['type'] == 'float64'
    assert 'mean' in q1_summary
    assert 'std' in q1_summary
    
    # Test categorical variable
    q2_summary = processor.get_variable_summary('Q2')
    assert q2_summary['name'] == 'Q2'
    assert q2_summary['type'] == 'object'
    assert 'frequencies' in q2_summary
    assert 'mode' in q2_summary

def test_validate_data(sample_data):
    """Test data validation."""
    processor = DataProcessor()
    processor.data = sample_data[0]
    processor.metadata = sample_data[1]
    
    validation_results = processor.validate_data()
    
    assert 'Q1' in validation_results
    assert any("missing values" in issue for issue in validation_results['Q1'])

def test_invalid_file_path():
    """Test handling invalid file path."""
    processor = DataProcessor()
    with pytest.raises(FileNotFoundError):
        processor.load_data_file('nonexistent.csv')

def test_missing_data_validation():
    """Test validation with missing data."""
    processor = DataProcessor()
    validation_results = processor.validate_data()
    assert validation_results == {}

def test_missing_data_cleaning():
    """Test cleaning with missing data."""
    processor = DataProcessor()
    with pytest.raises(ValueError):
        processor.clean_data()

def test_invalid_variable_summary():
    """Test getting summary for invalid variable."""
    processor = DataProcessor()
    processor.data = pd.DataFrame({'A': [1, 2, 3]})
    processor.metadata = {}
    
    with pytest.raises(KeyError):
        processor.get_variable_summary('nonexistent_variable')

def test_unsupported_file_format():
    """Test loading file with unsupported format."""
    processor = DataProcessor()
    with tempfile.NamedTemporaryFile(suffix='.txt') as temp_file:
        with pytest.raises(ValueError) as exc_info:
            processor.load_data_file(temp_file.name)
        assert "Unsupported file format" in str(exc_info.value)

def test_variable_metadata_optional_fields():
    """Test VariableMetadata with optional fields."""
    metadata = VariableMetadata(
        name='test',
        type='numeric'
    )
    assert metadata.label is None
    assert metadata.value_labels is None
    assert metadata.missing_values is None
    assert metadata.measure is None

def test_clean_data_with_missing_values(sample_data):
    """Test cleaning data with missing value ranges."""
    processor = DataProcessor()
    processor.data = pd.DataFrame({
        'test': [1, 2, 99, 4, 5]
    })
    processor.metadata = {
        'missing_ranges': {
            'test': [{'value': 99}]
        }
    }
    
    cleaned_df = processor.clean_data()
    assert cleaned_df['test'].isna().sum() == 1
    assert pd.isna(cleaned_df['test'].iloc[2])

def test_get_variable_summary_empty_series():
    """Test getting summary for empty categorical series."""
    processor = DataProcessor()
    processor.data = pd.DataFrame({
        'empty_cat': pd.Series(dtype='object')
    })
    processor.metadata = {}
    
    summary = processor.get_variable_summary('empty_cat')
    assert summary['mode'] is None
    assert summary['frequencies'] == {}

def test_clean_data_with_range_missing_values():
    """Test cleaning data with range-based missing values."""
    processor = DataProcessor()
    processor.data = pd.DataFrame({
        'test': [1, 2, 98, 99, 100, 4, 5]
    })
    processor.metadata = {
        'missing_ranges': {
            'test': [{'lo': 98, 'hi': 99}]
        }
    }
    
    cleaned_df = processor.clean_data()
    assert cleaned_df['test'].isna().sum() == 2
    assert pd.isna(cleaned_df['test'].iloc[2])
    assert pd.isna(cleaned_df['test'].iloc[3])

def test_clean_data_with_mixed_missing_values():
    """Test cleaning data with both single value and range missing values."""
    processor = DataProcessor()
    processor.data = pd.DataFrame({
        'test': [1, 2, 98, 99, 100, -999, 5]
    })
    processor.metadata = {
        'missing_ranges': {
            'test': [
                {'lo': 98, 'hi': 99},
                {'value': -999}
            ]
        }
    }
    
    cleaned_df = processor.clean_data()
    assert cleaned_df['test'].isna().sum() == 3
    assert pd.isna(cleaned_df['test'].iloc[2])  # 98
    assert pd.isna(cleaned_df['test'].iloc[3])  # 99
    assert pd.isna(cleaned_df['test'].iloc[5])  # -999

def test_clean_data_with_empty_series_and_range():
    """Test cleaning data with empty series and missing range."""
    processor = DataProcessor()
    # Create a DataFrame with an empty series
    df = pd.DataFrame({'empty_col': [], 'normal_col': [1, 2, 3]})
    processor.data = df
    processor.metadata = {
        'missing_ranges': {
            'empty_col': [{'lo': 98, 'hi': 99}],
            'normal_col': [{'value': 2}]
        }
    }
    
    cleaned_df = processor.clean_data()
    assert cleaned_df is not None
    assert 'empty_col' in cleaned_df.columns
    assert 'normal_col' in cleaned_df.columns
    assert cleaned_df['empty_col'].empty
    assert cleaned_df['normal_col'].isna().sum() == 1  # Value 2 should be NA 

def test_clean_data_empty_series():
    """Test cleaning data with empty series."""
    processor = DataProcessor()
    processor.data = pd.DataFrame({
        'empty_numeric': pd.Series(dtype='float64'),
        'empty_categorical': pd.Series(dtype='object')
    })
    processor.metadata = {
        'missing_ranges': {
            'empty_numeric': [{'value': 99}],
            'empty_categorical': []
        }
    }
    
    cleaned_df = processor.clean_data()
    assert len(cleaned_df) == 0
    assert 'empty_numeric' in cleaned_df.columns
    assert 'empty_categorical' in cleaned_df.columns
    assert cleaned_df['empty_numeric'].dtype == 'float64'
    assert cleaned_df['empty_categorical'].dtype == 'object' 