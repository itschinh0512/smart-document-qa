# Smart Document Q&A System

Hệ thống hỏi đáp tài liệu thông minh sử dụng công nghệ RAG (Retrieval-Augmented Generation).

## 📋 Giới thiệu

Smart Document Q&A là một ứng dụng full-stack cho phép người dùng tải lên tài liệu PDF và đặt câu hỏi về nội dung tài liệu. Hệ thống sử dụng:

- **RAG (Retrieval-Augmented Generation)**: Kết hợp tìm kiếm ngữ nghĩa và sinh văn bản AI
- **Groq LPU**: Công nghệ tăng tốc phần cứng cho inference thời gian thực
- **ChromaDB**: Cơ sở dữ liệu vector để lưu trữ embeddings
- **LangChain**: Framework xử lý văn bản và embeddings


## 📂 Cấu trúc dự án

```
smart-document-qa/
├── backend/                    # Backend Python
│   ├── app.py                 # Entry point với Gradio wrapper
│   ├── main.py                # FastAPI application chính
│   ├── requirements.txt       # Dependencies Python
│   ├── docs_api.md           # Tài liệu API
│   ├── render.yaml           # Cấu hình deploy Render.com
│   └── README.md             # Hướng dẫn backend
│
├── frontend/                  # Frontend React
│   ├── public/               # Static assets
│   ├── src/
│   │   ├── Components/       # React components
│   │   │   ├── Sidebar.js
│   │   │   ├── FileUpload.js
│   │   │   └── ChatInterface.js
│   │   ├── App.js
│   │   └── App.css
│   ├── package.json
│   └── README.md             # Hướng dẫn frontend
│
├── .gitignore
├── LICENSE
└── README.md                 # File này
```

## 🚀 Tech Stack

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.10+
- **Vector DB**: ChromaDB (in-memory)
- **Embeddings**: HuggingFace `all-MiniLM-L6-v2`
- **LLM**: Groq API (Llama 3.3 70B)
- **Text Processing**: LangChain, PyPDF

### Frontend
- **Framework**: React 19.2.3
- **HTTP Client**: Axios
- **Styling**: CSS3 custom

## 📦 Cài đặt nhanh

### Yêu cầu hệ thống
- Python 3.10 trở lên
- Node.js 16+ và npm
- Groq API key ([Đăng ký tại đây](https://console.groq.com/keys))

### 1. Clone repository
```bash
git clone https://github.com/itschinh0512/smart-document-qa.git
cd smart-document-qa
```

### 2. Cài đặt Backend
```bash
cd backend

# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo
source venv/bin/activate  # macOS/Linux
# hoặc
venv\Scripts\activate     # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Tạo file .env
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

### 3. Cài đặt Frontend
Mở terminal mới:
```bash
cd frontend

# Cài đặt dependencies
npm install
```

### 4. Chạy ứng dụng

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # Kích hoạt môi trường ảo
python main.py
# Backend chạy tại: http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
# Frontend chạy tại: http://localhost:3000
```

## 🧪 Kiểm tra hệ thống

### Kiểm tra Backend
```bash
# Health check
curl http://localhost:8000/health

# Kiểm tra kết nối AI
curl http://localhost:8000/test-ai

# Xem API documentation
# Truy cập: http://localhost:8000/docs
```

### Kiểm tra Frontend
1. Mở trình duyệt tại `http://localhost:3000`
2. Kiểm tra sidebar hiển thị "System Online"
3. Thử upload một file PDF
4. Đặt câu hỏi về nội dung tài liệu

## 📖 Cách sử dụng

### Bước 1: Tải lên tài liệu
- Click vào nút "Upload PDF" trên giao diện
- Chọn file PDF từ máy tính
- Đợi hệ thống xử lý và lập chỉ mục tài liệu

### Bước 2: Đặt câu hỏi
- Nhập câu hỏi vào ô chat
- Nhấn Enter hoặc click "Ask"
- Hệ thống sẽ:
  1. Tìm kiếm các đoạn văn bản liên quan trong tài liệu
  2. Sử dụng AI để sinh câu trả lời dựa trên ngữ cảnh
  3. Hiển thị câu trả lời kèm nguồn trích dẫn

### Bước 3: Điều chỉnh tham số (tùy chọn)
- Sử dụng thanh trượt "Context Depth (Top-K)" ở sidebar
- Giá trị cao hơn = nhiều ngữ cảnh hơn (chính xác hơn nhưng chậm hơn)
- Giá trị thấp hơn = ít ngữ cảnh hơn (nhanh hơn nhưng có thể thiếu thông tin)

## 🔧 Cấu hình

### Backend
File `.env` trong thư mục `backend/`:
```bash
GROQ_API_KEY=your_groq_api_key
PORT=8000
```

### Frontend
Chỉnh sửa `frontend/src/App.js` dòng 8:
```javascript
const BASE_URL = "http://localhost:8000";  // Cho development
```

Hoặc tạo file `.env` trong `frontend/`:
```bash
REACT_APP_API_URL=http://localhost:8000
```

## 📚 Tài liệu chi tiết

- **Backend**: [backend/README.md](backend/README.md) - Hướng dẫn chi tiết về API, kiến trúc RAG
- **Frontend**: [frontend/README.md](frontend/README.md) - Hướng dẫn về components, styling
- **API Documentation**: [backend/docs_api.md](backend/docs_api.md) - Tài liệu API endpoints

## 🎯 Tính năng chính

✅ Upload và xử lý tài liệu PDF  
✅ Tìm kiếm ngữ nghĩa với vector embeddings  
✅ Sinh câu trả lời thông minh bằng AI (Groq LLM)  
✅ Hiển thị nguồn trích dẫn  
✅ Giao diện chat trực quan  
✅ Điều chỉnh độ sâu ngữ cảnh  
✅ Real-time system monitoring  
✅ RESTful API với tài liệu Swagger  

## 📄 Giấy phép

Xem file [LICENSE](LICENSE) để biết chi tiết
