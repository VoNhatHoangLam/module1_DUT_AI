"""Nghiệp vụ quản lý bài kiểm tra (Quiz) và câu hỏi trắc nghiệm (Question)."""

from __future__ import annotations

import csv
import io
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Optional

from config import DATA_DIR
from models import Question, Quiz, QuizAnswer, QuizAttempt
from repositories import CsvRepository


class QuizService:
    """Lớp nghiệp vụ quản lý bài kiểm tra trắc nghiệm."""

    def __init__(
        self,
        quiz_repository: Optional[CsvRepository[Quiz]] = None,
        question_repository: Optional[CsvRepository[Question]] = None,
        attempt_repository: Optional[CsvRepository[QuizAttempt]] = None,
        answer_repository: Optional[CsvRepository[QuizAnswer]] = None,
    ) -> None:
        self.quiz_repository = quiz_repository or CsvRepository(
            DATA_DIR / "quizzes.csv", Quiz, "quiz_id", indexed_fields=("source_deck_id",)
        )
        self.question_repository = question_repository or CsvRepository(
            DATA_DIR / "questions.csv", Question, "question_id", indexed_fields=("quiz_id",)
        )
        self.attempt_repository = attempt_repository or CsvRepository(
            DATA_DIR / "quiz_attempts.csv", QuizAttempt, "attempt_id", indexed_fields=("quiz_id",)
        )
        self.answer_repository = answer_repository or CsvRepository(
            DATA_DIR / "quiz_answers.csv", QuizAnswer, "answer_id", indexed_fields=("attempt_id",)
        )

    def create_quiz(
        self,
        title: str,
        description: Optional[str] = None,
        time_limit_minutes: Optional[int] = None,
        source_deck_id: Optional[int] = None,
        questions: Optional[list[dict[str, Any]]] = None
    ) -> tuple[int, str, Optional[str], Optional[int], int]:
        """Tạo mới một bài kiểm tra và lưu ngân hàng câu hỏi đi kèm.

        Khởi tạo đối tượng Quiz và các Question, xác thực tính toàn vẹn dữ liệu
        trước khi gọi CsvRepository để lưu vào quizzes.csv và questions.csv
        đồng thời cập nhật các chỉ mục cây AVL với độ phức tạp O(log N).

        Args:
            title: Tiêu đề của bài kiểm tra (bắt buộc, không được để trống).
            description: Mô tả chi tiết của bài kiểm tra (tuỳ chọn, có thể None).
            time_limit_minutes: Thời gian làm bài tính bằng phút (tuỳ chọn, có thể None, nếu có phải > 0).
            source_deck_id: ID của bộ thẻ nguồn liên kết (tuỳ chọn, có thể None).
            questions: Danh sách các dict chứa dữ liệu câu hỏi (bắt buộc, không được None).
            **kwargs: Hỗ trợ linh hoạt các tham số bổ sung.

        Returns:
            tuple gồm (quiz_id, title, description, time_limit_minutes, question_count).

        Raises:
            ValueError: Khi title để trống, questions là None, thời gian làm bài không hợp lệ,
                        hoặc dữ liệu câu hỏi không hợp lệ (thiếu text, sai đáp án...).
            TypeError: Khi sai kiểu dữ liệu của các tham số đầu vào.
        """
        # 1. Xác thực tham số questions bắt buộc
        if questions is None:
            raise ValueError("Tham số questions là bắt buộc, không được là None")
        if not isinstance(questions, list):
            raise TypeError("Tham số questions phải là một danh sách (list)")

        # 2. Xác thực tiêu đề title bắt buộc
        if not isinstance(title, str):
            raise TypeError("Tiêu đề bài kiểm tra phải là chuỗi ký tự (str)")
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("Tiêu đề bài kiểm tra không được để trống")

        # 3. Xác thực mô tả description (tuỳ chọn)
        if description is not None:
            if not isinstance(description, str):
                raise TypeError("Mô tả bài kiểm tra phải là chuỗi ký tự hoặc None")
            clean_description = description.strip() if description.strip() else None
        else:
            clean_description = None

        # 4. Xác thực thời gian làm bài time_limit_minutes (tuỳ chọn, nếu có phải > 0)
        clean_time_limit: Optional[int] = None
        if time_limit_minutes is not None:
            if isinstance(time_limit_minutes, bool) or not isinstance(time_limit_minutes, int):
                raise TypeError("Thời gian làm bài (phút) phải là số nguyên hoặc None")
            if time_limit_minutes <= 0:
                raise ValueError("Thời gian làm bài (phút) phải là số nguyên dương lớn hơn 0")
            clean_time_limit = time_limit_minutes

        # 5. Xác thực source_deck_id (tuỳ chọn)
        clean_source_deck_id: Optional[int] = None
        if source_deck_id is not None:
            if isinstance(source_deck_id, bool) or not isinstance(source_deck_id, int):
                raise TypeError("source_deck_id phải là số nguyên hoặc None")
            clean_source_deck_id = source_deck_id

        # 6. Pre-validation: Kiểm tra tính toàn vẹn của tất cả câu hỏi trước khi ghi đĩa
        validated_questions: list[Question] = []
        valid_answers = {"A", "B", "C", "D"}

        for idx, q_data in enumerate(questions, start=1):
            if not isinstance(q_data, dict):
                raise TypeError(f"Mỗi phần tử trong questions phải là một dictionary (câu {idx})")

            # Nội dung câu hỏi
            raw_q_text = q_data.get("question_text", q_data.get("question", ""))
            if not isinstance(raw_q_text, str) or not raw_q_text.strip():
                raise ValueError(f"Nội dung câu hỏi thứ {idx} không được để trống")
            question_text = raw_q_text.strip()

            # Các phương án lựa chọn A, B, C, D
            option_a = str(q_data.get("option_a", q_data.get("optionA", ""))).strip()
            option_b = str(q_data.get("option_b", q_data.get("optionB", ""))).strip()
            option_c = str(q_data.get("option_c", q_data.get("optionC", ""))).strip()
            option_d = str(q_data.get("option_d", q_data.get("optionD", ""))).strip()

            if not (option_a and option_b and option_c and option_d):
                raise ValueError(
                    f"Các phương án lựa chọn (A, B, C, D) của câu hỏi thứ {idx} không được để trống"
                )

            # Đáp án đúng
            raw_correct = q_data.get("correct_answer", q_data.get("correctAnswer", ""))
            if not isinstance(raw_correct, str):
                raise TypeError(f"Đáp án đúng của câu hỏi thứ {idx} phải là chuỗi ký tự (str)")
            correct_answer = raw_correct.strip().upper()
            if correct_answer not in valid_answers:
                raise ValueError(
                    f"Đáp án đúng của câu hỏi thứ {idx} phải là một trong các giá trị: A, B, C, D "
                    f"(nhận được: {raw_correct!r})"
                )

            # Thứ tự hiển thị
            raw_pos = q_data.get("position", idx)
            try:
                position = int(raw_pos)
            except (ValueError, TypeError) as exc:
                raise TypeError(f"Thứ tự (position) của câu hỏi thứ {idx} phải là số nguyên") from exc

            # Điểm số
            raw_points = q_data.get("points", Decimal("1.00"))
            if isinstance(raw_points, Decimal):
                points = raw_points
            elif isinstance(raw_points, (int, float, str)):
                try:
                    points = Decimal(str(raw_points))
                except (InvalidOperation, ValueError, TypeError) as exc:
                    raise ValueError(f"Điểm số (points) của câu hỏi thứ {idx} không hợp lệ: {raw_points}") from exc
            else:
                raise TypeError(f"Điểm số (points) của câu hỏi thứ {idx} phải là số hoặc Decimal")

            is_deleted = bool(q_data.get("is_deleted", False))

            validated_questions.append(
                Question(
                    quiz_id=0,  # Sẽ gán quiz_id sau khi new_quiz được lưu
                    question_text=question_text,
                    option_a=option_a,
                    option_b=option_b,
                    option_c=option_c,
                    option_d=option_d,
                    correct_answer=correct_answer,
                    position=position,
                    points=points,
                    is_deleted=is_deleted,
                )
            )

        # 7. Khởi tạo và lưu Quiz mới vào quizzes.csv (O(log N))
        new_quiz = Quiz(
            title=clean_title,
            description=clean_description,
            time_limit_minutes=clean_time_limit,
            source_deck_id=clean_source_deck_id,
        )
        saved_quiz = self.quiz_repository.add(new_quiz)

        # 8. Lưu các Question vào questions.csv (O(log N) trên cả primary và secondary AVL tree)
        for question in validated_questions:
            question.quiz_id = saved_quiz.quiz_id  # type: ignore[assignment]
            self.question_repository.add(question)

        question_count = len(validated_questions)

        return (
            saved_quiz.quiz_id,  # type: ignore[return-value]
            saved_quiz.title,
            saved_quiz.description,
            saved_quiz.time_limit_minutes,
            question_count,
        )

    def import_questions_from_csv(
        self,
        file_path: Optional[str | Path] = None,
        csv_content: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Nhập và trích xuất danh sách câu hỏi từ file CSV hoặc chuỗi nội dung CSV.

        Hàm chỉ phân tích (parse) và xác thực dữ liệu câu hỏi để phục vụ việc
        tự động nhập vào form tạo Quiz trên giao diện (chỉ nhập thông tin câu hỏi,
        người dùng vẫn cần nhấn nút tạo Quiz để lưu).
        Hàm KHÔNG lưu bản ghi xuống quizzes.csv hay questions.csv.

        Chỉ nhận diện các header đúng như đã quy định trong data/questions.csv.

        Các cột bắt buộc:
            - question_text: Nội dung câu hỏi
            - option_a: Phương án A
            - option_b: Phương án B
            - option_c: Phương án C
            - option_d: Phương án D
            - correct_answer: Đáp án đúng (A, B, C hoặc D)

        Các cột tuỳ chọn theo đúng questions.csv:
            - position: Thứ tự câu hỏi (mặc định tự động tăng 1, 2, ...)
            - points: Điểm số (mặc định "1.00")
            - is_deleted: Trạng thái xoá (mặc định False)

        Args:
            file_path: Đường dẫn đến file CSV chứa câu hỏi (tuỳ chọn nếu có csv_content).
            csv_content: Nội dung file CSV dạng chuỗi (tuỳ chọn nếu có file_path).

        Returns:
            list[dict[str, Any]]: Danh sách các câu hỏi đã chuẩn hóa, sẵn sàng đưa vào
                                 form tạo Quiz hoặc truyền vào create_quiz.

        Raises:
            FileNotFoundError: Khi file_path không tồn tại trên hệ thống.
            ValueError: Khi thiếu tham số đầu vào, file CSV rỗng, thiếu header bắt buộc
                        hoặc dữ liệu câu hỏi không hợp lệ.
        """
        if file_path is None and csv_content is None:
            raise ValueError("Cần cung cấp ít nhất một trong hai tham số: file_path hoặc csv_content")

        if file_path is not None:
            path = Path(file_path)
            if not path.is_file():
                raise FileNotFoundError(f"Không tìm thấy file CSV tại: {path}")
            raw_text = path.read_text(encoding="utf-8-sig")
        else:
            raw_text = str(csv_content)

        if not raw_text.strip():
            raise ValueError("Nội dung file CSV không được để trống")

        required_headers = (
            "question_text",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_answer",
        )

        stream = io.StringIO(raw_text)
        reader = csv.DictReader(stream)

        if not reader.fieldnames:
            raise ValueError("File CSV không có dòng tiêu đề (header)")

        fieldnames = [f.strip() for f in reader.fieldnames if f]
        missing_headers = [h for h in required_headers if h not in fieldnames]
        if missing_headers:
            raise ValueError(
                f"File CSV thiếu các cột bắt buộc theo định dạng questions.csv: {', '.join(missing_headers)}"
            )

        imported_questions: list[dict[str, Any]] = []
        valid_answers = {"A", "B", "C", "D"}

        for line_number, row in enumerate(reader, start=2):
            # Bỏ qua các dòng hoàn toàn trống
            if not any(v and str(v).strip() for v in row.values()):
                continue

            # 1. question_text
            raw_text_val = str(row.get("question_text") or "").strip()
            if not raw_text_val:
                raise ValueError(f"Dòng {line_number}: 'question_text' không được để trống")

            # 2. Các phương án A, B, C, D
            opt_a = str(row.get("option_a") or "").strip()
            opt_b = str(row.get("option_b") or "").strip()
            opt_c = str(row.get("option_c") or "").strip()
            opt_d = str(row.get("option_d") or "").strip()
            if not (opt_a and opt_b and opt_c and opt_d):
                raise ValueError(
                    f"Dòng {line_number}: Các phương án lựa chọn (option_a, option_b, option_c, option_d) không được để trống"
                )

            # 3. correct_answer
            raw_ans = str(row.get("correct_answer") or "").strip().upper()
            if raw_ans not in valid_answers:
                raise ValueError(
                    f"Dòng {line_number}: 'correct_answer' phải là một trong các giá trị: A, B, C, D "
                    f"(nhận được: {row.get('correct_answer')!r})"
                )

            # 4. position
            pos_val = row.get("position")
            if pos_val is not None and str(pos_val).strip():
                try:
                    position = int(str(pos_val).strip())
                except ValueError as exc:
                    raise ValueError(f"Dòng {line_number}: 'position' phải là số nguyên") from exc
            else:
                position = len(imported_questions) + 1

            # 5. points
            pts_val = row.get("points")
            if pts_val is not None and str(pts_val).strip():
                try:
                    points = str(Decimal(str(pts_val).strip()))
                except (InvalidOperation, ValueError) as exc:
                    raise ValueError(f"Dòng {line_number}: 'points' không hợp lệ: {pts_val}") from exc
            else:
                points = "1.00"

            imported_questions.append({
                "question_text": raw_text_val,
                "option_a": opt_a,
                "option_b": opt_b,
                "option_c": opt_c,
                "option_d": opt_d,
                "correct_answer": raw_ans,
                "position": position,
                "points": points
            })

        if not imported_questions:
            raise ValueError("File CSV không chứa bất kỳ câu hỏi hợp lệ nào")

        return imported_questions

    def delete_quiz(self, quiz_id: int) -> bool:
        """Xóa bài kiểm tra theo quiz_id và xóa bản ghi trong các file CSV liên quan.

        Thực hiện xóa liên đới (Cascade Delete) theo thứ tự:
            1. data/quiz_answers.csv: Xóa toàn bộ câu trả lời của các lượt thi thuộc bài quiz này.
            2. data/quiz_attempts.csv: Xóa toàn bộ các lượt làm bài của bài quiz này.
            3. data/questions.csv: Xóa toàn bộ câu hỏi của bài quiz này.
            4. data/quizzes.csv: Xóa bản ghi bài kiểm tra.

        Args:
            quiz_id: ID của bài kiểm tra cần xóa.

        Returns:
            bool: True nếu tìm thấy và xóa thành công, False nếu quiz_id không tồn tại.

        Raises:
            TypeError: Khi quiz_id không phải là số nguyên hợp lệ.
        """
        if isinstance(quiz_id, bool) or not isinstance(quiz_id, int):
            raise TypeError("quiz_id phải là số nguyên")

        # 1. Kiểm tra sự tồn tại của bài quiz
        if not self.quiz_repository.exists(quiz_id):
            return False

        # 2. Xóa các câu trả lời liên quan trong quiz_answers.csv
        attempts = self.attempt_repository.find_by(quiz_id=quiz_id)
        for att in attempts:
            if att.attempt_id is not None:
                self.answer_repository.delete_where(attempt_id=att.attempt_id)

        # 3. Xóa các lượt làm bài trong quiz_attempts.csv
        self.attempt_repository.delete_where(quiz_id=quiz_id)

        # 4. Xóa các câu hỏi trong questions.csv
        self.question_repository.delete_where(quiz_id=quiz_id)

        # 5. Xóa bài quiz trong quizzes.csv
        return self.quiz_repository.delete(quiz_id)

    def get_quizzes(
        self,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> dict[str, Any]:
        """Lấy danh sách bài kiểm tra hoặc tìm kiếm theo tên có phân trang (tối đa 10 quiz).

        Chỉ cần tiêu đề bài kiểm tra có chứa chuỗi tìm kiếm (substring / partial match),
        không phân biệt chữ hoa hay chữ thường. Mặc định tự động lọc bỏ các bài quiz
        đã bị đánh dấu xóa (is_deleted = True).

        Args:
            keyword: Từ khóa tìm kiếm chuỗi con trong tiêu đề bài quiz.
            page: Số trang cần lấy (bắt đầu từ 1, mặc định 1).
            page_size: Số lượng quiz tối đa trên mỗi trang (mặc định 10, trần tối đa 10).

        Returns:
            dict[str, Any]:
                - items: Danh sách tối đa 10 quiz (chỉ gồm quiz_id, title, description,
                         time_limit_minutes, total_questions, source_deck_id).
                - total_pages: Tổng số trang (ceil(total_count / page_size)).
                - page: Trang hiện tại.
                - page_size: Kích thước trang thực tế (tối đa 10).

        Raises:
            TypeError: Khi page hoặc page_size không phải số nguyên.
        """
        if isinstance(page, bool) or not isinstance(page, int):
            raise TypeError("page phải là số nguyên")
        if isinstance(page_size, bool) or not isinstance(page_size, int):
            raise TypeError("page_size phải là số nguyên")

        actual_page = max(1, page)
        actual_page_size = max(1, min(page_size, 10))

        # 1. Lọc danh sách quiz hợp lệ từ cây AVL in-memory
        quizzes = self.quiz_repository.find_by(is_deleted=False)

        if keyword is not None:
            clean_kw = keyword.strip().lower()
            if clean_kw:
                quizzes = [q for q in quizzes if clean_kw in q.title.lower()]

        # Tính tổng số trang bằng tổng số bài quiz hợp lệ
        total_count = len(quizzes)
        total_pages = (total_count + actual_page_size - 1) // actual_page_size if total_count > 0 else 0

        # 2. Cắt dữ liệu trang hiện tại (tối đa 10 quiz)
        start_idx = (actual_page - 1) * actual_page_size
        end_idx = start_idx + actual_page_size
        paged_quizzes = quizzes[start_idx:end_idx]

        # 3. Làm giàu dữ liệu: Chỉ tính total_questions cho tối đa 10 quiz của trang này
        # Loại bỏ is_deleted, created_at, updated_at theo yêu cầu
        items: list[dict[str, Any]] = []
        for q in paged_quizzes:
            questions = self.question_repository.find_by(quiz_id=q.quiz_id, is_deleted=False)
            items.append({
                "quiz_id": q.quiz_id,
                "title": q.title,
                "description": q.description,
                "time_limit_minutes": q.time_limit_minutes,
                "total_questions": len(questions),
                "source_deck_id": q.source_deck_id,
            })

        return {
            "items": items,
            "total_pages": total_pages,
            "page": actual_page,
            "page_size": actual_page_size,
        }
