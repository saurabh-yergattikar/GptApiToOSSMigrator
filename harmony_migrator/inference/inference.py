"""Local inference engine for GPT-OSS models."""

import json
import time
from typing import Any, Dict, List, Optional

import requests
from pydantic import BaseModel

from ..core.config import Config
from ..core.models import BackendType, ModelType
from .backends import OllamaBackend, VLLMBackend, TransformersBackend


class InferenceResponse(BaseModel):
    """Response from local inference."""
    
    content: str
    model: str
    backend: str
    tokens_used: Optional[int] = None
    response_time: float
    metadata: Dict[str, Any] = {}


class LocalInference:
    """Local inference engine for GPT-OSS models."""
    
    def __init__(
        self,
        model: str = "gpt-oss-20b",
        backend: str = "ollama",
        config: Optional[Config] = None,
    ):
        self.model = ModelType(model) if isinstance(model, str) else model
        self.backend_type = BackendType(backend) if isinstance(backend, str) else backend
        self.config = config or Config()
        
        # Initialize backend
        self.backend = self._initialize_backend()
    
    def _initialize_backend(self):
        """Initialize the appropriate backend."""
        if self.backend_type == BackendType.OLLAMA:
            return OllamaBackend(
                model=self.model.value,
                host=self.config.inference.ollama_host,
                timeout=self.config.inference.timeout,
            )
        elif self.backend_type == BackendType.VLLM:
            return VLLMBackend(
                model=self.model.value,
                host=self.config.inference.vllm_host,
                timeout=self.config.inference.timeout,
            )
        elif self.backend_type == BackendType.TRANSFORMERS:
            return TransformersBackend(
                model=self.model.value,
                timeout=self.config.inference.timeout,
            )
        else:
            raise ValueError(f"Unsupported backend: {self.backend_type}")
    
    def generate(self, conversation: Dict[str, Any]) -> InferenceResponse:
        """Generate a response using the local model."""
        start_time = time.time()
        
        try:
            # Validate conversation structure
            errors = self._validate_conversation(conversation)
            if errors:
                raise ValueError(f"Invalid conversation: {', '.join(errors)}")
            
            # Generate response using backend
            response = self.backend.generate(conversation)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            return InferenceResponse(
                content=response["content"],
                model=self.model.value,
                backend=self.backend_type.value,
                tokens_used=response.get("tokens_used"),
                response_time=response_time,
                metadata=response.get("metadata", {}),
            )
        
        except Exception as e:
            response_time = time.time() - start_time
            raise InferenceError(f"Generation failed: {str(e)}", response_time)
    
    def _validate_conversation(self, conversation: Dict[str, Any]) -> List[str]:
        """Validate conversation structure."""
        errors = []
        
        # Check required fields
        if "roles" not in conversation:
            errors.append("Missing 'roles' field")
        if "channels" not in conversation:
            errors.append("Missing 'channels' field")
        
        # Validate roles
        if "roles" in conversation:
            for i, role in enumerate(conversation["roles"]):
                if not isinstance(role, dict):
                    errors.append(f"Role {i} must be a dictionary")
                    continue
                
                if "name" not in role:
                    errors.append(f"Role {i} missing 'name' field")
                if "content" not in role:
                    errors.append(f"Role {i} missing 'content' field")
        
        # Validate channels
        if "channels" in conversation:
            for i, channel in enumerate(conversation["channels"]):
                if not isinstance(channel, dict):
                    errors.append(f"Channel {i} must be a dictionary")
                    continue
                
                if "name" not in channel:
                    errors.append(f"Channel {i} missing 'name' field")
                if "content" not in channel:
                    errors.append(f"Channel {i} missing 'content' field")
        
        return errors
    
    def test_connection(self) -> bool:
        """Test connection to the inference backend."""
        try:
            return self.backend.test_connection()
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        try:
            return self.backend.get_model_info()
        except Exception as e:
            return {
                "model": self.model.value,
                "backend": self.backend_type.value,
                "error": str(e),
            }


class InferenceError(Exception):
    """Exception raised during inference."""
    
    def __init__(self, message: str, response_time: float = 0.0):
        self.message = message
        self.response_time = response_time
        super().__init__(self.message) 