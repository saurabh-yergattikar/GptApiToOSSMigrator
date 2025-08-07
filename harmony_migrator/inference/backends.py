"""Backend implementations for local inference."""

import json
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List

import requests


class BaseBackend(ABC):
    """Base class for inference backends."""
    
    def __init__(self, model: str, timeout: int = 30):
        self.model = model
        self.timeout = timeout
    
    @abstractmethod
    def generate(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a response from the model."""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to the backend."""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        pass


class OllamaBackend(BaseBackend):
    """Ollama backend for local inference."""
    
    def __init__(self, model: str, host: str = "http://localhost:11434", timeout: int = 30):
        super().__init__(model, timeout)
        self.host = host.rstrip('/')
        self.api_url = f"{self.host}/api/generate"
    
    def generate(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a response using Ollama."""
        # Convert Harmony conversation to Ollama format
        prompt = self._convert_to_prompt(conversation)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 2048,
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            
            result = response.json()
            return {
                "content": result.get("response", ""),
                "tokens_used": result.get("eval_count"),
                "metadata": {
                    "model": self.model,
                    "backend": "ollama",
                    "prompt_tokens": result.get("prompt_eval_count"),
                    "response_tokens": result.get("eval_count"),
                }
            }
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API error: {str(e)}")
    
    def _convert_to_prompt(self, conversation: Dict[str, Any]) -> str:
        """Convert Harmony conversation to Ollama prompt format."""
        prompt_parts = []
        
        # Add roles
        for role in conversation.get("roles", []):
            name = role.get("name", "")
            content = role.get("content", "")
            
            if name == "system":
                prompt_parts.append(f"System: {content}")
            elif name == "developer":
                prompt_parts.append(f"User: {content}")
            elif name == "assistant":
                prompt_parts.append(f"Assistant: {content}")
            else:
                prompt_parts.append(f"{name.title()}: {content}")
        
        # Add channel instructions
        channels = conversation.get("channels", [])
        if channels:
            channel_names = [c.get("name", "") for c in channels]
            if "analysis" in channel_names:
                prompt_parts.append("\nPlease provide your analysis and reasoning.")
            if "reasoning" in channel_names:
                prompt_parts.append("\nPlease show your step-by-step reasoning.")
            prompt_parts.append("\nPlease provide your final response.")
        
        return "\n\n".join(prompt_parts)
    
    def test_connection(self) -> bool:
        """Test connection to Ollama."""
        try:
            response = requests.get(
                f"{self.host}/api/tags",
                timeout=self.timeout,
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        try:
            response = requests.get(
                f"{self.host}/api/show",
                json={"name": self.model},
                timeout=self.timeout,
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "model": self.model,
                    "backend": "ollama",
                    "size": data.get("size"),
                    "modified_at": data.get("modified_at"),
                    "parameters": data.get("parameter_size"),
                }
            else:
                return {
                    "model": self.model,
                    "backend": "ollama",
                    "error": f"HTTP {response.status_code}",
                }
        
        except Exception as e:
            return {
                "model": self.model,
                "backend": "ollama",
                "error": str(e),
            }


class VLLMBackend(BaseBackend):
    """vLLM backend for local inference."""
    
    def __init__(self, model: str, host: str = "http://localhost:8000", timeout: int = 30):
        super().__init__(model, timeout)
        self.host = host.rstrip('/')
        self.api_url = f"{self.host}/v1/chat/completions"
    
    def generate(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a response using vLLM."""
        # Convert Harmony conversation to OpenAI format for vLLM
        messages = self._convert_to_messages(conversation)
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2048,
            "stream": False,
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            
            result = response.json()
            choice = result.get("choices", [{}])[0]
            
            return {
                "content": choice.get("message", {}).get("content", ""),
                "tokens_used": result.get("usage", {}).get("total_tokens"),
                "metadata": {
                    "model": self.model,
                    "backend": "vllm",
                    "prompt_tokens": result.get("usage", {}).get("prompt_tokens"),
                    "completion_tokens": result.get("usage", {}).get("completion_tokens"),
                }
            }
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"vLLM API error: {str(e)}")
    
    def _convert_to_messages(self, conversation: Dict[str, Any]) -> List[Dict[str, str]]:
        """Convert Harmony conversation to OpenAI message format."""
        messages = []
        
        for role in conversation.get("roles", []):
            name = role.get("name", "")
            content = role.get("content", "")
            
            # Map Harmony roles to OpenAI roles
            if name == "system":
                messages.append({"role": "system", "content": content})
            elif name == "developer":
                messages.append({"role": "user", "content": content})
            elif name == "assistant":
                messages.append({"role": "assistant", "content": content})
            else:
                messages.append({"role": "user", "content": f"{name}: {content}"})
        
        return messages
    
    def test_connection(self) -> bool:
        """Test connection to vLLM."""
        try:
            response = requests.get(
                f"{self.host}/v1/models",
                timeout=self.timeout,
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        try:
            response = requests.get(
                f"{self.host}/v1/models",
                timeout=self.timeout,
            )
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("data", [])
                model_info = next((m for m in models if m.get("id") == self.model), {})
                
                return {
                    "model": self.model,
                    "backend": "vllm",
                    "object": model_info.get("object"),
                    "created": model_info.get("created"),
                    "owned_by": model_info.get("owned_by"),
                }
            else:
                return {
                    "model": self.model,
                    "backend": "vllm",
                    "error": f"HTTP {response.status_code}",
                }
        
        except Exception as e:
            return {
                "model": self.model,
                "backend": "vllm",
                "error": str(e),
            }


class TransformersBackend(BaseBackend):
    """Transformers backend for local inference."""
    
    def __init__(self, model: str, timeout: int = 30):
        super().__init__(model, timeout)
        self._model = None
        self._tokenizer = None
    
    def generate(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a response using Transformers."""
        # This is a simplified implementation
        # In practice, you'd load the model and tokenizer
        prompt = self._convert_to_prompt(conversation)
        
        # Simulate generation (replace with actual model inference)
        response_text = f"Generated response for: {prompt[:100]}..."
        
        return {
            "content": response_text,
            "tokens_used": len(prompt.split()),
            "metadata": {
                "model": self.model,
                "backend": "transformers",
                "prompt_length": len(prompt),
            }
        }
    
    def _convert_to_prompt(self, conversation: Dict[str, Any]) -> str:
        """Convert Harmony conversation to prompt format."""
        prompt_parts = []
        
        for role in conversation.get("roles", []):
            name = role.get("name", "")
            content = role.get("content", "")
            prompt_parts.append(f"{name}: {content}")
        
        return "\n".join(prompt_parts)
    
    def test_connection(self) -> bool:
        """Test if Transformers backend is available."""
        try:
            # In practice, you'd check if the model is loaded
            return True
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            "model": self.model,
            "backend": "transformers",
            "status": "not_implemented",
            "note": "Transformers backend requires model loading implementation",
        } 