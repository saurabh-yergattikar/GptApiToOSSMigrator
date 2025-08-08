#!/usr/bin/env python3
"""Test script to demonstrate migration functionality."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from harmony_migrator.migrator.basic_migrator import BasicMigrator

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
    
    print("🚀 Testing HarmonyMigrator Migration")
    print("=" * 50)
    
    # Test migration
    migrator = BasicMigrator()
    
    print("📝 Original Code:")
    print("-" * 30)
    print(original_code)
    
    if migrator.can_migrate(original_code):
        print("\n✅ Code can be migrated!")
        
        result = migrator.migrate_chat_completion(original_code)
        
        print("\n📝 Migration Results:")
        print("=" * 30)
        
        for change in result.changes_made:
            print(f"✅ {change}")
        
        if result.warnings:
            print("\n⚠️  Warnings:")
            for warning in result.warnings:
                print(f"  - {warning}")
        
        print("\n🔄 Migrated Code:")
        print("-" * 30)
        print(result.migrated_code)
        
        print("\n🔧 Response Parser Code:")
        print("-" * 30)
        print(migrator.generate_response_parser(original_code))
        
        print("\n📋 Summary:")
        print("=" * 30)
        print("✅ Client initialization updated for local server")
        print("✅ Model changed to gpt-oss-20b")
        print("⚠️  Manual response parsing required")
        print("⚠️  Local server setup needed")
        
    else:
        print("❌ Code cannot be migrated with current version")

if __name__ == "__main__":
    test_migration() 