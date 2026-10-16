# FlashLearn - Nền tảng học tập Flashcard & Ôn thi trắc nghiệm

> Ứng dụng web học tập hiện đại phong cách Quizlet được xây dựng hoàn toàn 100% bằng **React 19**, **TypeScript**, **Vite** và **Tailwind CSS**. Toàn bộ giao diện người dùng, quản lý trạng thái, mô phỏng lật thẻ 3D, thi trắc nghiệm bấm giờ, quản trị viên và xác thực đều sử dụng các React components và React hooks chuẩn mực.

---

## 🚀 Tính năng chính

- **Tổng quan (Dashboard)**: Bảng điều khiển tóm tắt thống kê học tập, lối tắt ôn luyện nhanh các bộ flashcard và đề quiz mới nhất.
- **Flashcard (Cộng đồng & Của tôi)**: 
  - Khám phá các bộ thẻ công khai do cộng đồng chia sẻ.
  - Quản lý bộ flashcard cá nhân, tạo bộ thẻ mới, nhập từ tệp CSV/JSON.
  - Chế độ lật thẻ 3D mượt mà với thanh tiến độ, phím tắt (Space để lật, Mũi tên để chuyển thẻ), tự động phát và xáo trộn thẻ.
- **Quiz (Cộng đồng & Của tôi)**:
  - Danh sách đề thi trắc nghiệm phong phú với chế độ làm bài có đếm ngược thời gian.
  - Chấm điểm tức thì, xem giải thích chi tiết từng câu hỏi và tổng kết kết quả học tập.
- **Lịch sử thi**: Lưu trữ và theo dõi điểm số, số câu đúng và độ chính xác của từng lần làm bài.
- **Xác thực & Tài khoản (Đăng nhập / Đăng ký)**:
  - Trang **Đăng ký** tài khoản mới với username và mật khẩu bảo mật.
  - Trang **Đăng nhập** linh hoạt với 2 phương thức: qua Username + Mật khẩu hoặc trực tiếp qua Email.
- **Khu vực Quản trị (Admin)**:
  - Quản lý danh sách tài khoản người dùng, trạng thái khóa/mở khóa tài khoản và phân quyền.

---

## 🛠️ Công nghệ sử dụng

- **React 19**: Functional components, React Hooks (`useState`, `useMemo`, `useEffect`).
- **TypeScript**: Định kiểu chặt chẽ cho toàn bộ dữ liệu, props và sự kiện.
- **Vite**: Bundler siêu tốc cho ứng dụng web SPA.
- **Tailwind CSS v4**: Hệ thống styling utility-first hiện đại, responsive hoàn hảo trên mọi kích thước màn hình.
- **Lucide React**: Bộ icon hiện đại, trực quan.
- **Canvas Confetti**: Hiệu ứng pháo hoa chúc mừng khi hoàn thành xuất sắc bài thi.

---

## 💻 Khởi chạy dự án

```bash
# 1. Cài đặt các gói phụ thuộc
npm install

# 2. Khởi chạy máy chủ phát triển
npm run dev

# 3. Kiểm tra kiểu TypeScript
npm run lint

# 4. Đóng gói bản build sản xuất
npm run build
```
