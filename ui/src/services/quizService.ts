import {
  QuizSet,
  QuizSessionState,
  QuizAttemptResult,
  QuizQuestionInput,
} from '../types';
import { request } from './apiClient';

export interface GetQuizzesResponse {
  items: QuizSet[];
  total_pages: number;
  page: number;
  page_size: number;
}

export interface CreateQuizPayload {
  title: string;
  description?: string;
  category?: string;
  privacy?: 'public' | 'private';
  time_limit_minutes?: number;
  source_deck_id?: number | null;
  questions: QuizQuestionInput[];
}

export const quizService = {
  /**
   * Lấy danh sách bài thi trắc nghiệm.
   */
  async getQuizzes(keyword?: string, page: number = 1, pageSize: number = 20): Promise<GetQuizzesResponse> {
    const params = new URLSearchParams();
    if (keyword && keyword.trim()) params.set('keyword', keyword.trim());
    params.set('page', String(page));
    params.set('page_size', String(pageSize));

    return request<GetQuizzesResponse>(`/quizzes?${params.toString()}`);
  },

  /**
   * Lấy chi tiết bài quiz và danh sách câu hỏi.
   */
  async getQuizById(quizId: number | string): Promise<QuizSet> {
    return request<QuizSet>(`/quizzes/${quizId}`);
  },

  /**
   * Tạo bài kiểm tra mới và lưu vào quizzes.csv & questions.csv.
   */
  async createQuiz(payload: CreateQuizPayload): Promise<QuizSet> {
    return request<QuizSet>('/quizzes', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  /**
   * Xóa bài quiz và xóa liên đới (Cascade Delete) toàn bộ câu hỏi, lượt thi và kết quả.
   */
  async deleteQuiz(quizId: number | string): Promise<{ success: boolean; message: string }> {
    return request<{ success: boolean; message: string }>(`/quizzes/${quizId}`, {
      method: 'DELETE',
    });
  },

  /**
   * Phân tích câu hỏi trắc nghiệm từ CSV trước khi thêm vào form.
   */
  async importQuestionsFromCsv(csvContent: string): Promise<QuizQuestionInput[]> {
    return request<QuizQuestionInput[]>('/quizzes/import', {
      method: 'POST',
      body: JSON.stringify({ csv_content: csvContent }),
    });
  },

  /**
   * Bắt đầu làm bài thi: Khởi tạo QuizSession trên backend với mô hình 2 Stack.
   */
  async startQuiz(quizId: number | string): Promise<QuizSessionState> {
    return request<QuizSessionState>(`/quizzes/${quizId}/start`, {
      method: 'POST',
    });
  },

  /**
   * Chọn đáp án cho câu hỏi hiện tại và chuyển tiếp sang câu sau.
   */
  async answerQuestion(attemptId: number, selectedAnswer: string | null): Promise<QuizSessionState> {
    return request<QuizSessionState>(`/quizzes/session/${attemptId}/answer`, {
      method: 'POST',
      body: JSON.stringify({ selected_answer: selectedAnswer }),
    });
  },

  /**
   * Quay lại câu hỏi trước (Pop từ _back_stack và Push vào _forward_stack).
   */
  async navigateBack(attemptId: number): Promise<QuizSessionState> {
    return request<QuizSessionState>(`/quizzes/session/${attemptId}/back`, {
      method: 'POST',
    });
  },

  /**
   * Tiến tới câu hỏi tiếp theo (Pop từ _forward_stack và Push vào _back_stack).
   */
  async navigateForward(attemptId: number): Promise<QuizSessionState> {
    return request<QuizSessionState>(`/quizzes/session/${attemptId}/forward`, {
      method: 'POST',
    });
  },

  /**
   * Nộp bài kiểm tra: Chấm điểm chính xác, cập nhật quiz_attempts.csv & quiz_answers.csv.
   */
  async submitQuiz(
    attemptId: number,
    selectedAnswers?: Record<number, string | null>
  ): Promise<QuizAttemptResult> {
    return request<QuizAttemptResult>(`/quizzes/session/${attemptId}/submit`, {
      method: 'POST',
      body: JSON.stringify({ selected_answers: selectedAnswers }),
    });
  },
};
