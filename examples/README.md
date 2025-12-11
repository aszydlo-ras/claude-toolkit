# Examples

This directory contains example scripts demonstrating how to use the Claude Toolkit.

## Prerequisites

Before running any examples, make sure you have:

1. Installed the toolkit:
   ```bash
   pip install -e ..
   ```

2. Set your Anthropic API key:
   ```bash
   export ANTHROPIC_API_KEY='your-api-key-here'
   ```
   
   Or copy `.env.example` to `.env` and add your key there.

## Available Examples

### basic_usage.py
Demonstrates simple message sending with and without system prompts.

```bash
python basic_usage.py
```

### conversation.py
Shows how to maintain multi-turn conversations with Claude.

```bash
python conversation.py
```

### streaming.py
Demonstrates streaming responses for real-time output.

```bash
python streaming.py
```

### code_extraction.py
Shows how to extract and parse code blocks from Claude's responses.

```bash
python code_extraction.py
```

## Running Examples

From the examples directory:

```bash
cd examples
python basic_usage.py
```

Or from the root directory:

```bash
python examples/basic_usage.py
```
