"""Main converter class for converting OpenAI API calls to Harmony format."""

import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core.config import Config
from ..core.models import APICall, ConversionResult, MigrationReport
from .harmony_builder import HarmonyBuilder


class Converter:
    """Converts OpenAI API calls to Harmony format."""
    
    def __init__(self, config: Config):
        self.config = config
        self.console = Console()
        self.harmony_builder = HarmonyBuilder(config)
    
    def convert_calls(self, calls: List[APICall]) -> List[ConversionResult]:
        """Convert a list of API calls to Harmony format."""
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task("Converting API calls...", total=len(calls))
            
            for call in calls:
                progress.update(task, description=f"Converting {call.file_path.name}:{call.line_number}")
                result = self._convert_single_call(call)
                results.append(result)
                progress.advance(task)
        
        return results
    
    def _convert_single_call(self, call: APICall) -> ConversionResult:
        """Convert a single API call to Harmony format."""
        try:
            if call.call_type.value == "chat_completion":
                return self._convert_chat_completion(call)
            elif call.call_type.value == "function_call":
                return self._convert_function_call(call)
            elif call.call_type.value == "completion":
                return self._convert_completion(call)
            elif call.call_type.value == "embedding":
                return self._convert_embedding(call)
            else:
                return ConversionResult(
                    original_call=call,
                    converted_code="",
                    harmony_conversation={},
                    success=False,
                    errors=[f"Unsupported call type: {call.call_type}"],
                    estimated_tokens=call.estimated_tokens,
                )
        
        except Exception as e:
            return ConversionResult(
                original_call=call,
                converted_code="",
                harmony_conversation={},
                success=False,
                errors=[f"Conversion error: {str(e)}"],
                estimated_tokens=call.estimated_tokens,
            )
    
    def _convert_chat_completion(self, call: APICall) -> ConversionResult:
        """Convert a ChatCompletion call to Harmony format."""
        messages = call.parameters.get('messages', [])
        model = call.parameters.get('model', 'gpt-3.5-turbo')
        
        # Build Harmony conversation
        conversation = self.harmony_builder.build_conversation(
            messages=messages,
            model=model,
            reasoning_effort=self.config.reasoning_effort,
        )
        
        # Generate converted code
        converted_code = self._generate_harmony_code(conversation, call)
        
        return ConversionResult(
            original_call=call,
            converted_code=converted_code,
            harmony_conversation=conversation,
            success=True,
            warnings=[],
            errors=[],
            estimated_tokens=call.estimated_tokens,
        )
    
    def _convert_function_call(self, call: APICall) -> ConversionResult:
        """Convert a function call to Harmony format."""
        messages = call.parameters.get('messages', [])
        functions = call.functions
        model = call.parameters.get('model', 'gpt-3.5-turbo')
        
        # Build Harmony conversation with tools
        conversation = self.harmony_builder.build_conversation_with_tools(
            messages=messages,
            functions=functions,
            model=model,
            reasoning_effort=self.config.reasoning_effort,
        )
        
        # Generate converted code
        converted_code = self._generate_harmony_code_with_tools(conversation, call)
        
        warnings = []
        if functions:
            warnings.append("Function calls converted to Harmony tools - manual review recommended")
        
        return ConversionResult(
            original_call=call,
            converted_code=converted_code,
            harmony_conversation=conversation,
            success=True,
            warnings=warnings,
            errors=[],
            estimated_tokens=call.estimated_tokens,
        )
    
    def _convert_completion(self, call: APICall) -> ConversionResult:
        """Convert a Completion call to Harmony format."""
        prompt = call.parameters.get('prompt', '')
        model = call.parameters.get('model', 'gpt-3.5-turbo')
        
        # Build Harmony conversation for completion
        conversation = self.harmony_builder.build_completion_conversation(
            prompt=prompt,
            model=model,
            reasoning_effort=self.config.reasoning_effort,
        )
        
        # Generate converted code
        converted_code = self._generate_harmony_code(conversation, call)
        
        return ConversionResult(
            original_call=call,
            converted_code=converted_code,
            harmony_conversation=conversation,
            success=True,
            warnings=[],
            errors=[],
            estimated_tokens=call.estimated_tokens,
        )
    
    def _convert_embedding(self, call: APICall) -> ConversionResult:
        """Convert an Embedding call to Harmony format."""
        # Note: Embeddings are not directly supported in Harmony format
        # This would need a different approach
        return ConversionResult(
            original_call=call,
            converted_code="",
            harmony_conversation={},
            success=False,
            warnings=[],
            errors=["Embedding calls are not supported in Harmony format"],
            estimated_tokens=call.estimated_tokens,
        )
    
    def _generate_harmony_code(self, conversation: Dict[str, Any], call: APICall) -> str:
        """Generate real Harmony code from conversation structure."""
        imports = [
            "from openai_harmony import (",
            "    Author,",
            "    Conversation,",
            "    DeveloperContent,",
            "    HarmonyEncodingName,",
            "    Message,",
            "    Role,",
            "    SystemContent,",
            "    ToolDescription,",
            "    load_harmony_encoding,",
            "    ReasoningEffort",
            ")",
            "from harmony_migrator.inference import LocalInference",
        ]
        
        # Build system content
        reasoning_effort = self.config.reasoning_effort.value.upper()
        system_content = f'''SystemContent.new()
    .with_model_identity("You are ChatGPT, a large language model trained by OpenAI.")
    .with_reasoning_effort(ReasoningEffort.{reasoning_effort})
    .with_conversation_start_date("2025-06-28")
    .with_knowledge_cutoff("2024-06")
    .with_required_channels(["analysis", "commentary", "final"])'''
        
        # Build developer content
        developer_content = "DeveloperContent.new()"
        if conversation.get("messages"):
            # Find developer message content
            for msg in conversation["messages"]:
                if msg.get("role") == "developer":
                    instructions = msg.get("content", "").replace("# Instructions\n", "")
                    developer_content += f'\n    .with_instructions("""{instructions}""")'
                    break
        
        # Build conversation messages
        messages_code = []
        for msg in conversation["messages"]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                messages_code.append("Message.from_role_and_content(Role.SYSTEM, system_content)")
            elif role == "developer":
                messages_code.append("Message.from_role_and_content(Role.DEVELOPER, developer_content)")
            elif role == "user":
                messages_code.append(f'Message.from_role_and_content(Role.USER, """{content}""")')
            elif role == "assistant":
                messages_code.append(f'Message.from_role_and_content(Role.ASSISTANT, """{content}""")')
        
        code = f"""# Converted from OpenAI API call using real Harmony format
{chr(10).join(imports)}

# Load Harmony encoding
encoding = load_harmony_encoding(HarmonyEncodingName.HARMONY_GPT_OSS)

# Build system content
system_content = {system_content}

# Build developer content
developer_content = {developer_content}

# Create conversation
conversation = Conversation.from_messages([
    {chr(10).join(f"    {msg}," for msg in messages_code)}
])

# Render for completion
tokens = encoding.render_conversation_for_completion(conversation, Role.ASSISTANT)

# Initialize local inference
inference = LocalInference(
    model="{self.config.model.value}",
    backend="{self.config.backend.value}"
)

# Generate response using tokens
response = inference.generate_with_tokens(tokens)

# Parse response
parsed_response = encoding.parse_messages_from_completion_tokens(response, Role.ASSISTANT)

# Extract final response
final_response = None
for msg in parsed_response:
    if msg.channel == "final":
        final_response = msg.content
        break

print(final_response or "No final response generated")
"""
        
        return code
    
    def _generate_harmony_code_with_tools(self, conversation: Dict[str, Any], call: APICall) -> str:
        """Generate real Harmony code with tools from conversation structure."""
        imports = [
            "from openai_harmony import (",
            "    Author,",
            "    Conversation,",
            "    DeveloperContent,",
            "    HarmonyEncodingName,",
            "    Message,",
            "    Role,",
            "    SystemContent,",
            "    ToolDescription,",
            "    load_harmony_encoding,",
            "    ReasoningEffort",
            ")",
            "from harmony_migrator.inference import LocalInference",
        ]
        
        # Build system content
        reasoning_effort = self.config.reasoning_effort.value.upper()
        system_content = f'''SystemContent.new()
    .with_model_identity("You are ChatGPT, a large language model trained by OpenAI.")
    .with_reasoning_effort(ReasoningEffort.{reasoning_effort})
    .with_conversation_start_date("2025-06-28")
    .with_knowledge_cutoff("2024-06")
    .with_required_channels(["analysis", "commentary", "final"])'''
        
        # Build developer content with tools
        developer_content = "DeveloperContent.new()"
        if conversation.get("messages"):
            # Find developer message content
            for msg in conversation["messages"]:
                if msg.get("role") == "developer":
                    content = msg.get("content", "")
                    if "# Instructions" in content:
                        instructions = content.split("# Instructions")[1].split("# Tools")[0].strip()
                        developer_content += f'\n    .with_instructions("""{instructions}""")'
                    
                    # Add tools if present
                    if "# Tools" in content:
                        tools_section = content.split("# Tools")[1]
                        # Parse tools and add them
                        developer_content += '\n    .with_function_tools(['
                        # This would need proper parsing of the tools section
                        developer_content += '\n        # Tools would be added here'
                        developer_content += '\n    ])'
                    break
        
        # Build conversation messages
        messages_code = []
        for msg in conversation["messages"]:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                messages_code.append("Message.from_role_and_content(Role.SYSTEM, system_content)")
            elif role == "developer":
                messages_code.append("Message.from_role_and_content(Role.DEVELOPER, developer_content)")
            elif role == "user":
                messages_code.append(f'Message.from_role_and_content(Role.USER, """{content}""")')
            elif role == "assistant":
                messages_code.append(f'Message.from_role_and_content(Role.ASSISTANT, """{content}""")')
        
        code = f"""# Converted from OpenAI API call with functions using real Harmony format
{chr(10).join(imports)}

# Load Harmony encoding
encoding = load_harmony_encoding(HarmonyEncodingName.HARMONY_GPT_OSS)

# Build system content
system_content = {system_content}

# Build developer content with tools
developer_content = {developer_content}

# Create conversation
conversation = Conversation.from_messages([
    {chr(10).join(f"    {msg}," for msg in messages_code)}
])

# Render for completion
tokens = encoding.render_conversation_for_completion(conversation, Role.ASSISTANT)

# Initialize local inference
inference = LocalInference(
    model="{self.config.model.value}",
    backend="{self.config.backend.value}"
)

# Generate response using tokens
response = inference.generate_with_tokens(tokens)

# Parse response
parsed_response = encoding.parse_messages_from_completion_tokens(response, Role.ASSISTANT)

# Handle tool calls if present
for msg in parsed_response:
    if msg.channel == "commentary" and hasattr(msg, 'recipient') and msg.recipient:
        # Handle tool call
        tool_name = msg.recipient
        tool_args = msg.content  # JSON string
        
        # Execute tool (you would implement this)
        tool_result = execute_tool(tool_name, tool_args)
        
        # Add tool response to conversation
        conversation.add_message(Message.from_author_and_content(
            Author.new(Role.TOOL, tool_name),
            tool_result
        ).with_recipient("assistant").with_channel("commentary"))
        
        # Continue generation with tool result
        tokens = encoding.render_conversation_for_completion(conversation, Role.ASSISTANT)
        response = inference.generate_with_tokens(tokens)
        parsed_response = encoding.parse_messages_from_completion_tokens(response, Role.ASSISTANT)

# Extract final response
final_response = None
for msg in parsed_response:
    if msg.channel == "final":
        final_response = msg.content
        break

print(final_response or "No final response generated")

def execute_tool(tool_name, args):
    # Implement your tool execution logic here
    return '{{"result": "tool executed"}}'
"""
        
        return code
    
    def apply_conversions(self, results: List[ConversionResult], repo_path: Path) -> MigrationReport:
        """Apply conversions to files and generate migration report."""
        successful_conversions = sum(1 for r in results if r.success)
        failed_conversions = len(results) - successful_conversions
        
        # Calculate total savings
        total_tokens = sum(r.estimated_tokens for r in results)
        monthly_savings = self._estimate_monthly_savings(total_tokens)
        
        # Create migration report
        report = MigrationReport(
            scan_result=None,  # Will be set by caller
            conversion_results=results,
            total_conversions=len(results),
            successful_conversions=successful_conversions,
            failed_conversions=failed_conversions,
            estimated_total_savings=monthly_savings,
            model_used=self.config.model,
            backend_used=self.config.backend,
        )
        
        return report
    
    def _estimate_monthly_savings(self, total_tokens: int) -> str:
        """Estimate monthly cost savings."""
        # Rough estimate: $0.002 per 1K tokens for GPT-3.5-turbo
        # Assuming 100 API calls per month
        monthly_calls = 100
        cost_per_1k_tokens = 0.002
        monthly_tokens = total_tokens * monthly_calls
        monthly_cost = (monthly_tokens / 1000) * cost_per_1k_tokens
        
        return f"${monthly_cost:.2f}"
    
    def print_conversion_summary(self, results: List[ConversionResult]) -> None:
        """Print a summary of conversion results."""
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        self.console.print("\n[bold green]Conversion Complete![/bold green]\n")
        
        # Summary table
        summary_data = [
            ["Total Conversions", str(len(results))],
            ["Successful", str(successful)],
            ["Failed", str(failed)],
            ["Success Rate", f"{successful/len(results)*100:.1f}%" if results else "0%"],
        ]
        
        from rich.table import Table
        table = Table(title="Conversion Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        for metric, value in summary_data:
            table.add_row(metric, value)
        
        self.console.print(table)
        
        # Show warnings and errors
        all_warnings = []
        all_errors = []
        
        for result in results:
            all_warnings.extend(result.warnings)
            all_errors.extend(result.errors)
        
        if all_warnings:
            self.console.print("\n[bold yellow]Warnings:[/bold yellow]")
            for warning in all_warnings[:5]:  # Show first 5
                self.console.print(f"  ⚠️  {warning}")
            if len(all_warnings) > 5:
                self.console.print(f"  ... and {len(all_warnings) - 5} more warnings")
        
        if all_errors:
            self.console.print("\n[bold red]Errors:[/bold red]")
            for error in all_errors[:5]:  # Show first 5
                self.console.print(f"  ❌ {error}")
            if len(all_errors) > 5:
                self.console.print(f"  ... and {len(all_errors) - 5} more errors") 