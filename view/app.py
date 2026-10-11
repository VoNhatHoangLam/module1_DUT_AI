"""
FlashLearn - Nền tảng học tập Flashcard & Ôn thi trắc nghiệm phong cách Quizlet
Xây dựng hoàn toàn bằng Python và Gradio (gr.Blocks) với CSS tùy biến cao cấp.

Chạy ứng dụng:
    pip install -r requirements.txt
    python app.py
"""

import json
import random
import os
import io
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import gradio as gr

# ==============================================================================
# 1. DỮ LIỆU MẪU BAN ĐẦU (IN-MEMORY MOCK DATA)
# ==============================================================================

INITIAL_USERS = [
    {
        "id": "u1",
        "name": "Nguyễn Hoàng Nam",
        "email": "user@flashlearn.vn",
        "role": "user",
        "avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=Nam",
        "join_date": "2024-01-15",
        "status": "Hoạt động",
        "bio": "Sinh viên năm 3 ngành Công nghệ thông tin ĐHQG",
    },
    {
        "id": "u2",
        "name": "Trần Thị Mai Anh",
        "email": "maianh@flashlearn.vn",
        "role": "user",
        "avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=MaiAnh",
        "join_date": "2024-02-10",
        "status": "Hoạt động",
        "bio": "Học viên IELTS 7.5+ & Data Science",
    },
    {
        "id": "u3",
        "name": "Quản Trị Viên (Admin)",
        "email": "admin@flashlearn.vn",
        "role": "admin",
        "avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=AdminBoss",
        "join_date": "2023-11-01",
        "status": "Hoạt động",
        "bio": "Trưởng ban quản trị hệ thống FlashLearn",
    },
    {
        "id": "u4",
        "name": "Lê Viết Dũng",
        "email": "dung.spammer@temp.vn",
        "role": "user",
        "avatar": "https://api.dicebear.com/7.x/bottts/svg?seed=Dung",
        "join_date": "2024-03-01",
        "status": "Bị khóa",
        "bio": "Tài khoản vi phạm tiêu chuẩn cộng đồng",
    },
]

