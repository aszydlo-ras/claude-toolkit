"""
Claude API Client wrapper for easy interaction with Claude AI
"""

import os
from typing import List, Dict, Optional, Any
from anthropic import Anthropic


class ClaudeClient:
    """
    A simple wrapper around the Anthropic Claude API for easier interaction.
    
    Args:
        api_key: Anthropic API key. If not provided, will look for ANTHROPIC_API_KEY env var.
        model: The Claude model to use. Defaults to "claude-3-5-sonnet-20241022".
        max_tokens: Maximum tokens in the response. Defaults to 1024.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 1024
    ):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key must be provided either as argument or via ANTHROPIC_API_KEY environment variable"
            )
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        self.max_tokens = max_tokens
    
    def send_message(
        self,
        message: str,
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 1.0,
        **kwargs
    ) -> str:
        """
        Send a single message to Claude and get a response.
        
        Args:
            message: The user message to send
            system: Optional system prompt
            max_tokens: Override the default max_tokens
            temperature: Controls randomness (0-1)
            **kwargs: Additional arguments to pass to the API
            
        Returns:
            The text response from Claude
        """
        messages = [{"role": "user", "content": message}]
        
        params = {
            "model": self.model,
            "max_tokens": max_tokens or self.max_tokens,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        
        if system:
            params["system"] = system
        
        response = self.client.messages.create(**params)
        return response.content[0].text
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 1.0,
        **kwargs
    ) -> str:
        """
        Have a multi-turn conversation with Claude.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            system: Optional system prompt
            max_tokens: Override the default max_tokens
            temperature: Controls randomness (0-1)
            **kwargs: Additional arguments to pass to the API
            
        Returns:
            The text response from Claude
        """
        params = {
            "model": self.model,
            "max_tokens": max_tokens or self.max_tokens,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        
        if system:
            params["system"] = system
        
        response = self.client.messages.create(**params)
        return response.content[0].text
    
    def stream_message(
        self,
        message: str,
        system: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 1.0,
        **kwargs
    ):
        """
        Send a message and stream the response.
        
        Args:
            message: The user message to send
            system: Optional system prompt
            max_tokens: Override the default max_tokens
            temperature: Controls randomness (0-1)
            **kwargs: Additional arguments to pass to the API
            
        Yields:
            Text chunks as they arrive from Claude
        """
        messages = [{"role": "user", "content": message}]
        
        params = {
            "model": self.model,
            "max_tokens": max_tokens or self.max_tokens,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        
        if system:
            params["system"] = system
        
        with self.client.messages.stream(**params) as stream:
            for text in stream.text_stream:
                yield text
