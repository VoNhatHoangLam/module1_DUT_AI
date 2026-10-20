import { QuizAttempt, QuizAttemptResult } from '../types';
import { request } from './apiClient';

export const historyService = {
  /**
   * Lấy danh sách lịch sử các lượt làm bài đã nộp.
   */
  async listAttempts(quizId?: number, submittedOnly: boolean = true): Promise<QuizAttempt[]> {
    const params = new URLSearchParams();
    if (quizId !== undefined) params.set('quiz_id', String(quizId));
    params.set('submitted_only', String(submittedOnly));

    return request<QuizAttempt[]>(`/history?${params.toString()}`);
  },

  /**
   * Lấy chi tiết kết quả lượt thi kèm danh sách câu trả lời và đáp án đúng.
   */
  async getAttemptResult(attemptId: number | string): Promise<QuizAttemptResult> {
    return request<QuizAttemptResult>(`/history/${attemptId}`);
  },
};
