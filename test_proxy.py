#!/usr/bin/env python3
"""
Comprehensive test suite for OpenAI Compatible Proxy
"""

import json
import os
import httpx
import time
import subprocess
import signal
import sys
from contextlib import contextmanager

# Test configuration
PROXY_URL = "http://localhost:8000"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERVER_PROCESS = None

@contextmanager
def proxy_server():
    """Context manager to start and stop the proxy server"""
    global SERVER_PROCESS
    
    print("🚀 Starting proxy server...")
    
    # Set environment variables for the server
    env = os.environ.copy()
    env["SYSTEM_PROMPT"] = "You are a helpful assistant."
    
    try:
        # Start the server process
        SERVER_PROCESS = subprocess.Popen(
            [sys.executable, "main.py"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        max_retries = 30
        for i in range(max_retries):
            try:
                response = httpx.get(f"{PROXY_URL}/health", timeout=1.0)
                if response.status_code == 200:
                    print("✅ Server started successfully!")
                    break
            except:
                pass
            time.sleep(1)
            if i == max_retries - 1:
                raise Exception("Server failed to start within 30 seconds")
        
        yield SERVER_PROCESS
        
    finally:
        # Clean up server process
        if SERVER_PROCESS:
            print("🛑 Stopping proxy server...")
            SERVER_PROCESS.terminate()
            try:
                SERVER_PROCESS.wait(timeout=5)
            except subprocess.TimeoutExpired:
                SERVER_PROCESS.kill()
                SERVER_PROCESS.wait()
            SERVER_PROCESS = None
            print("✅ Server stopped")

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    try:
        response = httpx.get(f"{PROXY_URL}/health")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        return response.status_code == 200 and result.get("status") == "healthy"
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print("\nTesting root endpoint...")
    try:
        response = httpx.get(f"{PROXY_URL}/")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        return (response.status_code == 200 and 
                result.get("name") == "OpenAI Compatible Proxy" and
                result.get("system_prompt_configured") == True)
    except Exception as e:
        print(f"Root endpoint test failed: {e}")
        return False

def test_unauthorized_request():
    """Test request without API key"""
    print("\nTesting unauthorized request...")
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Hello"}
        ]
    }
    
    try:
        response = httpx.post(
            f"{PROXY_URL}/v1/chat/completions",
            json=data,
            timeout=30.0
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Correctly rejected unauthorized request")
            return True
        else:
            print(f"❌ Unexpected response: {response.text}")
            return False
    except Exception as e:
        print(f"Unauthorized test failed: {e}")
        return False

def test_chat_completion_non_streaming():
    """Test chat completion endpoint (non-streaming)"""
    print("\nTesting chat completion (non-streaming)...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Say exactly 'Hello from proxy test!'"}
        ],
        "max_tokens": 20
    }
    
    try:
        response = httpx.post(
            f"{PROXY_URL}/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30.0
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Model: {result.get('model')}")
            print(f"Response: {result['choices'][0]['message']['content']}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"Chat completion test failed: {e}")
        return False

def test_chat_completion_streaming():
    """Test chat completion endpoint (streaming)"""
    print("\nTesting chat completion (streaming)...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Count from 1 to 3"}
        ],
        "max_tokens": 20,
        "stream": True
    }
    
    try:
        with httpx.stream('POST', f"{PROXY_URL}/v1/chat/completions", 
                         headers=headers, json=data, timeout=30.0) as response:
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                chunks = []
                for chunk in response.iter_text():
                    if chunk.strip():
                        chunks.append(chunk.strip())
                        if len(chunks) <= 3:  # Show first few chunks
                            print(f"Chunk: {chunk.strip()}")
                
                # Check if we got streaming data
                has_data = any("data:" in chunk for chunk in chunks)
                has_done = any("[DONE]" in chunk for chunk in chunks)
                
                print(f"✅ Received {len(chunks)} chunks")
                print(f"✅ Has data chunks: {has_data}")
                print(f"✅ Has [DONE] marker: {has_done}")
                
                return has_data and has_done
            else:
                print(f"❌ Error: {response.text}")
                return False
    except Exception as e:
        print(f"Chat completion streaming test failed: {e}")
        return False

