"""Tests for the converter module."""

import tempfile
from pathlib import Path

import pytest

from harmony_migrator.core.config import Config
from harmony_migrator.core.models import APICall, CallType, ComplexityLevel
from harmony_migrator.converter import Converter


def test_converter_initialization():
    """Test converter initialization."""
    config = Config()
    converter = Converter(config)
    assert converter is not None


def test_convert_chat_completion():
    """Test converting a ChatCompletion call."""
    config = Config()
    converter = Converter(config)
    
    # Create a test API call
    call = APICall(
        file_path=Path("test.py"),
        line_number=5,
        call_type=CallType.CHAT_COMPLETION,
        complexity=ComplexityLevel.SIMPLE,
        estimated_tokens=100,
        code_snippet="openai.ChatCompletion.create(...)",
        parameters={
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"}
            ]
        },
        functions=[],
    )
    
    result = converter._convert_single_call(call)
    assert result.success
    assert "LocalInference" in result.converted_code
    assert "Conversation" in result.converted_code


def test_convert_function_call():
    """Test converting a function call."""
    config = Config()
    converter = Converter(config)
    
    # Create a test API call with functions
    call = APICall(
        file_path=Path("test.py"),
        line_number=5,
        call_type=CallType.FUNCTION_CALL,
        complexity=ComplexityLevel.MEDIUM,
        estimated_tokens=150,
        code_snippet="openai.ChatCompletion.create(...)",
        parameters={
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": "What's the weather?"}
            ]
        },
        functions=[
            {
                "name": "get_weather",
                "description": "Get weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"}
                    }
                }
            }
        ],
    )
    
    result = converter._convert_single_call(call)
    assert result.success
    assert "ToolRegistry" in result.converted_code


def test_convert_completion():
    """Test converting a Completion call."""
    config = Config()
    converter = Converter(config)
    
    # Create a test API call
    call = APICall(
        file_path=Path("test.py"),
        line_number=5,
        call_type=CallType.COMPLETION,
        complexity=ComplexityLevel.SIMPLE,
        estimated_tokens=50,
        code_snippet="openai.Completion.create(...)",
        parameters={
            "model": "gpt-3.5-turbo",
            "prompt": "Complete this sentence:"
        },
        functions=[],
    )
    
    result = converter._convert_single_call(call)
    assert result.success
    assert "LocalInference" in result.converted_code


def test_convert_embedding():
    """Test converting an Embedding call."""
    config = Config()
    converter = Converter(config)
    
    # Create a test API call
    call = APICall(
        file_path=Path("test.py"),
        line_number=5,
        call_type=CallType.EMBEDDING,
        complexity=ComplexityLevel.SIMPLE,
        estimated_tokens=10,
        code_snippet="openai.Embedding.create(...)",
        parameters={
            "model": "text-embedding-ada-002",
            "input": "Hello world"
        },
        functions=[],
    )
    
    result = converter._convert_single_call(call)
    assert not result.success
    assert "not supported" in result.errors[0] 