INITIAL_FLASHCARD_SETS = [
    {
        "id": "set_1",
        "title": "Khoa học máy tính & Thuật toán cốt lõi",
        "description": "Các thuật ngữ, cấu trúc dữ liệu và giải thuật căn bản cho kỹ sư phần mềm.",
        "category": "Công nghệ thông tin",
        "created_by": "Nguyễn Hoàng Nam",
        "user_id": "u1",
        "privacy": "Công khai",
        "status": "approved",  # approved, pending, rejected
        "updated_at": "2024-03-12",
        "cards": [
            {"term": "Binary Search", "definition": "Thuật toán tìm kiếm nhị phân trên mảng đã sắp xếp với độ phức tạp O(log n)."},
            {"term": "Hash Table", "definition": "Cấu trúc dữ liệu ánh xạ khóa (key) thành giá trị (value) với thời gian tra cứu trung bình O(1)."},
            {"term": "Dynamic Programming", "definition": "Phương pháp tối ưu hóa bài toán bằng cách chia thành các bài toán con trùng lặp và lưu trữ kết quả."},
            {"term": "Graph Dijkstra", "definition": "Thuật toán tìm đường đi ngắn nhất từ một đỉnh nguồn đến các đỉnh còn lại trong đồ thị có trọng số không âm."},
            {"term": "Polymorphism (Đa hình)", "definition": "Khả năng các đối tượng khác nhau phản hồi cùng một thông điệp hoặc phương thức theo cách riêng."},
            {"term": "Overfitting", "definition": "Hiện tượng mô hình Machine Learning học quá kỹ tập huấn luyện dẫn đến dự đoán kém trên tập kiểm thử."},
        ],
    },
    {
        "id": "set_2",
        "title": "Từ vựng IELTS Academic 7.5+ Chuyên sâu",
        "description": "Bộ từ vựng học thuật thường xuất hiện trong Reading và Writing Task 2.",
        "category": "Ngoại ngữ",
        "created_by": "Trần Thị Mai Anh",
        "user_id": "u2",
        "privacy": "Công khai",
        "status": "approved",
        "updated_at": "2024-03-14",
        "cards": [
            {"term": "Ubiquitous", "definition": "Present, appearing, or found everywhere (Phổ biến khắp nơi, có mặt ở mọi nơi)."},
            {"term": "Pragmatic", "definition": "Dealing with things sensibly and realistically (Thực dụng, thực tế, đề cao tính ứng dụng)."},
            {"term": "Mitigate", "definition": "Make less severe, serious, or painful (Làm giảm bớt, làm dịu đi tác động tiêu cực)."},
            {"term": "Exacerbate", "definition": "Make a problem, bad situation, or negative feeling worse (Làm trầm trọng thêm)."},
            {"term": "Paradigm shift", "definition": "A fundamental change in approach or underlying assumptions (Sự chuyển dịch mô thức cơ bản)."},
        ],
    },
    {
        "id": "set_3",
        "title": "DevOps & Cloud Architecture (AWS/GCP/Docker)",
        "description": "Các khái niệm microservices, containerization và CI/CD pipelines.",
        "category": "Công nghệ thông tin",
        "created_by": "Nguyễn Hoàng Nam",
        "user_id": "u1",
        "privacy": "Riêng tư",
        "status": "approved",
        "updated_at": "2024-03-10",
        "cards": [
            {"term": "Containerization", "definition": "Đóng gói mã nguồn cùng các thư viện phụ thuộc thành một đơn vị độc lập chạy nhất quán."},
            {"term": "Kubernetes Pod", "definition": "Đơn vị tính toán nhỏ nhất có thể triển khai trong Kubernetes, chứa một hoặc nhiều containers."},
            {"term": "Blue/Green Deployment", "definition": "Kỹ thuật phát hành ứng dụng với 2 môi trường giống nhau để giảm thiểu thời gian downtime."},
        ],
    },
    {
        "id": "set_4",
        "title": "Tâm lý học hành vi trong thiết kế UX",
        "description": "Bộ thẻ chờ kiểm duyệt của cộng đồng về nguyên lý tâm lý học ứng dụng.",
        "category": "Thiết kế & Nghệ thuật",
        "created_by": "Lê Viết Dũng",
        "user_id": "u4",
        "privacy": "Công khai",
        "status": "pending",
        "updated_at": "2024-03-15",
        "cards": [
            {"term": "Hick's Law", "definition": "Thời gian đưa ra quyết định tăng theo số lượng và độ phức tạp của các lựa chọn."},
            {"term": "Fitts's Law", "definition": "Thời gian di chuyển đến một mục tiêu phụ thuộc vào khoảng cách và kích thước của mục tiêu đó."},
        ],
    },
    {
        "id": "set_5",
        "title": "Ngữ pháp tiếng Anh B2 - C1 Học thuật",
        "description": "Cấu trúc đảo ngữ, mệnh đề rút gọn và câu điều kiện hỗn hợp nâng cao.",
        "category": "Ngoại ngữ",
        "created_by": "Trần Thị Mai Anh",
        "user_id": "u2",
        "privacy": "Công khai",
        "status": "approved",
        "updated_at": "2024-03-18",
        "cards": [
            {"term": "Inversion with Negative Adverbials", "definition": "Hardly/Scarcely + had + S + V3 when..."},
            {"term": "Mixed Conditionals (Type 3 + 2)", "definition": "If + had V3, S + would V (Điều kiện trái quá khứ dẫn đến kết quả hiện tại)."},
        ],
    },
]

