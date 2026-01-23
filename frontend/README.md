# Smart Document Q&A - Frontend

Giao diện web React cho hệ thống hỏi đáp tài liệu thông minh.

## 📋 Tổng quan

Frontend cung cấp giao diện người dùng trực quan để:
- 📤 Upload tài liệu PDF
- 💬 Đặt câu hỏi trong giao diện chat
- 📊 Theo dõi trạng thái hệ thống
- ⚙️ Điều chỉnh tham số truy xuất (Top-K)

## 🛠️ Tech Stack

- **Framework**: React 19.2.3
- **HTTP Client**: Axios 1.13.2
- **Styling**: CSS3 custom (không sử dụng UI library)
- **Build Tool**: Create React App (react-scripts 5.0.1)
- **Testing**: React Testing Library

## 📦 Cài đặt

### Bước 1: Cài đặt dependencies
```bash
cd frontend
npm install
```

### Bước 2: Cấu hình backend URL

**Cách 1: Chỉnh sửa trực tiếp trong code**

Mở `src/App.js` và chỉnh sửa dòng 8:
```javascript
// Cho development local
const BASE_URL = "http://localhost:8000";

// Cho production
const BASE_URL = "https://your-backend-url.onrender.com";
```

**Cách 2: Sử dụng environment variables (Khuyến nghị)**

Tạo file `.env` trong thư mục `frontend/`:
```bash
REACT_APP_API_URL=http://localhost:8000
```

Sau đó cập nhật `src/App.js`:
```javascript
const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";
```

## ▶️ Chạy ứng dụng

### Development mode
```bash
npm start
```
- Ứng dụng mở tại: `http://localhost:3000`
- Auto-reload khi có thay đổi code
- Hiển thị errors và warnings trong console

### Production build
```bash
npm run build
```
- Tạo thư mục `build/` với code đã tối ưu
- Sẵn sàng deploy lên server

### Chạy production build locally
```bash
# Cài đặt serve (nếu chưa có)
npm install -g serve

# Serve production build
serve -s build -p 3000
```

## 🧪 Kiểm tra hệ thống

### Bước 1: Chạy backend trước
Đảm bảo backend đang chạy tại `http://localhost:8000`

### Bước 2: Khởi động frontend
```bash
npm start
```

### Bước 3: Kiểm tra kết nối
1. Mở `http://localhost:3000` trong trình duyệt
2. Kiểm tra sidebar bên trái
3. Status badge phải hiển thị: **"● System Online"** (màu xanh)
4. Nếu hiển thị "Offline" (màu đỏ):
   - Kiểm tra backend có đang chạy không
   - Kiểm tra `BASE_URL` có đúng không
   - Xem browser console có lỗi gì không

### Bước 4: Test upload PDF
1. Click nút "Upload PDF"
2. Chọn một file PDF từ máy tính
3. Đợi thông báo "Document indexed successfully!"
4. Kiểm tra sidebar:
   - "Total Documents" phải tăng lên
   - (Lưu ý: Hiện đang hiển thị số chunks, không phải số documents)

### Bước 5: Test hỏi đáp
1. Nhập câu hỏi vào ô input, ví dụ: "Tài liệu này nói về gì?"
2. Nhấn Enter hoặc click nút "Ask"
3. Quan sát:
   - Hiển thị "AI is searching and generating..." trong khi xử lý
   - Sau 2-4 giây, câu trả lời xuất hiện
   - Câu trả lời phải liên quan đến nội dung PDF

### Bước 6: Test điều chỉnh Top-K
1. Kéo thanh trượt "Context Depth (Top-K)" ở sidebar
2. Thử với giá trị khác nhau (1-10)
3. Đặt cùng một câu hỏi với Top-K khác nhau
4. So sánh độ chi tiết của câu trả lời

### Bước 7: Chạy unit tests
```bash
npm test
```

## 📂 Cấu trúc components

```
frontend/src/
├── Components/
│   ├── Sidebar.js          # Thanh bên trái
│   │   ├── System status
│   │   ├── Document stats
│   │   └── Top-K slider
│   │
│   ├── FileUpload.js       # Upload PDF
│   │   ├── File input
│   │   ├── Upload button
│   │   └── Loading state
│   │
│   └── ChatInterface.js    # Giao diện chat
│       ├── Messages list
│       ├── Auto-scroll
│       ├── Input box
│       └── Typing indicator
│
├── App.js                  # Component chính
├── App.css                 # Styles chính
├── index.js                # React entry point
└── index.css               # Global styles
```

## 🚢 Deployment

### Netlify
```bash
npm install -g netlify-cli
netlify deploy

# Hoặc dùng Netlify dashboard:
# 1. Connect GitHub repo
# 2. Build command: npm run build
# 3. Publish directory: build
# 4. Add environment variable: REACT_APP_API_URL
```
