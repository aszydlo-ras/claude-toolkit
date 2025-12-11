"""
Utility functions for working with Claude responses
"""

import re
from typing import List, Dict, Tuple


def format_conversation(messages: List[Dict[str, str]]) -> str:
    """
    Format a conversation history into a readable string.
    
    Args:
        messages: List of message dicts with 'role' and 'content' keys
        
    Returns:
        Formatted conversation string
    """
    formatted = []
    for msg in messages:
        role = msg.get("role", "unknown").upper()
        content = msg.get("content", "")
        formatted.append(f"{role}: {content}")
    
    return "\n\n".join(formatted)


def extract_code_blocks(text: str, language: str = None) -> List[Tuple[str, str]]:
    """
    Extract code blocks from markdown-formatted text.
    
    Args:
        text: The text containing markdown code blocks
        language: Optional language filter (e.g., 'python', 'javascript')
        
    Returns:
        List of tuples (language, code) for each code block found
    """
    # Pattern to match markdown code blocks (with optional language and newline)
    pattern = r"```(\w*)\n?(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    
    code_blocks = [(lang or "unknown", code.strip()) for lang, code in matches]
    
    if language:
        code_blocks = [(lang, code) for lang, code in code_blocks if lang == language]
    
    return code_blocks


def count_tokens_estimate(text: str) -> int:
    """
    Provide a rough estimate of token count for a given text.
    This is a simple approximation: ~4 characters per token.
    
    Note: This is a very rough approximation and actual token counts
    may vary significantly. For accurate token counting, use the
    official Anthropic tokenizer.
    
    Args:
        text: The text to estimate tokens for
        
    Returns:
        Estimated token count (approximate)
    """
    return len(text) // 4


def truncate_text(text: str, max_tokens: int = 1000) -> str:
    """
    Truncate text to approximately fit within a token limit.
    
    Args:
        text: The text to truncate
        max_tokens: Maximum number of tokens (approximate)
        
    Returns:
        Truncated text
    """
    max_chars = max_tokens * 4
    if len(text) <= max_chars:
        return text
    
    return text[:max_chars] + "..."
