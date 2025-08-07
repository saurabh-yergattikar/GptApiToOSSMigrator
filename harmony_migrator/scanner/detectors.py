"""Detectors for finding OpenAI API calls in different programming languages."""

import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.models import APICall, CallType, ComplexityLevel


class BaseDetector:
    """Base class for API call detectors."""
    
    def detect_calls(self, content: str, file_path: Path) -> List[APICall]:
        """Detect API calls in file content."""
        raise NotImplementedError


class PythonDetector(BaseDetector):
    """Detector for Python files."""
    
    def detect_calls(self, content: str, file_path: Path) -> List[APICall]:
        """Detect OpenAI API calls in Python code."""
        calls = []
        
        try:
            tree = ast.parse(content)
            visitor = PythonAPIVisitor(file_path)
            visitor.visit(tree)
            calls = visitor.calls
        except SyntaxError:
            # If AST parsing fails, fall back to regex
            calls = self._detect_with_regex(content, file_path)
        
        return calls
    
    def _detect_with_regex(self, content: str, file_path: Path) -> List[APICall]:
        """Fallback regex detection for Python files."""
        calls = []
        lines = content.split('\n')
        
        # Patterns for OpenAI API calls
        patterns = [
            (r'openai\.ChatCompletion\.create\s*\(', CallType.CHAT_COMPLETION),
            (r'openai\.Completion\.create\s*\(', CallType.COMPLETION),
            (r'openai\.Embedding\.create\s*\(', CallType.EMBEDDING),
            (r'openai\.FineTune\.create\s*\(', CallType.FINE_TUNE),
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern, call_type in patterns:
                if re.search(pattern, line):
                    # Extract the function call
                    match = re.search(r'openai\.[^)]+\)', line)
                    if match:
                        code_snippet = match.group(0)
                        calls.append(APICall(
                            file_path=file_path,
                            line_number=line_num,
                            call_type=call_type,
                            complexity=ComplexityLevel.SIMPLE,
                            estimated_tokens=100,  # Default estimate
                            code_snippet=code_snippet,
                            parameters={},
                            functions=[],
                        ))
        
        return calls


class JavaScriptDetector(BaseDetector):
    """Detector for JavaScript/TypeScript files."""
    
    def detect_calls(self, content: str, file_path: Path) -> List[APICall]:
        """Detect OpenAI API calls in JavaScript/TypeScript code."""
        calls = []
        lines = content.split('\n')
        
        # Patterns for OpenAI API calls in JS/TS
        patterns = [
            (r'openai\.createChatCompletion\s*\(', CallType.CHAT_COMPLETION),
            (r'openai\.createCompletion\s*\(', CallType.COMPLETION),
            (r'openai\.createEmbedding\s*\(', CallType.EMBEDDING),
            (r'openai\.createFineTune\s*\(', CallType.FINE_TUNE),
            # Also detect fetch calls to OpenAI API
            (r'fetch\s*\(\s*["\']https://api\.openai\.com', CallType.CHAT_COMPLETION),
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern, call_type in patterns:
                if re.search(pattern, line):
                    # Extract the function call
                    match = re.search(r'openai\.[^)]+\)', line)
                    if match:
                        code_snippet = match.group(0)
                    else:
                        # For fetch calls, get the full line
                        code_snippet = line.strip()
                    
                    calls.append(APICall(
                        file_path=file_path,
                        line_number=line_num,
                        call_type=call_type,
                        complexity=ComplexityLevel.SIMPLE,
                        estimated_tokens=100,  # Default estimate
                        code_snippet=code_snippet,
                        parameters={},
                        functions=[],
                    ))
        
        return calls


class PythonAPIVisitor(ast.NodeVisitor):
    """AST visitor for detecting OpenAI API calls in Python."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.calls = []
    
    def visit_Call(self, node: ast.Call) -> None:
        """Visit function call nodes."""
        # Check if this is an OpenAI API call
        if isinstance(node.func, ast.Attribute):
            # Check for openai.ChatCompletion.create
            if (isinstance(node.func.value, ast.Attribute) and
                isinstance(node.func.value.value, ast.Name) and
                node.func.value.value.id == 'openai' and
                node.func.value.attr == 'ChatCompletion' and
                node.func.attr == 'create'):
                
                self._process_chat_completion(node)
            
            # Check for openai.Completion.create
            elif (isinstance(node.func.value, ast.Attribute) and
                  isinstance(node.func.value.value, ast.Name) and
                  node.func.value.value.id == 'openai' and
                  node.func.value.attr == 'Completion' and
                  node.func.attr == 'create'):
                
                self._process_completion(node)
            
            # Check for openai.Embedding.create
            elif (isinstance(node.func.value, ast.Attribute) and
                  isinstance(node.func.value.value, ast.Name) and
                  node.func.value.value.id == 'openai' and
                  node.func.value.attr == 'Embedding' and
                  node.func.attr == 'create'):
                
                self._process_embedding(node)
        
        self.generic_visit(node)
    
    def _process_chat_completion(self, node: ast.Call) -> None:
        """Process a ChatCompletion API call."""
        parameters = self._extract_parameters(node)
        functions = self._extract_functions(parameters)
        
        # Determine complexity
        complexity = ComplexityLevel.SIMPLE
        if functions:
            complexity = ComplexityLevel.MEDIUM
        if len(parameters) > 5:
            complexity = ComplexityLevel.COMPLEX
        
        # Estimate tokens
        estimated_tokens = self._estimate_tokens(parameters)
        
        calls = []
        if functions:
            # Split into separate calls for each function
            for func in functions:
                calls.append(APICall(
                    file_path=self.file_path,
                    line_number=node.lineno,
                    call_type=CallType.FUNCTION_CALL,
                    complexity=complexity,
                    estimated_tokens=estimated_tokens,
                    code_snippet=self._get_code_snippet(node),
                    parameters=parameters,
                    functions=[func],
                ))
        else:
            calls.append(APICall(
                file_path=self.file_path,
                line_number=node.lineno,
                call_type=CallType.CHAT_COMPLETION,
                complexity=complexity,
                estimated_tokens=estimated_tokens,
                code_snippet=self._get_code_snippet(node),
                parameters=parameters,
                functions=[],
            ))
        
        self.calls.extend(calls)
    
    def _process_completion(self, node: ast.Call) -> None:
        """Process a Completion API call."""
        parameters = self._extract_parameters(node)
        estimated_tokens = self._estimate_tokens(parameters)
        
        self.calls.append(APICall(
            file_path=self.file_path,
            line_number=node.lineno,
            call_type=CallType.COMPLETION,
            complexity=ComplexityLevel.SIMPLE,
            estimated_tokens=estimated_tokens,
            code_snippet=self._get_code_snippet(node),
            parameters=parameters,
            functions=[],
        ))
    
    def _process_embedding(self, node: ast.Call) -> None:
        """Process an Embedding API call."""
        parameters = self._extract_parameters(node)
        estimated_tokens = self._estimate_tokens(parameters)
        
        self.calls.append(APICall(
            file_path=self.file_path,
            line_number=node.lineno,
            call_type=CallType.EMBEDDING,
            complexity=ComplexityLevel.SIMPLE,
            estimated_tokens=estimated_tokens,
            code_snippet=self._get_code_snippet(node),
            parameters=parameters,
            functions=[],
        ))
    
    def _extract_parameters(self, node: ast.Call) -> Dict[str, Any]:
        """Extract parameters from a function call."""
        parameters = {}
        
        for keyword in node.keywords:
            if keyword.arg:
                parameters[keyword.arg] = self._extract_value(keyword.value)
        
        return parameters
    
    def _extract_value(self, node: ast.AST) -> Any:
        """Extract a value from an AST node."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.List):
            return [self._extract_value(item) for item in node.elts]
        elif isinstance(node, ast.Dict):
            return {
                self._extract_value(k): self._extract_value(v)
                for k, v in zip(node.keys, node.values)
            }
        elif isinstance(node, ast.Name):
            return f"<variable:{node.id}>"
        else:
            return "<complex_expression>"
    
    def _extract_functions(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract function definitions from parameters."""
        functions = parameters.get('functions', [])
        if isinstance(functions, list):
            return functions
        return []
    
    def _estimate_tokens(self, parameters: Dict[str, Any]) -> int:
        """Estimate token count based on parameters."""
        total_tokens = 0
        
        # Count tokens in messages
        messages = parameters.get('messages', [])
        for message in messages:
            if isinstance(message, dict):
                content = message.get('content', '')
                if isinstance(content, str):
                    total_tokens += len(content.split()) * 1.3  # Rough estimate
        
        # Count tokens in prompt
        prompt = parameters.get('prompt', '')
        if isinstance(prompt, str):
            total_tokens += len(prompt.split()) * 1.3
        
        # Add overhead for API call
        total_tokens += 50
        
        return max(total_tokens, 100)  # Minimum estimate
    
    def _get_code_snippet(self, node: ast.Call) -> str:
        """Get the code snippet for a function call."""
        # This is a simplified version - in practice, you'd need to
        # reconstruct the original code from the AST
        return f"openai.{self._get_call_name(node)}.create(...)"
    
    def _get_call_name(self, node: ast.Call) -> str:
        """Get the name of the API call."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Attribute):
                return node.func.value.attr
        return "Unknown" 