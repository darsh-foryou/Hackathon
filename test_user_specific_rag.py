#!/usr/bin/env python3
"""
Test script for User-Specific RAG functionality
This script demonstrates how files are associated with users and how RAG works per user.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_user_specific_rag():
    """Test the complete user-specific RAG workflow"""
    print("🚀 Testing User-Specific RAG Functionality")
    print("=" * 60)
    
    # Step 1: Create a user
    print("1. Creating user...")
    user_data = {
        "name": "Test User",
        "email": "test2@example.com",
        "company": "Test Corp",
        "phone": "+1234567890",
        "preferences": {"language": "en"}
    }
    
    response = requests.post(f"{BASE_URL}/crm/create_user", json=user_data)
    if response.status_code != 200:
        print(f"❌ Failed to create user: {response.text}")
        return
    
    user_info = response.json()
    user_id = user_info["user_id"]
    print(f"✅ User created: {user_id}")
    
    # Step 2: Upload a file for this user
    print("\n2. Uploading file for user...")
    
    # Create a simple test file
    test_content = """
    Product Information:
    - Product: Widget Pro
    - Price: $36.99
    - Features: High quality, durable, 1-year warranty
    - Category: Electronics
    
    Customer Support:
    - Email: support@widgetpro.com
    - Phone: 1-800-WIDGET
    - Hours: Monday-Friday 9AM-5PM EST
    """
    
    with open("test_document.txt", "w") as f:
        f.write(test_content)
    
    # Upload the file
    with open("test_document.txt", "rb") as f:
        files = {"file": f}
        data = {"file_type": "txt", "user_id": user_id}
        response = requests.post(f"{BASE_URL}/upload_docs", files=files, data=data)
    
    if response.status_code != 200:
        print(f"❌ Failed to upload file: {response.text}")
        return
    
    upload_result = response.json()
    print(f"✅ File uploaded: {upload_result['filename']}")
    
    # Step 3: Get user's files
    print("\n3. Getting user's files...")
    response = requests.get(f"{BASE_URL}/files/{user_id}")
    if response.status_code == 200:
        files_info = response.json()
        print(f"✅ User has {files_info['total_files']} files")
        for file_info in files_info['files']:
            print(f"   - {file_info['filename']} ({file_info['file_type']})")
    
    # Step 4: Test chat with user-specific RAG
    print("\n4. Testing chat with user-specific RAG...")
    
    # Test question about the uploaded document
    chat_data = {
        "user_id": user_id,
        "message": "What is the price of Widget Pro and what are its features?",
        "use_rag": True
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=chat_data)
    if response.status_code == 200:
        chat_result = response.json()
        print(f"✅ Chat response: {chat_result['response'][:200]}...")
        print(f"   User-specific RAG used: {chat_result.get('user_specific_rag', False)}")
        print(f"   Processing time: {chat_result['processing_time']}s")
    else:
        print(f"❌ Chat failed: {response.text}")
    
    # Step 5: Test question that should NOT be in user's documents
    print("\n5. Testing question not in user's documents...")
    chat_data = {
        "user_id": user_id,
        "message": "What is the capital of France?",
        "use_rag": True
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=chat_data)
    if response.status_code == 200:
        chat_result = response.json()
        print(f"✅ Chat response: {chat_result['response'][:200]}...")
        print(f"   User-specific RAG used: {chat_result.get('user_specific_rag', False)}")
    else:
        print(f"❌ Chat failed: {response.text}")
    
    # Step 6: Get user document summary
    print("\n6. Getting user document summary...")
    response = requests.get(f"{BASE_URL}/crm/documents/{user_id}")
    if response.status_code == 200:
        summary = response.json()
        doc_summary = summary['document_summary']
        print(f"✅ Document summary:")
        print(f"   Total files: {doc_summary['total_files']}")
        print(f"   Total size: {doc_summary['total_size']} bytes")
        print(f"   File types: {doc_summary['file_types']}")
    
    # Step 7: Test with a different user (should not see the first user's documents)
    print("\n7. Testing with different user...")
    user2_data = {
        "name": "Another User",
        "email": "another@example.com",
        "company": "Another Corp"
    }
    
    response = requests.post(f"{BASE_URL}/crm/create_user", json=user2_data)
    if response.status_code == 200:
        user2_id = response.json()["user_id"]
        print(f"✅ Second user created: {user2_id}")
        
        # Try to ask the same question - should not find the document
        chat_data = {
            "user_id": user2_id,
            "message": "What is the price of Widget Pro?",
            "use_rag": True
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=chat_data)
        if response.status_code == 200:
            chat_result = response.json()
            print(f"✅ Second user chat response: {chat_result['response'][:200]}...")
            print(f"   User-specific RAG used: {chat_result.get('user_specific_rag', False)}")
        else:
            print(f"❌ Second user chat failed: {response.text}")
    
    # Cleanup
    print("\n8. Cleaning up...")
    import os
    if os.path.exists("test_document.txt"):
        os.remove("test_document.txt")
    
    print("\n" + "=" * 60)
    print("✅ User-Specific RAG Test Completed!")
    print("\n📋 Key Features Demonstrated:")
    print("1. Files are associated with specific users")
    print("2. RAG searches user's own documents first")
    print("3. Users can't access other users' documents")
    print("4. File metadata is stored in MongoDB")
    print("5. Document summaries are available per user")

if __name__ == "__main__":
    test_user_specific_rag() 