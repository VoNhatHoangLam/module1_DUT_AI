# FlashLearn - Nền tảng học tập Flashcard & Ôn thi trắc nghiệm

> Ứng dụng frontend học tập phong cách Quizlet được xây dựng hoàn toàn bằng **Python & Gradio (`gr.Blocks`)** và **React (Vite SPA)**, kết hợp giao diện menu điều hướng thanh Sidebar bên trái hiện đại, bảng màu xanh dương Quizlet và `gr.State` cho trải nghiệm tương tác mượt mà trong bộ nhớ.

---

## 🚀 Hướng dẫn cài đặt & Chạy trên Windows / Linux / macOS

### Yêu cầu tiên quyết
- **Python 3.10+** (đã tích hợp sẵn pip).

### Bước 1: Mở Terminal (Command Prompt / PowerShell trên Windows)
Điều hướng đến thư mục dự án:
```cmd
cd path\to\flashlearn
```

### Bước 2: Tạo và kích hoạt môi trường ảo (Khuyến nghị)
Trên Windows:
```cmd
python -m venv venv
venv\Scripts\activate
```
Trên macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Bước 3: Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

### Bước 4: Khởi chạy ứng dụng Gradio
```bash
python app.py
```

Sau khi chạy lệnh trên, Gradio sẽ khởi động máy chủ cục bộ. Mở trình duyệt web và truy cập địa chỉ:
```
http://127.0.0.1:7860
```

---

## 🧭 Cấu trúc Menu Sidebar & Quy tắc dữ liệu giữa các tab

Giao diện ứng dụng sử dụng **Sidebar cố định ở phía bên trái** với các mục điều hướng dọc:

| Thứ tự | Tên Tab | Icon | Phạm vi dữ liệu hiển thị | Có nút Xóa? | Các nút thao tác phía trên |
| :---: | :--- | :---: | :--- | :---: | :--- |
| **1** | **Tổng quan** | `Layers` | Bảng điều khiển tóm tắt, thống kê số lượng thẻ, bài thi và lối tắt học nhanh. | — | — |
| **2** | **Flashcard** | `Globe` | **Tất cả các bộ flashcard công khai của mọi người** (người dùng đăng công khai trực tiếp ngay lập tức, không cần chờ Admin kiểm duyệt). | ❌ **Không** | Tìm kiếm, Lọc theo chủ đề |
| **3** | **Quiz** | `Award` | **Tất cả các bộ đề thi trắc nghiệm công khai, đã duyệt của mọi người**. Bấm giờ làm bài, chấm điểm và xem lời giải chi tiết. | ❌ Không | 📥 **“Nhập từ file”** & ➕ **“Tạo bộ thẻ mới”** |
| **4** | **Lịch sử thi** | `Clock` | Lịch sử toàn bộ các lần làm bài thi trắc nghiệm (ngày thi, số câu đúng, tỷ lệ % chính xác). | — | — |
| **5** | **Flashcard của tôi** | `BookmarkCheck` | **Chỉ các bộ flashcard do người dùng hiện tại sở hữu**. Không hiển thị bộ thẻ của người khác. | ✅ **Có** (kèm hộp thoại xác nhận) | 📥 **“Nhập từ file”** & ➕ **“Tạo bộ thẻ mới”** |
| **6** | **Quản trị (Admin)** | `Shield` | Dành cho tài khoản Admin: Thống kê số liệu, quản lý tài khoản người dùng, **quản lý bộ thẻ Flashcard (chỉ Xem và Xóa bộ thẻ)**. | — | — |

> **Ghi chú về hoán đổi vị trí & quy trình:**
> - Tab **“Flashcard”** nằm ở vị trí thứ 2, và tab **“Flashcard của tôi”** ở vị trí thứ 5.
> - **Đăng flashcard:** Người dùng có thể đăng bộ thẻ công khai ngay lập tức không cần chờ Admin kiểm duyệt.
> - **Admin Flashcard:** Chỉ giữ lại chức năng xem và xóa bộ thẻ; đã loại bỏ các nút duyệt, từ chối, ẩn.

---

## 🔑 Tài khoản Demo & Chuyển đổi vai trò

Ứng dụng hoạt động với dữ liệu mẫu trong bộ nhớ (`in-memory mock state`), không cần cấu hình database hay API bên ngoài.

| Vai trò | Email đăng nhập | Mật khẩu | Mô tả quyền hạn |
| :--- | :--- | :--- | :--- |
| **Học viên (User)** | `user@flashlearn.vn` | `********` | Sở hữu các bộ thẻ cá nhân trong tab **“Flashcard của tôi”**, xóa bộ thẻ cá nhân, đăng bộ thẻ công khai ngay lập tức, làm bài **“Quiz”**, tạo đề quiz mới. |
| **Học viên khác** | `maianh@flashlearn.vn` | `********` | Học viên chuyên ngữ IELTS, sở hữu các bộ từ vựng Academic riêng biệt. |
| **Quản trị viên (Admin)** | `admin@flashlearn.vn` | `********` | Xem toàn bộ thống kê hệ thống, quản lý khóa/mở khóa tài khoản, xem và xóa các bộ thẻ Flashcard, kiểm duyệt đề thi Quiz (Duyệt/Từ chối). |

*Lưu ý:* Bạn có thể chuyển nhanh vai trò bất cứ lúc nào thông qua nút chọn vai trò **"Học viên / Admin"** ở góc dưới cùng của sidebar bên trái.

---

## 📂 Cấu trúc thư mục

```text
flashlearn/
├── app.py                      # Mã nguồn Python chính chạy Gradio (Blocks, State & Callbacks)
├── requirements.txt            # Danh sách thư viện Python (gradio, pandas, plotly, openpyxl)
├── README.md                   # Hướng dẫn chi tiết cài đặt và sử dụng
├── assets/
│   └── style.css               # Tệp CSS phong cách Quizlet (hiệu ứng 3D lật thẻ, bảng màu xanh dương)
└── sample_data/
    ├── flashcards.csv          # Tệp dữ liệu mẫu bộ Flashcard để nhập thử nghiệm
    └── quiz_questions.csv      # Tệp dữ liệu mẫu câu hỏi trắc nghiệm để nhập thử nghiệm
```
