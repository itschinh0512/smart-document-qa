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
    
    def list_documents(self):
        """
        List all uploaded documents with their metadata
        """
        try: 
            if self.collection.count() == 0:
                return {
                    "status": "success",
                    "message": "No documents uploaded yet",
                    "documents": [],
                    "total_documents": 0,
                    "total_chunks": 0
                }
            
            # Get all items from collection
            results = self.collection.get()
            
            # Extract unique documents
            documents = {}
            for i, metadata in enumerate(results['metadatas']):
                doc_name = metadata. get('document', 'Unknown')
                page = metadata.get('page', 0)
                
                if doc_name not in documents: 
                    documents[doc_name] = {
                        "document_name": doc_name,
                        "pages": [],
                        "total_chunks": 0
                    }
                
                if page not in documents[doc_name]["pages"]:
                    documents[doc_name]["pages"].append(page)
                
                documents[doc_name]["total_chunks"] += 1
            
            # Sort pages
            for doc in documents.values():
                doc["pages"].sort()
                doc["page_count"] = len(doc["pages"])
            
            return {
                "status": "success",
                "documents": list(documents.values()),
                "total_documents": len(documents),
            }
        
        except Exception as e: 
            return {
                "status":  "error",
                "message":  str(e)
            }
    
    def delete_document(self, document_name: str):
        """
        Delete a specific document by name
        """
        try: 
            if self.collection.count() == 0:
                return {
                    "status": "error",
                    "message": "No documents to delete"
                }
            
            # Get all items
            results = self.collection.get()
            
            # Find chunks belonging to this document
            chunks_to_delete = []
            for i, metadata in enumerate(results['metadatas']):
                if metadata.get('document') == document_name:
                    chunks_to_delete.append(results['ids'][i])
            
            if not chunks_to_delete:
                return {
                    "status":  "error",
                    "message": f"Document '{document_name}' not found"
                }
            
            # Delete the chunks
            self.collection.delete(ids=chunks_to_delete)
            
            return {
                "status": "success",
                "message": f"Deleted document:  {document_name}",
                "chunks_deleted": len(chunks_to_delete),
                "remaining_chunks": self.collection.count()
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def clear_all_documents(self):
        """
        Delete ALL documents from the collection
        """
        try:
            if self. collection.count() == 0:
                return {
                    "status": "success",
                    "message": "No documents to clear",
                    "chunks_deleted": 0
                }
            
            chunks_count = self.collection.count()
            
            # Get all IDs and delete them
            results = self.collection.get()
            all_ids = results['ids']
            
            self.collection.delete(ids=all_ids)
            
            return {
                "status": "success",
                "message": "All documents cleared successfully",
                "chunks_deleted":  chunks_count,
                "remaining_chunks": self.collection.count()
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
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
        Generate answer with inline citations
        """
        try:
            # Check if documents exist
            if self.retrieval_agent.collection.count() == 0:
                return {
                    "status": "error",
                    "message": "No documents uploaded yet. Please upload a PDF first."
                }
            
            # Get relevant context
            retrieval_result = self.retrieval_agent.retrieve(
                question=question,
                top_k=top_k,
                mode="context"
            )
            
            if retrieval_result["status"] != "success":
                return retrieval_result
            
            combined_context = retrieval_result["context"]
            sources = retrieval_result["sources"]
            
            # Create numbered source references for the prompt
            source_references = []
            for i, source in enumerate(sources, 1):
                source_references. append(
                    f"[{i}] Page {source['page']} from {source['document']}"
                )
            source_list = "\n".join(source_references)
            
            # IMPROVED PROMPT with citation instructions
            prompt = f"""You are a helpful AI assistant that answers questions based on provided document context. 

    IMPORTANT INSTRUCTIONS:
    1. Answer the question using ONLY the information from the provided context
    2. Include inline citations using [1], [2], [3] format when referencing specific sources
    3. Be specific and reference which pages contain the information
    4. If the context doesn't contain enough information, say so clearly
    5. Do not make up information not present in the context

    CONTEXT FROM DOCUMENTS:
    {combined_context}

    AVAILABLE SOURCES:
    {source_list}

    USER QUESTION:
    {question}

    ANSWER (with inline citations):"""

            # Call Groq API
            response = self.groq_client. chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on document context.  Always include inline citations [1], [2], etc. when referencing sources."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            answer_text = response.choices[0]. message.content. strip()
            
            # Return with sources
            return {
                "status": "success",
                "question": question,
                "answer":  answer_text,  # Now includes inline citations like [1], [2]
                "sources": sources,  # Still include the source list
                "source_references": source_references,  # Numbered list for display
                "model_used": "llama-3.3-70b-versatile",
                "context_used": True,
                "used_rag": True
            }
        
        except Exception as e: 
            return {
                "status":  "error",
                "message":  str(e)
            }
    

class Intent_Classifier_Agent:
    """
    Classifies user intent to route queries appropriately
    Prevents unnecessary RAG operations for non-document questions
    """
    def __init__(self, groq_client):
        self.groq_client = groq_client
    
    def classify_intent(self, question: str):
        """
        Classify if the question is: 
        - 'document_query':  Question about uploaded documents (use RAG)
        - 'general_query': General question not about documents (don't use RAG)
        - 'greeting': Greeting or chitchat
        """
        try:
            classification_prompt = f"""You are an intent classifier for a document Q&A system. 

Classify the following user question into ONE of these categories:
1. "document_query" - Questions about document content, asking to summarize, explain, or find information IN documents
   Examples: "What is in section 3? ", "Summarize the document", "What does page 5 say about X?"
   
2. "general_query" - General knowledge questions (weather, math, current events, definitions) NOT about documents
   Examples: "What's the weather? ", "What is machine learning?", "Who is the president?"
   
3. "greeting" - Greetings, thanks, or casual conversation
   Examples: "Hello", "Hi", "Thanks", "How are you?"

User question: "{question}"

Respond with ONLY ONE WORD:  either "document_query", "general_query", or "greeting"
Do not include any explanation."""

            response = self.groq_client.chat.completions. create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an intent classifier.  Respond with only one word: document_query, general_query, or greeting."},
                    {"role": "user", "content": classification_prompt}
                ],
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=10
            )
            
            intent = response.choices[0].message. content.strip().lower()
            
            # Validate intent
            valid_intents = ["document_query", "general_query", "greeting"]
            if intent not in valid_intents:
                # Default to document_query if unclear (safe fallback)
                intent = "document_query"
            
            return {
                "status": "success",
                "question": question,
                "intent":  intent
            }
        
        except Exception as e:
            # If classification fails, default to document_query (safe fallback)
            return {
                "status": "success",
                "question": question,
                "intent": "document_query",
                "note": f"Classification failed: {str(e)}, defaulting to document query"
            }
    
    def get_general_response(self, question: str, intent: str):
        """
        Generate appropriate response for non-document queries
        """
        if intent == "greeting":
            return {
                "status": "success",
                "question": question,
                "answer": "Hello! 👋 I'm a document Q&A assistant. Please upload a PDF document, and I can answer questions about its content.  What would you like to know? ",
                "intent": "greeting",
                "used_rag": False
            }
        
        elif intent == "general_query":
            return {
                "status": "success",
                "question": question,
                "answer": "I'm specialized in answering questions about uploaded documents. I cannot answer general knowledge questions like weather, current events, or facts not in your documents. Please ask me something about the PDF you've uploaded, or upload a new document! ",
                "intent": "general_query",
                "used_rag": False
            }
        
        else:
            return None  # Should use RAG



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

# Initialize Intent Classifier Agent (NEW!)
intent_classifier = Intent_Classifier_Agent(groq_client=groq_client)

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
    try:
        # Step 1: Classify intent
        classification = intent_classifier.classify_intent(query.question)
        intent = classification["intent"]
        
        # Step 2: Route based on intent
        if intent in ["greeting", "general_query"]:
            return intent_classifier.get_general_response(query.question, intent)
        
        else:  # intent == "document_query"
            rag_response = generation_agent.generate_answer(query.question, query.top_k)
            
            # Add intent information
            if rag_response["status"] == "success":
                rag_response["intent"] = "document_query"
                rag_response["used_rag"] = True  # type: ignore
            
            return rag_response
    
    except Exception as e: 
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/classify-intent")
async def classify_intent(query: QueryRequest):
    """
    Debug endpoint to see how questions are classified
    Useful for testing and demonstration
    """
    return intent_classifier.classify_intent(query.question)

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

@app.get("/documents")
def list_documents():
    """
    List all uploaded documents with metadata
    Shows document names, page counts, and chunk counts
    """
    return retrieval_agent.list_documents()

@app.delete("/documents/{document_name}")
def delete_document(document_name: str):
    """
    Delete a specific document by name
    Example: DELETE /documents/my-file.pdf
    """
    return retrieval_agent.delete_document(document_name)

@app.delete("/documents")
def clear_all_documents():
    """
    Delete ALL documents from the system
    Use with caution! 
    """
    return retrieval_agent.clear_all_documents()

@app.get("/documents/count")
def document_count():
    """
    Quick endpoint to get document and chunk counts
    """
    docs_info = retrieval_agent.list_documents()
    if docs_info["status"] == "success":
        return {
            "status": "success",
            "total_documents": docs_info. get("total_documents", 0),
            "total_chunks": docs_info.get("total_chunks", 0)
        }
    return docs_info

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)