INITIAL_QUIZ_SETS = [
    {
        "id": "quiz_1",
        "title": "Kiểm tra kiến thức Công nghệ phần mềm & Thuật toán",
        "description": "Bài thi trắc nghiệm đánh giá kiến thức thuật toán, REST API và lập trình hướng đối tượng.",
        "category": "Công nghệ thông tin",
        "created_by": "Nguyễn Hoàng Nam",
        "user_id": "u1",
        "privacy": "Công khai",
        "status": "approved",
        "time_limit_minutes": 10,
        "questions": [
            {
                "id": 1,
                "question": "Độ phức tạp thời gian trung bình của thuật toán tìm kiếm nhị phân (Binary Search) là bao nhiêu?",
                "option_a": "O(1)",
                "option_b": "O(n)",
                "option_c": "O(log n)",
                "option_d": "O(n log n)",
                "correct_answer": "C",
                "explanation": "Binary Search chia đôi không gian tìm kiếm sau mỗi bước nên có độ phức tạp thời gian trung bình là O(log n).",
            },
            {
                "id": 2,
                "question": "Phương thức HTTP nào sau đây được thiết kế để cập nhật một phần (partial update) tài nguyên trong RESTful API?",
                "option_a": "GET",
                "option_b": "POST",
                "option_c": "PATCH",
                "option_d": "PUT",
                "correct_answer": "C",
                "explanation": "PATCH dùng để cập nhật một phần tài nguyên hiện có; trong khi PUT thường thay thế toàn bộ tài nguyên.",
            },
            {
                "id": 3,
                "question": "Nguyên lý nào trong OOP cho phép lớp con kế thừa các thuộc tính và hành vi của lớp cha?",
                "option_a": "Encapsulation (Đóng gói)",
                "option_b": "Inheritance (Kế thừa)",
                "option_c": "Polymorphism (Đa hình)",
                "option_d": "Abstraction (Trừu tượng)",
                "correct_answer": "B",
                "explanation": "Inheritance (Kế thừa) cho phép tái sử dụng mã nguồn và xây dựng thứ bậc phân lớp logic.",
            },
            {
                "id": 4,
                "question": "Hiện tượng Overfitting trong Machine Learning thường xuất hiện khi nào?",
                "option_a": "Mô hình quá đơn giản và thiếu tham số",
                "option_b": "Mô hình học quá sát tập dữ liệu huấn luyện kể cả nhiễu",
                "option_c": "Hệ số phạt Regularization được đặt quá cao",
                "option_d": "Dữ liệu huấn luyện có quá ít ngoại lai",
                "correct_answer": "B",
                "explanation": "Overfitting xảy ra khi mô hình quá khớp với dữ liệu train, dẫn đến giảm sút độ chính xác trên dữ liệu mới.",
            },
        ],
    },
    {
        "id": "quiz_2",
        "title": "Thử thách trắc nghiệm IELTS Academic Vocabulary",
        "description": "Kiểm tra mức độ thành thạo và ngữ cảnh sử dụng của các từ vựng học thuật C1/C2.",
        "category": "Ngoại ngữ",
        "created_by": "Trần Thị Mai Anh",
        "user_id": "u2",
        "privacy": "Công khai",
        "status": "approved",
        "time_limit_minutes": 15,
        "questions": [
            {
                "id": 1,
                "question": "Từ nào sau đây đồng nghĩa với 'Ubiquitous'?",
                "option_a": "Omnipresent",
                "option_b": "Scary",
                "option_c": "Obsolete",
                "option_d": "Fragile",
                "correct_answer": "A",
                "explanation": "Ubiquitous và Omnipresent đều mang nghĩa xuất hiện ở khắp mọi nơi.",
            },
            {
                "id": 2,
                "question": "Chọn từ thích hợp điền vào chỗ trống: 'The government took urgent steps to ___ the effects of the drought.'",
                "option_a": "exacerbate",
                "option_b": "mitigate",
                "option_c": "deteriorate",
                "option_d": "provoke",
                "correct_answer": "B",
                "explanation": "'Mitigate' có nghĩa là làm giảm nhẹ hoặc giảm thiểu tác hại.",
            },
        ],
    },
]

INITIAL_QUIZ_HISTORY = [
    {
        "history_id": "h1",
        "quiz_title": "Kiểm tra kiến thức Công nghệ phần mềm & Thuật toán",
        "taken_date": "2024-03-14 14:32",
        "score": 100,
        "correct_answers": "4/4",
        "accuracy_pct": "100%",
        "status": "Hoàn thành",
    },
    {
        "history_id": "h2",
        "quiz_title": "Thử thách trắc nghiệm IELTS Academic Vocabulary",
        "taken_date": "2024-03-12 09:15",
        "score": 50,
        "correct_answers": "1/2",
        "accuracy_pct": "50%",
        "status": "Hoàn thành",
    },
]

# ==============================================================================
# 2. LOGIC XỬ LÝ DỮ LIỆU & TIỆN ÍCH
# ==============================================================================