def test_completions_non_streaming():
    """Test completions endpoint (non-streaming)"""
    print("\nTesting completions (non-streaming)...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    data = {
        "model": "gpt-3.5-turbo-instruct",
        "prompt": "Say exactly 'Hello from completions test!'",
        "max_tokens": 20
    }
    
    try:
        response = httpx.post(
            f"{PROXY_URL}/v1/completions",
            headers=headers,
            json=data,
            timeout=30.0
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Model: {result.get('model')}")
            print(f"Response: {result['choices'][0]['text']}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"Completions test failed: {e}")
        return False

def test_completions_streaming():
    """Test completions endpoint (streaming)"""
    print("\nTesting completions (streaming)...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    data = {
        "model": "gpt-3.5-turbo-instruct",
        "prompt": "Count: 1, 2, 3",
        "max_tokens": 15,
        "stream": True
    }
    
    try:
        with httpx.stream('POST', f"{PROXY_URL}/v1/completions", 
                         headers=headers, json=data, timeout=30.0) as response:
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                chunks = []
                for chunk in response.iter_text():
                    if chunk.strip():
                        chunks.append(chunk.strip())
                        if len(chunks) <= 3:  # Show first few chunks
                            print(f"Chunk: {chunk.strip()}")
                
                # Check if we got streaming data
                has_data = any("data:" in chunk for chunk in chunks)
                has_done = any("[DONE]" in chunk for chunk in chunks)
                
                print(f"✅ Received {len(chunks)} chunks")
                print(f"✅ Has data chunks: {has_data}")
                print(f"✅ Has [DONE] marker: {has_done}")
                
                return has_data and has_done
            else:
                print(f"❌ Error: {response.text}")
                return False
    except Exception as e:
        print(f"Completions streaming test failed: {e}")
        return False

def test_models_endpoint():
    """Test models endpoint"""
    print("\nTesting models endpoint...")
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    try:
        response = httpx.get(
            f"{PROXY_URL}/v1/models",
            headers=headers,
            timeout=30.0
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            models = result.get('data', [])
            print(f"✅ Found {len(models)} models")
            
            # Check for some expected models
            model_ids = [model.get('id') for model in models]
            has_gpt35 = any('gpt-3.5-turbo' in model_id for model_id in model_ids)
            has_gpt4 = any('gpt-4' in model_id for model_id in model_ids)
            
            print(f"✅ Has GPT-3.5: {has_gpt35}")
            print(f"✅ Has GPT-4: {has_gpt4}")
            
            return len(models) > 0 and has_gpt35
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"Models endpoint test failed: {e}")
        return False

def test_system_prompt_injection():
    """Test that system prompt injection is working"""
    print("\nTesting system prompt injection...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    # Test with chat completions
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "What are you?"}
        ],
        "max_tokens": 50
    }
    
    try:
        response = httpx.post(
            f"{PROXY_URL}/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30.0
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            response_text = result['choices'][0]['message']['content']
            print(f"Chat response: {response_text}")
            
            # Check if response reflects system prompt behavior
            # The system prompt says "You are a helpful assistant" so the response should reflect this
            helpful_indicators = ["helpful", "assistant", "help", "assist", "support"]
            is_helpful = any(indicator in response_text.lower() for indicator in helpful_indicators)
            print(f"✅ Shows helpful assistant behavior: {is_helpful}")
            
            return is_helpful
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"System prompt injection test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 OpenAI Compatible Proxy Test Suite")
    print("=" * 50)
    
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key: export OPENAI_API_KEY=your_key_here")
        return 1
    
    # Basic tests (don't require API key)
    basic_tests = [
        ("Health Check", test_health_check),
        ("Root Endpoint", test_root_endpoint),
        ("Unauthorized Request", test_unauthorized_request),
    ]
    
    # API tests (require valid API key)
    api_tests = [
        ("Chat Completion (Non-streaming)", test_chat_completion_non_streaming),
        ("Chat Completion (Streaming)", test_chat_completion_streaming),
        ("Completions (Non-streaming)", test_completions_non_streaming),
        ("Completions (Streaming)", test_completions_streaming),
        ("Models Endpoint", test_models_endpoint),
        ("System Prompt Injection", test_system_prompt_injection),
    ]
    
    all_tests = basic_tests + api_tests
    results = []
    
    # Start the proxy server and run tests
    try:
        with proxy_server():
            for test_name, test_func in all_tests:
                print(f"\n{'='*20} {test_name} {'='*20}")
                try:
                    start_time = time.time()
                    result = test_func()
                    duration = time.time() - start_time
                    results.append((test_name, result, duration))
                    
                    status = "✅ PASS" if result else "❌ FAIL"
                    print(f"{status} ({duration:.2f}s)")
                    
                except Exception as e:
                    print(f"❌ CRASH: {e}")
                    results.append((test_name, False, 0))
                
                # Small delay between tests
                time.sleep(0.5)
    
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result, duration in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name} ({duration:.2f}s)")
        if result:
            passed += 1
    
    print(f"\n📈 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The proxy is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit(main())