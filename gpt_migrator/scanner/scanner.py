"""Scanner module for detecting OpenAI API calls."""

import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel


class APICall(BaseModel):
    """Represents a detected OpenAI API call."""
    file: str
    line: int
    type: str  # 'chat', 'completion', 'embedding', etc.
    model: Optional[str] = None
    estimated_tokens: Optional[int] = None
    complexity: str = "simple"  # 'simple', 'medium', 'complex'

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "file": self.file,
            "line": self.line,
            "type": self.type,
            "model": self.model,
            "estimated_tokens": self.estimated_tokens,
            "complexity": self.complexity,
        }


class Scanner:
    """Scanner for detecting OpenAI API calls in code."""
    
    def __init__(self):
        self.api_calls: List[APICall] = []
    
    def scan_file(self, file_path: str) -> List[APICall]:
        """Scan a single file for OpenAI API calls."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Try AST parsing first
            try:
                tree = ast.parse(content)
                visitor = OpenAIVisitor(file_path)
                visitor.visit(tree)
                self.api_calls.extend(visitor.api_calls)
            except SyntaxError:
                # Fallback to regex if not valid Python
                self._scan_with_regex(file_path, content)
            
            return self.api_calls
        except Exception as e:
            print(f"Error scanning {file_path}: {str(e)}")
            return []
    
    def scan_directory(self, directory: str) -> List[APICall]:
        """Scan a directory recursively for OpenAI API calls."""
        path = Path(directory)
        for file in path.rglob("*"):
            if file.is_file() and file.suffix in ['.py', '.js', '.ts']:
                self.scan_file(str(file))
        return self.api_calls
    
    def _scan_with_regex(self, file_path: str, content: str):
        """Scan using regex patterns."""
        patterns = [
            (r'openai\.ChatCompletion\.create\(', 'chat'),
            (r'openai\.Completion\.create\(', 'completion'),
            (r'openai\.Embedding\.create\(', 'embedding'),
        ]
        
        for line_num, line in enumerate(content.split('\n'), 1):
            for pattern, call_type in patterns:
                if re.search(pattern, line):
                    self.api_calls.append(
                        APICall(
                            file=file_path,
                            line=line_num,
                            type=call_type,
                            complexity=self._estimate_complexity(line)
                        )
                    )
    
    def _estimate_complexity(self, line: str) -> str:
        """Estimate the complexity of an API call."""
        if 'functions' in line or 'function_call' in line:
            return 'complex'
        if 'messages' in line or 'prompt' in line:
            return 'medium'
        return 'simple'


class OpenAIVisitor(ast.NodeVisitor):
    """AST visitor for detecting OpenAI API calls."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.api_calls: List[APICall] = []
    
    def visit_Call(self, node: ast.Call):
        """Visit a function call node."""
        # Check for openai.XXX.create() patterns
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Attribute):
            if hasattr(node.func.value.value, 'id') and node.func.value.value.id == 'openai':
                service = node.func.value.attr
                method = node.func.attr
                
                if method == 'create':
                    call_type = self._get_call_type(service)
                    if call_type:
                        self.api_calls.append(
                            APICall(
                                file=self.file_path,
                                line=node.lineno,
                                type=call_type,
                                model=self._extract_model(node),
                                complexity=self._estimate_complexity(node)
                            )
                        )
        
        self.generic_visit(node)
    
    def _get_call_type(self, service: str) -> Optional[str]:
        """Get the type of API call from the service name."""
        mapping = {
            'ChatCompletion': 'chat',
            'Completion': 'completion',
            'Embedding': 'embedding',
        }
        return mapping.get(service)
    
    def _extract_model(self, node: ast.Call) -> Optional[str]:
        """Extract the model name from the API call."""
        for kw in node.keywords:
            if kw.arg == 'model' and isinstance(kw.value, ast.Str):
                return kw.value.s
        return None
    
    def _estimate_complexity(self, node: ast.Call) -> str:
        """Estimate the complexity of an API call from its AST."""
        has_functions = False
        has_messages = False
        
        for kw in node.keywords:
            if kw.arg == 'functions':
                has_functions = True
            elif kw.arg == 'messages' or kw.arg == 'prompt':
                has_messages = True
        
        if has_functions:
            return 'complex'
        if has_messages:
            return 'medium'
        return 'simple'