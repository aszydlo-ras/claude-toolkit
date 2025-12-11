"""
Example of streaming responses from Claude
"""

from claude_toolkit import ClaudeClient

def main():
    client = ClaudeClient()
    
    print("Claude: ", end="", flush=True)
    
    # Stream the response
    for chunk in client.stream_message("Tell me a short story about a robot learning to paint."):
        print(chunk, end="", flush=True)
    
    print("\n")


if __name__ == "__main__":
    main()
