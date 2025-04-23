"""
Test suite for the cross-tabulation engine module.
"""
import pytest
import pandas as pd
import numpy as np
from core.crosstab_engine import (
    CrosstabGenerator,
    BannerTableGenerator,
    CrosstabResult,
    CrosstabEngine,
    StatisticType,
    StatisticalResult
)

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    data = {
        'Q1': [1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
        'Q2': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B'],
        'Q3': [1, 1, 2, 2, 1, 1, 2, 2, 1, 1],
        'Group': ['G1', 'G1', 'G1', 'G1', 'G1', 'G2', 'G2', 'G2', 'G2', 'G2'],
        'gender': ['M', 'M', 'F', 'F', 'M', 'F', 'M', 'F'],
        'age_group': ['18-24', '25-34', '18-24', '35-44', '25-34', '18-24', '35-44', '25-34'],
        'income': [30000, 45000, 35000, 60000, 50000, 40000, 55000, 48000],
        'satisfaction': [3, 4, 5, 2, 4, 3, 2, 5]
    }
    df = pd.DataFrame(data)
    
    metadata = {
        'variable_value_labels': {
            'Q1': {1: 'Strongly Disagree', 2: 'Disagree', 3: 'Neutral', 4: 'Agree', 5: 'Strongly Agree'},
            'Q2': {'A': 'Option A', 'B': 'Option B'},
            'Q3': {1: 'Low', 2: 'High'},
            'Group': {'G1': 'Group 1', 'G2': 'Group 2'}
        }
    }
    
    return df, metadata

def test_crosstab_generator_initialization(sample_data):
    """Test CrosstabGenerator initialization."""
    df, metadata = sample_data
    generator = CrosstabGenerator(df, metadata)
    assert generator.dataframe.equals(df)
    assert generator.metadata == metadata

def test_generate_crosstab(sample_data):
    """Test basic cross-tabulation generation."""
    df, metadata = sample_data
    generator = CrosstabGenerator(df, metadata)
    
    result = generator.generate_crosstab('Q1', 'Q2')
    
    assert isinstance(result, CrosstabResult)
    assert result.row_variable == 'Q1'
    assert result.column_variable == 'Q2'
    assert result.normalize is None
    assert 'chi_square' in result.statistics
    assert 'p_value' in result.statistics
    assert 'degrees_of_freedom' in result.statistics
    assert 'expected_frequencies' in result.statistics

def test_generate_crosstab_normalized(sample_data):
    """Test normalized cross-tabulation generation."""
    df, metadata = sample_data
    generator = CrosstabGenerator(df, metadata)
    
    result = generator.generate_crosstab('Q1', 'Q2', normalize='index')
    
    assert isinstance(result, CrosstabResult)
    assert result.normalize == 'index'
    assert np.allclose(result.table.sum(axis=1), 1.0)

def test_generate_layered_crosstab(sample_data):
    """Test layered cross-tabulation generation."""
    df, metadata = sample_data
    generator = CrosstabGenerator(df, metadata)
    
    results = generator.generate_layered_crosstab('Q1', 'Q2', ['Group'])
    
    assert isinstance(results, dict)
    assert len(results) == 2  # One for each group
    assert all(isinstance(result, CrosstabResult) for result in results.values())

def test_sort_crosstab(sample_data):
    """Test sorting cross-tabulation."""
    df, metadata = sample_data
    generator = CrosstabGenerator(df, metadata)
    
    result = generator.generate_crosstab('Q1', 'Q2')
    sorted_table = generator.sort_crosstab(result.table, sort_by='index', ascending=False)
    
    assert isinstance(sorted_table, pd.DataFrame)
    assert list(sorted_table.index) == sorted(result.table.index, reverse=True)

def test_merge_categories(sample_data):
    """Test merging categories in cross-tabulation."""
    df, metadata = sample_data
    generator = CrosstabGenerator(df, metadata)
    
    result = generator.generate_crosstab('Q1', 'Q2')
    merged_table = generator.merge_categories(
        result.table,
        {'Q1': [1, 2]},
        'Disagree'
    )
    
    assert isinstance(merged_table, pd.DataFrame)
    assert 'Disagree' in merged_table.index

def test_banner_table_generator_initialization(sample_data):
    """Test BannerTableGenerator initialization."""
    df, metadata = sample_data
    generator = BannerTableGenerator(df, metadata)
    assert generator.dataframe.equals(df)
    assert generator.metadata == metadata

def test_create_banner(sample_data):
    """Test creating a banner."""
    df, metadata = sample_data
    generator = BannerTableGenerator(df, metadata)
    
    banner = generator.create_banner(['Q2', 'Q3'])
    
    assert isinstance(banner, pd.DataFrame)
    assert len(banner.columns) == 4  # 2 variables × 2 values each
    assert all(col.startswith(('Q2_', 'Q3_')) for col in banner.columns)

def test_create_nested_banner(sample_data):
    """Test creating a nested banner."""
    df, metadata = sample_data
    generator = BannerTableGenerator(df, metadata)
    
    variable_groups = {
        'Demographics': ['Q2'],
        'Attitudes': ['Q3']
    }
    
    banner = generator.create_nested_banner(variable_groups)
    
    assert isinstance(banner, pd.DataFrame)
    assert len(banner.columns) == 4  # 2 groups × 2 values each
    assert all(col.startswith(('Demographics_', 'Attitudes_')) for col in banner.columns)

def test_generate_banner_table(sample_data):
    """Test generating a banner table."""
    df, metadata = sample_data
    generator = BannerTableGenerator(df, metadata)
    
    result = generator.generate_banner_table('Q1', ['Q2', 'Q3'])
    
    assert isinstance(result, CrosstabResult)
    assert result.row_variable == 'Q1'
    assert len(result.table.columns) == 4  # 2 variables × 2 values each

def test_generate_banner_table_with_groups(sample_data):
    """Test generating a banner table with variable groups."""
    df, metadata = sample_data
    generator = BannerTableGenerator(df, metadata)
    
    variable_groups = {
        'Demographics': ['Q2'],
        'Attitudes': ['Q3']
    }
    
    result = generator.generate_banner_table('Q1', variable_groups)
    
    assert isinstance(result, CrosstabResult)
    assert result.row_variable == 'Q1'
    assert len(result.table.columns) == 4  # 2 groups × 2 values each

def test_create_crosstab(sample_data):
    """Test basic cross-tabulation creation."""
    engine = CrosstabEngine(sample_data[0])
    result = engine.create_crosstab('gender', 'age_group')
    
    assert isinstance(result, CrosstabResult)
    assert isinstance(result.table, pd.DataFrame)
    assert isinstance(result.row_percentages, pd.DataFrame)
    assert isinstance(result.column_percentages, pd.DataFrame)
    assert isinstance(result.total_percentages, pd.DataFrame)
    assert isinstance(result.statistics, StatisticalResult)
    
    # Check table dimensions
    assert result.table.shape == (2, 3)  # 2 genders x 3 age groups
    assert result.table.index.names == ['gender']
    assert result.table.columns.names == ['age_group']
    
    # Check statistics
    assert result.statistics.test_type == StatisticType.CHI_SQUARE
    assert isinstance(result.statistics.statistic, float)
    assert isinstance(result.statistics.p_value, float)
    assert isinstance(result.statistics.effect_size, float)

def test_create_banner_table(sample_data):
    """Test banner table creation."""
    engine = CrosstabEngine(sample_data[0])
    results = engine.create_banner_table(
        row_vars=['gender'],
        col_vars=['age_group', 'satisfaction']
    )
    
    assert isinstance(results, dict)
    assert len(results) == 2  # gender x age_group and gender x satisfaction
    
    for key, result in results.items():
        assert isinstance(result, CrosstabResult)
        assert isinstance(result.table, pd.DataFrame)
        assert isinstance(result.statistics, StatisticalResult)

def test_perform_statistical_test_chi_square(sample_data):
    """Test chi-square test."""
    engine = CrosstabEngine(sample_data[0])
    result = engine.perform_statistical_test(
        'gender',
        'age_group',
        StatisticType.CHI_SQUARE
    )
    
    assert isinstance(result, StatisticalResult)
    assert result.test_type == StatisticType.CHI_SQUARE
    assert isinstance(result.statistic, float)
    assert isinstance(result.p_value, float)
    assert isinstance(result.effect_size, float)

def test_perform_statistical_test_t_test(sample_data):
    """Test t-test."""
    engine = CrosstabEngine(sample_data[0])
    result = engine.perform_statistical_test(
        'gender',
        'income',
        StatisticType.T_TEST
    )
    
    assert isinstance(result, StatisticalResult)
    assert result.test_type == StatisticType.T_TEST
    assert isinstance(result.statistic, float)
    assert isinstance(result.p_value, float)
    assert isinstance(result.effect_size, float)

def test_perform_statistical_test_anova(sample_data):
    """Test ANOVA."""
    engine = CrosstabEngine(sample_data[0])
    result = engine.perform_statistical_test(
        'age_group',
        'income',
        StatisticType.ANOVA
    )
    
    assert isinstance(result, StatisticalResult)
    assert result.test_type == StatisticType.ANOVA
    assert isinstance(result.statistic, float)
    assert isinstance(result.p_value, float)
    assert isinstance(result.effect_size, float)
    assert isinstance(result.degrees_of_freedom, tuple)
    assert len(result.degrees_of_freedom) == 2

def test_perform_statistical_test_fisher_exact(sample_data):
    """Test Fisher's exact test."""
    # Create a 2x2 table for Fisher's exact test
    data = {
        'group': ['A', 'A', 'B', 'B'],
        'outcome': ['Yes', 'No', 'Yes', 'No']
    }
    df = pd.DataFrame(data)
    engine = CrosstabEngine(df)
    
    result = engine.perform_statistical_test(
        'group',
        'outcome',
        StatisticType.FISHER_EXACT
    )
    
    assert isinstance(result, StatisticalResult)
    assert result.test_type == StatisticType.FISHER_EXACT
    assert isinstance(result.statistic, float)
    assert isinstance(result.p_value, float)

def test_invalid_statistical_test(sample_data):
    """Test invalid statistical test type."""
    engine = CrosstabEngine(sample_data[0])
    with pytest.raises(ValueError):
        engine.perform_statistical_test(
            'gender',
            'age_group',
            'invalid_test_type'
        )

def test_invalid_t_test_groups(sample_data):
    """Test t-test with invalid number of groups."""
    engine = CrosstabEngine(sample_data[0])
    with pytest.raises(ValueError):
        engine.perform_statistical_test(
            'age_group',  # More than 2 groups
            'income',
            StatisticType.T_TEST
        )

def test_invalid_anova_groups(sample_data):
    """Test ANOVA with invalid number of groups."""
    # Create data with only one group
    data = {
        'group': ['A', 'A', 'A', 'A'],
        'value': [1, 2, 3, 4]
    }
    df = pd.DataFrame(data)
    engine = CrosstabEngine(df)
    
    with pytest.raises(ValueError):
        engine.perform_statistical_test(
            'group',
            'value',
            StatisticType.ANOVA
        )

def test_empty_data():
    """Test with empty DataFrame."""
    with pytest.raises(ValueError):
        CrosstabEngine(pd.DataFrame())

def test_invalid_data_type():
    """Test with invalid data type."""
    with pytest.raises(ValueError):
        CrosstabEngine("not a dataframe") 