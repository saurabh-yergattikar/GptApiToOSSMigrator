"""Builder for creating Harmony conversation structures using the real format."""

from typing import Any, Dict, List, Optional

from ..core.config import Config
from ..core.models import ReasoningEffort


class HarmonyBuilder:
    """Builds real Harmony conversation structures from OpenAI API calls."""
    
    def __init__(self, config: Config):
        self.config = config
    
    def build_conversation(
        self,
        messages: List[Dict[str, Any]],
        model: str = "gpt-3.5-turbo",
        reasoning_effort: ReasoningEffort = ReasoningEffort.MEDIUM,
    ) -> Dict[str, Any]:
        """Build a real Harmony conversation from OpenAI messages."""
        # Convert OpenAI messages to real Harmony format
        harmony_messages = []
        
        # Add system message (required for Harmony)
        system_content = self._build_system_content(reasoning_effort)
        harmony_messages.append({
            "role": "system",
            "content": system_content,
            "type": "system"
        })
        
        # Convert OpenAI messages to Harmony format
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'system':
                # System messages become developer messages in Harmony
                harmony_messages.append({
                    "role": "developer",
                    "content": f"# Instructions\n{content}",
                    "type": "developer"
                })
            elif role == 'user':
                harmony_messages.append({
                    "role": "user",
                    "content": content,
                    "type": "user"
                })
            elif role == 'assistant':
                harmony_messages.append({
                    "role": "assistant",
                    "content": content,
                    "type": "assistant"
                })
        
        return {
            "messages": harmony_messages,
            "model": model,
            "reasoning_effort": reasoning_effort.value,
            "format": "harmony"
        }
    
    def build_conversation_with_tools(
        self,
        messages: List[Dict[str, Any]],
        functions: List[Dict[str, Any]],
        model: str = "gpt-3.5-turbo",
        reasoning_effort: ReasoningEffort = ReasoningEffort.MEDIUM,
    ) -> Dict[str, Any]:
        """Build a real Harmony conversation with tools from OpenAI function calls."""
        # Build base conversation
        conversation = self.build_conversation(messages, model, reasoning_effort)
        
        # Add function tools to developer message
        if functions:
            tools_section = self._build_tools_section(functions)
            # Find developer message and add tools
            for msg in conversation["messages"]:
                if msg["role"] == "developer":
                    msg["content"] += f"\n{tools_section}"
                    break
        
        return conversation
    
    def build_completion_conversation(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo",
        reasoning_effort: ReasoningEffort = ReasoningEffort.MEDIUM,
    ) -> Dict[str, Any]:
        """Build a real Harmony conversation for completion-style prompts."""
        # Add system message
        system_content = self._build_system_content(reasoning_effort)
        
        messages = [
            {
                "role": "system",
                "content": system_content,
                "type": "system"
            },
            {
                "role": "user",
                "content": prompt,
                "type": "user"
            }
        ]
        
        return {
            "messages": messages,
            "model": model,
            "reasoning_effort": reasoning_effort.value,
            "format": "harmony"
        }
    
    def _build_system_content(self, reasoning_effort: ReasoningEffort) -> str:
        """Build the real Harmony system message content."""
        reasoning_map = {
            ReasoningEffort.LOW: "low",
            ReasoningEffort.MEDIUM: "medium",
            ReasoningEffort.HIGH: "high"
        }
        
        return f"""You are ChatGPT, a large language model trained by OpenAI.
Knowledge cutoff: 2024-06
Current date: 2025-06-28
Reasoning: {reasoning_map[reasoning_effort]}
# Valid channels: analysis, commentary, final. Channel must be included for every message.
Calls to these tools must go to the commentary channel: 'functions'."""
    
    def _build_tools_section(self, functions: List[Dict[str, Any]]) -> str:
        """Build the real Harmony tools section for developer message."""
        tools_content = "\n# Tools\n## functions\nnamespace functions {\n"
        
        for func in functions:
            name = func.get('name', '')
            description = func.get('description', '')
            parameters = func.get('parameters', {})
            
            if description:
                tools_content += f"// {description}\n"
            
            # Build TypeScript-like function definition
            if parameters.get('type') == 'object':
                props = parameters.get('properties', {})
                required = parameters.get('required', [])
                
                param_str = "(_: {\n"
                for prop_name, prop_def in props.items():
                    prop_type = prop_def.get('type', 'string')
                    prop_desc = prop_def.get('description', '')
                    
                    if prop_desc:
                        param_str += f"// {prop_desc}\n"
                    
                    # Handle optional parameters
                    if prop_name not in required:
                        param_str += f"{prop_name}?: {prop_type},\n"
                    else:
                        param_str += f"{prop_name}: {prop_type},\n"
                
                param_str += "}) => any;"
            else:
                param_str = "() => any;"
            
            tools_content += f"type {name} = {param_str}\n\n"
        
        tools_content += "} // namespace functions"
        return tools_content
    
    def generate_harmony_prompt(self, conversation: Dict[str, Any]) -> str:
        """Generate the real Harmony prompt format with special tokens."""
        prompt = ""
        
        for message in conversation["messages"]:
            role = message["role"]
            content = message["content"]
            
            # Add special tokens for real Harmony format
            prompt += f"<|start|>{role}<|message|>{content}<|end|>\n"
        
        # Add assistant start for response
        prompt += "<|start|>assistant\n"
        
        return prompt
    
    def validate_conversation(self, conversation: Dict[str, Any]) -> List[str]:
        """Validate a real Harmony conversation structure."""
        errors = []
        
        # Check required fields
        if "messages" not in conversation:
            errors.append("Missing 'messages' field")
        
        # Validate messages
        if "messages" in conversation:
            has_system = False
            for i, msg in enumerate(conversation["messages"]):
                if "role" not in msg:
                    errors.append(f"Message {i} missing 'role' field")
                if "content" not in msg:
                    errors.append(f"Message {i} missing 'content' field")
                
                if msg.get("role") == "system":
                    has_system = True
            
            if not has_system:
                errors.append("Missing required 'system' message")
        
        return errors 