"""
Storage manager for handling file operations.

This module provides functionality for storing and retrieving data files,
including processed data, visualizations, and metadata.
"""

import os
import shutil
from pathlib import Path
import pandas as pd
import json
from typing import Optional, Union, Any
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import threading
import uuid

class StorageManager:
    """Manages storage operations for the application."""

    def __init__(self, base_dir: Path):
        """
        Initialize the storage manager.

        Args:
            base_dir (Path): Base directory for storage operations
        """
        self.base_dir = Path(base_dir)
        self.uploads_dir = self.base_dir / "uploads"
        self.exports_dir = self.base_dir / "exports"
        self.metadata_dir = self.base_dir / "metadata"
        self.visualizations_dir = self.base_dir / "visualizations"
        self._lock = threading.Lock()

        # Create necessary directories
        for dir_path in [self.uploads_dir, self.exports_dir, self.metadata_dir, self.visualizations_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    @property
    def storage_dir(self) -> Path:
        """Get the base storage directory."""
        return self.base_dir

    def _generate_file_id(self, filename: str) -> str:
        """
        Generate a unique file ID.

        Args:
            filename (str): Base filename

        Returns:
            str: Unique file ID
        """
        with self._lock:
            return f"{Path(filename).stem}_{uuid.uuid4().hex[:8]}"

    def save_data(self, filename: str, data: Any) -> str:
        """
        Save data to a file.

        Args:
            filename (str): Name of the file to save
            data (Any): Data to save

        Returns:
            str: File ID of the saved data
        """
        file_id = self._generate_file_id(filename)
        
        # Determine file extension and path based on data type
        if isinstance(data, pd.DataFrame):
            file_path = self.uploads_dir / f"{file_id}.csv"
            data.to_csv(file_path, index=False)
        else:
            file_path = self.uploads_dir / f"{file_id}.json"
            with open(file_path, 'w') as f:
                json.dump(data, f)

        # Set file permissions
        try:
            os.chmod(file_path, 0o644)
        except OSError:
            # Ignore permission errors on Windows
            pass
            
        return file_id

    def load_data(self, file_id: str) -> Any:
        """
        Load data from a file.

        Args:
            file_id (str): ID of the file to load

        Returns:
            Any: Loaded data
        """
        csv_path = self.uploads_dir / f"{file_id}.csv"
        json_path = self.uploads_dir / f"{file_id}.json"

        if csv_path.exists():
            try:
                return pd.read_csv(csv_path)
            except pd.errors.EmptyDataError:
                return pd.DataFrame()
            except Exception as e:
                raise ValueError(f"Error reading CSV file {file_id}: {str(e)}")
        elif json_path.exists():
            with open(json_path, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON in file {file_id}: {str(e)}")
        else:
            raise FileNotFoundError(f"File {file_id} not found")

    def save_visualization(self, viz_id: str, figure: Union[plt.Figure, go.Figure], format: str = 'png') -> str:
        """
        Save a visualization to a file.

        Args:
            viz_id (str): ID for the visualization
            figure (Union[plt.Figure, go.Figure]): Figure to save
            format (str): Format to save in ('png', 'jpg', 'svg', 'html')

        Returns:
            str: Path to the saved visualization
        """
        # Ensure visualization directory exists
        self.visualizations_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = self.visualizations_dir / f"{viz_id}.{format}"
        
        try:
            if isinstance(figure, plt.Figure):
                if format in ['png', 'jpg', 'svg']:
                    figure.savefig(file_path, format=format, bbox_inches='tight')
                else:
                    raise ValueError(f"Unsupported format {format} for matplotlib figure")
            elif isinstance(figure, go.Figure):
                if format == 'html':
                    figure.write_html(file_path)
                elif format in ['png', 'jpg', 'svg']:
                    try:
                        import plotly.io as pio
                        # Check if kaleido is properly initialized
                        if not hasattr(pio, 'kaleido') or not hasattr(pio.kaleido, 'scope'):
                            raise ImportError("Kaleido is not properly initialized")
                        figure.write_image(file_path)
                    except (ImportError, AttributeError) as e:
                        raise ValueError(
                            "Image export requires a properly configured kaleido package. "
                            "Please ensure it's installed and initialized correctly: "
                            "pip install kaleido==0.2.1"
                        )
                else:
                    raise ValueError(f"Unsupported format {format} for plotly figure")
            else:
                raise TypeError("Figure must be either matplotlib.Figure or plotly.graph_objects.Figure")
            
            # Set file permissions
            try:
                os.chmod(file_path, 0o644)
            except OSError:
                # Ignore permission errors on Windows
                pass
                
            return str(file_path)
        except Exception as e:
            raise ValueError(f"Error saving visualization: {str(e)}")

    def load_visualization(self, viz_id: str, format: str = 'png') -> Union[plt.Figure, bytes]:
        """
        Load a visualization from a file.

        Args:
            viz_id (str): ID of the visualization
            format (str): Format of the visualization

        Returns:
            Union[plt.Figure, bytes]: Loaded visualization
        """
        # Handle both file paths and visualization IDs
        if os.path.exists(viz_id):
            file_path = Path(viz_id)
        else:
            file_path = self.visualizations_dir / f"{viz_id}.{format}"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Visualization {viz_id}.{format} not found")
            
        try:
            if format in ['png', 'jpg']:
                # For images, return the raw bytes
                with open(file_path, 'rb') as f:
                    return f.read()
            elif format == 'svg':
                # For SVG, return the text content
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif format == 'html':
                # For HTML, return the text content
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                raise ValueError(f"Unsupported format {format}")
        except Exception as e:
            raise ValueError(f"Error loading visualization: {str(e)}")

    def list_files(self, pattern: str = "*") -> list[str]:
        """
        List files in storage.

        Args:
            pattern (str): Pattern to match filenames

        Returns:
            list[str]: List of file IDs
        """
        files = []
        for ext in [".csv", ".json"]:
            files.extend([
                f.name for f in self.uploads_dir.glob(f"*{ext}")
                if f.name.endswith(ext)
            ])
        return files

    def delete_file(self, file_id: str) -> None:
        """
        Delete a file.

        Args:
            file_id (str): ID of the file to delete
        """
        for ext in [".csv", ".json"]:
            file_path = self.uploads_dir / f"{file_id}{ext}"
            if file_path.exists():
                file_path.unlink()

        # Also delete any associated metadata
        metadata_path = self.metadata_dir / f"{file_id}.json"
        if metadata_path.exists():
            metadata_path.unlink()

    def file_exists(self, file_id: str) -> bool:
        """
        Check if a file exists.

        Args:
            file_id (str): ID of the file to check

        Returns:
            bool: True if file exists, False otherwise
        """
        return any(
            (self.uploads_dir / f"{file_id}{ext}").exists()
            for ext in [".csv", ".json"]
        )

    def store_metadata(self, file_id: str, metadata: dict) -> None:
        """
        Store metadata for a file.

        Args:
            file_id (str): ID of the file
            metadata (dict): Metadata to store
        """
        metadata_path = self.metadata_dir / f"{file_id}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)

    def get_metadata(self, file_id: str) -> dict:
        """
        Retrieve metadata for a file.

        Args:
            file_id (str): ID of the file

        Returns:
            dict: Retrieved metadata
        """
        metadata_path = self.metadata_dir / f"{file_id}.json"
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata for {file_id} not found")
        with open(metadata_path, 'r') as f:
            return json.load(f)

    def metadata_exists(self, file_id: str) -> bool:
        """
        Check if metadata exists for a file.

        Args:
            file_id (str): ID of the file

        Returns:
            bool: True if metadata exists, False otherwise
        """
        return (self.metadata_dir / f"{file_id}.json").exists()

    def cleanup(self) -> None:
        """Clean up all stored files and metadata."""
        # Remove all directories
        for dir_path in [self.uploads_dir, self.exports_dir, self.metadata_dir, self.visualizations_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)

        # Remove base directory
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)

        # Recreate directories
        self.base_dir.mkdir(parents=True, exist_ok=True)
        for dir_path in [self.uploads_dir, self.exports_dir, self.metadata_dir, self.visualizations_dir]:
            dir_path.mkdir(parents=True, exist_ok=True) 