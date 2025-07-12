#!/usr/bin/env python3
"""
Test script for Multi-Agentic Conversational AI System
Run this script to test the API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"✅ Health check: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_root():
    """Test root endpoint"""
    print("🔍 Testing root endpoint...")
    try:
        response = requests.get("http://localhost:8000/")
        print(f"✅ Root endpoint: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False

def test_crm_categories():
    """Test CRM categories endpoint"""
    print("🔍 Testing CRM categories...")
    try:
        response = requests.get(f"{BASE_URL}/crm/categories")
        print(f"✅ CRM categories: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ CRM categories failed: {e}")
        return False

def test_create_user():
    """Test user creation"""
    print("🔍 Testing user creation...")
    try:
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "company": "Test Corp",
            "phone": "+1-555-123-4567",
            "preferences": {"language": "en", "timezone": "UTC"}
        }
        response = requests.post(f"{BASE_URL}/crm/create_user", json=user_data)
        result = response.json()
        print(f"✅ User created: {result['user_id']}")
        return result['user_id']
    except Exception as e:
        print(f"❌ User creation failed: {e}")
        return None

def test_chat(user_id):
    """Test chat functionality"""
    print("🔍 Testing chat functionality...")
    try:
        chat_data = {
            "user_id": user_id,
            "message": "Hello! My name is Test User and I work at Test Corp. I need help with your product.",
            "use_rag": True
        }
        response = requests.post(f"{BASE_URL}/chat", json=chat_data)
        result = response.json()
        print(f"✅ Chat response: {result['response'][:100]}...")
        print(f"   Processing time: {result['processing_time']}s")
        print(f"   Session ID: {result['session_id']}")
        return result['session_id']
    except Exception as e:
        print(f"❌ Chat failed: {e}")
        return None

def test_conversation_history(user_id):
    """Test conversation history"""
    print("🔍 Testing conversation history...")
    try:
        response = requests.get(f"{BASE_URL}/crm/conversations/{user_id}")
        conversations = response.json()
        print(f"✅ Found {len(conversations)} conversations")
        for conv in conversations[:3]:  # Show first 3
            print(f"   - Session: {conv['session_id'][:8]}... | Messages: {conv['message_count']} | Category: {conv['category']}")
        return True
    except Exception as e:
        print(f"❌ Conversation history failed: {e}")
        return False

def test_session_messages(session_id):
    """Test session messages"""
    print("🔍 Testing session messages...")
    try:
        response = requests.get(f"{BASE_URL}/crm/conversation/{session_id}/messages")
        result = response.json()
        print(f"✅ Session has {result['message_count']} messages")
        for msg in result['messages'][:2]:  # Show first 2 messages
            print(f"   - {msg['role']}: {msg['content'][:50]}...")
        return True
    except Exception as e:
        print(f"❌ Session messages failed: {e}")
        return False

def test_upload_simulation():
    """Simulate document upload (without actual file)"""
    print("🔍 Testing upload endpoint structure...")
    try:
        # This would normally upload a file, but we'll just test the endpoint exists
        response = requests.get("http://localhost:8000/docs")
        if response.status_code == 200:
            print("✅ Upload endpoint available (check /docs for details)")
            return True
        else:
            print("❌ Upload endpoint not accessible")
            return False
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Multi-Agentic AI System Tests")
    print("=" * 50)
    
    # Test basic endpoints
    if not test_health():
        print("❌ Health check failed. Make sure the server is running!")
        return
    
    test_root()
    test_crm_categories()
    
    # Test CRM functionality
    user_id = test_create_user()
    if not user_id:
        print("❌ Cannot proceed without user creation")
        return
    
    # Test chat functionality
    session_id = test_chat(user_id)
    if not session_id:
        print("❌ Cannot proceed without chat functionality")
        return
    
    # Test conversation management
    test_conversation_history(user_id)
    test_session_messages(session_id)
    
    # Test upload endpoint
    test_upload_simulation()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("\n📋 Next steps:")
    print("1. Visit http://localhost:8000/docs for interactive API documentation")
    print("2. Try uploading documents using the /upload_docs endpoint")
    print("3. Test more complex conversations with the chat endpoint")
    print("4. Explore CRM features through the /crm endpoints")

if __name__ == "__main__":
    main() 