def create_admin_charts(users, flashcard_sets, quiz_sets, history):
    """Tạo biểu đồ thống kê Plotly cho bảng điều khiển Admin."""
    cat_counts = {}
    for s in flashcard_sets:
        cat_counts[s["category"]] = cat_counts.get(s["category"], 0) + 1
    
    df_cat = pd.DataFrame(list(cat_counts.items()), columns=["Chủ đề", "Số bộ flashcard"])
    fig_cat = px.bar(
        df_cat,
        x="Chủ đề",
        y="Số bộ flashcard",
        title="Phân bố Flashcard theo chủ đề",
        color="Chủ đề",
        color_discrete_sequence=["#2563eb", "#38bdf8", "#10b981", "#f59e0b"]
    )
    fig_cat.update_layout(showlegend=False, margin=dict(l=20, r=20, t=40, b=20), height=300)

    statuses = [s["status"] for s in flashcard_sets] + [q["status"] for q in quiz_sets]
    status_df = pd.DataFrame({"Trạng thái": statuses})
    status_counts = status_df["Trạng thái"].value_counts().reset_index()
    status_counts.columns = ["Trạng thái", "Số lượng"]
    status_map = {"approved": "Đã duyệt", "pending": "Chờ duyệt", "rejected": "Từ chối", "hidden": "Ẩn"}
    status_counts["Trạng thái"] = status_counts["Trạng thái"].map(lambda x: status_map.get(x, x))
    
    fig_pie = px.pie(
        status_counts,
        names="Trạng thái",
        values="Số lượng",
        title="Tỷ lệ kiểm duyệt nội dung hệ thống",
        color_discrete_sequence=["#10b981", "#f59e0b", "#ef4444", "#64748b"]
    )
    fig_pie.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=300)

    return fig_cat, fig_pie

# ==============================================================================
# 3. GIAO DIỆN CHÍNH DÙNG GRADIO BLOCKS
# ==============================================================================

