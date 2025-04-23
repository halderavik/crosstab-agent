"""
Module for handling crosstab analysis results.

This module defines the CrosstabResult class which encapsulates the results
of a crosstab analysis, including the frequency table and various percentage
calculations.
"""

from typing import Dict, Optional, Any, Union, List
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field, field_validator, ConfigDict

class CrosstabStatistics(BaseModel):
    """
    Statistical measures for a crosstab analysis.

    Attributes:
        chi_square (float): Chi-square statistic
        p_value (float): P-value from chi-square test
        degrees_of_freedom (float): Degrees of freedom
        cramers_v (float): Cramer's V statistic
        expected_values (List[List[float]]): Expected values matrix
        residuals (List[List[float]]): Residuals matrix
    """
    chi_square: float
    p_value: float
    degrees_of_freedom: float
    cramers_v: float
    expected_values: List[List[float]]
    residuals: List[List[float]]

    @field_validator('expected_values', 'residuals')
    @classmethod
    def validate_matrix(cls, v):
        """Validate that the value is a valid matrix."""
        if isinstance(v, pd.DataFrame):
            return v.values.tolist()
        elif isinstance(v, np.ndarray):
            return v.tolist()
        elif isinstance(v, list):
            return v
        raise ValueError("Value must be a matrix (list of lists)")

class CrosstabResult(BaseModel):
    """
    Result of a cross-tabulation analysis.

    Attributes:
        table (pd.DataFrame): The contingency table
        row_percentages (pd.DataFrame): Row-wise percentages
        column_percentages (pd.DataFrame): Column-wise percentages
        total_percentages (pd.DataFrame): Total percentages
        statistics (CrosstabStatistics): Statistical measures
    """
    table: pd.DataFrame
    row_percentages: Optional[pd.DataFrame] = None
    column_percentages: Optional[pd.DataFrame] = None
    total_percentages: Optional[pd.DataFrame] = None
    statistics: Optional[CrosstabStatistics] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator('table', 'row_percentages', 'column_percentages', 'total_percentages')
    @classmethod
    def validate_dataframe(cls, v):
        """Validate that the value is a pandas DataFrame."""
        if v is not None and not isinstance(v, pd.DataFrame):
            raise ValueError("Value must be a pandas DataFrame")
        return v

    @field_validator('statistics')
    @classmethod
    def validate_statistics(cls, v):
        """Validate the statistics object."""
        if v is None:
            return v
        if isinstance(v, dict):
            # Convert dictionary to CrosstabStatistics
            return CrosstabStatistics(**v)
        if isinstance(v, CrosstabStatistics):
            return v
        raise ValueError("Statistics must be a dictionary or CrosstabStatistics object") 