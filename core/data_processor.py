"""
Data processor module for handling data file parsing and data cleaning.
"""

from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from pathlib import Path
from pydantic import BaseModel

class VariableMetadata(BaseModel):
    """Metadata for a variable in the dataset."""
    name: str
    label: Optional[str] = None
    type: str
    value_labels: Optional[Dict[Any, str]] = None
    missing_values: Optional[List[Any]] = None
    measure: Optional[str] = None

class DataProcessor:
    """Handles data file parsing and data cleaning."""
    
    def __init__(self, data: Optional[pd.DataFrame] = None, metadata: Optional[Dict[str, Any]] = None):
        """Initialize the data processor."""
        self.data = data
        self.metadata = metadata or {}
    
    def load_data_file(self, file_path: str) -> tuple[pd.DataFrame, Dict[str, Any]]:
        """Load data from a file.
        
        Args:
            file_path: Path to the data file
            
        Returns:
            Tuple of (DataFrame, metadata)
            
        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file format is not supported
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Read the file based on extension
        if file_path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
        
        # Create basic metadata
        metadata = {
            'variables': list(df.columns),
            'n_cases': len(df),
            'variable_value_labels': {},
            'missing_ranges': {}
        }
        
        self.data = df
        self.metadata = metadata
        return df, metadata
    
    def get_variable_info(self, variable_name: str) -> VariableMetadata:
        """Get metadata for a specific variable.
        
        Args:
            variable_name: Name of the variable
            
        Returns:
            VariableMetadata object containing variable information
            
        Raises:
            ValueError: If no data is loaded
            KeyError: If the variable is not found in the dataset
        """
        if self.data is None:
            raise ValueError("No data loaded")
            
        if variable_name not in self.data.columns:
            raise KeyError(f"Variable {variable_name} not found in dataset")
        
        return VariableMetadata(
            name=variable_name,
            type=str(self.data[variable_name].dtype),
            value_labels=self.metadata.get('variable_value_labels', {}).get(variable_name),
            missing_values=self.metadata.get('missing_ranges', {}).get(variable_name),
            measure=self.metadata.get('variable_measure', {}).get(variable_name)
        )
    
    def clean_data(self, variables: Optional[List[str]] = None) -> pd.DataFrame:
        """Clean the data for analysis.
        
        Args:
            variables: List of variables to include (None for all)
            
        Returns:
            Cleaned DataFrame
            
        Raises:
            ValueError: If no data is loaded
        """
        if self.data is None:
            raise ValueError("No data loaded")
            
        df = self.data.copy()
        
        if variables:
            df = df[variables]
        
        # Handle missing values
        for col in df.columns:
            missing_ranges = self.metadata.get('missing_ranges', {}).get(col, [])
            for range_def in missing_ranges:
                if 'value' in range_def:
                    df[col] = df[col].replace(range_def['value'], pd.NA)
                elif 'lo' in range_def and 'hi' in range_def:
                    mask = (df[col] >= range_def['lo']) & (df[col] <= range_def['hi'])
                    df.loc[mask, col] = pd.NA
        
        return df
    
    def get_variable_summary(self, variable_name: str) -> Dict[str, Any]:
        """Get summary statistics for a variable.
        
        Args:
            variable_name: Name of the variable
            
        Returns:
            Dictionary containing summary statistics
            
        Raises:
            ValueError: If no data is loaded
            KeyError: If the variable is not found in the dataset
        """
        if self.data is None:
            raise ValueError("No data loaded")
            
        if variable_name not in self.data.columns:
            raise KeyError(f"Variable {variable_name} not found in dataset")
        
        series = self.data[variable_name]
        
        summary = {
            "name": variable_name,
            "type": str(series.dtype),
            "n_missing": series.isna().sum(),
            "n_unique": series.nunique()
        }
        
        if pd.api.types.is_numeric_dtype(series):
            summary.update({
                "mean": series.mean(),
                "std": series.std(),
                "min": series.min(),
                "max": series.max(),
                "quartiles": series.quantile([0.25, 0.5, 0.75]).to_dict()
            })
        else:
            value_counts = series.value_counts()
            summary.update({
                "frequencies": value_counts.to_dict(),
                "mode": value_counts.index[0] if not value_counts.empty else None
            })
        
        return summary
        
    def validate_data(self) -> Dict[str, List[str]]:
        """Validate the loaded data.
        
        Returns:
            Dictionary mapping variable names to lists of validation issues
        """
        if self.data is None:
            return {}
            
        validation_results = {}
        
        for col in self.data.columns:
            issues = []
            series = self.data[col]
            
            # Check for missing values
            if series.isna().any():
                issues.append(f"Contains {series.isna().sum()} missing values")
            
            # Check for unexpected values based on metadata
            if col in self.metadata.get('variable_value_labels', {}):
                expected_values = set(self.metadata['variable_value_labels'][col].keys())
                actual_values = set(series.dropna().unique())
                unexpected = actual_values - expected_values
                if unexpected:
                    issues.append(f"Contains unexpected values: {unexpected}")
            
            if issues:
                validation_results[col] = issues
                
        return validation_results

    def transform_data(self, operations: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Transform data using a list of operations.

        Args:
            operations (List[Dict[str, Any]]): List of transformation operations.
                Each operation is a dictionary with:
                - type: The type of operation ('filter', 'groupby', etc.)
                - Additional parameters specific to the operation type

        Returns:
            pd.DataFrame: Transformed data

        Raises:
            ValueError: If no data is loaded or if operation is invalid
        """
        if self.data is None:
            raise ValueError("No data loaded")

        df = self.data.copy()

        for op in operations:
            op_type = op.get('type')
            if op_type == 'filter':
                column = op.get('column')
                operator = op.get('operator')
                value = op.get('value')

                if not all([column, operator, value is not None]):
                    raise ValueError("Filter operation requires column, operator, and value")

                if operator == '>':
                    df = df[df[column] > value]
                elif operator == '<':
                    df = df[df[column] < value]
                elif operator == '>=':
                    df = df[df[column] >= value]
                elif operator == '<=':
                    df = df[df[column] <= value]
                elif operator == '==':
                    df = df[df[column] == value]
                elif operator == '!=':
                    df = df[df[column] != value]
                else:
                    raise ValueError(f"Unsupported operator: {operator}")

            elif op_type == 'groupby':
                column = op.get('column')
                agg = op.get('agg')
                numeric_only = op.get('numeric_only', False)

                if not all([column, agg]):
                    raise ValueError("Groupby operation requires column and aggregation method")

                if agg == 'mean':
                    df = df.groupby(column, as_index=False).mean(numeric_only=numeric_only)
                elif agg == 'sum':
                    df = df.groupby(column, as_index=False).sum(numeric_only=numeric_only)
                elif agg == 'count':
                    df = df.groupby(column).size().reset_index(name='count')
                else:
                    raise ValueError(f"Unsupported aggregation method: {agg}")

            else:
                raise ValueError(f"Unsupported operation type: {op_type}")

        return df 