def build_app():
    custom_css = """
    .gradio-container {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
        background-color: #f8fafc !important;
    }
    .flashcard-box {
        background: linear-gradient(145deg, #ffffff, #eff6ff);
        border: 2px solid #bfdbfe;
        border-radius: 20px;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.15);
        padding: 3rem 2rem;
        min-height: 280px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
    }
    .flashcard-box:hover {
        border-color: #3b82f6;
        transform: translateY(-2px);
        box-shadow: 0 15px 30px -5px rgba(37, 99, 235, 0.25);
    }
    .hero-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 18px;
        box-shadow: 0 10px 20px -3px rgba(30, 58, 138, 0.3);
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid #e2e8f0;
        text-align: center;
    }
    """

    with gr.Blocks(title="FlashLearn - Nền tảng học tập Flashcard & Trắc nghiệm", css=custom_css, theme=gr.themes.Default(primary_hue="blue")) as demo:
        # State lưu trữ toàn bộ ứng dụng
        state_current_user = gr.State(INITIAL_USERS[0])  # u1 mặc định
        state_current_role = gr.State("user")  # guest, user, admin
        state_flashcard_sets = gr.State(INITIAL_FLASHCARD_SETS)
        state_quiz_sets = gr.State(INITIAL_QUIZ_SETS)
        state_quiz_history = gr.State(INITIAL_QUIZ_HISTORY)
        state_users = gr.State(INITIAL_USERS)
        
        # State phục vụ ôn tập (Study Mode)
        state_active_study_set = gr.State(INITIAL_FLASHCARD_SETS[0])
        state_study_cards = gr.State(INITIAL_FLASHCARD_SETS[0]["cards"])
        state_study_index = gr.State(0)
        state_study_is_flipped = gr.State(False)
        state_study_known_indices = gr.State([])
        state_study_unknown_indices = gr.State([])

        # State phục vụ làm bài trắc nghiệm (Quiz Mode)
        state_active_quiz_set = gr.State(INITIAL_QUIZ_SETS[0])
        state_quiz_q_index = gr.State(0)
        state_quiz_user_answers = gr.State({})
        state_quiz_submitted = gr.State(False)

        # Header chung & Chuyển đổi nhanh chế độ demo
        with gr.Row(variant="compact"):
            with gr.Column(scale=8):
                gr.HTML("""
                <div style="display: flex; align-items: center; gap: 12px; padding: 10px 0;">
                    <div style="background: #2563eb; color: white; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 24px; box-shadow: 0 4px 10px rgba(37,99,235,0.3);">⚡</div>
                    <div>
                        <h2 style="margin: 0; font-size: 1.5rem; color: #1e3a8a; font-weight: 800; letter-spacing: -0.5px;">FlashLearn</h2>
                        <p style="margin: 0; font-size: 0.85rem; color: #64748b;">Nền tảng ôn tập Flashcard 3D & Thi trắc nghiệm thông minh</p>
                    </div>
                </div>
                """)
            with gr.Column(scale=4):
                role_selector = gr.Radio(
                    choices=["Học viên (User)", "Quản trị viên (Admin)"],
                    value="Học viên (User)",
                    label="Chuyển chế độ xem demo",
                    interactive=True,
                )

        # ======================================================================
        # TAB 1: TỔNG QUAN / GIỚI THIỆU (GUEST & OVERVIEW)
        # ======================================================================
        with gr.Tab("🌟 Tổng quan & Khám phá") as tab_overview:
            with gr.Row():
                with gr.Column(scale=12):
                    gr.HTML("""
                    <div class="hero-card">
                        <span style="background: rgba(255,255,255,0.25); padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">Phương pháp Spaced Repetition</span>
                        <h1 style="font-size: 2.5rem; margin: 12px 0; font-weight: 800;">Chinh phục mọi kỳ thi với FlashLearn</h1>
                        <p style="font-size: 1.15rem; max-width: 750px; opacity: 0.95; line-height: 1.6;">
                            Học từ vựng, thuật ngữ chuyên ngành và giải bài trắc nghiệm với trải nghiệm lật thẻ trực quan, ghi nhớ sâu hơn 80% so với phương pháp đọc truyền thống.
                        </p>
                    </div>
                    """)

        # ======================================================================
        # TAB 2: FLASHCARD (HOÁN ĐỔI VỊ TRÍ: HIỂN THỊ TẤT CẢ BỘ THẺ CÔNG KHAI, KHÔNG CÓ NÚT XÓA)
        # ======================================================================
        with gr.Tab("🌐 Flashcard") as tab_community:
            gr.Markdown("### 🌍 Khám phá tất cả các bộ Flashcard công khai của mọi người")
            with gr.Row():
                comm_search = gr.Textbox(placeholder="Tìm kiếm bộ flashcard công khai...", label="Tìm kiếm", scale=8)
                comm_filter = gr.Dropdown(choices=["Tất cả chủ đề", "Công nghệ thông tin", "Ngoại ngữ"], value="Tất cả chủ đề", label="Chủ đề", scale=4)

            def get_community_df(sets_list):
                rows = []
                for s in sets_list:
                    if s["privacy"] == "Công khai" and s["status"] == "approved":
                        rows.append({
                            "Bộ thẻ": s["title"],
                            "Chủ đề": s["category"],
                            "Tác giả": s["created_by"],
                            "Số thẻ": len(s["cards"]),
                            "Cập nhật": s["updated_at"]
                        })
                return pd.DataFrame(rows)

            comm_df_view = gr.DataFrame(
                value=get_community_df(INITIAL_FLASHCARD_SETS),
                interactive=False,
                label="Danh sách Flashcard công khai (Không hiển thị nút xóa)"
            )

        # ======================================================================
        # TAB 3: QUIZ (BÀI THI TRẮC NGHIỆM CŨ - 2 NÚT THAO TÁC "Nhập từ file" VÀ "Tạo bộ thẻ mới")
        # ======================================================================
        with gr.Tab("📝 Quiz") as tab_quiz:
            gr.Markdown("### 📋 Danh sách bài thi Quiz trắc nghiệm công khai")
            with gr.Row():
                btn_quiz_import = gr.Button("📥 Nhập từ file", scale=6)
                btn_quiz_create = gr.Button("➕ Tạo bộ thẻ mới", variant="primary", scale=6)

            with gr.Row():
                quiz_header_display = gr.Markdown(f"#### 📖 Đề thi đang chọn: **{INITIAL_QUIZ_SETS[0]['title']}**")
                quiz_q_progress = gr.Markdown(f"**Câu hỏi 1 / {len(INITIAL_QUIZ_SETS[0]['questions'])}**")

            quiz_question_text = gr.Markdown(
                f"### **Câu 1:** {INITIAL_QUIZ_SETS[0]['questions'][0]['question']}"
            )

            quiz_radio_options = gr.Radio(
                choices=[
                    f"A. {INITIAL_QUIZ_SETS[0]['questions'][0]['option_a']}",
                    f"B. {INITIAL_QUIZ_SETS[0]['questions'][0]['option_b']}",
                    f"C. {INITIAL_QUIZ_SETS[0]['questions'][0]['option_c']}",
                    f"D. {INITIAL_QUIZ_SETS[0]['questions'][0]['option_d']}",
                ],
                label="Chọn đáp án:",
                value=None
            )

            with gr.Row():
                btn_quiz_prev = gr.Button("⬅️ Câu trước")
                btn_quiz_next = gr.Button("Câu tiếp theo ➡️")
                btn_quiz_submit = gr.Button("🏁 NỘP BÀI THI", variant="primary")

            with gr.Accordion("📊 Kết quả và Lời giải chi tiết", open=False) as quiz_result_accordion:
                quiz_result_summary = gr.HTML("<p>Chưa có kết quả.</p>")
                quiz_explanation_view = gr.Markdown("")

        # ======================================================================
        # TAB 4: LỊCH SỬ THI
        # ======================================================================
        with gr.Tab("📜 Lịch sử thi") as tab_history:
            gr.Markdown("### 📜 Lịch sử các lần làm bài thi trắc nghiệm")
            history_df_view = gr.DataFrame(
                value=pd.DataFrame(INITIAL_QUIZ_HISTORY),
                interactive=False
            )

        # ======================================================================
        # TAB 5: FLASHCARD CỦA TÔI (HOÁN ĐỔI VỊ TRÍ: CHỈ HIỂN THỊ CÁ NHÂN, CÓ NÚT XÓA)
        # ======================================================================
        with gr.Tab("📚 Flashcard của tôi") as tab_my_sets:
            gr.Markdown("### 🗂️ Quản lý các bộ Flashcard cá nhân của bạn")
            
            def get_my_sets_dataframe(sets_list, current_user_id="u1"):
                filtered = []
                for s in sets_list:
                    if s["user_id"] == current_user_id:
                        filtered.append({
                            "ID": s["id"],
                            "Tên bộ Flashcard": s["title"],
                            "Chủ đề": s["category"],
                            "Số thẻ": len(s["cards"]),
                            "Chế độ": s["privacy"],
                            "Trạng thái": s["status"],
                            "Cập nhật": s["updated_at"]
                        })
                return pd.DataFrame(filtered)

            my_sets_df_view = gr.DataFrame(
                value=get_my_sets_dataframe(INITIAL_FLASHCARD_SETS, "u1"),
                interactive=False,
                label="Bộ flashcard cá nhân của tôi"
            )

            with gr.Accordion("⚙️ Thao tác với bộ thẻ cá nhân (Bao gồm Xóa)", open=True):
                with gr.Row():
                    my_selected_set_id = gr.Dropdown(
                        choices=[s["id"] for s in INITIAL_FLASHCARD_SETS if s["user_id"] == "u1"],
                        value=INITIAL_FLASHCARD_SETS[0]["id"],
                        label="Chọn mã bộ thẻ cá nhân"
                    )
                    btn_study_my_set = gr.Button("🎯 Ôn tập bộ này", variant="primary")
                    btn_delete_my_set = gr.Button("🗑️ XÓA BỘ THẺ NÀY", variant="stop")

                delete_status_msg = gr.Markdown("")

        # ======================================================================
        # TAB 6: ÔN TẬP LẬT THẺ (STUDY MODE)
        # ======================================================================
        with gr.Tab("🎴 Ôn tập lật thẻ (Study Mode)") as tab_study:
            gr.HTML("""
            <div style="text-align: center; margin-bottom: 1rem;">
                <h2 style="color: #1e3a8a; margin: 0; font-weight: 800;">Chế độ ôn tập Flashcard 3D</h2>
                <p style="color: #64748b; margin: 4px 0 0 0;">Nhấn vào thẻ hoặc nút 'Lật thẻ' để xem định nghĩa.</p>
            </div>
            """)

            with gr.Row():
                study_set_title_display = gr.Markdown(f"### 📖 Bộ thẻ: **{INITIAL_FLASHCARD_SETS[0]['title']}**")
                study_progress_badge = gr.Markdown(f"**Tiến độ: 1 / {len(INITIAL_FLASHCARD_SETS[0]['cards'])}**")

            with gr.Row():
                with gr.Column(scale=2):
                    pass
                with gr.Column(scale=8):
                    card_content_html = gr.HTML(
                        value=f"""
                        <div class="flashcard-box">
                            <span style="color: #64748b; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">MẶT TRƯỚC (THUẬT NGỮ)</span>
                            <div style="font-size: 1.85rem; font-weight: 800; color: #1e3a8a; line-height: 1.4;">
                                {INITIAL_FLASHCARD_SETS[0]['cards'][0]['term']}
                            </div>
                        </div>
                        """
                    )
                with gr.Column(scale=2):
                    pass

            with gr.Row():
                btn_prev_card = gr.Button("⬅️ Thẻ trước", scale=2)
                btn_flip_card = gr.Button("🔄 LẬT THẺ (FLIP)", variant="primary", scale=4)
                btn_next_card = gr.Button("Thẻ tiếp ➡️", scale=2)

        # ======================================================================
        # TAB 7: QUẢN TRỊ VIÊN (ADMIN DASHBOARD)
        # ======================================================================
        with gr.Tab("🛡️ Quản trị hệ thống (Admin)") as tab_admin:
            gr.Markdown("### 🛡️ Bảng điều khiển Quản trị viên FlashLearn")
            fig1, fig2 = create_admin_charts(INITIAL_USERS, INITIAL_FLASHCARD_SETS, INITIAL_QUIZ_SETS, INITIAL_QUIZ_HISTORY)
            with gr.Row():
                chart_category = gr.Plot(value=fig1, label="Thống kê chủ đề", scale=6)
                chart_moderation = gr.Plot(value=fig2, label="Trạng thái kiểm duyệt", scale=6)

        # ======================================================================
        # CALLBACKS
        # ======================================================================
        def update_flashcard_ui(cards, index, is_flipped):
            if not cards:
                return "<div class='flashcard-box'><h3>Không có thẻ nào</h3></div>", "Tiến độ: 0/0"
            idx = max(0, min(index, len(cards) - 1))
            card = cards[idx]
            if not is_flipped:
                html = f"""
                <div class="flashcard-box">
                    <span style="color: #64748b; font-size: 0.85rem; font-weight: 700; margin-bottom: 12px;">MẶT TRƯỚC</span>
                    <div style="font-size: 2rem; font-weight: 800; color: #1e3a8a;">{card['term']}</div>
                </div>
                """
            else:
                html = f"""
                <div class="flashcard-box" style="background: #dbeafe;">
                    <span style="color: #2563eb; font-size: 0.85rem; font-weight: 700; margin-bottom: 12px;">MẶT SAU</span>
                    <div style="font-size: 1.55rem; font-weight: 700; color: #1e3a8a;">{card['definition']}</div>
                </div>
                """
            badge = f"**Tiến độ: {idx + 1} / {len(cards)}**"
            return html, badge

        def flip_card(is_flipped, cards, idx):
            new_flipped = not is_flipped
            html, badge = update_flashcard_ui(cards, idx, new_flipped)
            return new_flipped, html

        btn_flip_card.click(
            flip_card,
            inputs=[state_study_is_flipped, state_study_cards, state_study_index],
            outputs=[state_study_is_flipped, card_content_html]
        )

        def next_card(idx, cards):
            new_idx = min(idx + 1, len(cards) - 1)
            html, badge = update_flashcard_ui(cards, new_idx, False)
            return new_idx, False, html, badge

        btn_next_card.click(
            next_card,
            inputs=[state_study_index, state_study_cards],
            outputs=[state_study_index, state_study_is_flipped, card_content_html, study_progress_badge]
        )

        def prev_card(idx, cards):
            new_idx = max(0, idx - 1)
            html, badge = update_flashcard_ui(cards, new_idx, False)
            return new_idx, False, html, badge

        btn_prev_card.click(
            prev_card,
            inputs=[state_study_index, state_study_cards],
            outputs=[state_study_index, state_study_is_flipped, card_content_html, study_progress_badge]
        )

        # Xóa bộ thẻ cá nhân trong tab "Flashcard của tôi"
        def delete_my_set(set_id, all_sets):
            updated = [s for s in all_sets if s["id"] != set_id]
            df = get_my_sets_dataframe(updated, "u1")
            return updated, df, f"✅ Đã xóa bộ thẻ `{set_id}` khỏi dữ liệu cá nhân!"

        btn_delete_my_set.click(
            delete_my_set,
            inputs=[my_selected_set_id, state_flashcard_sets],
            outputs=[state_flashcard_sets, my_sets_df_view, delete_status_msg]
        )

    return demo

if __name__ == "__main__":
    app = build_app()
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)
