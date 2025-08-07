"""Core data models for HarmonyMigrator."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class CallType(str, Enum):
    """Types of OpenAI API calls that can be detected."""
    
    CHAT_COMPLETION = "chat_completion"
    COMPLETION = "completion"
    FUNCTION_CALL = "function_call"
    EMBEDDING = "embedding"
    FINE_TUNE = "fine_tune"


class ComplexityLevel(str, Enum):
    """Complexity levels for API calls."""
    
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


class BackendType(str, Enum):
    """Supported inference backends."""
    
    OLLAMA = "ollama"
    VLLM = "vllm"
    TRANSFORMERS = "transformers"


class ModelType(str, Enum):
    """Supported GPT-OSS models."""
    
    GPT_OSS_20B = "gpt-oss-20b"
    GPT_OSS_120B = "gpt-oss-120b"


class ReasoningEffort(str, Enum):
    """Harmony reasoning effort levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class APICall(BaseModel):
    """Represents a detected OpenAI API call."""
    
    file_path: Path = Field(..., description="Path to the file containing the call")
    line_number: int = Field(..., description="Line number of the call")
    call_type: CallType = Field(..., description="Type of API call")
    complexity: ComplexityLevel = Field(..., description="Complexity of the call")
    estimated_tokens: int = Field(..., description="Estimated token count")
    code_snippet: str = Field(..., description="Original code snippet")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Call parameters")
    functions: List[Dict[str, Any]] = Field(default_factory=list, description="Function definitions")
    
    class Config:
        arbitrary_types_allowed = True


class ScanResult(BaseModel):
    """Result of scanning a codebase for OpenAI API calls."""
    
    total_files_scanned: int = Field(..., description="Total number of files scanned")
    api_calls_found: int = Field(..., description="Number of API calls detected")
    estimated_monthly_savings: str = Field(..., description="Estimated monthly cost savings")
    migration_complexity: ComplexityLevel = Field(..., description="Overall migration complexity")
    calls: List[APICall] = Field(default_factory=list, description="List of detected API calls")
    scan_timestamp: datetime = Field(default_factory=datetime.now, description="When the scan was performed")
    
    class Config:
        json_encoders = {
            Path: str,
            datetime: lambda v: v.isoformat(),
        }


class ConversionResult(BaseModel):
    """Result of converting an API call to Harmony format."""
    
    original_call: APICall = Field(..., description="Original API call")
    converted_code: str = Field(..., description="Converted Harmony code")
    harmony_conversation: Dict[str, Any] = Field(..., description="Harmony conversation structure")
    success: bool = Field(..., description="Whether conversion was successful")
    warnings: List[str] = Field(default_factory=list, description="Conversion warnings")
    errors: List[str] = Field(default_factory=list, description="Conversion errors")
    estimated_tokens: int = Field(..., description="Estimated tokens for converted call")
    
    class Config:
        arbitrary_types_allowed = True


class Conversation(BaseModel):
    """Harmony conversation structure."""
    
    roles: List[Dict[str, str]] = Field(default_factory=list, description="Conversation roles")
    channels: List[Dict[str, str]] = Field(default_factory=list, description="Conversation channels")
    tools: List[Dict[str, Any]] = Field(default_factory=list, description="Available tools")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Conversation metadata")


class MigrationReport(BaseModel):
    """Complete migration report for a codebase."""
    
    scan_result: ScanResult = Field(..., description="Original scan results")
    conversion_results: List[ConversionResult] = Field(default_factory=list, description="Conversion results")
    total_conversions: int = Field(..., description="Total number of conversions attempted")
    successful_conversions: int = Field(..., description="Number of successful conversions")
    failed_conversions: int = Field(..., description="Number of failed conversions")
    estimated_total_savings: str = Field(..., description="Total estimated cost savings")
    migration_timestamp: datetime = Field(default_factory=datetime.now, description="When migration was performed")
    model_used: ModelType = Field(..., description="GPT-OSS model used")
    backend_used: BackendType = Field(..., description="Inference backend used")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
    
    @property
    def success_rate(self) -> float:
        """Calculate the success rate of conversions."""
        if self.total_conversions == 0:
            return 0.0
        return self.successful_conversions / self.total_conversions
    
    @property
    def summary(self) -> Dict[str, Any]:
        """Get a summary of the migration report."""
        return {
            "total_files_scanned": self.scan_result.total_files_scanned,
            "api_calls_found": self.scan_result.api_calls_found,
            "conversions_attempted": self.total_conversions,
            "conversions_successful": self.successful_conversions,
            "success_rate": f"{self.success_rate:.1%}",
            "estimated_savings": self.estimated_total_savings,
            "model_used": self.model_used.value,
            "backend_used": self.backend_used.value,
        } 