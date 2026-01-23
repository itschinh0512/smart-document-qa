# Smart Document Q&A - Backend

Backend Python sử dụng kiến trúc RAG (Retrieval-Augmented Generation) cho hệ thống hỏi đáp tài liệu thông minh.

## 📋 Tổng quan

Backend triển khai pipeline RAG hoàn chỉnh với hai agent chính:

### 1. **Retrieval Agent** (Agent Truy xuất)
- **Chức năng**: Xử lý upload PDF, tạo embeddings, tìm kiếm ngữ nghĩa
- **Công nghệ**:
  - ChromaDB: Lưu trữ vector embeddings
  - HuggingFace `all-MiniLM-L6-v2`: Model embedding (384 chiều)
  - LangChain RecursiveCharacterTextSplitter: Chia nhỏ văn bản thông minh

### 2. **Generation Agent** (Agent Sinh văn bản)
- **Chức năng**: Sinh câu trả lời dựa trên ngữ cảnh được truy xuất
- **Công nghệ**:
  - Groq API với Llama 3.3 70B
  - LPU (Language Processing Unit) cho tốc độ inference cao
  - Temperature 0.3 để cân bằng độ chính xác và sáng tạo

## 🛠️ Tech Stack

```
FastAPI (Web Framework)
    │
    ├── PyPDF (PDF parsing)
    ├── LangChain (Text processing)
    │   └── HuggingFaceEmbeddings
    │       └── all-MiniLM-L6-v2
    │
    ├── ChromaDB (Vector database)
    │   └── In-memory storage
    │
    └── Groq API (LLM)
        └── Llama 3.3 70B Versatile
```

## 📦 Cài đặt

### Bước 1: Chuẩn bị môi trường
```bash
# Di chuyển vào thư mục backend
cd backend

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Trên macOS/Linux:
source venv/bin/activate

# Trên Windows:
venv\Scripts\activate
```

### Bước 2: Cài đặt dependencies
```bash
pip install -r requirements.txt
```

Lần chạy đầu tiên sẽ tải xuống embedding model (~80MB).

### Bước 3: Cấu hình biến môi trường
Tạo file `.env` trong thư mục `backend/`:
```bash
GROQ_API_KEY=your_groq_api_key_here
PORT=8000
```

**Lấy Groq API Key:**
1. Truy cập https://console.groq.com/keys
2. Đăng ký/đăng nhập
3. Tạo API key mới
4. Copy và paste vào file `.env`

## ▶️ Chạy ứng dụng

### Development mode (FastAPI thuần)
```bash
python main.py
```
API sẽ chạy tại: `http://localhost:8000`

### Production mode (với Gradio UI)
```bash
python app.py
```
- Gradio interface: `http://localhost:7860`
- API docs: `http://localhost:7860/docs`

## 🧪 Kiểm tra hệ thống

### 1. Health Check
```bash
curl http://localhost:8000/health
```

**Kết quả mong đợi:**
```json
{
  "status": "healthy",
  "service": "backend",
  "collection_count": 0,
  "embedding_model": "all-MiniLM-L6-v2 (via LangChain)"
}
```

### 2. Test kết nối AI
```bash
curl http://localhost:8000/test-ai
```

**Kết quả mong đợi:**
```json
{
  "status": "success",
  "message": "Groq API is configured correctly!",
  "test_response": "Groq is working!",
  "model": "llama-3.3-70b-versatile"
}
```

### 3. Upload PDF
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@test.pdf"
```

**Kết quả mong đợi:**
```json
{
  "status": "success",
  "filename": "test.pdf",
  "document_id": "abc12345",
  "total_pages": 5,
  "total_chunks": 23,
  "chunks_stored": 23,
  "embedding_dimension": 384
}
```

### 4. Tìm kiếm tài liệu
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"question": "Nội dung chính của tài liệu là gì?", "top_k": 3}'
```

### 5. Hỏi đáp với AI
```bash
curl -X POST http://localhost:8000/ai-ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Tóm tắt tài liệu này", "top_k": 3}'
```

### 6. Xem thống kê hệ thống
```bash
curl http://localhost:8000/stats
```

### 7. API Documentation (Swagger UI)
Mở trình duyệt và truy cập: `http://localhost:8000/docs`

## 📖 API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| GET | `/ping` | Ping test |
| GET | `/stats` | Thống kê hệ thống |
| GET | `/test-ai` | Test kết nối Groq API |
| POST | `/upload` | Upload PDF document |
| POST | `/search` | Tìm kiếm chunks liên quan |
| POST | `/ai-ask` | Hỏi đáp với AI |

Chi tiết đầy đủ: [docs_api.md](docs_api.md)

## 📂 Cấu trúc code

```
backend/
├── main.py                 # FastAPI app chính
│   ├── Retrieval_Agent     # Class xử lý retrieval
│   ├── Generation_Agent    # Class xử lý generation
│   └── API endpoints
│
├── app.py                  # Gradio wrapper (HuggingFace Spaces)
├── requirements.txt        # Python dependencies
├── docs_api.md            # API documentation
├── render.yaml            # Render.com deployment config
└── README.md              # File này
```

## 🚢 Deployment

### HuggingFace Spaces
1. Tạo Space mới (Python SDK)
2. Upload các file backend
3. Thêm `GROQ_API_KEY` vào Secrets
4. Space tự động chạy `app.py`

