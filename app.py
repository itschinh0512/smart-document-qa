# app.py - HuggingFace Spaces entry point with Gradio wrapper
import gradio as gr
import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

# Import your existing FastAPI app from main.py
from main import app as fastapi_app

# Create a simple Gradio interface
with gr.Blocks(title="Document Q&A Backend") as demo:
    gr.Markdown("""
    # 📚 Smart Document Q&A Backend
    
    ## AI-Powered Document Question Answering System
    
    This is the backend API for the Document Q&A system.
    
    ### 🔗 Quick Links:
    - [📖 API Documentation (Swagger UI)](/docs)
    - [❤️ Health Check](/health)
    - [🏓 Ping Test](/ping)
    - [🤖 Test AI Connection](/test-ai)
    
    ### 📊 Main Endpoints:
    - `POST /upload` - Upload PDF documents
    - `POST /ai-ask` - Ask questions about uploaded documents
    - `POST /search` - Search for relevant chunks (debug)
    - `GET /stats` - View system statistics
    
    ### 🚀 How to Use:
    1. Visit `/docs` for interactive API testing
    2. Upload a PDF using `/upload` endpoint
    3. Ask questions using `/ai-ask` endpoint
    4. Get AI-powered answers with sources! 
    
    ### 🏗️ Architecture:
    - **Intent Classification**: Routes queries intelligently
    - **Semantic Search**: Vector embeddings with ChromaDB
    - **RAG Pipeline**: Retrieval-Augmented Generation
    - **AI Model**: Groq (llama-3.3-70b-versatile)
    """)
    
    gr.Markdown("---")
    gr.Markdown("🎓 Built by:  polaris0512 | 📅 Demo: January 17, 2026")

# Mount FastAPI app to Gradio
app = gr.mount_gradio_app(fastapi_app, demo, path="/")

# Add redirect from root to docs (optional)
@app.get("/")
def redirect_to_gradio():
    """Redirect root to Gradio interface"""
    return RedirectResponse(url="/gradio")

if __name__ == "__main__":
    uvicorn. run(app, host="0.0.0.0", port=7860)