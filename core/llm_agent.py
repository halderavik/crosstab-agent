"""
LLM agent module for handling natural language queries.
"""

from typing import Dict, Any, List, Optional
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnableWithMessageHistory
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from config.settings import Settings

class LLMAgentSetup:
    """Sets up the LLM agent with necessary components."""
    
    def __init__(self):
        """Initialize the LLM agent setup."""
        settings = Settings()
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-3.5-turbo",
            api_key=settings.openai_api_key
        )
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )
    
    def create_chain(self, prompt: ChatPromptTemplate) -> RunnableWithMessageHistory:
        """Create a conversation chain.
        
        Args:
            prompt: Chat prompt template
            
        Returns:
            Configured conversation chain
        """
        chain = prompt | self.llm
        return RunnableWithMessageHistory(
            chain,
            memory=self.memory,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="output",
            verbose=True
        )

class PromptEngineer:
    """Creates prompts for different analysis scenarios."""
    
    @staticmethod
    def create_system_message() -> SystemMessage:
        """Create the system message."""
        return SystemMessage(content="""
        You are an expert statistical analyst specializing in SPSS data analysis.
        Your role is to help users understand their data through cross-tabulation
        analysis and visualization. Provide clear, accurate explanations and
        suggest relevant statistical tests when appropriate.
        """)
    
    @staticmethod
    def create_crosstab_prompt() -> ChatPromptTemplate:
        """Create prompt for cross-tabulation analysis."""
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "Analyze the cross-tabulation results and provide insights."
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
    
    @staticmethod
    def create_interpretation_prompt() -> ChatPromptTemplate:
        """Create prompt for result interpretation."""
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "Interpret the statistical results and explain their significance."
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
    
    @staticmethod
    def create_clarification_prompt() -> ChatPromptTemplate:
        """Create prompt for requesting clarification."""
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "Ask for clarification about the analysis request."
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}")
        ])

class AnalysisChain:
    """Sets up different conversation chains for analysis."""
    
    def __init__(self):
        """Initialize the analysis chain."""
        self.setup = LLMAgentSetup()
        self.prompt_engineer = PromptEngineer()
        
        # Create specialized chains
        self.crosstab_chain = self.setup.create_chain(
            self.prompt_engineer.create_crosstab_prompt()
        )
        self.interpretation_chain = self.setup.create_chain(
            self.prompt_engineer.create_interpretation_prompt()
        )
        self.clarification_chain = self.setup.create_chain(
            self.prompt_engineer.create_clarification_prompt()
        )
    
    def analyze_crosstab(self, results: Dict[str, Any]) -> str:
        """Analyze cross-tabulation results.
        
        Args:
            results: Cross-tabulation results
            
        Returns:
            Analysis of the results
        """
        return self.crosstab_chain.invoke({
            "input": f"Analyze these cross-tabulation results: {results}"
        })
    
    def interpret_statistics(self, statistics: Dict[str, float]) -> str:
        """Interpret statistical results.
        
        Args:
            statistics: Statistical test results
            
        Returns:
            Interpretation of the statistics
        """
        return self.interpretation_chain.invoke({
            "input": f"Interpret these statistical results: {statistics}"
        })
    
    def request_clarification(self, query: str) -> str:
        """Request clarification about the analysis.
        
        Args:
            query: User's query
            
        Returns:
            Clarification request
        """
        return self.clarification_chain.invoke({
            "input": f"Need clarification about: {query}"
        })

class ResponseGenerator:
    """Generates responses based on analysis results."""
    
    def __init__(self):
        """Initialize the response generator."""
        self.analysis_chain = AnalysisChain()
    
    def generate_analysis_response(
        self,
        results: Dict[str, Any],
        include_suggestions: bool = True
    ) -> Dict[str, Any]:
        """Generate a complete analysis response.
        
        Args:
            results: Analysis results
            include_suggestions: Whether to include follow-up suggestions
            
        Returns:
            Dictionary containing the response components
        """
        analysis = self.analysis_chain.analyze_crosstab(results)
        interpretation = self.analysis_chain.interpret_statistics(
            results.get("statistics", {})
        )
        
        response = {
            "analysis": analysis,
            "interpretation": interpretation
        }
        
        if include_suggestions:
            response["suggestions"] = self._generate_suggestions(results)
        
        return response
    
    def _generate_suggestions(self, results: Dict[str, Any]) -> List[str]:
        """Generate follow-up suggestions.
        
        Args:
            results: Analysis results
            
        Returns:
            List of suggested follow-up analyses
        """
        # Add logic for generating suggestions based on results
        suggestions = [
            "Consider analyzing subgroups separately",
            "Try visualizing the results with a heatmap",
            "Explore related variables for deeper insights"
        ]
        return suggestions
    
    def request_clarification(self, query: str) -> str:
        """Request clarification about the analysis.
        
        Args:
            query: User's query
            
        Returns:
            Clarification request
        """
        return self.analysis_chain.request_clarification(query) 