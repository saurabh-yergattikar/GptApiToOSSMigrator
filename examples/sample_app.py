"""Sample application with OpenAI API calls."""

import os
import openai

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY", "your-api-key")

def simple_chat():
    """Simple chat completion."""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! How are you?"}
        ]
    )
    return response.choices[0].message.content

def complex_chat():
    """Complex chat with function calling."""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a weather expert."},
            {"role": "user", "content": "What's the weather like?"}
        ],
        functions=[{
            "name": "get_weather",
            "description": "Get the current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name"
                    }
                }
            }
        }]
    )
    return response.choices[0].message.content

def get_embedding(text):
    """Get text embedding."""
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def complete_text(prompt):
    """Text completion."""
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=100
    )
    return response.choices[0].text

if __name__ == "__main__":
    # Test the functions
    print("Chat:", simple_chat())
    print("Complex:", complex_chat())
    print("Embedding:", get_embedding("Hello world")[:5])
    print("Completion:", complete_text("Once upon a time"))