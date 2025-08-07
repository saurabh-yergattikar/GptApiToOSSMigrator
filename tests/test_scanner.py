"""Tests for the scanner module."""

import tempfile
from pathlib import Path

import pytest

from harmony_migrator.core.config import Config
from harmony_migrator.scanner import Scanner


def test_scanner_initialization():
    """Test scanner initialization."""
    config = Config()
    scanner = Scanner(config)
    assert scanner is not None


def test_scan_empty_directory():
    """Test scanning an empty directory."""
    config = Config()
    scanner = Scanner(config)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        result = scanner.scan_repository(Path(temp_dir))
        assert result.total_files_scanned == 0
        assert result.api_calls_found == 0


def test_scan_with_openai_calls():
    """Test scanning a directory with OpenAI API calls."""
    config = Config()
    scanner = Scanner(config)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a test file with OpenAI API calls
        test_file = temp_path / "test_app.py"
        test_file.write_text("""
import openai

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)
""")
        
        result = scanner.scan_repository(temp_path)
        assert result.total_files_scanned == 1
        assert result.api_calls_found == 1
        assert len(result.calls) == 1
        
        call = result.calls[0]
        assert call.file_path.name == "test_app.py"
        assert call.call_type.value == "chat_completion"


def test_scan_excludes_patterns():
    """Test that scanner excludes specified patterns."""
    config = Config()
    config.scanning.exclude_patterns.append("*.pyc")
    scanner = Scanner(config)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create files that should be excluded
        excluded_file = temp_path / "test.pyc"
        excluded_file.write_text("import openai")
        
        # Create a file that should be included
        included_file = temp_path / "test.py"
        included_file.write_text("""
import openai
response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[])
""")
        
        result = scanner.scan_repository(temp_path)
        assert result.total_files_scanned == 1
        assert result.api_calls_found == 1 