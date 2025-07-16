#!/usr/bin/env python3
"""
Test script for OpenAI Compatible Proxy
"""

import json
import os
import httpx

# Test configuration
PROXY_URL = "http://localhost:8000"
# You would need to set this to your actual OpenAI API key for testing
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-test-key-replace-with-real-key")

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    try:
        response = httpx.get(f"{PROXY_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print("\nTesting root endpoint...")
    try:
        response = httpx.get(f"{PROXY_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Root endpoint test failed: {e}")
        return False

def test_chat_completion():
    """Test chat completion endpoint"""
    print("\nTesting chat completion...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Say hello!"}
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
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Chat completion test failed: {e}")
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
            print(f"Available models: {len(result.get('data', []))}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Models endpoint test failed: {e}")
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
            print("Correctly rejected unauthorized request")
            return True
        else:
            print(f"Unexpected response: {response.text}")
            return False
    except Exception as e:
        print(f"Unauthorized test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("OpenAI Compatible Proxy Test Suite")
    print("=" * 40)
    
    tests = [
        ("Health Check", test_health_check),
        ("Root Endpoint", test_root_endpoint),
        ("Unauthorized Request", test_unauthorized_request),
    ]
    
    # Only run OpenAI API tests if we have a real API key
    if OPENAI_API_KEY and not OPENAI_API_KEY.startswith("sk-test-"):
        tests.extend([
            ("Chat Completion", test_chat_completion),
            ("Models Endpoint", test_models_endpoint),
        ])
    else:
        print("\nNote: Skipping OpenAI API tests (no valid API key)")
        print("Set OPENAI_API_KEY environment variable to run full tests")
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 40)
    print("Test Results:")
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("All tests passed! ✅")
        return 0
    else:
        print("Some tests failed! ❌")
        return 1

if __name__ == "__main__":
    exit(main())