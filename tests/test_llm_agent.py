"""
Tests for the LLM agent module.

This module contains tests for verifying the functionality of:
- LLMAgentSetup
- PromptEngineer
- AnalysisChain
- ResponseGenerator
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)
from langchain_core.runnables import RunnableWithMessageHistory
from core.llm_agent import (
    LLMAgentSetup,
    PromptEngineer,
    AnalysisChain,
    ResponseGenerator
)

@pytest.fixture
def mock_settings():
    """Mock settings with test API key."""
    with patch('core.llm_agent.Settings') as mock_settings:
        mock_settings.return_value.openai_api_key = 'test-api-key'
        yield mock_settings

@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    with patch('core.llm_agent.ChatOpenAI') as mock_llm:
        mock_instance = MagicMock()
        mock_instance.__or__ = lambda self, other: other
        mock_instance.invoke = Mock(return_value="Test response")
        mock_llm.return_value = mock_instance
        yield mock_llm

@pytest.fixture
def mock_runnable():
    """Mock RunnableWithMessageHistory for testing."""
    with patch('core.llm_agent.RunnableWithMessageHistory') as mock_runnable:
        mock_instance = MagicMock()
        mock_instance.invoke = Mock(return_value="Test response")
        mock_runnable.return_value = mock_instance
        yield mock_runnable

def test_llm_agent_setup(mock_settings, mock_llm, mock_runnable):
    """Test LLMAgentSetup initialization and configuration."""
    agent_setup = LLMAgentSetup()
    
    # Verify settings and LLM initialization
    mock_settings.assert_called_once()
    mock_llm.assert_called_once_with(
        temperature=0.7,
        model_name="gpt-3.5-turbo",
        api_key='test-api-key'
    )
    
    # Test chain creation
    prompt = PromptEngineer.create_crosstab_prompt()
    chain = agent_setup.create_chain(prompt)
    assert isinstance(chain, MagicMock)  # Mock of RunnableWithMessageHistory
    mock_runnable.assert_called_once()

def test_prompt_engineer():
    """Test PromptEngineer prompt creation."""
    # Test system message
    system_msg = PromptEngineer.create_system_message()
    assert isinstance(system_msg, SystemMessage)
    assert "expert statistical analyst" in system_msg.content
    
    # Test crosstab prompt
    crosstab_prompt = PromptEngineer.create_crosstab_prompt()
    assert "Analyze the cross-tabulation results" in str(crosstab_prompt)
    
    # Test interpretation prompt
    interpretation_prompt = PromptEngineer.create_interpretation_prompt()
    assert "Interpret the statistical results" in str(interpretation_prompt)
    
    # Test clarification prompt
    clarification_prompt = PromptEngineer.create_clarification_prompt()
    assert "Ask for clarification" in str(clarification_prompt)

@pytest.fixture
def analysis_chain(mock_settings, mock_llm, mock_runnable):
    """Create an AnalysisChain instance for testing."""
    return AnalysisChain()

def test_analysis_chain(analysis_chain):
    """Test AnalysisChain functionality."""
    # Test crosstab analysis
    crosstab_results = {'table': [[1, 2], [3, 4]], 'chi_square': 0.5}
    response = analysis_chain.analyze_crosstab(crosstab_results)
    assert response == "Test response"
    
    # Test statistics interpretation
    stats = {'chi_square': 0.5, 'p_value': 0.05}
    response = analysis_chain.interpret_statistics(stats)
    assert response == "Test response"
    
    # Test clarification request
    response = analysis_chain.request_clarification("test query")
    assert response == "Test response"

@pytest.fixture
def response_generator(mock_settings, mock_llm, mock_runnable):
    """Create a ResponseGenerator instance for testing."""
    return ResponseGenerator()

def test_response_generator(response_generator):
    """Test ResponseGenerator functionality."""
    # Test analysis response generation
    results = {
        'table': [[1, 2], [3, 4]],
        'statistics': {'chi_square': 0.5, 'p_value': 0.05}
    }
    
    response = response_generator.generate_analysis_response(results)
    assert isinstance(response, dict)
    assert 'analysis' in response
    assert 'interpretation' in response
    assert 'suggestions' in response
    assert len(response['suggestions']) == 3
    
    # Test without suggestions
    response = response_generator.generate_analysis_response(
        results,
        include_suggestions=False
    )
    assert 'suggestions' not in response
    
    # Test clarification request
    response = response_generator.request_clarification("test query")
    assert response == "Test response"

def test_edge_cases(mock_settings, mock_llm, mock_runnable):
    """Test edge cases and error handling."""
    agent_setup = LLMAgentSetup()
    
    # Test empty results
    analysis_chain = AnalysisChain()
    empty_results = {}
    response = analysis_chain.analyze_crosstab(empty_results)
    assert response == "Test response"
    
    # Test missing statistics
    response = analysis_chain.interpret_statistics({})
    assert response == "Test response"
    
    # Test empty query
    response = analysis_chain.request_clarification("")
    assert response == "Test response"

def test_integration(mock_settings, mock_llm, mock_runnable):
    """Test integration between components."""
    # Create instances
    agent_setup = LLMAgentSetup()
    analysis_chain = AnalysisChain()
    response_generator = ResponseGenerator()
    
    # Test full analysis pipeline
    results = {
        'table': [[1, 2], [3, 4]],
        'statistics': {'chi_square': 0.5, 'p_value': 0.05}
    }
    
    # Generate analysis
    analysis = analysis_chain.analyze_crosstab(results)
    assert analysis == "Test response"
    
    # Generate interpretation
    interpretation = analysis_chain.interpret_statistics(results['statistics'])
    assert interpretation == "Test response"
    
    # Generate final response
    response = response_generator.generate_analysis_response(results)
    assert isinstance(response, dict)
    assert all(key in response for key in ['analysis', 'interpretation', 'suggestions']) 