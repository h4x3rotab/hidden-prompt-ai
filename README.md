# OpenAI Compatible Proxy with System Prompt Injection

A lightweight proxy server that sits between clients and the OpenAI API, automatically injecting a system prompt configured via environment variables. Perfect for monetizing custom prompts without revealing their content.

## Features

- **OpenAI Compatible**: Fully compatible with OpenAI API endpoints
- **System Prompt Injection**: Automatically injects a configured system prompt into all requests
- **User API Key**: Users provide their own OpenAI API key (developer doesn't pay for usage)
- **Docker Ready**: Easy deployment with Docker and Docker Compose
- **Streaming Support**: Supports both streaming and non-streaming responses
- **Health Checks**: Built-in health check endpoint

## Quick Start

### Using Docker Compose (Recommended)

1. Clone or download this project
2. Set your system prompt in environment variable:
   ```bash
   export SYSTEM_PROMPT="You are an expert financial advisor with 20 years of experience."
   ```

3. Run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

### Using Docker

1. Build the image:
   ```bash
   docker build -t openai-proxy .
   ```

2. Run the container:
   ```bash
   docker run -d -p 8000:8000 \
     -e SYSTEM_PROMPT="Your custom system prompt here" \
     openai-proxy
   ```

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variable:
   ```bash
   export SYSTEM_PROMPT="Your custom system prompt here"
   ```

3. Run the server:
   ```bash
   python main.py
   ```

## Usage

The proxy server runs on port 8000 and provides the following endpoints:

### Chat Completions
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_OPENAI_API_KEY" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "What is the weather like?"}
    ]
  }'
```

### List Models
```bash
curl -X GET http://localhost:8000/v1/models \
  -H "Authorization: Bearer YOUR_OPENAI_API_KEY"
```

### Health Check
```bash
curl -X GET http://localhost:8000/health
```

## How It Works

1. **System Prompt Injection**: The configured `SYSTEM_PROMPT` is automatically injected as the first message in every chat completion request
2. **API Key Passthrough**: Users provide their own OpenAI API key in the Authorization header
3. **Transparent Proxy**: All other parameters and responses are passed through unchanged
4. **Prompt Protection**: The actual system prompt is never exposed to users

## Configuration

### Environment Variables

- `SYSTEM_PROMPT`: The system prompt to inject into all requests (required)

### Example System Prompts

```bash
# Simple assistant
SYSTEM_PROMPT="You are a helpful assistant that always responds professionally."

# Expert advisor
SYSTEM_PROMPT="You are an expert financial advisor with 20 years of experience. Provide detailed analysis and actionable recommendations."

# Creative writer
SYSTEM_PROMPT="You are a professional creative writer specializing in storytelling. Always structure your responses with vivid descriptions and engaging narratives."
```

## Monetization Use Cases

This proxy is perfect for:

- **Prompt Engineering Services**: Sell access to your optimized prompts
- **Specialized AI Assistants**: Create domain-specific AI assistants
- **API White-labeling**: Provide custom AI services under your brand
- **Consultation Services**: Offer AI-powered consultation with custom expertise

## API Compatibility

The proxy is fully compatible with OpenAI's API, supporting:

- Chat completions (streaming and non-streaming)
- Model listing
- All standard parameters (temperature, max_tokens, etc.)
- Error handling and status codes

## Security Considerations

- Users provide their own API keys (no key sharing)
- System prompt is never exposed to users
- Built-in health checks for monitoring
- Runs as non-root user in Docker

## Deployment

### Production Deployment

For production use, consider:

1. **Environment Variables**: Use Docker secrets or environment variable management
2. **Load Balancing**: Deploy multiple instances behind a load balancer
3. **Monitoring**: Set up monitoring and alerting for the health check endpoint
4. **HTTPS**: Use a reverse proxy (nginx, Cloudflare) for HTTPS termination

### Scaling

The proxy is stateless and can be easily scaled horizontally:

```bash
docker-compose up -d --scale openai-proxy=3
```

## License

This project is provided as-is for educational and commercial use.