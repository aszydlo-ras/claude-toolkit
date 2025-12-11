"""
Basic usage example for Claude Toolkit
"""

import os
from claude_toolkit import ClaudeClient

# Make sure to set ANTHROPIC_API_KEY environment variable
# or pass api_key directly to ClaudeClient

def main():
    # Initialize the client
    client = ClaudeClient()
    
    # Send a simple message
    response = client.send_message("Hello! What can you help me with today?")
    print("Claude:", response)
    
    # Send a message with a system prompt
    response = client.send_message(
        "Write a haiku about coding",
        system="You are a poetic assistant who loves programming"
    )
    print("\nClaude:", response)


if __name__ == "__main__":
    main()
