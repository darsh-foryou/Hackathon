# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Prerequisites
- Python 3.8 or higher
- OpenAI API key

### 2. Setup
```bash
# Clone and navigate to project
cd Hackathon

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp env_template.txt .env
# Edit .env and add your OpenAI API key
```

### 3. Run the Application
```bash
python run.py
```

The API will be available at `http://localhost:8000`

### 4. Test the System
```bash
# Run the test script
python test_api.py
```

### 5. Explore the API
- **Interactive Docs**: Visit `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

## 📝 Quick API Examples

### Basic Chat
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test123",
    "message": "Hello, my name is John and I work at Tech Corp"
  }'
```

### Create User
```bash
curl -X POST "http://localhost:8000/api/v1/crm/create_user" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "company": "Tech Corp"
  }'
```

### Upload Document
```bash
curl -X POST "http://localhost:8000/api/v1/upload_docs" \
  -F "file=@your_document.pdf" \
  -F "file_type=pdf"
```

## 🎯 Key Features to Try

1. **Conversational AI**: Send messages and get contextual responses
2. **User Management**: Create and manage user profiles
3. **Document Upload**: Upload PDFs, TXTs, CSVs, or JSONs for RAG
4. **Conversation History**: View past conversations and messages
5. **Session Management**: Create and manage conversation sessions

## 🔧 Troubleshooting

### Common Issues

**Port already in use**
```bash
# Change port in run.py or use different port
uvicorn app.main:app --port 8001
```

**OpenAI API key not set**
```bash
# Make sure .env file exists and has your API key
echo "OPENAI_API_KEY=your_key_here" > .env
```

**Dependencies not installed**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Getting Help
- Check the full README.md for detailed documentation
- Review API_CONTRACTS.md for complete API specifications
- Visit `/docs` for interactive API testing

## 🎉 You're Ready!

Your Multi-Agentic Conversational AI System is now running! Start exploring the features and building amazing conversational experiences. 