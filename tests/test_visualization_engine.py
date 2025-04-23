"""
Test suite for the visualization engine module.
"""
import pytest
import pandas as pd
import numpy as np
from core.visualization_engine import VisualizationEngine, ChartConfig
from core.crosstab_engine import CrosstabResult, StatisticalResult, StatisticType

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    data = {
        'Q1': [1, 2, 3, 4, 5, 1, 2, 3, 4, 5],
        'Q2': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B'],
        'Q3': [1, 1, 2, 2, 1, 1, 2, 2, 1, 1],
        'Group': ['G1', 'G1', 'G1', 'G1', 'G1', 'G2', 'G2', 'G2', 'G2', 'G2']
    }
    return pd.DataFrame(data)

@pytest.fixture
def sample_crosstab_result(sample_data):
    """Create a sample CrosstabResult for testing."""
    table = pd.crosstab(sample_data['Q1'], sample_data['Q2'])
    row_percentages = pd.crosstab(sample_data['Q1'], sample_data['Q2'], normalize='index')
    column_percentages = pd.crosstab(sample_data['Q1'], sample_data['Q2'], normalize='columns')
    total_percentages = pd.crosstab(sample_data['Q1'], sample_data['Q2'], normalize='all')
    
    # Calculate expected values and residuals
    row_totals = table.sum(axis=1)
    col_totals = table.sum(axis=0)
    total = table.sum().sum()
    expected = np.outer(row_totals, col_totals) / total
    residuals = (table - expected) / np.sqrt(expected)
    
    statistics = StatisticalResult(
        test_type=StatisticType.CHI_SQUARE,
        statistic=10.0,
        p_value=0.05,
        degrees_of_freedom=4,
        effect_size=0.5
    )
    
    return CrosstabResult(
        table=table,
        row_percentages=row_percentages,
        column_percentages=column_percentages,
        total_percentages=total_percentages,
        statistics=statistics,
        expected_values=pd.DataFrame(expected, index=table.index, columns=table.columns),
        residuals=pd.DataFrame(residuals, index=table.index, columns=table.columns)
    )

def test_visualization_engine_initialization():
    """Test VisualizationEngine initialization."""
    engine = VisualizationEngine()
    assert isinstance(engine.config, ChartConfig)
    
    custom_config = ChartConfig(
        title="Custom Title",
        width=1000,
        height=800
    )
    engine = VisualizationEngine(custom_config)
    assert engine.config.title == "Custom Title"
    assert engine.config.width == 1000
    assert engine.config.height == 800

def test_create_bar_chart(sample_data):
    """Test bar chart creation."""
    engine = VisualizationEngine()
    
    # Test with DataFrame
    fig = engine.create_bar_chart(sample_data)
    assert fig is not None
    assert len(fig.data) == len(sample_data.columns)
    
    # Test with custom config
    config = ChartConfig(
        title="Custom Bar Chart",
        x_label="X Axis",
        y_label="Y Axis"
    )
    fig = engine.create_bar_chart(sample_data, config=config)
    assert fig.layout.title.text == "Custom Bar Chart"
    assert fig.layout.xaxis.title.text == "X Axis"
    assert fig.layout.yaxis.title.text == "Y Axis"

def test_create_stacked_bar_chart(sample_data):
    """Test stacked bar chart creation."""
    engine = VisualizationEngine()
    
    # Test with DataFrame
    fig = engine.create_stacked_bar_chart(sample_data)
    assert fig is not None
    assert len(fig.data) == len(sample_data.columns)
    assert fig.layout.barmode == 'stack'
    
    # Test with percentages
    fig = engine.create_stacked_bar_chart(sample_data, show_percentages=True)
    assert fig is not None

def test_create_heatmap(sample_data):
    """Test heatmap creation."""
    engine = VisualizationEngine()
    
    # Test with DataFrame
    fig = engine.create_heatmap(sample_data)
    assert fig is not None
    assert isinstance(fig.data[0], go.Heatmap)
    
    # Test with custom colorscale
    config = ChartConfig(color_palette=['#ff0000', '#00ff00', '#0000ff'])
    fig = engine.create_heatmap(sample_data, config=config)
    assert fig is not None

def test_create_line_chart(sample_data):
    """Test line chart creation."""
    engine = VisualizationEngine()
    
    # Test with DataFrame
    fig = engine.create_line_chart(sample_data)
    assert fig is not None
    assert len(fig.data) == len(sample_data.columns)
    assert all(trace.mode == 'lines+markers' for trace in fig.data)
    
    # Test with horizontal orientation
    fig = engine.create_line_chart(sample_data)
    assert fig is not None

def test_create_pie_chart(sample_data):
    """Test pie chart creation."""
    engine = VisualizationEngine()
    
    # Test with DataFrame
    fig = engine.create_pie_chart(sample_data)
    assert fig is not None
    assert isinstance(fig.data[0], go.Pie)
    
    # Test with percentages
    fig = engine.create_pie_chart(sample_data, show_percentages=True)
    assert fig is not None

def test_create_statistical_visualization(sample_crosstab_result):
    """Test statistical visualization creation."""
    engine = VisualizationEngine()
    
    # Test with CrosstabResult
    fig = engine.create_statistical_visualization(sample_crosstab_result)
    assert fig is not None
    assert len(fig.data) >= 2  # At least observed and residuals
    
    # Test with invalid data
    invalid_result = CrosstabResult(
        table=sample_crosstab_result.table,
        row_percentages=sample_crosstab_result.row_percentages,
        column_percentages=sample_crosstab_result.column_percentages,
        total_percentages=sample_crosstab_result.total_percentages,
        statistics=None
    )
    with pytest.raises(ValueError):
        engine.create_statistical_visualization(invalid_result)

def test_chart_config_validation():
    """Test ChartConfig validation."""
    # Test valid config
    config = ChartConfig(
        title="Valid Config",
        width=800,
        height=600
    )
    assert config.title == "Valid Config"
    
    # Test invalid width
    with pytest.raises(ValueError):
        ChartConfig(width=-100)
    
    # Test invalid height
    with pytest.raises(ValueError):
        ChartConfig(height=-100)
    
    # Test invalid theme
    with pytest.raises(ValueError):
        ChartConfig(theme="invalid_theme") 