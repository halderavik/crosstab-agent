"""
Visualization engine for generating charts and visualizations from cross-tabulation results.
"""

from typing import Dict, List, Optional, Union
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pydantic import BaseModel
from core.crosstab_engine import CrosstabResult
import matplotlib.pyplot as plt
import seaborn as sns

class ChartConfig(BaseModel):
    """Configuration for chart generation."""
    title: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    width: int = 800
    height: int = 600
    theme: str = "plotly_white"
    color_palette: List[str] = [
        "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
    ]

class VisualizationEngine:
    """
    Engine for generating visualizations from cross-tabulation results.
    
    This class provides functionality for:
    - Bar charts
    - Stacked bar charts
    - Heatmaps
    - Line charts
    - Pie charts
    - Statistical significance visualization
    """

    def __init__(self, config: Optional[ChartConfig] = None):
        """
        Initialize the visualization engine.
        
        Args:
            config: Optional configuration for chart generation
        """
        self.config = config or ChartConfig()
        sns.set_theme()
        sns.set_palette("husl")

    def create_bar_chart(
        self,
        data: pd.DataFrame,
        x: str,
        y: str,
        chart_title: Optional[str] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None
    ) -> plt.Figure:
        """
        Create a bar chart.

        Args:
            data (pd.DataFrame): Data to visualize
            x (str): Column name for x-axis
            y (str): Column name for y-axis
            chart_title (Optional[str]): Chart title
            x_label (Optional[str]): X-axis label
            y_label (Optional[str]): Y-axis label

        Returns:
            plt.Figure: Matplotlib figure containing the chart
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create the bar chart
        sns.barplot(data=data, x=x, y=y, ax=ax)
        
        # Set labels and title
        if x_label:
            ax.set_xlabel(x_label)
        if y_label:
            ax.set_ylabel(y_label)
        if chart_title:
            ax.set_title(chart_title)
        
        # Rotate x-axis labels if needed
        if len(data[x].unique()) > 5:
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        return fig

    def create_stacked_bar_chart(
        self,
        data: Union[pd.DataFrame, CrosstabResult],
        orientation: str = "vertical",
        show_percentages: bool = False,
        config: Optional[ChartConfig] = None
    ) -> go.Figure:
        """
        Create a stacked bar chart from cross-tabulation data.
        
        Args:
            data: DataFrame or CrosstabResult to visualize
            orientation: "vertical" or "horizontal"
            show_percentages: Whether to show percentages instead of counts
            config: Optional chart configuration
            
        Returns:
            Plotly Figure object
        """
        config = config or self.config
        if isinstance(data, CrosstabResult):
            data = data.total_percentages if show_percentages else data.table
            
        fig = go.Figure()
        
        if orientation == "vertical":
            for col in data.columns:
                fig.add_trace(go.Bar(
                    name=str(col),
                    x=data.index,
                    y=data[col],
                    marker_color=self.config.color_palette[data.columns.get_loc(col) % len(self.config.color_palette)]
                ))
        else:
            for idx in data.index:
                fig.add_trace(go.Bar(
                    name=str(idx),
                    y=data.columns,
                    x=data.loc[idx],
                    orientation='h',
                    marker_color=self.config.color_palette[data.index.get_loc(idx) % len(self.config.color_palette)]
                ))
        
        fig.update_layout(
            title=self.config.title or "Stacked Bar Chart",
            xaxis_title=self.config.x_label or "Categories",
            yaxis_title=self.config.y_label or ("Percentage" if show_percentages else "Count"),
            width=self.config.width,
            height=self.config.height,
            template=self.config.theme,
            barmode='stack'
        )
        
        return fig

    def create_heatmap(
        self,
        data: Union[pd.DataFrame, CrosstabResult],
        show_percentages: bool = False,
        config: Optional[ChartConfig] = None
    ) -> go.Figure:
        """
        Create a heatmap from cross-tabulation data.
        
        Args:
            data: DataFrame or CrosstabResult to visualize
            show_percentages: Whether to show percentages instead of counts
            config: Optional chart configuration
            
        Returns:
            Plotly Figure object
        """
        config = config or self.config
        if isinstance(data, CrosstabResult):
            data = data.total_percentages if show_percentages else data.table
            
        fig = go.Figure(data=go.Heatmap(
            z=data.values,
            x=data.columns,
            y=data.index,
            colorscale='Viridis',
            text=data.values.round(2),
            texttemplate="%{text}",
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title=self.config.title or "Heatmap",
            xaxis_title=self.config.x_label or "Categories",
            yaxis_title=self.config.y_label or "Categories",
            width=self.config.width,
            height=self.config.height,
            template=self.config.theme
        )
        
        return fig

    def create_line_chart(
        self,
        data: Union[pd.DataFrame, CrosstabResult],
        show_percentages: bool = False,
        config: Optional[ChartConfig] = None
    ) -> go.Figure:
        """
        Create a line chart from cross-tabulation data.
        
        Args:
            data: DataFrame or CrosstabResult to visualize
            show_percentages: Whether to show percentages instead of counts
            config: Optional chart configuration
            
        Returns:
            Plotly Figure object
        """
        config = config or self.config
        if isinstance(data, CrosstabResult):
            data = data.total_percentages if show_percentages else data.table
            
        fig = go.Figure()
        
        for col in data.columns:
            fig.add_trace(go.Scatter(
                name=str(col),
                x=data.index,
                y=data[col],
                mode='lines+markers',
                line=dict(color=self.config.color_palette[data.columns.get_loc(col) % len(self.config.color_palette)])
            ))
        
        fig.update_layout(
            title=self.config.title or "Line Chart",
            xaxis_title=self.config.x_label or "Categories",
            yaxis_title=self.config.y_label or ("Percentage" if show_percentages else "Count"),
            width=self.config.width,
            height=self.config.height,
            template=self.config.theme
        )
        
        return fig

    def create_pie_chart(
        self,
        data: Union[pd.DataFrame, CrosstabResult],
        show_percentages: bool = False,
        config: Optional[ChartConfig] = None
    ) -> go.Figure:
        """
        Create a pie chart from cross-tabulation data.
        
        Args:
            data: DataFrame or CrosstabResult to visualize
            show_percentages: Whether to show percentages instead of counts
            config: Optional chart configuration
            
        Returns:
            Plotly Figure object
        """
        config = config or self.config
        if isinstance(data, CrosstabResult):
            data = data.total_percentages if show_percentages else data.table
            
        # For pie charts, we'll use the first column or row
        if len(data.columns) > 1:
            values = data.iloc[:, 0]
        else:
            values = data.iloc[0]
            
        fig = go.Figure(data=[go.Pie(
            labels=values.index,
            values=values.values,
            textinfo='label+percent',
            marker_colors=self.config.color_palette[:len(values)]
        )])
        
        fig.update_layout(
            title=self.config.title or "Pie Chart",
            width=self.config.width,
            height=self.config.height,
            template=self.config.theme
        )
        
        return fig

    def create_statistical_visualization(
        self,
        data: CrosstabResult,
        config: Optional[ChartConfig] = None
    ) -> go.Figure:
        """
        Create a visualization showing statistical significance.
        
        Args:
            data: CrosstabResult containing statistical information
            config: Optional chart configuration
            
        Returns:
            Plotly Figure object
        """
        config = config or self.config
        
        if not data.statistics:
            raise ValueError("No statistical information available")
            
        fig = make_subplots(rows=2, cols=1, subplot_titles=("Observed vs Expected", "Standardized Residuals"))
        
        # Observed vs Expected
        fig.add_trace(
            go.Heatmap(
                z=data.table.values,
                x=data.table.columns,
                y=data.table.index,
                colorscale='Viridis',
                name="Observed",
                showscale=False
            ),
            row=1, col=1
        )
        
        if data.expected_values is not None:
            fig.add_trace(
                go.Heatmap(
                    z=data.expected_values.values,
                    x=data.expected_values.columns,
                    y=data.expected_values.index,
                    colorscale='Viridis',
                    name="Expected",
                    showscale=False
                ),
                row=1, col=1
            )
        
        # Standardized Residuals
        if data.residuals is not None:
            fig.add_trace(
                go.Heatmap(
                    z=data.residuals.values,
                    x=data.residuals.columns,
                    y=data.residuals.index,
                    colorscale='RdBu',
                    name="Residuals",
                    showscale=True
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            title=self.config.title or "Statistical Analysis",
            width=self.config.width,
            height=self.config.height * 1.5,
            template=self.config.theme
        )
        
        return fig 