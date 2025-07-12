# API Contracts Documentation (Core Endpoints)

This document explains the 6 main APIs of your Multi-Agentic Conversational AI System, including their purpose, method, endpoint, request/response schema, and how to call each from the command line (cURL).

---

## 1. Chat Endpoint

**Purpose:** Accepts user message, returns LLM response with optional RAG-enhanced context.

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

**Purpose:** Upload docs (PDF/TXT/CSV/JSON) to populate the RAG base.

- **Method:** POST
- **Endpoint:** `/api/v1/upload_docs`

**Request (form-data):**
- `file`: (file) — select a PDF, TXT, CSV, or JSON file
- `file_type`: (text) — e.g., `pdf`, `txt`, `csv`, or `json`

**Response Example:**
```json
{
  "status": "success",
  "file_id": "349ac736-c8b8-4946-b4bb-4c6709cef8f5"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/upload_docs \
  -F "file=@/path/to/your/file.pdf" \
  -F "file_type=pdf"
```

---

## 3. Create User Endpoint

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

## 4. Update User Endpoint

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

## 5. Get Conversation History Endpoint

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

## 6. Reset Conversation(s) Endpoint

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

**All endpoints return JSON responses. Replace `user123` and `session-uuid` with your actual user/session IDs.** 