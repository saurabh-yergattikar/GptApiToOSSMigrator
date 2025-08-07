#!/usr/bin/env python3
"""
Sample OpenAI application for testing HarmonyMigrator.

This file contains various OpenAI API calls that can be detected
and converted by the HarmonyMigrator tool.
"""

import openai
import os

# Set up OpenAI API key (for demonstration)
os.environ["OPENAI_API_KEY"] = "sk-demo-key"

def simple_chat():
    """Simple chat completion example."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! How are you?"}
        ]
    )
    return response.choices[0].message.content

def chat_with_functions():
    """Chat completion with function calling."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "What's the weather in New York?"}
        ],
        functions=[
            {
                "name": "get_weather",
                "description": "Get weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "The city and state"}
                    },
                    "required": ["location"]
                }
            }
        ]
    )
    return response

def completion_example():
    """Text completion example."""
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Complete this sentence: The future of AI is",
        max_tokens=50
    )
    return response.choices[0].text

def embedding_example():
    """Embedding example."""
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input="Hello world"
    )
    return response.data[0].embedding

def complex_chat():
    """More complex chat completion."""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert Python developer."},
            {"role": "user", "content": "Write a function to calculate fibonacci numbers."}
        ],
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    print("Simple chat:", simple_chat())
    print("Chat with functions:", chat_with_functions())
    print("Completion:", completion_example())
    print("Embedding:", embedding_example())
    print("Complex chat:", complex_chat()) 