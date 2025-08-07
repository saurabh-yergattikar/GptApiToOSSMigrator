"""Configuration management for HarmonyMigrator."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import tomli
from pydantic import BaseModel, Field

from .models import BackendType, ModelType, ReasoningEffort


class ScanningConfig(BaseModel):
    """Configuration for code scanning."""
    
    exclude_patterns: List[str] = Field(
        default=[
            "*.test.py",
            "*.pyc",
            "__pycache__/*",
            "venv/*",
            "node_modules/*",
            ".git/*",
            "*.egg-info/*",
        ],
        description="File patterns to exclude from scanning"
    )
    max_file_size: str = Field(
        default="10MB",
        description="Maximum file size to scan"
    )
    include_extensions: List[str] = Field(
        default=[".py", ".js", ".ts"],
        description="File extensions to include"
    )


class ConversionConfig(BaseModel):
    """Configuration for code conversion."""
    
    preserve_comments: bool = Field(
        default=True,
        description="Preserve original comments in converted code"
    )
    add_imports: bool = Field(
        default=True,
        description="Automatically add required imports"
    )
    backup_files: bool = Field(
        default=True,
        description="Create backup files before conversion"
    )
    reasoning_effort: ReasoningEffort = Field(
        default=ReasoningEffort.MEDIUM,
        description="Default reasoning effort for Harmony"
    )


class InferenceConfig(BaseModel):
    """Configuration for inference backends."""
    
    ollama_host: str = Field(
        default="http://localhost:11434",
        description="Ollama server host"
    )
    vllm_host: str = Field(
        default="http://localhost:8000",
        description="vLLM server host"
    )
    timeout: int = Field(
        default=30,
        description="Request timeout in seconds"
    )
    max_retries: int = Field(
        default=3,
        description="Maximum retry attempts"
    )


class Config(BaseModel):
    """Main configuration for HarmonyMigrator."""
    
    # Default settings
    model: ModelType = Field(
        default=ModelType.GPT_OSS_20B,
        description="Default GPT-OSS model to use"
    )
    backend: BackendType = Field(
        default=BackendType.OLLAMA,
        description="Default inference backend"
    )
    reasoning_effort: ReasoningEffort = Field(
        default=ReasoningEffort.MEDIUM,
        description="Default reasoning effort"
    )
    
    # Sub-configurations
    scanning: ScanningConfig = Field(
        default_factory=ScanningConfig,
        description="Scanning configuration"
    )
    conversion: ConversionConfig = Field(
        default_factory=ConversionConfig,
        description="Conversion configuration"
    )
    inference: InferenceConfig = Field(
        default_factory=InferenceConfig,
        description="Inference configuration"
    )
    
    # Output settings
    output_format: str = Field(
        default="json",
        description="Default output format"
    )
    verbose: bool = Field(
        default=False,
        description="Enable verbose output"
    )
    color: bool = Field(
        default=True,
        description="Enable colored output"
    )
    
    @classmethod
    def load_from_file(cls, config_path: Path) -> "Config":
        """Load configuration from a TOML file."""
        if not config_path.exists():
            return cls()
        
        with open(config_path, "rb") as f:
            config_data = tomli.load(f)
        
        return cls(**config_data)
    
    @classmethod
    def load_from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        config_data = {}
        
        # Map environment variables to config fields
        env_mapping = {
            "HARMONY_MODEL": "model",
            "HARMONY_BACKEND": "backend",
            "HARMONY_REASONING_EFFORT": "reasoning_effort",
            "HARMONY_VERBOSE": "verbose",
            "HARMONY_COLOR": "color",
            "OLLAMA_HOST": "inference.ollama_host",
            "VLLM_HOST": "inference.vllm_host",
        }
        
        for env_var, config_path in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Handle nested config paths
                if "." in config_path:
                    parent, child = config_path.split(".", 1)
                    if parent not in config_data:
                        config_data[parent] = {}
                    config_data[parent][child] = value
                else:
                    config_data[config_path] = value
        
        return cls(**config_data)
    
    @classmethod
    def load_default(cls) -> "Config":
        """Load default configuration."""
        config_path = Path(".harmony-migrator.toml")
        if config_path.exists():
            return cls.load_from_file(config_path)
        
        # Try environment variables
        return cls.load_from_env()
    
    def save_to_file(self, config_path: Path) -> None:
        """Save configuration to a TOML file."""
        config_data = self.dict()
        
        # Convert to TOML format
        toml_data = {}
        for key, value in config_data.items():
            if isinstance(value, dict):
                toml_data[key] = value
            else:
                toml_data[key] = str(value) if not isinstance(value, (bool, int, float)) else value
        
        # Write TOML file
        with open(config_path, "w") as f:
            # Simple TOML writing (in production, use a proper TOML library)
            for section, data in toml_data.items():
                f.write(f"[{section}]\n")
                if isinstance(data, dict):
                    for k, v in data.items():
                        if isinstance(v, str):
                            f.write(f'{k} = "{v}"\n')
                        else:
                            f.write(f"{k} = {v}\n")
                else:
                    if isinstance(data, str):
                        f.write(f'value = "{data}"\n')
                    else:
                        f.write(f"value = {data}\n")
                f.write("\n")
    
    def get_backend_url(self) -> str:
        """Get the URL for the configured backend."""
        if self.backend == BackendType.OLLAMA:
            return self.inference.ollama_host
        elif self.backend == BackendType.VLLM:
            return self.inference.vllm_host
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")
    
    def validate(self) -> List[str]:
        """Validate configuration and return any errors."""
        errors = []
        
        # Validate model and backend compatibility
        if self.backend == BackendType.OLLAMA and self.model not in [
            ModelType.GPT_OSS_20B,
            ModelType.GPT_OSS_120B
        ]:
            errors.append(f"Model {self.model} may not be supported by Ollama backend")
        
        # Validate file size format
        try:
            size_str = self.scanning.max_file_size
            if size_str.endswith("MB"):
                int(size_str[:-2])
            elif size_str.endswith("KB"):
                int(size_str[:-2])
            else:
                int(size_str)
        except ValueError:
            errors.append(f"Invalid max_file_size format: {self.scanning.max_file_size}")
        
        return errors 