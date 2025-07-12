# API Contracts Documentation (Core Endpoints)

This document explains the main APIs of your Multi-Agentic Conversational AI System, including their purpose, method, endpoint, request/response schema, and how to call each from the command line (cURL).

---

## 1. Chat Endpoint

**Purpose:** Accepts user message, returns LLM response with optional RAG-enhanced context from user's uploaded documents.

- **Method:** POST
- **Endpoint:** `/api/v1/chat`

**Request Body (JSON):**
```json
{
  "user_id": "user123",
  "message": "Hello, my name is John and I work at Tech Corp.",
  "use_rag": true
}
```

**Response Example:**
```json
{
  "response": "Hello John! How can I help you at Tech Corp?",
  "model_used": "gpt-3.5-turbo",
  "processing_time": 1.23,
  "rag_used": true,
  "user_context_used": true,
  "conversation_history_used": true,
  "user_specific_rag": true,
  "tokens_used": 150,
  "session_id": "session-uuid",
  "error": false
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "Hello, my name is John and I work at Tech Corp.",
    "use_rag": true
  }'
```

---

## 2. Upload Document Endpoint

**Purpose:** Upload docs (PDF/TXT/CSV/JSON) for a specific user to populate their personal RAG knowledge base.

- **Method:** POST
- **Endpoint:** `/api/v1/upload_docs`

**Request (form-data):**
- `file`: (file) — select a PDF, TXT, CSV, or JSON file
- `file_type`: (text) — e.g., `pdf`, `txt`, `csv`, or `json`
- `user_id`: (text) — the user ID who owns this document

**Response Example:**
```json
{
  "status": "success",
  "file_id": "349ac736-c8b8-4946-b4bb-4c6709cef8f5",
  "filename": "document.pdf",
  "file_type": "pdf",
  "file_size": 1024000,
  "message": "File 'document.pdf' uploaded and processed successfully for user user123"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/upload_docs \
  -F "file=@/path/to/your/file.pdf" \
  -F "file_type=pdf" \
  -F "user_id=user123"
```

---

## 3. Get User Files Endpoint

**Purpose:** Get all files uploaded by a specific user.

- **Method:** GET
- **Endpoint:** `/api/v1/files/{user_id}`

**Response Example:**
```json
{
  "user_id": "user123",
  "files": [
    {
      "file_id": "349ac736-c8b8-4946-b4bb-4c6709cef8f5",
      "filename": "document.pdf",
      "file_type": "pdf",
      "file_size": 1024000,
      "vector_store_path": "app/vector_store/user123_349ac736-c8b8-4946-b4bb-4c6709cef8f5",
      "uploaded_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_files": 1
}
```

**cURL Example:**
```bash
curl -X GET http://localhost:8000/api/v1/files/user123
```

---

## 4. Delete User File Endpoint

**Purpose:** Delete a specific file for a user.

- **Method:** DELETE
- **Endpoint:** `/api/v1/files/{file_id}`

**Query Parameters:**
- `user_id`: (required) — the user ID who owns the file

**Response Example:**
```json
{
  "status": "success",
  "message": "File 'document.pdf' deleted successfully"
}
```

**cURL Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/files/349ac736-c8b8-4946-b4bb-4c6709cef8f5?user_id=user123"
```

---

## 5. Create User Endpoint

**Purpose:** Creates a new user profile with provided details.

- **Method:** POST
- **Endpoint:** `/api/v1/crm/create_user`

**Request Body (JSON):**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "company": "Tech Corp",
  "phone": "+1234567890",
  "preferences": {"language": "en"}
}
```

**Response Example:**
```json
{
  "user_id": "user123",
  "name": "John Doe",
  "email": "john@example.com",
  "company": "Tech Corp",
  "phone": "+1234567890",
  "preferences": {"language": "en"},
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/crm/create_user \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "company": "Tech Corp",
    "phone": "+1234567890",
    "preferences": {"language": "en"}
  }'
```

---

## 6. Update User Endpoint

**Purpose:** Updates user information by user ID.

- **Method:** PUT
- **Endpoint:** `/api/v1/crm/update_user/{user_id}`

**Request Body (JSON):**
```json
{
  "company": "New Tech Corp",
  "preferences": {"language": "en", "timezone": "UTC+1"}
}
```

**Response Example:**
```json
{
  "user_id": "user123",
  "name": "John Doe",
  "email": "john@example.com",
  "company": "New Tech Corp",
  "phone": "+1234567890",
  "preferences": {"language": "en", "timezone": "UTC+1"},
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

**cURL Example:**
```bash
curl -X PUT http://localhost:8000/api/v1/crm/update_user/user123 \
  -H "Content-Type: application/json" \
  -d '{
    "company": "New Tech Corp",
    "preferences": {"language": "en", "timezone": "UTC+1"}
  }'
```

---

## 7. Get Conversation History Endpoint

**Purpose:** Fetch full conversation history for a user.

- **Method:** GET
- **Endpoint:** `/api/v1/crm/conversations/{user_id}`

**Response Example:**
```json
[
  {
    "session_id": "session-uuid",
    "user_id": "user123",
    "category": "support",
    "title": null,
    "message_count": 5,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:45:00Z",
    "is_active": true
  }
]
```

**cURL Example:**
```bash
curl -X GET http://localhost:8000/api/v1/crm/conversations/user123
```

---

## 8. Get User Documents Summary Endpoint

**Purpose:** Get a summary of user's uploaded documents and file statistics.

- **Method:** GET
- **Endpoint:** `/api/v1/crm/documents/{user_id}`

**Response Example:**
```json
{
  "user_id": "user123",
  "document_summary": {
    "total_files": 2,
    "file_types": {
      "pdf": 1,
      "csv": 1
    },
    "total_size": 2048000,
    "files": [
      {
        "filename": "document.pdf",
        "file_type": "pdf",
        "file_size": 1024000,
        "uploaded_at": "2024-01-15T10:30:00Z"
      },
      {
        "filename": "data.csv",
        "file_type": "csv",
        "file_size": 1024000,
        "uploaded_at": "2024-01-15T11:00:00Z"
      }
    ]
  }
}
```

**cURL Example:**
```bash
curl -X GET http://localhost:8000/api/v1/crm/documents/user123
```

---

## 9. Reset Conversation(s) Endpoint

**Purpose:** Clears conversation memory (optional: per user or per session).

- **Method:** POST
- **Endpoint:** `/api/v1/reset`

**Request Body (JSON):**
```json
{
  "user_id": "user123"
}
```
*or to reset a specific session:*
```json
{
  "user_id": "user123",
  "session_id": "session-uuid"
}
```

**Response Example:**
```json
{
  "status": "success",
  "message": "Reset 2 active sessions for user user123"
}
```

**cURL Example:**
```bash
# Reset all sessions for a user
curl -X POST http://localhost:8000/api/v1/reset \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}'

# Reset a specific session
curl -X POST http://localhost:8000/api/v1/reset \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "session_id": "session-uuid"}'
```

---

## How User-Specific RAG Works

1. **Upload Process:**
   - User uploads a file with their `user_id`
   - File is processed and stored with user-specific naming (`{user_id}_{file_id}`)
   - File metadata is saved in MongoDB with user association

2. **Chat Process:**
   - When user sends a message, system searches their uploaded documents first
   - If relevant information is found, it's included in the LLM prompt
   - Response indicates if user-specific documents were used (`user_specific_rag: true`)

3. **Document Management:**
   - Users can view their uploaded files
   - Users can delete their files
   - Each user's documents are isolated from other users

---

**All endpoints return JSON responses. Replace `user123` and `session-uuid` with your actual user/session IDs.** 