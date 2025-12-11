"""
Example of multi-turn conversation with Claude
"""

from claude_toolkit import ClaudeClient, format_conversation

def main():
    client = ClaudeClient()
    
    # Build a conversation
    messages = [
        {"role": "user", "content": "I'm learning Python. Can you help me?"},
    ]
    
    response1 = client.chat(messages)
    print("Claude:", response1)
    
    # Add Claude's response and continue
    messages.append({"role": "assistant", "content": response1})
    messages.append({"role": "user", "content": "What's the difference between a list and a tuple?"})
    
    response2 = client.chat(messages)
    print("\nClaude:", response2)
    
    # Print formatted conversation
    messages.append({"role": "assistant", "content": response2})
    print("\n" + "="*50)
    print("Full Conversation:")
    print("="*50)
    print(format_conversation(messages))


if __name__ == "__main__":
    main()
