#!/usr/bin/env python3
"""Simple test without external dependencies."""

import re

def test_migration():
    """Test the migration functionality."""
    
    # Original code (your example)
    original_code = '''# business.py
def should_refund(sentiment: str) -> bool:
    return sentiment == "negative"  # <- your rule stays the same

# app_legacy.py
from openai import OpenAI
from business import should_refund

client = OpenAI()

def handle_ticket(text: str):
    # ask model to classify
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Reply with only: positive, neutral, or negative."},
            {"role": "user", "content": f"Classify sentiment: {text}"}
        ],
        temperature=0
    )
    sentiment = resp.choices[0].message["content"].strip().lower()

    # ✅ business logic unchanged
    return {
        "sentiment": sentiment,
        "refund": should_refund(sentiment)
    }
'''
    
    print("🚀 Testing GptApiToOSSMigrator Migration")
    print("=" * 50)
    
    # Test migration
    supported_patterns = [
        "openai.ChatCompletion.create",
        "client.chat.completions.create",
    ]
    
    can_migrate = any(pattern in original_code for pattern in supported_patterns)
    
    print("📝 Original Code:")
    print("-" * 30)
    print(original_code)
    
    if can_migrate:
        print("\n✅ Code can be migrated!")
        
        # Simple migration
        migrated_code = original_code
        
        # Replace OpenAI client initialization
        if "from openai import OpenAI" in migrated_code:
            migrated_code = re.sub(
                r"client = OpenAI\(\)",
                'client = OpenAI(api_key="EMPTY", base_url="http://localhost:8000/v1")',
                migrated_code
            )
        
        # Replace model name
        migrated_code = re.sub(
            r'model="gpt-[^"]*"',
            'model="gpt-oss-20b"',
            migrated_code
        )
        
        print("\n📝 Migration Results:")
        print("=" * 30)
        print("✅ Updated client initialization for local server")
        print("✅ Changed model to gpt-oss-20b")
        
        print("\n⚠️  Warnings:")
        print("  - Manual response parsing required for Harmony format")
        print("  - Verify local server is running on localhost:8000")
        
        print("\n🔄 Migrated Code:")
        print("-" * 30)
        print(migrated_code)
        
        print("\n🔧 Response Parser Code:")
        print("-" * 30)
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
        print(parser_code)
        
        print("\n📋 Summary:")
        print("=" * 30)
        print("✅ Client initialization updated for local server")
        print("✅ Model changed to gpt-oss-20b")
        print("⚠️  Manual response parsing required")
        print("⚠️  Local server setup needed")
        print("\n🎯 Business logic remains unchanged!")
        
    else:
        print("❌ Code cannot be migrated with current version")

if __name__ == "__main__":
    test_migration() 