# Document Q&A Backend API Documentation

## Base URL
```
http://127.0.0.1:8000
```

## Endpoints

### 1. Health Check
```
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "service": "backend",
  "collection_count": 15,
  "embedding_model": "all-MiniLM-L6-v2 (via LangChain)"
}
```

---

### 2. Get Statistics
```
GET /stats
```
**Response:**
```json
{
  "total_chunks_stored": 15,
  "collection_name": "documents",
  "embedding_provider": "LangChain"
}
```

---

### 3. Upload PDF ⭐ (Main Feature)
```
POST /upload
Content-Type: multipart/form-data
```

**Request:**
- Form field: `file` (PDF file)

**Response:**
```json
{
  "status": "success",
  "filename": "document.pdf",
  "document_id": "a3b2c1d4",
  "total_pages": 10,
  "total_chunks": 42,
  "chunks_stored": 42,
  "sample_chunk": "This is the beginning of.. .",
  "embedding_dimension": 384,
  "embedding_provider": "LangChain + HuggingFace"
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Error description"
}
```

---

### 4. Search Documents (Debug Mode)
```
POST /search
Content-Type: application/json
```

**Request:**
```json
{
  "question": "What is machine learning?",
  "top_k": 3
}
```

**Response:**
```json
{
  "status": "success",
  "question": "What is machine learning?",
  "results_found": 3,
  "relevant_chunks": [
    {
      "chunk_id": "a3b2c1d4_chunk_0",
      "text": "Machine learning is.. .",
      "metadata": {
        "page": 1,
        "document":  "ml-guide.pdf",
        "source": "ml-guide.pdf - Page 1"
      },
      "relevance_score": 0.234
    }
  ]
}
```

---

### 5. AI Question Answering ⭐⭐ (Main Feature)
```
POST /ai-ask
Content-Type: application/json
```

**Request:**
```json
{
  "question": "What are the main topics in this document?",
  "top_k": 3
}
```

**Response:**
```json
{
  "status": "success",
  "question": "What are the main topics in this document? ",
  "answer": "Based on the provided context, the main topics include machine learning fundamentals, neural networks, and supervised learning approaches.",
  "sources": [
    {
      "page": 1,
      "document": "ml-guide.pdf",
      "text_preview": "Machine learning is a subset of..."
    },
    {
      "page":  3,
      "document": "ml-guide.pdf",
      "text_preview": "Neural networks are computational..."
    }
  ],
  "model_used": "llama-3.3-70b-versatile (Groq)",
  "context_chunks_used": 3
}
```

**Error Responses:**
```json
{
  "status": "error",
  "message": "No documents uploaded yet.  Please upload a PDF first."
}
```

---

### 6. Test AI Connection
```
GET /test-ai
```

**Response:**
```json
{
  "status":  "success",
  "message":  "Groq API is configured correctly! ",
  "test_response": "Groq is working! ",
  "model":  "llama-3.3-70b-versatile"
}
```

---

## Frontend Integration Guide

### Recommended Flow

1. **Check backend health**
   ```javascript
   fetch('http://127.0.0.1:8000/health')
   ```

2. **Upload PDF**
   ```javascript
   const formData = new FormData();
   formData.append('file', pdfFile);
   
   fetch('http://127.0.0.1:8000/upload', {
     method: 'POST',
     body: formData
   })
   ```

3. **Ask Questions**
   ```javascript
   fetch('http://127.0.0.1:8000/ai-ask', {
     method:  'POST',
     headers:  {
       'Content-Type':  'application/json'
     },
     body: JSON.stringify({
       question: "What is this about?",
       top_k:  3
     })
   })
   ```

### CORS
CORS is enabled for all origins (`*`). You can call the API from any frontend. 

### Error Handling
All endpoints return `{"status": "success"}` or `{"status": "error"}`. Always check the status field.

---

## Notes for Frontend Developer

- **Main endpoint to use:** `/ai-ask` (this is the production endpoint)
- **Upload first:** Users must upload a PDF before asking questions
- **Loading states:** AI responses take 1-3 seconds - show a loading indicator
- **Sources:** Display the `sources` array to show which pages were used
- **Top_k parameter:** Default is 3, can be adjusted (3-5 works well)
- **Error messages:** Show error messages to users when status is "error"

---

## Testing

You can test all endpoints at:  `http://127.0.0.1:8000/docs` (Swagger UI)