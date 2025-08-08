"""Basic migrator for OpenAI to local models."""

import ast
import re
from typing import Dict, List, Optional

from pydantic import BaseModel


class MigrationResult(BaseModel):
    """Result of a migration operation."""
    original_code: str
    migrated_code: str
    changes_made: List[str]
    warnings: List[str]


class BasicMigrator:
    """Basic migrator for OpenAI chat completions."""
    
    def __init__(self):
        self.supported_patterns = [
            "openai.ChatCompletion.create",
            "client.chat.completions.create",
        ]
    
    def can_migrate(self, code: str) -> bool:
        """Check if the code can be migrated."""
        for pattern in self.supported_patterns:
            if pattern in code:
                return True
        return False
    
    def migrate_chat_completion(self, code: str) -> MigrationResult:
        """Migrate a chat completion to local model."""
        warnings = []
        changes = []
        
        # Simple pattern replacement (this is basic - would need more sophisticated parsing)
        migrated_code = code
        
        # Replace OpenAI client initialization
        if "from openai import OpenAI" in code:
            migrated_code = re.sub(
                r"client = OpenAI\(\)",
                'client = OpenAI(api_key="EMPTY", base_url="http://localhost:8000/v1")',
                migrated_code
            )
            changes.append("Updated client initialization for local server")
        
        # Replace model name
        migrated_code = re.sub(
            r'model="gpt-[^"]*"',
            'model="gpt-oss-20b"',
            migrated_code
        )
        changes.append("Updated model to gpt-oss-20b")
        
        # Add warning about response parsing
        warnings.append("Manual response parsing required for Harmony format")
        warnings.append("Verify local server is running on localhost:8000")
        
        return MigrationResult(
            original_code=code,
            migrated_code=migrated_code,
            changes_made=changes,
            warnings=warnings
        )
    
    def generate_response_parser(self, original_code: str) -> str:
        """Generate code to parse Harmony response format."""
        parser_code = '''
# Add this after your API call to parse Harmony response
sentiment = None
for item in resp.output:
    if item["type"] == "message":
        for part in item["content"]:
            if part.get("type") == "output_text" and part.get("channel") == "final":
                sentiment = part["text"].strip().lower()
                break
'''
        return parser_code 