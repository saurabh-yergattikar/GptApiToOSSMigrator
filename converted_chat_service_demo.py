"""
Converted Chat Service - Demonstrates OpenAI to Harmony migration
"""

from openai_harmony import (
    Author,
    Conversation,
    DeveloperContent,
    HarmonyEncodingName,
    Message,
    Role,
    SystemContent,
    ToolDescription,
    load_harmony_encoding,
    ReasoningEffort
)
from harmony_migrator.inference import LocalInference

# Load Harmony encoding
encoding = load_harmony_encoding(HarmonyEncodingName.HARMONY_GPT_OSS)

class ChatService:
    """Service for handling chat completions with Harmony format."""
    
    def __init__(self, model: str = "gpt-oss-20b"):
        self.model = model
        self.inference = LocalInference(model=model, backend="ollama")
    
    def simple_chat(self, message: str) -> str:
        """Simple chat completion converted to Harmony format."""
        try:
            # Build system content
            system_content = SystemContent.new()
                .with_model_identity("You are ChatGPT, a large language model trained by OpenAI.")
                .with_reasoning_effort(ReasoningEffort.MEDIUM)
                .with_conversation_start_date("2025-06-28")
                .with_knowledge_cutoff("2024-06")
                .with_required_channels(["analysis", "commentary", "final"])
            
            # Build developer content
            developer_content = DeveloperContent.new()
                .with_instructions("You are a helpful assistant.")
            
            # Create conversation
            conversation = Conversation.from_messages([
                Message.from_role_and_content(Role.SYSTEM, system_content),
                Message.from_role_and_content(Role.DEVELOPER, developer_content),
                Message.from_role_and_content(Role.USER, message),
            ])
            
            # Render for completion
            tokens = encoding.render_conversation_for_completion(conversation, Role.ASSISTANT)
            
            # Generate response using tokens
            response = self.inference.generate_with_tokens(tokens)
            
            # Parse response
            parsed_response = encoding.parse_messages_from_completion_tokens(response, Role.ASSISTANT)
            
            # Extract final response
            final_response = None
            for msg in parsed_response:
                if msg.channel == "final":
                    final_response = msg.content
                    break
            
            return final_response or "No final response generated"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def creative_writing(self, prompt: str) -> str:
        """Creative writing with Harmony format."""
        try:
            # Build system content
            system_content = SystemContent.new()
                .with_model_identity("You are ChatGPT, a large language model trained by OpenAI.")
                .with_reasoning_effort(ReasoningEffort.HIGH)
                .with_conversation_start_date("2025-06-28")
                .with_knowledge_cutoff("2024-06")
                .with_required_channels(["analysis", "commentary", "final"])
            
            # Build developer content
            developer_content = DeveloperContent.new()
                .with_instructions("You are a creative writer. Write engaging and imaginative content.")
            
            # Create conversation
            conversation = Conversation.from_messages([
                Message.from_role_and_content(Role.SYSTEM, system_content),
                Message.from_role_and_content(Role.DEVELOPER, developer_content),
                Message.from_role_and_content(Role.USER, prompt),
            ])
            
            # Render for completion
            tokens = encoding.render_conversation_for_completion(conversation, Role.ASSISTANT)
            
            # Generate response using tokens
            response = self.inference.generate_with_tokens(tokens)
            
            # Parse response
            parsed_response = encoding.parse_messages_from_completion_tokens(response, Role.ASSISTANT)
            
            # Extract final response
            final_response = None
            for msg in parsed_response:
                if msg.channel == "final":
                    final_response = msg.content
                    break
            
            return final_response or "No final response generated"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def code_assistant(self, code_question: str) -> str:
        """Code assistance with Harmony tools."""
        try:
            # Build system content
            system_content = SystemContent.new()
                .with_model_identity("You are ChatGPT, a large language model trained by OpenAI.")
                .with_reasoning_effort(ReasoningEffort.MEDIUM)
                .with_conversation_start_date("2025-06-28")
                .with_knowledge_cutoff("2024-06")
                .with_required_channels(["analysis", "commentary", "final"])
            
            # Build developer content with tools
            developer_content = DeveloperContent.new()
                .with_instructions("You are a Python programming expert.")
                .with_function_tools([
                    ToolDescription.new(
                        "explain_code",
                        "Explain Python code or concepts",
                        parameters={
                            "type": "object",
                            "properties": {
                                "concept": {
                                    "type": "string",
                                    "description": "The programming concept to explain"
                                },
                                "complexity": {
                                    "type": "string",
                                    "enum": ["beginner", "intermediate", "advanced"],
                                    "description": "The complexity level of the explanation"
                                }
                            },
                            "required": ["concept"]
                        }
                    )
                ])
            
            # Create conversation
            conversation = Conversation.from_messages([
                Message.from_role_and_content(Role.SYSTEM, system_content),
                Message.from_role_and_content(Role.DEVELOPER, developer_content),
                Message.from_role_and_content(Role.USER, code_question),
            ])
            
            # Render for completion
            tokens = encoding.render_conversation_for_completion(conversation, Role.ASSISTANT)
            
            # Generate response using tokens
            response = self.inference.generate_with_tokens(tokens)
            
            # Parse response
            parsed_response = encoding.parse_messages_from_completion_tokens(response, Role.ASSISTANT)
            
            # Handle tool calls if present
            for msg in parsed_response:
                if msg.channel == "commentary" and hasattr(msg, 'recipient') and msg.recipient:
                    # Handle tool call
                    tool_name = msg.recipient
                    tool_args = msg.content  # JSON string
                    
                    # Execute tool (you would implement this)
                    tool_result = self.execute_tool(tool_name, tool_args)
                    
                    # Add tool response to conversation
                    conversation.add_message(Message.from_author_and_content(
                        Author.new(Role.TOOL, tool_name),
                        tool_result
                    ).with_recipient("assistant").with_channel("commentary"))
                    
                    # Continue generation with tool result
                    tokens = encoding.render_conversation_for_completion(conversation, Role.ASSISTANT)
                    response = self.inference.generate_with_tokens(tokens)
                    parsed_response = encoding.parse_messages_from_completion_tokens(response, Role.ASSISTANT)
            
            # Extract final response
            final_response = None
            for msg in parsed_response:
                if msg.channel == "final":
                    final_response = msg.content
                    break
            
            return final_response or "No final response generated"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def multi_turn_conversation(self, conversation_history: list) -> str:
        """Multi-turn conversation with Harmony format."""
        try:
            # Build system content
            system_content = SystemContent.new()
                .with_model_identity("You are ChatGPT, a large language model trained by OpenAI.")
                .with_reasoning_effort(ReasoningEffort.MEDIUM)
                .with_conversation_start_date("2025-06-28")
                .with_knowledge_cutoff("2024-06")
                .with_required_channels(["analysis", "commentary", "final"])
            
            # Convert conversation history to Harmony format
            messages = [Message.from_role_and_content(Role.SYSTEM, system_content)]
            
            for msg in conversation_history:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                
                if role == 'system':
                    # System messages become developer messages in Harmony
                    developer_content = DeveloperContent.new().with_instructions(content)
                    messages.append(Message.from_role_and_content(Role.DEVELOPER, developer_content))
                elif role == 'user':
                    messages.append(Message.from_role_and_content(Role.USER, content))
                elif role == 'assistant':
                    messages.append(Message.from_role_and_content(Role.ASSISTANT, content))
            
            # Create conversation
            conversation = Conversation.from_messages(messages)
            
            # Render for completion
            tokens = encoding.render_conversation_for_completion(conversation, Role.ASSISTANT)
            
            # Generate response using tokens
            response = self.inference.generate_with_tokens(tokens)
            
            # Parse response
            parsed_response = encoding.parse_messages_from_completion_tokens(response, Role.ASSISTANT)
            
            # Extract final response
            final_response = None
            for msg in parsed_response:
                if msg.channel == "final":
                    final_response = msg.content
                    break
            
            return final_response or "No final response generated"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def execute_tool(self, tool_name: str, args: str) -> str:
        """Execute a tool call."""
        # This would be your actual tool implementation
        return '{"result": "tool executed"}'

# Example usage
if __name__ == "__main__":
    chat_service = ChatService()
    
    # Test simple chat
    response = chat_service.simple_chat("What is the capital of France?")
    print(f"Response: {response}") 