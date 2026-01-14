from fastapi import FastAPI, UploadFile, File
from fastapi. middleware.cors import CORSMiddleware
from pypdf import PdfReader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import chromadb
import io
import uuid
import os


load_dotenv()


class QueryRequest(BaseModel):
    question: str
    top_k: int = 3

class Retrieval_Agent:
    def __init__(self, app, db_client, embedding_model, chunker):
        self.app = app
        self.db_client = db_client
        self.embedding_model = embedding_model
        self.chunker = chunker
        
        # Get or create collection
        try:
            self.collection = self.db_client.get_collection("documents")
        except:
            self.collection = self.db_client.create_collection("documents")
    
    async def load(self, file: UploadFile):
        """
        Load a PDF file, extract text, create embeddings, and store in vector DB
        """
        try:
            # Read the uploaded file
            contents = await file.read()
            
            # Parse PDF
            pdf_reader = PdfReader(io.BytesIO(contents))
            
            # Extract text from all pages with metadata
            all_chunks = []
            all_metadata = []
            
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                page_text = page.extract_text()
                
                # Use text splitter for smart chunking
                chunks = self.chunker.split_text(page_text)
                
                # Add metadata to each chunk
                for chunk in chunks:
                    if len(chunk.strip()) > 50:  # Ignore very small chunks
                        all_chunks.append(chunk)
                        all_metadata.append({
                            "page": page_num,
                            "document": file.filename,
                            "source": f"{file.filename} - Page {page_num}"
                        })
            
            # Generate embeddings
            embeddings = self.embedding_model.embed_documents(all_chunks)
            
            # Generate unique IDs
            doc_id = str(uuid.uuid4())[:8]
            chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(all_chunks))]
            
            # Store in ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=all_chunks,
                metadatas=all_metadata,
                ids=chunk_ids
            )
            
            return {
                "status": "success",
                "filename": file.filename,
                "document_id": doc_id,
                "total_pages": len(pdf_reader.pages),
                "total_chunks": len(all_chunks),
                "chunks_stored": len(chunk_ids),
                "sample_chunk": all_chunks[0][:200] + "..." if all_chunks else "",
                "embedding_dimension": len(embeddings[0]) if embeddings else 0,
                "embedding_provider": "LangChain + HuggingFace"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def retrieve(self, question: str, top_k: int = 3, mode: str = "search"):
        """
        Retrieve relevant document chunks based on a question
        mode: 'search' returns detailed results, 'context' returns combined context
        """
        try:
            # Check if there are any documents
            if self.collection.count() == 0:
                return {
                    "status": "error",
                    "message": "No documents uploaded yet. Please upload a PDF first."
                }
            
            # Generate embedding for the query
            query_embedding = self.embedding_model.embed_query(question)
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            if mode == "search":
                # Format the results with details
                relevant_chunks = []
                for i in range(len(results['documents'][0])):
                    relevant_chunks.append({
                        "chunk_id": results['ids'][0][i],
                        "text": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "relevance_score": float(results['distances'][0][i]) if 'distances' in results else None
                    })
                
                return {
                    "status": "success",
                    "question": question,
                    "results_found": len(relevant_chunks),
                    "relevant_chunks": relevant_chunks
                }
            
            elif mode == "context":
                # Combine chunks into context
                context_chunks = results['documents'][0]
                combined_context = "\n\n---\n\n".join(context_chunks)
                
                # Format sources
                sources = []
                for i in range(len(results['documents'][0])):
                    sources.append({
                        "page": results['metadatas'][0][i].get('page', 'Unknown'),
                        "document": results['metadatas'][0][i].get('document', 'Unknown'),
                        "text_preview": results['documents'][0][i][:150] + "..."
                    })
                
                return {
                    "status": "success",
                    "question": question,
                    "context": combined_context,
                    "sources": sources,
                    "note": "This endpoint returns context only. AI answer coming in next task!"
                }
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_stats(self):
        """Get statistics about stored documents"""
        return {
            "total_chunks_stored": self.collection.count(),
            "collection_name": self.collection.name,
            "embedding_provider": "LangChain"
        }

class Generation_Agent:
    def __init__(self, groq_client, retrieval_agent):
        self.groq_client = groq_client
        self.retrieval_agent = retrieval_agent
    
    def test_connection(self):
        """Test if Groq API is configured correctly"""
        try:
            if not os.getenv("GROQ_API_KEY"):
                return {
                    "status": "error",
                    "message": "GROQ_API_KEY not found in .env file"
                }
            
            # Simple test call
            response = self.groq_client.chat.completions. create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content":  "Say 'Groq is working!'"}],
                max_tokens=20
            )
            
            return {
                "status": "success",
                "message": "Groq API is configured correctly! ",
                "test_response": response.choices[0].message.content,
                "model": "llama-3.3-70b-versatile"
            }
        
        except Exception as e: 
            return {
                "status":  "error",
                "message":  f"Groq API error: {str(e)}"
            }
    
    def generate_answer(self, question: str, top_k: int = 3):
        """
        Generate an AI answer based on retrieved document context
        """
        try: 
            # Check if documents exist
            if self.retrieval_agent.collection.count() == 0:
                return {
                    "status": "error",
                    "message": "No documents uploaded yet. Please upload a PDF first."
                }
            
            # Check if Groq API key is configured
            if not os. getenv("GROQ_API_KEY"):
                return {
                    "status": "error",
                    "message": "Groq API key not configured.  Please add GROQ_API_KEY to . env file."
                }
            
            # Step 1: Retrieve context using retrieval agent
            retrieval_result = self.retrieval_agent.retrieve(
                question=question,
                top_k=top_k,
                mode="context"
            )
            
            if retrieval_result["status"] == "error":
                return retrieval_result
            
            combined_context = retrieval_result["context"]
            sources = retrieval_result["sources"]
            
            # Step 2: Create prompt for Groq
            system_prompt = """You are a helpful AI assistant that answers questions based on provided document context. 

Rules:
1. Answer ONLY based on the provided context
2. If the context doesn't contain the answer, say "I cannot find this information in the provided documents."
3. Be concise and accurate
4. Cite specific details from the context when possible
5. If the question is unclear, ask for clarification"""

            user_prompt = f"""Context from documents:
{combined_context}

Question: {question}

Please provide a clear and accurate answer based on the context above."""

            # Step 3: Call Groq API
            response = self.groq_client. chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content":  system_prompt},
                    {"role": "user", "content":  user_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Step 4: Extract the answer
            ai_answer = response.choices[0].message.content
            
            return {
                "status": "success",
                "question": question,
                "answer": ai_answer,
                "sources": sources,
                "model_used": "llama-3.3-70b-versatile (Groq)",
                "context_chunks_used": top_k
            }
        
        except Exception as e: 
            return {
                "status":  "error",
                "message":  str(e)
            }
        
app = FastAPI(title="Document Q&A Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

#ChromaDB Initialization
chroma_client = chromadb.Client()

#LangChain Embeddings
print("Downloading...")
embedding_model = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

# Initialize text splitter (LangChain's smart chunking)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,  # Overlap helps maintain context
    length_function=len,
    separators=["\n\n", "\n", " ", ""]
)

# Initialize Groq client ← ADD THIS SECTION
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize Retrieval Agent
retrieval_agent = Retrieval_Agent(
    app=app,
    db_client=chroma_client,
    embedding_model=embedding_model,
    chunker=text_splitter
)

# Initialize Generation Agent
generation_agent = Generation_Agent(
    groq_client=groq_client,
    retrieval_agent=retrieval_agent
)

@app.get("/")
def root():
    return {"message":  "Document Q&A API is running!  🚀"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF, extract text, create embeddings with LangChain, and store in vector DB
    """
    return await retrieval_agent.load(file)

@app.post("/search")
async def search_documents(query: QueryRequest):
    """
    Search for relevant document chunks based on a question
    """
    return retrieval_agent.retrieve(query.question, query.top_k, mode="search")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "backend",
        "collection_count": retrieval_agent.collection.count(),
        "embedding_model": "all-MiniLM-L6-v2 (via LangChain)"
    }

@app.get("/stats")
def get_stats():
    """
    Get statistics about stored documents
    """
    return retrieval_agent.get_stats()

@app.get("/test-ai")
async def test_ai():
    """
    Test if Groq API is configured correctly
    """
    return generation_agent.test_connection()

@app.post("/ai-ask")
async def ai_ask_question(query: QueryRequest):
    """
    Ask a question and get an AI-generated answer (powered by Groq)
    """
    return generation_agent.generate_answer(query.question, query.top_k)

@app.get("/ping")
def ping():
    """
    Simple endpoint for frontend to test connectivity
    """
    return {
        "status": "success",
        "message": "Backend is reachable! ",
        "timestamp": str(uuid.uuid4())
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)