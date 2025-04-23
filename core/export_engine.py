"""
Module for handling data and visualization exports.

This module provides functionality for exporting processed data and visualizations
to various formats.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional, Union, Literal
from pydantic import BaseModel
import matplotlib.pyplot as plt

class ExportConfig(BaseModel):
    """Configuration for export operations."""
    format: str  # 'csv', 'excel', 'json'
    file_path: str
    sheet_name: Optional[str] = None
    include_metadata: bool = False
    include_statistics: bool = True

class ExportEngine:
    """
    Handles exporting data and visualizations to various formats.

    Attributes:
        export_dir (Path): Directory for storing exports
    """

    def __init__(self, export_dir: Union[str, Path]):
        """
        Initialize the export engine.

        Args:
            export_dir (Union[str, Path]): Directory for storing exports
        """
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export_data(
        self,
        data: pd.DataFrame,
        format: Literal['csv', 'excel'] = 'csv',
        filename: str = 'exported_data'
    ) -> Path:
        """
        Export data to a file.

        Args:
            data (pd.DataFrame): Data to export
            format (Literal['csv', 'excel']): Export format
            filename (str): Base filename (without extension)

        Returns:
            Path: Path to the exported file
        """
        export_path = self.export_dir / f"{filename}.{format}"
        
        if format == 'csv':
            data.to_csv(export_path, index=False)
        elif format == 'excel':
            data.to_excel(export_path, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")

        return export_path

    def export_visualization(
        self,
        fig: plt.Figure,
        filename: str,
        format: Literal['png', 'pdf', 'svg'] = 'png'
    ) -> Path:
        """
        Export a visualization to a file.

        Args:
            fig (plt.Figure): Matplotlib figure to export
            filename (str): Base filename (without extension)
            format (Literal['png', 'pdf', 'svg']): Export format

        Returns:
            Path: Path to the exported file
        """
        export_path = self.export_dir / f"{filename}.{format}"
        fig.savefig(export_path, format=format, bbox_inches='tight')
        return export_path

    def export_crosstab(self, data: Dict[str, Any], config: ExportConfig) -> str:
        """Export cross-tabulation results.
        
        Args:
            data: Dictionary containing cross-tabulation results
            config: Export configuration
            
        Returns:
            Path to the exported file
        """
        file_path = self.export_dir / config.file_path
        
        if config.format.lower() == 'csv':
            return self._export_to_csv(data, file_path)
        elif config.format.lower() == 'excel':
            return self._export_to_excel(data, file_path, config.sheet_name)
        elif config.format.lower() == 'json':
            return self._export_to_json(data, file_path)
        else:
            raise ValueError(f"Unsupported export format: {config.format}")
    
    def _export_to_csv(self, data: Dict[str, Any], file_path: Path) -> str:
        """Export data to CSV format."""
        df = pd.DataFrame(data['table'])
        df.to_csv(file_path, index=True)
        return str(file_path)
    
    def _export_to_excel(self, data: Dict[str, Any], file_path: Path, sheet_name: Optional[str]) -> str:
        """Export data to Excel format with multiple sheets."""
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Write main crosstab
            pd.DataFrame(data['table']).to_excel(
                writer, 
                sheet_name=sheet_name or 'Crosstab',
                index=True
            )
            
            # Write percentages if available
            if 'row_percentages' in data:
                pd.DataFrame(data['row_percentages']).to_excel(
                    writer,
                    sheet_name='Row Percentages',
                    index=True
                )
            
            if 'column_percentages' in data:
                pd.DataFrame(data['column_percentages']).to_excel(
                    writer,
                    sheet_name='Column Percentages',
                    index=True
                )
            
            # Write statistics if available
            if 'statistics' in data:
                pd.DataFrame([data['statistics']]).to_excel(
                    writer,
                    sheet_name='Statistics',
                    index=False
                )
        
        return str(file_path)
    
    def _export_to_json(self, data: Dict[str, Any], file_path: Path) -> str:
        """Export data to JSON format."""
        # Convert DataFrames to dict format
        export_data = {}
        for key, value in data.items():
            if isinstance(value, pd.DataFrame):
                export_data[key] = value.to_dict(orient='split')
            else:
                export_data[key] = value
        
        pd.DataFrame([export_data]).to_json(file_path, orient='records')
        return str(file_path) 