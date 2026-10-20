"""Máy chủ FastAPI tích hợp nghiệp vụ FlashCard & Quiz và giao diện người dùng."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any, Mapping, Optional

from fastapi import Body, FastAPI, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from models import Card, Deck, Question, Quiz, QuizAnswer, QuizAttempt
from services import (
    AttemptAlreadySubmittedError,
    AttemptNotFoundError,
    DeckService,
    HistoryService,
    NoCardToReviewError,
    NoQuestionError,
    QuizNotFoundError,
    QuizService,
)
from services.quiz_service import QuizAttemptResult, QuizSession
from services.study_service import FlashcardStudyQueue

# -----------------------------------------------------------------------------
# Khởi tạo Ứng dụng & Dịch vụ nghiệp vụ
# -----------------------------------------------------------------------------

app = FastAPI(
    title="FlashLearn API",
    description="Hệ thống Backend tích hợp cấu trúc dữ liệu AVLTree, Queue, 2-Stack",
    version="1.0.0",
)

# Cấu hình CORS để frontend React (Vite dev server) kết nối mượt mà
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

deck_service = DeckService()
quiz_service = QuizService()
history_service = HistoryService()

# Quản lý phiên làm việc in-memory
study_sessions: dict[str, FlashcardStudyQueue] = {}
quiz_sessions: dict[int, QuizSession] = {}


# -----------------------------------------------------------------------------
# Pydantic Schemas cho Request & Response
# -----------------------------------------------------------------------------

class CardItem(BaseModel):
    term: str = Field(..., description="Từ vựng / Thuật ngữ (front_text)")
    definition: str = Field(..., description="Định nghĩa / Ý nghĩa (back_text)")
    position: Optional[int] = Field(None, description="Thứ tự hiển thị")


class CreateDeckRequest(BaseModel):
    title: str = Field(..., min_length=1, description="Tiêu đề bộ thẻ")
    description: Optional[str] = Field(None, description="Mô tả bộ thẻ")
    category: Optional[str] = Field("Chung", description="Danh mục bộ thẻ")
    privacy: Optional[str] = Field("public", description="Chế độ riêng tư: public | private")
    cards: list[CardItem] = Field(..., min_length=1, description="Danh sách thẻ flashcard")


class ImportCsvRequest(BaseModel):
    csv_content: str = Field(..., description="Chuỗi văn bản nội dung CSV")


class StartStudyRequest(BaseModel):
    deck_id: int = Field(..., description="ID bộ thẻ cần học")


class MarkStudyCardRequest(BaseModel):
    is_known: bool = Field(..., description="True nếu đã thuộc, False nếu chưa thuộc")


class QuestionItem(BaseModel):
    question: str = Field(..., min_length=1, description="Nội dung câu hỏi")
    optionA: str = Field(..., min_length=1, description="Phương án A")
    optionB: str = Field(..., min_length=1, description="Phương án B")
    optionC: Optional[str] = Field("", description="Phương án C")
    optionD: Optional[str] = Field("", description="Phương án D")
    correctAnswer: str = Field(..., description="Đáp án đúng: A, B, C hoặc D")
    explanation: Optional[str] = Field("", description="Giải thích chi tiết")
    points: Optional[float] = Field(1.0, description="Điểm số của câu hỏi")
    position: Optional[int] = Field(None, description="Vị trí câu hỏi")


class CreateQuizRequest(BaseModel):
    title: str = Field(..., min_length=1, description="Tiêu đề bài kiểm tra")
    description: Optional[str] = Field(None, description="Mô tả bài kiểm tra")
    category: Optional[str] = Field("Chung", description="Danh mục")
    privacy: Optional[str] = Field("public", description="public | private")
    time_limit_minutes: Optional[int] = Field(10, description="Thời gian làm bài tính bằng phút")
    source_deck_id: Optional[int] = Field(None, description="ID bộ thẻ nguồn (nếu có)")
    questions: list[QuestionItem] = Field(..., min_length=1, description="Danh sách câu hỏi")


class AnswerQuestionRequest(BaseModel):
    selected_answer: Optional[str] = Field(None, description="A, B, C, D hoặc null")


class SubmitQuizRequest(BaseModel):
    selected_answers: Optional[dict[int, Optional[str]]] = Field(
        None, description="Bản đồ câu hỏi -> đáp án đã chọn"
    )


# -----------------------------------------------------------------------------
# Hàm hỗ trợ Chuyển đổi dữ liệu (Serialization Helpers)
# -----------------------------------------------------------------------------

def serialize_card(card: Card) -> dict[str, Any]:
    return {
        "id": str(card.card_id or ""),
        "card_id": card.card_id,
        "deck_id": card.deck_id,
        "term": card.front_text,
        "definition": card.back_text,
        "position": card.position,
    }


def serialize_deck(deck: Deck, cards: Optional[list[Card]] = None) -> dict[str, Any]:
    data = {
        "id": str(deck.deck_id),
        "deck_id": deck.deck_id,
        "title": deck.title,
        "description": deck.description or "",
        "total_cards": deck.total_cards,
        "is_studied": deck.is_studied,
        "updatedAt": str(deck.updated_at or deck.created_at or ""),
        "category": "Chung",
        "createdBy": "Học viên",
        "userId": "1",
        "privacy": "public",
        "status": "approved",
    }
    if cards is not None:
        data["cards"] = [serialize_card(c) for c in cards]
    return data


def serialize_question(q: Question) -> dict[str, Any]:
    return {
        "id": q.question_id,
        "question_id": q.question_id,
        "quiz_id": q.quiz_id,
        "question": q.question_text,
        "optionA": q.option_a,
        "optionB": q.option_b,
        "optionC": q.option_c,
        "optionD": q.option_d,
        "correctAnswer": q.correct_answer,
        "position": q.position,
        "points": float(q.points) if q.points is not None else 1.0,
        "explanation": "Đáp án đúng là " + str(q.correct_answer),
    }


def serialize_quiz(quiz: Quiz, questions: Optional[list[Question]] = None) -> dict[str, Any]:
    data = {
        "id": str(quiz.quiz_id),
        "quiz_id": quiz.quiz_id,
        "title": quiz.title,
        "description": quiz.description or "",
        "timeLimitMinutes": quiz.time_limit_minutes or 10,
        "source_deck_id": quiz.source_deck_id,
        "category": "Chung",
        "createdBy": "Học viên",
        "userId": "1",
        "privacy": "public",
        "status": "approved",
        "total_questions": len(questions) if questions is not None else 0,
    }
    if questions is not None:
        data["questions"] = [serialize_question(q) for q in questions]
    return data


def serialize_attempt(att: QuizAttempt) -> dict[str, Any]:
    score_val = float(att.score_percent) if att.score_percent is not None else 0.0
    return {
        "id": str(att.attempt_id),
        "attempt_id": att.attempt_id,
        "quizId": str(att.quiz_id),
        "quizTitle": att.quiz_title_snapshot,
        "takenDate": str(att.submitted_at or att.started_at or ""),
        "score": round(score_val),
        "correctCount": att.correct_count,
        "totalCount": att.total_questions,
        "accuracy": f"{round(score_val)}%",
        "status": "Hoàn thành" if att.attempt_status == "SUBMITTED" else att.attempt_status,
        "userAnswers": {},
    }


def serialize_attempt_result(res: QuizAttemptResult) -> dict[str, Any]:
    attempt_dict = serialize_attempt(res.attempt)
    answers_list = []
    user_answers: dict[int, str] = {}
    for ans in res.answers:
        if ans.selected_answer is not None and ans.answer_id is not None:
            user_answers[ans.answer_id] = ans.selected_answer
        answers_list.append({
            "answer_id": ans.answer_id,
            "attempt_id": ans.attempt_id,
            "selected_answer": ans.selected_answer,
            "correct_answer_snapshot": ans.correct_answer_snapshot,
            "is_correct": ans.is_correct,
            "points_earned": float(ans.points_earned) if ans.points_earned is not None else 0.0,
            "question_text_snapshot": ans.question_text_snapshot,
            "selected_option_text_snapshot": ans.selected_option_text_snapshot,
            "correct_option_text_snapshot": ans.correct_option_text_snapshot,
        })
    attempt_dict["userAnswers"] = user_answers
    return {
        "attempt": attempt_dict,
        "answers": answers_list,
    }


# -----------------------------------------------------------------------------
# 1. API Quản lý Bộ Thẻ (Decks)
# -----------------------------------------------------------------------------

@app.get("/api/decks")
def get_decks(
    keyword: Optional[str] = Query(None, description="Từ khóa tiền tố tiêu đề bộ thẻ cần tìm kiếm bằng Cây AVL O(log N + K)"),
    page: int = Query(1, ge=1, description="Số trang"),
    page_size: int = Query(10, ge=1, le=100, description="Kích thước trang"),
) -> dict[str, Any]:
    """Lấy danh sách bộ thẻ hoặc tìm kiếm tiền tố tiêu đề từ cây chỉ mục AVL O(log N + K)."""
    result = deck_service.get_decks(keyword=keyword, page=page, page_size=page_size)
    items: list[dict[str, Any]] = []
    for d in result["items"]:
        deck_and_cards = deck_service.get_deck_by_id(d.deck_id)
        cards = deck_and_cards[1] if deck_and_cards else []
        items.append(serialize_deck(d, cards))

    return {
        "items": items,
        "total_pages": result["total_pages"],
        "page": result["page"],
        "page_size": result["page_size"],
    }


@app.get("/api/decks/{deck_id}")
def get_deck_by_id(deck_id: int) -> dict[str, Any]:
    """Tìm kiếm chi tiết bộ thẻ và danh sách thẻ con O(log N)."""
    deck_and_cards = deck_service.get_deck_by_id(deck_id)
    if deck_and_cards is None:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy bộ thẻ với ID {deck_id}")
    deck, cards = deck_and_cards
    return serialize_deck(deck, cards)


@app.post("/api/decks")
def create_deck(payload: CreateDeckRequest) -> dict[str, Any]:
    """Tạo mới bộ thẻ và lưu vào decks.csv cùng cards.csv."""
    try:
        cards_data = [
            {"term": c.term, "definition": c.definition, "position": c.position or idx}
            for idx, c in enumerate(payload.cards, start=1)
        ]
        deck_id, title, desc, card_count = deck_service.create_deck(
            title=payload.title,
            cards=cards_data,
            description=payload.description,
        )
        created = deck_service.get_deck_by_id(deck_id)
        if created:
            return serialize_deck(created[0], created[1])
        return {"deck_id": deck_id, "title": title, "card_count": card_count}
    except (ValueError, TypeError) as err:
        raise HTTPException(status_code=400, detail=str(err))


@app.delete("/api/decks/{deck_id}")
def delete_deck(deck_id: int) -> dict[str, Any]:
    """Xóa vĩnh viễn bộ thẻ và xóa liên hoàn (Cascade Delete) các thẻ con."""
    success = deck_service.delete_deck(deck_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy bộ thẻ {deck_id} để xóa")
    return {"success": True, "message": f"Đã xóa thành công bộ thẻ {deck_id}"}


@app.post("/api/decks/import")
def import_cards(payload: ImportCsvRequest) -> list[dict[str, Any]]:
    """Phân tích dữ liệu thẻ từ CSV để điền vào form tạo bộ thẻ."""
    try:
        cards = deck_service.import_cards_from_csv(payload.csv_content)
        return cards
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


# -----------------------------------------------------------------------------
# 2. API Quản lý Phiên Học Flashcard (Queue FIFO 2 Giai Đoạn)
# -----------------------------------------------------------------------------

@app.post("/api/study/start")
def start_study(payload: StartStudyRequest) -> dict[str, Any]:
    """Khởi tạo phiên ôn tập Flashcard theo hàng đợi hai giai đoạn chuẩn FIFO."""
    deck_and_cards = deck_service.get_deck_by_id(payload.deck_id)
    if not deck_and_cards or not deck_and_cards[1]:
        raise HTTPException(status_code=400, detail="Bộ thẻ không tồn tại hoặc không có thẻ nào để học")

    deck, cards = deck_and_cards
    study_queue = FlashcardStudyQueue(cards)
    session_id = str(uuid.uuid4())
    study_sessions[session_id] = study_queue

    current = study_queue.current_card
    return {
        "session_id": session_id,
        "deck_id": deck.deck_id,
        "deck_title": deck.title,
        "current_card": serialize_card(current) if current else None,
        "remaining_count": study_queue.remaining_count,
        "unknown_count": study_queue.unknown_count,
        "known_count": study_queue.known_count,
        "total_cards": study_queue.total_cards,
        "is_completed": study_queue.is_completed,
        "is_initial_phase": study_queue.is_initial_phase,
    }


@app.post("/api/study/{session_id}/mark")
def mark_study_card(session_id: str, payload: MarkStudyCardRequest) -> dict[str, Any]:
    """Đánh dấu thẻ hiện tại (Thuộc / Chưa thuộc) và lấy thẻ tiếp theo từ Queue."""
    session = study_sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên học flashcard")

    try:
        marked_card = session.mark_card(payload.is_known)
        current = session.current_card
        return {
            "session_id": session_id,
            "marked_card": serialize_card(marked_card),
            "current_card": serialize_card(current) if current else None,
            "remaining_count": session.remaining_count,
            "unknown_count": session.unknown_count,
            "known_count": session.known_count,
            "total_cards": session.total_cards,
            "is_completed": session.is_completed,
            "is_initial_phase": session.is_initial_phase,
        }
    except NoCardToReviewError:
        return {
            "session_id": session_id,
            "current_card": None,
            "remaining_count": 0,
            "unknown_count": 0,
            "known_count": session.known_count,
            "total_cards": session.total_cards,
            "is_completed": True,
            "is_initial_phase": False,
        }
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


@app.get("/api/study/{session_id}/state")
def get_study_state(session_id: str) -> dict[str, Any]:
    """Lấy trạng thái hiện tại của phiên học flashcard."""
    session = study_sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên học")

    current = session.current_card
    return {
        "session_id": session_id,
        "current_card": serialize_card(current) if current else None,
        "remaining_count": session.remaining_count,
        "unknown_count": session.unknown_count,
        "known_count": session.known_count,
        "total_cards": session.total_cards,
        "is_completed": session.is_completed,
        "is_initial_phase": session.is_initial_phase,
    }


# -----------------------------------------------------------------------------
# 3. API Quản lý Bài Kiểm Tra Quiz
# -----------------------------------------------------------------------------

@app.get("/api/quizzes")
def get_quizzes(
    keyword: Optional[str] = Query(None, description="Từ khóa tìm kiếm"),
    page: int = Query(1, ge=1, description="Số trang"),
    page_size: int = Query(10, ge=1, le=100, description="Kích thước trang"),
) -> dict[str, Any]:
    """Lấy danh sách các bài thi trắc nghiệm kèm câu hỏi."""
    result = quiz_service.get_quizzes(keyword=keyword, page=page, page_size=page_size)
    items: list[dict[str, Any]] = []
    for item in result["items"]:
        quiz_id = item["quiz_id"]
        questions = quiz_service.question_repository.find_by(quiz_id=quiz_id, is_deleted=False)
        quiz_obj = quiz_service.quiz_repository.get_by_id(quiz_id)
        if quiz_obj:
            items.append(serialize_quiz(quiz_obj, questions))

    return {
        "items": items,
        "total_pages": result["total_pages"],
        "page": result["page"],
        "page_size": result["page_size"],
    }


@app.get("/api/quizzes/{quiz_id}")
def get_quiz_by_id(quiz_id: int) -> dict[str, Any]:
    """Lấy thông tin chi tiết bài quiz và danh sách câu hỏi."""
    quiz_obj = quiz_service.quiz_repository.get_by_id(quiz_id)
    if quiz_obj is None or quiz_obj.is_deleted:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy quiz ID {quiz_id}")
    questions = quiz_service.question_repository.find_by(quiz_id=quiz_id, is_deleted=False)
    questions.sort(key=lambda q: q.position)
    return serialize_quiz(quiz_obj, questions)


@app.post("/api/quizzes")
def create_quiz(payload: CreateQuizRequest) -> dict[str, Any]:
    """Tạo mới bài quiz cùng ngân hàng câu hỏi vào quizzes.csv và questions.csv."""
    try:
        raw_questions: list[dict[str, Any]] = []
        for idx, q in enumerate(payload.questions, start=1):
            raw_questions.append({
                "question_text": q.question,
                "option_a": q.optionA,
                "option_b": q.optionB,
                "option_c": q.optionC or "None",
                "option_d": q.optionD or "None",
                "correct_answer": q.correctAnswer,
                "position": q.position or idx,
                "points": Decimal(str(q.points or 1.0)),
            })

        quiz_id, title, desc, time_limit, count = quiz_service.create_quiz(
            title=payload.title,
            description=payload.description,
            time_limit_minutes=payload.time_limit_minutes,
            source_deck_id=payload.source_deck_id,
            questions=raw_questions,
        )

        quiz_obj = quiz_service.quiz_repository.get_by_id(quiz_id)
        questions = quiz_service.question_repository.find_by(quiz_id=quiz_id, is_deleted=False)
        if quiz_obj:
            return serialize_quiz(quiz_obj, questions)
        return {"quiz_id": quiz_id, "title": title, "total_questions": count}
    except (ValueError, TypeError) as err:
        raise HTTPException(status_code=400, detail=str(err))


@app.delete("/api/quizzes/{quiz_id}")
def delete_quiz(quiz_id: int) -> dict[str, Any]:
    """Xóa liên đới (Cascade Delete) bài quiz, câu hỏi, lượt làm bài và câu trả lời."""
    success = quiz_service.delete_quiz(quiz_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy quiz {quiz_id} để xóa")
    return {"success": True, "message": f"Đã xóa thành công bài kiểm tra {quiz_id}"}


@app.post("/api/quizzes/import")
def import_quiz_questions(payload: ImportCsvRequest) -> list[dict[str, Any]]:
    """Phân tích dữ liệu câu hỏi trắc nghiệm từ file/chuỗi CSV."""
    try:
        questions = quiz_service.import_questions_from_csv(csv_content=payload.csv_content)
        # Chuẩn hóa về format QuizQuestionInput cho UI
        formatted = []
        for q in questions:
            formatted.append({
                "question": q["question_text"],
                "optionA": q["option_a"],
                "optionB": q["option_b"],
                "optionC": q["option_c"],
                "optionD": q["option_d"],
                "correctAnswer": q["correct_answer"],
                "position": q.get("position", 1),
                "points": float(q.get("points", 1.0)),
                "explanation": "Câu hỏi nhập từ CSV",
            })
        return formatted
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


# -----------------------------------------------------------------------------
# 4. API Phiên Làm Bài Quiz (2-Stack Back/Forward & Chấm Điểm)
# -----------------------------------------------------------------------------

@app.post("/api/quizzes/{quiz_id}/start")
def start_quiz_session(quiz_id: int) -> dict[str, Any]:
    """Bắt đầu làm bài thi: Tạo QuizAttempt và phiên QuizSession với 2 Stack điều hướng."""
    try:
        session = quiz_service.start_quiz(quiz_id)
        assert session.attempt.attempt_id is not None
        quiz_sessions[session.attempt.attempt_id] = session

        current_q = session.current_question
        return {
            "attempt_id": session.attempt.attempt_id,
            "quiz_id": quiz_id,
            "quiz_title": session.attempt.quiz_title_snapshot,
            "total_questions": session.attempt.total_questions,
            "current_question": serialize_question(current_q) if current_q else None,
            "current_answer": session.current_answer,
            "can_back": session.can_back,
            "can_forward": session.can_forward,
            "remaining_count": session.remaining_count,
            "is_completed": session.is_completed,
            "selected_answers": session.selected_answers,
        }
    except (QuizNotFoundError, NoQuestionError) as err:
        raise HTTPException(status_code=400, detail=str(err))


@app.post("/api/quizzes/session/{attempt_id}/answer")
def answer_quiz_question(attempt_id: int, payload: AnswerQuestionRequest) -> dict[str, Any]:
    """Ghi nhận đáp án và chuyển tiếp sang câu kế tiếp (Stack push vào back_stack)."""
    session = quiz_sessions.get(attempt_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Phiên làm bài không tồn tại hoặc đã nộp")

    try:
        session.answer_current(payload.selected_answer)
        current_q = session.current_question
        return {
            "attempt_id": attempt_id,
            "current_question": serialize_question(current_q) if current_q else None,
            "current_answer": session.current_answer,
            "can_back": session.can_back,
            "can_forward": session.can_forward,
            "remaining_count": session.remaining_count,
            "is_completed": session.is_completed,
            "selected_answers": session.selected_answers,
        }
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


@app.post("/api/quizzes/session/{attempt_id}/back")
def quiz_navigate_back(attempt_id: int) -> dict[str, Any]:
    """Quay lại câu hỏi trước đó bằng cách pop từ _back_stack và push vào _forward_stack."""
    session = quiz_sessions.get(attempt_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Phiên làm bài không tồn tại")

    try:
        session.back()
        current_q = session.current_question
        return {
            "attempt_id": attempt_id,
            "current_question": serialize_question(current_q) if current_q else None,
            "current_answer": session.current_answer,
            "can_back": session.can_back,
            "can_forward": session.can_forward,
            "remaining_count": session.remaining_count,
            "is_completed": session.is_completed,
            "selected_answers": session.selected_answers,
        }
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


@app.post("/api/quizzes/session/{attempt_id}/forward")
def quiz_navigate_forward(attempt_id: int) -> dict[str, Any]:
    """Tiến tới câu hỏi kế tiếp bằng cách pop từ _forward_stack và push vào _back_stack."""
    session = quiz_sessions.get(attempt_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Phiên làm bài không tồn tại")

    try:
        session.forward()
        current_q = session.current_question
        return {
            "attempt_id": attempt_id,
            "current_question": serialize_question(current_q) if current_q else None,
            "current_answer": session.current_answer,
            "can_back": session.can_back,
            "can_forward": session.can_forward,
            "remaining_count": session.remaining_count,
            "is_completed": session.is_completed,
            "selected_answers": session.selected_answers,
        }
    except Exception as err:
        raise HTTPException(status_code=400, detail=str(err))


@app.post("/api/quizzes/session/{attempt_id}/submit")
def submit_quiz_attempt(attempt_id: int, payload: Optional[SubmitQuizRequest] = None) -> dict[str, Any]:
    """Chấm điểm bài thi, lưu kết quả xuống quiz_attempts.csv & quiz_answers.csv và giải phóng phiên."""
    session = quiz_sessions.get(attempt_id)
    selected_answers: Mapping[int, Optional[str]]
    if payload and payload.selected_answers is not None:
        selected_answers = payload.selected_answers
    elif session is not None:
        selected_answers = session.selected_answers
    else:
        selected_answers = {}

    try:
        result = quiz_service.submit_quiz(attempt_id, selected_answers)
        if attempt_id in quiz_sessions:
            del quiz_sessions[attempt_id]
        return serialize_attempt_result(result)
    except (AttemptNotFoundError, AttemptAlreadySubmittedError, ValueError) as err:
        raise HTTPException(status_code=400, detail=str(err))


# -----------------------------------------------------------------------------
# 5. API Lịch Sử Làm Bài (History)
# -----------------------------------------------------------------------------

@app.get("/api/history")
def get_quiz_history(
    quiz_id: Optional[int] = Query(None, description="Lọc theo quiz_id"),
    submitted_only: bool = Query(True, description="Chỉ lấy lượt thi đã nộp"),
) -> list[dict[str, Any]]:
    """Tra cứu danh sách lịch sử thi sắp xếp mới nhất lên đầu."""
    attempts = history_service.list_attempts(quiz_id=quiz_id, submitted_only=submitted_only)
    return [serialize_attempt(att) for att in attempts]


@app.get("/api/history/{attempt_id}")
def get_attempt_detail(attempt_id: int) -> dict[str, Any]:
    """Xem lại chi tiết bài làm, điểm số và đối chiếu từng câu hỏi kèm đáp án đúng."""
    try:
        result = history_service.get_attempt_result(attempt_id)
        return serialize_attempt_result(result)
    except AttemptNotFoundError:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy lượt làm bài {attempt_id}")


# -----------------------------------------------------------------------------
# Khởi chạy chính
# -----------------------------------------------------------------------------

def main() -> None:
    """Khởi chạy máy chủ FastAPI bằng uvicorn."""
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
