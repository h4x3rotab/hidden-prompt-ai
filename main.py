import os
import json
import httpx
from typing import Optional, Dict, List
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="OpenAI Compatible Proxy with System Prompt Injection")

OPENAI_BASE_URL = "https://api.openai.com/v1"
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "")

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    stop: Optional[List[str]] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None

def inject_system_prompt(messages: List[ChatMessage]) -> List[ChatMessage]:
    """Inject system prompt as the first message if SYSTEM_PROMPT is set"""
    if not SYSTEM_PROMPT:
        return messages
    
    # Check if there's already a system message
    has_system_message = any(msg.role == "system" for msg in messages)
    
    if has_system_message:
        # Replace existing system message with our injected one
        modified_messages = []
        for msg in messages:
            if msg.role == "system":
                modified_messages.append(ChatMessage(role="system", content=SYSTEM_PROMPT))
            else:
                modified_messages.append(msg)
        return modified_messages
    else:
        # Add system message at the beginning
        return [ChatMessage(role="system", content=SYSTEM_PROMPT)] + messages

async def forward_to_openai(request_data: dict, api_key: str, endpoint: str, stream: bool = False, method: str = "POST"):
    """Forward request to OpenAI API"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    url = f"{OPENAI_BASE_URL}/{endpoint}"
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        if method == "GET":
            response = await client.get(url, headers=headers)
        elif stream:
            response = await client.post(url, json=request_data, headers=headers, stream=True)
        else:
            response = await client.post(url, json=request_data, headers=headers)
        
        if response.status_code != 200:
            error_content = await response.aread() if stream else response.content
            raise HTTPException(
                status_code=response.status_code,
                detail=json.loads(error_content.decode()) if error_content else "OpenAI API Error"
            )
        
        return response

@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    authorization: str = Header(None)
):
    """OpenAI-compatible chat completions endpoint with system prompt injection"""
    
    # Extract API key from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    api_key = authorization.replace("Bearer ", "")
    
    # Inject system prompt
    modified_messages = inject_system_prompt(request.messages)
    
    # Prepare request for OpenAI
    openai_request = request.model_dump(exclude_none=True)
    openai_request["messages"] = [msg.model_dump() for msg in modified_messages]
    
    # Forward to OpenAI
    if request.stream:
        response = await forward_to_openai(openai_request, api_key, "chat/completions", stream=True)
        
        async def stream_generator():
            async for chunk in response.aiter_text():
                yield chunk
        
        return StreamingResponse(
            stream_generator(),
            media_type="text/plain",
            headers={"Content-Type": "text/plain; charset=utf-8"}
        )
    else:
        response = await forward_to_openai(openai_request, api_key, "chat/completions")
        return JSONResponse(content=response.json())

@app.get("/v1/models")
async def list_models(authorization: str = Header(None)):
    """Forward models request to OpenAI"""
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    api_key = authorization.replace("Bearer ", "")
    
    response = await forward_to_openai({}, api_key, "models", method="GET")
    return JSONResponse(content=response.json())

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "system_prompt_configured": bool(SYSTEM_PROMPT)}

@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "name": "OpenAI Compatible Proxy",
        "version": "1.0.0",
        "description": "Proxy server with system prompt injection",
        "system_prompt_configured": bool(SYSTEM_PROMPT)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)