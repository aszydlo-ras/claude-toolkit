# Claude Toolkit

A Python toolkit for easy interaction with Anthropic's Claude AI API. This library provides a simple and intuitive interface for working with Claude, including single messages, multi-turn conversations, and streaming responses.

## Features

- 🚀 Simple and intuitive API wrapper for Claude
- 💬 Support for single messages and multi-turn conversations
- 🌊 Streaming response support
- 🛠️ Utility functions for formatting and parsing responses
- 📝 Code block extraction from responses
- 🎯 Type hints for better IDE support

## Installation

### From source

```bash
git clone https://github.com/aszydlo-ras/claude-toolkit.git
cd claude-toolkit
pip install -e .
```

### Using pip (when published)

```bash
pip install claude-toolkit
```

## Requirements

- Python 3.8+
- An Anthropic API key (get one at https://www.anthropic.com/)

## Quick Start

### Setting up your API key

Set your Anthropic API key as an environment variable:

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

Or create a `.env` file:

```
ANTHROPIC_API_KEY=your-api-key-here
```

### Basic Usage

```python
from claude_toolkit import ClaudeClient

# Initialize the client
client = ClaudeClient()

# Send a simple message
response = client.send_message("Hello! What can you help me with today?")
print(response)
```

### With System Prompt

```python
response = client.send_message(
    "Write a haiku about coding",
    system="You are a poetic assistant who loves programming"
)
print(response)
```

### Multi-turn Conversation

```python
from claude_toolkit import ClaudeClient, format_conversation

client = ClaudeClient()

messages = [
    {"role": "user", "content": "I'm learning Python. Can you help me?"}
]

response = client.chat(messages)
messages.append({"role": "assistant", "content": response})
messages.append({"role": "user", "content": "What's the difference between a list and a tuple?"})

response = client.chat(messages)
print(response)
```

### Streaming Responses

```python
client = ClaudeClient()

for chunk in client.stream_message("Tell me a story about a robot."):
    print(chunk, end="", flush=True)
```

### Extracting Code Blocks

```python
from claude_toolkit import extract_code_blocks

response = client.send_message("Write a Python function to calculate fibonacci numbers")
code_blocks = extract_code_blocks(response, language="python")

for language, code in code_blocks:
    print(f"Language: {language}")
    print(code)
```

## API Reference

### ClaudeClient

The main client for interacting with Claude.

#### Constructor

```python
ClaudeClient(
    api_key: Optional[str] = None,
    model: str = "claude-3-5-sonnet-20241022",
    max_tokens: int = 1024
)
```

- `api_key`: Your Anthropic API key (or set `ANTHROPIC_API_KEY` env var)
- `model`: The Claude model to use
- `max_tokens`: Maximum tokens in responses

#### Methods

##### send_message()

Send a single message to Claude.

```python
send_message(
    message: str,
    system: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: float = 1.0,
    **kwargs
) -> str
```

##### chat()

Have a multi-turn conversation.

```python
chat(
    messages: List[Dict[str, str]],
    system: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: float = 1.0,
    **kwargs
) -> str
```

##### stream_message()

Stream a response from Claude.

```python
stream_message(
    message: str,
    system: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: float = 1.0,
    **kwargs
) -> Iterator[str]
```

### Utility Functions

#### format_conversation()

Format a conversation history into a readable string.

```python
format_conversation(messages: List[Dict[str, str]]) -> str
```

#### extract_code_blocks()

Extract code blocks from markdown-formatted text.

```python
extract_code_blocks(text: str, language: str = None) -> List[Tuple[str, str]]
```

#### count_tokens_estimate()

Get a rough estimate of token count.

```python
count_tokens_estimate(text: str) -> int
```

#### truncate_text()

Truncate text to fit within a token limit.

```python
truncate_text(text: str, max_tokens: int = 1000) -> str
```

## Examples

Check out the `examples/` directory for more usage examples:

- `basic_usage.py` - Simple message sending
- `conversation.py` - Multi-turn conversations
- `streaming.py` - Streaming responses
- `code_extraction.py` - Extracting code from responses

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

Built on top of the official [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python).