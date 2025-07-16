# Hidden Prompt AI

A lightweight proxy server that sits between clients and the OpenAI API, automatically injecting a system prompt configured via environment variables. Perfect for monetizing custom prompts without revealing their content.

## Features

- **Full OpenAI API Compatibility**: Supports both chat completions and text completions
- **System Prompt Injection**: Automatically injects a configured system prompt into all requests
- **User API Key**: Users provide their own OpenAI API key (developer doesn't pay for usage)
- **Docker Ready**: Easy deployment with pre-built Docker image
- **Streaming Support**: Supports both streaming and non-streaming responses
- **Self-contained Testing**: Comprehensive test suite validates all functionality

## Quick Start

### Using Pre-built Docker Image (Fastest)

```bash
docker run -d -p 8000:8000 \
  -e SYSTEM_PROMPT="You are an expert financial advisor with 20 years of experience." \
  h4x3rotab/llm-sandbox:latest
```

### Local Development

```bash
pip install -r requirements.txt
export SYSTEM_PROMPT="Your custom system prompt here"
python main.py
```

## API Endpoints

### Chat Completions
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_OPENAI_API_KEY" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": true
  }'
```

### Text Completions
```bash
curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_OPENAI_API_KEY" \
  -d '{
    "model": "gpt-3.5-turbo-instruct",
    "prompt": "Once upon a time",
    "max_tokens": 100
  }'
```

### Other Endpoints
- `GET /v1/models` - List available models
- `GET /health` - Health check

## How It Works

1. **System Prompt Injection**: 
   - **Chat Completions**: Injected as first system message
   - **Text Completions**: Prepended to user's prompt
2. **API Key Passthrough**: Users provide their own OpenAI API key
3. **Transparent Proxy**: All other parameters passed through unchanged
4. **Prompt Protection**: System prompt never exposed to users

## Configuration

Set your system prompt via environment variable:

```bash
# Expert advisor
SYSTEM_PROMPT="You are an expert financial advisor with 20 years of experience."

# Code reviewer  
SYSTEM_PROMPT="You are a senior software engineer specializing in code reviews."

# Creative writer
SYSTEM_PROMPT="You are a professional creative writer specializing in storytelling."
```

## Testing

Run the comprehensive test suite:

```bash
export OPENAI_API_KEY=your_key_here
python test_proxy.py
```

The test suite automatically starts the server, tests all endpoints, validates streaming and system prompt injection, then stops the server.

## Monetization Use Cases

- **Prompt Engineering Services**: Sell access to optimized prompts
- **Specialized AI Assistants**: Create domain-specific AI assistants  
- **API White-labeling**: Provide custom AI services under your brand
- **Educational Tools**: Create subject-specific AI tutors

## Deployment

### Production
```bash
# Pull and run
docker pull h4x3rotab/llm-sandbox:latest
docker run -d -p 8000:8000 -e SYSTEM_PROMPT="Your prompt" h4x3rotab/llm-sandbox:latest

# Scale horizontally
docker-compose up -d --scale openai-proxy=3
```

### Security
- Users provide their own API keys (no key sharing)
- System prompt never exposed to users
- Runs as non-root user in Docker
- Stateless architecture

## Development

```
├── main.py              # Main proxy server
├── test_proxy.py        # Comprehensive test suite  
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container configuration
├── docker-compose.yml  # Docker Compose setup
└── README.md           # This file
```

Run tests before contributing: `python test_proxy.py`

## License

This project is provided as-is for educational and commercial use.