"""
Example of extracting code blocks from Claude's responses
"""

from claude_toolkit import ClaudeClient, extract_code_blocks

def main():
    client = ClaudeClient()
    
    # Ask Claude to write some code
    response = client.send_message(
        "Write a Python function to calculate the fibonacci sequence"
    )
    
    print("Full response:")
    print(response)
    print("\n" + "="*50)
    
    # Extract code blocks
    code_blocks = extract_code_blocks(response)
    
    print(f"\nFound {len(code_blocks)} code block(s):")
    for i, (language, code) in enumerate(code_blocks, 1):
        print(f"\nCode block {i} ({language}):")
        print("-" * 40)
        print(code)


if __name__ == "__main__":
    main()
