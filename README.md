---
title: Smart Doc QA
emoji: 📚
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.16.0
app_file: app.py
pinned: false
license: mit
---

# Smart Document Q&A Backend

AI-powered document question answering system using RAG (Retrieval-Augmented Generation).

## 🚀 Features

- **📄 PDF Processing**:  Extract and chunk documents intelligently
- **🔍 Semantic Search**: Vector embeddings with ChromaDB
- **🤖 Intent Classification**:  Smart query routing
- **💬 AI Answers**: Powered by Groq LLM (llama-3.3-70b)
- **📊 Source Citations**: Track which pages were used

## 🏗️ Architecture

### Multi-Agent System: 
1. **Intent Classifier Agent** - Determines if query is about documents or general knowledge
2. **Retrieval Agent** - Searches documents using semantic embeddings
3. **Generation Agent** - Generates AI-powered answers with context

### Tech Stack:
- FastAPI
- HuggingFace Embeddings (all-MiniLM-L6-v2)
- ChromaDB Vector Database
- Groq LLM API
- pypdf for document processing

## 📖 API Documentation

Visit `/docs` for interactive Swagger UI documentation.

## 🧪 Quick Test

1. Upload PDF:  `POST /upload`
2. Ask question: `POST /ai-ask`
3. Get AI-powered answer with sources!

## 👨‍💻 Developer

Built by @polaris0512 for educational purposes.

Demo Date: January 17, 2026