"""
Tests for settings configuration.
"""
import os
import pytest
from config.settings import Settings

def test_default_allowed_extensions():
    """Test that default allowed extensions are set correctly."""
    settings = Settings()
    assert settings.allowed_extensions == [".sav"]

def test_allowed_extensions_from_env_json():
    """Test that allowed extensions can be set from environment variable using JSON."""
    # Set environment variable as JSON
    os.environ["SPSS_ALLOWED_EXTENSIONS"] = '[".sav", ".csv", ".xlsx"]'
    
    settings = Settings()
    assert settings.allowed_extensions == [".sav", ".csv", ".xlsx"]
    
    # Clean up
    del os.environ["SPSS_ALLOWED_EXTENSIONS"]

def test_allowed_extensions_from_env_csv():
    """Test that allowed extensions can be set from environment variable using CSV."""
    # Set environment variable as comma-separated
    os.environ["SPSS_ALLOWED_EXTENSIONS"] = ".sav,.csv,.xlsx"
    
    settings = Settings()
    assert settings.allowed_extensions == [".sav", ".csv", ".xlsx"]
    
    # Clean up
    del os.environ["SPSS_ALLOWED_EXTENSIONS"]

def test_debug_from_env():
    """Test that debug can be set from environment variable."""
    # Test True value
    os.environ["SPSS_DEBUG"] = "true"
    settings = Settings()
    assert settings.debug is True
    
    # Test False value
    os.environ["SPSS_DEBUG"] = "false"
    settings = Settings()
    assert settings.debug is False
    
    # Clean up
    del os.environ["SPSS_DEBUG"]

def test_upload_dir_creation():
    """Test that upload directory is created."""
    settings = Settings()
    assert settings.upload_dir.exists()
    assert settings.upload_dir.is_dir()

def test_allowed_origins_from_env():
    """Test that allowed origins can be set from environment variable."""
    # Test comma-separated format
    os.environ["SPSS_ALLOWED_ORIGINS"] = "http://localhost:3000,http://example.com"
    settings = Settings()
    assert settings.allowed_origins == ["http://localhost:3000", "http://example.com"]
    
    # Test JSON format
    os.environ["SPSS_ALLOWED_ORIGINS"] = '["http://localhost:3000", "http://example.com"]'
    settings = Settings()
    assert settings.allowed_origins == ["http://localhost:3000", "http://example.com"]
    
    # Clean up
    del os.environ["SPSS_ALLOWED_ORIGINS"] 